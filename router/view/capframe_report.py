from flask import Blueprint, request, jsonify
import db.report
import src.utils as utils

bp = Blueprint('view_report', __name__, url_prefix='/report')

@bp.route('/<cf_id>', methods=['POST'])
def create_report(cf_id):
    try:
        reason = request.form.get('reason', '').strip()
        
        if not reason:
            return jsonify({'success': False, 'message': '사유를 입력해주세요.'}), 400
        
        if len(reason) > 500:
            return jsonify({'success': False, 'message': '사유는 500자 이내로 입력해주세요.'}), 400
        
        if db.report.report_pending_exists_for_cf_id(cf_id):
            return jsonify({'success': False, 'message': '이미 요청이 접수된 콘텐츠입니다.'}), 409
        
        reporter_ip = utils.get_ip()
        
        if db.report.report_create(cf_id, reason, reporter_ip):
            return jsonify({'success': True, 'message': '요청이 접수되었습니다.'}), 200
        else:
            return jsonify({'success': False, 'message': '처리 중 오류가 발생했습니다.'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': '처리 중 오류가 발생했습니다.'}), 500
