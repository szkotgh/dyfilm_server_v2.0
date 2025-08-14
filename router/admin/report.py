from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import db.report
import auth
import src.utils as utils

bp = Blueprint('admin_report', __name__, url_prefix='/report')

@bp.route('', methods=['GET'])
@auth.admin_required
def report_list():
    """신고 목록을 보여줍니다."""
    reports = db.report.report_get_all()
    pending_count = db.report.report_get_pending_count()
    
    return render_template('admin/report/list.html', 
                         reports=reports, 
                         pending_count=pending_count,
                         user_ip=utils.get_ip())

@bp.route('/<int:report_id>/approve', methods=['POST'])
@auth.admin_required
def approve_report(report_id):
    """신고를 승인합니다."""
    try:
        if db.report.report_approve(report_id):
            flash('신고가 승인되었습니다.', 'success')
        else:
            flash('신고 승인 중 오류가 발생했습니다.', 'error')
    except Exception as e:
        print(f"Error approving report: {e}")
        flash('신고 승인 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('router.admin.admin_report.report_list'))

@bp.route('/<int:report_id>/reject', methods=['POST'])
@auth.admin_required
def reject_report(report_id):
    """신고를 반려합니다."""
    try:
        if db.report.report_reject(report_id):
            flash('신고가 반려되었습니다.', 'success')
        else:
            flash('신고 반려 중 오류가 발생했습니다.', 'error')
    except Exception as e:
        print(f"Error rejecting report: {e}")
        flash('신고 반려 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('router.admin.admin_report.report_list'))
