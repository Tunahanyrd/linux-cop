#!/usr/bin/env python3
import os, typer
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from rich.markdown import Markdown
from rich.panel import Panel
from pathlib import Path
import base64
import re
import json
from src import context
from src.session_start import start_console
from src.get_api import list_api_keys, add_api_key, delete_api_key, switch_api_key
from src import tools
from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
from langchain.agents import AgentExecutor

app = typer.Typer()

def get_history_file():
    shell = os.environ.get("SHELL", "")
    if "fish" in shell:
        return Path("~/.local/share/fish/fish_history").expanduser()
    elif "zsh" in shell:
        return Path("~/.zsh_history").expanduser()
    else:
        return Path("~/.bash_history").expanduser()

llm = context.llm

agent = context.agent
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
    context.llm = context.get_llm(context.model, tools=tools.tools_)
    if hasattr(context.llm, "agent"):
        print("[INFO] Local Granite agent active (smolagents).")
        context.agent = context.llm.agent
        context.executor = context.llm
    else:
        context.agent = create_tool_calling_agent(context.llm, tools.tools_, context.agent_prompt)
        context.executor = AgentExecutor(agent=context.agent, tools=tools.tools_, verbose=False)
    while True:
        try:
            q = context.console.input("[bold magenta]👤 User[/bold magenta]: ").strip()
            q = context.sanitize_input(q)
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
                    context.console.print(f"[red]⚠️ {t(lang, 'img_cmd')} [/red]")
                    continue

                image_path_str = match.group(2) or match.group(3)
                message_text = (match.group(4)).strip()

                image_path = Path(os.path.expanduser(image_path_str)).resolve()
                if not image_path.exists():
                    context.console.print(f"[bold red]❌ {t(lang, 'img_nf')}[/bold red] {image_path}")
                    continue

                with open(image_path, "rb") as f:
                    data = base64.b64encode(f.read()).decode("utf-8")

                context.console.print(f"[bold magenta]📷 [/bold magenta] {image_path.name}")

                llm = context.llm

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
            if hasattr(context.llm, "agent"):
                out = context.executor.invoke(q)  # Granite path: düz metin gönder
            else:
                out = context.executor.invoke({"input": q, "chat_history": context.HISTORY})

            if isinstance(out, dict):
                resp_text = out.get("output", "").strip()
            else:
                resp_text = str(out).strip()

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
