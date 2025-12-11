import sqlite3
import os
from datetime import datetime, timedelta
import os.path as path
import src.utils as utils

DB_HOME = './db'
DB_FILE = path.join(DB_HOME, 'database.db')
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

MAIN_IMAGE_DIR_PATH = path.join(DB_HOME, 'main_image')
FRAMES_PATH = path.join(DB_HOME, 'frames')
CAPTURES_PATH = path.join(DB_HOME, 'captures')
CAPFRAMES_PATH = path.join(DB_HOME, 'capframes')
QR_PATH = path.join(DB_HOME, 'qr')

# init
if not os.path.exists(MAIN_IMAGE_DIR_PATH): os.makedirs(MAIN_IMAGE_DIR_PATH)
if not os.path.exists(QR_PATH): os.makedirs(QR_PATH)
if not path.exists(FRAMES_PATH): os.makedirs(FRAMES_PATH)
if not path.exists(CAPTURES_PATH): os.makedirs(CAPTURES_PATH)
if not path.exists(CAPFRAMES_PATH): os.makedirs(CAPFRAMES_PATH)

cursor.execute('PRAGMA foreign_keys = ON;')
## DEVICE
cursor.execute('''
    CREATE TABLE IF NOT EXISTS device (
        d_id INTEGER PRIMARY KEY AUTOINCREMENT,
        status BOOLEAN NOT NULL DEFAULT FALSE,
        desc TEXT,
        auth_token TEXT NOT NULL,
        "create" DATETIME NOT NULL,
        last_use DATETIME
    )
''')
## MAIN_IMAGE
cursor.execute('''
    CREATE TABLE IF NOT EXISTS main_image (
        mi_id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT NOT NULL,
        desc TEXT,
        is_default BOOLEAN NOT NULL DEFAULT FALSE,
        "create" DATETIME NOT NULL
    )
''')
## MAIN_IMAGE_DEVICE (main_image와 device의 다대다 관계)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS main_image_device (
        mi_id INTEGER NOT NULL,
        d_id INTEGER NOT NULL,
        
        FOREIGN KEY (mi_id) REFERENCES main_image (mi_id) ON DELETE CASCADE,
        FOREIGN KEY (d_id) REFERENCES device (d_id) ON DELETE CASCADE,
        
        PRIMARY KEY (mi_id, d_id)
    )
''')
# 기존 default_device_id 데이터 마이그레이션 (한 번만 실행)
try:
    cursor.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='main_image' 
        AND sql LIKE '%default_device_id%'
    ''')
    if cursor.fetchone():
        # 기존 default_device_id가 있는 경우 마이그레이션
        cursor.execute('''
            SELECT mi_id, default_device_id FROM main_image 
            WHERE default_device_id IS NOT NULL
        ''')
        old_data = cursor.fetchall()
        for row in old_data:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO main_image_device (mi_id, d_id) 
                    VALUES (?, ?)
                ''', (row['mi_id'], row['default_device_id']))
            except:
                pass
        conn.commit()
        # default_device_id 컬럼 제거 (SQLite는 ALTER TABLE DROP COLUMN을 지원하지 않으므로 새 테이블 생성)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS main_image_new (
                mi_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                desc TEXT,
                is_default BOOLEAN NOT NULL DEFAULT FALSE,
                "create" DATETIME NOT NULL
            )
        ''')
        cursor.execute('''
            INSERT INTO main_image_new (mi_id, file_name, desc, is_default, "create")
            SELECT mi_id, file_name, desc, is_default, "create" FROM main_image
        ''')
        cursor.execute('DROP TABLE main_image')
        cursor.execute('ALTER TABLE main_image_new RENAME TO main_image')
        conn.commit()
except:
    pass
