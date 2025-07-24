from app import create_app
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash
from config import Config

def create_admin_user():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(is_admin=True).first()
        if admin:
            print(f"Admin user already exists: {admin.email}")
            return admin
        
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
        
        print(f"Admin user created successfully!")
        print(f"Email: {Config.ADMIN_EMAIL}")
        print(f"Password: {Config.ADMIN_PASSWORD}")
        
        return admin_user

if __name__ == '__main__':
    create_admin_user() 