import difflib
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from linux_cop.cli.settings import open_settings

console = Console()
print = console.print

SYSTEM_COMMANDS = {
    "/settings": {
        "icon": "⚙️",
        "desc": "Open the settings menu",
        "func": open_settings,
    },
    "/help": {
        "icon": "❓",
        "desc": "Show available commands",
        "func": lambda ctx: show_help(),
    },
    "/exit": {
        "icon": "🚪",
        "desc": "Exit the program",
        "func": lambda ctx: exit_program(),
    },
    "/clear": {
        "icon": "🧹",
        "desc": "Clear the terminal screen",
        "func": lambda ctx: clear_screen(),
    },
}

AGENT_COMMANDS = {
    "/img": {
        "icon": "🖼️",
        "desc": "Send an image for analysis",
        "example": "/img ~/photo.png describe the picture"
    },
    "/file": {
        "icon": "📄",
        "desc": "Send a document or PDF for summarization",
        "example": "/file ~/report.pdf summarize"
    },
    "/audio": {
        "icon": "🎵",
        "desc": "Send an audio file for transcription",
        "example": "/audio ~/voice.wav transcribe"
    },
    "/video": {
        "icon": "🎬",
        "desc": "Send a video file for scene description",
        "example": "/video ~/clip.mp4 summarize"
    },
    "/draw": {
        "icon": "🎨",
        "desc": "Generate an image from text prompt",
        "example": "/draw a cyberpunk city at night"
    },
}

def show_help():
    """Show available commands in two categories."""
    
    # Sistem komutları tablosu
    system_table = Table(
        show_header=True, 
        header_style="bold cyan",
        box=box.ROUNDED,
        border_style="cyan"
    )
    system_table.add_column("Icon", style="yellow", width=5, justify="center")
    system_table.add_column("Command", style="bold green", no_wrap=True, width=15)
    system_table.add_column("Description", style="white")

    for cmd, info in SYSTEM_COMMANDS.items():
        system_table.add_row(info["icon"], cmd, info["desc"])

    print(Panel(
        system_table,
        title="[bold cyan]📋 System Commands[/bold cyan]",
        border_style="cyan",
        box=box.DOUBLE
    ))
    print("\n")

    # AI komutları tablosu
    agent_table = Table(
        show_header=True, 
        header_style="bold magenta",
        box=box.ROUNDED,
        border_style="magenta"
    )
    agent_table.add_column("Icon", style="yellow", width=5, justify="center")
    agent_table.add_column("Command", style="bold green", no_wrap=True, width=15)
    agent_table.add_column("Description", style="white", width=35)
    agent_table.add_column("Example", style="dim cyan")

    for cmd, info in AGENT_COMMANDS.items():
        agent_table.add_row(
            info["icon"], 
            cmd, 
            info["desc"],
            info["example"]
        )

    print(Panel(
        agent_table,
        title="[bold magenta]🤖 AI & Multimodal Commands[/bold magenta]",
        subtitle="[dim]For supported models only[/dim]",
        border_style="magenta",
        box=box.DOUBLE
    ))
    
    # İpucu
    print("\n")
    tip = Panel(
        "[bold yellow]💡 Pro Tip:[/bold yellow] Some terminals (like Konsole) support drag & drop!\n"
        "Just drag a file into the terminal to get its path automatically.",
        border_style="yellow",
        box=box.ROUNDED
    )
    print(tip)
    
    print("[dim italic]Note: AI commands are processed by the language model.[/dim italic]\n")

def clear_screen():
    """Clear the terminal screen."""
    console.clear()
    print("[green]✓[/green] Screen cleared!\n")

def exit_program():
    print("\n")
    print(Panel(
        "[bold yellow]👋 Thank you for using Linux COP!\n"
        "Session terminated successfully.[/bold yellow]",
        border_style="yellow",
        box=box.DOUBLE
    ))
    raise SystemExit

def handle_command(user_input, context):
    """Check if user input is a local command. Returns (handled: bool, updated_context)."""
    if not user_input.startswith("/"):
        return False, context

    if user_input.startswith(tuple(AGENT_COMMANDS.keys())):
        return False, context

    cmd = user_input.strip().split()[0]

    if cmd in SYSTEM_COMMANDS:
        SYSTEM_COMMANDS[cmd]["func"](context)
        return True, context

    suggestion = difflib.get_close_matches(cmd, SYSTEM_COMMANDS.keys(), n=1)
    if suggestion:
        print(f"\n[bold red]❌ Unknown command:[/bold red] [yellow]{cmd}[/yellow]")
        print(f"[dim]Did you mean[/dim] [bold cyan]{suggestion[0]}[/bold cyan][dim]?[/dim]\n")
    else:
        print(f"\n[bold red]❌ Unknown command:[/bold red] [yellow]{cmd}[/yellow]")
        print(f"[dim]Type[/dim] [bold cyan]/help[/bold cyan] [dim]for available commands.[/dim]\n")
    return True, context
