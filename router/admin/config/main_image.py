import os
from flask import Blueprint, flash, redirect, render_template, request, send_file, session, url_for, jsonify
import src.utils as utils
import auth
import db.main_image
import db.device

bp = Blueprint('main_image', __name__, url_prefix='/main_image')

@bp.before_request
@auth.admin_required
def check_admin():
    pass

@bp.route('', methods=['GET', 'POST'])
def index():
    return render_template('admin/config/main_image.html', user_ip=utils.get_ip())

@bp.route('/list', methods=['GET'])
def get_list():
    try:
        limit = int(request.args.get('limit', '30'))
        offset = int(request.args.get('offset', '0'))
    except ValueError:
        limit = 30
        offset = 0
    rows = db.main_image.main_image_get_list_paginated(limit=limit, offset=offset)
    items = []
    for r in rows:
        device_ids = db.main_image.main_image_get_devices(r['mi_id'])
        items.append({
            'mi_id': r['mi_id'],
            'file_name': r['file_name'],
            'desc': r['desc'],
            'is_default': bool(r['is_default']),
            'device_ids': device_ids,
            'create': r['create'],
            'image_url': url_for('router.admin.config.main_image.get_image', mi_id=r['mi_id'])
        })
    return jsonify({ 'items': items })

@bp.route('/count', methods=['GET'])
def get_count():
    return jsonify({ 'total': db.main_image.main_image_count() })

