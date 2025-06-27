import os
from flask import Blueprint, flash, json, redirect, render_template, request, session, url_for
import src.utils as utils
import auth
import db.frame

bp = Blueprint('frame', __name__, url_prefix='/frame')

@bp.before_request
@auth.admin_required
def check_admin():
    pass

@bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('admin/config/frame.html', user_ip=utils.get_ip(), frames=db.frame.frame_get_list())

@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        input_file = request.files.get('frame_file')
        input_meta = request.form.get('meta')
        input_desc = request.form.get('desc')
        
        # check input file
        if not input_file or not input_meta or not input_desc or not input_file.filename:
            flash('Missing parameter', 'error')
            return redirect(url_for('router.admin.config.frame.create'))
        
        if utils.get_extension(input_file.filename) != 'png':
            flash('Invalid file type. only png is supported', 'error')
            return redirect(url_for('router.admin.config.frame.create'))
        
        # check input meta
        try:
            check_meta = json.loads(input_meta)
            if utils.is_valid_frame_meta(check_meta) == False:
                flash('Invalid meta format', 'error')
                return redirect(url_for('router.admin.config.frame.create'))
            input_meta = json.dumps(check_meta, indent=0)
        except:
            flash('Invalid meta json format', 'error')
            return redirect(url_for('router.admin.config.frame.create'))
        
        # save
        file_name = f"{utils.gen_hash()}.{utils.get_extension(input_file.filename)}"
        file_path = os.path.join(db.FRAMES_PATH, file_name)
        
        db_result = db.frame.frame_create(file_name, input_meta, input_desc)
        
        if not db_result:
            flash('Failed to save frame image', 'error')
            return redirect(url_for('router.admin.config.frame.create'))
        
        try:
            input_file.save(file_path)
        except:
            flash('Failed to create frame', 'error')
            return redirect(url_for('router.admin.config.frame.create'))
        
        flash('Frame created successfully', 'success')
        return redirect(url_for('router.admin.config.frame.index'))
    
    return render_template('admin/config/frame_create.html', is_admin=session.get('ADMIN', False), user_ip=utils.get_ip())

@bp.route('/config_status', methods=['POST'])
def config_status():
    f_id = int(request.form.get('f_id'))
    
    # check input
    if not f_id:
        flash('Missing parameter', 'error')
        return redirect(url_for('router.admin.config.frame.index'))
    
    frame_result = db.frame.frame_get(f_id)
    if frame_result == False:
        flash('Frame not found', 'error')
        return redirect(url_for('router.admin.config.frame.index'))
    
    # change status
    status = False if frame_result[1] == True else True
    result = db.frame.frame_config_status(f_id, status)
    
    if result:
        flash('Status updated successfully', 'success')
    else:
        flash('Failed to update status', 'error')
    return redirect(url_for('router.admin.config.frame.index'))

@bp.route('/config_image', methods=['POST'])
def config_image():
    f_id = request.form.get('f_id')
    config_image = request.files.get('config_image')
    
    if not f_id or not config_image or not config_image.filename:
        flash('Missing parameter', 'error')
        return redirect(url_for('router.admin.config.frame.index'))
    
    if utils.get_extension(config_image.filename) != 'png':
        flash('Invalid file type. only png is supported', 'error')
        return redirect(url_for('router.admin.config.frame.index'))
    
    frame_result = db.frame.frame_get(int(f_id))
    if not frame_result:
        flash('Frame not found', 'error')
        return redirect(url_for('router.admin.config.frame.index'))
    
    file_name = frame_result[2]
    file_path = os.path.join(db.FRAMES_PATH, file_name)
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        config_image.save(file_path)
        flash('Image updated successfully', 'success')
    except Exception as e:
        flash('Failed to update image', 'error')
        return redirect(url_for('router.admin.config.frame.index'))
    
    return redirect(url_for('router.admin.config.frame.index'))

@bp.route('/config_meta', methods=['POST'])
def config_meta():
    f_id = request.form.get('f_id')
    input_meta = request.form.get('config_meta')
    
    if not f_id or not input_meta:
        flash('Missing parameter', 'error')
        return redirect(url_for('router.admin.config.frame.index'))
    
    try:
        check_meta = json.loads(input_meta)
        if utils.is_valid_frame_meta(check_meta) == False:
            flash('Invalid meta format', 'error')
            return redirect(url_for('router.admin.config.frame.index'))
        input_meta = json.dumps(check_meta, separators=(',', ':'))
        input_meta = input_meta.replace('\\n', '').replace('\\t', '').replace('\\r', '')

    except:
        flash('Invalid meta json format', 'error')
        return redirect(url_for('router.admin.config.frame.index'))
    
    result = db.frame.frame_config_meta(int(f_id), input_meta)
    
    if result:
        flash('Meta updated successfully', 'success')
    else:
        flash('Failed to update meta', 'error')
    
    return redirect(url_for('router.admin.config.frame.index'))

@bp.route('/config_desc', methods=['POST'])
def config_desc():
    f_id = request.form.get('f_id')
    input_desc = request.form.get('config_desc')
    
    if not f_id or not input_desc:
        flash('Missing parameter', 'error')
        return redirect(url_for('router.admin.config.frame.index'))
    
    result = db.frame.frame_config_desc(int(f_id), input_desc)
    
    if result:
        flash('Description updated successfully', 'success')
    else:
        flash('Failed to update description', 'error')
    
    return redirect(url_for('router.admin.config.frame.index'))

@bp.route('/remove', methods=['POST'])
def remove():
    f_id = request.form.get('f_id')
    
    if not f_id:
        flash('Missing parameter', 'error')
        return redirect(url_for('router.admin.config.frame.index'))
    
    frame_result = db.frame.frame_get(int(f_id))
    if not frame_result:
        flash('Frame not found', 'error')
        return redirect(url_for('router.admin.config.frame.index'))
    
    # delete image database, file
    db_result = db.frame.frame_remove(f_id)
    if not db_result:
        flash('Failed to remove frame from database', 'error')
        return redirect(url_for('router.admin.config.frame.index'))
    
    file_name = frame_result[2]
    file_path = os.path.join(db.FRAMES_PATH, file_name)
    try:
        os.remove(file_path)
        flash('Frame removed successfully', 'success')
    except Exception as e:
        flash(f'Failed to remove frame: {str(e)}', 'error')
        return redirect(url_for('router.admin.config.frame.index'))
    
    return redirect(url_for('router.admin.config.frame.index'))