from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any

notice_bp = Blueprint('notice_board', __name__)

# Mock data storage (in production, this would be a database)
NOTICE_DATA_FILE = 'data/notices.json'

def load_notice_data():
    """Load notice data from file"""
    if os.path.exists(NOTICE_DATA_FILE):
        try:
            with open(NOTICE_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_notice_data(data):
    """Save notice data to file"""
    os.makedirs(os.path.dirname(NOTICE_DATA_FILE), exist_ok=True)
    with open(NOTICE_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@notice_bp.route('/api/notices', methods=['GET'])
def get_notices():
    """Get all notices"""
    try:
        # For now, return mock data
        # In production, this would query the database
        notices = [
            {
                "id": "1",
                "title": "Mid-term Exam Schedule Released",
                "content": "The mid-term examination schedule for all courses has been published. Please check the academic calendar for detailed timings and venues. Students are advised to arrive 15 minutes before the scheduled time.",
                "type": "announcement",
                "priority": "high",
                "targetAudience": "students",
                "author": "Dr. Sarah Johnson",
                "authorId": "FAC001",
                "createdAt": "2024-01-15T09:00:00Z",
                "updatedAt": "2024-01-15T09:00:00Z",
                "expiresAt": "2024-02-15T23:59:59Z",
                "isActive": True,
                "readBy": ["STU001", "STU002", "STU003"],
                "tags": ["exams", "schedule", "academic"]
            },
            {
                "id": "2",
                "title": "Library Maintenance - Temporary Closure",
                "content": "The main library will be closed for maintenance from January 20-22, 2024. Alternative study spaces are available in the computer labs and study halls. Online resources remain accessible.",
                "type": "urgent",
                "priority": "high",
                "targetAudience": "all",
                "author": "Library Administration",
                "authorId": "LIB001",
                "createdAt": "2024-01-18T14:30:00Z",
                "updatedAt": "2024-01-18T14:30:00Z",
                "expiresAt": "2024-01-25T23:59:59Z",
                "isActive": True,
                "readBy": ["STU001", "STU004"],
                "tags": ["library", "maintenance", "closure"]
            },
            {
                "id": "3",
                "title": "Assignment Submission Deadline Reminder",
                "content": "This is a reminder that CS201 Assignment 2 is due tomorrow (January 20, 2024) by 11:59 PM. Late submissions will incur a penalty of 10% per day.",
                "type": "reminder",
                "priority": "medium",
                "targetAudience": "specific_course",
                "course": "CS201",
                "author": "Dr. Michael Chen",
                "authorId": "FAC002",
                "createdAt": "2024-01-19T10:15:00Z",
                "updatedAt": "2024-01-19T10:15:00Z",
                "expiresAt": "2024-01-21T23:59:59Z",
                "isActive": True,
                "readBy": ["STU002", "STU003"],
                "tags": ["assignment", "deadline", "CS201"]
            },
            {
                "id": "4",
                "title": "Faculty Meeting - Next Week",
                "content": "Monthly faculty meeting scheduled for January 25, 2024 at 2:00 PM in Conference Room A. Agenda includes curriculum updates and student performance review.",
                "type": "announcement",
                "priority": "medium",
                "targetAudience": "faculty",
                "author": "Dr. Sarah Johnson",
                "authorId": "FAC001",
                "createdAt": "2024-01-16T11:00:00Z",
                "updatedAt": "2024-01-16T11:00:00Z",
                "expiresAt": "2024-01-26T23:59:59Z",
                "isActive": True,
                "readBy": ["FAC002", "FAC003"],
                "tags": ["meeting", "faculty", "curriculum"]
            },
            {
                "id": "5",
                "title": "Student Feedback Survey",
                "content": "We value your feedback! Please take a few minutes to complete the course evaluation survey. Your input helps us improve the learning experience.",
                "type": "general",
                "priority": "low",
                "targetAudience": "students",
                "author": "Academic Affairs",
                "authorId": "ADM001",
                "createdAt": "2024-01-10T16:00:00Z",
                "updatedAt": "2024-01-10T16:00:00Z",
                "expiresAt": "2024-01-31T23:59:59Z",
                "isActive": True,
                "readBy": ["STU001", "STU002", "STU003", "STU004"],
                "tags": ["feedback", "survey", "evaluation"]
            }
        ]
        
        return jsonify({
            "success": True,
            "data": notices
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@notice_bp.route('/api/notices', methods=['POST'])
def create_notice():
    """Create a new notice"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'content', 'type', 'priority', 'targetAudience']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Create new notice
        new_notice = {
            "id": str(len(load_notice_data()) + 1),
            "title": data['title'],
            "content": data['content'],
            "type": data['type'],
            "priority": data['priority'],
            "targetAudience": data['targetAudience'],
            "course": data.get('course'),
            "author": data.get('author', 'Dr. Sarah Johnson'),
            "authorId": data.get('authorId', 'FAC001'),
            "createdAt": datetime.now().isoformat() + 'Z',
            "updatedAt": datetime.now().isoformat() + 'Z',
            "expiresAt": data.get('expiresAt'),
            "isActive": True,
            "readBy": [],
            "tags": data.get('tags', []),
            "attachments": data.get('attachments', [])
        }
        
        # In production, this would save to database
        # For now, we'll just return success
        return jsonify({
            "success": True,
            "data": new_notice,
            "message": "Notice created successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@notice_bp.route('/api/notices/<notice_id>', methods=['PUT'])
def update_notice(notice_id):
    """Update an existing notice"""
    try:
        data = request.get_json()
        
        # In production, this would update the database
        # For now, we'll just return success
        return jsonify({
            "success": True,
            "message": "Notice updated successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@notice_bp.route('/api/notices/<notice_id>', methods=['DELETE'])
def delete_notice(notice_id):
    """Delete a notice"""
    try:
        # In production, this would delete from database
        # For now, we'll just return success
        return jsonify({
            "success": True,
            "message": "Notice deleted successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@notice_bp.route('/api/notices/<notice_id>/read', methods=['POST'])
def mark_notice_read(notice_id):
    """Mark a notice as read by a user"""
    try:
        data = request.get_json()
        user_id = data.get('userId')
        
        if not user_id:
            return jsonify({
                "success": False,
                "error": "User ID is required"
            }), 400
        
        # In production, this would update the database
        # For now, we'll just return success
        return jsonify({
            "success": True,
            "message": "Notice marked as read"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@notice_bp.route('/api/notices/stats', methods=['GET'])
def get_notice_stats():
    """Get notice board statistics"""
    try:
        # Mock stats
        stats = {
            "totalNotices": 15,
            "activeNotices": 12,
            "urgentNotices": 3,
            "expiredNotices": 3
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
