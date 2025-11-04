from flask import Flask, render_template, send_file, request
import src.utils as utils
import router

app = Flask(__name__)

app.secret_key = utils.get_env('SESSION_SECRET_KEY')

app.config['SESSION_COOKIE_NAME'] = 'SESSION'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_DOMAIN'] = None
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_MAX_AGE'] = 3600
app.config['SESSION_COOKIE_SECURE'] = True

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "font-src 'self' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    return response

app.register_blueprint(router.bp)

@app.route('/')
def index():
    return render_template('index.html', admin_email=utils.get_env('ADMIN_EMAIL'))

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


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {e}", exc_info=True)
    return utils.get_code('unknown_error')

if __name__ == '__main__':
    app.run(host=utils.get_env("HOST_IP"), port=int(utils.get_env("HOST_PORT")), debug=True)

