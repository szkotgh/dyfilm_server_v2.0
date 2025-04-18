import db
import src.utils as utils
from datetime import datetime

def capframe_get_list():
    db.cursor.execute("SELECT * FROM capframe")
    rows = db.cursor.fetchall()
    return rows

def capframe_get(cf_id):
    db.cursor.execute("SELECT * FROM capframe WHERE cf_id = ?", (cf_id,))
    row = db.cursor.fetchone()
    return row

def capframe_create(cf_id:str, d_id:int, f_id:int, file_name, processing_time:float):
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        db.cursor.execute("INSERT INTO capframe (cf_id, d_id, f_id, file_name, 'create', processing_time) VALUES (?, ?, ?, ?, ?, ?)",
                        (cf_id, d_id, f_id, file_name, current_date, processing_time));
        db.conn.commit()
        return True
    except:
        return False

def capframe_remove(cf_id:str):
    try:
        db.cursor.execute("DELETE FROM capframe WHERE cf_id = ?", (cf_id,))
        db.conn.commit()
        return True
    except:
        return False

def capframe_config_desc(cf_id:str, desc:str):
    db.cursor.execute("UPDATE capframe SET desc = ? WHERE cf_id = ?", (desc, cf_id))
    db.conn.commit()
    
    return True

def capframe_config_status(cf_id:str, status:bool):
    db.cursor.execute("UPDATE capframe SET status = ? WHERE cf_id = ?", (status, cf_id))
    db.conn.commit()
    
    return True