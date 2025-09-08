from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import data_loader

notice_bp = Blueprint('notice_board', __name__)

def load_notice_data():
    """Load notice data from JSON file"""
    try:
        data = data_loader.load_json('notices.json')
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Error loading notice data: {e}")
        return []

def save_notice_data(data):
    """Save notice data to JSON file"""
    try:
        return data_loader.save_json('notices.json', data)
    except Exception as e:
        print(f"Error saving notice data: {e}")
        return False

@notice_bp.route('/api/notices', methods=['GET'])
def get_notices():
    """Get all notices"""
    try:
        # Load notices from JSON file
        notices = load_notice_data()
        
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
        
        # Load existing notice data
        notice_data = load_notice_data()
        
        # Create new notice
        new_notice = {
            "id": str(len(notice_data) + 1),
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
        
        # Add to notice data
        notice_data.append(new_notice)
        
        # Save back to JSON file
        if save_notice_data(notice_data):
            return jsonify({
                "success": True,
                "data": new_notice,
                "message": "Notice created successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save notice"
            }), 500
            
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
        # Load notice data from JSON file
        notice_data = load_notice_data()
        
        # Calculate stats
        total_notices = len(notice_data)
        active_notices = len([n for n in notice_data if n.get('isActive', True)])
        urgent_notices = len([n for n in notice_data if n.get('priority') == 'high'])
        
        # Count expired notices
        current_time = datetime.now()
        expired_notices = 0
        for notice in notice_data:
            if notice.get('expiresAt'):
                try:
                    expires_at = datetime.fromisoformat(notice['expiresAt'].replace('Z', '+00:00'))
                    if current_time > expires_at:
                        expired_notices += 1
                except:
                    pass
        
        stats = {
            "totalNotices": total_notices,
            "activeNotices": active_notices,
            "urgentNotices": urgent_notices,
            "expiredNotices": expired_notices
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
