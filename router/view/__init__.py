from flask import Blueprint, request
from . import frame, capture, capframe

bp = Blueprint('view', __name__, url_prefix='/view')

bp.register_blueprint(frame.bp)
bp.register_blueprint(capture.bp)
bp.register_blueprint(capframe.bp)