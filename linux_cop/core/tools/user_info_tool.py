# core/tools/user_info_tool.py
from langchain.tools import tool
import json, os
from pathlib import Path
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

USER_INFO_FILE = files("linux_cop.docs.memory.system").joinpath("user_info.json")
USER_INFO_PATH = Path(str(USER_INFO_FILE))
USER_INFO_PATH.parent.mkdir(parents=True, exist_ok=True)

if not USER_INFO_PATH.exists():
    USER_INFO_PATH.write_text("{}", encoding="utf-8")

@tool("user_info_tool")
def user_info_tool(data: dict) -> str:
    """
    Save or update user information persistently.
    """
    try:
        existing = json.load(USER_INFO_PATH.read_text(encoding="utf-8"))
        existing.update(data)
        USER_INFO_PATH.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
        return f"Memory updated: {list(data.keys())}"
    except Exception as e:
        return f"[error] failed to save memory: {e}"

@tool("get_user_info_tool")
def get_user_info_tool() -> str:
    """
    Retrieve saved user information as JSON.
    """
    try:
        data = json.loads(USER_INFO_PATH.read_text(encoding="utf-8"))
        if not data:
            return "(no memory saved yet)"
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"[error] failed to read memory: {e}"
