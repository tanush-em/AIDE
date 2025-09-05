import asyncio
import logging
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.task_decomposer import Task, TaskStatus, TaskType
from agents.query_agent import QueryUnderstandingAgent
from agents.retrieval_agent import KnowledgeRetrievalAgent
from agents.synthesis_agent import ContextSynthesisAgent
from agents.generation_agent import ResponseGenerationAgent
from agents.conversation_agent import ConversationManagerAgent
from agents.mongodb_tools import mongodb_tools

logger = logging.getLogger(__name__)

class TaskExecutor:
    """Executes tasks sequentially with real-time progress updates"""
    
    def __init__(self):
        # Initialize agents
        self.query_agent = QueryUnderstandingAgent()
        self.retrieval_agent = KnowledgeRetrievalAgent()
        self.synthesis_agent = ContextSynthesisAgent()
        self.generation_agent = ResponseGenerationAgent()
        self.conversation_agent = ConversationManagerAgent()
        
        # Task execution context
        self.execution_context = {}
        self.progress_callback = None
        
    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set callback function for progress updates"""
        self.progress_callback = callback
    
    async def execute_tasks(self, tasks: List[Task]) -> Dict[str, Any]:
        """
        Execute tasks sequentially
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            Final execution result
        """
        try:
            logger.info(f"Starting execution of {len(tasks)} tasks")
            
            completed_tasks = []
            failed_tasks = []
            execution_results = {}
            
            # Send initial progress update
            await self._send_progress_update({
                'status': 'started',
                'total_tasks': len(tasks),
                'completed_tasks': 0,
                'current_task': None,
                'tasks': [task.to_dict() for task in tasks]
            })
            
            # Execute tasks sequentially
            for i, task in enumerate(tasks):
                try:
                    # Check if task is ready to execute
                    if not self._is_task_ready(task, completed_tasks):
                        logger.warning(f"Task {task.task_id} dependencies not met, skipping")
                        task.status = TaskStatus.SKIPPED
                        continue
                    
                    # Update task status
                    task.status = TaskStatus.IN_PROGRESS
                    task.started_at = datetime.now(timezone.utc)
                    
                    # Send progress update
                    await self._send_progress_update({
                        'status': 'in_progress',
                        'total_tasks': len(tasks),
                        'completed_tasks': len(completed_tasks),
                        'current_task': task.to_dict(),
                        'tasks': [t.to_dict() for t in tasks]
                    })
                    
                    # Execute the task
                    logger.info(f"Executing task {task.task_id}: {task.description}")
                    result = await self._execute_single_task(task)
                    
                    # Update task with result
                    task.result = result
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now(timezone.utc)
                    
                    # Store result in execution context for dependent tasks
                    execution_results[task.task_id] = result
                    completed_tasks.append(task.task_id)
                    
                    logger.info(f"Task {task.task_id} completed successfully")
                    
                except Exception as e:
                    logger.error(f"Task {task.task_id} failed: {str(e)}")
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    task.completed_at = datetime.now(timezone.utc)
                    failed_tasks.append(task.task_id)
                    
                    # Send error update
                    await self._send_progress_update({
                        'status': 'error',
                        'total_tasks': len(tasks),
                        'completed_tasks': len(completed_tasks),
                        'current_task': task.to_dict(),
                        'error': str(e),
                        'tasks': [t.to_dict() for t in tasks]
                    })
                    
                    # For now, continue with other tasks even if one fails
                    # In the future, we might want to implement retry logic or stop execution
            
            # Send final progress update
            await self._send_progress_update({
                'status': 'completed',
                'total_tasks': len(tasks),
                'completed_tasks': len(completed_tasks),
                'failed_tasks': len(failed_tasks),
                'tasks': [task.to_dict() for task in tasks]
            })
            
            # Prepare final result
            final_result = self._prepare_final_result(tasks, execution_results)
            
            logger.info(f"Task execution completed. {len(completed_tasks)} successful, {len(failed_tasks)} failed")
            return final_result
            
        except Exception as e:
            logger.error(f"Error in task execution: {str(e)}")
            await self._send_progress_update({
                'status': 'error',
                'error': str(e),
                'tasks': [task.to_dict() for task in tasks]
            })
            raise

    def _is_task_ready(self, task: Task, completed_tasks: List[str]) -> bool:
        """Check if task dependencies are met"""
        return all(dep in completed_tasks for dep in task.dependencies)

    async def _execute_single_task(self, task: Task) -> Dict[str, Any]:
        """Execute a single task based on its type"""
        try:
            # Prepare parameters with context from previous tasks
            params = self._prepare_task_parameters(task)
            
            if task.task_type == TaskType.QUERY_ANALYSIS:
                return await self._execute_query_analysis(params)
            elif task.task_type == TaskType.KNOWLEDGE_RETRIEVAL:
                return await self._execute_knowledge_retrieval(params)
            elif task.task_type == TaskType.DATA_QUERY:
                return await self._execute_data_query(params)
            elif task.task_type == TaskType.CONTEXT_SYNTHESIS:
                return await self._execute_context_synthesis(params)
            elif task.task_type == TaskType.RESPONSE_GENERATION:
                return await self._execute_response_generation(params)
            elif task.task_type == TaskType.CONVERSATION_UPDATE:
                return await self._execute_conversation_update(params)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
                
        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {str(e)}")
            raise

    def _prepare_task_parameters(self, task: Task) -> Dict[str, Any]:
        """Prepare task parameters with context from previous tasks"""
        params = task.parameters.copy()
        
        # Add context from previous tasks
        for dep_task_id in task.dependencies:
            if dep_task_id in self.execution_context:
                dep_result = self.execution_context[dep_task_id]
                
                # Map dependency results to current task parameters
                if task.task_type == TaskType.KNOWLEDGE_RETRIEVAL:
                    if 'query_analysis' not in params:
                        params['query_analysis'] = dep_result
                elif task.task_type == TaskType.CONTEXT_SYNTHESIS:
                    if 'search_results' not in params:
                        params['search_results'] = dep_result.get('search_results', [])
                elif task.task_type == TaskType.RESPONSE_GENERATION:
                    if 'comprehensive_context' not in params:
                        params['comprehensive_context'] = dep_result.get('comprehensive_context', '')
                    if 'query_analysis' not in params:
                        # Find query analysis from earlier tasks
                        for ctx_task_id, ctx_result in self.execution_context.items():
                            if 'query_analysis' in ctx_result:
                                params['query_analysis'] = ctx_result['query_analysis']
                                break
        
        return params

    async def _execute_query_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query analysis task"""
        result = await self.query_agent.process(params)
        self.execution_context['query_analysis'] = result
        return result

    async def _execute_knowledge_retrieval(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute knowledge retrieval task"""
        result = await self.retrieval_agent.process(params)
        self.execution_context['retrieval'] = result
        return result

    async def _execute_data_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute database query task"""
        # Use MongoDB tools for data queries
        query = params.get('query', '')
        
        # Determine collection and tool based on query content
        query_lower = query.lower()
        if any(word in query_lower for word in ["user", "users", "person", "people"]):
            collection = "users"
        elif any(word in query_lower for word in ["document", "documents", "file", "files"]):
            collection = "documents"
        elif any(word in query_lower for word in ["conversation", "conversations", "chat", "session"]):
            collection = "conversations"
        else:
            collection = "documents"  # Default
        
        # Execute appropriate MongoDB tool
        if any(word in query_lower for word in ["count", "sum", "average", "group by", "aggregate"]):
            result = await mongodb_tools.aggregate_data_tool(query, collection)
        else:
            result = await mongodb_tools.search_database_tool(query, collection)
        
        self.execution_context['data_query'] = result
        return result

    async def _execute_context_synthesis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute context synthesis task"""
        result = await self.synthesis_agent.process(params)
        self.execution_context['synthesis'] = result
        return result

    async def _execute_response_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute response generation task"""
        result = await self.generation_agent.process(params)
        self.execution_context['generation'] = result
        return result

    async def _execute_conversation_update(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute conversation update task"""
        result = await self.conversation_agent.process(params)
        self.execution_context['conversation_update'] = result
        return result

    def _prepare_final_result(self, tasks: List[Task], execution_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare the final result from task execution"""
        # Get the final response from the generation task
        final_response = None
        confidence = 'medium'
        suggestions = []
        
        for task in tasks:
            if task.task_type == TaskType.RESPONSE_GENERATION and task.result:
                final_response = task.result.get('response', '')
                confidence = task.result.get('confidence', 'medium')
                suggestions = task.result.get('suggestions', [])
                break
        
        # If no generation task result, create a fallback response
        if not final_response:
            final_response = "I've processed your request, but encountered some issues generating a response."
            confidence = 'low'
        
        return {
            'response': final_response,
            'confidence': confidence,
            'suggestions': suggestions,
            'task_execution_summary': {
                'total_tasks': len(tasks),
                'completed_tasks': len([t for t in tasks if t.status == TaskStatus.COMPLETED]),
                'failed_tasks': len([t for t in tasks if t.status == TaskStatus.FAILED]),
                'skipped_tasks': len([t for t in tasks if t.status == TaskStatus.SKIPPED])
            },
            'execution_results': execution_results,
            'tasks': [task.to_dict() for task in tasks]
        }

    async def _send_progress_update(self, update_data: Dict[str, Any]):
        """Send progress update via callback"""
        if self.progress_callback:
            try:
                await self.progress_callback(update_data)
            except Exception as e:
                logger.error(f"Error sending progress update: {str(e)}")
