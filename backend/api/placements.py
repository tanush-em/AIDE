from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import data_loader

placements_bp = Blueprint('placements', __name__)

def load_placement_data():
    """Load placement data from JSON file"""
    try:
        data = data_loader.load_json('placements.json')
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Error loading placement data: {e}")
        return []

def save_placement_data(data):
    """Save placement data to JSON file"""
    try:
        return data_loader.save_json('placements.json', data)
    except Exception as e:
        print(f"Error saving placement data: {e}")
        return False

@placements_bp.route('/api/placements', methods=['GET'])
def get_placements():
    """Get all placement drives"""
    try:
        # Load placements from JSON file
        placements = load_placement_data()
        
        return jsonify({
            "success": True,
            "data": placements
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@placements_bp.route('/api/placements', methods=['POST'])
def create_placement():
    """Create a new placement drive"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['companyName', 'jobTitle', 'jobDescription', 'location', 'salaryRange', 'driveDate', 'registrationDeadline']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Load existing placement data
        placement_data = load_placement_data()
        
        # Create new placement drive
        new_placement = {
            "id": str(len(placement_data) + 1),
            "companyName": data['companyName'],
            "jobTitle": data['jobTitle'],
            "jobDescription": data['jobDescription'],
            "requirements": data.get('requirements', []),
            "location": data['location'],
            "salaryRange": data['salaryRange'],
            "driveDate": data['driveDate'],
            "registrationDeadline": data['registrationDeadline'],
            "eligibilityCriteria": data.get('eligibilityCriteria', {
                "minCGPA": 7.0,
                "branches": ["CSE", "IT"],
                "yearOfPassing": [2024, 2025],
                "backlogs": 0
            }),
            "process": data.get('process', {
                "rounds": ["Online Test", "Technical Interview", "HR Interview"],
                "duration": "1 day"
            }),
            "contactPerson": data.get('contactPerson', {
                "name": "HR Representative",
                "email": "hr@company.com",
                "phone": "+91-0000000000"
            }),
            "status": data.get('status', 'upcoming'),
            "totalApplications": 0,
            "shortlisted": 0,
            "selected": 0,
            "createdAt": datetime.now().isoformat() + 'Z',
            "updatedAt": datetime.now().isoformat() + 'Z',
            "tags": data.get('tags', []),
            "attachments": data.get('attachments', [])
        }
        
        # Add to placement data
        placement_data.append(new_placement)
        
        # Save back to JSON file
        if save_placement_data(placement_data):
            return jsonify({
                "success": True,
                "data": new_placement,
                "message": "Placement drive created successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save placement drive"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@placements_bp.route('/api/placements/<placement_id>', methods=['PUT'])
def update_placement(placement_id):
    """Update an existing placement drive"""
    try:
        data = request.get_json()
        
        # Load existing placement data
        placement_data = load_placement_data()
        
        # Find the placement to update
        placement_index = None
        for i, placement in enumerate(placement_data):
            if placement['id'] == placement_id:
                placement_index = i
                break
        
        if placement_index is None:
            return jsonify({
                "success": False,
                "error": "Placement drive not found"
            }), 404
        
        # Update the placement with new data
        updated_placement = placement_data[placement_index].copy()
        
        # Update fields if provided
        updatable_fields = [
            'companyName', 'jobTitle', 'jobDescription', 'requirements', 'location',
            'salaryRange', 'driveDate', 'registrationDeadline', 'eligibilityCriteria',
            'process', 'contactPerson', 'status', 'tags', 'attachments'
        ]
        
        for field in updatable_fields:
            if field in data:
                updated_placement[field] = data[field]
        
        # Update timestamp
        updated_placement['updatedAt'] = datetime.now().isoformat() + 'Z'
        
        # Replace the placement in the list
        placement_data[placement_index] = updated_placement
        
        # Save back to JSON file
        if save_placement_data(placement_data):
            return jsonify({
                "success": True,
                "data": updated_placement,
                "message": "Placement drive updated successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save placement drive"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@placements_bp.route('/api/placements/<placement_id>', methods=['DELETE'])
def delete_placement(placement_id):
    """Delete a placement drive"""
    try:
        # Load existing placement data
        placement_data = load_placement_data()
        
        # Find the placement to delete
        placement_index = None
        for i, placement in enumerate(placement_data):
            if placement['id'] == placement_id:
                placement_index = i
                break
        
        if placement_index is None:
            return jsonify({
                "success": False,
                "error": "Placement drive not found"
            }), 404
        
        # Remove the placement from the list
        deleted_placement = placement_data.pop(placement_index)
        
        # Save back to JSON file
        if save_placement_data(placement_data):
            return jsonify({
                "success": True,
                "data": deleted_placement,
                "message": "Placement drive deleted successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save placement data"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@placements_bp.route('/api/placements/stats', methods=['GET'])
def get_placement_stats():
    """Get placement statistics"""
    try:
        # Load placement data from JSON file
        placement_data = load_placement_data()
        
        # Calculate stats
        total_drives = len(placement_data)
        upcoming_drives = len([p for p in placement_data if p.get('status') == 'upcoming'])
        ongoing_drives = len([p for p in placement_data if p.get('status') == 'ongoing'])
        completed_drives = len([p for p in placement_data if p.get('status') == 'completed'])
        total_applications = sum(p.get('totalApplications', 0) for p in placement_data)
        total_selected = sum(p.get('selected', 0) for p in placement_data)
        
        # Calculate average salary
        salaries = []
        for placement in placement_data:
            salary_range = placement.get('salaryRange', {})
            if salary_range and 'min' in salary_range and 'max' in salary_range:
                avg_salary = (salary_range['min'] + salary_range['max']) / 2
                salaries.append(avg_salary)
        
        average_salary = sum(salaries) / len(salaries) if salaries else 0
        
        stats = {
            "totalDrives": total_drives,
            "upcomingDrives": upcoming_drives,
            "ongoingDrives": ongoing_drives,
            "completedDrives": completed_drives,
            "totalApplications": total_applications,
            "totalSelected": total_selected,
            "averageSalary": average_salary
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
