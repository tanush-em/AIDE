from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta
from bson import ObjectId
import uuid
from ..models.notice import NoticeCreate, NoticeUpdate, NoticeResponse, NoticeStats

logger = logging.getLogger(__name__)

notices_bp = Blueprint('notices', __name__)

@notices_bp.route('/post', methods=['POST'])
@jwt_required()
def post_notice():
    """Post a new notice"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        try:
            notice_data = NoticeCreate(**data)
        except Exception as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Only faculty and coordinators can post notices'}), 403
        
        # Generate notice ID
        notice_id = f"NOT{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # Create notice
        notice = {
            'notice_id': notice_id,
            'title': notice_data.title,
            'content': notice_data.content,
            'priority': notice_data.priority.value,
            'category': notice_data.category.value,
            'target_audience': notice_data.target_audience,
            'department': notice_data.department,
            'posted_by': current_user['user_id'],
            'attachments': notice_data.attachments or [],
            'expiry_date': notice_data.expiry_date,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        
        # Insert into MongoDB
        result = current_app.mongo.notices.insert_one(notice)
        
        # Get the created record
        created_record = current_app.mongo.notices.find_one({'_id': result.inserted_id})
        created_record['id'] = str(created_record['_id'])
        del created_record['_id']
        
        logger.info(f"✅ Notice posted {notice_id} by {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Notice posted successfully',
            'notice': created_record,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Notice posting error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notices_bp.route('/list', methods=['GET'])
@jwt_required()
def list_notices():
    """List all notices with filtering"""
    try:
        current_user = get_jwt_identity()
        
        # Get query parameters
        priority = request.args.get('priority')
        category = request.args.get('category')
        department = request.args.get('department')
        target_audience = request.args.get('target_audience')
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Build query
        query = {'is_active': True}
        
        # Filter by priority
        if priority:
            query['priority'] = priority
        
        # Filter by category
        if category:
            query['category'] = category
        
        # Filter by department
        if department:
            query['department'] = department
        
        # Filter by target audience
        if target_audience:
            query['target_audience'] = {'$in': [target_audience, 'all']}
        
        # Add role-based filtering
        if current_user['role'] == 'student':
            query['target_audience'] = {'$in': ['students', 'all']}
        elif current_user['role'] == 'faculty':
            query['target_audience'] = {'$in': ['faculty', 'all']}
        
        # Get notices
        notices = list(current_app.mongo.notices.find(
            query,
            {'_id': 0}
        ).sort([
            ('priority', -1),  # High priority first
            ('created_at', -1)  # Recent first
        ]).skip(skip).limit(limit))
        
        # Get total count
        total_count = current_app.mongo.notices.count_documents(query)
        
        return jsonify({
            'success': True,
            'notices': notices,
            'total_count': total_count,
            'limit': limit,
            'skip': skip,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Notice listing error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notices_bp.route('/<notice_id>', methods=['GET'])
@jwt_required()
def get_notice(notice_id):
    """Get a specific notice by ID"""
    try:
        current_user = get_jwt_identity()
        
        # Get notice
        notice = current_app.mongo.notices.find_one({'notice_id': notice_id}, {'_id': 0})
        if not notice:
            return jsonify({'error': 'Notice not found'}), 404
        
        # Check if notice is active
        if not notice['is_active']:
            return jsonify({'error': 'Notice is not active'}), 404
        
        # Check if user has access to this notice
        if current_user['role'] == 'student' and 'students' not in notice['target_audience'] and 'all' not in notice['target_audience']:
            return jsonify({'error': 'Access denied'}), 403
        elif current_user['role'] == 'faculty' and 'faculty' not in notice['target_audience'] and 'all' not in notice['target_audience']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Increment view count (optional)
        current_app.mongo.notices.update_one(
            {'notice_id': notice_id},
            {'$inc': {'view_count': 1}}
        )
        
        return jsonify({
            'success': True,
            'notice': notice,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Notice retrieval error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notices_bp.route('/update/<notice_id>', methods=['PUT'])
@jwt_required()
def update_notice(notice_id):
    """Update a notice"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Only faculty and coordinators can update notices'}), 403
        
        # Get notice
        notice = current_app.mongo.notices.find_one({'notice_id': notice_id})
        if not notice:
            return jsonify({'error': 'Notice not found'}), 404
        
        # Check if user posted the notice or is coordinator
        if (current_user['role'] == 'faculty' and 
            notice['posted_by'] != current_user['user_id']):
            return jsonify({'error': 'Unauthorized to update this notice'}), 403
        
        # Validate input
        try:
            update_data = NoticeUpdate(**data)
        except Exception as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        
        # Build update document
        update_doc = {}
        if update_data.title:
            update_doc['title'] = update_data.title
        if update_data.content:
            update_doc['content'] = update_data.content
        if update_data.priority:
            update_doc['priority'] = update_data.priority.value
        if update_data.category:
            update_doc['category'] = update_data.category.value
        if update_data.target_audience:
            update_doc['target_audience'] = update_data.target_audience
        if update_data.department:
            update_doc['department'] = update_data.department
        if update_data.attachments:
            update_doc['attachments'] = update_data.attachments
        if update_data.expiry_date:
            update_doc['expiry_date'] = update_data.expiry_date
        if update_data.is_active is not None:
            update_doc['is_active'] = update_data.is_active
        
        if not update_doc:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        update_doc['updated_at'] = datetime.utcnow()
        
        # Update in MongoDB
        result = current_app.mongo.notices.update_one(
            {'notice_id': notice_id},
            {'$set': update_doc}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Failed to update notice'}), 500
        
        logger.info(f"✅ Notice {notice_id} updated by {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Notice updated successfully',
            'notice_id': notice_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Notice update error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notices_bp.route('/delete/<notice_id>', methods=['DELETE'])
@jwt_required()
def delete_notice(notice_id):
    """Delete a notice (soft delete)"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Only faculty and coordinators can delete notices'}), 403
        
        # Get notice
        notice = current_app.mongo.notices.find_one({'notice_id': notice_id})
        if not notice:
            return jsonify({'error': 'Notice not found'}), 404
        
        # Check if user posted the notice or is coordinator
        if (current_user['role'] == 'faculty' and 
            notice['posted_by'] != current_user['user_id']):
            return jsonify({'error': 'Unauthorized to delete this notice'}), 403
        
        # Soft delete by setting is_active to False
        result = current_app.mongo.notices.update_one(
            {'notice_id': notice_id},
            {
                '$set': {
                    'is_active': False,
                    'deleted_at': datetime.utcnow(),
                    'deleted_by': current_user['user_id']
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Failed to delete notice'}), 500
        
        logger.info(f"✅ Notice {notice_id} deleted by {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Notice deleted successfully',
            'notice_id': notice_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Notice deletion error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notices_bp.route('/my-notices', methods=['GET'])
@jwt_required()
def get_my_notices():
    """Get notices posted by the current user"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Get notices posted by user
        notices = list(current_app.mongo.notices.find(
            {'posted_by': current_user['user_id']},
            {'_id': 0}
        ).sort('created_at', -1).skip(skip).limit(limit))
        
        # Get total count
        total_count = current_app.mongo.notices.count_documents({'posted_by': current_user['user_id']})
        
        return jsonify({
            'success': True,
            'notices': notices,
            'total_count': total_count,
            'limit': limit,
            'skip': skip,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ My notices error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notices_bp.route('/urgent', methods=['GET'])
@jwt_required()
def get_urgent_notices():
    """Get urgent/high priority notices"""
    try:
        current_user = get_jwt_identity()
        
        # Build query for urgent notices
        query = {
            'is_active': True,
            'priority': 'high'
        }
        
        # Add role-based filtering
        if current_user['role'] == 'student':
            query['target_audience'] = {'$in': ['students', 'all']}
        elif current_user['role'] == 'faculty':
            query['target_audience'] = {'$in': ['faculty', 'all']}
        
        # Get urgent notices
        urgent_notices = list(current_app.mongo.notices.find(
            query,
            {'_id': 0}
        ).sort('created_at', -1).limit(10))
        
        return jsonify({
            'success': True,
            'urgent_notices': urgent_notices,
            'count': len(urgent_notices),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Urgent notices error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notices_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_notice_statistics():
    """Get notice statistics"""
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
        
        # Calculate statistics by priority
        priority_pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': '$priority',
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        priority_stats = list(current_app.mongo.notices.aggregate(priority_pipeline))
        
        # Calculate statistics by category
        category_pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': '$category',
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        category_stats = list(current_app.mongo.notices.aggregate(category_pipeline))
        
        # Calculate statistics by target audience
        audience_pipeline = [
            {'$match': match_query},
            {'$unwind': '$target_audience'},
            {'$group': {
                '_id': '$target_audience',
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        audience_stats = list(current_app.mongo.notices.aggregate(audience_pipeline))
        
        # Calculate active vs inactive notices
        active_count = current_app.mongo.notices.count_documents({'is_active': True})
        inactive_count = current_app.mongo.notices.count_documents({'is_active': False})
        
        return jsonify({
            'success': True,
            'statistics': {
                'by_priority': priority_stats,
                'by_category': category_stats,
                'by_audience': audience_stats,
                'active_notices': active_count,
                'inactive_notices': inactive_count
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Notice statistics error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notices_bp.route('/search', methods=['GET'])
@jwt_required()
def search_notices():
    """Search notices by title or content"""
    try:
        current_user = get_jwt_identity()
        
        # Get search query
        query_text = request.args.get('q', '').strip()
        if not query_text:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Build search query
        search_query = {
            'is_active': True,
            '$or': [
                {'title': {'$regex': query_text, '$options': 'i'}},
                {'content': {'$regex': query_text, '$options': 'i'}}
            ]
        }
        
        # Add role-based filtering
        if current_user['role'] == 'student':
            search_query['target_audience'] = {'$in': ['students', 'all']}
        elif current_user['role'] == 'faculty':
            search_query['target_audience'] = {'$in': ['faculty', 'all']}
        
        # Get search results
        search_results = list(current_app.mongo.notices.find(
            search_query,
            {'_id': 0}
        ).sort([
            ('priority', -1),
            ('created_at', -1)
        ]).limit(20))
        
        return jsonify({
            'success': True,
            'search_query': query_text,
            'results': search_results,
            'count': len(search_results),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Notice search error: {str(e)}")
        return jsonify({'error': str(e)}), 500
