from flask import Blueprint, flash, redirect, render_template, request, session, url_for
import src.utils as utils
import auth
import db.device

bp = Blueprint('device', __name__, url_prefix='/device')

@bp.before_request
@auth.admin_required
def check_admin():
    pass

@bp.route('/')
def index():
    return render_template('admin/config/device.html', user_ip=utils.get_ip(), devices=db.device.device_get_list())

@bp.route('/create', methods=['POST'])
def create():
    result = db.device.device_create()
    
    if result:
        flash('Device created successfully', 'success')
    else:
        flash('Failed to create device', 'error')
    return redirect(url_for('router.admin.config.device.index'))

@bp.route('/remove', methods=['POST'])
def remove():
    d_id = request.form.get('d_id')
    
    if not d_id:
        flash('Missing parameter', 'error')
        return redirect(url_for('router.admin.config.device.index'))
    
    # remove device
    result = db.device.device_remove(d_id)
    
    if result:
        flash('Device removed successfully', 'success')
    else:
        flash('Failed to remove device', 'error')
    return redirect(url_for('router.admin.config.device.index'))

@bp.route('/config_status', methods=['POST'])
def config_status():
    d_id = request.form.get('d_id')
    
    if not d_id:
        flash('Missing parameter', 'error')
        return redirect(url_for('router.admin.config.device.index'))
    
    # change status
    equal_device = db.device.device_get(d_id)
    if not equal_device:
        flash('Device not found', 'error')
        return redirect(url_for('router.admin.config.device.index'))
    
    status = False if equal_device[1] == True else True
    result = db.device.device_config_status(d_id, status)
    
    if result:
        flash('Status updated successfully', 'success')
    else:
        flash('Failed to update status', 'error')
    return redirect(url_for('router.admin.config.device.index'))

@bp.route('/config_desc', methods=['POST'])
def config_desc():
    d_id = request.form.get('d_id')
    config_desc = request.form.get('config_desc')
    
    if not d_id or not config_desc:
        flash('Missing parameter', 'error')
        return redirect(url_for('router.admin.config.device.index'))
    
    # change description
    result = db.device.device_config_desc(d_id, config_desc)
    
    if result:
        flash('Description updated successfully', 'success')
    else:
        flash('Failed to update description', 'error')
    return redirect(url_for('router.admin.config.device.index'))

@bp.route('/refresh_token', methods=['POST'])
def refresh_token():
    d_id = request.form.get('d_id')
    
    if not d_id:
        flash('Missing parameter', 'error')
        return redirect(url_for('router.admin.config.device.index'))
    
    # refresh token
    result = db.device.device_config_auth_token(d_id)
    
    if result:
        flash('Token refreshed successfully', 'success')
    else:
        flash('Failed to refresh token', 'error')
    return redirect(url_for('router.admin.config.device.index'))