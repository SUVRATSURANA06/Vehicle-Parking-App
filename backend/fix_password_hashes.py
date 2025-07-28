from app import create_app
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash
from config import Config

def fix_password_hashes():
    app = create_app()
    with app.app_context():
        
        User.query.delete()
        db.session.commit()
        print("✅ Cleared all existing users")
        
        admin_user = User(
            username=Config.ADMIN_USERNAME,
            email=Config.ADMIN_EMAIL,
            password=generate_password_hash(Config.ADMIN_PASSWORD),
            first_name='Admin',
            last_name='User',
            is_admin=True,
            is_active=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user created with correct hash method")
        print(f"Admin credentials: {Config.ADMIN_EMAIL} / {Config.ADMIN_PASSWORD}")

if __name__ == '__main__':
    fix_password_hashes() 