from flask import Blueprint, request, jsonify
from datetime import datetime
import requests
import os
from typing import Dict, Any

question_paper_bp = Blueprint('question_paper', __name__)

# Configuration for the external question paper application
QUESTION_PAPER_URL = "http://localhost:5890"
QUESTION_PAPER_TIMEOUT = 5  # seconds

def check_question_paper_service():
    """Check if the question paper service is running"""
    try:
        response = requests.get(QUESTION_PAPER_URL, timeout=QUESTION_PAPER_TIMEOUT)
        return {
            "is_running": True,
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds()
        }
    except requests.exceptions.RequestException as e:
        return {
            "is_running": False,
            "error": str(e)
        }

@question_paper_bp.route('/api/question-paper/status', methods=['GET'])
def get_question_paper_status():
    """Get the status of the question paper generator service"""
    try:
        status = check_question_paper_service()
        
        return jsonify({
            "success": True,
            "data": {
                "service_url": QUESTION_PAPER_URL,
                "is_running": status["is_running"],
                "last_checked": datetime.now().isoformat() + 'Z',
                "details": status
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@question_paper_bp.route('/api/question-paper/info', methods=['GET'])
def get_question_paper_info():
    """Get information about the question paper generator"""
    try:
        status = check_question_paper_service()
        
        info = {
            "name": "Question Paper Generator",
            "description": "External application for generating and managing question papers",
            "url": QUESTION_PAPER_URL,
            "status": "online" if status["is_running"] else "offline",
            "features": [
                "Create question papers from templates",
                "Manage question banks",
                "Generate multiple question sets",
                "Export to PDF and Word formats",
                "Course-specific question papers",
                "Difficulty level management"
            ],
            "supported_formats": ["PDF", "DOCX", "TXT"],
            "last_updated": datetime.now().isoformat() + 'Z'
        }
        
        return jsonify({
            "success": True,
            "data": info
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@question_paper_bp.route('/api/question-paper/redirect', methods=['POST'])
def redirect_to_question_paper():
    """Get redirect information for the question paper generator"""
    try:
        data = request.get_json() or {}
        course_code = data.get('course_code', '')
        paper_type = data.get('paper_type', 'general')
        
        # Build redirect URL with parameters
        redirect_url = QUESTION_PAPER_URL
        params = []
        
        if course_code:
            params.append(f"course={course_code}")
        if paper_type:
            params.append(f"type={paper_type}")
        
        if params:
            redirect_url += "?" + "&".join(params)
        
        return jsonify({
            "success": True,
            "data": {
                "redirect_url": redirect_url,
                "course_code": course_code,
                "paper_type": paper_type,
                "timestamp": datetime.now().isoformat() + 'Z'
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@question_paper_bp.route('/api/question-paper/courses', methods=['GET'])
def get_available_courses():
    """Get list of courses that can be used for question paper generation"""
    try:
        # This would typically come from your courses data
        # For now, we'll return a static list based on the sample data
        courses = [
            {
                "code": "CS101",
                "name": "Data Structures",
                "department": "Computer Science",
                "instructor": "Dr. Sarah Johnson"
            },
            {
                "code": "CS201",
                "name": "Algorithms",
                "department": "Computer Science",
                "instructor": "Dr. Michael Chen"
            },
            {
                "code": "CS301",
                "name": "Database Systems",
                "department": "Computer Science",
                "instructor": "Dr. Emily Davis"
            },
            {
                "code": "MATH101",
                "name": "Calculus I",
                "department": "Mathematics",
                "instructor": "Dr. Robert Wilson"
            },
            {
                "code": "PHYS101",
                "name": "Physics I",
                "department": "Physics",
                "instructor": "Dr. Lisa Anderson"
            }
        ]
        
        return jsonify({
            "success": True,
            "data": courses
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
