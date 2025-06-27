from functools import wraps
import src.utils as utils
from flask import flash, g, redirect, url_for, session, request
import db.device

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            session['ADMIN']
            session['ADMIN_LAST_ACTIVE_TIME']
        except:
            session.clear()
            flash('Admin login required', 'error')
            return redirect(url_for('router.admin.login'))
        
        if session.get('ADMIN', False) == False:
            session.clear()
            flash('Admin login required', 'error')
            return redirect(url_for('router.admin.login'))
        
        admin_last_active_datetime = utils.convert_string_to_datetime(session['ADMIN_LAST_ACTIVE_TIME'])
        now_datetime_diff = utils.get_now_datetime() - admin_last_active_datetime
        if int(now_datetime_diff.total_seconds()) > int(utils.get_env('ADMIN_SESSION_TIMEOUT')):
            session.clear()
            flash('Admin session expired. Log again.', 'error')
            return redirect(url_for('router.admin.login'))
        
        session['ADMIN_LAST_ACTIVE_TIME'] = utils.get_now_datetime_str()
        
        return f(*args, **kwargs)
    return decorated_function

def device_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token = request.headers.get('Authorization')
        if not auth_token or not auth_token.strip():
            return utils.get_code('authorize_failed')
        
        db_result = db.device.device_get_by_token(auth_token)
        if not db_result:
            return utils.get_code('authorize_failed')
        
        # last use time update
        db.device.device_update_last_use_time(db_result[0])
        
        # temp save device info data
        g.device_info = db_result
        return f(*args, **kwargs)
    return decorated_function

def device_auth_with_status(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_token = request.headers.get('Authorization')
        if not auth_token or not auth_token.strip():
            return utils.get_code('authorize_failed')
        
        db_result = db.device.device_get_by_token(auth_token)
        if not db_result:
            return utils.get_code('authorize_failed')
        
        # check device status
        if db_result[1] == False:
            return utils.get_code('device_disabled')
        
        # last use time update
        db.device.device_update_last_use_time(db_result[0])
        
        # temp save device info data
        g.device_info = (db_result)
        return f(*args, **kwargs)
    return decorated_function