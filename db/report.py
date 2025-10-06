import db
import src.utils as utils
from datetime import datetime

def report_create(cf_id: str, reason: str, reporter_ip: str) -> bool:
    try:
        current_time = utils.get_now_datetime_str()
        db.cursor.execute(
            "INSERT INTO report (cf_id, reason, reporter_ip, report_time) VALUES (?, ?, ?, ?)",
            (cf_id, reason, reporter_ip, current_time)
        )
        db.conn.commit()
        return True
    except Exception as e:
        print(f"Error creating report: {e}")
        return False

def report_get_all() -> list:
    try:
        db.cursor.execute("""
            SELECT r.*, c.file_name, c."create" as capframe_create_time 
            FROM report r 
            JOIN capframe c ON r.cf_id = c.cf_id 
            ORDER BY r.report_time DESC
        """)
        return db.cursor.fetchall()
    except Exception as e:
        print(f"Error getting reports: {e}")
        return []

def report_get_by_id(report_id: int):
    try:
        db.cursor.execute("SELECT * FROM report WHERE report_id = ?", (report_id,))
        return db.cursor.fetchone()
    except Exception as e:
        print(f"Error getting report: {e}")
        return None

def report_approve(report_id: int) -> bool:
    try:
        report = report_get_by_id(report_id)
        if not report:
            return False
        
        cf_id = report[1]
        current_time = utils.get_now_datetime_str()
        
        db.cursor.execute(
            "UPDATE report SET is_approved = 1, admin_review_time = ? WHERE report_id = ?",
            (current_time, report_id)
        )
        
        db.cursor.execute(
            "UPDATE capframe SET status = 0 WHERE cf_id = ?",
            (cf_id,)
        )
        
        db.conn.commit()
        return True
    except Exception as e:
        print(f"Error approving report: {e}")
        return False

def report_reject(report_id: int) -> bool:
    try:
        current_time = utils.get_now_datetime_str()
        db.cursor.execute(
            "UPDATE report SET is_approved = 0, admin_review_time = ? WHERE report_id = ?",
            (current_time, report_id)
        )
        db.conn.commit()
        return True
    except Exception as e:
        print(f"Error rejecting report: {e}")
        return False

def report_get_pending_count() -> int:
    try:
        db.cursor.execute("SELECT COUNT(*) FROM report WHERE is_approved IS NULL")
        result = db.cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error getting pending report count: {e}")
        return 0

def report_pending_exists_for_cf_id(cf_id: str) -> bool:
    try:
        db.cursor.execute("SELECT COUNT(*) FROM report WHERE cf_id = ? AND is_approved IS NULL", (cf_id,))
        result = db.cursor.fetchone()
        return result[0] > 0 if result else False
    except Exception as e:
        print(f"Error checking pending report existence: {e}")
        return False

def report_exists_for_cf_id(cf_id: str) -> bool:
    try:
        db.cursor.execute("SELECT COUNT(*) FROM report WHERE cf_id = ?", (cf_id,))
        result = db.cursor.fetchone()
        return result[0] > 0 if result else False
    except Exception as e:
        print(f"Error checking report existence: {e}")
        return False

def report_get_by_cf_id(cf_id: str):
    try:
        db.cursor.execute("SELECT * FROM report WHERE cf_id = ? ORDER BY report_time DESC LIMIT 1", (cf_id,))
        return db.cursor.fetchone()
    except Exception as e:
        print(f"Error getting report by cf_id: {e}")
        return None

def report_get_list_paginated(limit: int, offset: int):
    try:
        db.cursor.execute("""
            SELECT r.*, c.file_name, c."create" as capframe_create_time 
            FROM report r 
            JOIN capframe c ON r.cf_id = c.cf_id 
            ORDER BY r.report_time DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        rows = db.cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error getting paginated reports: {e}")
        return []

def report_count() -> int:
    try:
        db.cursor.execute("SELECT COUNT(*) FROM report")
        row = db.cursor.fetchone()
        return int(row[0]) if row else 0
    except Exception as e:
        print(f"Error getting report count: {e}")
        return 0
