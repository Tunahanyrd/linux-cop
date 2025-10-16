"""
core.agents.base_agent
"""
import sys
sys.dont_write_bytecode = True
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import SummarizationMiddleware
from langchain.messages import HumanMessage, SystemMessage
from datetime import datetime, timezone
from pathlib import Path
try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files

from linux_cop.core.middleware.sys_info_mw import SystemInfoMiddleware
from linux_cop.core.tools import get_all_tools
from linux_cop.core.utils.parser import parse, reset_parser_state
from linux_cop.core.utils.parse_user import parse_user
from linux_cop.core.env.apis import load
import uuid

load()

checkpoint = InMemorySaver()

def build_agent(model_name: str = "google_genai:gemini-2.5-flash", 
                system_prompt: str = None):
    """
    Connect all tools and initialize agent
    """
    tools = get_all_tools()

    if system_prompt is None:
        prompt_file = files("linux_cop.docs.prompts").joinpath("system_prompt.md")
        system_prompt = prompt_file.read_text(encoding="utf-8")
    elif isinstance(system_prompt, Path):
        system_prompt = system_prompt.open("r", encoding="utf-8").read()
    middleware = [
        SystemInfoMiddleware(),
        SummarizationMiddleware(
            model=model_name,
            max_tokens_before_summary=2048
        )
    ]

    agent = create_agent(
        model=model_name,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=checkpoint,
        middleware=middleware
    )
    return agent

def run_agent(user_input: str,
              model_name: str = "google_genai:gemini-2.5-flash",
              thread_id: str = f"cli-session-{uuid.uuid4().hex[:8]}",
              verbosity: str= "minimal"):
    """
    Run agent and invoke LLM
    CLI and web interface calling here.
    """
    load()
    final_input = parse_user(user_input)
    agent = build_agent(model_name=model_name)

    config = {"configurable": {"thread_id": thread_id}}
    
    now = datetime.now().astimezone()
    time_msg = SystemMessage(
        content=f"Current local datetime: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    )
    input_data = {"messages": [time_msg, HumanMessage(content=final_input["content"])]}
    
    reset_parser_state()
    # stream_mode="messages" -> Her mesajı ayrı ayrı stream eder (reasoning dahil)
    # stream_mode="updates" -> Sadece node update'lerini stream eder
    for event in agent.stream(input_data, stream_mode="messages", config=config):
        if not event:
            continue
        parse(event, verbosity=verbosity, show_middleware=True)


        


        