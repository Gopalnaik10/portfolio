import os
from pathlib import Path
from flask import Blueprint, send_from_directory, redirect, session, request
from backend.config import Config
from backend.utils.auth_decorators import admin_required

page_bp = Blueprint('page_routes', __name__)

BASE_DIR = Config.BASE_DIR

# ---------------- Public Portfolio ----------------
@page_bp.route('/', methods=['GET'])
def index():
    return send_from_directory(str(BASE_DIR / 'frontend'), 'index.html')

# Static files for Frontend
@page_bp.route('/css/<path:filename>', methods=['GET'])
def frontend_css(filename):
    return send_from_directory(str(BASE_DIR / 'frontend' / 'css'), filename)

@page_bp.route('/js/<path:filename>', methods=['GET'])
def frontend_js(filename):
    return send_from_directory(str(BASE_DIR / 'frontend' / 'js'), filename)

@page_bp.route('/assets/<path:filename>', methods=['GET'])
def frontend_assets(filename):
    return send_from_directory(str(BASE_DIR / 'frontend' / 'assets'), filename)

# ---------------- Uploaded Files ----------------
@page_bp.route('/uploads/<path:filename>', methods=['GET'])
def uploaded_file(filename):
    file_path = Config.UPLOAD_FOLDER / filename
    if file_path.is_file():
        return send_from_directory(str(Config.UPLOAD_FOLDER), filename)
    
    # Fallback to bundled frontend assets for default images if not yet in persistent upload folder
    asset_name = Path(filename).name
    bundled_asset = BASE_DIR / 'frontend' / 'assets' / asset_name
    if bundled_asset.is_file():
        return send_from_directory(str(BASE_DIR / 'frontend' / 'assets'), asset_name)

    return send_from_directory(str(Config.UPLOAD_FOLDER), filename)

# ---------------- Admin Interface ----------------
@page_bp.route('/admin', methods=['GET'])
@page_bp.route('/admin/', methods=['GET'])
def admin_root():
    if session.get('admin_id'):
        return redirect('/admin/dashboard')
    return redirect('/admin/login')

@page_bp.route('/admin/login', methods=['GET'])
def admin_login():
    if session.get('admin_id'):
        return redirect('/admin/dashboard')
    return send_from_directory(str(BASE_DIR / 'admin'), 'login.html')

@page_bp.route('/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    return send_from_directory(str(BASE_DIR / 'admin'), 'dashboard.html')

# Static files for Admin CMS
@page_bp.route('/admin/css/<path:filename>', methods=['GET'])
def admin_css(filename):
    return send_from_directory(str(BASE_DIR / 'admin' / 'css'), filename)

@page_bp.route('/admin/js/<path:filename>', methods=['GET'])
def admin_js(filename):
    return send_from_directory(str(BASE_DIR / 'admin' / 'js'), filename)
