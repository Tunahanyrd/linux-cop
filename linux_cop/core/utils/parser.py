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
from rich.live import Live
from rich.text import Text

from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage, SystemMessage, HumanMessage

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
        self.current_reasoning_live: Optional[Live] = None
        self.reasoning_buffer: str = ""
        self.seen_reasonings: set[str] = set()  
        self.streaming_content: str = ""  
        self.current_ai_message_id: Optional[str] = None  

    def reset_turn(self) -> None:
        self.seen_message_ids.clear()
        self.seen_reasonings.clear()  
        if self.current_reasoning_live:
            self.current_reasoning_live.stop()
            self.current_reasoning_live = None
        self.reasoning_buffer = ""
        self.streaming_content = ""
        self.current_ai_message_id = None

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
            block = f"```bash\n{content}\n```"

        console.print(Panel(
            Markdown(block),
            title=f"[bold cyan]🔧 Tool Output: {name}[/bold cyan]",
            border_style="cyan",
            style="on #1a1a2a"
        ))

    def _render_ai_message(self, ai_msg: Any, *, label: str = "💬 Agent") -> None:
        msg_id = getattr(ai_msg, "id", None)
        
        addkw = getattr(ai_msg, "additional_kwargs", {}) or {}
        fc = addkw.get("function_call")
        if fc and isinstance(fc, dict):
            name = fc.get("name", "tool_call")
            args = fc.get("arguments", "")
            
            reasoning_sig = f"{name}:{args[:50]}"
            if reasoning_sig in self.seen_reasonings:
                return  
            self.seen_reasonings.add(reasoning_sig)
            
            if args:
                try:
                    args_pretty = json.dumps(json.loads(args), ensure_ascii=False, indent=2)
                except Exception:
                    args_pretty = args
                panel = f"```json\n{args_pretty}\n```"
                console.print("\n")
                console.print(Panel(
                    Markdown(panel),
                    title=f"[bold yellow]🧠 Reasoning: {name}()[/bold yellow]",
                    border_style="yellow",
                    style="on #2a2a1a"  
                ))
            return
        
        is_chunk = hasattr(ai_msg, "chunk_position")
        chunk_pos = getattr(ai_msg, "chunk_position", None)
        
        if msg_id and msg_id != self.current_ai_message_id:
            if self.streaming_content:
                self._flush_streaming_content()
            self.current_ai_message_id = msg_id
            self.streaming_content = ""
        
        raw = _normalize_content(getattr(ai_msg, "content", ""))
        text = _strip_front_json_blob(raw).strip()
        
        if text:
            self.streaming_content += text
        
        response_meta = getattr(ai_msg, "response_metadata", {}) or {}
        is_last = chunk_pos == "last" or response_meta.get("finish_reason") is not None
        
        if is_last and self.streaming_content:
            self._flush_streaming_content()
    
    def _flush_streaming_content(self) -> None:
        """Biriken streaming content'i Panel içinde göster"""
        if not self.streaming_content:
            return
        
        text = _shorten(self.streaming_content, limit=6000)
        console.print(f"\n")
        console.print(Panel(
            Markdown(text),
            title="[bold cyan]💬 Linux COP Response[/bold cyan]",
            border_style="cyan",
            style="on #1a1a1a" 
        ))
        
        self.streaming_content = ""
        self.current_ai_message_id = None

    def handle_event(self, event: Any, *, show_middleware: bool = True) -> None:
        """
        Process a stream chunk
        
        stream_mode="updates" format:
          {'SystemInfoMiddleware.before_model': {'messages': [SystemMessage(...), HumanMessage(...)]}}
          {'model': {'messages': [AIMessage(...)]}}
          {'tools': {'messages': [ToolMessage(...)]}}
        
        stream_mode="messages" format:
          (message, metadata) tuple where message is AIMessage/ToolMessage/etc
        """
        if isinstance(event, tuple) and len(event) >= 2:
            message, metadata = event[0], event[1]
            
            if isinstance(message, (AIMessage, AIMessageChunk)):
                self._render_ai_message(message, label="💬 Agent")
            elif isinstance(message, ToolMessage):
                self._render_tool_message(message)
            elif isinstance(message, SystemMessage) and not self.printed_sysinfo:
                self._render_sysinfo([message])
            return
        
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
