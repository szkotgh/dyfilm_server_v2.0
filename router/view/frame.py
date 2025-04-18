import os
from flask import Blueprint, send_file, session
import src.utils as utils
import db
import db.frame

bp = Blueprint('view_frame', __name__, url_prefix='/frame')

@bp.route('/<f_id>', methods=['GET'])
def send_frame(f_id):
    f_info = db.frame.frame_get(f_id)
    if not f_info:
        return utils.get_code('not_found')
    
    is_admin = session.get('ADMIN', False)
    if f_info[1] == False and is_admin  == False:
        return utils.get_code('private_post')
    
    try:
        return send_file(os.path.join(db.FRAMES_PATH, f_info[2]))
    except:
        return utils.get_code('file_not_found')