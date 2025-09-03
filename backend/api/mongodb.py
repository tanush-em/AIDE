from flask import Blueprint, request, jsonify
import sys
import os
import asyncio
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongodb_service import mongodb_service
from agents.mongodb_tools import mongodb_tools
from database.connection import mongodb_connection

# Create blueprint
mongodb_bp = Blueprint('mongodb', __name__)

# Global MongoDB service instance
mongodb_service_instance = None

def init_mongodb_service():
    """Initialize the MongoDB service"""
    global mongodb_service_instance
    if mongodb_service_instance is None:
        mongodb_service_instance = mongodb_service

async def ensure_mongodb_initialized():
    """Ensure MongoDB service is initialized"""
    global mongodb_service_instance
    if mongodb_service_instance is None:
        mongodb_service_instance = mongodb_service
    
    if not mongodb_service_instance.is_initialized:
        await mongodb_service_instance.initialize()

@mongodb_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for MongoDB system"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            health_status = loop.run_until_complete(mongodb_connection.health_check())
            return jsonify(health_status)
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'MongoDB health check failed: {str(e)}'
        }), 500

@mongodb_bp.route('/stats', methods=['GET'])
def get_database_stats():
    """Get database statistics"""
    try:
        # Use a new event loop for each request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            stats = loop.run_until_complete(mongodb_service_instance.get_database_stats())
            return jsonify(stats)
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Document endpoints
@mongodb_bp.route('/documents', methods=['GET'])
def get_documents():
    """Get documents with optional filters"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            # Get query parameters
            limit = int(request.args.get('limit', 10))
            document_type = request.args.get('type')
            category = request.args.get('category')
            status = request.args.get('status')
            
            # Build query
            query = {}
            if document_type:
                query['document_type'] = document_type
            if category:
                query['category'] = category
            if status:
                query['status'] = status
            
            documents = loop.run_until_complete(
                mongodb_service_instance.search_documents(query, limit)
            )
            
            return jsonify({
                'documents': documents,
                'count': len(documents),
                'query': query
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mongodb_bp.route('/documents', methods=['POST'])
def create_document():
    """Create a new document"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Document data is required'}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            document = loop.run_until_complete(
                mongodb_service_instance.create_document(data)
            )
            
            return jsonify(document), 201
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mongodb_bp.route('/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get a specific document by ID"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            document = loop.run_until_complete(
                mongodb_service_instance.get_document(document_id)
            )
            
            if not document:
                return jsonify({'error': 'Document not found'}), 404
            
            return jsonify(document)
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mongodb_bp.route('/documents/<document_id>', methods=['PUT'])
def update_document(document_id):
    """Update a document"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Update data is required'}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            document = loop.run_until_complete(
                mongodb_service_instance.update_document(document_id, data)
            )
            
            if not document:
                return jsonify({'error': 'Document not found'}), 404
            
            return jsonify(document)
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mongodb_bp.route('/documents/search', methods=['POST'])
def search_documents():
    """Search documents by text"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Search query is required'}), 400
        
        query = data['query']
        limit = int(data.get('limit', 10))
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            documents = loop.run_until_complete(
                mongodb_service_instance.search_documents_by_text(query, limit)
            )
            
            return jsonify({
                'documents': documents,
                'count': len(documents),
                'query': query
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User endpoints
@mongodb_bp.route('/users', methods=['GET'])
def get_users():
    """Get users with optional filters"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            limit = int(request.args.get('limit', 10))
            role = request.args.get('role')
            status = request.args.get('status')
            
            query = {}
            if role:
                query['role'] = role
            if status:
                query['status'] = status
            
            users = loop.run_until_complete(
                mongodb_service_instance.search_users(query, limit)
            )
            
            return jsonify({
                'users': users,
                'count': len(users),
                'query': query
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mongodb_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'User data is required'}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            user = loop.run_until_complete(
                mongodb_service_instance.create_user(data)
            )
            
            return jsonify(user), 201
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mongodb_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            user = loop.run_until_complete(
                mongodb_service_instance.get_user(user_id)
            )
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify(user)
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mongodb_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Update data is required'}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            user = loop.run_until_complete(
                mongodb_service_instance.update_user(user_id, data)
            )
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify(user)
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Analytics endpoints
@mongodb_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """Get analytics with optional filters"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            limit = int(request.args.get('limit', 100))
            event_type = request.args.get('event_type')
            source = request.args.get('source')
            
            filters = {}
            if event_type:
                filters['event_type'] = event_type
            if source:
                filters['source'] = source
            
            analytics = loop.run_until_complete(
                mongodb_service_instance.get_analytics(filters, limit)
            )
            
            return jsonify({
                'analytics': analytics,
                'count': len(analytics),
                'filters': filters
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Query logs endpoints
@mongodb_bp.route('/query-logs', methods=['GET'])
def get_query_logs():
    """Get query logs with optional filters"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            limit = int(request.args.get('limit', 100))
            query_type = request.args.get('query_type')
            success = request.args.get('success')
            
            filters = {}
            if query_type:
                filters['query_type'] = query_type
            if success is not None:
                filters['success'] = success.lower() == 'true'
            
            logs = loop.run_until_complete(
                mongodb_service_instance.get_query_logs(filters, limit)
            )
            
            return jsonify({
                'query_logs': logs,
                'count': len(logs),
                'filters': filters
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Tool endpoints for agent operations
@mongodb_bp.route('/tools/search', methods=['POST'])
def search_database_tool():
    """Search database using MongoDB tools"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Search query is required'}), 400
        
        query = data['query']
        collection = data.get('collection', 'documents')
        limit = int(data.get('limit', 10))
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            result = loop.run_until_complete(
                mongodb_tools.search_database_tool(query, collection, limit)
            )
            
            return jsonify(result)
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mongodb_bp.route('/tools/aggregate', methods=['POST'])
def aggregate_data_tool():
    """Perform aggregation using MongoDB tools"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Aggregation query is required'}), 400
        
        query = data['query']
        collection = data.get('collection', 'analytics')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            result = loop.run_until_complete(
                mongodb_tools.aggregate_data_tool(query, collection)
            )
            
            return jsonify(result)
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mongodb_bp.route('/tools/view-record', methods=['POST'])
def view_record_tool():
    """View a specific record using MongoDB tools"""
    try:
        data = request.get_json()
        if not data or 'record_id' not in data:
            return jsonify({'error': 'Record ID is required'}), 400
        
        record_id = data['record_id']
        collection = data.get('collection', 'documents')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            result = loop.run_until_complete(
                mongodb_tools.view_record_tool(record_id, collection)
            )
            
            return jsonify(result)
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mongodb_bp.route('/tools/edit-record', methods=['POST'])
def edit_record_tool():
    """Edit a record using MongoDB tools"""
    try:
        data = request.get_json()
        if not data or 'record_id' not in data or 'update_data' not in data:
            return jsonify({'error': 'Record ID and update data are required'}), 400
        
        record_id = data['record_id']
        update_data = data['update_data']
        collection = data.get('collection', 'documents')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            result = loop.run_until_complete(
                mongodb_tools.edit_record_tool(record_id, update_data, collection)
            )
            
            return jsonify(result)
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mongodb_bp.route('/tools/create-record', methods=['POST'])
def create_record_tool():
    """Create a record using MongoDB tools"""
    try:
        data = request.get_json()
        if not data or 'record_data' not in data:
            return jsonify({'error': 'Record data is required'}), 400
        
        record_data = data['record_data']
        collection = data.get('collection', 'documents')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(ensure_mongodb_initialized())
            
            result = loop.run_until_complete(
                mongodb_tools.create_record_tool(record_data, collection)
            )
            
            return jsonify(result)
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
