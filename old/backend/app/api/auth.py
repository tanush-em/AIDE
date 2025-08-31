from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import csv
import os
import bcrypt
from datetime import datetime, timedelta
import logging
from ..models.user import UserCreate, UserResponse, LoginRequest, LoginResponse
from ..utils.auth import hash_password, verify_password, load_csv_data

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

# Data file paths (preserving existing structure)
STUDENT_DATA_PATH = 'data/auth/student.csv'
FACULTY_DATA_PATH = 'data/auth/faculty.csv'

@auth_bp.route('/login', methods=['POST'])
def login():
    """Enhanced login endpoint with JWT support"""
    try:
        data = request.get_json()
        
        # Validate input using Pydantic
        try:
            login_request = LoginRequest(**data)
        except Exception as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        
        email = login_request.email.strip()
        password = login_request.password.strip()
        role = login_request.role.value
        
        logger.info(f"Login attempt - Email: {email}, Role: {role}")
        
        # Load appropriate data based on role (preserving existing CSV system)
        if role == 'student':
            users = load_csv_data(STUDENT_DATA_PATH)
            id_field = 'rollno'
            name_field = 'name'
        elif role == 'faculty':
            users = load_csv_data(FACULTY_DATA_PATH)
            id_field = 'faculty_id'
            name_field = 'name'
        else:
            return jsonify({'error': 'Invalid role. Must be student or faculty'}), 400
        
        logger.info(f"Loaded {len(users)} users for role {role}")
        
        # Find user in CSV data
        user = None
        for u in users:
            user_email = u.get('email', '').strip()
            user_password = str(u.get('password', '')).strip()
            
            if user_email == email and user_password == password:
                user = u
                break
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create user response object
        user_response = UserResponse(
            user_id=user.get(id_field),
            email=user.get('email'),
            role=role,
            profile={
                "first_name": user.get(name_field, '').split()[0] if user.get(name_field) else '',
                "last_name": ' '.join(user.get(name_field, '').split()[1:]) if user.get(name_field) else '',
                "department": "Computer Science",  # Default for existing data
                "phone": "",
                "year": 2 if role == 'student' else None,
                "batch": "2022-2026" if role == 'student' else None,
                "employee_id": user.get(id_field) if role == 'faculty' else None,
                "designation": "Faculty" if role == 'faculty' else None
            },
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Create JWT tokens
        access_token = create_access_token(
            identity={
                'user_id': user.get(id_field),
                'email': user.get('email'),
                'role': role
            },
            expires_delta=timedelta(hours=1)
        )
        
        refresh_token = create_refresh_token(
            identity={
                'user_id': user.get(id_field),
                'email': user.get('email'),
                'role': role
            },
            expires_delta=timedelta(days=30)
        )
        
        # Store user in MongoDB for enhanced features (optional)
        try:
            mongo_user = {
                'user_id': user.get(id_field),
                'email': user.get('email'),
                'password_hash': hash_password(password),  # Hash for security
                'role': role,
                'profile': user_response.profile.dict(),
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'last_login': datetime.utcnow()
            }
            
            # Check if user exists in MongoDB
            existing_user = current_app.mongo.users.find_one({'user_id': user.get(id_field)})
            if existing_user:
                # Update last login
                current_app.mongo.users.update_one(
                    {'user_id': user.get(id_field)},
                    {'$set': {'last_login': datetime.utcnow()}}
                )
            else:
                # Insert new user
                current_app.mongo.users.insert_one(mongo_user)
                
        except Exception as e:
            logger.warning(f"Failed to store user in MongoDB: {e}")
            # Continue with login even if MongoDB storage fails
        
        logger.info(f"✅ Successful login for user: {user.get(id_field)}")
        
        return jsonify(LoginResponse(
            success=True,
            user=user_response,
            access_token=access_token,
            refresh_token=refresh_token
        ).dict())
        
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        
        return jsonify({
            'access_token': new_access_token,
            'success': True
        })
        
    except Exception as e:
        logger.error(f"❌ Token refresh error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/validate', methods=['POST'])
def validate_session():
    """Validate user session (preserving existing endpoint)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        role = data.get('role')
        
        if not user_id or not role:
            return jsonify({'error': 'User ID and role are required'}), 400
        
        # Load appropriate data based on role
        if role == 'student':
            users = load_csv_data(STUDENT_DATA_PATH)
            id_field = 'rollno'
        elif role == 'faculty':
            users = load_csv_data(FACULTY_DATA_PATH)
            id_field = 'faculty_id'
        else:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Check if user exists in CSV
        user = None
        for u in users:
            if str(u.get(id_field, '')).strip() == str(user_id).strip():
                user = u
                break
        
        if user:
            return jsonify({'valid': True, 'user': user})
        else:
            return jsonify({'valid': False, 'error': 'User not found'}), 404
            
    except Exception as e:
        logger.error(f"❌ Session validation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user = get_jwt_identity()
        
        # Try to get user from MongoDB first
        user = current_app.mongo.users.find_one({'user_id': current_user['user_id']})
        
        if user:
            return jsonify({
                'success': True,
                'user': {
                    'user_id': user['user_id'],
                    'email': user['email'],
                    'role': user['role'],
                    'profile': user['profile'],
                    'is_active': user['is_active'],
                    'created_at': user['created_at'].isoformat(),
                    'last_login': user.get('last_login', user['created_at']).isoformat()
                }
            })
        else:
            # Fallback to CSV data
            role = current_user['role']
            if role == 'student':
                users = load_csv_data(STUDENT_DATA_PATH)
                id_field = 'rollno'
                name_field = 'name'
            else:
                users = load_csv_data(FACULTY_DATA_PATH)
                id_field = 'faculty_id'
                name_field = 'name'
            
            for u in users:
                if str(u.get(id_field, '')).strip() == str(current_user['user_id']).strip():
                    return jsonify({
                        'success': True,
                        'user': {
                            'user_id': u.get(id_field),
                            'email': u.get('email'),
                            'role': role,
                            'profile': {
                                "first_name": u.get(name_field, '').split()[0] if u.get(name_field) else '',
                                "last_name": ' '.join(u.get(name_field, '').split()[1:]) if u.get(name_field) else '',
                                "department": "Computer Science",
                                "phone": "",
                                "year": 2 if role == 'student' else None,
                                "batch": "2022-2026" if role == 'student' else None,
                                "employee_id": u.get(id_field) if role == 'faculty' else None,
                                "designation": "Faculty" if role == 'faculty' else None
                            },
                            'is_active': True
                        }
                    })
            
            return jsonify({'error': 'User not found'}), 404
            
    except Exception as e:
        logger.error(f"❌ Profile retrieval error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard tokens)"""
    try:
        current_user = get_jwt_identity()
        logger.info(f"User logout: {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Successfully logged out'
        })
        
    except Exception as e:
        logger.error(f"❌ Logout error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for authentication service"""
    try:
        # Check if CSV files exist
        student_file_exists = os.path.exists(STUDENT_DATA_PATH)
        faculty_file_exists = os.path.exists(FACULTY_DATA_PATH)
        
        # Check MongoDB connection
        mongo_healthy = False
        try:
            current_app.mongo.command('ping')
            mongo_healthy = True
        except:
            pass
        
        return jsonify({
            'service': 'authentication',
            'status': 'healthy',
            'components': {
                'csv_files': {
                    'student_data': student_file_exists,
                    'faculty_data': faculty_file_exists
                },
                'mongodb': mongo_healthy
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Health check error: {str(e)}")
        return jsonify({
            'service': 'authentication',
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500
