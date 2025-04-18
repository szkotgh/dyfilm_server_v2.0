from dotenv import load_dotenv
import datetime
import json
import os
from flask import request
import hashlib
import logging

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# functions
with open(os.path.join('static', 'code.json'), 'r') as file:
    code_dir = json.load(file)

def get_env(key: str):
    return os.environ[key]

def get_code(key: str, info = None):
    code = code_dir[key]
    
    if info is not None:
        code['info'] = info
    
    return code, code['code']

def get_ip(): 
    user_ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0].strip()
    return f'{user_ip}'

def gen_hash(key: str = None):
    if key is None:
        return str(os.urandom(16).hex())
    return str(hashlib.md5(key.encode()).hexdigest())

def get_now_datetime():
    return datetime.datetime.now()

def get_now_datetime_str():
    return get_now_datetime().strftime(DATETIME_FORMAT)

def convert_string_to_datetime(date_str: str):
    try:
        return datetime.datetime.strptime(date_str, DATETIME_FORMAT)
    except ValueError:
        return False

def get_extension(filename: str) -> str:
    if '.' in filename:
        return filename.rsplit('.', 1)[-1].lower()
    return False

def is_valid_frame_meta(data: dict) -> bool:
    if "canvas" not in data or "captures" not in data:
        return False

    canvas = data["canvas"]
    captures = data["captures"]

    canvas_required_fields = {
        "size": list,
        "time_loca": list,
        "time_font_size": int,
        "time_font_color": list,
        "qr_loca": list,
        "qr_size": list,
    }

    for key, expected_type in canvas_required_fields.items():
        if key not in canvas or not isinstance(canvas[key], expected_type):
            return False

    if not (len(canvas["size"]) == 2 and len(canvas["time_loca"]) == 2 and
            len(canvas["time_font_color"]) == 4 and len(canvas["qr_loca"]) == 2 and
            len(canvas["qr_size"]) == 2):
        return False

    for capture in captures:
        if not isinstance(capture, dict):
            return False
        if "size" not in capture or "loca" not in capture:
            return False
        if (not isinstance(capture["size"], list) or len(capture["size"]) != 2 or
                not isinstance(capture["loca"], list) or len(capture["loca"]) != 2):
            return False

    return True

# init
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(get_env('LOGFILE_PATH')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)