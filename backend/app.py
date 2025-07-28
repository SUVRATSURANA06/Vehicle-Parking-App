from flask import Flask, jsonify
from flask_cors import CORS
from extensions import db, login_manager, redis_client, celery, mail
from routes.auth_routes import auth_bp
from routes.main_routes import main_bp
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp
from models.user import User
from config import Config
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    celery.conf.update(app.config)
    
    # Enable CORS for Vue.js frontend
    CORS(app, origins=['http://localhost:5173', 'http://localhost:3000'], supports_credentials=True)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden', 'message': 'Access denied'}), 403
    
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'database': 'connected' if db.engine.pool.checkedin() > 0 else 'disconnected',
            'redis': 'connected' if redis_client and redis_client.ping() else 'disconnected'
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        db.create_all()
        
        # Ensure admin user exists
        from create_admin import create_admin_user
        create_admin_user()
    
        from init_db import init_db
        init_db()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

