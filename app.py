from flask import Flask, render_template, send_file, redirect
import src.utils as utils
import db
import router

app = Flask(__name__)
app.register_blueprint(router.bp)

@app.route('/', strict_slashes=False)
def index():
    return render_template('index.html')

@app.route('/robots.txt')
def robots():
    return send_file('static/robots.txt')

@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')

@app.errorhandler(404)
def handle_exception_404(e):
    return utils.get_code('not_found')

@app.errorhandler(Exception)
def handle_exception(e):
    return utils.get_code('unknown_error')

if __name__ == '__main__':
    app.run(host=utils.get_env("HOST_IP"), port=utils.get_env("HOST_PORT"))
