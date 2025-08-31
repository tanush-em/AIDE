from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/<role>/<user_id>', methods=['GET'])
@jwt_required()
def get_dashboard_data(role, user_id):
    """Get dashboard data for user (preserving existing endpoint)"""
    try:
        current_user = get_jwt_identity()
        
        # Verify user access
        if current_user['user_id'] != user_id or current_user['role'] != role:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        if role not in ['student', 'faculty', 'coordinator']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Get enhanced dashboard data
        dashboard_data = get_enhanced_dashboard_data(role, user_id)
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        logger.error(f"❌ Dashboard data error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_enhanced_dashboard_data(role: str, user_id: str) -> dict:
    """Get enhanced dashboard data with MongoDB integration"""
    try:
        # Base dashboard data (preserving existing structure)
        dashboard_data = {
            'student': {
                'timetable': [
                    {'day': 'Monday', 'time': '9:00 AM', 'subject': 'Mathematics', 'room': 'A101'},
                    {'day': 'Monday', 'time': '10:30 AM', 'subject': 'Physics', 'room': 'B202'},
                    {'day': 'Tuesday', 'time': '9:00 AM', 'subject': 'Chemistry', 'room': 'C303'},
                ],
                'attendance': {'present': 85, 'total': 100, 'percentage': 85},
                'notifications': [
                    {'type': 'warning', 'message': 'Low attendance in Mathematics', 'time': '2 hours ago'},
                    {'type': 'info', 'message': 'New study material uploaded', 'time': '1 day ago'},
                ],
                'pending_actions': [
                    {'type': 'exam', 'title': 'Mid-term Mathematics', 'deadline': '2024-01-15'},
                    {'type': 'assignment', 'title': 'Physics Lab Report', 'deadline': '2024-01-10'},
                ]
            },
            'faculty': {
                'classes_today': [
                    {'time': '9:00 AM', 'subject': 'Mathematics', 'room': 'A101', 'students': 45},
                    {'time': '2:00 PM', 'subject': 'Advanced Calculus', 'room': 'B202', 'students': 32},
                ],
                'pending_grading': [
                    {'assignment': 'Calculus Quiz 1', 'submissions': 45, 'due': '2024-01-08'},
                    {'assignment': 'Linear Algebra HW', 'submissions': 38, 'due': '2024-01-10'},
                ],
                'leave_requests': [
                    {'student': 'John Doe', 'reason': 'Medical emergency', 'dates': '2024-01-12 to 2024-01-14'},
                ]
            },
            'coordinator': {
                'upcoming_events': [
                    {'name': 'Annual Tech Fest', 'date': '2024-01-20', 'registrations': 150},
                    {'name': 'Career Fair', 'date': '2024-01-25', 'registrations': 89},
                ],
                'system_notifications': [
                    {'type': 'info', 'message': 'New faculty member joined', 'time': '1 hour ago'},
                    {'type': 'warning', 'message': 'Schedule conflict detected', 'time': '3 hours ago'},
                ]
            }
        }
        
        base_data = dashboard_data.get(role, {})
        
        # Enhance with MongoDB data if available
        try:
            if hasattr(current_app, 'mongo'):
                enhanced_data = enhance_with_mongodb_data(role, user_id, base_data)
                return enhanced_data
        except Exception as e:
            logger.warning(f"MongoDB enhancement failed: {e}")
        
        return base_data
        
    except Exception as e:
        logger.error(f"❌ Error getting dashboard data: {e}")
        return {}

def enhance_with_mongodb_data(role: str, user_id: str, base_data: dict) -> dict:
    """Enhance dashboard data with MongoDB information"""
    try:
        enhanced_data = base_data.copy()
        
        if role == 'student':
            # Get student-specific data from MongoDB
            attendance_stats = get_student_attendance_stats(user_id)
            leave_requests = get_student_leave_requests(user_id)
            event_registrations = get_student_event_registrations(user_id)
            
            enhanced_data.update({
                'attendance_stats': attendance_stats,
                'leave_requests': leave_requests,
                'event_registrations': event_registrations,
                'recent_notices': get_recent_notices(['students', 'all'])
            })
            
        elif role == 'faculty':
            # Get faculty-specific data from MongoDB
            pending_leave_requests = get_pending_leave_requests(user_id)
            class_attendance = get_class_attendance_summary(user_id)
            upcoming_events = get_faculty_events(user_id)
            
            enhanced_data.update({
                'pending_leave_requests': pending_leave_requests,
                'class_attendance': class_attendance,
                'upcoming_events': upcoming_events,
                'recent_notices': get_recent_notices(['faculty', 'all'])
            })
            
        elif role == 'coordinator':
            # Get coordinator-specific data from MongoDB
            system_stats = get_system_statistics()
            pending_approvals = get_pending_approvals()
            
            enhanced_data.update({
                'system_stats': system_stats,
                'pending_approvals': pending_approvals,
                'recent_notices': get_recent_notices(['all'])
            })
        
        return enhanced_data
        
    except Exception as e:
        logger.error(f"❌ Error enhancing with MongoDB data: {e}")
        return base_data

def get_student_attendance_stats(student_id: str) -> dict:
    """Get student attendance statistics from MongoDB"""
    try:
        if not hasattr(current_app, 'mongo'):
            return {}
        
        # Aggregate attendance data
        pipeline = [
            {'$match': {'student_id': student_id}},
            {'$group': {
                '_id': '$course_code',
                'total_sessions': {'$sum': 1},
                'present_sessions': {'$sum': {'$cond': [{'$eq': ['$status', 'present']}, 1, 0]}},
                'absent_sessions': {'$sum': {'$cond': [{'$eq': ['$status', 'absent']}, 1, 0]}},
                'late_sessions': {'$sum': {'$cond': [{'$eq': ['$status', 'late']}, 1, 0]}}
            }},
            {'$addFields': {
                'attendance_percentage': {
                    '$multiply': [
                        {'$divide': ['$present_sessions', '$total_sessions']},
                        100
                    ]
                }
            }}
        ]
        
        results = list(current_app.mongo.attendance.aggregate(pipeline))
        
        return {
            'course_stats': results,
            'overall_percentage': calculate_overall_attendance(results)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting attendance stats: {e}")
        return {}

def get_student_leave_requests(student_id: str) -> list:
    """Get student leave requests from MongoDB"""
    try:
        if not hasattr(current_app, 'mongo'):
            return []
        
        requests = list(current_app.mongo.leave_requests.find(
            {'student_id': student_id},
            {'_id': 0}
        ).sort('created_at', -1).limit(5))
        
        return requests
        
    except Exception as e:
        logger.error(f"❌ Error getting leave requests: {e}")
        return []

def get_student_event_registrations(student_id: str) -> list:
    """Get student event registrations from MongoDB"""
    try:
        if not hasattr(current_app, 'mongo'):
            return []
        
        registrations = list(current_app.mongo.event_registrations.find(
            {'student_id': student_id},
            {'_id': 0}
        ).sort('registered_at', -1).limit(5))
        
        return registrations
        
    except Exception as e:
        logger.error(f"❌ Error getting event registrations: {e}")
        return []

def get_recent_notices(target_audience: list) -> list:
    """Get recent notices from MongoDB"""
    try:
        if not hasattr(current_app, 'mongo'):
            return []
        
        notices = list(current_app.mongo.notices.find(
            {
                'target_audience': {'$in': target_audience},
                'is_active': True
            },
            {'_id': 0}
        ).sort('created_at', -1).limit(5))
        
        return notices
        
    except Exception as e:
        logger.error(f"❌ Error getting notices: {e}")
        return []

def get_pending_leave_requests(faculty_id: str) -> list:
    """Get pending leave requests for faculty approval"""
    try:
        if not hasattr(current_app, 'mongo'):
            return []
        
        requests = list(current_app.mongo.leave_requests.find(
            {'status': 'pending'},
            {'_id': 0}
        ).sort('created_at', -1).limit(10))
        
        return requests
        
    except Exception as e:
        logger.error(f"❌ Error getting pending leave requests: {e}")
        return []

def get_class_attendance_summary(faculty_id: str) -> dict:
    """Get class attendance summary for faculty"""
    try:
        if not hasattr(current_app, 'mongo'):
            return {}
        
        # Get courses taught by faculty
        pipeline = [
            {'$match': {'marked_by': faculty_id}},
            {'$group': {
                '_id': '$course_code',
                'total_sessions': {'$sum': 1},
                'avg_attendance': {'$avg': {'$cond': [{'$eq': ['$status', 'present']}, 1, 0]}}
            }}
        ]
        
        results = list(current_app.mongo.attendance.aggregate(pipeline))
        
        return {'course_summary': results}
        
    except Exception as e:
        logger.error(f"❌ Error getting class attendance: {e}")
        return {}

def get_faculty_events(faculty_id: str) -> list:
    """Get events created by faculty"""
    try:
        if not hasattr(current_app, 'mongo'):
            return []
        
        events = list(current_app.mongo.events.find(
            {'created_by': faculty_id},
            {'_id': 0}
        ).sort('start_datetime', 1).limit(5))
        
        return events
        
    except Exception as e:
        logger.error(f"❌ Error getting faculty events: {e}")
        return []

def get_system_statistics() -> dict:
    """Get system-wide statistics for coordinator"""
    try:
        if not hasattr(current_app, 'mongo'):
            return {}
        
        stats = {
            'total_students': current_app.mongo.users.count_documents({'role': 'student'}),
            'total_faculty': current_app.mongo.users.count_documents({'role': 'faculty'}),
            'pending_leave_requests': current_app.mongo.leave_requests.count_documents({'status': 'pending'}),
            'upcoming_events': current_app.mongo.events.count_documents({'status': 'upcoming'}),
            'active_notices': current_app.mongo.notices.count_documents({'is_active': True})
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Error getting system stats: {e}")
        return {}

def get_pending_approvals() -> dict:
    """Get pending approvals for coordinator"""
    try:
        if not hasattr(current_app, 'mongo'):
            return {}
        
        approvals = {
            'leave_requests': list(current_app.mongo.leave_requests.find(
                {'status': 'pending'},
                {'_id': 0}
            ).sort('created_at', -1).limit(5)),
            'events': list(current_app.mongo.events.find(
                {'status': 'pending'},
                {'_id': 0}
            ).sort('created_at', -1).limit(5))
        }
        
        return approvals
        
    except Exception as e:
        logger.error(f"❌ Error getting pending approvals: {e}")
        return {}

def calculate_overall_attendance(course_stats: list) -> float:
    """Calculate overall attendance percentage"""
    try:
        if not course_stats:
            return 0.0
        
        total_sessions = sum(course['total_sessions'] for course in course_stats)
        total_present = sum(course['present_sessions'] for course in course_stats)
        
        if total_sessions == 0:
            return 0.0
        
        return round((total_present / total_sessions) * 100, 2)
        
    except Exception as e:
        logger.error(f"❌ Error calculating overall attendance: {e}")
        return 0.0
