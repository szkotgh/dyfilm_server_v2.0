import os
from flask import Blueprint, flash, redirect, send_file, session, render_template
import db.capframe
import src.utils as utils
import db

bp = Blueprint('view_capframe', __name__, url_prefix='/capframe')

@bp.route('/<cf_id>', methods=['GET'])
def send_capframe(cf_id):
    cf_result = db.capframe.capframe_get(cf_id)
    if not cf_result:
        return utils.get_code('file_not_found')
    
    is_admin = session.get('ADMIN', False)
    if not cf_result[3] and not is_admin:
        return render_template('errors/private_post.html'), 403
    
    file_path = os.path.join(db.CAPFRAMES_PATH, cf_result[4])
    
    if not utils.is_safe_path(db.CAPFRAMES_PATH, cf_result[4]) or not os.path.exists(file_path) or not os.path.isfile(file_path):
        return utils.get_code('file_not_found')
    
    try:
        filename = f"{cf_result[6]}.{utils.get_extension(cf_result[4])}"
        return send_file(file_path, as_attachment=False, download_name=filename) # as_attachment=utils.is_mobile_user()
    except:
        return utils.get_code('file_not_found')