## FRAME
cursor.execute('''
    CREATE TABLE IF NOT EXISTS frame (
        f_id INTEGER PRIMARY KEY AUTOINCREMENT,
        status BOOLEAN NOT NULL DEFAULT TRUE,
        file_name TEXT NOT NULL,
        meta TEXT NOT NULL,
        desc TEXT,
        "create" DATETIME NOT NULL,
        use_count INTEGER NOT NULL DEFAULT 0
    )
''')
## CAPTURE
cursor.execute('''
    CREATE TABLE IF NOT EXISTS capture (
        c_id TEXT PRIMARY KEY NOT NULL,
        d_id INTEGER,
        status BOOLEAN NOT NULL DEFAULT TRUE,
        file_name TEXT NOT NULL,
        desc TEXT,
        "create" DATETIME NOT NULL,
        
        FOREIGN KEY (d_id) REFERENCES device (d_id)
    )
''')
## CAPFRAME
cursor.execute('''
    CREATE TABLE IF NOT EXISTS capframe (
        cf_id TEXT PRIMARY KEY NOT NULL,
        d_id INTEGER,
        f_id INTEGER NOT NULL,
        status BOOLEAN NOT NULL DEFAULT TRUE,
        file_name TEXT NOT NULL,
        desc TEXT,
        "create" DATETIME NOT NULL,
        processing_time REAL,
        
        FOREIGN KEY (d_id) REFERENCES device (d_id),
        FOREIGN KEY (f_id) REFERENCES frame (f_id)
    )
''')
## CAPFRAME_INFO
cursor.execute('''
    CREATE TABLE IF NOT EXISTS capframe_info (
        cf_id TEXT,
        c_id TEXT,
        c_no INTEGER NOT NULL,
        
        FOREIGN KEY (cf_id) REFERENCES capframe (cf_id) ON DELETE CASCADE,
        FOREIGN KEY (c_id) REFERENCES capture (c_id),
        
        PRIMARY KEY (cf_id, c_no)
    )
''')

## REPORT
cursor.execute('''
    CREATE TABLE IF NOT EXISTS report (
        report_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cf_id TEXT NOT NULL,
        reason TEXT NOT NULL,
        admin_review_time DATETIME,
        is_approved INTEGER DEFAULT NULL,
        reporter_ip TEXT NOT NULL,
        report_time DATETIME NOT NULL,
        
        FOREIGN KEY (cf_id) REFERENCES capframe (cf_id) ON DELETE CASCADE
    )
''')

def get_statistics():
    stats = {}
    
    # 전체 capframe 개수 (완성된 사진)
    cursor.execute("SELECT COUNT(*) as count FROM capframe WHERE status = 1")
    stats['total_capframes'] = cursor.fetchone()['count']
    
    # 일주일간 capframe 개수
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("SELECT COUNT(*) as count FROM capframe WHERE status = 1 AND 'create' >= ?", (week_ago,))
    stats['weekly_capframes'] = cursor.fetchone()['count']
    
    # 전체 capture 개수 (개별 사진)
    cursor.execute("SELECT COUNT(*) as count FROM capture WHERE status = 1")
    stats['total_captures'] = cursor.fetchone()['count']
    
    # 오늘 capframe 개수
    today = datetime.now().strftime('%Y-%m-%d 00:00:00')
    cursor.execute("SELECT COUNT(*) as count FROM capframe WHERE status = 1 AND date('create') >= ?", (today,))
    stats['today_capframes'] = cursor.fetchone()['count']
    
    # 일주일간 capture 개수
    cursor.execute("SELECT COUNT(*) as count FROM capture WHERE status = 1 AND 'create' >= ?", (week_ago,))
    stats['weekly_captures'] = cursor.fetchone()['count']
    
    # 활성 디바이스 개수
    cursor.execute("SELECT COUNT(*) as count FROM device WHERE status = 1")
    stats['active_devices'] = cursor.fetchone()['count']
    
    # 전체 디바이스 개수
    cursor.execute("SELECT COUNT(*) as count FROM device")
    stats['total_devices'] = cursor.fetchone()['count']
    
    # 활성 프레임 개수
    cursor.execute("SELECT COUNT(*) as count FROM frame WHERE status = 1")
    stats['active_frames'] = cursor.fetchone()['count']
    
    # 전체 프레임 개수
    cursor.execute("SELECT COUNT(*) as count FROM frame")
    stats['total_frames'] = cursor.fetchone()['count']
    
    # 처리 대기 중인 신고 개수
    cursor.execute("SELECT COUNT(*) as count FROM report WHERE is_approved IS NULL")
    stats['pending_reports'] = cursor.fetchone()['count']
    
    # 가장 많이 사용된 프레임 (상위 3개)
    # cursor.execute("""
    #     SELECT f.f_id, f."desc", f.use_count 
    #     FROM frame f 
    #     WHERE f.status = 1 
    #     ORDER BY f.use_count DESC 
    #     LIMIT 3
    # """)
    cursor.execute("""
        SELECT f.f_id, f."desc", f.use_count 
        FROM frame f 
        ORDER BY f.use_count DESC 
        LIMIT 3
    """)
    stats['top_frames'] = cursor.fetchall()
    
    # 최근 7일간 일별 capframe 생성 통계
    daily_stats = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) as count FROM capframe WHERE status = 1 AND date('create') = ?", (date,))
        count = cursor.fetchone()['count']
        daily_stats.append({'date': date, 'count': count})
    stats['daily_stats'] = list(reversed(daily_stats))
    
    return stats

