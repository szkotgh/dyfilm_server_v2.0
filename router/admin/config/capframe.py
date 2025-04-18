import json
import os
import time
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
import src.utils as utils
import auth
import db.capframe
import db.capframe_info
import db.frame
import db.capture
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

bp = Blueprint('capframe', __name__, url_prefix='/capframe')

@bp.before_request
@auth.admin_required
def check_admin():
    pass

@bp.route('/', methods=['GET'])
def index():
    return render_template('admin/config/capframe.html', user_ip=utils.get_ip(), capframes=db.capframe.capframe_get_list())

@bp.route('/create', methods=['GET'])
def create():
    return render_template('admin/config/capframe_create_first_select.html', user_ip=utils.get_ip(), frames=db.frame.frame_get_list())

@bp.route('/remove', methods=['POST'])
def remove():
    cf_id = request.form.get('cf_id')
    
    if not cf_id:
        flash('CapFrame ID is required', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    capframe_result = db.capframe.capframe_get(cf_id)
    if not capframe_result:
        flash('CapFrame not found', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    # remove capframe
    db_result = db.capframe.capframe_remove(cf_id)
    if not db_result:
        flash('Failed to remove CapFrame', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    file_name = capframe_result[4]
    file_path = os.path.join(db.CAPFRAMES_PATH, file_name)
    try:
        os.remove(file_path)
    except Exception as e:
        flash(f'Failed to remove capture image: {e}', 'error')
        return redirect(url_for('router.admin.config.capture.index'))
    
    flash('CapFrame removed successfully', 'success')
    return redirect(url_for('router.admin.config.capframe.index'))

@bp.route('/config_status', methods=['POST'])
def config_status():
    cf_id = request.form.get('cf_id')
    
    if not cf_id:
        flash('CapFrame ID and Status are required', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    db_result = db.capframe.capframe_get(cf_id)
    if not db_result:
        flash('CapFrame not found', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    status = False if db_result[3] == True else True
    db_result = db.capframe.capframe_config_status(cf_id, status)
    if not db_result:
        flash('Failed to update CapFrame status', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    flash('CapFrame status updated successfully', 'success')
    return redirect(url_for('router.admin.config.capframe.index'))

@bp.route('/config_desc', methods=['POST'])
def config_desc():
    cf_id = request.form.get('cf_id')
    config_desc = request.form.get('config_desc')
    
    if not cf_id or not config_desc:
        flash('Requirement parameter missing', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    db_result = db.capframe.capframe_get(cf_id)
    if not db_result:
        flash('CapFrame not found', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    db_result = db.capframe.capframe_config_desc(cf_id, config_desc)
    if not db_result:
        flash('Failed to update CapFrame description', 'error')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    flash('CapFrame description updated successfully', 'success')
    return redirect(url_for('router.admin.config.capframe.index'))

@bp.route('/create/<int:f_id>', methods=['GET', 'POST'])
def create_frame_selected(f_id):
    if not f_id:
        flash('Frame ID is required', 'error')
        return redirect(url_for('router.admin.config.capframe.create'))
    
    frame_result = db.frame.frame_get(f_id)
    if not frame_result:
        flash('Frame not found. Select again', 'error')
        return redirect(url_for('router.admin.config.capframe.create'))
    
    frame_meta = json.loads(frame_result[3])
    frame_capture_count = len(frame_meta['captures'])
    
    if request.method == "POST":
        selected_captures = []
        for i in range(frame_capture_count):
            value = request.form.get(f'c_id-{i}')
            
            capture_result = db.capture.capture_get(value)
            if not value or not value.strip() or not capture_result:
                flash('Capture ID Error. Select again', 'error')
                return redirect(url_for('router.admin.config.capframe.create_frame_selected', f_id=f_id))
            
            selected_captures.append(capture_result)

        # * create capframe
        start_time = time.time()
        
        CAPFRAME_ID = utils.gen_hash()
        
        CANVAS_SIZE = frame_meta['canvas']['size']
        TIME_LOCA = frame_meta['canvas']['time_loca']
        TIME_FONT_SIZE = frame_meta['canvas']['time_font_size']
        TIME_FONT_COLOR = frame_meta['canvas']['time_font_color']
        QR_LOCA = frame_meta['canvas']['qr_loca']
        QR_SIZE = frame_meta['canvas']['qr_size']
        capframe = Image.new("RGBA", CANVAS_SIZE, (255, 255, 255, 0))
        capframe_draw = ImageDraw.Draw(capframe)
        
        # draw capture
        for index, capture in enumerate(frame_meta['captures']):
            capture_info = selected_captures[index]
            
            CAPTURE_PATH = os.path.join(db.CAPTURES_PATH, capture_info[3])
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
        FRAME_PATH = os.path.join(db.FRAMES_PATH, frame_result[2])
        frame = Image.open(FRAME_PATH).convert("RGBA")
        frame = frame.resize(CANVAS_SIZE)
        capframe.paste(frame, (0, 0), frame)

        # draw qr
        QR_PATH = os.path.join(db.QR_PATH, f'{CAPFRAME_ID}.png')
        utils.gen_qr(
            save_path=QR_PATH,
            url_path=url_for('router.view.view_capframe.send_capframe', cf_id=CAPFRAME_ID)
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
        
        SAVE_NAME = f"{utils.gen_hash()}.png"
        SAVE_PATH = os.path.join(db.CAPFRAMES_PATH, SAVE_NAME)
        capframe.save(SAVE_PATH)

        end_time = time.time()
        processing_time = round(float(end_time - start_time), 4)
        
        db.capframe.capframe_create(
            cf_id=CAPFRAME_ID,
            d_id=None,
            f_id=f_id,
            file_name=SAVE_NAME,
            processing_time=processing_time
        )
        
        # capframe info insert
        for index, capture in enumerate(frame_meta['captures']):
            capture_info = selected_captures[index]
            db.capframe_info.capframe_info_add(
                cf_id=CAPFRAME_ID,
                c_id=capture_info[0],
                c_no=index
            )
        
        flash('CapFrame created successfully', 'success')
        return redirect(url_for('router.admin.config.capframe.index'))
    
    return render_template('admin/config/capframe_create.html', user_ip=utils.get_ip(), captures=db.capture.capture_get_list(), frame=frame_result, capture_len=frame_capture_count, capframes=db.capframe.capframe_get_list())

