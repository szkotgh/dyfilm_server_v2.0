from flask import Blueprint
import src.utils as utils
import auth
import db.frame

bp = Blueprint('frame', __name__, url_prefix='/frame')


@bp.route('/frame_list', methods=['GET'])
@auth.device_auth
def frame_list():
    return utils.get_code('success', db.frame.frame_get_list())
