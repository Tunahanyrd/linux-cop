from rich.console import Console
from pathlib import Path
from typing import Dict, List
import subprocess
import json
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
console = Console()

HISTORY: List = []

lang: str = "tr"

BASE_DIR = Path(__file__).resolve().parent.parent

MESSAGES: Dict[str, Dict[str, str]] = json.loads((BASE_DIR / "docs/i18n/MESSAGES.json").read_text(encoding="utf-8"))
MOODS = json.loads((BASE_DIR / "docs/i18n/MOODS.json").read_text(encoding="utf-8"))

llm=None
agent=None
executor=None
def t(lang: str, key: str) -> str:
    """Translate key to given language; fallback to English."""
    table = MESSAGES.get(lang) or MESSAGES["en"]
    return table.get(key, MESSAGES["en"].get(key, key))

try:
    with open(BASE_DIR / "docs/prompts/system_prompt.md", "r") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    console.print(f"[bold red]{t(lang, 'f_not_found')}[/bold red]")
    exit(1)

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),   
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

def t(language: str, key: str) -> str:
    """Translate key to given language; fallback to English."""
    table = MESSAGES.get(language) or MESSAGES["en"]
    return table.get(key, MESSAGES["en"].get(key, key))

def get_fastfetch_summary() -> str:
    """Returns a short fastfetch output for LLM context."""
    try:
        res = subprocess.run(
            "fastfetch --logo none",
            shell=True,
            text=True,
            capture_output=True,
            timeout=5
        )
        return "Sistem özellikleri: " + (res.stdout.strip() or "(fastfetch output unavailable)")
    except Exception:
        return "(fastfetch not installed)"

CMD_LOG = Path.home() / ".linuxcopilot_cmdlog.json"

model_choices = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",

    "ibm-granite/granite-4.0-micro",
    "ibm-granite/granite-4.0-micro-base",
    "ibm-granite/granite-4.0-h-micro",
    "ibm-granite/granite-4.0-h-micro-base",
    "ibm-granite/granite-4.0-h-tiny",
    "ibm-granite/granite-4.0-h-tiny-base",
    "ibm-granite/granite-4.0-h-small",
    "ibm-granite/granite-4.0-h-small-base",
    "ibm-granite/granite-4.0-tiny-preview",
    "ibm-granite/granite-4.0-tiny-base-preview",
]

def get_llm(selection: str, tools=None):
    if selection.startswith("gemini"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        from src.get_api import get_api_key
        API = get_api_key()
        return ChatGoogleGenerativeAI(
            model=selection,
            temperature=0.7,
            google_api_key=API,
        )

    elif selection.startswith("ibm-granite"):
        from src.smolagent_to_langchain import Wrapper
        print(f"[INFO] Using local Granite model: {selection}")
        return Wrapper(selection, tools or [])

    else:
        from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
        model = HuggingFaceEndpoint(
            repo_id=selection,
            max_new_tokens=512,
            top_k=10,
            top_p=0.95,
            temperature=0.01,
            repetition_penalty=1.03,
            provider="auto",
        )
        return ChatHuggingFace(llm=model)

chat_history = []
def sanitize_input(text: str) -> str:
    """
    Docker/locale sorunları için surrogate karakterleri temizler.
    UTF-8 encoding hatalarını önler.
    """
    if not text:
        return text
    return text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
