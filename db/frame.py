import db
import src.utils as utils
from datetime import datetime

def frame_get_list():
    db.cursor.execute("SELECT * FROM frame")
    rows = db.cursor.fetchall()
    rows.reverse()
    return rows

def frame_get_list_paginated(limit: int, offset: int):
    try:
        db.cursor.execute('SELECT * FROM frame ORDER BY "create" DESC LIMIT ? OFFSET ?', (limit, offset))
        rows = db.cursor.fetchall()
        return rows
    except Exception:
        db.cursor.execute("SELECT * FROM frame")
        rows = db.cursor.fetchall()
        rows.reverse()
        return rows[offset:offset+limit]

def frame_count() -> int:
    try:
        db.cursor.execute('SELECT COUNT(*) as count FROM frame')
        row = db.cursor.fetchone()
        return int(row['count']) if row else 0
    except Exception:
        return 0

def frame_get(f_id: int):
    db.cursor.execute('''
        SELECT * FROM frame WHERE f_id = ?
    ''', (f_id,))
    row = db.cursor.fetchone()
    
    if not row: return False
    return row

def frame_create(file_name, meta, desc) -> bool:
    try:
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        db.cursor.execute('''
            INSERT INTO frame (file_name, meta, desc, "create") VALUES (?, ?, ?, ?)
        ''', (file_name, meta, desc, current_date))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False
    
def frame_config_status(f_id: int, status: bool) -> bool:
    try:
        db.cursor.execute('''
            UPDATE frame SET status = ? WHERE f_id = ?
        ''', (status, f_id))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False
    
def frame_config_meta(f_id: int, meta: str) -> bool:
    try:
        db.cursor.execute('''
            UPDATE frame SET meta = ? WHERE f_id = ?
        ''', (meta, f_id))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False
    
def frame_config_desc(f_id: int, desc: str) -> bool:
    try:
        if desc is None or desc.strip() == '': return False
        
        db.cursor.execute('''
            UPDATE frame SET desc = ? WHERE f_id = ?
        ''', (desc, f_id))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False
    
def frame_remove(f_id: int) -> bool:
    try:
        db.cursor.execute('''
            DELETE FROM frame WHERE f_id = ?
        ''', (f_id,))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False
