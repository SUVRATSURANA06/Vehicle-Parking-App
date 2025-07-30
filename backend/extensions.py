from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
import redis
from celery import Celery
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()
cors = CORS()
mail = Mail()

# Redis client
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    redis_client.ping()
except Exception as e:
    print(f"Warning: Redis connection failed: {e}")
    redis_client = None

# Celery
celery = Celery('parking_app') 