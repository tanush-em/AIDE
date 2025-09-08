from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import data_loader

dashboard_bp = Blueprint('dashboard', __name__)

def load_all_data():
    """Load all data from CSV and JSON files"""
    try:
        students_data = data_loader.load_csv('students.csv')
        courses_data = data_loader.load_csv('courses.csv')
        attendance_data = data_loader.load_csv('attendance.csv')
        leave_data = data_loader.load_json('leave_requests.json')
        notice_data = data_loader.load_json('notices.json')
        
        return {
            'students': students_data.to_dict('records') if not students_data.empty else [],
            'courses': courses_data.to_dict('records') if not courses_data.empty else [],
            'attendance': attendance_data.to_dict('records') if not attendance_data.empty else [],
            'leaves': leave_data if isinstance(leave_data, list) else [],
            'notices': notice_data if isinstance(notice_data, list) else []
        }
    except Exception as e:
        print(f"Error loading data: {e}")
        return {
            'students': [],
            'courses': [],
            'attendance': [],
            'leaves': [],
            'notices': []
        }

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Load all data from files
        data = load_all_data()
        
        # Calculate basic stats
        total_students = len(data['students'])
        total_courses = len(data['courses'])
        pending_leaves = len([l for l in data['leaves'] if l.get('status') == 'pending'])
        active_notices = len([n for n in data['notices'] if n.get('isActive', True)])
        
        # Calculate attendance rate
        attendance_records = data['attendance']
        if attendance_records:
            present_count = len([a for a in attendance_records if a.get('status') == 'present'])
            total_attendance = len(attendance_records)
            attendance_rate = (present_count / total_attendance) * 100 if total_attendance > 0 else 0
        else:
            attendance_rate = 0
        
        # Generate recent activities from actual data
        recent_activities = []
        
        # Add recent attendance activities
        recent_attendance = sorted(attendance_records, key=lambda x: x.get('date', ''), reverse=True)[:3]
        for i, att in enumerate(recent_attendance):
            recent_activities.append({
                "id": f"att_{i+1}",
                "type": "attendance",
                "title": f"{att.get('course_code', 'Unknown')} - {att.get('class_name', 'Class')}",
                "description": f"Attendance marked for {att.get('student_name', 'Student')} - {att.get('status', 'Unknown')}",
                "timestamp": f"{att.get('date', '')}T10:00:00Z",
                "status": "completed"
            })
        
        # Add recent leave activities
        recent_leaves = sorted(data['leaves'], key=lambda x: x.get('submittedAt', ''), reverse=True)[:2]
        for i, leave in enumerate(recent_leaves):
            recent_activities.append({
                "id": f"leave_{i+1}",
                "type": "leave",
                "title": f"Leave Request - {leave.get('studentName', 'Unknown')}",
                "description": f"{leave.get('leaveType', 'Unknown')} leave for {leave.get('duration', 0)} days - {leave.get('status', 'pending')}",
                "timestamp": leave.get('submittedAt', ''),
                "status": leave.get('status', 'pending')
            })
        
        # Add recent notice activities
        recent_notices = sorted(data['notices'], key=lambda x: x.get('createdAt', ''), reverse=True)[:2]
        for i, notice in enumerate(recent_notices):
            recent_activities.append({
                "id": f"notice_{i+1}",
                "type": "notice",
                "title": notice.get('title', 'Notice'),
                "description": f"Notice posted by {notice.get('author', 'Unknown')}",
                "timestamp": notice.get('createdAt', ''),
                "status": "completed"
            })
        
        # Sort activities by timestamp
        recent_activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        stats = {
            "totalStudents": total_students,
            "totalCourses": total_courses,
            "attendanceRate": round(attendance_rate, 1),
            "pendingLeaves": pending_leaves,
            "activeNotices": active_notices,
            "recentActivities": recent_activities[:5]  # Limit to 5 most recent
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

@dashboard_bp.route('/api/dashboard/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data for charts and graphs"""
    try:
        # Load all data from files
        data = load_all_data()
        
        # Calculate attendance trend by date
        attendance_by_date = {}
        for record in data['attendance']:
            date = record.get('date')
            if date:
                if date not in attendance_by_date:
                    attendance_by_date[date] = {'present': 0, 'total': 0}
                attendance_by_date[date]['total'] += 1
                if record.get('status') == 'present':
                    attendance_by_date[date]['present'] += 1
        
        attendance_trend = []
        for date in sorted(attendance_by_date.keys()):
            rate = (attendance_by_date[date]['present'] / attendance_by_date[date]['total']) * 100
            attendance_trend.append({"date": date, "rate": round(rate, 1)})
        
        # Calculate leave requests by type
        leave_by_type = {}
        for leave in data['leaves']:
            leave_type = leave.get('leaveType', 'unknown')
            leave_by_type[leave_type] = leave_by_type.get(leave_type, 0) + 1
        
        leave_requests_by_type = [{"type": k, "count": v} for k, v in leave_by_type.items()]
        
        # Calculate course performance
        course_performance = []
        for course in data['courses']:
            course_code = course.get('course_code', '')
            course_attendance = [a for a in data['attendance'] if a.get('course_code') == course_code]
            
            if course_attendance:
                present_count = len([a for a in course_attendance if a.get('status') == 'present'])
                attendance_rate = (present_count / len(course_attendance)) * 100
            else:
                attendance_rate = 0
            
            course_performance.append({
                "course": course_code,
                "attendance": round(attendance_rate, 1),
                "enrollment": course.get('current_enrollment', 0),
                "capacity": course.get('enrollment_limit', 0)
            })
        
        # Calculate monthly stats (simplified)
        current_month = datetime.now().strftime('%B').lower()
        monthly_stats = {
            current_month: {
                "totalClasses": len(set([a.get('date') for a in data['attendance']])),
                "averageAttendance": round(sum([(len([a for a in data['attendance'] if a.get('status') == 'present']) / len(data['attendance'])) * 100]) if data['attendance'] else 0, 1),
                "leaveRequests": len(data['leaves']),
                "noticesPosted": len(data['notices'])
            }
        }
        
        analytics = {
            "attendanceTrend": attendance_trend,
            "leaveRequestsByType": leave_requests_by_type,
            "coursePerformance": course_performance,
            "monthlyStats": monthly_stats
        }
        
        return jsonify({
            "success": True,
            "data": analytics
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@dashboard_bp.route('/api/dashboard/quick-actions', methods=['GET'])
def get_quick_actions():
    """Get available quick actions for the dashboard"""
    try:
        quick_actions = [
            {
                "id": "mark_attendance",
                "title": "Mark Attendance",
                "description": "Record today's attendance",
                "icon": "Users",
                "url": "/attendance/mark",
                "color": "blue"
            },
            {
                "id": "review_leaves",
                "title": "Review Leaves",
                "description": "Approve pending requests",
                "icon": "Calendar",
                "url": "/leave/pending",
                "color": "green"
            },
            {
                "id": "post_notice",
                "title": "Post Notice",
                "description": "Create new announcement",
                "icon": "Bell",
                "url": "/notices/create",
                "color": "purple"
            },
            {
                "id": "view_grades",
                "title": "View Grades",
                "description": "Check student performance",
                "icon": "BarChart3",
                "url": "/grades",
                "color": "orange"
            }
        ]
        
        return jsonify({
            "success": True,
            "data": quick_actions
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
