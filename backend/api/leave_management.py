from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import data_loader

leave_bp = Blueprint('leave_management', __name__)

def load_leave_data():
    """Load leave request data from JSON file"""
    try:
        data = data_loader.load_json('leave_requests.json')
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Error loading leave data: {e}")
        return []

def save_leave_data(data):
    """Save leave request data to JSON file"""
    try:
        return data_loader.save_json('leave_requests.json', data)
    except Exception as e:
        print(f"Error saving leave data: {e}")
        return False

@leave_bp.route('/api/leave/requests', methods=['GET'])
def get_leave_requests():
    """Get all leave requests"""
    try:
        # Load leave requests from JSON file
        requests = load_leave_data()
        
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
        
        # Load existing leave data
        leave_data = load_leave_data()
        
        # Create new request
        new_request = {
            "id": str(len(leave_data) + 1),
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
            "attachments": data.get('attachments', []),
            "reviewedBy": None,
            "reviewedAt": None,
            "remarks": None
        }
        
        # Add to leave data
        leave_data.append(new_request)
        
        # Save back to JSON file
        if save_leave_data(leave_data):
            return jsonify({
                "success": True,
                "data": new_request,
                "message": "Leave request submitted successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save leave request"
            }), 500
            
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
        reviewed_by = data.get('reviewedBy', 'Dr. Sarah Johnson')
        
        # Load existing leave data
        leave_data = load_leave_data()
        
        # Find and update the request
        for request in leave_data:
            if str(request['id']) == str(request_id):
                request['status'] = 'approved'
                request['reviewedBy'] = reviewed_by
                request['reviewedAt'] = datetime.now().isoformat() + 'Z'
                request['remarks'] = remarks
                break
        else:
            return jsonify({
                "success": False,
                "error": "Leave request not found"
            }), 404
        
        # Save back to JSON file
        if save_leave_data(leave_data):
            return jsonify({
                "success": True,
                "message": "Leave request approved successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save leave request"
            }), 500
            
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
        reviewed_by = data.get('reviewedBy', 'Dr. Sarah Johnson')
        
        # Load existing leave data
        leave_data = load_leave_data()
        
        # Find and update the request
        for request in leave_data:
            if str(request['id']) == str(request_id):
                request['status'] = 'rejected'
                request['reviewedBy'] = reviewed_by
                request['reviewedAt'] = datetime.now().isoformat() + 'Z'
                request['remarks'] = remarks
                break
        else:
            return jsonify({
                "success": False,
                "error": "Leave request not found"
            }), 404
        
        # Save back to JSON file
        if save_leave_data(leave_data):
            return jsonify({
                "success": True,
                "message": "Leave request rejected"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save leave request"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@leave_bp.route('/api/leave/stats', methods=['GET'])
def get_leave_stats():
    """Get leave management statistics"""
    try:
        # Load leave data from JSON file
        leave_data = load_leave_data()
        
        # Calculate stats
        total_requests = len(leave_data)
        pending_requests = len([r for r in leave_data if r.get('status') == 'pending'])
        approved_requests = len([r for r in leave_data if r.get('status') == 'approved'])
        rejected_requests = len([r for r in leave_data if r.get('status') == 'rejected'])
        
        # Calculate average processing time (in days)
        processed_requests = [r for r in leave_data if r.get('status') in ['approved', 'rejected'] and r.get('reviewedAt')]
        if processed_requests:
            total_processing_time = 0
            for request in processed_requests:
                submitted = datetime.fromisoformat(request['submittedAt'].replace('Z', '+00:00'))
                reviewed = datetime.fromisoformat(request['reviewedAt'].replace('Z', '+00:00'))
                processing_time = (reviewed - submitted).total_seconds() / (24 * 3600)  # Convert to days
                total_processing_time += processing_time
            average_processing_time = round(total_processing_time / len(processed_requests), 1)
        else:
            average_processing_time = 0
        
        stats = {
            "totalRequests": total_requests,
            "pendingRequests": pending_requests,
            "approvedRequests": approved_requests,
            "rejectedRequests": rejected_requests,
            "averageProcessingTime": average_processing_time
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
