import json
import time
from typing import List, Dict, Any
from datetime import datetime
import os

class ConversationMemory:
    """Manages conversation history and session state"""
    
    def __init__(self, session_id: str, max_history: int = 10):
        self.session_id = session_id
        self.max_history = max_history
        self.messages: List[Dict[str, Any]] = []
        self.session_start = time.time()
        self.last_activity = time.time()
        
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to conversation history"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.messages.append(message)
        self.last_activity = time.time()
        
        # Keep only the last max_history messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history"""
        return self.messages.copy()
    
    def get_formatted_history(self) -> str:
        """Get conversation history formatted for LLM context"""
        formatted = []
        for msg in self.messages:
            formatted.append(f"{msg['role'].title()}: {msg['content']}")
        return "\n".join(formatted)
    
    def is_session_active(self, timeout: int = 3600) -> bool:
        """Check if session is still active"""
        return (time.time() - self.last_activity) < timeout
    
    def export_conversation(self, format_type: str = 'json') -> str:
        """Export conversation in specified format"""
        if format_type == 'json':
            return json.dumps({
                'session_id': self.session_id,
                'session_start': datetime.fromtimestamp(self.session_start).isoformat(),
                'messages': self.messages
            }, indent=2)
        elif format_type == 'txt':
            lines = [f"Session ID: {self.session_id}"]
            lines.append(f"Session Start: {datetime.fromtimestamp(self.session_start).isoformat()}")
            lines.append("-" * 50)
            for msg in self.messages:
                lines.append(f"[{msg['timestamp']}] {msg['role'].title()}: {msg['content']}")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def clear_history(self):
        """Clear conversation history"""
        self.messages = []
        self.last_activity = time.time()

class MemoryManager:
    """Manages multiple conversation sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, ConversationMemory] = {}
    
    def get_session(self, session_id: str, max_history: int = 10) -> ConversationMemory:
        """Get or create a conversation session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationMemory(session_id, max_history)
        return self.sessions[session_id]
    
    def cleanup_inactive_sessions(self, timeout: int = 3600):
        """Remove inactive sessions"""
        current_time = time.time()
        inactive_sessions = [
            session_id for session_id, session in self.sessions.items()
            if (current_time - session.last_activity) > timeout
        ]
        
        for session_id in inactive_sessions:
            del self.sessions[session_id]
    
    def get_all_sessions(self) -> Dict[str, ConversationMemory]:
        """Get all active sessions"""
        return self.sessions.copy()
