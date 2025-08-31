from flask import Blueprint, request, jsonify
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.rag_service import RAGService
import asyncio
import uuid

# Create blueprint
rag_bp = Blueprint('rag', __name__)

# Global RAG service instance
rag_service = None

def init_rag_service():
    """Initialize the RAG service"""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
        # Note: We'll initialize it when the first request comes in
        # to avoid blocking the Flask startup

async def ensure_rag_initialized():
    """Ensure RAG service is initialized"""
    global rag_service
    if rag_service is None:
        rag_service = RAGService()
    
    if not rag_service.is_initialized:
        await rag_service.initialize()

@rag_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message']
        session_id = data.get('session_id')
        user_id = data.get('user_id', 'default')
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Run async initialization and processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Ensure RAG is initialized
            loop.run_until_complete(ensure_rag_initialized())
            
            # Process the query
            result = loop.run_until_complete(
                rag_service.process_query(session_id, message, user_id)
            )
            
            return jsonify({
                'session_id': session_id,
                'response': result['response'],
                'confidence': result.get('confidence', 'medium'),
                'suggestions': result.get('suggestions', []),
                'agent_status': result.get('agent_status', {}),
                'conversation_length': result.get('conversation_length', 0),
                'session_active': result.get('session_active', True)
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/status', methods=['GET'])
def get_status():
    """Get RAG system status"""
    try:
        if rag_service is None:
            return jsonify({
                'initialized': False,
                'message': 'RAG service not created yet'
            })
        
        status = rag_service.get_system_status()
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """Get conversation history for a session"""
    try:
        if rag_service is None or not rag_service.is_initialized:
            return jsonify({'error': 'RAG system not initialized'}), 503
        
        history = rag_service.get_conversation_history(session_id)
        return jsonify(history)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/export/<session_id>', methods=['GET'])
def export_conversation(session_id):
    """Export conversation session"""
    try:
        if rag_service is None or not rag_service.is_initialized:
            return jsonify({'error': 'RAG system not initialized'}), 503
        
        format_type = request.args.get('format', 'json')
        if format_type not in ['json', 'txt']:
            return jsonify({'error': 'Invalid format. Use json or txt'}), 400
        
        export_data = rag_service.export_conversation(session_id, format_type)
        return jsonify(export_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/clear/<session_id>', methods=['DELETE'])
def clear_session(session_id):
    """Clear a conversation session"""
    try:
        if rag_service is None or not rag_service.is_initialized:
            return jsonify({'error': 'RAG system not initialized'}), 503
        
        result = rag_service.clear_session(session_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/rebuild', methods=['POST'])
def rebuild_knowledge_base():
    """Rebuild the knowledge base"""
    try:
        # Run async rebuild
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Ensure RAG is initialized
            loop.run_until_complete(ensure_rag_initialized())
            
            # Rebuild knowledge base
            result = loop.run_until_complete(
                rag_service.rebuild_knowledge_base()
            )
            
            return jsonify(result)
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/cleanup', methods=['POST'])
def cleanup_sessions():
    """Clean up inactive sessions"""
    try:
        if rag_service is None or not rag_service.is_initialized:
            return jsonify({'error': 'RAG system not initialized'}), 503
        
        data = request.get_json() or {}
        timeout = data.get('timeout')
        
        result = rag_service.cleanup_inactive_sessions(timeout)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for RAG system"""
    try:
        if rag_service is None:
            return jsonify({
                'status': 'not_initialized',
                'message': 'RAG service not created'
            })
        
        if not rag_service.is_initialized:
            return jsonify({
                'status': 'initializing',
                'message': 'RAG system is initializing',
                'error': rag_service.initialization_error
            })
        
        return jsonify({
            'status': 'healthy',
            'message': 'RAG system is operational',
            'system_status': rag_service.get_system_status()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'RAG system error',
            'error': str(e)
        }), 500
