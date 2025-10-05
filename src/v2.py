#!/usr/bin/env python3
import os, subprocess, typer, getpass, time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
from rich.console import Console
from pathlib import Path
from pydantic import BaseModel, Field, TypeAdapter
from typing import Optional, List
import re
load_dotenv ()
API = os.getenv("GEMINI_API_KEY2")

app = typer.Typer()
console = Console()

def normalize_content(content):
    if isinstance(content, list):
        return "\n".join(str(x) for x in content)
    return str(content or "").strip()

def get_fastfetch_summary() -> str:
    """Returns a short fastfetch output for LLM context (hidden from user)."""
    try:
        res = subprocess.run(
            "fastfetch --logo none",
            shell=True, text=True,
            capture_output=True, timeout=5
        )
        return res.stdout.strip() or "(fastfetch output unavailable)"
    except Exception:
        return "(fastfetch not installed)"

class LinuxCopilotState(BaseModel):
  user_request: str
  history: List[str] = Field(default_factory=list)
  last_plan: Optional[str] = None
  last_output: Optional[str] = None
  sudo_approved: bool = False
  tool_needed: bool = False
  
_DANGEROUS_PATTERNS = [
    re.compile(r"rm\s+-rf\s+/(?:\s|$)"),
    re.compile(r"mkfs(\.| )"),
    re.compile(r"dd\s+if="),
    re.compile(r":\(\)\s*\{\s*:\|\:\s*;\s*\}\s*;:"),
    re.compile(r"chmod\s+-R\s+777\s+/"),
    re.compile(r"chown\s+-R\s+\S+\s+/"),
    re.compile(r"\b(init\s+0|shutdown\b|reboot\b)\b"),
]

def _is_destructive(cmd: str) -> bool:
    for pat in _DANGEROUS_PATTERNS:
        if pat.search(cmd):
            return True
    return False


_RECENT_CMDS = {}
_RECENT_WINDOW_S = 8.0 

def _normalize(cmd: str) -> str:
   return re.sub(r"\s+", " ", cmd.strip())

@tool("run_shell_command", return_direct=True)
def run_shell_command(cmd: str) -> str:
    """Safely run a Linux shell command with optional sudo confirmation."""
    if not cmd or not cmd.strip():
        return "[ERROR] Empty command."

    cmd = cmd.strip()
    norm = _normalize(cmd)
    now = time.time()

    last = _RECENT_CMDS.get(norm, 0.0)
    if now - last < _RECENT_WINDOW_S:
        return f"[SKIPPED_DUPLICATE] {norm}"

    _RECENT_CMDS[norm] = now

    if _is_destructive(cmd):
        return "[DENIED] Potentially destructive command blocked."

    try:
        if "sudo" in cmd:
            confirm = input(f"[!] '{cmd}' needs admin privileges. Proceed? (y/n): ").strip().lower()
            if confirm != "y":
                return "[CANCELLED] sudo execution denied."
            password = getpass.getpass("[sudo] password: ")

            cmd = cmd.replace("sudo", "sudo -S -p ''", 1)
            proc = subprocess.run(
                cmd, shell=True, text=True,
                input=password + "\n",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=20
            )
        else:
            proc = subprocess.run(
                cmd, shell=True, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=20
            )
    except subprocess.TimeoutExpired:
        return "[TIMEOUT] Command exceeded 20s."
    except Exception as e:
        return f"[ERROR] {e}"
    finally:
        _RECENT_CMDS[norm] = time.time()

    out, err = (proc.stdout or "").strip(), (proc.stderr or "").strip()
    if proc.returncode != 0:
        if out and err:
            return f"{out}\n[stderr]\n{err}"
        return f"[stderr]\n{err or f'(exit {proc.returncode})'}"
    return out or "(no output)"



tools = [run_shell_command]

model_def = open("../docs/prompts/model_def.md", "r").read()
model_func = open("../docs/prompts/model_func.md", "r").read()
model_safety = open("../docs/prompts/model_safety.md", "r").read()

full_prompt = f"""{model_def}

{model_func}

{model_safety}

Your reasoning format must follow:
Thought: describe your reasoning
Action: choose one tool and its input
Observation: the tool's output
Answer: your final explanation in natural language

You are allowed to propose any valid command, including those requiring `sudo`.
However, the actual command execution is handled by a secure Python tool that:
- will ask the user for confirmation before running any command containing `sudo`
- will reject destructive or unsafe commands automatically.

Your role: plan commands clearly and safely, never ask for passwords directly.

Consider each message as a continuation of the previous one if there is an old message. 
Because we are in a session.

You are allowed to make multiple tool calls in sequence 
if the user's request requires multiple steps.
Each tool call should depend on the result of the previous one.

Remember, the user's computer is your computer. 
If you do something bad, you're doing something bad to yourself; 
if you do something good, 
you're both doing your job and doing something good for yourself.

If the task requires multiple sequential commands or steps,
ALWAYS end your message with the exact token 'CONTINUE' (in uppercase, on a new line)
to indicate you are ready for the next step.
If the task is done, end with 'DONE'.
After each tool output (observation), you must interpret it in natural language.
If the output is a list of files, summarize what was found and what the next step will be.
If the output shows an error, analyze why and propose a correction.
Never just print raw command output without commentary.
Your final message to the user must sound like a helpful assistant, not a terminal.
Avoid raw command outputs unless explicitly requested with “show raw output”.
"""

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", full_prompt),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

