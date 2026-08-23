from flask import Blueprint, request, jsonify
from backend.services.auth_service import AuthService
from backend.utils.auth_decorators import admin_required

auth_bp = Blueprint('auth_routes', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '')
    password = data.get('password', '')

    success, message, user_data = AuthService.login(email, password)
    if not success:
        return jsonify({'success': False, 'error': message}), 401

    return jsonify({
        'success': True,
        'message': message,
        'user': user_data
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    AuthService.logout()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@auth_bp.route('/me', methods=['GET'])
def get_me():
    user = AuthService.get_current_user()
    if not user:
        return jsonify({'success': False, 'authenticated': False}), 401
    return jsonify({
        'success': True,
        'authenticated': True,
        'user': user.to_dict()
    })

@auth_bp.route('/change-password', methods=['POST'])
@admin_required
def change_password():
    data = request.get_json(silent=True) or {}
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    success, message = AuthService.change_password(current_password, new_password)
    if not success:
        return jsonify({'success': False, 'error': message}), 400

    return jsonify({'success': True, 'message': message})
