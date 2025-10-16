#!/usr/bin/env python3
# cli/main.py
from linux_cop.cli.startup import startup_screen
from linux_cop.cli.commands import handle_command
from linux_cop.core.agents.base_agent import run_agent
from linux_cop.core.utils.parser import parse
from rich.console import Console
from rich.markdown import Markdown
import sys, signal

def _handle_sigint(signum, frame):
    print("\n[bold yellow]👋 Goodbye![/bold yellow]")
    sys.exit(0)

console = Console()
print = console.print

def main():
    signal.signal(signal.SIGINT, _handle_sigint)
    context = startup_screen()
    session = "cli-session"

    print("\nType [bold cyan]/help[/bold cyan] for commands.")
    print("[dim]Type /exit to quit.[/dim]\n")

    while True:
        user_input = input("🧠 You: ").strip()
        
        handled, context = handle_command(user_input, context)
        if handled:
            continue
        verbosity = context.get("verbosity", "minimal")

        run_agent(
            user_input,
            model_name=context["model"],
            thread_id=session,
            verbosity=verbosity
        )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[bold yellow]👋 Goodbye![/bold yellow]")
        raise SystemExit
    except Exception as e:
        print("An error occurred: ", e)