think_prompt = ChatPromptTemplate.from_messages([
    ("system", full_prompt),
    ("human", "{query}")
])
google = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7,
    google_api_key=API
)

llm = think_prompt | google 
agent = create_tool_calling_agent(llm=google, tools=tools, prompt=agent_prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

def analyse_req(state: LinuxCopilotState):
    """Model analiz yapar ve tool gerekip gerekmediğini belirler."""
    context = "\n".join(state.history)
    query = f"""
    Önceki bağlam:
    {context}

    Yeni istek: {state.user_request}

    1. Bu isteği anlamlandır.
    2. Tool kullanmak (örneğin terminal komutu çalıştırmak) gerekiyor mu?
    3. Kısa bir plan yaz ve sonuna 'TOOL=EVET' veya 'TOOL=HAYIR' yaz.
    4. Bilgisayarımı istediğin gibi bana sormadan kullanabilirsin.
    """
    res = llm.invoke(query)
    plan_text = res.content
    plan_text = normalize_content(res.content)
    state.last_plan = plan_text
    state.tool_needed = "tool=evet" in plan_text.lower()
    state.history.append(f"[Plan] {plan_text}")
    return state

def exec_cmd(state: LinuxCopilotState):
    """Execute command or chat depending on whether tool is needed."""
    cwd = subprocess.run("pwd", shell=True, text=True, capture_output=True).stdout.strip()

    context = "\n".join(state.history[-5:])

    base_query = f"Current working directory: {cwd}\n" \
f"User home: {os.path.expanduser('~')}\n" \
f"{context}\n\nKullanıcının isteği: {state.user_request}\n" \
f"Use absolute paths when referring to files or folders." \
+ """
If the task requires multiple steps, end your message with CONTINUE.
If the task is fully done, end with DONE.
⚠️ IMPORTANT INSTRUCTION:
You must NEVER write or propose raw Python code (like `subprocess.run(...)`).
If you need to run a shell command, you MUST use the tool `run_shell_command(cmd: str)`.
Do not write "Action: tool_code" or use code blocks — use the tool system only.

        """

    if state.tool_needed:
        res = executor.invoke({"input": base_query})
        out = res.get("output", "")
    else:
        res = llm.invoke(base_query)
        out = getattr(res, "content", str(res))

    state.last_output = out.strip()
    state.history.append(f"[Output] {out[:500]}")

    if "continue" in out.lower() or "CONTINUE" in out.lower():
        return state

    return state

def summarise_session(state: LinuxCopilotState):
    """Summarize what has happened in the session."""
    context = "\n".join(state.history[-6:])
    summary_prompt = f"""
Aşağıda Linux-Copilot ile yapılan son etkileşimlerin geçmişi bulunuyor.
Önceki aşamada sadece kod çalıştırılabildiği için kullanıcıya yeterli açıklama yapamıyoruz. 
O nedenle sen anlatır mısın? Ama bunu kullanıcıya çaktırma sanki iki model aynı anda o işi yapmış gibi.
Geçmiş:
{context}
"""
    res = llm.invoke(summary_prompt)
    summary = normalize_content(res.content)   
    state.last_output = summary
    state.history.append(f"[Reflection] {summary}")
    return state

graph = StateGraph(LinuxCopilotState)
graph.add_node("analyse", analyse_req)
graph.add_node("exec", exec_cmd)
graph.add_node("summarise", summarise_session)

graph.add_edge("analyse", "exec")
graph.add_conditional_edges(
    "exec",
    lambda state: "exec" 
    if "done" in state.last_output.strip().lower() 
    else "summarise"
)
graph.add_edge("summarise", END)
graph.set_entry_point("analyse")

memory = MemorySaver()
graph_app = graph.compile(checkpointer=memory)

@app.command()
def ask(q: str):
    """Asks a one-time question."""
    state = LinuxCopilotState(user_request=q)
    res = graph_app.invoke(state)
    console.rule("[bold green]🤖 Copilot: ")
    console.print(res.last_output)

@app.command()
def session():
    """Starts a session with memory."""
    sysinfo = get_fastfetch_summary()
    console.print(f"[dim]System context loaded\n")
    state = LinuxCopilotState(user_request=f"""
                              Sistem bilgisi:\n{sysinfo} 
                              You already have the following system information context (DO NOT try to re-detect it):
                              """)
    console.rule("[bold yellow]🧠 Linux Copilot Session")
    adapter = TypeAdapter(LinuxCopilotState)
    while True:
        if not (state.last_output and "continue" in state.last_output.lower()):
            q = input("\n👤 User: ")
            if q.lower() in ["exit", "quit"]:
                console.print("\n[bold red]Session finished")
                break
            state.user_request = q

        thread_id = "linux_session"
        state_dict = graph_app.invoke(state, config={"configurable": {"thread_id": thread_id}})
        state = adapter.validate_python(state_dict)

        console.print(f"\n🤖 [bold cyan]{state.last_output}[/bold cyan]")


if __name__ == "__main__":
  app()