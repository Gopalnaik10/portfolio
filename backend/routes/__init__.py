from flask import Flask

def register_blueprints(app: Flask):
    from .page_routes import page_bp
    from .auth_routes import auth_bp
    from .public_routes import public_bp
    from .admin_routes import admin_bp

    app.register_blueprint(page_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(public_bp, url_prefix='/api/public')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
