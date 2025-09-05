from flask import Blueprint, request, jsonify
import sys
import os
import logging
import asyncio
import uuid
import datetime
from typing import Dict, Any

# Configure logging for this module
logger = logging.getLogger(__name__)

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.task_orchestrator import task_orchestrator

# Create blueprint
task_workflow_bp = Blueprint('task_workflow', __name__)

# Store for progress callbacks (in production, use Redis or similar)
progress_callbacks = {}

@task_workflow_bp.route('/chat', methods=['POST'])
def chat_with_tasks():
    """Handle chat messages with task-based workflow"""
    try:
        logger.info("Task-based chat endpoint accessed")
        data = request.get_json()
        if not data or 'message' not in data:
            logger.warning("Task chat request missing message field")
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message']
        session_id = data.get('session_id')
        user_id = data.get('user_id', 'default')
        conversation_history = data.get('conversation_history', [])
        
        logger.info(f"Processing task-based chat message for session {session_id}, user {user_id}")
        logger.info(f"Message: {message[:100]}{'...' if len(message) > 100 else ''}")
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session ID: {session_id}")
        
        # Run async task processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Process the query with task-based workflow
            logger.info("Processing query with task-based workflow...")
            result = loop.run_until_complete(
                task_orchestrator.process_query_with_tasks(
                    query=message,
                    conversation_history=conversation_history,
                    user_id=user_id,
                    session_id=session_id,
                    progress_callback=None  # We'll handle progress via separate endpoint
                )
            )
            
            logger.info(f"Task-based query processed successfully. Response length: {len(result.get('response', ''))}")
            
            return jsonify({
                'session_id': session_id,
                'response': result['response'],
                'confidence': result.get('confidence', 'medium'),
                'suggestions': result.get('suggestions', []),
                'task_execution_summary': result.get('task_execution_summary', {}),
                'tasks': result.get('tasks', []),
                'workflow_type': 'task_based',
                'processing_time': result.get('processing_time'),
                'conversation_length': len(conversation_history) + 2  # +2 for user message and response
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error in task-based chat endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@task_workflow_bp.route('/chat/stream', methods=['POST'])
def chat_with_tasks_stream():
    """Handle chat messages with task-based workflow and streaming progress"""
    try:
        logger.info("Task-based streaming chat endpoint accessed")
        data = request.get_json()
        if not data or 'message' not in data:
            logger.warning("Task streaming chat request missing message field")
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message']
        session_id = data.get('session_id')
        user_id = data.get('user_id', 'default')
        conversation_history = data.get('conversation_history', [])
        
        logger.info(f"Processing streaming task-based chat message for session {session_id}, user {user_id}")
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session ID: {session_id}")
        
        # Set up progress tracking
        progress_updates = []
        
        async def progress_callback(update_data: Dict[str, Any]):
            """Callback to capture progress updates"""
            progress_updates.append(update_data)
            logger.info(f"Progress update for session {session_id}: {update_data.get('status', 'unknown')}")
        
        # Run async task processing
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Process the query with task-based workflow
            logger.info("Processing query with streaming task-based workflow...")
            result = loop.run_until_complete(
                task_orchestrator.process_query_with_tasks(
                    query=message,
                    conversation_history=conversation_history,
                    user_id=user_id,
                    session_id=session_id,
                    progress_callback=progress_callback
                )
            )
            
            logger.info(f"Streaming task-based query processed successfully. Response length: {len(result.get('response', ''))}")
            
            return jsonify({
                'session_id': session_id,
                'response': result['response'],
                'confidence': result.get('confidence', 'medium'),
                'suggestions': result.get('suggestions', []),
                'task_execution_summary': result.get('task_execution_summary', {}),
                'tasks': result.get('tasks', []),
                'progress_updates': progress_updates,
                'workflow_type': 'task_based_streaming',
                'processing_time': result.get('processing_time'),
                'conversation_length': len(conversation_history) + 2
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Error in task-based streaming chat endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@task_workflow_bp.route('/session/<session_id>/status', methods=['GET'])
def get_session_status(session_id):
    """Get the status of a specific session"""
    try:
        logger.info(f"Session status endpoint accessed for session: {session_id}")
        status = task_orchestrator.get_session_status(session_id)
        
        if status is None:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'session_id': session_id,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Error getting session status for {session_id}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@task_workflow_bp.route('/sessions', methods=['GET'])
def get_all_sessions():
    """Get all active sessions"""
    try:
        logger.info("All sessions endpoint accessed")
        sessions = task_orchestrator.get_all_sessions()
        
        return jsonify({
            'sessions': sessions,
            'total_sessions': len(sessions)
        })
        
    except Exception as e:
        logger.error(f"Error getting all sessions: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@task_workflow_bp.route('/session/<session_id>', methods=['DELETE'])
def clear_session(session_id):
    """Clear a specific session"""
    try:
        logger.info(f"Clear session endpoint accessed for session: {session_id}")
        success = task_orchestrator.clear_session(session_id)
        
        if not success:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'message': f'Session {session_id} cleared successfully',
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error clearing session {session_id}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@task_workflow_bp.route('/statistics', methods=['GET'])
def get_task_statistics():
    """Get task execution statistics"""
    try:
        logger.info("Task statistics endpoint accessed")
        
        # Run async statistics gathering
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            stats = loop.run_until_complete(task_orchestrator.get_task_statistics())
            return jsonify(stats)
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Error getting task statistics: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@task_workflow_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for task workflow system"""
    try:
        logger.info("Task workflow health check endpoint accessed")
        
        # Run async health check
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            stats = loop.run_until_complete(task_orchestrator.get_task_statistics())
            
            return jsonify({
                'status': 'healthy',
                'message': 'Task workflow system is operational',
                'statistics': stats,
                'timestamp': str(datetime.datetime.now())
            })
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Error in task workflow health check: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': 'Task workflow system error',
            'error': str(e)
        }), 500
