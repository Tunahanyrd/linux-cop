# cli/commands.py
import difflib
from rich.console import Console
from linux_cop.cli.settings import open_settings

console = Console()
print = console.print

COMMANDS = {
    "/settings": {
        "desc": "Open the settings menu",
        "func": open_settings
    },
    "/help": {
        "desc": "Show available commands",
        "func": lambda ctx: show_help()
    },
    "/exit": {
        "desc": "Exit the program",
        "func": lambda ctx: exit_program()
    },
}

def show_help():
    print("\n[bold cyan]Available Commands:[/bold cyan]")
    for cmd, info  in COMMANDS.items():
        print(f"[green]{cmd}[/green] - {info['desc']}")
    print()
    
def exit_program():
    print("[bold yellow]👋 Goodbye![/bold yellow]")
    raise SystemExit

def handle_command(user_input, context):
    """Check if user input is a local command. Returns (handled: bool, updated_context)."""
    if not user_input.startswith("/"):
        return False, context  
    cmd = user_input.strip().split()[0]

    if cmd in COMMANDS:
        COMMANDS[cmd]["func"](context)
        return True, context
    suggestion = difflib.get_close_matches(cmd, COMMANDS.keys(), n=1)
    if suggestion:
        print(f"[red]Unknown command:[/red] {cmd}. Did you mean [cyan]{suggestion[0]}[/cyan]?")
    else:
        print(f"[red]Unknown command:[/red] {cmd}. Type [cyan]/help[/cyan] for available commands.")
    return True, context  # handled