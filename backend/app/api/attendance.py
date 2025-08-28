from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta
from bson import ObjectId
from ..models.attendance import AttendanceCreate, AttendanceUpdate, AttendanceResponse, AttendanceStats, BulkAttendanceCreate
from ..rag.policy_manager import PolicyManager

logger = logging.getLogger(__name__)

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/mark', methods=['POST'])
@jwt_required()
def mark_attendance():
    """Mark attendance for a single student"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        try:
            attendance_data = AttendanceCreate(**data)
        except Exception as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        
        # Check if user is faculty
        if current_user['role'] != 'faculty':
            return jsonify({'error': 'Only faculty can mark attendance'}), 403
        
        # Create attendance record
        attendance_record = {
            'student_id': attendance_data.student_id,
            'course_code': attendance_data.course_code,
            'course_name': attendance_data.course_name,
            'date': attendance_data.date,
            'status': attendance_data.status.value,
            'marked_by': current_user['user_id'],
            'session_type': attendance_data.session_type.value,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Insert into MongoDB
        result = current_app.mongo.attendance.insert_one(attendance_record)
        
        # Get the created record
        created_record = current_app.mongo.attendance.find_one({'_id': result.inserted_id})
        created_record['id'] = str(created_record['_id'])
        del created_record['_id']
        
        logger.info(f"✅ Attendance marked for student {attendance_data.student_id} by {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Attendance marked successfully',
            'attendance': created_record,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Attendance marking error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/bulk-mark', methods=['POST'])
@jwt_required()
def bulk_mark_attendance():
    """Mark attendance for multiple students"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        try:
            bulk_data = BulkAttendanceCreate(**data)
        except Exception as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        
        # Check if user is faculty
        if current_user['role'] != 'faculty':
            return jsonify({'error': 'Only faculty can mark attendance'}), 403
        
        # Process attendance records
        attendance_records = []
        for record in bulk_data.attendance_records:
            attendance_record = {
                'student_id': record['student_id'],
                'course_code': bulk_data.course_code,
                'course_name': bulk_data.course_name,
                'date': bulk_data.date,
                'status': record.get('status', 'present'),
                'marked_by': current_user['user_id'],
                'session_type': bulk_data.session_type.value,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            attendance_records.append(attendance_record)
        
        # Insert into MongoDB
        if attendance_records:
            result = current_app.mongo.attendance.insert_many(attendance_records)
            
            logger.info(f"✅ Bulk attendance marked for {len(attendance_records)} students by {current_user['user_id']}")
            
            return jsonify({
                'success': True,
                'message': f'Attendance marked for {len(attendance_records)} students',
                'inserted_count': len(result.inserted_ids),
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return jsonify({'error': 'No attendance records provided'}), 400
        
    except Exception as e:
        logger.error(f"❌ Bulk attendance marking error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/view/<student_id>', methods=['GET'])
@jwt_required()
def view_attendance(student_id):
    """View attendance for a student"""
    try:
        current_user = get_jwt_identity()
        
        # Check permissions
        if current_user['role'] == 'student' and current_user['user_id'] != student_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get query parameters
        course_code = request.args.get('course_code')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = int(request.args.get('limit', 50))
        
        # Build query
        query = {'student_id': student_id}
        if course_code:
            query['course_code'] = course_code
        if start_date and end_date:
            query['date'] = {
                '$gte': datetime.fromisoformat(start_date),
                '$lte': datetime.fromisoformat(end_date)
            }
        
        # Get attendance records
        attendance_records = list(current_app.mongo.attendance.find(
            query,
            {'_id': 0}
        ).sort('date', -1).limit(limit))
        
        # Calculate statistics
        stats = calculate_attendance_stats(student_id, course_code, start_date, end_date)
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'attendance_records': attendance_records,
            'statistics': stats,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Attendance viewing error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/stats/<student_id>', methods=['GET'])
@jwt_required()
def get_attendance_stats(student_id):
    """Get detailed attendance statistics for a student"""
    try:
        current_user = get_jwt_identity()
        
        # Check permissions
        if current_user['role'] == 'student' and current_user['user_id'] != student_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get query parameters
        course_code = request.args.get('course_code')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Calculate statistics
        stats = calculate_attendance_stats(student_id, course_code, start_date, end_date)
        
        # Validate against policies
        policy_manager = PolicyManager()
        validation = policy_manager.validate_attendance_requirements({
            'attendance_percentage': stats['overall_percentage'],
            'session_type': 'lecture'  # Default, can be enhanced
        })
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'statistics': stats,
            'policy_validation': validation,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Attendance stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/course/<course_code>', methods=['GET'])
@jwt_required()
def get_course_attendance(course_code):
    """Get attendance for a specific course"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is faculty
        if current_user['role'] != 'faculty':
            return jsonify({'error': 'Only faculty can view course attendance'}), 403
        
        # Get query parameters
        date = request.args.get('date')
        session_type = request.args.get('session_type')
        
        # Build query
        query = {'course_code': course_code}
        if date:
            query['date'] = datetime.fromisoformat(date)
        if session_type:
            query['session_type'] = session_type
        
        # Get attendance records
        attendance_records = list(current_app.mongo.attendance.find(
            query,
            {'_id': 0}
        ).sort('date', -1))
        
        # Calculate course statistics
        course_stats = calculate_course_attendance_stats(course_code, date, session_type)
        
        return jsonify({
            'success': True,
            'course_code': course_code,
            'attendance_records': attendance_records,
            'course_statistics': course_stats,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Course attendance error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/update/<attendance_id>', methods=['PUT'])
@jwt_required()
def update_attendance(attendance_id):
    """Update attendance record"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Check if user is faculty
        if current_user['role'] != 'faculty':
            return jsonify({'error': 'Only faculty can update attendance'}), 403
        
        # Validate input
        try:
            update_data = AttendanceUpdate(**data)
        except Exception as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        
        # Build update document
        update_doc = {'updated_at': datetime.utcnow()}
        if update_data.status:
            update_doc['status'] = update_data.status.value
        if update_data.session_type:
            update_doc['session_type'] = update_data.session_type.value
        
        # Update in MongoDB
        result = current_app.mongo.attendance.update_one(
            {'_id': ObjectId(attendance_id)},
            {'$set': update_doc}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Attendance record not found'}), 404
        
        logger.info(f"✅ Attendance updated {attendance_id} by {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Attendance updated successfully',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Attendance update error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@attendance_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_attendance_alerts():
    """Get attendance alerts for low attendance"""
    try:
        current_user = get_jwt_identity()
        
        # Get query parameters
        threshold = float(request.args.get('threshold', 75.0))
        days_back = int(request.args.get('days_back', 30))
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # Get students with low attendance
        pipeline = [
            {
                '$match': {
                    'date': {'$gte': start_date, '$lte': end_date}
                }
            },
            {
                '$group': {
                    '_id': {
                        'student_id': '$student_id',
                        'course_code': '$course_code'
                    },
                    'total_sessions': {'$sum': 1},
                    'present_sessions': {'$sum': {'$cond': [{'$eq': ['$status', 'present']}, 1, 0]}},
                    'absent_sessions': {'$sum': {'$cond': [{'$eq': ['$status', 'absent']}, 1, 0]}},
                    'late_sessions': {'$sum': {'$cond': [{'$eq': ['$status', 'late']}, 1, 0]}}
                }
            },
            {
                '$addFields': {
                    'attendance_percentage': {
                        '$multiply': [
                            {'$divide': ['$present_sessions', '$total_sessions']},
                            100
                        ]
                    }
                }
            },
            {
                '$match': {
                    'attendance_percentage': {'$lt': threshold}
                }
            },
            {
                '$sort': {'attendance_percentage': 1}
            }
        ]
        
        alerts = list(current_app.mongo.attendance.aggregate(pipeline))
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'threshold': threshold,
            'days_back': days_back,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Attendance alerts error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def calculate_attendance_stats(student_id, course_code=None, start_date=None, end_date=None):
    """Calculate attendance statistics for a student"""
    try:
        # Build match query
        match_query = {'student_id': student_id}
        if course_code:
            match_query['course_code'] = course_code
        if start_date and end_date:
            match_query['date'] = {
                '$gte': datetime.fromisoformat(start_date),
                '$lte': datetime.fromisoformat(end_date)
            }
        
        pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': '$course_code',
                'total_sessions': {'$sum': 1},
                'present_sessions': {'$sum': {'$cond': [{'$eq': ['$status', 'present']}, 1, 0]}},
                'absent_sessions': {'$sum': {'$cond': [{'$eq': ['$status', 'absent']}, 1, 0]}},
                'late_sessions': {'$sum': {'$cond': [{'$eq': ['$status', 'late']}, 1, 0]}},
                'excused_sessions': {'$sum': {'$cond': [{'$eq': ['$status', 'excused']}, 1, 0]}}
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
        
        # Calculate overall statistics
        total_sessions = sum(course['total_sessions'] for course in results)
        total_present = sum(course['present_sessions'] for course in results)
        overall_percentage = (total_present / total_sessions * 100) if total_sessions > 0 else 0
        
        return {
            'course_stats': results,
            'overall_percentage': round(overall_percentage, 2),
            'total_sessions': total_sessions,
            'total_present': total_present,
            'total_absent': sum(course['absent_sessions'] for course in results),
            'total_late': sum(course['late_sessions'] for course in results),
            'total_excused': sum(course['excused_sessions'] for course in results)
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating attendance stats: {e}")
        return {}

def calculate_course_attendance_stats(course_code, date=None, session_type=None):
    """Calculate attendance statistics for a course"""
    try:
        # Build match query
        match_query = {'course_code': course_code}
        if date:
            match_query['date'] = datetime.fromisoformat(date)
        if session_type:
            match_query['session_type'] = session_type
        
        pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': '$student_id',
                'total_sessions': {'$sum': 1},
                'present_sessions': {'$sum': {'$cond': [{'$eq': ['$status', 'present']}, 1, 0]}},
                'attendance_percentage': {
                    '$multiply': [
                        {'$divide': [
                            {'$sum': {'$cond': [{'$eq': ['$status', 'present']}, 1, 0]}},
                            {'$sum': 1}
                        ]},
                        100
                    ]
                }
            }},
            {'$sort': {'attendance_percentage': 1}}
        ]
        
        results = list(current_app.mongo.attendance.aggregate(pipeline))
        
        if not results:
            return {}
        
        # Calculate course-level statistics
        total_students = len(results)
        avg_attendance = sum(student['attendance_percentage'] for student in results) / total_students
        low_attendance_students = len([s for s in results if s['attendance_percentage'] < 75])
        
        return {
            'total_students': total_students,
            'average_attendance': round(avg_attendance, 2),
            'low_attendance_students': low_attendance_students,
            'student_details': results
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating course attendance stats: {e}")
        return {}
