"""
LangGraph streaming parser (stateful)
- Uyumlu: agent.stream(..., stream_mode="updates") eventleri
- Destek: SystemInfoMiddleware, AIMessage, ToolMessage
- Özellikler:
  * Duplicate bastırma (id bazlı)
  * Boş / (no output) ToolMessage filtreleme
  * Gemini'nin list/dict content normalization
  * Markdown + panel render (rich)
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
import json
import re

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

try:
    from langchain_core.messages import AIMessage, ToolMessage, SystemMessage, HumanMessage
except Exception:
    AIMessage = type("AIMessage", (), {})
    ToolMessage = type("ToolMessage", (), {})
    SystemMessage = type("SystemMessage", (), {})
    HumanMessage = type("HumanMessage", (), {})

console = Console()


def _normalize_content(content: Any) -> str:
    """return list/dict to string"""
    if content is None:
        return ""
    if isinstance(content, list):
        joined = "\n".join(str(c) for c in content if c is not None)
        return joined
    if isinstance(content, dict):
        try:
            return json.dumps(content, ensure_ascii=False, indent=2)
        except Exception:
            return str(content)
    return str(content)


def _strip_front_json_blob(text: str) -> str:
    """
    Remove JSON block
    """
    if not text:
        return text
    return re.sub(r"^\s*\{.*?\}\s*\n*", "", text, flags=re.DOTALL)


def _looks_like_json(text: str) -> bool:
    t = text.strip()
    return (t.startswith("{") and t.endswith("}")) or (t.startswith("[") and t.endswith("]"))


def _shorten(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n… [output truncated]"


# ------------------------------------------------
# STATEFUL parser: duplicate and sysinfo controle
# ------------------------------------------------
class StreamingRenderer:
    def __init__(self) -> None:
        self.seen_message_ids: set[str] = set()
        self.printed_sysinfo: bool = False

    def reset_turn(self) -> None:
        self.seen_message_ids.clear()

    def _render_sysinfo(self, messages: List[Any]) -> None:
        if self.printed_sysinfo:
            return
        sys_txt = None
        for m in messages:
            if isinstance(m, SystemMessage):
                sys_txt = _normalize_content(getattr(m, "content", ""))
                break
        if not sys_txt:
            return

        sys_txt = _shorten(sys_txt, limit=1200)
        console.print(Panel.fit(Markdown(sys_txt), title="System Info (fastfetch)", border_style="magenta"))
        self.printed_sysinfo = True

    def _render_tool_message(self, tool_msg: Any) -> None:
        msg_id = getattr(tool_msg, "id", None)
        if msg_id and msg_id in self.seen_message_ids:
            return
        if msg_id:
            self.seen_message_ids.add(msg_id)

        name = getattr(tool_msg, "name", "tool")
        content = _normalize_content(getattr(tool_msg, "content", "")).strip()

        if not content or content == "(no output)":
            return

        if _looks_like_json(content):
            block = f"```json\n{content}\n```"
        else:
            block = f"```text\n{content}\n```"

        console.print(Panel.fit(Markdown(block), title=f"🧰 {name}", border_style="cyan"))

    def _render_ai_message(self, ai_msg: Any, *, label: str = "💬 Agent") -> None:
        msg_id = getattr(ai_msg, "id", None)
        if msg_id and msg_id in self.seen_message_ids:
            return
        if msg_id:
            self.seen_message_ids.add(msg_id)

        raw = _normalize_content(getattr(ai_msg, "content", ""))
        text = _strip_front_json_blob(raw).strip()
        if not text:
            return

        text = _shorten(text, limit=6000)
        console.print(f"\n[bold green]{label}:[/bold green]")
        console.print(Markdown(text))

        addkw = getattr(ai_msg, "additional_kwargs", {}) or {}
        fc = addkw.get("function_call")
        if fc and isinstance(fc, dict):
            name = fc.get("name", "tool_call")
            args = fc.get("arguments", "")
            if args:
                try:
                    args_pretty = json.dumps(json.loads(args), ensure_ascii=False, indent=2)
                except Exception:
                    args_pretty = args
                panel = f"```json\n{args_pretty}\n```"
                console.print(Panel.fit(Markdown(panel), title=f"🧭 Plan: {name}()", border_style="yellow"))

    def handle_event(self, event: Any, *, show_middleware: bool = True) -> None:
        """
        Process a stream chunk
        example event:
          {'SystemInfoMiddleware.before_model': {'messages': [SystemMessage(...), HumanMessage(...)]}}
          {'SummarizationMiddleware.before_model': None}
          {'model': {'messages': [AIMessage(...)]}}
          {'tools': {'messages': [ToolMessage(...)]}}
        """
        if not event or not isinstance(event, dict):
            return

        for key, payload in event.items():
            if key.endswith(".before_model"):
                if not show_middleware:
                    continue
                if not payload or not isinstance(payload, dict):
                    continue
                msgs = payload.get("messages", []) or []
                if "SystemInfoMiddleware" in key:
                    if not self.printed_sysinfo:
                        self._render_sysinfo(msgs)
                continue

            if key == "model":
                if not payload or not isinstance(payload, dict):
                    continue
                msgs = payload.get("messages", []) or []
                for m in msgs:
                    if isinstance(m, AIMessage):
                        self._render_ai_message(m, label="💬 Agent")
                continue

            if key == "tools":
                if not payload or not isinstance(payload, dict):
                    continue
                msgs = payload.get("messages", []) or []
                for m in msgs:
                    if isinstance(m, ToolMessage):
                        self._render_tool_message(m)
                continue

_renderer = StreamingRenderer()

def parse(event: Any, verbosity: str = "detailed", show_middleware: bool = True) -> None:
    """
    Call from the CLI: parse(event) in each stream chunk.
    verbosity is currently a placeholder; the filter can be expanded if needed.
    """
    _renderer.handle_event(event, show_middleware=show_middleware)

def reset_parser_state() -> None:
    """If you want to reset duplicates in the new user tour, call me."""
    _renderer.reset_turn()
