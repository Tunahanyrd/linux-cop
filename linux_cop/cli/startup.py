# cli/startup.py
import inquirer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from langchain_core.messages import SystemMessage
from linux_cop.cli.settings import load_context, open_settings
from pathlib import Path
import datetime
import time
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

ASCII_LOGO = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██╗     ██╗███╗   ██╗██╗   ██╗██╗  ██╗     ██████╗ ██████╗ ██████╗ 
║   ██║     ██║████╗  ██║██║   ██║╚██╗██╔╝    ██╔════╝██╔═══██╗██╔══██╗
║   ██║     ██║██╔██╗ ██║██║   ██║ ╚███╔╝     ██║     ██║   ██║██████╔╝
║   ██║     ██║██║╚██╗██║██║   ██║ ██╔██╗     ██║     ██║   ██║██╔═══╝ 
║   ███████╗██║██║ ╚████║╚██████╔╝██╔╝ ██╗    ╚██████╗╚██████╔╝██║     
║   ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝     ╚═════╝ ╚═════╝ ╚═╝     
║                                                           ║
║          Your Intelligent Linux Command Assistant        ║
╚═══════════════════════════════════════════════════════════╝
"""

def startup_screen():
    console = Console()
    print = console.print

    # Temizle ve logo göster
    console.clear()
    print(f"[bold cyan]{ASCII_LOGO}[/bold cyan]")
    
    # Loading animasyonu
    with console.status("[bold green]Initializing Linux COP...", spinner="dots") as status:
        time.sleep(0.5)
        status.update("[bold green]Loading configuration...")
        context = load_context()
        time.sleep(0.3)
        
        if not context or any(v is None for v in context.values()):
            console.clear()
            print(f"[bold cyan]{ASCII_LOGO}[/bold cyan]")
            print("[bold red]⚠️  Initial setup required — opening settings...[/bold red]")
            context = open_settings(context)
        
        status.update("[bold green]Loading AI models...")
        time.sleep(0.3)
        status.update("[bold green]Preparing environment...")
        time.sleep(0.3)

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

    # Sistem bilgisi tablosu
    table = Table(show_header=False, box=box.ROUNDED, border_style="cyan")
    table.add_column("Key", style="bold yellow", width=15)
    table.add_column("Value", style="bright_white")
    
    table.add_row("🤖 Model", model)
    table.add_row("🎭 Mood", mood.capitalize())
    table.add_row("🧠 Memory", "✓ Enabled" if memory else "✗ Disabled")
    table.add_row("📅 Date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    print("\n")
    print(Panel(
        table,
        title="[bold green]⚡ System Status[/bold green]",
        border_style="green",
        box=box.DOUBLE
    ))
    
    return context
