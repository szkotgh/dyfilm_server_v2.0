import os
from datetime import timedelta
from flask import Flask, render_template, send_file, request
from werkzeug.middleware.proxy_fix import ProxyFix
import src.utils as utils
import router

app = Flask(__name__)

# 신뢰하는 역방향 프록시(로컬 nginx) 1홉의 X-Forwarded-* 만 신뢰한다.
# 이렇게 하면 remote_addr가 프록시가 설정한 값(위조 불가)이 되며, 클라이언트가
# 임의로 보낼 수 있는 헤더를 IP로 신뢰하지 않게 된다. 프록시 체인이 더 깊고
# 실제 클라이언트 IP가 필요하면 x_for 값을 체인 깊이에 맞게 늘린다.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

app.secret_key = utils.get_env('SESSION_SECRET_KEY')

app.config['SESSION_COOKIE_NAME'] = 'SESSION'
app.config['SESSION_COOKIE_PATH'] = '/'
app.config['SESSION_COOKIE_DOMAIN'] = None
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_SECURE'] = True
# SESSION_COOKIE_MAX_AGE는 Flask 설정 키가 아니어서 무효였음. 실제 쿠키 수명은
# PERMANENT_SESSION_LIFETIME(절대 세션 상한)으로 지정하고 로그인 시 session.permanent=True로 표시.
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=int(os.environ.get('ADMIN_SESSION_ABSOLUTE_TIMEOUT', '28800')))

# 업로드/요청 본문 크기 상한(32MB) — 무제한 본문으로 인한 메모리/디스크 고갈 DoS 방지.
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

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
    app.run(host=utils.get_env("HOST_IP"), port=int(utils.get_env("HOST_PORT")))

