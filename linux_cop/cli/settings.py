# cli/settings.py
import inquirer
import yaml
from pathlib import Path
from rich.console import Console
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

console = Console()
print = console.print

try:
    CONFIG_PATH = Path(str(files("linux_cop.config").joinpath("settings.yaml")))
except Exception:
    CONFIG_PATH = Path(__file__).parent.parent / "config" / "settings.yaml"

DEFAULTS = {
    "model": "google_genai:gemini-2.5-flash",
    "mood": "minimalist",
    "memory_enabled": True,
    "verbosity": "minimal"
}

MOODS = ["minimalist", "explanatory", "serious", "humorous", "instructor"]
MODEL_CHOICES = ["google_genai:gemini-2.5-flash", "google_genai:gemini-2.5-pro"]
VERBOSITY_CHOICES = ["minimal", "detailed"]


def open_settings(context=None):
    """Interactive settings menu. Creates or updates settings.yaml."""
    if context is None:
        context = load_context()

    console.rule("[bold yellow]⚙️  Settings Menu[/bold yellow]")

    while True:
        choice = inquirer.list_input(
            "Select an optaion:",
            choices=[
                "🤖 Change Model",
                "🎭 Change Mood",
                "🧠 Toggle Memory Mode",
                "💬 Response Detail Level",
                "💾 Save & Return",
                "❌ Cancel",
            ],
        )

        if choice == "🤖 Change Model":
            new_model = inquirer.list_input(
                "Select Model:",
                choices=MODEL_CHOICES,
                default=context.get("model", DEFAULTS["model"]),
            )
            context["model"] = new_model
            print(f"[green]Model set to:[/green] {new_model}")

        elif choice == "🎭 Change Mood":
            new_mood = inquirer.list_input(
                "Select Mood:",
                choices=MOODS,
                default=context.get("mood", DEFAULTS["mood"]),
            )
            context["mood"] = new_mood
            print(f"[green]Mood set to:[/green] {new_mood}")

        elif choice == "🧠 Toggle Memory Mode":
            new_state = not context.get("memory_enabled", True)
            context["memory_enabled"] = new_state
            print(f"[yellow]Memory mode:[/yellow] {'ON' if new_state else 'OFF'}")

        elif choice == "💾 Save & Return":
            save_context(context)
            print("[bold green]✅ Settings saved.[/bold green]\n")
            return context

        elif choice == "❌ Cancel":
            print("[dim]Returning without saving...[/dim]")
            return context
        elif choice == "💬 Response Detail Level":
            new_v = inquirer.list_input(
                "Select response verbosity:",
                choices=VERBOSITY_CHOICES,
                default=context.get("verbosity", "minimal")
            )
            context["verbosity"] = new_v
            print(f"[cyan]Verbosity set to:[/cyan] {new_v}")

def save_context(context):
    """Write settings.yaml with only serializable config keys."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    serializable = {
        "model": context.get("model", DEFAULTS["model"]),
        "mood": context.get("mood", DEFAULTS["mood"]),
        "memory_enabled": context.get("memory_enabled", True),
        "verbosity": context.get("verbosity", "minimal"),
    }

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(serializable, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def load_context():
    """Load YAML settings. If missing keys, fill with defaults."""
    if not CONFIG_PATH.exists():
        return DEFAULTS.copy()

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f) or {}
        except yaml.YAMLError:
            data = {}

    for k, v in DEFAULTS.items():
        data.setdefault(k, v)

    return data
