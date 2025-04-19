import sqlite3
import os
from datetime import datetime
import os.path as path
import src.utils as utils

DB_HOME = './db'
DB_FILE = path.join(DB_HOME, 'main.db')
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

FRAMES_PATH = path.join(DB_HOME, 'frames')
CAPTURES_PATH = path.join(DB_HOME, 'captures')
CAPFRAMES_PATH = path.join(DB_HOME, 'capframes')
QR_PATH = path.join(DB_HOME, 'qr')

# init
if not os.path.exists(QR_PATH):
    os.makedirs(QR_PATH)

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
## FRAME
if not path.exists(FRAMES_PATH):
    os.makedirs(FRAMES_PATH)
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
if not path.exists(CAPTURES_PATH):
    os.makedirs(CAPTURES_PATH)
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
if not path.exists(CAPFRAMES_PATH):
    os.makedirs(CAPFRAMES_PATH)
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

