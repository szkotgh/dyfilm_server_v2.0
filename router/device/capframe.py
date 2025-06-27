import json
import os
from flask import Blueprint, g, request, send_file
import src.utils as utils
import auth
import db.capframe
import db.capture
import db.frame

bp = Blueprint('capframe', __name__, url_prefix='/capframe')

@bp.route('/capframe_get', methods=['GET'])
@auth.device_auth_with_status
def capframe_get():
    d_id = g.device_info[0]
    
    cf_id = request.args.get('cf_id')
    if not cf_id or not utils.validate_id_format(cf_id):
        return utils.get_code('missing_parameter')
    
    capframe_info = db.capframe.capframe_get(cf_id)
    if not capframe_info:
        return utils.get_code('invalid_parameter')
    
    file_path = os.path.join(db.CAPFRAMES_PATH, capframe_info[4])
    
    if not utils.is_safe_path(db.CAPFRAMES_PATH, capframe_info[4]) or not os.path.exists(file_path) or not os.path.isfile(file_path):
        return utils.get_code('file_not_found')
    
    try:
        return send_file(file_path)
    except:
        return utils.get_code('unknown_error', info='Failed to send capframe image')

@bp.route('/capframe_create', methods=['POST'])
@auth.device_auth_with_status
def capframe_create():
    d_id = g.device_info[0]
    
    f_id = request.form.get('f_id')
    if not f_id or not f_id.isdigit():
        return utils.get_code('missing_parameter')
    
    frame_info = db.frame.frame_get(int(f_id))
    if not frame_info:
        return utils.get_code('invalid_parameter')
    
    try:
        frame_meta = json.loads(frame_info[3])
    except (json.JSONDecodeError, TypeError):
        return utils.get_code('invalid_parameter')
    
    frame_capture_count = len(frame_meta.get('captures', []))
    if frame_capture_count == 0:
        return utils.get_code('invalid_parameter')
    
    ready_captures = []
    
    for i in range(frame_capture_count):
        c_id = request.form.get(f'c_id_{i+1}')
        if not c_id or not utils.validate_id_format(c_id):
            return utils.get_code('missing_parameter')
        
        capture_info = db.capture.capture_get(c_id)
        if not capture_info:
            return utils.get_code('invalid_parameter')
        
        ready_captures.append(capture_info)
        
    c_id_list = []
    for ready_capture in ready_captures:
        c_id_list.append(ready_capture[0])
    
    result = db.capframe.capframe_create(d_id, frame_info[0], c_id_list)
    if not result:
        return utils.get_code('unknown_error', info=g.capframe_fall_info)
    else:
        return utils.get_code('success', result)
    
