from flask import Blueprint, request, jsonify, send_file
from backend.services.portfolio_service import PortfolioService
from backend.services.upload_service import UploadService
from backend.services.analytics_service import AnalyticsService
from backend.utils.auth_decorators import admin_required
import io
import json

admin_bp = Blueprint('admin_routes', __name__)

# All routes in this blueprint require admin authentication
@admin_bp.before_request
@admin_required
def require_admin_auth():
    pass

# Dashboard & Analytics
@admin_bp.route('/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    stats = PortfolioService.get_admin_dashboard_stats()
    analytics = AnalyticsService.get_analytics_summary()
    stats['analytics'] = analytics
    return jsonify({'success': True, 'data': stats})

# Profile Management
@admin_bp.route('/profile', methods=['GET'])
def get_profile():
    profile = PortfolioService.get_public_portfolio_data()['profile']
    return jsonify({'success': True, 'data': profile})

@admin_bp.route('/profile', methods=['PUT'])
def update_profile():
    data = request.get_json(silent=True) or {}
    updated = PortfolioService.update_profile(data)
    return jsonify({'success': True, 'message': 'Profile updated successfully', 'data': updated})

@admin_bp.route('/profile/upload-image', methods=['POST'])
def upload_profile_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file provided'}), 400

    file = request.files['image']

    # Retrieve current profile image before updating
    current_profile = PortfolioService.get_public_portfolio_data().get('profile', {})
    old_image_url = current_profile.get('profile_image')

    success, result = UploadService.save_profile_image(file)
    if not success:
        return jsonify({'success': False, 'error': result}), 400

    PortfolioService.update_profile({'profile_image': result})

    # Only after successful replacement, delete old Cloudinary asset if it was a Cloudinary asset
    if old_image_url and old_image_url != result:
        UploadService.delete_cloudinary_asset(old_image_url)

    return jsonify({'success': True, 'message': 'Profile picture updated', 'image_url': result})

# Skills Management
@admin_bp.route('/skills', methods=['GET'])
def get_skills():
    skills = PortfolioService.get_all_skills()
    return jsonify({'success': True, 'data': skills})

@admin_bp.route('/skills', methods=['POST'])
def add_skill():
    data = request.get_json(silent=True) or {}
    if not data.get('name'):
        return jsonify({'success': False, 'error': 'Skill name is required'}), 400
    skill = PortfolioService.add_skill(data)
    return jsonify({'success': True, 'message': 'Skill created', 'data': skill})

@admin_bp.route('/skills/<int:skill_id>', methods=['PUT'])
def update_skill(skill_id: int):
    data = request.get_json(silent=True) or {}
    updated = PortfolioService.update_skill(skill_id, data)
    if not updated:
        return jsonify({'success': False, 'error': 'Skill not found'}), 404
    return jsonify({'success': True, 'message': 'Skill updated', 'data': updated})

@admin_bp.route('/skills/<int:skill_id>', methods=['DELETE'])
def delete_skill(skill_id: int):
    if not PortfolioService.delete_skill(skill_id):
        return jsonify({'success': False, 'error': 'Skill not found'}), 404
    return jsonify({'success': True, 'message': 'Skill deleted'})

@admin_bp.route('/skills/reorder', methods=['POST'])
def reorder_skills():
    data = request.get_json(silent=True) or {}
    ordered_ids = data.get('ordered_ids', [])
    PortfolioService.reorder_skills(ordered_ids)
    return jsonify({'success': True, 'message': 'Skills order updated'})

# Projects Management
@admin_bp.route('/projects', methods=['GET'])
def get_projects():
    projects = PortfolioService.get_all_projects_admin()
    return jsonify({'success': True, 'data': projects})

@admin_bp.route('/projects', methods=['POST'])
def add_project():
    data = request.get_json(silent=True) or {}
    if not data.get('title') or not data.get('short_description'):
        return jsonify({'success': False, 'error': 'Title and short description are required'}), 400
    proj = PortfolioService.add_project(data)
    return jsonify({'success': True, 'message': 'Project created', 'data': proj})

@admin_bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id: int):
    data = request.get_json(silent=True) or {}
    updated = PortfolioService.update_project(project_id, data)
    if not updated:
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    return jsonify({'success': True, 'message': 'Project updated', 'data': updated})

@admin_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id: int):
    if not PortfolioService.delete_project(project_id):
        return jsonify({'success': False, 'error': 'Project not found'}), 404
    return jsonify({'success': True, 'message': 'Project deleted'})

@admin_bp.route('/projects/reorder', methods=['POST'])
def reorder_projects():
    data = request.get_json(silent=True) or {}
    ordered_ids = data.get('ordered_ids', [])
    PortfolioService.reorder_projects(ordered_ids)
    return jsonify({'success': True, 'message': 'Projects order updated'})

@admin_bp.route('/projects/upload-image', methods=['POST'])
def upload_project_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file provided'}), 400
    file = request.files['image']
    success, result = UploadService.save_project_image(file)
    if not success:
        return jsonify({'success': False, 'error': result}), 400
    return jsonify({'success': True, 'message': 'Project image uploaded', 'image_url': result})

# Education Management
@admin_bp.route('/education', methods=['GET'])
def get_education():
    edu_list = PortfolioService.get_all_education_admin()
    return jsonify({'success': True, 'data': edu_list})

@admin_bp.route('/education', methods=['POST'])
def add_education():
    data = request.get_json(silent=True) or {}
    if not data.get('degree') or not data.get('institution'):
        return jsonify({'success': False, 'error': 'Degree and institution are required'}), 400
    edu = PortfolioService.add_education(data)
    return jsonify({'success': True, 'message': 'Education record added', 'data': edu})

