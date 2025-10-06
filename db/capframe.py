import json
import os
import time

from flask import g, url_for
import db
import src.utils as utils
from datetime import datetime
import db.device
import db.capture
import db.frame
import db.capframe_info
from PIL import Image, ImageDraw, ImageFont

def capframe_get_list():
    db.cursor.execute("SELECT * FROM capframe")
    rows = db.cursor.fetchall()
    rows.reverse()
    return rows

def capframe_get_list_paginated(limit: int, offset: int):
    try:
        db.cursor.execute('SELECT * FROM capframe ORDER BY "create" DESC LIMIT ? OFFSET ?', (limit, offset))
        rows = db.cursor.fetchall()
        return rows
    except Exception:
        db.cursor.execute("SELECT * FROM capframe")
        rows = db.cursor.fetchall()
        rows.reverse()
        return rows[offset:offset+limit]

def capframe_count() -> int:
    try:
        db.cursor.execute('SELECT COUNT(*) as count FROM capframe')
        row = db.cursor.fetchone()
        return int(row['count']) if row else 0
    except Exception:
        return 0

def capframe_get(cf_id):
    db.cursor.execute("SELECT * FROM capframe WHERE cf_id = ?", (cf_id,))
    row = db.cursor.fetchone()
    return row

def capframe_create(d_id:int, f_id:int, c_id: list):
    # check parameter vaild
    if not f_id or not c_id or type(f_id) != int or type(c_id) != list:
        g.capframe_fall_info = "missing parameter"
        return False
    
    frame_info = db.frame.frame_get(f_id)
    if not frame_info:
        g.capframe_fall_info = "invalid parameter: f_id, frame not found"
        return False
    
    frame_meta = json.loads(frame_info['meta'])
    frame_capture_count = len(frame_meta['captures'])
    if len(c_id) < frame_capture_count:
        g.capframe_fall_info = "invalid parameter: c_id list"
        return False
    for l in c_id:
        if type(l) != str:
            g.capframe_fall_info = "invalid parameter: c_id"
            return False
    
    # init variable
    cf_id = utils.gen_hash()
    start_time = time.time()
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    SAVE_NAME = f"{cf_id}.png"
    SAVE_PATH = os.path.join(db.CAPFRAMES_PATH, SAVE_NAME)
    
    CANVAS_SIZE = frame_meta['canvas']['size']
    TIME_LOCA = frame_meta['canvas']['time_loca']
    TIME_FONT_SIZE = frame_meta['canvas']['time_font_size']
    TIME_FONT_COLOR = frame_meta['canvas']['time_font_color']
    QR_LOCA = frame_meta['canvas']['qr_loca']
    QR_SIZE = frame_meta['canvas']['qr_size']
    
    # capframe create start
    ## capture check
    ready_captures = []
    for i in range(frame_capture_count):
        capture_info = db.capture.capture_get(c_id[i])
        if not capture_info:
            g.capframe_fall_info = "invalid parameter: c_id, capture not found"
            return False
        ready_captures.append(capture_info)
    
    # create canvas
    capframe = Image.new("RGBA", CANVAS_SIZE, (255, 255, 255, 0))
    capframe_draw = ImageDraw.Draw(capframe)
    
    # draw capture
    for index, capture in enumerate(frame_meta['captures']):
        capture_info = ready_captures[index]
        
        CAPTURE_PATH = os.path.join(db.CAPTURES_PATH, capture_info['file_name'])
        capture_img = Image.open(CAPTURE_PATH).convert("RGB")
        img_width, img_height = capture_img.size
        target_width, target_height = capture['size']
        
        ## 세로가 길면 세로를 크기에 맞춰 리사이즈 (가로는 비율 유지)
        if img_height > target_height:
            scale = target_height / img_height
            new_width = int(img_width * scale)
            capture_img = capture_img.resize((new_width, target_height), Image.LANCZOS)
            img_width, img_height = new_width, target_height
        
        ## 가로가 타겟보다 길면 가운데를 기준으로 크롭
        if img_width > target_width:
            left = (img_width - target_width) // 2
            right = left + target_width
            capture_img = capture_img.crop((left, 0, right, img_height))
            img_width = target_width
        
        ## 이미지가 타겟보다 작으면 확대 (비율 유지)
        if img_width < target_width or img_height < target_height:
            scale = max(target_width / img_width, target_height / img_height)
            new_size = (int(img_width * scale), int(img_height * scale))
            capture_img = capture_img.resize(new_size, Image.LANCZOS)
            img_width, img_height = new_size
        
        ## 최종 크롭 (타겟 크기에 정확히 맞추기)
        if img_width != target_width or img_height != target_height:
            left = (img_width - target_width) // 2
            top = (img_height - target_height) // 2
            right = left + target_width
            bottom = top + target_height
            capture_img = capture_img.crop((left, top, right, bottom))
        
        capframe.paste(capture_img, capture['loca'])
    
    # draw frame
    FRAME_PATH = os.path.join(db.FRAMES_PATH, frame_info['file_name'])
    frame = Image.open(FRAME_PATH).convert("RGBA")
    frame = frame.resize(CANVAS_SIZE)
    capframe.paste(frame, (0, 0), frame)
    
    # draw qr
    QR_PATH = os.path.join(db.QR_PATH, f'{cf_id}.png')
    utils.gen_qr(
        save_path=QR_PATH,
        url_path=url_for('router.view.view_capframe.view_capframe', cf_id=cf_id)
    )
    qr_img = Image.open(QR_PATH)
    qr_img = qr_img.resize(QR_SIZE)
    capframe.paste(qr_img, QR_LOCA)
    
    # draw time
    font = ImageFont.truetype('static/fonts/AppleSDGothicNeoL.ttf', TIME_FONT_SIZE)
    now_datetime = datetime.now()
    now_datetime_str = now_datetime.strftime('%Y-%m-%d %H:%M')
    capframe_draw.text(
        TIME_LOCA,
        now_datetime_str,
        font=font,
        fill=tuple(TIME_FONT_COLOR),
    )
    
    end_time = time.time()
    processing_time = round(float(end_time - start_time), 4)
    
    # save capframe
    ## save image file
    try:
        capframe.save(SAVE_PATH)
    except:
        g.capframe_fall_info = "failed to save capframe image"
        return False
    
    ## save capframe db
    try:
        db.cursor.execute("INSERT INTO capframe (cf_id, d_id, f_id, file_name, 'create', processing_time) VALUES (?, ?, ?, ?, ?, ?)",
                          (cf_id, d_id, f_id, SAVE_NAME, current_date, processing_time));
        db.conn.commit()
    except:
        g.capframe_fall_info = "failed to save capframe db"
        return False
    
    ## save capframe_info db
    for index, capture in enumerate(frame_meta['captures']):
        capture_info = ready_captures[index]
        result = db.capframe_info.capframe_info_add(
            cf_id=cf_id,
            c_id=capture_info['c_id'],
            c_no=index
        )
        if not result:
            g.capframe_fall_info = "failed to save capframe_info db"
            capframe_remove(cf_id)
            return False
    
    db.cursor.execute("UPDATE frame SET use_count = use_count + 1 WHERE f_id = ?", (f_id,))
    db.conn.commit()
    
    return cf_id

def capframe_remove(cf_id: str):
    try:
        db.cursor.execute("SELECT f_id FROM capframe WHERE cf_id = ?", (cf_id,))
        row = db.cursor.fetchone()
        if row:
            f_id = row['f_id']
        else:
            return False

        # 삭제
        db.cursor.execute("DELETE FROM capframe WHERE cf_id = ?", (cf_id,))
        db.conn.commit()

        # ✅ use_count 감소
        db.cursor.execute("UPDATE frame SET use_count = use_count - 1 WHERE f_id = ?", (f_id,))
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
