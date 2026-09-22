import os
from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
import src.utils as utils
from src.ratelimit import login_limiter
import bcrypt
import auth
import router.admin.config as config
import router.admin.report as report
import db

bp = Blueprint('admin', __name__, url_prefix='/admin')
bp.register_blueprint(config.bp)
bp.register_blueprint(report.bp)

@bp.route('', methods=['GET', 'POST'])
@auth.admin_required
def index():
    stats = db.get_statistics()
    return render_template('admin/index.html', user_ip=utils.get_ip(), stats=stats)

@bp.route('/state/storage', methods=['GET'])
@auth.admin_required
def state_storage():
    hardware_info = utils.get_hardware_info()
    db_size = {
        'db': utils.get_db_size(),
        'capframes': utils.get_db_capframes_size(),
        'captures': utils.get_db_captures_size(),
        'frames': utils.get_db_frames_size(),
        'qr': utils.get_db_qr_size(),
        'main_image': utils.get_db_main_image_size(),
        'total': utils.get_db_size() + utils.get_db_capframes_size() + utils.get_db_captures_size() + utils.get_db_frames_size() + utils.get_db_qr_size() + utils.get_db_main_image_size()
    }
    return jsonify({'hardware_info': hardware_info, 'db_size': db_size}), 200, {'Content-Type': 'application/json'}

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('ADMIN', False) == True:
        flash('You are already logged in', 'info')
        return redirect(url_for('router.admin.index'))
    
    if request.method == 'POST':
        # Cloudflare/nginx가 전달한 클라이언트 IP별로 로그인 실패 횟수를 제한한다.
        client_key = utils.get_ip() or 'unknown'
        if login_limiter.is_limited(client_key):
            utils.logger.warning(f'ADMIN LOGIN RATE-LIMITED from {client_key}')
            resp = render_template('admin/login.html', user_ip=utils.get_ip(), getout=True)
            return resp, 429, {'Retry-After': '300'}

        input_pw = request.form.get('password')

        if not input_pw or not input_pw.strip():
            login_limiter.record(client_key)
            return render_template('admin/login.html', user_ip=utils.get_ip(), getout=True)

        if bcrypt.checkpw(input_pw.encode('utf-8'), os.environ['ADMIN_PASSWORD'].encode('utf-8')):
            login_limiter.reset(client_key)
            session.clear()
            session.permanent = True  # PERMANENT_SESSION_LIFETIME(절대 만료) 적용
            session['ADMIN'] = True
            session['ADMIN_LAST_ACTIVE_TIME'] = utils.get_now_datetime_str()
            session['ADMIN_LOGIN_TIME'] = utils.get_now_datetime_str()
            session['SESSION_FINGERPRINT'] = auth.generate_session_fingerprint()
            utils.logger.info(f'ADMIN LOGIN FROM: {utils.get_ip()}')
            flash('Login successfully', 'success')
            return redirect(url_for('router.admin.index'))
        else:
            login_limiter.record(client_key)
            utils.logger.warning(f'ADMIN LOGIN FAILED from {client_key}')
            return render_template('admin/login.html', user_ip=utils.get_ip(), getout=True)
        
    return render_template('admin/login.html', user_ip=utils.get_ip())

@bp.route('/logout')
@auth.admin_required
def logout():
    session.clear()
    flash('Logout successfully', 'success')
    return redirect(url_for('router.admin.login'))
