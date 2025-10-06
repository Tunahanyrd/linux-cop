from langchain_community.tools import ShellTool
from pydantic import BaseModel, Field
from langchain_community.tools import (
    ShellTool, WriteFileTool, ReadFileTool, WriteFileTool,
    ListDirectoryTool, MoveFileTool, DeleteFileTool, FileSearchTool, WikipediaQueryRun, 
    DuckDuckGoSearchRun
)
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
import subprocess, mimetypes, os, datetime, base64
from langchain.tools import tool
from langchain_core.tools import StructuredTool
from PIL import Image
from pathlib import Path
from io import BytesIO
API = os.getenv("GEMINI_API_KEY")

MEM_PATH = Path("docs/memory")

class SilentTool(StructuredTool):
    def run(self, *args, **kwargs):
        result = super().run(*args, **kwargs)
        if isinstance(result, dict) and "data" in result:
            result["data"] = "<hidden>"
        return result
    
def get_fastfetch_summary() -> str:
    """Returns a short fastfetch output for LLM context (hidden from user)."""
    try:
        res = subprocess.run(
            "fastfetch --logo none",
            shell=True, text=True,
            capture_output=True, timeout=5
        )
        return "Sistem özellikler: " + res.stdout.strip() or "(fastfetch output unavailable)"
    except Exception:
        return "(fastfetch not installed)"
    
class ShellInputGemini(BaseModel):
    """Gemini ile uyumlu tek komutluk shell input."""
    command: str = Field(description="Single shell command to execute.")

class GeminiShellTool(ShellTool):
    """ShellTool'un Gemini uyumlu versiyonu."""
    name: str = "terminal"
    description: str = "Run a single shell command on this Linux machine."
    args_schema: type[BaseModel] = ShellInputGemini

    def _run(self, command: str, **kwargs) -> str:
        if isinstance(command, list):
            command = " && ".join(command)
        print(f"Executing (Gemini mode): {command}")
        try:
            return self.process.run([command])
        except Exception as e:
            return f"Error executing command: {e}"
        
def get_fastfetch_summary() -> str:
    """Returns a short fastfetch output for LLM context (hidden from user)."""
    try:
        res = subprocess.run(
            "fastfetch --logo none",
            shell=True, text=True,
            capture_output=True, timeout=5
        )
        return "Sistem özellikler: " + res.stdout.strip() or "(fastfetch output unavailable)"
    except Exception:
        return "(fastfetch not installed)"
    
def is_binary(path):
    mime = mimetypes.guess_type(path)[0]
    if mime is None:
        return False
    return not mime.startswith("text")

@tool
def tool_read_file(path: str, chunk_size: int = 2048, start: int = 0) -> str:
  """Reads a text file in chunks and returns a small portion of its content starting from `start`.
  Only use this tool for **text-based** files (UTF-8). 
  Binary or unreadable files (like images, audio, or executables) must be skipped."""
  try:
    if is_binary(path):
      return "[binary file detected — skipped]"
    with open(path, "r", encoding="utf-8") as f:
        f.seek(start)
        data = f.read(chunk_size)
        next_pos = f.tell()
    if not data:
      return "[EOF]"
    return f"[chunk {start}-{next_pos}]\n{data}"
  except Exception as e:
    return f"[ERROR] {e}"

def capture_screen() -> str:
    """
    Takes a screenshot in KDE/Wayland using Spectacle, sends it to a multimodal LLM,
    and returns the model’s visual description of the screen.
    !!!Temporary inactive!!!
    """
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"/home/{os.getlogin()}/Masaüstü/screenshot_{ts}.png"
    subprocess.run(["spectacle", "-b", "-n", "-o", path], check=True)

    img = Image.open(path)
    buf = BytesIO()
    img.save(buf, format="PNG")
    data = base64.b64encode(buf.getvalue()).decode("utf-8")

    return [{
        "type": "image",
        "source_type": "base64",
        "mime_type": "image/png",
        "data": data,
        "description": "Current desktop screenshot"
    }] 

capture_screen = SilentTool.from_function(capture_screen)

@tool
def save_memory(msg: str) -> str:
    """
    With this tool, 
    you can delete user information from memory 
    whenever you want to delete something.
    """
    path = Path("docs/memory/agent")
    try:
        with open(path / "agent_memory.md", "a+", encoding="utf-8") as f:
            f.write(msg + "\n")
        return "Kaydedildi."
    except Exception as e:
        return f"[ERROR] {e}"

@tool
def delete_memory(msg: str) -> str:
    """
    With this tool, 
    you can save important information about the user to memory 
    when you learn it.
    """
    path = Path("docs/memory/agent")
    try:
        with open(path / "agent_memory.md", "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(path / "agent_memory.md", "w", encoding="utf-8") as f:
            for line in lines:
                if msg not in line:
                    f.write(line)
        return f"Silindi: {msg}"
    except Exception as e:
        return f"[ERROR] {e}"

@tool
def user_macros(macro: str, command: str):
    """
    With this tool, 
    you can save user macros to the memory 
    when user want to you
    """
    path = Path("docs/memory/agent")
    try:
        with open(path / "user_macros.md", "a+", encoding="utf-8") as f:
            f.write("macro --> command", "\n")
        return "Makro kaydedildi. kullanmak için !{macro}."
    except Exception as e:
        return f"[ERROR] {e}"
    
@tool
def delete_macro(macro: str) -> str:
    """
    With this tool, 
    you can delete user macros on the memory 
    """
    path = Path("docs/memory/agent")
    try:
        with open(path / "user_macros.md", "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(path / "user_macros.md", "w", encoding="utf-8") as f:
            for line in lines:
                if macro not in line:
                    f.write(line)
        return f"Makro silindi: {macro}"
    except Exception as e:
        return f"[ERROR] {e}"
    
tools_ = [
    GeminiShellTool(),
    tool_read_file,  
    WriteFileTool(),
    ListDirectoryTool(),
    MoveFileTool(),
    DeleteFileTool(),
    FileSearchTool(),
    WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),
    DuckDuckGoSearchRun(),
    capture_screen,
    save_memory,
    delete_memory,
    user_macros,
    delete_macro
]

