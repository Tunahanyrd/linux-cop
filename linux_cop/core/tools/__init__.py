"""
core.tools
~~~~~~~~~~
LangChain v1 and classic prebuilt tool registry.
Many prebuilt LangChain tools.
"""

from langchain.tools import tool
from langchain_classic.tools import (
    DuckDuckGoSearchRun,
    ReadFileTool,
    WriteFileTool,
)
from linux_cop.core.tools.shell_tool import terminal_tool
from linux_cop.core.tools.python_repl_tool import python_repl_tool
from linux_cop.core.tools.user_info_tool import user_info_tool, get_user_info_tool
import sys
sys.dont_write_bytecode=True

def get_all_tools():
    """
    Return all active tools
    Use with create_agent(tools=get_all_tools()) 
    """
    tools = [
        DuckDuckGoSearchRun(),
        ReadFileTool(),
        WriteFileTool(),
        terminal_tool,
        python_repl_tool,
        user_info_tool,
        get_user_info_tool
    ]
    return tools