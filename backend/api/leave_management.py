from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any

leave_bp = Blueprint('leave_management', __name__)

# Mock data storage (in production, this would be a database)
LEAVE_DATA_FILE = 'data/leave_requests.json'

def load_leave_data():
    """Load leave request data from file"""
    if os.path.exists(LEAVE_DATA_FILE):
        try:
            with open(LEAVE_DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_leave_data(data):
    """Save leave request data to file"""
    os.makedirs(os.path.dirname(LEAVE_DATA_FILE), exist_ok=True)
    with open(LEAVE_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@leave_bp.route('/api/leave/requests', methods=['GET'])
def get_leave_requests():
    """Get all leave requests"""
    try:
        # For now, return mock data
        # In production, this would query the database
        requests = [
            {
                "id": "1",
                "studentId": "STU001",
                "studentName": "Alice Johnson",
                "studentRollNumber": "CS001",
                "course": "CS101",
                "leaveType": "sick",
                "startDate": "2024-01-20",
                "endDate": "2024-01-22",
                "duration": 3,
                "reason": "Fever and flu symptoms. Doctor recommended rest.",
                "status": "pending",
                "submittedAt": "2024-01-19T10:30:00Z",
                "attachments": ["medical_certificate.pdf"]
            },
            {
                "id": "2",
                "studentId": "STU002",
                "studentName": "Bob Smith",
                "studentRollNumber": "CS002",
                "course": "CS101",
                "leaveType": "personal",
                "startDate": "2024-01-25",
                "endDate": "2024-01-25",
                "duration": 1,
                "reason": "Family emergency - need to attend to urgent matter.",
                "status": "pending",
                "submittedAt": "2024-01-24T14:20:00Z"
            },
            {
                "id": "3",
                "studentId": "STU003",
                "studentName": "Carol Davis",
                "studentRollNumber": "CS003",
                "course": "CS201",
                "leaveType": "academic",
                "startDate": "2024-01-18",
                "endDate": "2024-01-18",
                "duration": 1,
                "reason": "Attending academic conference for research presentation.",
                "status": "approved",
                "submittedAt": "2024-01-15T09:15:00Z",
                "reviewedAt": "2024-01-16T11:30:00Z",
                "reviewedBy": "Dr. Sarah Johnson",
                "remarks": "Approved for academic development."
            },
            {
                "id": "4",
                "studentId": "STU004",
                "studentName": "David Wilson",
                "studentRollNumber": "CS004",
                "course": "CS201",
                "leaveType": "personal",
                "startDate": "2024-01-12",
                "endDate": "2024-01-15",
                "duration": 4,
                "reason": "Personal family event.",
                "status": "rejected",
                "submittedAt": "2024-01-10T16:45:00Z",
                "reviewedAt": "2024-01-11T10:20:00Z",
                "reviewedBy": "Dr. Sarah Johnson",
                "remarks": "Duration too long for personal leave. Please provide more details."
            }
        ]
        
        return jsonify({
            "success": True,
            "data": requests
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@leave_bp.route('/api/leave/request', methods=['POST'])
def create_leave_request():
    """Create a new leave request"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['studentId', 'leaveType', 'startDate', 'endDate', 'reason']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Calculate duration
        start_date = datetime.strptime(data['startDate'], '%Y-%m-%d')
        end_date = datetime.strptime(data['endDate'], '%Y-%m-%d')
        duration = (end_date - start_date).days + 1
        
        # Create new request
        new_request = {
            "id": str(len(load_leave_data()) + 1),
            "studentId": data['studentId'],
            "studentName": data.get('studentName', 'Unknown Student'),
            "studentRollNumber": data.get('studentRollNumber', ''),
            "course": data.get('course', ''),
            "leaveType": data['leaveType'],
            "startDate": data['startDate'],
            "endDate": data['endDate'],
            "duration": duration,
            "reason": data['reason'],
            "status": "pending",
            "submittedAt": datetime.now().isoformat() + 'Z',
            "attachments": data.get('attachments', [])
        }
        
        # In production, this would save to database
        # For now, we'll just return success
        return jsonify({
            "success": True,
            "data": new_request,
            "message": "Leave request submitted successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@leave_bp.route('/api/leave/request/<request_id>/approve', methods=['POST'])
def approve_leave_request(request_id):
    """Approve a leave request"""
    try:
        data = request.get_json()
        remarks = data.get('remarks', '')
        
        # In production, this would update the database
        # For now, we'll just return success
        return jsonify({
            "success": True,
            "message": "Leave request approved successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@leave_bp.route('/api/leave/request/<request_id>/reject', methods=['POST'])
def reject_leave_request(request_id):
    """Reject a leave request"""
    try:
        data = request.get_json()
        remarks = data.get('remarks', '')
        
        # In production, this would update the database
        # For now, we'll just return success
        return jsonify({
            "success": True,
            "message": "Leave request rejected"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@leave_bp.route('/api/leave/stats', methods=['GET'])
def get_leave_stats():
    """Get leave management statistics"""
    try:
        # Mock stats
        stats = {
            "totalRequests": 24,
            "pendingRequests": 8,
            "approvedRequests": 14,
            "rejectedRequests": 2,
            "averageProcessingTime": 1.5
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

@leave_bp.route('/api/leave/policies', methods=['GET'])
def get_leave_policies():
    """Get leave policies"""
    try:
        policies = [
            {
                "type": "sick",
                "maxDays": 5,
                "requiresDocumentation": True,
                "description": "Medical leave for illness or injury"
            },
            {
                "type": "personal",
                "maxDays": 3,
                "requiresDocumentation": False,
                "description": "Personal leave for family matters or personal issues"
            },
            {
                "type": "emergency",
                "maxDays": 7,
                "requiresDocumentation": True,
                "description": "Emergency leave for urgent family situations"
            },
            {
                "type": "academic",
                "maxDays": 10,
                "requiresDocumentation": True,
                "description": "Academic leave for conferences, research, or academic activities"
            }
        ]
        
        return jsonify({
            "success": True,
            "data": policies
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
