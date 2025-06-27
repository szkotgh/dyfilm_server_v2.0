from flask import Blueprint, render_template, session
import src.utils as utils
from . import device, frame, capture, capframe

bp = Blueprint('config', __name__, url_prefix='/config')

bp.register_blueprint(device.bp)
bp.register_blueprint(frame.bp)
bp.register_blueprint(capture.bp)
bp.register_blueprint(capframe.bp)
