from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import db.report
import auth
import src.utils as utils

bp = Blueprint('report_manage', __name__, url_prefix='/report')

@bp.route('', methods=['GET'])
@auth.admin_required
def report_list():
    reports = db.report.report_get_all()
    pending_count = db.report.report_get_pending_count()
    
    return render_template('admin/report/list.html', 
                         reports=reports, 
                         pending_count=pending_count,
                         user_ip=utils.get_ip())

@bp.route('/ajax/list', methods=['GET'])
@auth.admin_required
def report_list_ajax():
    """AJAX용 신고 목록을 반환합니다."""
    try:
        limit = int(request.args.get('limit', 30))
        offset = int(request.args.get('offset', 0))
        
        reports = db.report.report_get_list_paginated(limit, offset)
        
        # 데이터를 JSON 형식으로 변환
        items = []
        for report in reports:
            items.append({
                'report_id': report['report_id'],
                'cf_id': report['cf_id'],
                'reason': report['reason'],
                'admin_review_time': report['admin_review_time'],
                'is_approved': report['is_approved'],
                'reporter_ip': report['reporter_ip'],
                'report_time': report['report_time'],
                'file_name': report['file_name'],
                'capframe_create_time': report['capframe_create_time']
            })
        
        return jsonify({'items': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/ajax/count', methods=['GET'])
@auth.admin_required
def report_count_ajax():
    """전체 신고 개수를 반환합니다."""
    try:
        count = db.report.report_count()
        return jsonify({'total': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:report_id>/approve', methods=['POST'])
@auth.admin_required
def approve_report(report_id):
    try:
        if db.report.report_approve(report_id):
            flash(f'접수되었습니다. (ID: {report_id})', 'success')
        else:
            flash(f'처리할 수 없습니다. (ID: {report_id})', 'error')
    except Exception as e:
        flash(f'오류가 발생했습니다: {e}', 'error')
    
    return redirect(url_for('router.admin.report_manage.report_list'))

@bp.route('/<int:report_id>/reject', methods=['POST'])
@auth.admin_required
def reject_report(report_id):
    try:
        if db.report.report_reject(report_id):
            flash(f'반려되었습니다. (ID: {report_id})', 'success')
        else:
            flash(f'처리할 수 없습니다. (ID: {report_id})', 'error')
    except Exception as e:
        flash(f'오류가 발생했습니다: {e}', 'error')
    
    return redirect(url_for('router.admin.report_manage.report_list'))
