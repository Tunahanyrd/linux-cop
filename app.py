#!/usr/bin/env python3
import os, typer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from dotenv import load_dotenv
from rich.markdown import Markdown
from rich.panel import Panel
from pathlib import Path
from src.tools import tools_
import base64
import re
import json

from src.i18n import t
from src.session_start import console, HISTORY, start_console, lang
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
    with open("./docs/prompts/system_prompt.md", "r") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    console.print(f"[bold red]{t(lang, "f_not_found")}[/bold red]")
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
    with open("docs/memory/system/system_history.json", "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

from src.get_api import list_api_keys, add_api_key, delete_api_key

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
            q = console.input("[bold magenta]👤 User[/bold magenta]: ").strip()
            if q.lower() in {"exit", "quit"}:
                console.print(f"\n[bold red]{t(lang, "session_end")}[/bold red]")
                break
            if not q:
                continue

            if q.startswith("!img "):
                console.print("[red] Bu özellik geçici olarak devre dışıdır!")
                continue
                match = re.match(r'!img\s+(?:(["\'])(.*?)\1|(\S+))(?:\s+(.*))?$', q.strip())
                if not match:
                    console.print("[red]⚠️ Geçersiz !img kullanımı. Örnek: !img \"~/resim.png\" bu nedir[/red]")
                    continue

                image_path_str = match.group(2) or match.group(3)
                message_text = (match.group(4) or "Görseli analiz et").strip()

                image_path = Path(os.path.expanduser(image_path_str)).resolve()
                if not image_path.exists():
                    console.print(f"[bold red]❌ Görsel bulunamadı:[/bold red] {image_path}")
                    continue

                with open(image_path, "rb") as f:
                    data = base64.b64encode(f.read()).decode("utf-8")

                console.print(f"[bold magenta]📷 Görsel eklendi:[/bold magenta] {image_path.name}")

                llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.7)

                messages = [
                    SystemMessage(content=SYSTEM_PROMPT),
                    *HISTORY,
                    HumanMessage(content=[
                        {"type": "text", "text": message_text},
                        {"type": "image_url", "image_url": f"data:image/png;base64,{data}"}
                    ])
                ]

                resp = llm.invoke(messages)
                resp_text = resp.content if hasattr(resp, "content") else str(resp)
                console.print(Panel(resp_text, title="🤖 Yanıt", border_style="magenta"))

                HISTORY.extend([
                    HumanMessage(content=f"[IMG] {message_text}"),
                    AIMessage(content=resp_text)
                ])
                continue
            add_to_history("user", q)
            out = executor.invoke({"input": q, "chat_history": HISTORY})
            resp_text = out.get("output", "").strip()

            if not resp_text:
                console.print(f"[bold red]{t(lang, "resp_err")}[/bold red]\n")
                print(out)
                continue

            resp_md = Markdown(resp_text)
            console.print(Panel(resp_md, title=f"{t(lang, "response")}", border_style="cyan"))
            add_to_history("ai", resp_text)
            HISTORY.extend([
                HumanMessage(content=q),
                AIMessage(content=resp_text)
            ])

        except KeyboardInterrupt:
            console.print(f"\n\n[bold red]{t(lang, "terminate")}[/bold red]")
            break

        except Exception as e:
            console.print(f"[bold red]🚨 {t(lang, "err")}[/bold red] {e}\n")

if __name__ == "__main__":
    app()
