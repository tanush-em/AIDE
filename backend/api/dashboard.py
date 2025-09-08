from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Mock dashboard stats
        stats = {
            "totalStudents": 156,
            "attendanceRate": 87.5,
            "pendingLeaves": 8,
            "upcomingEvents": 3,
            "recentActivities": [
                {
                    "id": "1",
                    "type": "attendance",
                    "title": "CS101 - Data Structures",
                    "description": "Attendance marked for 45/50 students",
                    "timestamp": (datetime.now() - timedelta(hours=2)).isoformat() + 'Z',
                    "status": "completed"
                },
                {
                    "id": "2",
                    "type": "leave",
                    "title": "Leave Request - John Smith",
                    "description": "Sick leave for 3 days pending approval",
                    "timestamp": (datetime.now() - timedelta(hours=4)).isoformat() + 'Z',
                    "status": "pending"
                },
                {
                    "id": "3",
                    "type": "notice",
                    "title": "Mid-term Exam Schedule",
                    "description": "Exam schedule published for all courses",
                    "timestamp": (datetime.now() - timedelta(hours=6)).isoformat() + 'Z',
                    "status": "completed"
                },
                {
                    "id": "4",
                    "type": "grade",
                    "title": "Assignment Grades Due",
                    "description": "CS201 Assignment 2 grades due tomorrow",
                    "timestamp": (datetime.now() - timedelta(hours=8)).isoformat() + 'Z',
                    "status": "overdue"
                }
            ]
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
        # Mock analytics data
        analytics = {
            "attendanceTrend": [
                {"date": "2024-01-15", "rate": 85.2},
                {"date": "2024-01-16", "rate": 87.1},
                {"date": "2024-01-17", "rate": 89.3},
                {"date": "2024-01-18", "rate": 86.7},
                {"date": "2024-01-19", "rate": 88.9}
            ],
            "leaveRequestsByType": [
                {"type": "sick", "count": 12},
                {"type": "personal", "count": 8},
                {"type": "emergency", "count": 3},
                {"type": "academic", "count": 5}
            ],
            "coursePerformance": [
                {"course": "CS101", "attendance": 89.2, "assignments": 87.5},
                {"course": "CS201", "attendance": 85.7, "assignments": 91.3},
                {"course": "CS301", "attendance": 92.1, "assignments": 88.9},
                {"course": "MATH101", "attendance": 84.6, "assignments": 85.2}
            ],
            "monthlyStats": {
                "january": {
                    "totalClasses": 45,
                    "averageAttendance": 87.3,
                    "leaveRequests": 28,
                    "noticesPosted": 12
                },
                "february": {
                    "totalClasses": 42,
                    "averageAttendance": 89.1,
                    "leaveRequests": 24,
                    "noticesPosted": 8
                }
            }
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
