from flask import Flask, render_template, send_file, request
import src.utils as utils
import db
import router
from flask_wtf.csrf import CSRFError

app = Flask(__name__)

app.secret_key = utils.get_env('SESSION_SECRET_KEY')
app.config['SECRET_KEY'] = utils.get_env('CSRF_SECRET_KEY')

app.register_blueprint(router.bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/robots.txt')
def robots():
    return send_file('static/robots.txt')

@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')

@app.route('/codes')
def codes():
    return send_file('static/code.json')

@app.errorhandler(404)
def handle_exception_404(e):
    return utils.get_code('not_found')

@app.errorhandler(405)
def handle_exception_405(e):
    return utils.get_code('method_not_allowed')

@app.errorhandler(CSRFError)
def handle_exception_csrf(e):
    return utils.get_code('csrf_invalid')

# @app.errorhandler(Exception)
# def handle_exception(e):
#     return utils.get_code('unknown_error')

if __name__ == '__main__':
    app.run(host=utils.get_env("HOST_IP"), port=utils.get_env("HOST_PORT"))
