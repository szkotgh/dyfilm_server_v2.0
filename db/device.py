import db
import src.utils as utils
from datetime import datetime

def device_get_list():
    db.cursor.execute("SELECT * FROM device")
    rows = db.cursor.fetchall()
    return rows

def device_get_list_paginated(limit: int, offset: int):
    try:
        db.cursor.execute('SELECT * FROM device ORDER BY "create" DESC LIMIT ? OFFSET ?', (limit, offset))
        rows = db.cursor.fetchall()
        return rows
    except Exception:
        db.cursor.execute("SELECT * FROM device")
        rows = db.cursor.fetchall()
        return rows[offset:offset+limit]

def device_count() -> int:
    try:
        db.cursor.execute('SELECT COUNT(*) FROM device')
        row = db.cursor.fetchone()
        return int(row[0]) if row else 0
    except Exception:
        return 0

def device_get(d_id: int):
    db.cursor.execute('''
        SELECT * FROM device WHERE d_id = ?
    ''', (d_id,))
    row = db.cursor.fetchone()
    
    if not row: return False
    return row

def device_get_by_token(auth_token: str):
    try:
        db.cursor.execute('''
            SELECT * FROM device WHERE auth_token = ?
        ''', (auth_token,))
        row = db.cursor.fetchone()
        
        if not row: return False
        
        return row
    except Exception:
        return False

def device_create() -> bool:
    try:
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        auth_token = utils.gen_hash()
        
        db.cursor.execute('''
            INSERT INTO device (auth_token, "create") VALUES (?, ?)
        ''', (auth_token, current_date))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False

def device_config_status(d_id: int, status: bool) -> bool:
    try:
        db.cursor.execute('''
            UPDATE device SET status = ? WHERE d_id = ?
        ''', (status, d_id))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False

def device_config_desc(d_id: int, desc: str) -> bool:
    try:
        if desc is None or desc.strip() == '': return False
        db.cursor.execute('''
            UPDATE device SET desc = ? WHERE d_id = ?
        ''', (desc, d_id))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False

def device_update_last_use_time(d_id: int) -> bool:
    try:
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.cursor.execute('''
            UPDATE device SET last_use = ? WHERE d_id = ?
        ''', (current_date, d_id))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False

def device_config_auth_token(d_id: int) -> bool:
    try:
        auth_token = utils.gen_hash(len=32)
        
        db.cursor.execute('''
            UPDATE device SET auth_token = ? WHERE d_id = ?
        ''', (auth_token, d_id))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False

def device_remove(d_id: int) -> bool:
    try:
        db.cursor.execute('''
            DELETE FROM device WHERE d_id = ?
        ''', (d_id,))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False
