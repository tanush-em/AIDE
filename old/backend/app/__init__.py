from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
import redis
import os
from dotenv import load_dotenv

load_dotenv()

jwt = JWTManager()
mongo_client = None
redis_client = None

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800  # 7 days
    
    # Initialize extensions
    CORS(app, origins=['http://localhost:3000'], supports_credentials=True)
    jwt.init_app(app)
    
    # Initialize databases
    init_databases(app)
    
    # Register blueprints
    from .api.auth import auth_bp
    from .api.dashboard import dashboard_bp
    from .api.attendance import attendance_bp
    from .api.leaves import leaves_bp
    from .api.events import events_bp
    from .api.notices import notices_bp
    from .api.resources import resources_bp
    from .api.agents import agents_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(leaves_bp, url_prefix='/api/leaves')
    app.register_blueprint(events_bp, url_prefix='/api/events')
    app.register_blueprint(notices_bp, url_prefix='/api/notices')
    app.register_blueprint(resources_bp, url_prefix='/api/resources')
    app.register_blueprint(agents_bp, url_prefix='/api/agents')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {
            'status': 'healthy',
            'message': 'Academic AI Management System is running',
            'timestamp': '2024-01-01T00:00:00Z'
        }
    
    return app

def init_databases(app):
    """Initialize MongoDB and Redis connections"""
    global mongo_client, redis_client
    
    try:
        # MongoDB connection
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/academic_ai')
        mongo_client = MongoClient(mongo_uri)
        app.mongo = mongo_client.academic_ai
        
        # Test MongoDB connection
        mongo_client.admin.command('ping')
        print("✅ MongoDB connected successfully")
        
        # Redis connection
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        redis_client = redis.from_url(redis_url)
        app.redis = redis_client
        
        # Test Redis connection
        redis_client.ping()
        print("✅ Redis connected successfully")
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        raise e

def get_mongo_client():
    """Get MongoDB client instance"""
    return mongo_client

def get_redis_client():
    """Get Redis client instance"""
    return redis_client
