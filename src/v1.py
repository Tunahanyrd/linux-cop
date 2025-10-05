import os, subprocess, typer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain import hub
from dotenv import load_dotenv
from rich.console import Console
import glob
from pathlib import Path
load_dotenv()
API = os.getenv("GEMINI_API_KEY")

console = Console()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro",
                             temperature=0.2,
                             google_api_key=API)

@tool("run_shell_command", return_direct=True)
def run_shell_command(cmd: str) -> str:
  """Run a safe Linux shell command and return its output."""
  try:
    res = subprocess.run(
      cmd, shell=True, check=True, capture_output=True, text=True, timeout=10
    )
    return res.stdout.strip()
  except subprocess.CalledProcessError as e:
    return f"Error: {e.stderr.strip()}"
  except Exception as e:
    return f"Execution failed: {e}"

tools = [run_shell_command]

model_def = open("../docs/prompts/model_def.md", "r").read()
model_func = open("../docs/prompts/model_func.md", "r").read()
model_safety = open("../docs/prompts/model_safety.md", "r").read()

full_prompt = f"""{model_def}

{model_func}

{model_safety}

Your reasoning format must follow:
Thought: describe your reasoning
Action: choose one tool and its input
Observation: the tool's output
Answer: your final explanation in natural language
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", full_prompt),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

app = typer.Typer(help="Linux Copilot — Natural language terminal assistant")

@app.command()
def ask(q: str):
  """Ask the Linux Copilot a question in natural language."""
  console.rule("[bold green]🧠 Linux Copilot")
  
  resp = executor.invoke({"input": q})
  console.print(resp["output"])

if __name__ == "__main__":
    app()