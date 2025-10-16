import os, json, sys
sys.dont_write_bytecode=True
from importlib import resources

def load():
    with resources.files("linux_cop.config").joinpath("credentials.json").open("r") as f:
        creds = json.load(f)
    for k,v in creds.items():
        os.environ[k] = v