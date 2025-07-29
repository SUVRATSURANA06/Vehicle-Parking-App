from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
from extensions import db, redis_client
from models.user import User
from datetime import datetime
from config import Config
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        # user already exists
        existing_user = User.query.filter(
            (User.email == data['email']) | (User.username == data['username'])
        ).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'User already exists'})
        # new user
        hashed_password = generate_password_hash(data['password'])
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=hashed_password,
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            pin_code=data.get('pin_code', ''),
            is_admin=False
        )
        db.session.add(new_user)
        db.session.commit()
        # Clear cached user data
        if redis_client:
            redis_client.delete("admin_stats")
        return jsonify({'success': True, 'message': 'Registration successful! Please login.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password) and user.is_active:
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return jsonify({
                'success': True, 
                'message': 'Login successful',
                'user': user.to_dict(),
                'is_admin': user.is_admin
            })
        else:
            message = 'Invalid email or password'
            if user and not user.is_active:
                message = 'Account is deactivated. Please contact administrator.'
            return jsonify({'success': False, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@auth_bp.route('/logout')
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@auth_bp.route('/create-admin', methods=['POST'])
def create_admin():
    """Create the default admin user (only accessible once)"""
    try:
        # Check if admin already exists
        admin = User.query.filter_by(is_admin=True).first()
        if admin:
            return jsonify({'success': False, 'message': 'Admin user already exists'})
        # Create admin user
        hashed_password = generate_password_hash(Config.ADMIN_PASSWORD)
        admin_user = User(
            username=Config.ADMIN_USERNAME,
            email=Config.ADMIN_EMAIL,
            password=hashed_password,
            first_name='Admin',
            last_name='User',
            is_admin=True,
            is_active=True
        )
        db.session.add(admin_user)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Admin user created successfully',
            'credentials': {
                'username': Config.ADMIN_USERNAME,
                'email': Config.ADMIN_EMAIL,
                'password': Config.ADMIN_PASSWORD
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@auth_bp.route('/check-auth')
def check_auth():
    """Check if user is authenticated and return user info (session-based)"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict(),
            'is_admin': current_user.is_admin
        })
    else:
        return jsonify({'authenticated': False})
