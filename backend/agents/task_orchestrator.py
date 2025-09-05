import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone

from agents.task_decomposer import TaskDecomposer, Task
from agents.task_executor import TaskExecutor

logger = logging.getLogger(__name__)

class TaskOrchestrator:
    """Orchestrates the complete task-based workflow"""
    
    def __init__(self):
        self.task_decomposer = TaskDecomposer()
        self.task_executor = TaskExecutor()
        self.active_sessions = {}  # Track active sessions
        
    async def process_query_with_tasks(self, 
                                     query: str,
                                     conversation_history: List[Dict[str, Any]] = None,
                                     user_id: str = None,
                                     session_id: str = None,
                                     progress_callback: Callable[[Dict[str, Any]], None] = None) -> Dict[str, Any]:
        """
        Process a query using the task-based workflow
        
        Args:
            query: The user's query
            conversation_history: Previous conversation context
            user_id: User identifier
            session_id: Session identifier
            progress_callback: Callback for real-time progress updates
            
        Returns:
            Final response with task execution details
        """
        try:
            logger.info(f"Starting task-based processing for query: {query[:100]}...")
            
            # Set up progress callback
            if progress_callback:
                self.task_executor.set_progress_callback(progress_callback)
            
            # Step 1: Decompose query into tasks
            logger.info("Decomposing query into tasks...")
            tasks = await self.task_decomposer.decompose_query(
                query=query,
                conversation_history=conversation_history or [],
                user_id=user_id,
                session_id=session_id
            )
            
            # Store session info
            if session_id:
                self.active_sessions[session_id] = {
                    'tasks': tasks,
                    'started_at': datetime.now(timezone.utc),
                    'status': 'processing'
                }
            
            # Send initial task list update
            if progress_callback:
                await progress_callback({
                    'status': 'tasks_created',
                    'total_tasks': len(tasks),
                    'tasks': [task.to_dict() for task in tasks],
                    'message': f'Created {len(tasks)} tasks to process your query'
                })
            
            # Step 2: Execute tasks sequentially
            logger.info(f"Executing {len(tasks)} tasks sequentially...")
            execution_result = await self.task_executor.execute_tasks(tasks)
            
            # Update session status
            if session_id and session_id in self.active_sessions:
                self.active_sessions[session_id]['status'] = 'completed'
                self.active_sessions[session_id]['completed_at'] = datetime.now(timezone.utc)
            
            # Prepare final response
            final_response = {
                'response': execution_result.get('response', ''),
                'confidence': execution_result.get('confidence', 'medium'),
                'suggestions': execution_result.get('suggestions', []),
                'task_execution_summary': execution_result.get('task_execution_summary', {}),
                'tasks': execution_result.get('tasks', []),
                'workflow_type': 'task_based',
                'processing_time': self._calculate_processing_time(session_id),
                'session_id': session_id
            }
            
            logger.info("Task-based processing completed successfully")
            return final_response
            
        except Exception as e:
            logger.error(f"Error in task-based processing: {str(e)}")
            
            # Update session status
            if session_id and session_id in self.active_sessions:
                self.active_sessions[session_id]['status'] = 'error'
                self.active_sessions[session_id]['error'] = str(e)
                self.active_sessions[session_id]['completed_at'] = datetime.now(timezone.utc)
            
            # Send error update
            if progress_callback:
                await progress_callback({
                    'status': 'error',
                    'error': str(e),
                    'message': f'Error processing query: {str(e)}'
                })
            
            return {
                'response': f"I encountered an error while processing your request: {str(e)}. Please try again.",
                'confidence': 'low',
                'suggestions': ['Try rephrasing your question', 'Check your internet connection'],
                'error': str(e),
                'workflow_type': 'task_based',
                'session_id': session_id
            }
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific session"""
        return self.active_sessions.get(session_id)
    
    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active sessions"""
        return self.active_sessions.copy()
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a specific session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False
    
    def _calculate_processing_time(self, session_id: str) -> Optional[float]:
        """Calculate total processing time for a session"""
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            if 'started_at' in session and 'completed_at' in session:
                return (session['completed_at'] - session['started_at']).total_seconds()
        return None
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """Get statistics about task execution"""
        total_sessions = len(self.active_sessions)
        completed_sessions = len([s for s in self.active_sessions.values() if s.get('status') == 'completed'])
        error_sessions = len([s for s in self.active_sessions.values() if s.get('status') == 'error'])
        processing_sessions = len([s for s in self.active_sessions.values() if s.get('status') == 'processing'])
        
        return {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'error_sessions': error_sessions,
            'processing_sessions': processing_sessions,
            'success_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        }

# Global task orchestrator instance
task_orchestrator = TaskOrchestrator()
