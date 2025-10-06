import os
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
import src.utils as utils
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

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('ADMIN', False) == True:
        flash('You are already logged in', 'info')
        return redirect(url_for('router.admin.index'))
    
    if request.method == 'POST':
        input_pw = request.form.get('password')
        
        if not input_pw or not input_pw.strip():
            return render_template('admin/login.html', user_ip=utils.get_ip(), getout=True)

        if bcrypt.checkpw(input_pw.encode('utf-8'), os.environ['ADMIN_PASSWORD'].encode('utf-8')):
            session.clear()
            session['ADMIN'] = True
            session['ADMIN_LAST_ACTIVE_TIME'] = utils.get_now_datetime_str()
            session['SESSION_FINGERPRINT'] = auth.generate_session_fingerprint()
            utils.logger.info(f'ADMIN LOGIN FROM: {utils.get_ip()}')
            flash('Login successfully', 'success')
            return redirect(url_for('router.admin.index'))
        else:
            return render_template('admin/login.html', user_ip=utils.get_ip(), getout=True)
        
    return render_template('admin/login.html', user_ip=utils.get_ip())

@bp.route('/logout')
@auth.admin_required
def logout():
    session.clear()
    flash('Logout successfully', 'success')
    return redirect(url_for('router.admin.login'))