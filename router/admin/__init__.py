from flask import Blueprint, redirect, request, session, url_for
import src.utils as utils

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'your_password':
            session['authenticated'] = True
            return redirect(url_for('admin.index'))
        else:
            return redirect(url_for('admin.index'))

    return '''
        <form method="post">
            Password: <input type="password" name="password">
            <input type="submit" value="Go">
        </form>
    '''