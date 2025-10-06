import os
from flask import Blueprint, flash, redirect, send_file, session
import src.utils as utils
import db
import db.capture

bp = Blueprint('view_capture', __name__, url_prefix='/capture')

@bp.route('/<c_id>', methods=['GET'])
def send_capture(c_id):
    c_result = db.capture.capture_get(c_id)
    if not c_result:
        return utils.get_code('file_not_found')
    
    is_admin = session.get('ADMIN', False)
    if not c_result['status'] and not is_admin:
        return utils.get_code('private_post')
    
    file_path = os.path.join(db.CAPTURES_PATH, c_result['file_name'])
    
    if not utils.is_safe_path(db.CAPTURES_PATH, c_result['file_name']) or not os.path.exists(file_path) or not os.path.isfile(file_path):
        return utils.get_code('file_not_found')
    
    try:
        filename = f"{c_result['create']}.{utils.get_extension(c_result['file_name'])}"
        return send_file(file_path, as_attachment=False, download_name=filename) # as_attachment=utils.is_mobile_user()
    except:
        return utils.get_code('file_not_found')