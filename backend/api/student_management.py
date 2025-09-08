from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import os
import pandas as pd
from typing import List, Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import data_loader

student_bp = Blueprint('student_management', __name__)

def load_students_data():
    """Load students data from CSV file"""
    try:
        df = data_loader.load_csv('students.csv')
        if df.empty:
            return []
        return df.to_dict('records')
    except Exception as e:
        print(f"Error loading students data: {e}")
        return []

def load_courses_data():
    """Load courses data from CSV file"""
    try:
        df = data_loader.load_csv('courses.csv')
        if df.empty:
            return []
        return df.to_dict('records')
    except Exception as e:
        print(f"Error loading courses data: {e}")
        return []

def save_students_data(data):
    """Save students data to CSV file"""
    try:
        df = pd.DataFrame(data)
        return data_loader.save_csv('students.csv', df)
    except Exception as e:
        print(f"Error saving students data: {e}")
        return False

def save_courses_data(data):
    """Save courses data to CSV file"""
    try:
        df = pd.DataFrame(data)
        return data_loader.save_csv('courses.csv', df)
    except Exception as e:
        print(f"Error saving courses data: {e}")
        return False

@student_bp.route('/api/students', methods=['GET'])
def get_students():
    """Get all students"""
    try:
        students = load_students_data()
        
        # Add query parameters for filtering
        course = request.args.get('course')
        department = request.args.get('department')
        status = request.args.get('status')
        
        if course:
            students = [s for s in students if s.get('course') == course]
        if department:
            students = [s for s in students if s.get('department') == department]
        if status:
            students = [s for s in students if s.get('status') == status]
        
        return jsonify({
            "success": True,
            "data": students
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@student_bp.route('/api/students/<student_id>', methods=['GET'])
def get_student(student_id):
    """Get a specific student by ID"""
    try:
        students = load_students_data()
        student = next((s for s in students if str(s['id']) == str(student_id)), None)
        
        if not student:
            return jsonify({
                "success": False,
                "error": "Student not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": student
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@student_bp.route('/api/students', methods=['POST'])
def create_student():
    """Create a new student"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'roll_number', 'email', 'course', 'department']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Load existing students data
        students_data = load_students_data()
        
        # Check if roll number already exists
        if any(s.get('roll_number') == data['roll_number'] for s in students_data):
            return jsonify({
                "success": False,
                "error": "Student with this roll number already exists"
            }), 400
        
        # Create new student
        new_student = {
            "id": len(students_data) + 1,
            "name": data['name'],
            "roll_number": data['roll_number'],
            "email": data['email'],
            "course": data['course'],
            "department": data['department'],
            "phone": data.get('phone', ''),
            "address": data.get('address', ''),
            "enrollment_date": data.get('enrollment_date', datetime.now().strftime('%Y-%m-%d')),
            "status": data.get('status', 'active')
        }
        
        # Add to students data
        students_data.append(new_student)
        
        # Save back to CSV
        if save_students_data(students_data):
            return jsonify({
                "success": True,
                "data": new_student,
                "message": "Student created successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save student data"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@student_bp.route('/api/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    """Update a student"""
    try:
        data = request.get_json()
        
        # Load existing students data
        students_data = load_students_data()
        
        # Find and update the student
        for i, student in enumerate(students_data):
            if str(student['id']) == str(student_id):
                # Update fields
                for key, value in data.items():
                    if key in student:
                        student[key] = value
                
                student['updated_at'] = datetime.now().isoformat()
                students_data[i] = student
                break
        else:
            return jsonify({
                "success": False,
                "error": "Student not found"
            }), 404
        
        # Save back to CSV
        if save_students_data(students_data):
            return jsonify({
                "success": True,
                "data": students_data[i],
                "message": "Student updated successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save student data"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@student_bp.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses"""
    try:
        courses = load_courses_data()
        
        # Add query parameters for filtering
        department = request.args.get('department')
        instructor = request.args.get('instructor')
        
        if department:
            courses = [c for c in courses if c.get('department') == department]
        if instructor:
            courses = [c for c in courses if c.get('instructor') == instructor]
        
        return jsonify({
            "success": True,
            "data": courses
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@student_bp.route('/api/courses/<course_id>', methods=['GET'])
def get_course(course_id):
    """Get a specific course by ID"""
    try:
        courses = load_courses_data()
        course = next((c for c in courses if str(c['id']) == str(course_id)), None)
        
        if not course:
            return jsonify({
                "success": False,
                "error": "Course not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": course
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@student_bp.route('/api/courses', methods=['POST'])
def create_course():
    """Create a new course"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['course_code', 'course_name', 'department', 'instructor', 'credits']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Load existing courses data
        courses_data = load_courses_data()
        
        # Check if course code already exists
        if any(c.get('course_code') == data['course_code'] for c in courses_data):
            return jsonify({
                "success": False,
                "error": "Course with this code already exists"
            }), 400
        
        # Create new course
        new_course = {
            "id": len(courses_data) + 1,
            "course_code": data['course_code'],
            "course_name": data['course_name'],
            "department": data['department'],
            "instructor": data['instructor'],
            "credits": data['credits'],
            "schedule": data.get('schedule', ''),
            "room": data.get('room', ''),
            "enrollment_limit": data.get('enrollment_limit', 50),
            "current_enrollment": data.get('current_enrollment', 0)
        }
        
        # Add to courses data
        courses_data.append(new_course)
        
        # Save back to CSV
        if save_courses_data(courses_data):
            return jsonify({
                "success": True,
                "data": new_course,
                "message": "Course created successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save course data"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
