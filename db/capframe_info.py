import db
import src.utils as utils
from datetime import datetime

def capframe_get_list():
    db.cursor.execute("SELECT * FROM capframe_info")
    rows = db.cursor.fetchall()
    return rows

def capframe_get(cf_id: str):
    db.cursor.execute('''
        SELECT * FROM capframe_info WHERE c_id = ?
    ''', (cf_id,))
    rows = db.cursor.fetchone()
    
    if not rows: return False
    return rows

def capframe_create(d_id, f_id, file_name):
    try:
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        db.cursor.execute('''
            INSERT INTO capframe_info (d_id, f_id, file_name, create)
            VALUES (?, ?, ?, ?)
        ''', (d_id, f_id, file_name, current_date))
        
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        
        return True
    except Exception:
        return False