@bp.route('/create', methods=['POST'])
def create():
    input_file = request.files.get('main_image_file')
    input_desc = request.form.get('desc')
    
    if not input_file or not input_file.filename:
        flash('파일을 선택해주세요', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    # 파일 확장자 확인
    extension = utils.get_extension(input_file.filename)
    if extension not in ['gif', 'png', 'jpg', 'jpeg']:
        flash('지원하지 않는 파일 형식입니다. gif, png, jpg, jpeg만 허용됩니다.', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    # 파일 저장
    file_name = f"{utils.gen_hash()}.{extension}"
    file_path = os.path.join(db.MAIN_IMAGE_DIR_PATH, file_name)
    
    try:
        input_file.save(file_path)
    except Exception as e:
        flash(f'파일 저장 실패: {str(e)}', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    # DB에 저장
    db_result = db.main_image.main_image_create(file_name, input_desc)
    
    if not db_result:
        # DB 저장 실패 시 파일 삭제
        try:
            os.remove(file_path)
        except:
            pass
        flash('데이터베이스 저장 실패', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    flash('Main Image가 성공적으로 생성되었습니다', 'success')
    return redirect(url_for('router.admin.config.main_image.index'))

@bp.route('/remove', methods=['POST'])
def remove():
    mi_id = request.form.get('mi_id')
    
    if not mi_id:
        flash('파라미터가 누락되었습니다', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    result = db.main_image.main_image_remove(int(mi_id))
    
    if result:
        flash('Main Image가 성공적으로 삭제되었습니다', 'success')
    else:
        flash('Main Image 삭제 실패', 'error')
    return redirect(url_for('router.admin.config.main_image.index'))

@bp.route('/config_desc', methods=['POST'])
def config_desc():
    mi_id = request.form.get('mi_id')
    input_desc = request.form.get('config_desc')
    
    if not mi_id:
        flash('파라미터가 누락되었습니다', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    result = db.main_image.main_image_config_desc(int(mi_id), input_desc)
    
    if result:
        flash('설명이 성공적으로 업데이트되었습니다', 'success')
    else:
        flash('설명 업데이트 실패', 'error')
    return redirect(url_for('router.admin.config.main_image.index'))

@bp.route('/config_image', methods=['POST'])
def config_image():
    mi_id = request.form.get('mi_id')
    config_image = request.files.get('config_image')
    
    if not mi_id or not config_image or not config_image.filename:
        flash('파라미터가 누락되었습니다', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    # 파일 확장자 확인
    extension = utils.get_extension(config_image.filename)
    if extension not in ['gif', 'png', 'jpg', 'jpeg']:
        flash('지원하지 않는 파일 형식입니다. gif, png, jpg, jpeg만 허용됩니다.', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    main_image_result = db.main_image.main_image_get(int(mi_id))
    if not main_image_result:
        flash('Main Image를 찾을 수 없습니다', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    old_file_name = main_image_result['file_name']
    old_file_path = os.path.join(db.MAIN_IMAGE_DIR_PATH, old_file_name)
    
    # 새 파일 이름 생성
    new_file_name = f"{utils.gen_hash()}.{extension}"
    new_file_path = os.path.join(db.MAIN_IMAGE_DIR_PATH, new_file_name)
    
    try:
        # 새 파일 저장
        config_image.save(new_file_path)
        
        # DB 업데이트
        db.main_image.main_image_config_file_name(int(mi_id), new_file_name)
        
        # 기존 파일 삭제
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
            except:
                pass
        
        flash('이미지가 성공적으로 업데이트되었습니다', 'success')
    except Exception as e:
        flash(f'이미지 업데이트 실패: {str(e)}', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    return redirect(url_for('router.admin.config.main_image.index'))

@bp.route('/config_is_default', methods=['POST'])
def config_is_default():
    mi_id = request.form.get('mi_id')
    
    if not mi_id:
        flash('파라미터가 누락되었습니다', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    result = db.main_image.main_image_set_default(int(mi_id))
    
    if result:
        flash('기본 이미지가 성공적으로 설정되었습니다', 'success')
    else:
        flash('기본 이미지 설정 실패', 'error')
    return redirect(url_for('router.admin.config.main_image.index'))

@bp.route('/unset_default', methods=['POST'])
def unset_default():
    """모든 기본 이미지를 해제합니다."""
    result = db.main_image.main_image_unset_default()
    
    if result:
        flash('기본 이미지가 성공적으로 해제되었습니다', 'success')
    else:
        flash('기본 이미지 해제 실패', 'error')
    return redirect(url_for('router.admin.config.main_image.index'))

@bp.route('/config_devices', methods=['POST'])
def config_devices():
    mi_id = request.form.get('mi_id')
    device_ids = request.form.getlist('device_ids')  # 여러 값 받기
    
    if not mi_id:
        flash('파라미터가 누락되었습니다', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    # 빈 문자열 제거 및 정수 변환
    device_ids_list = []
    for d_id in device_ids:
        if d_id and d_id.strip() and d_id != 'null':
            try:
                device_ids_list.append(int(d_id))
            except ValueError:
                pass
    
    result = db.main_image.main_image_set_devices(int(mi_id), device_ids_list)
    
    if result:
        flash('장치별 기본 이미지가 성공적으로 설정되었습니다', 'success')
    else:
        flash('장치별 기본 이미지 설정 실패', 'error')
    return redirect(url_for('router.admin.config.main_image.index'))

@bp.route('/get_image/<int:mi_id>', methods=['GET'])
def get_image(mi_id):
    main_image = db.main_image.main_image_get(mi_id)
    if not main_image:
        flash('이미지를 찾을 수 없습니다', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    main_image_path = os.path.join(db.MAIN_IMAGE_DIR_PATH, main_image['file_name'])
    
    if not os.path.exists(main_image_path):
        flash('파일을 찾을 수 없습니다', 'error')
        return redirect(url_for('router.admin.config.main_image.index'))
    
    # MIME 타입 결정
    extension = utils.get_extension(main_image['file_name'])
    mime_types = {
        'gif': 'image/gif',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg'
    }
    mimetype = mime_types.get(extension, 'image/jpeg')
    
    return send_file(main_image_path, mimetype=mimetype, max_age=0)

@bp.route('/device_list', methods=['GET'])
def device_list():
    """장치 목록을 반환합니다."""
    devices = db.device.device_get_list()
    items = []
    for d in devices:
        items.append({
            'd_id': d['d_id'],
            'desc': d['desc'],
            'status': bool(d['status'])
        })
    return jsonify({ 'items': items })
