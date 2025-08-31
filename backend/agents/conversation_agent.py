import sys
import os
from typing import Dict, Any, List
import uuid
import time

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from utils.memory import ConversationMemory, MemoryManager

class ConversationManagerAgent(BaseAgent):
    """Agent responsible for managing conversation sessions and coordinating other agents"""
    
    def __init__(self, memory_manager: MemoryManager):
        super().__init__(
            name="Conversation Manager Agent",
            description="Manages conversation sessions and coordinates the RAG agent workflow"
        )
        self.memory_manager = memory_manager
        self.active_sessions = {}
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a conversation turn and coordinate all agents"""
        session_id = input_data.get('session_id')
        user_message = input_data.get('message', '')
        user_id = input_data.get('user_id', 'default')
        
        # Get or create session
        if not session_id:
            session_id = str(uuid.uuid4())
        
        session = self.memory_manager.get_session(session_id)
        
        # Add user message to history
        session.add_message('user', user_message)
        
        # Get conversation history
        conversation_history = session.get_conversation_history()
        
        # Prepare workflow data
        workflow_data = {
            'session_id': session_id,
            'user_id': user_id,
            'query': user_message,
            'conversation_history': conversation_history,
            'timestamp': time.time()
        }
        
        # Execute the RAG workflow
        result = await self._execute_rag_workflow(workflow_data)
        
        # Add assistant response to history
        session.add_message('assistant', result['response'])
        
        # Prepare response
        response_data = {
            'session_id': session_id,
            'response': result['response'],
            'confidence': result.get('confidence', 'medium'),
            'suggestions': result.get('suggestions', []),
            'agent_status': result.get('agent_status', {}),
            'conversation_length': len(conversation_history) + 2,  # +2 for current exchange
            'session_active': session.is_session_active()
        }
        
        return response_data
    
    async def _execute_rag_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete RAG workflow with all agents"""
        # This will be set by the main application
        if hasattr(self, 'orchestrator'):
            return await self.orchestrator.process_query_parallel(workflow_data)
        else:
            return {
                'response': "I'm processing your request. The RAG workflow is being set up.",
                'confidence': 'medium',
                'suggestions': ['Please wait while I set up the complete system'],
                'agent_status': {'status': 'initializing'}
            }
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a specific session"""
        session = self.memory_manager.get_session(session_id)
        return {
            'session_id': session_id,
            'session_start': session.session_start,
            'last_activity': session.last_activity,
            'message_count': len(session.messages),
            'is_active': session.is_session_active()
        }
    
    def export_conversation(self, session_id: str, format_type: str = 'json') -> str:
        """Export a conversation session"""
        session = self.memory_manager.get_session(session_id)
        return session.export_conversation(format_type)
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a conversation session"""
        if session_id in self.memory_manager.sessions:
            session = self.memory_manager.sessions[session_id]
            session.clear_history()
            return True
        return False
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all active sessions"""
        sessions_info = {}
        for session_id, session in self.memory_manager.sessions.items():
            sessions_info[session_id] = {
                'session_start': session.session_start,
                'last_activity': session.last_activity,
                'message_count': len(session.messages),
                'is_active': session.is_session_active()
            }
        return sessions_info
    
    def cleanup_inactive_sessions(self, timeout: int = 3600):
        """Clean up inactive sessions"""
        self.memory_manager.cleanup_inactive_sessions(timeout)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        active_sessions = self.get_all_sessions()
        active_count = sum(1 for info in active_sessions.values() if info['is_active'])
        
        return {
            'total_sessions': len(active_sessions),
            'active_sessions': active_count,
            'inactive_sessions': len(active_sessions) - active_count,
            'memory_manager_status': 'active',
            'last_cleanup': time.time()
        }
