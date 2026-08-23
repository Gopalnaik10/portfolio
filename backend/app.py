import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from flask import Flask, jsonify, request
from backend.config import Config
from backend.models import db
from backend.routes import register_blueprints
from database.init_db import init_database


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Auto-initialize database tables and seed if necessary
    init_database(app)

    # Register blueprints
    register_blueprints(app)

    # Production error handlers — never expose stack traces publicly
    @app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Bad request'}), 400
        return _error_page(400, 'Bad Request', 'The request could not be understood.'), 400

    @app.errorhandler(401)
    def unauthorized(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Unauthorized — please log in'}), 401
        from flask import redirect
        return redirect('/admin/login')

    @app.errorhandler(403)
    def forbidden(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Forbidden'}), 403
        return _error_page(403, 'Access Forbidden', 'You do not have permission to access this resource.'), 403

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Resource not found'}), 404
        return _error_page(404, 'Page Not Found', 'The page you are looking for does not exist.'), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'File too large — maximum upload size is 20MB'}), 413
        return _error_page(413, 'File Too Large', 'The uploaded file exceeds the maximum allowed size (20 MB).'), 413

    @app.errorhandler(500)
    def internal_error(e):
        # Roll back any broken DB transaction
        try:
            db.session.rollback()
        except Exception:
            pass
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'An internal server error occurred'}), 500
        return _error_page(500, 'Server Error', 'Something went wrong on our end. Please try again shortly.'), 500

    return app


def _error_page(code: int, title: str, message: str) -> str:
    """Generate a clean, minimal error page that doesn't expose internals."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{code} {title} | Gopal Naik</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
      background: #070B14;
      color: #F8FAFC;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
      text-align: center;
    }}
    .error-box {{ max-width: 500px; }}
    .error-code {{
      font-size: 6rem;
      font-weight: 900;
      line-height: 1;
      background: linear-gradient(135deg, #818CF8, #8B5CF6);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 1rem;
    }}
    h1 {{ font-size: 1.75rem; margin-bottom: 0.75rem; }}
    p {{ color: #94A3B8; line-height: 1.6; margin-bottom: 2rem; }}
    a {{
      display: inline-block;
      padding: 0.7rem 1.5rem;
      background: #4F46E5;
      color: #fff;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 600;
      transition: background 0.2s;
    }}
    a:hover {{ background: #4338CA; }}
  </style>
</head>
<body>
  <div class="error-box">
    <div class="error-code">{code}</div>
    <h1>{title}</h1>
    <p>{message}</p>
    <a href="/">&larr; Return to Portfolio</a>
  </div>
</body>
</html>"""


app = create_app()

if __name__ == '__main__':
    print(f"[SERVER] Portfolio CMS running at http://{Config.HOST}:{Config.PORT}")
    print(f"[AUTH]   Admin Login: http://{Config.HOST}:{Config.PORT}/admin/login")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, use_reloader=False)
