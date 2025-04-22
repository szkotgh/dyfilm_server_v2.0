from flask import Blueprint, g, request
import src.utils as utils
import auth
from . import frame

bp = Blueprint('device', __name__, url_prefix='/device')
bp.register_blueprint(frame.bp)

@bp.route('/verify_token', methods=['GET'])
@auth.device_auth
def verify_token():
    return utils.get_code('authorized_success', g.device_info)