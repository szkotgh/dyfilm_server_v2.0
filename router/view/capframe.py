import os
from flask import Blueprint, flash, redirect, send_file, session, render_template, url_for
import db.capframe
import src.utils as utils
import db
from .capframe_report import bp as capframe_report_bp

bp = Blueprint('view_capframe', __name__, url_prefix='/capframe')
bp.register_blueprint(capframe_report_bp)

@bp.route('/<cf_id>', methods=['GET'])
def view_capframe(cf_id):
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
        
        template_data = {
            'cf_id': cf_id,
            'filename': filename,
            'capture_time': cf_result[6],
            'image_url': url_for('router.view.view_capframe.serve_capframe', cf_id=cf_id),
            'download_url': url_for('router.view.view_capframe.download_capframe', cf_id=cf_id)
        }
    
        return render_template('view/capframe_view.html', **template_data)
    except:
        return utils.get_code('file_not_found')

@bp.route('/<cf_id>/image', methods=['GET'])
def serve_capframe(cf_id):
    cf_result = db.capframe.capframe_get(cf_id)
    if not cf_result:
        return utils.get_code('file_not_found')
    
    is_admin = session.get('ADMIN', False)
    if not cf_result[3] and not is_admin:
        return utils.get_code('file_not_found'), 403
    
    file_path = os.path.join(db.CAPFRAMES_PATH, cf_result[4])
    
    if not utils.is_safe_path(db.CAPFRAMES_PATH, cf_result[4]) or not os.path.exists(file_path) or not os.path.isfile(file_path):
        return utils.get_code('file_not_found')
    
    try:
        response = send_file(file_path, mimetype='image/*', as_attachment=False)
        response.headers['Content-Disposition'] = 'inline'
        return response
    except:
        return utils.get_code('file_not_found')

@bp.route('/<cf_id>/download', methods=['GET'])
def download_capframe(cf_id):
    cf_result = db.capframe.capframe_get(cf_id)
    if not cf_result:
        return utils.get_code('file_not_found')
    
    is_admin = session.get('ADMIN', False)
    if not cf_result[3] and not is_admin:
        return utils.get_code('file_not_found'), 403
    
    file_path = os.path.join(db.CAPFRAMES_PATH, cf_result[4])
    
    if not utils.is_safe_path(db.CAPFRAMES_PATH, cf_result[4]) or not os.path.exists(file_path) or not os.path.isfile(file_path):
        return utils.get_code('file_not_found')
    
    try:
        filename = f"{cf_result[6]}.{utils.get_extension(cf_result[4])}"
        response = send_file(file_path, as_attachment=True, download_name=filename)
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except:
        return utils.get_code('file_not_found')