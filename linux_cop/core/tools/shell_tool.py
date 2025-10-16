"""
core.tools.shell_persistent
---------------------------
Kalıcı (persistent) bash oturumu.
LangChain v1.0 tool-calling ile uyumlu.
"""

import os
import pty
import subprocess
import select
import json
import datetime
from pathlib import Path
from typing_extensions import Annotated
from langchain.tools import tool
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

# Paket içindeki shell_history.json dosyasını kullan
LOG_FILE_RES = files("linux_cop.logs").joinpath("shell_history.json")
LOG_FILE = Path(str(LOG_FILE_RES))
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

class PersistentShell:
    def __init__(self):
        self.master_fd, self.slave_fd = pty.openpty()
        self.proc = subprocess.Popen(
            ["/bin/bash"],
            stdin=self.slave_fd,
            stdout=self.slave_fd,
            stderr=self.slave_fd,
            text=True,
            bufsize=0,
        )

    def run(self, command: str, timeout: int = 45) -> str:
        os.write(self.master_fd, (command + "\n").encode())

        output = []
        end_time = datetime.datetime.now().timestamp() + timeout

        while datetime.datetime.now().timestamp() < end_time:
            r, _, _ = select.select([self.master_fd], [], [], 0.1)
            if r:
                try:
                    chunk = os.read(self.master_fd, 4096).decode(errors="ignore")
                    if chunk:
                        output.append(chunk)

                    if chunk.strip().endswith("$") or chunk.strip().endswith("#"):
                        break
                except OSError:
                    break

        return "".join(output).strip()

SHELL = PersistentShell()
@tool("terminal_tool")
def terminal_tool(
    command: Annotated[str, "Command(s) to execute in persistent bash session."],
    timeout: Annotated[int, "Maximum seconds before timeout."] = 45,
) -> str:
    """Run shell command inside a persistent bash session."""
    try:
        result = SHELL.run(command, timeout=timeout)
        entry = {
            "time": datetime.datetime.now().isoformat(timespec="seconds"),
            "command": command,
            "output": result[:2000],
        }

        history = []
        if LOG_FILE.exists():
            try:
                history = json.loads(LOG_FILE.read_text())
            except Exception:
                pass
        history.append(entry)
        LOG_FILE.write_text(json.dumps(history[-100:], indent=2, ensure_ascii=False))

        return result or "(no output)"

    except Exception as e:
        return f"[error] {e}"
