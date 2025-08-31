from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta
from bson import ObjectId
import uuid
from ..models.leave_request import LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse, LeaveBalance, LeaveStats
from ..rag.policy_manager import PolicyManager

logger = logging.getLogger(__name__)

leaves_bp = Blueprint('leaves', __name__)

@leaves_bp.route('/request', methods=['POST'])
@jwt_required()
def create_leave_request():
    """Create a new leave request"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        try:
            leave_data = LeaveRequestCreate(**data)
        except Exception as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        
        # Check if user is student
        if current_user['role'] != 'student':
            return jsonify({'error': 'Only students can create leave requests'}), 403
        
        # Check if student is creating request for themselves
        if current_user['user_id'] != leave_data.student_id:
            return jsonify({'error': 'Students can only create leave requests for themselves'}), 403
        
        # Validate against policies
        policy_manager = PolicyManager()
        validation = policy_manager.validate_leave_request({
            'start_date': leave_data.start_date.isoformat(),
            'end_date': leave_data.end_date.isoformat(),
            'leave_type': leave_data.leave_type.value
        })
        
        if not validation.get('valid', False):
            return jsonify({
                'error': 'Leave request validation failed',
                'details': validation
            }), 400
        
        # Generate request ID
        request_id = f"LR{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # Create leave request
        leave_request = {
            'request_id': request_id,
            'student_id': leave_data.student_id,
            'start_date': leave_data.start_date,
            'end_date': leave_data.end_date,
            'reason': leave_data.reason,
            'leave_type': leave_data.leave_type.value,
            'status': 'pending',
            'supporting_documents': leave_data.supporting_documents or [],
            'faculty_remarks': '',
            'reviewed_by': None,
            'created_at': datetime.utcnow(),
            'reviewed_at': None
        }
        
        # Check for auto-approval
        if validation.get('auto_approve', False):
            leave_request['status'] = 'approved'
            leave_request['reviewed_by'] = 'system'
            leave_request['reviewed_at'] = datetime.utcnow()
            leave_request['faculty_remarks'] = 'Auto-approved based on policy'
        
        # Insert into MongoDB
        result = current_app.mongo.leave_requests.insert_one(leave_request)
        
        # Get the created record
        created_record = current_app.mongo.leave_requests.find_one({'_id': result.inserted_id})
        created_record['id'] = str(created_record['_id'])
        del created_record['_id']
        
        logger.info(f"✅ Leave request created {request_id} by student {leave_data.student_id}")
        
        return jsonify({
            'success': True,
            'message': 'Leave request created successfully',
            'leave_request': created_record,
            'validation': validation,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Leave request error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@leaves_bp.route('/approve/<request_id>', methods=['POST'])
@jwt_required()
def approve_leave_request(request_id):
    """Approve or reject a leave request"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Check if user is faculty
        if current_user['role'] != 'faculty':
            return jsonify({'error': 'Only faculty can approve leave requests'}), 403
        
        # Get leave request
        leave_request = current_app.mongo.leave_requests.find_one({'request_id': request_id})
        if not leave_request:
            return jsonify({'error': 'Leave request not found'}), 404
        
        # Check if already processed
        if leave_request['status'] != 'pending':
            return jsonify({'error': f'Leave request already {leave_request["status"]}'}), 400
        
        # Validate action
        action = data.get('action', '').lower()
        if action not in ['approve', 'reject']:
            return jsonify({'error': 'Invalid action. Must be "approve" or "reject"'}), 400
        
        # Get remarks
        remarks = data.get('remarks', '')
        
        # Update leave request
        update_data = {
            'status': 'approved' if action == 'approve' else 'rejected',
            'reviewed_by': current_user['user_id'],
            'reviewed_at': datetime.utcnow(),
            'faculty_remarks': remarks
        }
        
        result = current_app.mongo.leave_requests.update_one(
            {'request_id': request_id},
            {'$set': update_data}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Failed to update leave request'}), 500
        
        logger.info(f"✅ Leave request {request_id} {action}d by {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': f'Leave request {action}d successfully',
            'request_id': request_id,
            'action': action,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Leave approval error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@leaves_bp.route('/view/<student_id>', methods=['GET'])
@jwt_required()
def view_leave_requests(student_id):
    """View leave requests for a student"""
    try:
        current_user = get_jwt_identity()
        
        # Check permissions
        if current_user['role'] == 'student' and current_user['user_id'] != student_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get query parameters
        status = request.args.get('status')
        leave_type = request.args.get('leave_type')
        limit = int(request.args.get('limit', 50))
        
        # Build query
        query = {'student_id': student_id}
        if status:
            query['status'] = status
        if leave_type:
            query['leave_type'] = leave_type
        
        # Get leave requests
        leave_requests = list(current_app.mongo.leave_requests.find(
            query,
            {'_id': 0}
        ).sort('created_at', -1).limit(limit))
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'leave_requests': leave_requests,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Leave requests viewing error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@leaves_bp.route('/pending', methods=['GET'])
@jwt_required()
def get_pending_leave_requests():
    """Get pending leave requests for faculty approval"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is faculty
        if current_user['role'] != 'faculty':
            return jsonify({'error': 'Only faculty can view pending requests'}), 403
        
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        
        # Get pending requests
        pending_requests = list(current_app.mongo.leave_requests.find(
            {'status': 'pending'},
            {'_id': 0}
        ).sort('created_at', -1).limit(limit))
        
        return jsonify({
            'success': True,
            'pending_requests': pending_requests,
            'count': len(pending_requests),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Pending leave requests error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@leaves_bp.route('/balance/<student_id>', methods=['GET'])
@jwt_required()
def get_leave_balance(student_id):
    """Get leave balance for a student"""
    try:
        current_user = get_jwt_identity()
        
        # Check permissions
        if current_user['role'] == 'student' and current_user['user_id'] != student_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get leave balance
        balance = calculate_leave_balance(student_id)
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'leave_balance': balance,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Leave balance error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@leaves_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_leave_statistics():
    """Get leave request statistics"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build match query
        match_query = {}
        if start_date and end_date:
            match_query['created_at'] = {
                '$gte': datetime.fromisoformat(start_date),
                '$lte': datetime.fromisoformat(end_date)
            }
        
        # Calculate statistics
        pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        status_stats = list(current_app.mongo.leave_requests.aggregate(pipeline))
        
        # Calculate by leave type
        type_pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': '$leave_type',
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        type_stats = list(current_app.mongo.leave_requests.aggregate(type_pipeline))
        
        # Calculate average processing time
        processing_pipeline = [
            {'$match': {'reviewed_at': {'$exists': True}}},
            {'$addFields': {
                'processing_time': {
                    '$divide': [
                        {'$subtract': ['$reviewed_at', '$created_at']},
                        1000 * 60 * 60  # Convert to hours
                    ]
                }
            }},
            {'$group': {
                '_id': None,
                'avg_processing_time': {'$avg': '$processing_time'},
                'min_processing_time': {'$min': '$processing_time'},
                'max_processing_time': {'$max': '$processing_time'}
            }}
        ]
        
        processing_stats = list(current_app.mongo.leave_requests.aggregate(processing_pipeline))
        
        return jsonify({
            'success': True,
            'statistics': {
                'by_status': status_stats,
                'by_type': type_stats,
                'processing_time': processing_stats[0] if processing_stats else {}
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Leave statistics error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@leaves_bp.route('/update/<request_id>', methods=['PUT'])
@jwt_required()
def update_leave_request(request_id):
    """Update a leave request (only for pending requests)"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Get leave request
        leave_request = current_app.mongo.leave_requests.find_one({'request_id': request_id})
        if not leave_request:
            return jsonify({'error': 'Leave request not found'}), 404
        
        # Check if user owns the request or is faculty
        if (current_user['role'] == 'student' and 
            current_user['user_id'] != leave_request['student_id']):
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Check if request can be updated
        if leave_request['status'] != 'pending':
            return jsonify({'error': 'Only pending requests can be updated'}), 400
        
        # Validate input
        try:
            update_data = LeaveRequestUpdate(**data)
        except Exception as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        
        # Build update document
        update_doc = {}
        if update_data.start_date:
            update_doc['start_date'] = update_data.start_date
        if update_data.end_date:
            update_doc['end_date'] = update_data.end_date
        if update_data.reason:
            update_doc['reason'] = update_data.reason
        if update_data.supporting_documents:
            update_doc['supporting_documents'] = update_data.supporting_documents
        
        if not update_doc:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        update_doc['updated_at'] = datetime.utcnow()
        
        # Update in MongoDB
        result = current_app.mongo.leave_requests.update_one(
            {'request_id': request_id},
            {'$set': update_doc}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Failed to update leave request'}), 500
        
        logger.info(f"✅ Leave request {request_id} updated by {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Leave request updated successfully',
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Leave request update error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@leaves_bp.route('/cancel/<request_id>', methods=['POST'])
@jwt_required()
def cancel_leave_request(request_id):
    """Cancel a leave request"""
    try:
        current_user = get_jwt_identity()
        
        # Get leave request
        leave_request = current_app.mongo.leave_requests.find_one({'request_id': request_id})
        if not leave_request:
            return jsonify({'error': 'Leave request not found'}), 404
        
        # Check if user owns the request
        if current_user['user_id'] != leave_request['student_id']:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Check if request can be cancelled
        if leave_request['status'] not in ['pending', 'approved']:
            return jsonify({'error': 'Request cannot be cancelled'}), 400
        
        # Update status
        result = current_app.mongo.leave_requests.update_one(
            {'request_id': request_id},
            {
                '$set': {
                    'status': 'cancelled',
                    'cancelled_at': datetime.utcnow(),
                    'cancelled_by': current_user['user_id']
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Failed to cancel leave request'}), 500
        
        logger.info(f"✅ Leave request {request_id} cancelled by {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Leave request cancelled successfully',
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Leave request cancellation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def calculate_leave_balance(student_id):
    """Calculate leave balance for a student"""
    try:
        # Get leave policies
        policy_manager = PolicyManager()
        leave_policies = policy_manager.get_leave_policies()
        leave_types = leave_policies.get('leave_types', {})
        
        # Get current academic year (simplified)
        current_year = datetime.now().year
        academic_year = f"{current_year}-{current_year + 1}"
        
        # Calculate balance for each leave type
        balance = []
        
        for leave_type, policy in leave_types.items():
            max_days = policy.get('max_days_per_semester', 0)
            
            # Get used days for this academic year
            start_date = datetime(current_year, 8, 1)  # Academic year start
            end_date = datetime(current_year + 1, 5, 31)  # Academic year end
            
            used_days = calculate_used_leave_days(student_id, leave_type, start_date, end_date)
            
            balance.append({
                'leave_type': leave_type,
                'total_allowed': max_days,
                'used_days': used_days,
                'remaining_days': max(0, max_days - used_days),
                'academic_year': academic_year
            })
        
        return balance
        
    except Exception as e:
        logger.error(f"❌ Error calculating leave balance: {e}")
        return []

def calculate_used_leave_days(student_id, leave_type, start_date, end_date):
    """Calculate used leave days for a student"""
    try:
        # Get approved leave requests
        pipeline = [
            {
                '$match': {
                    'student_id': student_id,
                    'leave_type': leave_type,
                    'status': 'approved',
                    'start_date': {'$gte': start_date},
                    'end_date': {'$lte': end_date}
                }
            },
            {
                '$addFields': {
                    'leave_days': {
                        '$add': [
                            {'$subtract': ['$end_date', '$start_date']},
                            1
                        ]
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total_days': {'$sum': '$leave_days'}
                }
            }
        ]
        
        result = list(current_app.mongo.leave_requests.aggregate(pipeline))
        
        if result:
            # Convert timedelta to days
            total_timedelta = result[0]['total_days']
            return total_timedelta.days if hasattr(total_timedelta, 'days') else 0
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Error calculating used leave days: {e}")
        return 0
