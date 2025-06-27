import os
from flask import Blueprint, flash, redirect, render_template, request, url_for
import src.utils as utils
import auth
import db.capture

bp = Blueprint('capture', __name__, url_prefix='/capture')

@bp.before_request
@auth.admin_required
def check_admin():
    pass

@bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('admin/config/capture.html', user_ip=utils.get_ip(), captures=db.capture.capture_get_list())

@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        image_file = request.files.get('image_file')
        desc = request.form.get('desc')

        # check input file
        if not image_file or not desc:
            flash('Missing parameter', 'error')
            return redirect(url_for('router.admin.config.capture.create'))

        if utils.get_extension(image_file.filename) not in ['png', 'jpg', 'jpeg']:
            flash('Invalid file type. only png, jpg, jpeg are supported', 'error')
            return redirect(url_for('router.admin.config.capture.create'))

        # save
        c_id = utils.gen_hash()
        
        file_name = f"{utils.gen_hash()}.{utils.get_extension(image_file.filename)}"
        file_path = os.path.join(db.CAPTURES_PATH, file_name)
        
        db_result = db.capture.capture_create(c_id, None, file_name)
        # create capture
        if not db_result:
            flash('Failed to create capture', 'error')
            return redirect(url_for('router.admin.config.capture.create'))
        
        try:
            image_file.save(file_path)
        except:
            return utils.get_code('unknown_error', info='Failed to save capture image')
        
        # update capture desc
        db_result = db.capture.capture_config_desc(c_id, desc)
        if not db_result:
            flash('Failed to update capture description', 'error')
            return redirect(url_for('router.admin.config.capture.create'))
        
        flash('Capture created successfully', 'success')
        return redirect(url_for('router.admin.config.capture.index'))

    return render_template('admin/config/capture_create.html', user_ip=utils.get_ip())

@bp.route('/remove', methods=['POST'])
def remove():
    c_id = request.form.get('c_id')

    if not c_id:
        flash('Missing parameter', 'error')
        return redirect(url_for('router.admin.config.capture.index'))

    capture_result = db.capture.capture_get(c_id)
    if not capture_result:
        flash('Capture not found', 'error')
        return redirect(url_for('router.admin.config.capture.index'))

    # delete capture
    db_result = db.capture.capture_remove(c_id)
    if not db_result:
        flash('Failed to remove frame from database', 'error')
        return redirect(url_for('router.admin.config.capture.index'))

    # delete capture image
    file_name = capture_result[3]
    file_path = os.path.join(db.CAPTURES_PATH, file_name)
    try:
        os.remove(file_path)
        flash('Capture removed successfully', 'success')
    except Exception as e:
        flash(f'Failed to remove capture image: {e}', 'error')
        return redirect(url_for('router.admin.config.capture.index'))
    
    return redirect(url_for('router.admin.config.capture.index'))

@bp.route('config_status', methods=['POST'])
def config_status():
    c_id = request.form.get('c_id')
    
    if not c_id:
        flash('Missing parameter', 'error')
        return redirect(url_for('router.admin.config.capture.index'))
    
    db_result = db.capture.capture_get(c_id)
    if not db_result:
        flash('Capture not found', 'error')
        return redirect(url_for('router.admin.config.capture.index'))
    
    status = False if db_result[2] == True else True
    db_result = db.capture.capture_config_status(c_id, status)
    
    if not db_result:
        flash('Failed to update capture status', 'error')
        return redirect(url_for('router.admin.config.capture.index'))
    
    flash('Capture status updated successfully', 'success')
    return redirect(url_for('router.admin.config.capture.index'))

@bp.route('/config_desc', methods=['POST'])
def config_desc():
    c_id = request.form.get('c_id')
    config_desc = request.form.get('config_desc')

    if not c_id or not config_desc or not config_desc.strip():
        flash('Missing parameter', 'error')
        return redirect(url_for('router.admin.config.capture.index'))

    db_result = db.capture.capture_get(c_id)
    if not db_result:
        flash('Capture not found', 'error')
        return redirect(url_for('router.admin.config.capture.index'))

    db_result = db.capture.capture_config_desc(c_id, config_desc)
    if not db_result:
        flash('Failed to update capture description', 'error')
        return redirect(url_for('router.admin.config.capture.index'))

    flash('Capture description updated successfully', 'success')
    return redirect(url_for('router.admin.config.capture.index'))