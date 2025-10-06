import os
from flask import Blueprint, flash, redirect, render_template, request, send_file, session, url_for, jsonify
import src.utils as utils
import auth
import db.device

bp = Blueprint('device', __name__, url_prefix='/device')

@bp.before_request
@auth.admin_required
def check_admin():
    pass

@bp.route('')
def index():
    return render_template('admin/config/device.html', user_ip=utils.get_ip())

@bp.route('/list', methods=['GET'])
def get_list():
    try:
        limit = int(request.args.get('limit', '30'))
        offset = int(request.args.get('offset', '0'))
    except ValueError:
        limit = 30
        offset = 0
    rows = db.device.device_get_list_paginated(limit=limit, offset=offset)
    items = []
    for r in rows:
        items.append({
            'd_id': r['d_id'],
            'status': bool(r['status']),
            'desc': r['desc'],
            'auth_token': r['auth_token'],
            'create': r['create'],
            'last_use': r['last_use'],
        })
    return jsonify({ 'items': items })

@bp.route('/count', methods=['GET'])
def get_count():
    return jsonify({ 'total': db.device.device_count() })

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
    
    status = False if equal_device['status'] == True else True
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

# main-image
@bp.route('/get_main_image', methods=['GET'])
def get_main_image():
    main_image_files = os.listdir(db.MAIN_IMAGE_DIR_PATH)
    if not main_image_files:
        flash('Image not found', 'error')
        return redirect(url_for('router.admin.config.device.index'))
    
    main_image_path = os.path.join(db.MAIN_IMAGE_DIR_PATH, main_image_files[0])
    
    if not os.path.exists(main_image_path):
        flash('Image not found', 'error')
        return redirect(url_for('router.admin.config.device.index'))
    
    return send_file(main_image_path, mimetype='image/jpeg', max_age=0)

@bp.route('/main_image', methods=['POST'])
def config_main_image():
    main_image = request.files.get('config_image')
    
    if not main_image:
        flash('Missing parameter', 'error')
        return redirect(url_for('router.admin.config.device.index'))
    if not utils.get_extension(main_image.filename) in ['gif']:
        flash('Invalid image format. Supported only .gif file', 'error')
        return redirect(url_for('router.admin.config.device.index'))
    
    try:
        # remove all old image
        for filename in os.listdir(db.MAIN_IMAGE_DIR_PATH):
            file_path = os.path.join(db.MAIN_IMAGE_DIR_PATH, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        # save
        main_image.save(os.path.join(db.MAIN_IMAGE_DIR_PATH, 'main_image.' + utils.get_extension(main_image.filename)))
        
        flash('Image updated successfully', 'success')
        return redirect(url_for('router.admin.config.device.index'))
    except Exception as e:
        flash('Failed to save image: ' + str(e), 'error')
        return redirect(url_for('router.admin.config.device.index'))
    