from .tools import tools_, get_fastfetch_summary
import inquirer
from langchain_core.messages import SystemMessage
from rich.console import Console
from .i18n import t, MOODS

console = Console()
HISTORY = [get_fastfetch_summary()]
lang = None
def start_console():
    # Language selection
    global lang
    lang = inquirer.list_input("Language / Dil:", choices=["tr", "en"], default="tr")
    console.rule(f"[bold yellow]{t(lang, 'session_title')}")
    console.print(f"[dim]{t(lang, 'exit_hint')}[/dim]\n")
    console.print(f"[dim]{t(lang, 'img_hint')}[/dim]\n")

    console.print(f"[bold blue]{t(lang, 'system_loaded')}[/bold blue]\n")
    mood = inquirer.list_input(
        t(lang, "choose_mood"),
        choices=list(MOODS[lang].keys())
    )
    mood_filename = MOODS[lang[mood]]
    console.print(f"{t(lang, 'chosen_mood')}: {mood}")
    HISTORY.append(SystemMessage(t(lang, "respond_in_lang")))

    HISTORY.append(SystemMessage(f"""{t(lang, 'mood_selected')}"""))
    HISTORY.append(open(f"docs/prompts/mood/{mood_filename}.md").read())
    
    history_content = open("docs/memory/system/system_history.json", "r", encoding="utf-8").read().strip()
    if history_content:
        HISTORY.append(SystemMessage(f"""{t(lang, "history_content")}"""))
        HISTORY.append(history_content)

    macros = open("docs/memory/agent/user_macros.md", "r", encoding="utf-8").read().strip()
    if macros:
        HISTORY.append(SystemMessage(f"""{t(lang, "macros")} """))
        HISTORY.append(macros)