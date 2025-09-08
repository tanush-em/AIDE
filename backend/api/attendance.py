from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any

attendance_bp = Blueprint('attendance', __name__)

# Mock data storage (in production, this would be a database)
ATTENDANCE_DATA_FILE = 'data/attendance.json'

def load_attendance_data():
    """Load attendance data from file"""
    if os.path.exists(ATTENDANCE_DATA_FILE):
        try:
            with open(ATTENDANCE_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_attendance_data(data):
    """Save attendance data to file"""
    os.makedirs(os.path.dirname(ATTENDANCE_DATA_FILE), exist_ok=True)
    with open(ATTENDANCE_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@attendance_bp.route('/api/attendance/students', methods=['GET'])
def get_students():
    """Get all students with attendance data"""
    try:
        # For now, return mock data
        # In production, this would query the database
        students = [
            {
                "id": "1",
                "name": "Alice Johnson",
                "rollNumber": "CS001",
                "email": "alice.johnson@university.edu",
                "course": "CS101",
                "attendance": [
                    {"date": "2024-01-15", "status": "present", "class": "Data Structures"},
                    {"date": "2024-01-16", "status": "present", "class": "Data Structures"},
                    {"date": "2024-01-17", "status": "late", "class": "Data Structures"},
                    {"date": "2024-01-18", "status": "present", "class": "Data Structures"},
                    {"date": "2024-01-19", "status": "absent", "class": "Data Structures"},
                ]
            },
            {
                "id": "2",
                "name": "Bob Smith",
                "rollNumber": "CS002",
                "email": "bob.smith@university.edu",
                "course": "CS101",
                "attendance": [
                    {"date": "2024-01-15", "status": "present", "class": "Data Structures"},
                    {"date": "2024-01-16", "status": "present", "class": "Data Structures"},
                    {"date": "2024-01-17", "status": "present", "class": "Data Structures"},
                    {"date": "2024-01-18", "status": "present", "class": "Data Structures"},
                    {"date": "2024-01-19", "status": "present", "class": "Data Structures"},
                ]
            },
            {
                "id": "3",
                "name": "Carol Davis",
                "rollNumber": "CS003",
                "email": "carol.davis@university.edu",
                "course": "CS201",
                "attendance": [
                    {"date": "2024-01-15", "status": "present", "class": "Algorithms"},
                    {"date": "2024-01-16", "status": "absent", "class": "Algorithms"},
                    {"date": "2024-01-17", "status": "present", "class": "Algorithms"},
                    {"date": "2024-01-18", "status": "excused", "class": "Algorithms"},
                    {"date": "2024-01-19", "status": "present", "class": "Algorithms"},
                ]
            }
        ]
        
        return jsonify({
            "success": True,
            "data": students
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@attendance_bp.route('/api/attendance/mark', methods=['POST'])
def mark_attendance():
    """Mark attendance for students"""
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        date = data.get('date')
        status = data.get('status')  # present, absent, late, excused
        class_name = data.get('class')
        remarks = data.get('remarks', '')
        
        if not all([student_id, date, status, class_name]):
            return jsonify({
                "success": False,
                "error": "Missing required fields"
            }), 400
        
        # In production, this would update the database
        # For now, we'll just return success
        return jsonify({
            "success": True,
            "message": "Attendance marked successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@attendance_bp.route('/api/attendance/export', methods=['GET'])
def export_attendance():
    """Export attendance data"""
    try:
        course = request.args.get('course', 'all')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        format_type = request.args.get('format', 'json')
        
        # In production, this would generate and return the file
        # For now, return mock data
        return jsonify({
            "success": True,
            "message": "Export generated successfully",
            "download_url": "/api/attendance/download/export.csv"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@attendance_bp.route('/api/attendance/stats', methods=['GET'])
def get_attendance_stats():
    """Get attendance statistics"""
    try:
        course = request.args.get('course', 'all')
        
        # Mock stats
        stats = {
            "total_students": 156,
            "attendance_rate": 87.5,
            "present_today": 142,
            "absent_today": 14,
            "late_today": 8,
            "excused_today": 2
        }
        
        return jsonify({
            "success": True,
            "data": stats
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
