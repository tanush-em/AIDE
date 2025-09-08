from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import json
import os
import pandas as pd
from typing import List, Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import data_loader
import tempfile

export_bp = Blueprint('data_export', __name__)

@export_bp.route('/api/export/attendance', methods=['GET'])
def export_attendance():
    """Export attendance data to CSV or Excel"""
    try:
        format_type = request.args.get('format', 'csv').lower()
        course = request.args.get('course', 'all')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Load attendance data
        df = data_loader.load_csv('attendance.csv')
        
        if df.empty:
            return jsonify({
                "success": False,
                "error": "No attendance data found"
            }), 404
        
        # Filter by course if specified
        if course != 'all':
            df = df[df['course_code'] == course]
        
        # Filter by date range if specified
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]
        
        # Create temporary file
        if format_type == 'excel':
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            df.to_excel(temp_file.name, index=False)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'attendance_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        else:  # CSV
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
            df.to_csv(temp_file.name, index=False)
            mimetype = 'text/csv'
            filename = f'attendance_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@export_bp.route('/api/export/students', methods=['GET'])
def export_students():
    """Export students data to CSV or Excel"""
    try:
        format_type = request.args.get('format', 'csv').lower()
        course = request.args.get('course', 'all')
        department = request.args.get('department', 'all')
        
        # Load students data
        df = data_loader.load_csv('students.csv')
        
        if df.empty:
            return jsonify({
                "success": False,
                "error": "No students data found"
            }), 404
        
        # Filter by course if specified
        if course != 'all':
            df = df[df['course'] == course]
        
        # Filter by department if specified
        if department != 'all':
            df = df[df['department'] == department]
        
        # Create temporary file
        if format_type == 'excel':
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            df.to_excel(temp_file.name, index=False)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'students_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        else:  # CSV
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
            df.to_csv(temp_file.name, index=False)
            mimetype = 'text/csv'
            filename = f'students_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@export_bp.route('/api/export/courses', methods=['GET'])
def export_courses():
    """Export courses data to CSV or Excel"""
    try:
        format_type = request.args.get('format', 'csv').lower()
        department = request.args.get('department', 'all')
        
        # Load courses data
        df = data_loader.load_csv('courses.csv')
        
        if df.empty:
            return jsonify({
                "success": False,
                "error": "No courses data found"
            }), 404
        
        # Filter by department if specified
        if department != 'all':
            df = df[df['department'] == department]
        
        # Create temporary file
        if format_type == 'excel':
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            df.to_excel(temp_file.name, index=False)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'courses_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        else:  # CSV
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
            df.to_csv(temp_file.name, index=False)
            mimetype = 'text/csv'
            filename = f'courses_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@export_bp.route('/api/export/leaves', methods=['GET'])
def export_leaves():
    """Export leave requests data to CSV or Excel"""
    try:
        format_type = request.args.get('format', 'csv').lower()
        status = request.args.get('status', 'all')
        leave_type = request.args.get('leave_type', 'all')
        
        # Load leave data
        leave_data = data_loader.load_json('leave_requests.json')
        
        if not leave_data:
            return jsonify({
                "success": False,
                "error": "No leave data found"
            }), 404
        
        # Convert to DataFrame
        df = pd.DataFrame(leave_data)
        
        # Filter by status if specified
        if status != 'all':
            df = df[df['status'] == status]
        
        # Filter by leave type if specified
        if leave_type != 'all':
            df = df[df['leaveType'] == leave_type]
        
        # Create temporary file
        if format_type == 'excel':
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            df.to_excel(temp_file.name, index=False)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'leaves_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        else:  # CSV
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
            df.to_csv(temp_file.name, index=False)
            mimetype = 'text/csv'
            filename = f'leaves_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@export_bp.route('/api/export/notices', methods=['GET'])
def export_notices():
    """Export notices data to CSV or Excel"""
    try:
        format_type = request.args.get('format', 'csv').lower()
        priority = request.args.get('priority', 'all')
        notice_type = request.args.get('type', 'all')
        
        # Load notice data
        notice_data = data_loader.load_json('notices.json')
        
        if not notice_data:
            return jsonify({
                "success": False,
                "error": "No notice data found"
            }), 404
        
        # Convert to DataFrame
        df = pd.DataFrame(notice_data)
        
        # Filter by priority if specified
        if priority != 'all':
            df = df[df['priority'] == priority]
        
        # Filter by type if specified
        if notice_type != 'all':
            df = df[df['type'] == notice_type]
        
        # Create temporary file
        if format_type == 'excel':
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
            df.to_excel(temp_file.name, index=False)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = f'notices_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        else:  # CSV
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
            df.to_csv(temp_file.name, index=False)
            mimetype = 'text/csv'
            filename = f'notices_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        temp_file.close()
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@export_bp.route('/api/export/all', methods=['GET'])
def export_all_data():
    """Export all data as a ZIP file"""
    try:
        import zipfile
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        zip_filename = f'complete_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Export all data files
            files_to_export = [
                ('attendance.csv', 'attendance.csv'),
                ('students.csv', 'students.csv'),
                ('courses.csv', 'courses.csv'),
                ('leave_requests.json', 'leave_requests.json'),
                ('notices.json', 'notices.json')
            ]
            
            for source_file, archive_name in files_to_export:
                source_path = os.path.join('data', source_file)
                if os.path.exists(source_path):
                    zipf.write(source_path, archive_name)
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name=zip_filename,
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
