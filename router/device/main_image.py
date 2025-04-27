import os
from flask import Blueprint, send_file
import auth
import db
import src.utils as utils

bp = Blueprint('capframe', __name__, url_prefix='/main_image')

@bp.route('/get_image', methods=['GET'])
@auth.device_auth_with_status
def get_image():
    main_image_files = os.listdir(db.MAIN_IMAGE_DIR_PATH)
    if not main_image_files:
        return utils.get_code('file_not_found')
    
    main_image_path = os.path.join(db.MAIN_IMAGE_DIR_PATH, main_image_files[0])
    
    if not os.path.exists(main_image_path):
        return utils.get_code('file_not_found')
    
    return send_file(main_image_path, mimetype='image/jpeg', max_age=0)