import db
import src.utils as utils
from datetime import datetime
import os

def main_image_get(mi_id):
    db.cursor.execute("SELECT * FROM main_image WHERE mi_id = ?", (mi_id,))
    row = db.cursor.fetchone()
    return row

def main_image_get_list():
    db.cursor.execute("SELECT * FROM main_image ORDER BY mi_id DESC")
    rows = db.cursor.fetchall()
    return rows

def main_image_get_list_paginated(limit: int, offset: int):
    try:
        db.cursor.execute('SELECT * FROM main_image ORDER BY mi_id DESC LIMIT ? OFFSET ?', (limit, offset))
        rows = db.cursor.fetchall()
        return rows
    except Exception:
        db.cursor.execute("SELECT * FROM main_image ORDER BY mi_id DESC")
        rows = db.cursor.fetchall()
        return rows[offset:offset+limit]

def main_image_count() -> int:
    try:
        db.cursor.execute('SELECT COUNT(*) as count FROM main_image')
        row = db.cursor.fetchone()
        return int(row['count']) if row else 0
    except Exception:
        return 0

def main_image_create(file_name: str, desc: str = None) -> bool:
    try:
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        db.cursor.execute('''
            INSERT INTO main_image (file_name, desc, is_default, "create") VALUES (?, ?, ?, ?)
        ''', (file_name, desc, False, current_date))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False

def main_image_remove(mi_id: int) -> bool:
    try:
        # 파일 삭제
        main_image = main_image_get(mi_id)
        if main_image:
            file_path = os.path.join(db.MAIN_IMAGE_DIR_PATH, main_image['file_name'])
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
        
        # main_image_device 테이블의 데이터는 CASCADE로 자동 삭제됨
        db.cursor.execute('''
            DELETE FROM main_image WHERE mi_id = ?
        ''', (mi_id,))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False

def main_image_config_desc(mi_id: int, desc: str) -> bool:
    try:
        db.cursor.execute('''
            UPDATE main_image SET desc = ? WHERE mi_id = ?
        ''', (desc, mi_id))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False

def main_image_config_file_name(mi_id: int, file_name: str) -> bool:
    try:
        db.cursor.execute('''
            UPDATE main_image SET file_name = ? WHERE mi_id = ?
        ''', (file_name, mi_id))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False

def main_image_set_default(mi_id: int) -> bool:
    try:
        # 모든 is_default를 False로 설정
        db.cursor.execute('''
            UPDATE main_image SET is_default = ?
        ''', (False,))
        
        # 선택한 항목을 True로 설정
        db.cursor.execute('''
            UPDATE main_image SET is_default = ? WHERE mi_id = ?
        ''', (True, mi_id))
        if db.cursor.rowcount == 0: return False
        db.conn.commit()
        return True
    except Exception:
        return False

def main_image_unset_default() -> bool:
    """모든 기본 이미지를 해제합니다."""
    try:
        db.cursor.execute('''
            UPDATE main_image SET is_default = ?
        ''', (False,))
        db.conn.commit()
        return True
    except Exception:
        return False

def main_image_get_devices(mi_id: int):
    """특정 main_image에 연결된 장치 목록을 반환합니다."""
    try:
        db.cursor.execute('''
            SELECT d_id FROM main_image_device WHERE mi_id = ?
        ''', (mi_id,))
        rows = db.cursor.fetchall()
        return [row['d_id'] for row in rows]
    except Exception:
        return []

def main_image_set_devices(mi_id: int, device_ids: list) -> bool:
    """특정 main_image에 연결된 장치들을 설정합니다."""
    try:
        # 기존 연결 제거
        db.cursor.execute('''
            DELETE FROM main_image_device WHERE mi_id = ?
        ''', (mi_id,))
        
        # 새 연결 추가
        if device_ids:
            for d_id in device_ids:
                if d_id:  # None이나 빈 값 제외
                    db.cursor.execute('''
                        INSERT OR IGNORE INTO main_image_device (mi_id, d_id) VALUES (?, ?)
                    ''', (mi_id, int(d_id)))
        
        db.conn.commit()
        return True
    except Exception:
        return False

def main_image_get_for_device(device_id: int):
    """
    장치에 맞는 main_image를 반환합니다.
    우선순위: main_image_device 조인 테이블 > is_default > None
    """
    # 1. main_image_device 조인 테이블로 설정된 이미지 찾기
    db.cursor.execute('''
        SELECT mi.* FROM main_image mi
        INNER JOIN main_image_device mid ON mi.mi_id = mid.mi_id
        WHERE mid.d_id = ?
        ORDER BY mi.mi_id DESC
        LIMIT 1
    ''', (device_id,))
    row = db.cursor.fetchone()
    if row:
        return row
    
    # 2. is_default가 True인 이미지 찾기
    db.cursor.execute('''
        SELECT * FROM main_image WHERE is_default = ? LIMIT 1
    ''', (True,))
    row = db.cursor.fetchone()
    if row:
        return row
    
    # 3. 장치별 설정도 없고 전역 기본 이미지도 없으면 None 반환
    return None
