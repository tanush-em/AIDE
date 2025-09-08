from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import os
import pandas as pd
from typing import List, Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import data_loader

attendance_bp = Blueprint('attendance', __name__)

def load_attendance_data():
    """Load attendance data from CSV file"""
    try:
        df = data_loader.load_csv('attendance.csv')
        if df.empty:
            return []
        return df.to_dict('records')
    except Exception as e:
        print(f"Error loading attendance data: {e}")
        return []

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

def save_attendance_data(data):
    """Save attendance data to CSV file"""
    try:
        df = pd.DataFrame(data)
        return data_loader.save_csv('attendance.csv', df)
    except Exception as e:
        print(f"Error saving attendance data: {e}")
        return False

@attendance_bp.route('/api/attendance/students', methods=['GET'])
def get_students():
    """Get all students with attendance data"""
    try:
        # Load students and attendance data from CSV files
        students_data = load_students_data()
        attendance_data = load_attendance_data()
        
        # Group attendance by student
        attendance_by_student = {}
        for record in attendance_data:
            student_id = str(record['student_id'])
            if student_id not in attendance_by_student:
                attendance_by_student[student_id] = []
            
            attendance_by_student[student_id].append({
                "date": record['date'],
                "status": record['status'],
                "class": record['class_name'],
                "remarks": record.get('remarks', '')
            })
        
        # Combine student data with attendance
        students = []
        for student in students_data:
            student_id = str(student['id'])
            students.append({
                "id": student['id'],
                "name": student['name'],
                "rollNumber": student['roll_number'],
                "email": student['email'],
                "course": student['course'],
                "department": student['department'],
                "attendance": attendance_by_student.get(student_id, [])
            })
        
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
        course_code = data.get('course_code', '')
        marked_by = data.get('marked_by', 'Dr. Sarah Johnson')
        
        if not all([student_id, date, status, class_name]):
            return jsonify({
                "success": False,
                "error": "Missing required fields"
            }), 400
        
        # Load existing attendance data
        attendance_data = load_attendance_data()
        
        # Get student info
        students_data = load_students_data()
        student_info = next((s for s in students_data if str(s['id']) == str(student_id)), None)
        
        if not student_info:
            return jsonify({
                "success": False,
                "error": "Student not found"
            }), 404
        
        # Create new attendance record
        new_record = {
            "id": len(attendance_data) + 1,
            "student_id": student_id,
            "student_name": student_info['name'],
            "roll_number": student_info['roll_number'],
            "course_code": course_code or student_info['course'],
            "date": date,
            "status": status,
            "class_name": class_name,
            "remarks": remarks,
            "marked_by": marked_by
        }
        
        # Add to attendance data
        attendance_data.append(new_record)
        
        # Save back to CSV
        if save_attendance_data(attendance_data):
            return jsonify({
                "success": True,
                "message": "Attendance marked successfully",
                "data": new_record
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save attendance data"
            }), 500
            
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
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        # Load data from CSV files
        attendance_data = load_attendance_data()
        students_data = load_students_data()
        
        # Filter by course if specified
        if course != 'all':
            attendance_data = [a for a in attendance_data if a.get('course_code') == course]
            students_data = [s for s in students_data if s.get('course') == course]
        
        # Calculate stats
        total_students = len(students_data)
        
        # Get today's attendance
        today_attendance = [a for a in attendance_data if a.get('date') == date]
        
        present_today = len([a for a in today_attendance if a.get('status') == 'present'])
        absent_today = len([a for a in today_attendance if a.get('status') == 'absent'])
        late_today = len([a for a in today_attendance if a.get('status') == 'late'])
        excused_today = len([a for a in today_attendance if a.get('status') == 'excused'])
        
        # Calculate overall attendance rate
        total_attendance_records = len(attendance_data)
        if total_attendance_records > 0:
            present_records = len([a for a in attendance_data if a.get('status') == 'present'])
            attendance_rate = (present_records / total_attendance_records) * 100
        else:
            attendance_rate = 0
        
        stats = {
            "total_students": total_students,
            "attendance_rate": round(attendance_rate, 1),
            "present_today": present_today,
            "absent_today": absent_today,
            "late_today": late_today,
            "excused_today": excused_today,
            "date": date,
            "course": course
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
