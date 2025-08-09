import db
import src.utils as utils
from datetime import datetime

def capture_get_list():
    db.cursor.execute("SELECT * FROM capture")
    rows = db.cursor.fetchall()
    rows.reverse()
    return rows

def capture_get_list_paginated(limit: int, offset: int):
    try:
        db.cursor.execute('SELECT * FROM capture ORDER BY "create" DESC LIMIT ? OFFSET ?', (limit, offset))
        rows = db.cursor.fetchall()
        return rows
    except Exception:
        db.cursor.execute("SELECT * FROM capture")
        rows = db.cursor.fetchall()
        rows.reverse()
        return rows[offset:offset+limit]

def capture_count() -> int:
    try:
        db.cursor.execute('SELECT COUNT(*) FROM capture')
        row = db.cursor.fetchone()
        return int(row[0]) if row else 0
    except Exception:
        return 0

def capture_get(c_id: str):
    db.cursor.execute('''
        SELECT * FROM capture WHERE c_id = ?
    ''', (c_id,))
    row = db.cursor.fetchone()
    
    if not row: return False
    return row

def capture_create(c_id, d_id, file_name):
    try:
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        db.cursor.execute('''
            INSERT INTO capture (c_id, d_id, file_name, 'create') VALUES (?, ?, ?, ?)               
        ''', (c_id, d_id, file_name, current_date))
        
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        
        return True
    
    except:
        return False

def capture_remove(c_id):
    try:
        db.cursor.execute('''
            DELETE FROM capture WHERE c_id = ?
        ''', (c_id,))
        
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        
        return True
    
    except:
        return False

def capture_config_desc(c_id, config_desc):
    try:
        db.cursor.execute('''
            UPDATE capture SET desc = ? WHERE c_id = ?
        ''', (config_desc, c_id))
        
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        
        return True
    
    except:
        return False
    
def capture_config_status(c_id, status):
    try:
        db.cursor.execute('''
            UPDATE capture SET status = ? WHERE c_id = ?
        ''', (status, c_id))
        
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        
        return True
    
    except:
        return False