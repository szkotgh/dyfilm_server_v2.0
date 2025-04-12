import sqlite3
import os
import os.path as path

DB_HOME = './db'
DB_FILE = path.join(DB_HOME, 'meta.db')
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

FRAMES_PATH = path.join(DB_HOME, 'frames')
CAPTURES_PATH = path.join(DB_HOME, 'captures')
CAPFRAMES_PATH = path.join(DB_HOME, 'capframes')

# init
if not path.exists(FRAMES_PATH):
    os.makedirs(FRAMES_PATH)
    cursor.execute
    
if not path.exists(CAPTURES_PATH):
    os.makedirs(CAPTURES_PATH)
    
if not path.exists(CAPFRAMES_PATH):
    os.makedirs(CAPFRAMES_PATH)

