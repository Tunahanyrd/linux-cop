import os, json, sys
sys.dont_write_bytecode=True
from importlib import resources
from pathlib import Path
def load():
    creds_path = Path(resources.files("linux_cop.config").joinpath("credentials.json"))
    
    if not creds_path.exists():
        creds_path.parent.mkdir(parents=True, exist_ok=True)
        creds_path.write_text("{}", encoding="utf-8")
    try:
        with creds_path.open("r") as f:
            creds = json.load(f) or {}
    except json.JSONDecodeError:
        creds = {}
        
    for k,v in creds.items():
        os.environ[k] = v