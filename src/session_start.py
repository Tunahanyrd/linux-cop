import inquirer
from langchain_core.messages import SystemMessage
from src import context

def start_console():
    # Language selection
    context.lang = inquirer.list_input("Language / Dil:", choices=["tr", "en"], default="tr")
    context.model = inquirer.list_input("Model:", choices=context.model_choices, default="gemini-2.5-flash")
    
    # Initialize HISTORY with fastfetch
    context.HISTORY.append(context.get_fastfetch_summary())
    context.HISTORY.append(f"User's selected language is: {context.lang}, please pay attention to that.")
    context.console.rule(f"[bold yellow]{context.t(context.lang, 'session_title')}")
    context.console.print(f"[dim]{context.t(context.lang, 'exit_hint')}[/dim]\n")
    context.console.print(f"[dim]{context.t(context.lang, 'img_hint')}[/dim]\n")

    context.console.print(f"[bold blue]{context.t(context.lang, 'system_loaded')}[/bold blue]\n")
    mood = inquirer.list_input(
        context.t(context.lang, "choose_mood"),
        choices=list(context.MOODS[context.lang].keys())
    )
    mood_key = mood.lower()
    mood_filename = context.MOODS.get(context.lang, {}).get(mood_key)
    if not mood_filename:
        mood_filename = context.MOODS.get(context.lang, {}).get(list(context.MOODS.get(context.lang, {}).keys())[0], "minimalist")
    context.console.print(f"{context.t(context.lang, 'chosen_mood')}: {mood}")
    context.HISTORY.append(SystemMessage(context.t(context.lang, "respond_in_lang")))

    context.HISTORY.append(SystemMessage(context.t(context.lang, 'mood_selected').format(mood=mood_key)))
    context.HISTORY.append(open(context.BASE_DIR / f"docs/prompts/mood/{mood_filename}.md").read())
    
    history_content = open(context.BASE_DIR / "docs/memory/system/system_history.json", "r", encoding="utf-8").read().strip()
    if history_content:
        context.HISTORY.append(SystemMessage(f"""{context.t(context.lang, "history_content")}"""))
        context.HISTORY.append(history_content)

    macros = open(context.BASE_DIR / "docs/memory/agent/user_macros.md", "r", encoding="utf-8").read().strip()
    if macros:
        context.HISTORY.append(SystemMessage(f"""{context.t(context.lang, "macros")} """))
        context.HISTORY.append(macros)