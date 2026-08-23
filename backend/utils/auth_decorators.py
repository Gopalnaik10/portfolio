from functools import wraps
from flask import session, jsonify, request, redirect, url_for

def admin_required(f):
    """
    Decorator for API endpoints requiring admin session authentication.
    Returns 401 JSON for API requests or redirects to login for page visits.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_id = session.get('admin_id')
        if not admin_id:
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'Unauthorized: Admin session required'
                }), 401
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated_function
