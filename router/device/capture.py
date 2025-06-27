import os
import magic
from flask import Blueprint, g, request, send_file
import src.utils as utils
import auth
import db.capture

bp = Blueprint('capture', __name__, url_prefix='/capture')

def validate_image_file(file):
    if not file or not file.filename:
        return False
    
    allowed_extensions = ['png', 'jpg', 'jpeg']
    allowed_mime_types = ['image/png', 'image/jpeg', 'image/jpg']
    
    extension = utils.get_extension(file.filename)
    if extension not in allowed_extensions:
        return False
    
    try:
        file.seek(0)
        mime_type = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)
        
        if mime_type not in allowed_mime_types:
            return False
            
        return True
    except:
        return False

@bp.route('/capture_get', methods=['GET'])
@auth.device_auth_with_status
def capture_get():
    c_id = request.args.get('c_id')
    
    if not c_id or not utils.validate_id_format(c_id):
        return utils.get_code('missing_parameter')
    
    db_result = db.capture.capture_get(c_id)
    
    if not db_result:
        return utils.get_code('invalid_parameter')
    
    file_name = db_result[3]
    file_path = os.path.join(db.CAPTURES_PATH, file_name)
    
    if not utils.is_safe_path(db.CAPTURES_PATH, file_name) or not os.path.exists(file_path) or not os.path.isfile(file_path):
        return utils.get_code('file_not_found')
    
    try:
        return send_file(file_path, mimetype='image/jpeg')
    except:
        return utils.get_code('file_not_found')

@bp.route('/regi_capture', methods=['POST'])
@auth.device_auth_with_status
def regi_capture():
    d_id = g.device_info[0]
    image = request.files.get('image')
    
    if not image:
        return utils.get_code('missing_parameter')
    
    if not validate_image_file(image):
        return utils.get_code('invalid_file_type')
    
    c_id = utils.gen_hash()
    file_name = f"{utils.gen_hash()}.{utils.get_extension(image.filename)}"
    file_path = os.path.join(db.CAPTURES_PATH, file_name)
    
    db_result = db.capture.capture_create(c_id, d_id, file_name)
    
    if not db_result:
        return utils.get_code('unknown_error', info='Failed to create capture')
    
    try:
        image.save(file_path)
    except:
        return utils.get_code('unknown_error', info='Failed to save capture image')
    
    return utils.get_code('success', c_id)