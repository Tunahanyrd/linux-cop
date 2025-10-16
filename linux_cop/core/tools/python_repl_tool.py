# core.tools.python_repl_tool
from langchain.tools import tool
import io
import sys
import contextlib

class PythonREPL:
    def __init__(self):
        self.env = {}

    def run(self, code: str) -> str:
        code = code.strip()
        buffer = io.StringIO()

        try:
            with contextlib.redirect_stdout(buffer):
                compiled = compile(code, "<repl>", "eval")
                result = eval(compiled, self.env)
                self.env["_"] = result
            output = buffer.getvalue()
            if result is not None:
                output += str(result)
            return output.strip() or "(no output)"

        except SyntaxError:
            try:
                with contextlib.redirect_stdout(buffer):
                    exec(code, self.env)
                output = buffer.getvalue()
                result = self.env.get("_", "")
                combined = (output + "\n" + str(result)).strip()
                return combined or "(no output)"
            except Exception as e:
                return f"[Python error] {e}"

        except Exception as e:
            return f"[Python error] {e}"


PYTHON = PythonREPL()


@tool("python_repl_tool")
def python_repl_tool(code: str) -> str:
    """
    Execute Python code in a persistent REPL environment.
    Captures print() output and return values.
    """
    return PYTHON.run(code)
