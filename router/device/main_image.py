import os
from flask import Blueprint, send_file, g
import auth
import db
import db.main_image
import src.utils as utils

bp = Blueprint('main_image', __name__, url_prefix='/main_image')

@bp.route('/get_image', methods=['GET'])
@auth.device_auth_with_status
def get_image():
    device_id = g.device_info['d_id']
    
    # 우선순위에 따라 main_image 찾기
    main_image = db.main_image.main_image_get_for_device(device_id)
    
    if main_image:
        main_image_path = os.path.join(db.MAIN_IMAGE_DIR_PATH, main_image['file_name'])
        
        if os.path.exists(main_image_path):
            # MIME 타입 결정
            extension = utils.get_extension(main_image['file_name'])
            mime_types = {
                'gif': 'image/gif',
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg'
            }
            mimetype = mime_types.get(extension, 'image/jpeg')
            
            return send_file(main_image_path, mimetype=mimetype, max_age=0)
    
    # main_image가 없으면 기본 이미지 반환
    default_image_path = os.path.join('static', 'images', 'not_set_main_image.png')
    
    if os.path.exists(default_image_path):
        return send_file(default_image_path, mimetype='image/png', max_age=0)
    
    return utils.get_code('file_not_found')