@admin_bp.route('/education/<int:edu_id>', methods=['PUT'])
def update_education(edu_id: int):
    data = request.get_json(silent=True) or {}
    updated = PortfolioService.update_education(edu_id, data)
    if not updated:
        return jsonify({'success': False, 'error': 'Education record not found'}), 404
    return jsonify({'success': True, 'message': 'Education updated', 'data': updated})

@admin_bp.route('/education/<int:edu_id>', methods=['DELETE'])
def delete_education(edu_id: int):
    if not PortfolioService.delete_education(edu_id):
        return jsonify({'success': False, 'error': 'Education record not found'}), 404
    return jsonify({'success': True, 'message': 'Education deleted'})

@admin_bp.route('/education/reorder', methods=['POST'])
def reorder_education():
    data = request.get_json(silent=True) or {}
    ordered_ids = data.get('ordered_ids', [])
    PortfolioService.reorder_education(ordered_ids)
    return jsonify({'success': True, 'message': 'Education order updated'})

# Social Links Management
@admin_bp.route('/socials', methods=['GET'])
def get_socials():
    socials = PortfolioService.get_all_socials()
    return jsonify({'success': True, 'data': socials})

@admin_bp.route('/socials', methods=['POST'])
def add_social():
    data = request.get_json(silent=True) or {}
    if not data.get('name') or not data.get('url'):
        return jsonify({'success': False, 'error': 'Name and URL are required'}), 400
    social = PortfolioService.add_social(data)
    return jsonify({'success': True, 'message': 'Social link added', 'data': social})

@admin_bp.route('/socials/<int:social_id>', methods=['PUT'])
def update_social(social_id: int):
    data = request.get_json(silent=True) or {}
    updated = PortfolioService.update_social(social_id, data)
    if not updated:
        return jsonify({'success': False, 'error': 'Social link not found'}), 404
    return jsonify({'success': True, 'message': 'Social link updated', 'data': updated})

@admin_bp.route('/socials/<int:social_id>', methods=['DELETE'])
def delete_social(social_id: int):
    if not PortfolioService.delete_social(social_id):
        return jsonify({'success': False, 'error': 'Social link not found'}), 404
    return jsonify({'success': True, 'message': 'Social link deleted'})

# Resume Management
@admin_bp.route('/resume', methods=['GET'])
def get_resume():
    resume = PortfolioService.get_active_resume()
    return jsonify({'success': True, 'data': resume.to_dict() if resume else None})

@admin_bp.route('/resume/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'success': False, 'error': 'No resume PDF file uploaded'}), 400
    file = request.files['resume']
    success, rel_url, original_name, file_size = UploadService.save_resume_pdf(file)
    if not success:
        return jsonify({'success': False, 'error': rel_url}), 400

    resume = PortfolioService.set_active_resume(rel_url, original_name, file_size)
    return jsonify({'success': True, 'message': 'Resume uploaded and activated', 'data': resume})

@admin_bp.route('/resume/<int:resume_id>', methods=['DELETE'])
def delete_resume(resume_id: int):
    success, msg = PortfolioService.delete_resume(resume_id)
    if not success:
        return jsonify({'success': False, 'error': msg}), 500
    return jsonify({'success': True, 'message': msg})

@admin_bp.route('/resume', methods=['DELETE'])
def delete_active_resume():
    success, msg = PortfolioService.delete_active_resume()
    if not success:
        return jsonify({'success': False, 'error': msg}), 500
    return jsonify({'success': True, 'message': msg})

# Messages Inbox
@admin_bp.route('/messages', methods=['GET'])
def get_messages():
    messages = PortfolioService.get_all_messages()
    return jsonify({'success': True, 'data': messages})

@admin_bp.route('/messages/<int:msg_id>/read', methods=['PUT'])
def mark_message_read(msg_id: int):
    data = request.get_json(silent=True) or {}
    is_read = bool(data.get('is_read', True))
    updated = PortfolioService.mark_message_read(msg_id, is_read)
    if not updated:
        return jsonify({'success': False, 'error': 'Message not found'}), 404
    return jsonify({'success': True, 'data': updated})

@admin_bp.route('/messages/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id: int):
    if not PortfolioService.delete_message(msg_id):
        return jsonify({'success': False, 'error': 'Message not found'}), 404
    return jsonify({'success': True, 'message': 'Message deleted'})

# Settings & SEO
@admin_bp.route('/settings', methods=['GET'])
def get_settings():
    settings = PortfolioService.get_settings()
    return jsonify({'success': True, 'data': settings})

@admin_bp.route('/settings', methods=['PUT'])
def update_settings():
    data = request.get_json(silent=True) or {}
    updated = PortfolioService.update_settings(data)
    return jsonify({'success': True, 'message': 'Settings saved', 'data': updated})

# Backup & Restore
@admin_bp.route('/backup/export', methods=['GET'])
def export_backup():
    backup_data = PortfolioService.export_full_backup()
    mem_file = io.BytesIO()
    mem_file.write(json.dumps(backup_data, indent=2).encode('utf-8'))
    mem_file.seek(0)
    return send_file(
        mem_file,
        as_attachment=True,
        download_name=f"portfolio_backup_{backup_data['exported_at'][:10]}.json",
        mimetype='application/json'
    )

@admin_bp.route('/backup/restore', methods=['POST'])
def restore_backup():
    if 'backup_file' not in request.files:
        return jsonify({'success': False, 'error': 'No backup JSON file provided'}), 400
    file = request.files['backup_file']
    try:
        content = json.load(file)
    except Exception as e:
        return jsonify({'success': False, 'error': f'Invalid JSON file: {str(e)}'}), 400

    success, message = PortfolioService.restore_from_backup(content)
    if not success:
        return jsonify({'success': False, 'error': message}), 400

    return jsonify({'success': True, 'message': message})
