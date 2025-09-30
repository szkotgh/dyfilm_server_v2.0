from functools import wraps
import src.utils as utils
from flask import flash, g, redirect, url_for, session, request
import db.device
import hashlib

def generate_session_fingerprint():
    user_ip = utils.get_ip()
    user_agent = request.headers.get('User-Agent', '')
    fingerprint_data = f"{user_ip}:{user_agent}"
    return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]

def validate_session_fingerprint():
    stored_fingerprint = session.get('SESSION_FINGERPRINT')
    current_fingerprint = generate_session_fingerprint()
    
    if not stored_fingerprint:
        return False
    
    if stored_fingerprint != current_fingerprint:
        utils.logger.warning(f'Session fingerprint mismatch - Stored: {stored_fingerprint}, Current: {current_fingerprint}')
        return False
    
    return True

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            admin_status = session.get('ADMIN')
            admin_last_active_time = session.get('ADMIN_LAST_ACTIVE_TIME')
            
            if admin_status is None or admin_last_active_time is None:
                session.clear()
                flash('Admin login required', 'error')
                return redirect(url_for('router.admin.login'))
            
            if admin_status != True:
                session.clear()
                flash('Admin login required', 'error')
                return redirect(url_for('router.admin.login'))
            
            if not validate_session_fingerprint():
                session.clear()
                flash('Session security validation failed. Please log in again.', 'error')
                utils.logger.warning(f'Session fingerprint validation failed for IP: {utils.get_ip()}')
                return redirect(url_for('router.admin.login'))
            
            admin_last_active_datetime = utils.convert_string_to_datetime(admin_last_active_time)
            if admin_last_active_datetime is False:
                session.clear()
                flash('Invalid session data. Please log in again.', 'error')
                return redirect(url_for('router.admin.login'))
            
            now_datetime = utils.get_now_datetime()
            time_diff = now_datetime - admin_last_active_datetime
            
            if time_diff.total_seconds() < 0:
                session.clear()
                flash('Invalid session time. Please log in again.', 'error')
                return redirect(url_for('router.admin.login'))
            
            session_timeout = int(utils.get_env('ADMIN_SESSION_TIMEOUT'))
            if time_diff.total_seconds() > session_timeout:
                session.clear()
                flash('Admin session expired. Log again.', 'error')
                return redirect(url_for('router.admin.login'))
            
            session['ADMIN_LAST_ACTIVE_TIME'] = utils.get_now_datetime_str()
            
        except (KeyError, ValueError, TypeError) as e:
            session.clear()
            flash('Invalid session data. Please log in again.', 'error')
            return redirect(url_for('router.admin.login'))
        except Exception as e:
            session.clear()
            flash('Session validation error. Please log in again.', 'error')
            return redirect(url_for('router.admin.login'))
        
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