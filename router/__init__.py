from flask import Blueprint
from router import device, admin, view, report

bp = Blueprint('router', __name__)

bp.register_blueprint(device.bp)
bp.register_blueprint(admin.bp)
bp.register_blueprint(view.bp)
bp.register_blueprint(report.bp)