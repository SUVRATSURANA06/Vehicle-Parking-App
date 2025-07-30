from flask import Blueprint, jsonify
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """API endpoint for app info"""
    return jsonify({
        'app_name': 'Vehicle Parking App',
        'version': '2.0.0',
        'description': 'Smart parking solutions for modern cities'
    })

@main_bp.route('/api/info')
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'Vehicle Parking App API',
        'version': '2.0.0',
        'endpoints': {
            'auth': '/login, /register, /logout',
            'user': '/user/*',
            'admin': '/admin/*'
        }
    })
