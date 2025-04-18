import os
from flask import Blueprint, send_file, session
import db.capframe
import src.utils as utils
import db

bp = Blueprint('view_capframe', __name__, url_prefix='/capframe')

@bp.route('/<cf_id>', methods=['GET'])
def send_capframe(cf_id):
    cf_info = db.capframe.capframe_get(cf_id)
    if not cf_info:
        return utils.get_code('not_found')
    
    is_admin = session.get('ADMIN', False)
    if not cf_info[3] and not is_admin:
        return utils.get_code('private_post')
    
    try:
        return send_file(os.path.join(db.CAPFRAMES_PATH, cf_info[4]))
    except:
        return utils.get_code('file_not_found')