from flask import Blueprint, g, request
import src.utils as utils
import auth
import db.device

bp = Blueprint('device', __name__, url_prefix='/device')

@bp.route('/verify_token', methods=['GET'])
@auth.device_auth
def verify_token():
    result = utils.get_code('authorized_success')
    result[0]['info'] = g.device_info
    return result