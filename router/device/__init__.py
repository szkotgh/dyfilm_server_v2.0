from flask import Blueprint

bp = Blueprint('device', __name__, url_prefix='/device')

@bp.route('/test')
def test():
    return "Device Test"