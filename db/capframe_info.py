import db
import src.utils as utils
from datetime import datetime

def capframe_info_get_list():
    db.cursor.execute("SELECT * FROM capframe_info")
    rows = db.cursor.fetchall()
    return rows

def capframe_info_get(cf_id: str):
    db.cursor.execute('''
        SELECT * FROM capframe_info WHERE c_id = ?
    ''', (cf_id,))
    rows = db.cursor.fetchall()
    
    if not rows: return False
    return rows

def capframe_info_add(cf_id: str, c_id: str, c_no: int):
    db.cursor.execute('''
        INSERT INTO capframe_info (cf_id, c_id, c_no) VALUES (?, ?, ?)
    ''', (cf_id, c_id, c_no))
    db.conn.commit()
    
    return True