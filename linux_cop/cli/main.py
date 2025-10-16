#!/usr/bin/env python3
# cli/main.py
import traceback
try:
    from linux_cop.cli.startup import startup_screen
    from linux_cop.cli.commands import handle_command
    from linux_cop.core.agents.base_agent import run_agent
    from linux_cop.core.utils.parser import parse
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich import box
    import sys, signal
except Exception as e:
    traceback.print_exc()
    print("an exception occured", e)
    raise SystemExit(-1)

def _handle_sigint(signum, frame):
    console = Console()
    console.print("\n")
    console.print(Panel(
        "[bold yellow]👋 Thank you for using Linux COP!\n"
        "Session terminated successfully.[/bold yellow]",
        border_style="yellow",
        box=box.DOUBLE
    ))
    sys.exit(0)

console = Console()
print = console.print

def main():
    signal.signal(signal.SIGINT, _handle_sigint)
    context = startup_screen()
    session = "cli-session"

    # Komut bilgisi
    print("\n")
    help_panel = Panel(
        "[bold cyan]💡 Quick Tips[/bold cyan]\n\n"
        "• Type your command or question naturally\n"
        "• Use [bold cyan]/help[/bold cyan] to see all commands\n"
        "• Press [bold cyan]Ctrl+C[/bold cyan] to exit anytime\n"
        "• Use [bold cyan]/settings[/bold cyan] to change configuration",
        border_style="blue",
        box=box.ROUNDED
    )
    print(help_panel)
    print("\n")

    command_count = 0
    
    while True:
        try:
            user_input = Prompt.ask(
                "\n[bold green]┌─[[/bold green][bold cyan]🤖 Linux COP[/bold cyan][bold green]][/bold green]"
                "\n[bold green]└─>[/bold green]"
            ).strip()
            
            if not user_input:
                continue
                
            command_count += 1
            
            handled, context = handle_command(user_input, context)
            if handled:
                continue
            verbosity = context.get("verbosity", "minimal")
            
            # GERÇEK ZAMANLI STREAMING - Processing mesajını kaldırdık
            # Şimdi düşünme zinciri (reasoning), tool çağrıları ve cevap CANLI gösterilecek
            try:
                run_agent(
                    user_input,
                    model_name=context["model"],
                    thread_id=session,
                    verbosity=verbosity
                )
            except Exception as e:
                console.print(f"\n[bold red]❌ Error:[/bold red] {e}\n")
                
        except KeyboardInterrupt:
            _handle_sigint(None, None)
        except EOFError:
            _handle_sigint(None, None)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        _handle_sigint(None, None)
    except Exception as e:
        console = Console()
        console.print(f"\n[bold red]💥 Fatal Error:[/bold red] {e}\n")
        traceback.print_exc()
    except KeyboardInterrupt:
        print("[bold yellow]👋 Goodbye![/bold yellow]")
        raise SystemExit
    except Exception as e:
        print("An error occurred: ", e)

