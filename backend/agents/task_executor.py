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
        # Initialize agents (will be initialized when needed to avoid circular imports)
        self.query_agent = None
        self.retrieval_agent = None
        self.synthesis_agent = None
        self.generation_agent = None
        self.conversation_agent = None
        
        # Task execution context
        self.execution_context = {}
        self.progress_callback = None
        
    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Set callback function for progress updates"""
        self.progress_callback = callback
    
    async def _initialize_agents(self):
        """Initialize agents when needed"""
        if self.query_agent is None:
            self.query_agent = QueryUnderstandingAgent()
        if self.retrieval_agent is None:
            # Import and initialize vector store with required parameters
            from rag.vector_store import ChromaDBVectorStore
            from rag.embeddings import EmbeddingManager
            
            # Initialize embedding manager
            embedding_manager = EmbeddingManager()
            
            # Initialize vector store with proper parameters
            store_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'vector_store')
            vector_store = ChromaDBVectorStore(store_path=store_path, embedding_manager=embedding_manager)
            
            self.retrieval_agent = KnowledgeRetrievalAgent(vector_store)
        if self.synthesis_agent is None:
            self.synthesis_agent = ContextSynthesisAgent()
        if self.generation_agent is None:
            # Load API key from environment variables
            groq_api_key = os.environ.get('GROQ_API_KEY')
            if not groq_api_key or groq_api_key == 'your_groq_api_key_here':
                logger.warning("GROQ_API_KEY not found in environment variables")
                print("GROQ_API_KEY not found in environment variables")
            self.generation_agent = ResponseGenerationAgent(api_key=groq_api_key)
        if self.conversation_agent is None:
            # Import and initialize memory manager
            from utils.memory import MemoryManager
            memory_manager = MemoryManager()
            self.conversation_agent = ConversationManagerAgent(memory_manager)
    
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
            
            # Initialize agents
            await self._initialize_agents()
            
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
        
        # Add context from previous tasks based on task type
        if task.task_type == TaskType.KNOWLEDGE_RETRIEVAL:
            # Get query analysis from previous task
            for dep_task_id in task.dependencies:
                if dep_task_id in self.execution_context:
                    dep_result = self.execution_context[dep_task_id]
                    if 'query_analysis' in dep_result:
                        params['query_analysis'] = dep_result['query_analysis']
                    else:
                        params['query_analysis'] = dep_result
                    break
                    
        elif task.task_type == TaskType.DATA_QUERY:
            # Get query analysis for database queries
            for dep_task_id in task.dependencies:
                if dep_task_id in self.execution_context:
                    dep_result = self.execution_context[dep_task_id]
                    if 'query_analysis' in dep_result:
                        params['query_analysis'] = dep_result['query_analysis']
                    else:
                        params['query_analysis'] = dep_result
                    break
                    
        elif task.task_type == TaskType.CONTEXT_SYNTHESIS:
            # Get search results and query analysis
            search_results = []
            query_analysis = {}
            
            for dep_task_id in task.dependencies:
                if dep_task_id in self.execution_context:
                    dep_result = self.execution_context[dep_task_id]
                    
                    # Check if this is retrieval results
                    if 'search_results' in dep_result:
                        search_results.extend(dep_result['search_results'])
                    # Check if this is data query results
                    elif 'mongodb_result' in dep_result:
                        # Convert MongoDB results to search results format
                        mongodb_data = dep_result['mongodb_result']
                        if 'data' in mongodb_data:
                            for item in mongodb_data['data']:
                                search_results.append({
                                    'content': str(item),
                                    'metadata': {'source': 'mongodb', 'type': 'database_record'},
                                    'score': 1.0
                                })
                    # Check if this is data query with search_results
                    elif 'search_results' in dep_result:
                        search_results.extend(dep_result['search_results'])
                    # Check if this is query analysis
                    elif 'query_analysis' in dep_result:
                        query_analysis = dep_result['query_analysis']
                    else:
                        query_analysis = dep_result
            
            params['search_results'] = search_results
            params['query_analysis'] = query_analysis
            
        elif task.task_type == TaskType.RESPONSE_GENERATION:
            # Get comprehensive context and query analysis
            comprehensive_context = ""
            query_analysis = {}
            
            for dep_task_id in task.dependencies:
                if dep_task_id in self.execution_context:
                    dep_result = self.execution_context[dep_task_id]
                    
                    if 'comprehensive_context' in dep_result:
                        comprehensive_context = dep_result['comprehensive_context']
                    elif 'search_results' in dep_result:
                        # Build context from search results
                        context_parts = []
                        for result in dep_result['search_results']:
                            context_parts.append(f"Source: {result.get('content', '')}")
                        comprehensive_context = "\n\n".join(context_parts)
                    elif 'mongodb_result' in dep_result:
                        # Build context from MongoDB results
                        mongodb_data = dep_result['mongodb_result']
                        if 'data' in mongodb_data:
                            context_parts = []
                            for item in mongodb_data['data']:
                                context_parts.append(f"Database Record: {str(item)}")
                            comprehensive_context = "\n\n".join(context_parts)
                    
                    if 'query_analysis' in dep_result:
                        query_analysis = dep_result['query_analysis']
                    elif not query_analysis:
                        query_analysis = dep_result
            
            # If we still don't have context, try to get it from any available source
            if not comprehensive_context:
                for ctx_task_id, ctx_result in self.execution_context.items():
                    if 'search_results' in ctx_result and ctx_result['search_results']:
                        context_parts = []
                        for result in ctx_result['search_results']:
                            context_parts.append(f"Source: {result.get('content', '')}")
                        comprehensive_context = "\n\n".join(context_parts)
                        break
                    elif 'mongodb_result' in ctx_result and ctx_result['mongodb_result'].get('data'):
                        context_parts = []
                        for item in ctx_result['mongodb_result']['data']:
                            context_parts.append(f"Database Record: {str(item)}")
                        comprehensive_context = "\n\n".join(context_parts)
                        break
            
            params['comprehensive_context'] = comprehensive_context
            params['query_analysis'] = query_analysis
            
        elif task.task_type == TaskType.CONVERSATION_UPDATE:
            # Get the final response from generation task
            for dep_task_id in task.dependencies:
                if dep_task_id in self.execution_context:
                    dep_result = self.execution_context[dep_task_id]
                    if 'response' in dep_result:
                        params['response'] = dep_result['response']
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
        elif any(word in query_lower for word in ["leave", "attendance", "policy", "policies", "procedure", "procedures"]):
            collection = "documents"  # Look for policy documents
        else:
            collection = "documents"  # Default
        
        # Execute appropriate MongoDB tool
        print(f"\n=== TASK EXECUTOR DEBUG - Data Query ===")
        print(f"Query: {query}")
        print(f"Collection: {collection}")
        
        if any(word in query_lower for word in ["count", "sum", "average", "group by", "aggregate"]):
            result = await mongodb_tools.aggregate_data_tool(query, collection)
        else:
            result = await mongodb_tools.search_database_tool(query, collection)
        
        print(f"MongoDB Result: {result}")
        
        # Store result with proper key for context flow
        self.execution_context['data_query'] = {
            'mongodb_result': result,
            'search_results': self._convert_mongodb_to_search_results(result)
        }
        
        print(f"Converted search results: {self.execution_context['data_query']['search_results']}")
        return self.execution_context['data_query']
    
    def _convert_mongodb_to_search_results(self, mongodb_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert MongoDB results to search results format"""
        search_results = []
        
        if 'data' in mongodb_result and mongodb_result['data']:
            for item in mongodb_result['data']:
                search_results.append({
                    'content': str(item),
                    'metadata': {
                        'source': 'mongodb',
                        'type': 'database_record',
                        'collection': 'documents'
                    },
                    'score': 1.0
                })
        
        return search_results

    async def _execute_context_synthesis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute context synthesis task"""
        result = await self.synthesis_agent.process(params)
        self.execution_context['synthesis'] = result
        return result

    async def _execute_response_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute response generation task"""
        print(f"\n=== TASK EXECUTOR DEBUG - Response Generation ===")
        print(f"Params received: {params}")
        print(f"Execution context keys: {list(self.execution_context.keys())}")
        for key, value in self.execution_context.items():
            print(f"Context {key}: {str(value)[:200]}...")
        
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
