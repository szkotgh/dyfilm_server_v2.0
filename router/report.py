from flask import Blueprint, request, jsonify, flash, redirect, url_for
import db.report
import src.utils as utils
from flask_wtf.csrf import generate_csrf

bp = Blueprint('report', __name__, url_prefix='/report')

@bp.route('/<cf_id>', methods=['POST'])
def create_report(cf_id):
    """신고를 생성합니다."""
    try:
        reason = request.form.get('reason', '').strip()
        
        if not reason:
            return jsonify({'success': False, 'message': '신고 사유를 입력해주세요.'}), 400
        
        if len(reason) > 500:
            return jsonify({'success': False, 'message': '신고 사유는 500자 이내로 입력해주세요.'}), 400
        
        # 이미 신고가 접수된 cf_id인지 확인
        if db.report.report_exists_for_cf_id(cf_id):
            return jsonify({'success': False, 'message': '이미 신고가 접수된 콘텐츠입니다.'}), 409
        
        reporter_ip = utils.get_ip()
        
        # 신고 생성
        if db.report.report_create(cf_id, reason, reporter_ip):
            return jsonify({'success': True, 'message': '신고가 접수되었습니다.'}), 200
        else:
            return jsonify({'success': False, 'message': '신고 접수 중 오류가 발생했습니다.'}), 500
            
    except Exception as e:
        print(f"Error in create_report: {e}")
        return jsonify({'success': False, 'message': '신고 접수 중 오류가 발생했습니다.'}), 500
