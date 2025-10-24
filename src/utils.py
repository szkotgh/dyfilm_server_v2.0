from dotenv import load_dotenv
import datetime
import json
import os
import re
from flask import request, session
import hashlib
import qrcode
import logging
from user_agents import parse

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
    user_ip = request.headers.get("Cf-Connecting-Ip", request.remote_addr)
    return user_ip

def gen_hash(key: str = None, len=16):
    if key is None:
        return os.urandom(16).hex()[:len]
    return hashlib.md5(key.encode()).hexdigest()[:len]

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

def is_safe_path(base_path: str, file_path: str) -> bool:
    try:
        base_path = os.path.abspath(base_path)
        full_path = os.path.abspath(os.path.join(base_path, file_path))
        return full_path.startswith(base_path)
    except:
        return False

def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    if not input_str:
        return ""
    
    input_str = str(input_str).strip()
    if len(input_str) > max_length:
        input_str = input_str[:max_length]
    
    return input_str

def validate_id_format(id_str: str) -> bool:
    if not id_str:
        return False
    
    id_pattern = re.compile(r'^[a-f0-9]{16,32}$')
    return bool(id_pattern.match(str(id_str)))

def is_mobile_user():
    user_agent_str = str(request.user_agent)
    user_agent = parse(user_agent_str)

    return user_agent.is_mobile or user_agent.is_tablet

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

def gen_qr(save_path, url_path: str):
    data = f'{get_env("SERVER_DOMAIN")}{url_path}'
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_img.save(save_path)

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