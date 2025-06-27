import os
from flask import Blueprint, request, send_file
import src.utils as utils
import auth
import db.frame

bp = Blueprint('frame', __name__, url_prefix='/frame')

@bp.route('/frame_list', methods=['GET'])
@auth.device_auth_with_status
def frame_list():
    return utils.get_code('success', db.frame.frame_get_list())

@bp.route('/frame_get', methods=['GET'])
@auth.device_auth_with_status
def frame_get():
    f_id = request.args.get('f_id')
    
    if not f_id:
        return utils.get_code('missing_parameter')
    
    f_info = db.frame.frame_get(f_id)
    if not f_info:
        return utils.get_code('invalid_parameter')
    
    file_path = os.path.join(db.FRAMES_PATH, f_info[2])
    
    if not utils.is_safe_path(db.FRAMES_PATH, f_info[2]) or not os.path.exists(file_path) or not os.path.isfile(file_path):
        return utils.get_code('file_not_found')
    
    try:
        return send_file(file_path)
    except:
        return utils.get_code('file_not_found')