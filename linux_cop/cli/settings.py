# cli/settings.py
import inquirer, yaml, json
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
SUPPORTED_PROVIDERS = [
    "openai",
    "anthropic",
    "azure_openai",
    "azure_ai",
    "cohere",
    "google_vertexai",
    "google_genai",
    "fireworks",
    "ollama",
    "together",
    "mistralai",
    "huggingface",
    "groq",
    "bedrock",
    "bedrock_converse",
    "google_anthropic_vertex",
    "deepseek",
    "ibm",
    "xai",
    "perplexity",
]
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
                "🤖 Select Provider and Model",
                "🎭 Change Mood",
                "🧠 Toggle Memory Mode",
                "💬 Response Detail Level",
                "🔑 Manage API Key",
                "💾 Save & Return",
                "❌ Cancel",
            ],
        )

        if choice == "🤖 Select Provider and Model":
            provider = inquirer.list_input(
                "Select Provider:",
                choices=sorted(SUPPORTED_PROVIDERS) + ["Custom"],
            )

            if provider == "Custom":
                provider = inquirer.text("Enter custom provider name").strip().lower()

            if not provider:
                print("[red]Provider name cannot be empty.[/red]")
                continue

            model_name = inquirer.text(
                f"Enter model name for {provider} (e.g. gpt-4o, gemini-2.5-pro, claude-4.5-sonnet):"
            ).strip()

            if not model_name:
                print("[red]Model name cannot be empty.[/red]")
                continue

            full_model = f"{provider}:{model_name}"
            context["model"] = full_model
            print(f"[green]✅ Model set to:[/green] {full_model}")


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

        elif choice == "🔑 Manage API Key":
            creds_path = Path(str(files("linux_cop.config").joinpath("credentials.json")))
            creds_path.parent.mkdir(parents=True, exist_ok=True)

            if creds_path.exists():
                try:
                    creds = json.loads(creds_path.read_text(encoding="utf-8")) or {}
                except Exception:
                    creds = {}
            else:
                creds = {}

            while True:
                console.rule("[bold cyan]🔑 API Key Manager[/bold cyan]")

                if not creds:
                    print("[dim]No API keys stored yet.[/dim]")
                else:
                    for name, key in creds.items():
                        shown = key[:6] + "..." if len(key) > 6 else key
                        print(f"[yellow]- {name}:[/yellow] {shown}")

                action = inquirer.list_input(
                    "Select an action: ",
                    choices=[
                        "➕ Add / Update Key",
                        "🗑️ Delete Key",
                        "⬅️ Back to Settings",
                    ],
                )

                if action == "➕ Add / Update Key":
                    provider = inquirer.text("Enter provider name (e.g. GOOGLE, OPENAI, ANTHROPIC)").strip().upper()
                    if not provider:
                        print("[red]Provider name cannot be empty.[/red]")
                        continue
                    key_name = f"{provider}_API_KEY"
                    new_key = inquirer.text(f"Enter value for {key_name}").strip()
                    if not new_key:
                        print("[red]Key cannot be empty.[/red]")
                        continue

                    try:
                        existing = json.loads(creds_path.read_text(encoding="utf-8")) if creds_path.exists() else {}
                    except Exception:
                        existing = {}

                    existing[key_name] = new_key
                    creds_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")

                    creds = existing  
                    print(f"[green]✅ Saved {key_name}[/green]")

                elif action == "🗑️ Delete Key":
                    if not creds:
                        print("[dim]Nothing to delete.[/dim]")
                        continue
                    to_delete = inquirer.list_input(
                        "Select key to delete:",
                        choices=list(creds.keys()) + ["Cancel"],
                    )
                    if to_delete != "Cancel":
                        creds.pop(to_delete, None)
                        creds_path.write_text(json.dumps(creds, indent=2, ensure_ascii=False), encoding="utf-8")
                        print(f"[red]❌ Deleted {to_delete}[/red]")

                elif action == "⬅️ Back to Settings":
                    break
                
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
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f) or {}
        except yaml.YAMLError:
            data = {}

    for k, v in DEFAULTS.items():
        data.setdefault(k, v)

    return data
