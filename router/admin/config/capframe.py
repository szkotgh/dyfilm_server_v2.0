import json
import os
import time
from flask import Blueprint, flash, redirect, render_template, request, session, url_for, jsonify
import src.utils as utils
import auth
import db.capframe
import db.capframe_info
import db.frame
import db.capture
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

bp = Blueprint('capframe', __name__, url_prefix='/capframe')

@bp.before_request
@auth.admin_required
def check_admin():
    pass

@bp.route('/', methods=['GET'])
def index():
    return render_template('admin/config/capframe.html', user_ip=utils.get_ip())

@bp.route('/list', methods=['GET'])
def get_list():
    try:
        limit = int(request.args.get('limit', '30'))
        offset = int(request.args.get('offset', '0'))
    except ValueError:
        limit = 30
        offset = 0
    rows = db.capframe.capframe_get_list_paginated(limit=limit, offset=offset)
    items = []
    for r in rows:
        items.append({
            'cf_id': r[0],
            'd_id': r[1],
            'f_id': r[2],
            'status': bool(r[3]),
            'file_name': r[4],
            'desc': r[5],
            'create': r[6],
            'processing_time': r[7],
            'image_url': url_for('router.view.view_capframe.send_capframe', cf_id=r[0])
        })
    return jsonify({ 'items': items })

@bp.route('/count', methods=['GET'])
def get_count():
    return jsonify({ 'total': db.capframe.capframe_count() })

@bp.route('/create', methods=['GET'])
def create():
    return render_template('admin/config/capframe_create_first_select.html', user_ip=utils.get_ip(), frames=db.frame.frame_get_list())

@bp.route('/remove', methods=['POST'])
def remove():
    cf_id = request.form.get('cf_id')
    
    if not cf_id:
        flash('CapFrame ID is required', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    capframe_result = db.capframe.capframe_get(cf_id)
    if not capframe_result:
        flash('CapFrame not found', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    # remove capframe
    db_result = db.capframe.capframe_remove(cf_id)
    if not db_result:
        flash('Failed to remove CapFrame', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    file_name = capframe_result[4]
    file_path = os.path.join(db.CAPFRAMES_PATH, file_name)
    try:
        os.remove(file_path)
    except Exception as e:
        flash(f'Failed to remove capture image: {e}', 'error')
        return redirect(url_for('router.admin.config.capture.index'))
    
    flash('CapFrame removed successfully', 'success')
    return redirect(url_for('router.admin.config.capframe.index'))

@bp.route('/config_status', methods=['POST'])
def config_status():
    cf_id = request.form.get('cf_id')
    
    if not cf_id:
        flash('CapFrame ID and Status are required', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    db_result = db.capframe.capframe_get(cf_id)
    if not db_result:
        flash('CapFrame not found', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    status = False if db_result[3] == True else True
    db_result = db.capframe.capframe_config_status(cf_id, status)
    if not db_result:
        flash('Failed to update CapFrame status', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    flash('CapFrame status updated successfully', 'success')
    return redirect(url_for('router.admin.config.capframe.index'))

@bp.route('/config_desc', methods=['POST'])
def config_desc():
    cf_id = request.form.get('cf_id')
    config_desc = request.form.get('config_desc')
    
    if not cf_id or not config_desc:
        flash('Requirement parameter missing', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    db_result = db.capframe.capframe_get(cf_id)
    if not db_result:
        flash('CapFrame not found', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    db_result = db.capframe.capframe_config_desc(cf_id, config_desc)
    if not db_result:
        flash('Failed to update CapFrame description', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    flash('CapFrame description updated successfully', 'success')
    return redirect(url_for('router.admin.config.capframe.index'))

@bp.route('/create/<int:f_id>', methods=['GET', 'POST'])
def create_frame_selected(f_id):
    if not f_id:
        flash('Frame ID is required', 'error')
        return redirect(url_for('router.admin.config.capframe.create'))
    
    frame_info = db.frame.frame_get(f_id)
    if not frame_info:
        flash('Frame not found. Select again', 'error')
        return redirect(url_for('router.admin.config.capframe.create'))
    
    frame_meta = json.loads(frame_info[3])
    frame_capture_count = len(frame_meta['captures'])
    
    if request.method == "POST":
        ready_capture_c_id_list = []
        for i in range(frame_capture_count):
            value = request.form.get(f'c_id-{i}')
            
            capture_info = db.capture.capture_get(value)
            if not value or not value.strip() or not capture_info:
                flash('Capture ID Error. Select again', 'error')
                return redirect(url_for('router.admin.config.capframe.create_frame_selected', f_id=f_id))
            
            ready_capture_c_id_list.append(capture_info[0])

        create_result = db.capframe.capframe_create(None, f_id, ready_capture_c_id_list)
        if not create_result:
            flash('Failed to create CapFrame', 'error')
            return redirect(url_for('router.admin.config.capframe.create_frame_selected', f_id=f_id))
        
        flash('CapFrame created successfully', 'success')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    return render_template('admin/config/capframe_create.html', user_ip=utils.get_ip(), captures=db.capture.capture_get_list(), frame=frame_info, capture_len=frame_capture_count, capframes=db.capframe.capframe_get_list())

