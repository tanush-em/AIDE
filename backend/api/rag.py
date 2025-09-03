from flask import Blueprint, request, jsonify
import sys
import os
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.rag_service import RAGService
import asyncio
import uuid
import datetime

# Create blueprint
rag_bp = Blueprint('rag', __name__)

# Global RAG service instance
rag_service = None

def init_rag_service():
    """Initialize the RAG service"""
    global rag_service
    if rag_service is None:
        logger.info("Initializing RAG service...")
        rag_service = RAGService()
        # Note: We'll initialize it when the first request comes in
        # to avoid blocking the Flask startup

async def ensure_rag_initialized():
    """Ensure RAG service is initialized"""
    global rag_service
    if rag_service is None:
        logger.info("Creating new RAG service instance...")
        rag_service = RAGService()
    
    if not rag_service.is_initialized:
        logger.info("Initializing RAG service...")
        await rag_service.initialize()
        logger.info("RAG service initialized successfully")

@rag_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        logger.info("Chat endpoint accessed")
        data = request.get_json()
        if not data or 'message' not in data:
            logger.warning("Chat request missing message field")
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message']
        session_id = data.get('session_id')
        user_id = data.get('user_id', 'default')
        
        logger.info(f"Processing chat message for session {session_id}, user {user_id}")
        logger.info(f"Message: {message[:100]}{'...' if len(message) > 100 else ''}")
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session ID: {session_id}")
        
        # Run async initialization and processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Ensure RAG is initialized
            logger.info("Ensuring RAG service is initialized...")
            loop.run_until_complete(ensure_rag_initialized())
            
            # Process the query
            logger.info("Processing query with RAG service...")
            result = loop.run_until_complete(
                rag_service.process_query(session_id, message, user_id)
            )
            
            logger.info(f"Query processed successfully. Response length: {len(result.get('response', ''))}")
            
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
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/status', methods=['GET'])
def get_status():
    """Get RAG system status"""
    try:
        logger.info("Status endpoint accessed")
        if rag_service is None:
            logger.info("RAG service not created yet")
            return jsonify({
                'initialized': False,
                'message': 'RAG service not created yet'
            })
        
        status = rag_service.get_system_status()
        logger.info(f"System status retrieved: {status}")
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """Get conversation history for a session"""
    try:
        logger.info(f"History endpoint accessed for session: {session_id}")
        if rag_service is None or not rag_service.is_initialized:
            logger.warning("RAG system not initialized for history request")
            return jsonify({'error': 'RAG system not initialized'}), 503
        
        history = rag_service.get_conversation_history(session_id)
        logger.info(f"History retrieved for session {session_id}: {len(history)} messages")
        return jsonify(history)
        
    except Exception as e:
        logger.error(f"Error getting history for session {session_id}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/export/<session_id>', methods=['GET'])
def export_conversation(session_id):
    """Export conversation session"""
    try:
        logger.info(f"Export endpoint accessed for session: {session_id}")
        if rag_service is None or not rag_service.is_initialized:
            logger.warning("RAG system not initialized for export request")
            return jsonify({'error': 'RAG system not initialized'}), 503
        
        format_type = request.args.get('format', 'json')
        if format_type not in ['json', 'txt']:
            logger.warning(f"Invalid export format requested: {format_type}")
            return jsonify({'error': 'Invalid format. Use json or txt'}), 400
        
        logger.info(f"Exporting conversation {session_id} in {format_type} format")
        export_data = rag_service.export_conversation(session_id, format_type)
        logger.info(f"Export completed for session {session_id}")
        return jsonify(export_data)
        
    except Exception as e:
        logger.error(f"Error exporting conversation {session_id}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/clear/<session_id>', methods=['DELETE'])
def clear_session(session_id):
    """Clear a conversation session"""
    try:
        logger.info(f"Clear endpoint accessed for session: {session_id}")
        if rag_service is None or not rag_service.is_initialized:
            logger.warning("RAG system not initialized for clear request")
            return jsonify({'error': 'RAG system not initialized'}), 503
        
        logger.info(f"Clearing session {session_id}")
        result = rag_service.clear_session(session_id)
        logger.info(f"Session {session_id} cleared successfully")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error clearing session {session_id}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/rebuild', methods=['POST'])
def rebuild_knowledge_base():
    """Rebuild the knowledge base"""
    try:
        logger.info("Rebuild endpoint accessed")
        # Run async rebuild
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Ensure RAG is initialized
            logger.info("Ensuring RAG service is initialized for rebuild...")
            loop.run_until_complete(ensure_rag_initialized())
            
            # Rebuild knowledge base
            logger.info("Starting knowledge base rebuild...")
            result = loop.run_until_complete(
                rag_service.rebuild_knowledge_base()
            )
            
            logger.info("Knowledge base rebuild completed successfully")
            return jsonify(result)
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error rebuilding knowledge base: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/cleanup', methods=['POST'])
def cleanup_sessions():
    """Clean up inactive sessions"""
    try:
        logger.info("Cleanup endpoint accessed")
        if rag_service is None or not rag_service.is_initialized:
            logger.warning("RAG system not initialized for cleanup request")
            return jsonify({'error': 'RAG system not initialized'}), 503
        
        data = request.get_json() or {}
        timeout = data.get('timeout')
        
        logger.info(f"Cleaning up inactive sessions with timeout: {timeout}")
        result = rag_service.cleanup_inactive_sessions(timeout)
        logger.info(f"Cleanup completed: {result}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in cleanup: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@rag_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for RAG system"""
    try:
        logger.info("RAG health check endpoint accessed")
        if rag_service is None:
            logger.info("RAG service not created")
            return jsonify({
                'status': 'not_initialized',
                'message': 'RAG service not created'
            })
        
        if not rag_service.is_initialized:
            logger.info("RAG system is initializing")
            return jsonify({
                'status': 'initializing',
                'message': 'RAG system is initializing',
                'error': rag_service.initialization_error
            })
        
        logger.info("RAG system is healthy")
        return jsonify({
            'status': 'healthy',
            'message': 'RAG system is operational',
            'system_status': rag_service.get_system_status()
        })
        
    except Exception as e:
        logger.error(f"Error in RAG health check: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'RAG system error',
            'error': str(e)
        }), 500

@rag_bp.route('/simple-health', methods=['GET'])
def simple_health_check():
    """Simple health check that doesn't require RAG service"""
    logger.info("Simple health check endpoint accessed")
    return jsonify({
        'status': 'ok',
        'message': 'RAG API endpoint is accessible',
        'timestamp': str(datetime.datetime.now())
    })
