from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime
import asyncio
from ..agents.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

agents_bp = Blueprint('agents', __name__)

# Initialize the agent orchestrator
orchestrator = AgentOrchestrator()

@agents_bp.route('/chat', methods=['POST'])
@jwt_required()
async def chat_with_agent():
    """Chat with AI agents using intelligent routing"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        context = data.get('context', {})
        
        # Add user context
        context['user_id'] = current_user['user_id']
        context['role'] = current_user['role']
        context['email'] = current_user['email']
        
        # Route query to appropriate agent(s)
        result = await orchestrator.route_query(query, context)
        
        logger.info(f"✅ AI Agent query processed for user {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Agent chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/chat/<agent_name>', methods=['POST'])
@jwt_required()
async def chat_with_specific_agent(agent_name):
    """Chat with a specific AI agent"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        context = data.get('context', {})
        
        # Add user context
        context['user_id'] = current_user['user_id']
        context['role'] = current_user['role']
        context['email'] = current_user['email']
        
        # Process with specific agent
        result = await orchestrator._process_with_agent(agent_name, query, context)
        
        logger.info(f"✅ Specific agent {agent_name} query processed for user {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'agent': agent_name,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Specific agent chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/capabilities', methods=['GET'])
@jwt_required()
async def get_agent_capabilities():
    """Get capabilities of all AI agents"""
    try:
        capabilities = await orchestrator.get_agent_capabilities()
        
        return jsonify({
            'success': True,
            'capabilities': capabilities,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting agent capabilities: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/health', methods=['GET'])
@jwt_required()
async def get_agent_health():
    """Get health status of all AI agents"""
    try:
        health_status = orchestrator.get_health_status()
        health_check = await orchestrator.health_check()
        
        return jsonify({
            'success': True,
            'health_status': health_status,
            'health_check': health_check,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting agent health: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/statistics', methods=['GET'])
@jwt_required()
async def get_agent_statistics():
    """Get usage statistics for all AI agents"""
    try:
        current_user = get_jwt_identity()
        
        # Check if user is faculty or coordinator
        if current_user['role'] not in ['faculty', 'coordinator']:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        statistics = await orchestrator.get_agent_statistics()
        
        return jsonify({
            'success': True,
            'statistics': statistics,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting agent statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/tool/<agent_name>/<tool_name>', methods=['POST'])
@jwt_required()
async def execute_agent_tool(agent_name, tool_name):
    """Execute a specific tool on a specific agent"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json() or {}
        
        # Add user context to parameters
        parameters = data.get('parameters', {})
        parameters['user_id'] = current_user['user_id']
        parameters['role'] = current_user['role']
        
        # Execute tool
        result = await orchestrator.execute_tool(agent_name, tool_name, parameters)
        
        logger.info(f"✅ Tool {tool_name} executed on agent {agent_name} by user {current_user['user_id']}")
        
        return jsonify({
            'success': True,
            'agent': agent_name,
            'tool': tool_name,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error executing agent tool: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/leave/query', methods=['POST'])
@jwt_required()
async def leave_agent_query():
    """Direct query to Leave Agent"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        context = data.get('context', {})
        
        # Add user context
        context['user_id'] = current_user['user_id']
        context['role'] = current_user['role']
        
        # Process with Leave Agent
        result = await orchestrator._process_with_agent('leave', query, context)
        
        return jsonify({
            'success': True,
            'agent': 'leave',
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Leave agent query error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/attendance/query', methods=['POST'])
@jwt_required()
async def attendance_agent_query():
    """Direct query to Attendance Agent"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        context = data.get('context', {})
        
        # Add user context
        context['user_id'] = current_user['user_id']
        context['role'] = current_user['role']
        
        # Process with Attendance Agent
        result = await orchestrator._process_with_agent('attendance', query, context)
        
        return jsonify({
            'success': True,
            'agent': 'attendance',
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Attendance agent query error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/event/query', methods=['POST'])
@jwt_required()
async def event_agent_query():
    """Direct query to Event Agent"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        context = data.get('context', {})
        
        # Add user context
        context['user_id'] = current_user['user_id']
        context['role'] = current_user['role']
        
        # Process with Event Agent
        result = await orchestrator._process_with_agent('event', query, context)
        
        return jsonify({
            'success': True,
            'agent': 'event',
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Event agent query error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/qa/query', methods=['POST'])
@jwt_required()
async def qa_agent_query():
    """Direct query to QA Agent"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        context = data.get('context', {})
        
        # Add user context
        context['user_id'] = current_user['user_id']
        context['role'] = current_user['role']
        
        # Process with QA Agent
        result = await orchestrator._process_with_agent('qa', query, context)
        
        return jsonify({
            'success': True,
            'agent': 'qa',
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ QA agent query error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/validate-leave', methods=['POST'])
@jwt_required()
async def validate_leave_request():
    """Validate leave request using Leave Agent"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'leave_request' not in data:
            return jsonify({'error': 'Leave request data is required'}), 400
        
        leave_request = data['leave_request']
        
        # Execute validation tool
        result = await orchestrator.execute_tool('leave', 'validate_leave_request', {
            'leave_request': leave_request,
            'user_id': current_user['user_id'],
            'role': current_user['role']
        })
        
        return jsonify({
            'success': True,
            'validation_result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Leave validation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/validate-attendance', methods=['POST'])
@jwt_required()
async def validate_attendance():
    """Validate attendance using Attendance Agent"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'attendance_data' not in data:
            return jsonify({'error': 'Attendance data is required'}), 400
        
        attendance_data = data['attendance_data']
        
        # Execute validation tool
        result = await orchestrator.execute_tool('attendance', 'validate_attendance', {
            'attendance_data': attendance_data,
            'user_id': current_user['user_id'],
            'role': current_user['role']
        })
        
        return jsonify({
            'success': True,
            'validation_result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Attendance validation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/search-knowledge', methods=['POST'])
@jwt_required()
async def search_knowledge_base():
    """Search knowledge base using QA Agent"""
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({'error': 'Search query is required'}), 400
        
        query = data['query']
        
        # Execute search tool
        result = await orchestrator.execute_tool('qa', 'search_knowledge_base', {
            'query': query,
            'user_id': current_user['user_id'],
            'role': current_user['role']
        })
        
        return jsonify({
            'success': True,
            'search_results': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Knowledge search error: {str(e)}")
        return jsonify({'error': str(e)}), 500
