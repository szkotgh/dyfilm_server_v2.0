import os
from flask import Blueprint, send_file, session
import src.utils as utils
import db
import db.capture

bp = Blueprint('view_capture', __name__, url_prefix='/capture')

@bp.route('/<c_id>', methods=['GET'])
def send_capture(c_id):
    c_result = db.capture.capture_get(c_id)
    if not c_result:
        return utils.get_code('not_found')
    
    is_admin = session.get('ADMIN', False)
    if not c_result[2] and not is_admin:
        return utils.get_code('private_post')
    
    try:
        filename = f"{c_result[5]}.{utils.get_extension(c_result[3])}"
        return send_file(os.path.join(db.CAPTURES_PATH, c_result[3]), as_attachment=utils.is_mobile_user(), download_name=filename)
    except:
        return utils.get_code('file_not_found')