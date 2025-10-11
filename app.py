#!/usr/bin/env python3
import os, typer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from rich.markdown import Markdown
from rich.panel import Panel
from pathlib import Path
from src.tools import tools_
import base64
import re
import json
from subprocess import run
from src import context
from src.session_start import start_console
from src.get_api import list_api_keys, add_api_key, delete_api_key, switch_api_key, get_api_key

API = get_api_key()
if not API or not API.strip():
    switch_api_key()

app = typer.Typer()

def get_history_file():
    shell = os.environ.get("SHELL", "")
    if "fish" in shell:
        return Path("~/.local/share/fish/fish_history").expanduser()
    elif "zsh" in shell:
        return Path("~/.zsh_history").expanduser()
    else:
        return Path("~/.bash_history").expanduser()

try:
    with open(context.BASE_DIR / "docs/prompts/system_prompt.md", "r") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    context.console.print(f"[bold red]{context.t(context.lang, 'f_not_found')}[/bold red]")
    exit(1)

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),   
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

llm = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash",
    temperature=0.7,
    google_api_key=API
)

agent = create_tool_calling_agent(llm, tools_, agent_prompt)
executor = AgentExecutor(
    agent=agent,
    tools=tools_,
    verbose=False,
)
chat_history = []

def add_to_history(role, content):
    chat_history.append({"role": role, "content": content})
    if len(chat_history) > 20:
        chat_history.pop(0)
    with open(context.BASE_DIR / "docs/memory/system/system_history.json", "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    LinuxCop main entrypoint.
    Runs 'cop session' by default if no command is provided.
    """
    if ctx.invoked_subcommand is None:
        context.console.print("[bold cyan]No command provided — starting interactive session...[/bold cyan]")
        session()
@app.command()
def apis():
    """List all registered Gemini API keys."""
    list_api_keys()

@app.command()
def add_api():
    """Add a new Gemini API key."""
    add_api_key()

@app.command()
def del_api():
    """Delete an existing Gemini API key."""
    delete_api_key()

@app.command()
def switch_api():
    """Switch to the next available Gemini API key."""
    switch_api_key()

@app.command()
def session():
    """Linux Copilot session."""
    start_console()
    while True:
        try:
            q = context.console.input("[bold magenta]👤 User[/bold magenta]: ").strip()
            if q.lower() in {"exit", "quit"}:
                context.console.print(f"\n[bold red]{context.t(context.lang, 'session_end')}[/bold red]")
                break
            if not q:
                continue
            
            if q.startswith("!img "): # temporary disabled
                context.console.print("[red] Temporary Disabled!")
                continue
                match = re.match(r'!img\s+(?:(["\'])(.*?)\1|(\S+))(?:\s+(.*))?$', q.strip())
                if not match:
                    context.console.print("[red]⚠️ Geçersiz !img kullanımı. Örnek: !img \"~/resim.png\" bu nedir[/red]")
                    continue

                image_path_str = match.group(2) or match.group(3)
                message_text = (match.group(4) or "Görseli analiz et").strip()

                image_path = Path(os.path.expanduser(image_path_str)).resolve()
                if not image_path.exists():
                    context.console.print(f"[bold red]❌ Görsel bulunamadı:[/bold red] {image_path}")
                    continue

                with open(image_path, "rb") as f:
                    data = base64.b64encode(f.read()).decode("utf-8")

                context.console.print(f"[bold magenta]📷 Görsel eklendi:[/bold magenta] {image_path.name}")

                llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.7)

                messages = [
                    SystemMessage(content=SYSTEM_PROMPT),
                    *context.HISTORY,
                    HumanMessage(content=[
                        {"type": "text", "text": message_text},
                        {"type": "image_url", "image_url": f"data:image/png;base64,{data}"}
                    ])
                ]

                resp = llm.invoke(messages)
                resp_text = resp.content if hasattr(resp, "content") else str(resp)
                context.console.print(Panel(resp_text, title="🤖 Yanıt", border_style="magenta"))

                context.HISTORY.extend([
                    HumanMessage(content=f"[IMG] {message_text}"),
                    AIMessage(content=resp_text)
                ])
                continue
            add_to_history("user", q)
            out = executor.invoke({"input": q, "chat_history": context.HISTORY})
            resp_text = out.get("output", "").strip()

            if not resp_text:
                context.console.print(f"[bold red]{context.t(context.lang, 'resp_err')}[/bold red]\n")
                print(out)
                continue

            resp_md = Markdown(resp_text)
            context.console.print(Panel(resp_md, title=f"{context.t(context.lang, 'response')}", border_style="cyan"))
            add_to_history("ai", resp_text)
            context.HISTORY.extend([
                HumanMessage(content=q),
                AIMessage(content=resp_text)
            ])

        except KeyboardInterrupt:
            context.console.print(f"\n\n[bold red]{context.t(context.lang, 'terminate')}[/bold red]")
            break

        except Exception as e:
            context.console.print(f"[bold red]🚨 {context.t(context.lang, 'err')}[/bold red] {e}\n")

if __name__ == "__main__":
    app()
