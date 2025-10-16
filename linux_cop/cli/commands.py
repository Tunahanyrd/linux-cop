import difflib
from rich.console import Console
from rich.table import Table
from linux_cop.cli.settings import open_settings

console = Console()
print = console.print

SYSTEM_COMMANDS = {
    "/settings": {
        "desc": "Open the settings menu",
        "func": open_settings,
    },
    "/help": {
        "desc": "Show available commands",
        "func": lambda ctx: show_help(),
    },
    "/exit": {
        "desc": "Exit the program",
        "func": lambda ctx: exit_program(),
    },
}

AGENT_COMMANDS = {
    "/img": "Send an image for analysis. Example: /img ~/photo.png describe the picture",
    "/file": "Send a document or PDF for summarization. Example: /file ~/report.pdf summarize",
    "/audio": "Send an audio file for transcription. Example: /audio ~/voice.wav transcribe",
    "/video": "Send a video file for scene description. Example: /video ~/clip.mp4 summarize",
    "/draw": "Generate an image from text prompt. Example: /draw a cyberpunk city at night",
}

def show_help():
    """Show available commands in two categories."""
    table = Table(title="Available Commands (For supported models only)", show_header=True, header_style="bold cyan")
    table.add_column("Command", style="green", no_wrap=True)
    table.add_column("Description", style="white")
    table.caption("Some terminals (for example 'Konsole' support drag end drop)")
    for cmd, info in SYSTEM_COMMANDS.items():
        table.add_row(cmd, info["desc"])

    console.print(table)

    agent_table = Table(title="AI & Multimodal Commands", show_header=True, header_style="bold magenta")
    agent_table.add_column("Command", style="green", no_wrap=True)
    agent_table.add_column("Description", style="white")

    for cmd, desc in AGENT_COMMANDS.items():
        agent_table.add_row(cmd, desc)

    console.print(agent_table)
    console.print("[dim]Note: AI commands are processed by the language model, not the local system.[/dim]\n")

def exit_program():
    print("[bold yellow]👋 Goodbye![/bold yellow]")
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
        print(f"[red]Unknown command:[/red] {cmd}. Did you mean [cyan]{suggestion[0]}[/cyan]?")
    else:
        print(f"[red]Unknown command:[/red] {cmd}. Type [cyan]/help[/cyan] for available commands.")
    return True, context
