from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os
import json

app = Flask(__name__)
CORS(app)

# Data file paths
STUDENT_DATA_PATH = 'data/auth/student.csv'
FACULTY_DATA_PATH = 'data/auth/faculty.csv'

def load_csv_data(file_path):
    """Load data from CSV file"""
    data = []
    if os.path.exists(file_path):
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
    return data

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', '').strip().lower()
        
        print(f"Login attempt - Email: {email}, Role: {role}, Password: {password}")
        
        if not email or not password or not role:
            return jsonify({'error': 'Email, password, and role are required'}), 400
        
        # Load appropriate data based on role
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
        
        print(f"Loaded {len(users)} users for role {role}")
        for u in users:
            print(f"User: {u}")
        
        # Find user
        user = None
        for u in users:
            user_email = u.get('email', '').strip()
            user_password = str(u.get('password', '')).strip()
            print(f"Comparing - Input: {email} vs {user_email}, Password: {password} vs {user_password}")
            if user_email == email and user_password == str(password):
                user = u
                break
        
        if user:
            return jsonify({
                'success': True,
                'user': {
                    'id': user.get(id_field),
                    'name': user.get(name_field),
                    'email': user.get('email'),
                    'role': role
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/validate', methods=['POST'])
def validate_session():
    """Validate user session"""
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
        
        # Check if user exists
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
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/<role>/<user_id>', methods=['GET'])
def get_dashboard_data(role, user_id):
    """Get dashboard data for user"""
    try:
        if role not in ['student', 'faculty', 'coordinator']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Mock dashboard data - in a real app, this would come from a database
        dashboard_data = {
            'student': {
                'timetable': [
                    {'day': 'Monday', 'time': '9:00 AM', 'subject': 'Mathematics', 'room': 'A101'},
                    {'day': 'Monday', 'time': '10:30 AM', 'subject': 'Physics', 'room': 'B202'},
                    {'day': 'Tuesday', 'time': '9:00 AM', 'subject': 'Chemistry', 'room': 'C303'},
                ],
                'attendance': {'present': 85, 'total': 100, 'percentage': 85},
                'notifications': [
                    {'type': 'warning', 'message': 'Low attendance in Mathematics', 'time': '2 hours ago'},
                    {'type': 'info', 'message': 'New study material uploaded', 'time': '1 day ago'},
                ],
                'pending_actions': [
                    {'type': 'exam', 'title': 'Mid-term Mathematics', 'deadline': '2024-01-15'},
                    {'type': 'assignment', 'title': 'Physics Lab Report', 'deadline': '2024-01-10'},
                ]
            },
            'faculty': {
                'classes_today': [
                    {'time': '9:00 AM', 'subject': 'Mathematics', 'room': 'A101', 'students': 45},
                    {'time': '2:00 PM', 'subject': 'Advanced Calculus', 'room': 'B202', 'students': 32},
                ],
                'pending_grading': [
                    {'assignment': 'Calculus Quiz 1', 'submissions': 45, 'due': '2024-01-08'},
                    {'assignment': 'Linear Algebra HW', 'submissions': 38, 'due': '2024-01-10'},
                ],
                'leave_requests': [
                    {'student': 'John Doe', 'reason': 'Medical emergency', 'dates': '2024-01-12 to 2024-01-14'},
                ]
            },
            'coordinator': {
                'upcoming_events': [
                    {'name': 'Annual Tech Fest', 'date': '2024-01-20', 'registrations': 150},
                    {'name': 'Career Fair', 'date': '2024-01-25', 'registrations': 89},
                ],
                'system_notifications': [
                    {'type': 'info', 'message': 'New faculty member joined', 'time': '1 hour ago'},
                    {'type': 'warning', 'message': 'Schedule conflict detected', 'time': '3 hours ago'},
                ]
            }
        }
        
        return jsonify(dashboard_data.get(role, {}))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notices', methods=['GET'])
def get_notices():
    """Get all notices"""
    try:
        notice_file_path = 'data/notice/notice.json'
        if os.path.exists(notice_file_path):
            with open(notice_file_path, 'r', encoding='utf-8') as file:
                notices = json.load(file)
            return jsonify(notices)
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 