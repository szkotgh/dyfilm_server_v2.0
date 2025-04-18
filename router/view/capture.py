import os
from flask import Blueprint, send_file, session
import src.utils as utils
import db
import db.capture

bp = Blueprint('view_capture', __name__, url_prefix='/capture')

@bp.route('/<c_id>', methods=['GET'])
def send_capture(c_id):
    c_info = db.capture.capture_get(c_id)
    if not c_info:
        return utils.get_code('not_found')
    
    is_admin = session.get('ADMIN', False)
    if not c_info[2] and not is_admin:
        return utils.get_code('private_post')
    
    try:
        return send_file(os.path.join(db.CAPTURES_PATH, c_info[3]))
    except:
        return utils.get_code('file_not_found')