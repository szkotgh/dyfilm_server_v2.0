from dotenv import load_dotenv
import json
import os

load_dotenv()
with open(os.path.join('src', 'code.json'), 'r') as file:
    code_dir = json.load(file)

def get_env(key: str):
    return os.environ[key]

def get_code(key: str):
    return code_dir[key], code_dir[key]['code']