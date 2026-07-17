import os
import magic
from flask import Blueprint, g, request, send_file
from PIL import Image
import src.utils as utils
import auth
import db.capture

bp = Blueprint('capture', __name__, url_prefix='/capture')

MAX_UPLOAD_PIXELS = 50_000_000  # 업로드 이미지 해상도 상한(압축 폭탄 차단)

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

        # 해상도 검증(압축 폭탄 차단): 헤더만 읽어 치수 확인 후 스트림 위치 복원
        try:
            with Image.open(file) as img:
                too_large = (img.width * img.height) > MAX_UPLOAD_PIXELS
        except Exception:
            file.seek(0)
            return False
        file.seek(0)
        if too_large:
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

    # 비활성화(status=0)된 캡처는 디바이스에도 제공하지 않는다.
    if not db_result['status']:
        return utils.get_code('file_not_found')

    file_name = db_result['file_name']
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
    d_id = g.device_info['d_id']
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