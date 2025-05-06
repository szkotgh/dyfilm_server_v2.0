import os
from flask import Blueprint, g, request, send_file
import src.utils as utils
import auth
import db.capture

bp = Blueprint('capture', __name__, url_prefix='/capture')

@bp.route('/capture_get', methods=['GET'])
@auth.device_auth_with_status
def capture_get():
    c_id = request.args.get('c_id')
    
    if not c_id:
        return utils.get_code('missing_parameter')
    
    # get capture
    db_result = db.capture.capture_get(c_id)
    
    if not db_result:
        return utils.get_code('invalid_parameter')
    
    file_name = db_result[3]
    file_path = os.path.join(db.CAPTURES_PATH, file_name)
    
    if not os.path.exists(file_path):
        return utils.get_code('file_not_found')
    
    return send_file(file_path, mimetype='image/jpeg')

@bp.route('/regi_capture', methods=['POST'])
@auth.device_auth_with_status
def regi_capture():
    d_id = g.device_info[0]
    image = request.files.get('image')
    
    if not image:
        return utils.get_code('missing_parameter')
    if utils.get_extension(image.filename) not in ['png', 'jpg', 'jpeg']:
        return utils.get_code('invalid_file_type')
    
    # save
    c_id = utils.gen_hash()
    file_name = f"{utils.gen_hash()}.{utils.get_extension(image.filename)}"
    file_path = os.path.join(db.CAPTURES_PATH, file_name)
    
    db_result = db.capture.capture_create(c_id, d_id, file_name)
    
    # create capture
    if not db_result:
        return utils.get_code('unknown_error', info='Failed to create capture')
    
    try:
        image.save(file_path)
    except:
        return utils.get_code('unknown_error', info='Failed to save capture image')
    
    return utils.get_code('success', c_id)