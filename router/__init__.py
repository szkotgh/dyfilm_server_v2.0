from flask import Blueprint
import router.device as device
import router.admin as admin

bp = Blueprint('router', __name__)

bp.register_blueprint(device.bp)
bp.register_blueprint(admin.bp)