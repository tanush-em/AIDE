import bcrypt
import csv
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    try:
        # Encode password to bytes
        password_bytes = password.encode('utf-8')
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string
        return hashed.decode('utf-8')
        
    except Exception as e:
        logger.error(f"❌ Error hashing password: {e}")
        raise

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        # Encode both to bytes
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        # Verify password
        return bcrypt.checkpw(password_bytes, hashed_bytes)
        
    except Exception as e:
        logger.error(f"❌ Error verifying password: {e}")
        return False

def load_csv_data(file_path: str) -> List[Dict[str, Any]]:
    """Load data from CSV file with error handling"""
    data = []
    
    try:
        if not os.path.exists(file_path):
            logger.warning(f"CSV file not found: {file_path}")
            return data
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Clean up whitespace in values and remove quotes
                cleaned_row = {}
                for key, value in row.items():
                    clean_key = key.strip()
                    if isinstance(value, str):
                        # Remove quotes and strip whitespace
                        clean_value = value.strip().strip('"').strip("'")
                    else:
                        clean_value = value
                    cleaned_row[clean_key] = clean_value
                data.append(cleaned_row)
        
        logger.info(f"✅ Loaded {len(data)} records from {file_path}")
        
    except Exception as e:
        logger.error(f"❌ Error loading CSV data from {file_path}: {e}")
        raise
    
    return data

def save_csv_data(file_path: str, data: List[Dict[str, Any]], fieldnames: List[str] = None) -> bool:
    """Save data to CSV file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Determine fieldnames if not provided
        if not fieldnames and data:
            fieldnames = list(data[0].keys())
        
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            if fieldnames:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(file)
                for row in data:
                    writer.writerow(row.values())
        
        logger.info(f"✅ Saved {len(data)} records to {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error saving CSV data to {file_path}: {e}")
        return False

def validate_user_credentials(email: str, password: str, role: str) -> Dict[str, Any]:
    """Validate user credentials against CSV data"""
    try:
        # Determine file path based on role
        if role == 'student':
            file_path = 'data/auth/student.csv'
            id_field = 'rollno'
        elif role == 'faculty':
            file_path = 'data/auth/faculty.csv'
            id_field = 'faculty_id'
        else:
            return {
                'valid': False,
                'error': 'Invalid role'
            }
        
        # Load user data
        users = load_csv_data(file_path)
        
        # Find matching user
        for user in users:
            user_email = user.get('email', '').strip()
            user_password = str(user.get('password', '')).strip()
            
            if user_email == email and user_password == password:
                return {
                    'valid': True,
                    'user': {
                        'user_id': user.get(id_field),
                        'email': user.get('email'),
                        'name': user.get('name'),
                        'role': role
                    }
                }
        
        return {
            'valid': False,
            'error': 'Invalid credentials'
        }
        
    except Exception as e:
        logger.error(f"❌ Error validating credentials: {e}")
        return {
            'valid': False,
            'error': str(e)
        }

def create_user_in_csv(user_data: Dict[str, Any], role: str) -> bool:
    """Create a new user in the appropriate CSV file"""
    try:
        # Determine file path and fieldnames based on role
        if role == 'student':
            file_path = 'data/auth/student.csv'
            fieldnames = ['rollno', 'name', 'email', 'password']
            user_id = user_data.get('rollno')
        elif role == 'faculty':
            file_path = 'data/auth/faculty.csv'
            fieldnames = ['faculty_id', 'name', 'email', 'password']
            user_id = user_data.get('faculty_id')
        else:
            logger.error(f"Invalid role for user creation: {role}")
            return False
        
        # Load existing data
        existing_data = load_csv_data(file_path)
        
        # Check if user already exists
        for user in existing_data:
            if user.get('email') == user_data.get('email'):
                logger.warning(f"User with email {user_data.get('email')} already exists")
                return False
        
        # Add new user
        existing_data.append(user_data)
        
        # Save updated data
        return save_csv_data(file_path, existing_data, fieldnames)
        
    except Exception as e:
        logger.error(f"❌ Error creating user in CSV: {e}")
        return False

def update_user_in_csv(user_id: str, updates: Dict[str, Any], role: str) -> bool:
    """Update an existing user in the appropriate CSV file"""
    try:
        # Determine file path and ID field based on role
        if role == 'student':
            file_path = 'data/auth/student.csv'
            id_field = 'rollno'
        elif role == 'faculty':
            file_path = 'data/auth/faculty.csv'
            id_field = 'faculty_id'
        else:
            logger.error(f"Invalid role for user update: {role}")
            return False
        
        # Load existing data
        existing_data = load_csv_data(file_path)
        
        # Find and update user
        for i, user in enumerate(existing_data):
            if str(user.get(id_field, '')).strip() == str(user_id).strip():
                # Update user data
                existing_data[i].update(updates)
                
                # Save updated data
                fieldnames = list(existing_data[0].keys())
                return save_csv_data(file_path, existing_data, fieldnames)
        
        logger.warning(f"User with ID {user_id} not found")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error updating user in CSV: {e}")
        return False
