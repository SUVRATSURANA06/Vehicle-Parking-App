from app import create_app
from extensions import db
from models.user import User
from config import Config

def fix_admin():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
        if admin:
            admin.is_admin = True
            admin.is_active = True
            db.session.commit()
            print(f"✅ Updated {admin.email} to is_admin=True and is_active=True")
        else:
            print(f"❌ Admin user with email {Config.ADMIN_EMAIL} not found")

if __name__ == '__main__':
    fix_admin() 