from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, session, abort, redirect
from backend.services.portfolio_service import PortfolioService
from backend.services.analytics_service import AnalyticsService
from backend.utils.validators import validate_contact_message
from backend.config import Config

public_bp = Blueprint('public_routes', __name__)

@public_bp.route('/portfolio', methods=['GET'])
def get_public_portfolio():
    # Record anonymized page visit
    AnalyticsService.record_visit(page="/")

    data = PortfolioService.get_public_portfolio_data()
    settings = data.get('settings', {})
    
    # Check if maintenance mode is enabled and user is not an authenticated admin
    is_admin = bool(session.get('admin_id'))
    if settings.get('maintenance_mode') and not is_admin:
        return jsonify({
            'success': True,
            'maintenance_mode': True,
            'maintenance_message': settings.get('maintenance_message', 'Site under maintenance.'),
            'settings': settings
        })

    return jsonify({
        'success': True,
        'maintenance_mode': False,
        'data': data
    })

@public_bp.route('/contact', methods=['POST'])
def submit_contact():
    data = request.get_json(silent=True) or {}
    is_valid, error_msg = validate_contact_message(data)
    if not is_valid:
        return jsonify({'success': False, 'error': error_msg}), 400

    msg = PortfolioService.submit_contact_message(
        name=data['name'],
        email=data['email'],
        subject=data['subject'],
        message=data['message']
    )
    return jsonify({
        'success': True,
        'message': 'Thank you! Your message has been received securely.',
        'data': msg
    })

@public_bp.route('/resume/download', methods=['GET'])
def download_resume():
    resume = PortfolioService.get_active_resume()
    if not resume:
        response = jsonify({'success': False, 'error': 'No resume currently uploaded'})
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response, 404

    # If resume is stored on Cloudinary (or remote secure URL)
    if resume.filename.startswith("http://") or resume.filename.startswith("https://"):
        return redirect(resume.filename)

    # Resolve local file path
    file_rel = resume.filename.lstrip('/')
    file_path = Config.BASE_DIR / file_rel

    if not file_path.exists() or not file_path.is_file():
        # Clean up stale DB record if physical file is missing
        PortfolioService.delete_resume(resume.id)
        response = jsonify({'success': False, 'error': 'Resume file not found on server'})
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response, 404

    response = send_file(
        str(file_path),
        as_attachment=True,
        download_name=resume.original_filename or "Resume.pdf",
        mimetype='application/pdf'
    )
    # Prevent browser caching of downloaded file
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@public_bp.route('/view-project/<int:project_id>', methods=['POST'])
def record_project_view(project_id: int):
    new_views = PortfolioService.record_project_view(project_id)
    return jsonify({'success': True, 'views': new_views})
