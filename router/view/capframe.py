import os
from flask import Blueprint, flash, redirect, send_file, session
import db.capframe
import src.utils as utils
import db

bp = Blueprint('view_capframe', __name__, url_prefix='/capframe')

@bp.route('/<cf_id>', methods=['GET'])
def send_capframe(cf_id):
    cf_result = db.capframe.capframe_get(cf_id)
    if not cf_result:
        return utils.get_code('not_found')
    
    is_admin = session.get('ADMIN', False)
    if not cf_result[3] and not is_admin:
        flash("비공개처리된 사진입니다. 관리자에게 문의하세요.", 'error')
        return redirect('/')
    
    try:
        filename = f"{cf_result[6]}.{utils.get_extension(cf_result[4])}"
        return send_file(os.path.join(db.CAPFRAMES_PATH, cf_result[4]), as_attachment=False, download_name=filename) # as_attachment=utils.is_mobile_user()
    except:
        return utils.get_code('file_not_found')