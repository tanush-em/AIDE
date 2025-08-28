from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta
from bson import ObjectId
import uuid
import os
import hashlib
from werkzeug.utils import secure_filename
from ..models.resource import ResourceCreate, ResourceUpdate, ResourceResponse, ResourceStats

logger = logging.getLogger(__name__)

resources_bp = Blueprint('resources', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 
    'txt', 'jpg', 'jpeg', 'png', 'gif', 'mp4', 'mp3',
    'zip', 'rar', 'csv', 'json', 'xml'
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_hash(file_path):
    """Calculate SHA-256 hash of file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@resources_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_resource():
    """Upload a new resource"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Only faculty and coordinators can upload resources'}), 403
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'general')
        tags = request.form.get('tags', '').split(',') if request.form.get('tags') else []
        access_level = request.form.get('access_level', 'public')
        department = request.form.get('department', '')
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # Secure filename
        filename = secure_filename(file.filename)
        original_filename = file.filename
        
        # Generate unique filename
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, '..', 'uploads', 'resources')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # Calculate file hash
        file_hash = get_file_hash(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Generate resource ID
        resource_id = f"RES{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
        
        # Create resource record
        resource = {
            'resource_id': resource_id,
            'title': title,
            'description': description,
            'original_filename': original_filename,
            'stored_filename': unique_filename,
            'file_path': file_path,
            'file_size': file_size,
            'file_hash': file_hash,
            'file_type': file_extension,
            'category': category,
            'tags': [tag.strip() for tag in tags if tag.strip()],
            'access_level': access_level,
            'department': department,
            'uploaded_by': current_user['user_id'],
            'download_count': 0,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        
        # Insert into MongoDB
        result = current_app.mongo.resources.insert_one(resource)
        
        # Get the created record
        created_record = current_app.mongo.resources.find_one({'_id': result.inserted_id})
        created_record['id'] = str(created_record['_id'])
        del created_record['_id']
        del created_record['file_path']  # Don't expose file path
        
        logger.info(f"✅ Resource uploaded {resource_id} by {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Resource uploaded successfully',
            'resource': created_record,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Resource upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/list', methods=['GET'])
@jwt_required()
def list_resources():
    """List all resources with filtering"""
    try:
        current_user = get_jwt_identity()
        
        # Get query parameters
        category = request.args.get('category')
        file_type = request.args.get('file_type')
        department = request.args.get('department')
        access_level = request.args.get('access_level')
        uploaded_by = request.args.get('uploaded_by')
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Build query
        query = {'is_active': True}
        
        # Filter by category
        if category:
            query['category'] = category
        
        # Filter by file type
        if file_type:
            query['file_type'] = file_type
        
        # Filter by department
        if department:
            query['department'] = department
        
        # Filter by access level
        if access_level:
            query['access_level'] = access_level
        
        # Filter by uploader
        if uploaded_by:
            query['uploaded_by'] = uploaded_by
        
        # Add role-based access filtering
        if current_user['role'] == 'student':
            query['access_level'] = {'$in': ['public', 'students']}
        elif current_user['role'] == 'faculty':
            query['access_level'] = {'$in': ['public', 'students', 'faculty']}
        
        # Get resources
        resources = list(current_app.mongo.resources.find(
            query,
            {'_id': 0, 'file_path': 0}  # Don't expose file path
        ).sort('created_at', -1).skip(skip).limit(limit))
        
        # Get total count
        total_count = current_app.mongo.resources.count_documents(query)
        
        return jsonify({
            'success': True,
            'resources': resources,
            'total_count': total_count,
            'limit': limit,
            'skip': skip,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Resource listing error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/<resource_id>', methods=['GET'])
@jwt_required()
def get_resource(resource_id):
    """Get a specific resource by ID"""
    try:
        current_user = get_jwt_identity()
        
        # Get resource
        resource = current_app.mongo.resources.find_one({'resource_id': resource_id})
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        
        # Check if resource is active
        if not resource['is_active']:
            return jsonify({'error': 'Resource is not active'}), 404
        
        # Check access level
        if current_user['role'] == 'student' and resource['access_level'] not in ['public', 'students']:
            return jsonify({'error': 'Access denied'}), 403
        elif current_user['role'] == 'faculty' and resource['access_level'] not in ['public', 'students', 'faculty']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Remove sensitive fields
        resource['id'] = str(resource['_id'])
        del resource['_id']
        del resource['file_path']
        
        return jsonify({
            'success': True,
            'resource': resource,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Resource retrieval error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/download/<resource_id>', methods=['GET'])
@jwt_required()
def download_resource(resource_id):
    """Download a resource"""
    try:
        current_user = get_jwt_identity()
        
        # Get resource
        resource = current_app.mongo.resources.find_one({'resource_id': resource_id})
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        
        # Check if resource is active
        if not resource['is_active']:
            return jsonify({'error': 'Resource is not active'}), 404
        
        # Check access level
        if current_user['role'] == 'student' and resource['access_level'] not in ['public', 'students']:
            return jsonify({'error': 'Access denied'}), 403
        elif current_user['role'] == 'faculty' and resource['access_level'] not in ['public', 'students', 'faculty']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if file exists
        if not os.path.exists(resource['file_path']):
            return jsonify({'error': 'File not found on server'}), 404
        
        # Increment download count
        current_app.mongo.resources.update_one(
            {'resource_id': resource_id},
            {'$inc': {'download_count': 1}}
        )
        
        # Log download
        download_log = {
            'resource_id': resource_id,
            'downloaded_by': current_user['user_id'],
            'downloaded_at': datetime.utcnow()
        }
        current_app.mongo.resource_downloads.insert_one(download_log)
        
        logger.info(f"✅ Resource {resource_id} downloaded by {current_user['user_id']}")
        
        # Return file
        return send_file(
            resource['file_path'],
            as_attachment=True,
            download_name=resource['original_filename']
        )
        
    except Exception as e:
        logger.error(f"❌ Resource download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/update/<resource_id>', methods=['PUT'])
@jwt_required()
def update_resource(resource_id):
    """Update a resource"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Only faculty and coordinators can update resources'}), 403
        
        # Get resource
        resource = current_app.mongo.resources.find_one({'resource_id': resource_id})
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        
        # Check if user uploaded the resource or is coordinator
        if (current_user['role'] == 'faculty' and 
            resource['uploaded_by'] != current_user['user_id']):
            return jsonify({'error': 'Unauthorized to update this resource'}), 403
        
        # Validate input
        try:
            update_data = ResourceUpdate(**data)
        except Exception as e:
            return jsonify({'error': f'Validation error: {str(e)}'}), 400
        
        # Build update document
        update_doc = {}
        if update_data.title:
            update_doc['title'] = update_data.title
        if update_data.description:
            update_doc['description'] = update_data.description
        if update_data.category:
            update_doc['category'] = update_data.category
        if update_data.tags:
            update_doc['tags'] = update_data.tags
        if update_data.access_level:
            update_doc['access_level'] = update_data.access_level
        if update_data.department:
            update_doc['department'] = update_data.department
        if update_data.is_active is not None:
            update_doc['is_active'] = update_data.is_active
        
        if not update_doc:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        update_doc['updated_at'] = datetime.utcnow()
        
        # Update in MongoDB
        result = current_app.mongo.resources.update_one(
            {'resource_id': resource_id},
            {'$set': update_doc}
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Failed to update resource'}), 500
        
        logger.info(f"✅ Resource {resource_id} updated by {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Resource updated successfully',
            'resource_id': resource_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Resource update error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/delete/<resource_id>', methods=['DELETE'])
@jwt_required()
def delete_resource(resource_id):
    """Delete a resource (soft delete)"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Only faculty and coordinators can delete resources'}), 403
        
        # Get resource
        resource = current_app.mongo.resources.find_one({'resource_id': resource_id})
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404
        
        # Check if user uploaded the resource or is coordinator
        if (current_user['role'] == 'faculty' and 
            resource['uploaded_by'] != current_user['user_id']):
            return jsonify({'error': 'Unauthorized to delete this resource'}), 403
        
        # Soft delete by setting is_active to False
        result = current_app.mongo.resources.update_one(
            {'resource_id': resource_id},
            {
                '$set': {
                    'is_active': False,
                    'deleted_at': datetime.utcnow(),
                    'deleted_by': current_user['user_id']
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({'error': 'Failed to delete resource'}), 500
        
        logger.info(f"✅ Resource {resource_id} deleted by {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'message': 'Resource deleted successfully',
            'resource_id': resource_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Resource deletion error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/my-resources', methods=['GET'])
@jwt_required()
def get_my_resources():
    """Get resources uploaded by the current user"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        # Get resources uploaded by user
        resources = list(current_app.mongo.resources.find(
            {'uploaded_by': current_user['user_id']},
            {'_id': 0, 'file_path': 0}
        ).sort('created_at', -1).skip(skip).limit(limit))
        
        # Get total count
        total_count = current_app.mongo.resources.count_documents({'uploaded_by': current_user['user_id']})
        
        return jsonify({
            'success': True,
            'resources': resources,
            'total_count': total_count,
            'limit': limit,
            'skip': skip,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ My resources error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/search', methods=['GET'])
@jwt_required()
def search_resources():
    """Search resources by title, description, or tags"""
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
                {'description': {'$regex': query_text, '$options': 'i'}},
                {'tags': {'$in': [query_text.lower()]}}
            ]
        }
        
        # Add role-based access filtering
        if current_user['role'] == 'student':
            search_query['access_level'] = {'$in': ['public', 'students']}
        elif current_user['role'] == 'faculty':
            search_query['access_level'] = {'$in': ['public', 'students', 'faculty']}
        
        # Get search results
        search_results = list(current_app.mongo.resources.find(
            search_query,
            {'_id': 0, 'file_path': 0}
        ).sort('created_at', -1).limit(20))
        
        return jsonify({
            'success': True,
            'search_query': query_text,
            'results': search_results,
            'count': len(search_results),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Resource search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_resource_statistics():
    """Get resource statistics"""
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
        
        # Calculate statistics by category
        category_pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': '$category',
                'count': {'$sum': 1},
                'total_size': {'$sum': '$file_size'}
            }},
            {'$sort': {'count': -1}}
        ]
        
        category_stats = list(current_app.mongo.resources.aggregate(category_pipeline))
        
        # Calculate statistics by file type
        type_pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': '$file_type',
                'count': {'$sum': 1},
                'total_size': {'$sum': '$file_size'}
            }},
            {'$sort': {'count': -1}}
        ]
        
        type_stats = list(current_app.mongo.resources.aggregate(type_pipeline))
        
        # Calculate statistics by access level
        access_pipeline = [
            {'$match': match_query},
            {'$group': {
                '_id': '$access_level',
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        access_stats = list(current_app.mongo.resources.aggregate(access_pipeline))
        
        # Calculate total statistics
        total_resources = current_app.mongo.resources.count_documents({'is_active': True})
        total_size = sum(resource['file_size'] for resource in current_app.mongo.resources.find({'is_active': True}))
        total_downloads = sum(resource['download_count'] for resource in current_app.mongo.resources.find({'is_active': True}))
        
        # Get most downloaded resources
        most_downloaded = list(current_app.mongo.resources.find(
            {'is_active': True},
            {'title': 1, 'download_count': 1, 'file_type': 1, '_id': 0}
        ).sort('download_count', -1).limit(10))
        
        return jsonify({
            'success': True,
            'statistics': {
                'by_category': category_stats,
                'by_file_type': type_stats,
                'by_access_level': access_stats,
                'total_resources': total_resources,
                'total_size': total_size,
                'total_downloads': total_downloads,
                'most_downloaded_resources': most_downloaded
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Resource statistics error: {str(e)}")
        return jsonify({'error': str(e)}), 500
