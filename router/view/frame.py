import os
from flask import Blueprint, send_file, session
import db.frame
import src.utils as utils
import db

bp = Blueprint('view_frame', __name__, url_prefix='/frame')

@bp.route('/<f_id>', methods=['GET'])
def send_frame(f_id):
    f_info = db.frame.frame_get(f_id)
    if not f_info:
        return utils.get_code('file_not_found')
    
    is_admin = session.get('ADMIN', False)
    if not f_info['status'] and not is_admin:
        return utils.get_code('private_post')
    
    file_path = os.path.join(db.FRAMES_PATH, f_info['file_name'])
    
    if not utils.is_safe_path(db.FRAMES_PATH, f_info['file_name']) or not os.path.exists(file_path) or not os.path.isfile(file_path):
        return utils.get_code('file_not_found')
    
    try:
        return send_file(file_path)
    except:
        return utils.get_code('file_not_found')