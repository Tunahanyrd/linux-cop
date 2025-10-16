# cli/startup.py
import inquirer
from rich.console import Console
from rich.panel import Panel
from langchain_core.messages import SystemMessage
from linux_cop.cli.settings import load_context, open_settings
from pathlib import Path
import datetime
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

def startup_screen():
    console = Console()
    print = console.print

    context = load_context()

    if not context or any(v is None for v in context.values()):
        print("[bold red]Initial setup required — opening settings...[/bold red]")
        context = open_settings(context)

    console.rule("[bold yellow]LangChain CLI Agent[/bold yellow]")
    print(Panel("System initialization... 🧠", style="cyan"))

    mood = context["mood"]
    model = context["model"]
    memory = context["memory_enabled"]

    context["HISTORY"] = []

    try:
        mood_file = files("linux_cop.docs.prompts.mood").joinpath(f"{mood}.md")
        mood_content = mood_file.read_text(encoding="utf-8")
        context["HISTORY"].append(SystemMessage(f"Mood selected: {mood}"))
        context["HISTORY"].append(mood_content)
    except Exception as e:
        print(f"[yellow]⚠️ Missing mood file: [/yellow] {mood}.md ({e})")

    print(
        Panel(
            f"[bold blue]System Loaded Successfully[/bold blue]\n"
            f"[dim]Model: {model} | Mood: {mood} | Memory: {'ON' if memory else 'OFF'}[/dim]",
            expand=False,
        )
    )
    return context
