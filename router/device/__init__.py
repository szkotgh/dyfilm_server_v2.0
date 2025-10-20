from flask import Blueprint, g, request
import src.utils as utils
import auth
from . import frame, capture, capframe, main_image

bp = Blueprint('device', __name__, url_prefix='/device')
bp.register_blueprint(frame.bp)
bp.register_blueprint(capture.bp)
bp.register_blueprint(capframe.bp)
bp.register_blueprint(main_image.bp)

@bp.route('/verify_token', methods=['GET'])
@auth.device_auth
def verify_token():
    device_info_list = list(g.device_info) if g.device_info else None
    return utils.get_code('authorized_success', device_info_list)