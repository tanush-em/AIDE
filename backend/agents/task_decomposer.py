import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Types of tasks that can be created"""
    QUERY_ANALYSIS = "query_analysis"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    DATA_QUERY = "data_query"
    CONTEXT_SYNTHESIS = "context_synthesis"
    RESPONSE_GENERATION = "response_generation"
    CONVERSATION_UPDATE = "conversation_update"

class TaskStatus(Enum):
    """Status of task execution"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class Task:
    """Represents a single task in the workflow"""
    
    def __init__(self, 
                 task_id: str,
                 task_type: TaskType,
                 description: str,
                 agent_type: str,
                 parameters: Dict[str, Any],
                 dependencies: List[str] = None,
                 priority: int = 1):
        self.task_id = task_id
        self.task_type = task_type
        self.description = description
        self.agent_type = agent_type
        self.parameters = parameters
        self.dependencies = dependencies or []
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None
        self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization"""
        return {
            'task_id': self.task_id,
            'task_type': self.task_type.value,
            'description': self.description,
            'agent_type': self.agent_type,
            'parameters': self.parameters,
            'dependencies': self.dependencies,
            'priority': self.priority,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat()
        }

class TaskDecomposer:
    """Decomposes user queries into a sequence of tasks"""
    
    def __init__(self):
        self.task_templates = {
            TaskType.QUERY_ANALYSIS: {
                'description': 'Analyze and understand the user query',
                'agent_type': 'query_agent',
                'required_params': ['query']
            },
            TaskType.KNOWLEDGE_RETRIEVAL: {
                'description': 'Retrieve relevant knowledge from vector store',
                'agent_type': 'retrieval_agent',
                'required_params': ['query', 'query_analysis']
            },
            TaskType.DATA_QUERY: {
                'description': 'Query structured data from database',
                'agent_type': 'mongodb_tools',
                'required_params': ['query']
            },
            TaskType.CONTEXT_SYNTHESIS: {
                'description': 'Synthesize context from retrieved information',
                'agent_type': 'synthesis_agent',
                'required_params': ['query', 'search_results', 'conversation_history']
            },
            TaskType.RESPONSE_GENERATION: {
                'description': 'Generate final response based on synthesized context',
                'agent_type': 'generation_agent',
                'required_params': ['query', 'comprehensive_context', 'query_analysis']
            },
            TaskType.CONVERSATION_UPDATE: {
                'description': 'Update conversation history',
                'agent_type': 'conversation_agent',
                'required_params': ['query', 'response']
            }
        }

    async def decompose_query(self, 
                            query: str, 
                            conversation_history: List[Dict[str, Any]] = None,
                            user_id: str = None,
                            session_id: str = None) -> List[Task]:
        """
        Decompose a user query into a sequence of tasks
        
        Args:
            query: The user's query
            conversation_history: Previous conversation context
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            List of tasks to execute
        """
        try:
            logger.info(f"Decomposing query: {query[:100]}...")
            
            # Analyze query to determine required tasks
            query_analysis = await self._analyze_query_complexity(query)
            
            # Generate task sequence based on analysis
            tasks = await self._generate_task_sequence(
                query, 
                query_analysis, 
                conversation_history or [],
                user_id,
                session_id
            )
            
            logger.info(f"Generated {len(tasks)} tasks for query")
            return tasks
            
        except Exception as e:
            logger.error(f"Error decomposing query: {str(e)}")
            # Return minimal task sequence as fallback
            return await self._create_fallback_tasks(query, conversation_history or [])

    async def _analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine complexity and required processing"""
        query_lower = query.lower()
        
        # Check for different types of queries
        analysis = {
            'needs_rag': False,
            'needs_database': False,
            'needs_synthesis': False,
            'complexity': 'simple',
            'estimated_tasks': 2
        }
        
        # RAG patterns (conceptual questions)
        rag_patterns = [
            'what is', 'what are', 'how does', 'explain', 'describe',
            'tell me about', 'what does', 'meaning', 'definition',
            'purpose', 'benefits', 'advantages', 'disadvantages'
        ]
        
        # Database patterns (data queries)
        db_patterns = [
            'show me', 'find', 'search for', 'get', 'retrieve', 'list',
            'display', 'view', 'count', 'sum', 'average', 'group by',
            'filter', 'where', 'all users', 'all documents', 'recent',
            'today', 'this week', 'status', 'type', 'category'
        ]
        
        # Check for RAG patterns
        if any(pattern in query_lower for pattern in rag_patterns):
            analysis['needs_rag'] = True
            analysis['estimated_tasks'] += 2
        
        # Check for database patterns
        if any(pattern in query_lower for pattern in db_patterns):
            analysis['needs_database'] = True
            analysis['estimated_tasks'] += 1
        
        # Determine complexity
        if analysis['needs_rag'] and analysis['needs_database']:
            analysis['complexity'] = 'complex'
            analysis['needs_synthesis'] = True
            analysis['estimated_tasks'] += 1
        elif analysis['needs_rag'] or analysis['needs_database']:
            analysis['complexity'] = 'medium'
        else:
            analysis['complexity'] = 'simple'
        
        return analysis

    async def _generate_task_sequence(self, 
                                    query: str,
                                    analysis: Dict[str, Any],
                                    conversation_history: List[Dict[str, Any]],
                                    user_id: str,
                                    session_id: str) -> List[Task]:
        """Generate the sequence of tasks based on query analysis"""
        tasks = []
        task_counter = 1
        
        # Always start with query analysis
        tasks.append(Task(
            task_id=f"task_{task_counter}",
            task_type=TaskType.QUERY_ANALYSIS,
            description="Analyze and understand the user query",
            agent_type="query_agent",
            parameters={
                'query': query,
                'user_id': user_id,
                'session_id': session_id
            },
            priority=1
        ))
        task_counter += 1
        
        # Add knowledge retrieval if needed
        if analysis['needs_rag']:
            tasks.append(Task(
                task_id=f"task_{task_counter}",
                task_type=TaskType.KNOWLEDGE_RETRIEVAL,
                description="Retrieve relevant knowledge from vector store",
                agent_type="retrieval_agent",
                parameters={
                    'query': query,
                    'max_results': 5,
                    'threshold': 0.7
                },
                dependencies=[f"task_{task_counter - 1}"],
                priority=2
            ))
            task_counter += 1
        
        # Add database query if needed
        if analysis['needs_database']:
            tasks.append(Task(
                task_id=f"task_{task_counter}",
                task_type=TaskType.DATA_QUERY,
                description="Query structured data from database",
                agent_type="mongodb_tools",
                parameters={
                    'query': query,
                    'user_id': user_id,
                    'session_id': session_id
                },
                dependencies=[f"task_{task_counter - 1}"],
                priority=2
            ))
            task_counter += 1
        
        # Add context synthesis if complex query
        if analysis['needs_synthesis']:
            tasks.append(Task(
                task_id=f"task_{task_counter}",
                task_type=TaskType.CONTEXT_SYNTHESIS,
                description="Synthesize context from retrieved information",
                agent_type="synthesis_agent",
                parameters={
                    'query': query,
                    'conversation_history': conversation_history
                },
                dependencies=[f"task_{task_counter - 1}", f"task_{task_counter - 2}"],
                priority=3
            ))
            task_counter += 1
        
        # Always end with response generation
        tasks.append(Task(
            task_id=f"task_{task_counter}",
            task_type=TaskType.RESPONSE_GENERATION,
            description="Generate final response based on synthesized context",
            agent_type="generation_agent",
            parameters={
                'query': query,
                'conversation_history': conversation_history
            },
            dependencies=[f"task_{task_counter - 1}"],
            priority=4
        ))
        task_counter += 1
        
        # Add conversation update
        tasks.append(Task(
            task_id=f"task_{task_counter}",
            task_type=TaskType.CONVERSATION_UPDATE,
            description="Update conversation history",
            agent_type="conversation_agent",
            parameters={
                'query': query,
                'user_id': user_id,
                'session_id': session_id
            },
            dependencies=[f"task_{task_counter - 1}"],
            priority=5
        ))
        
        return tasks

    async def _create_fallback_tasks(self, 
                                   query: str, 
                                   conversation_history: List[Dict[str, Any]]) -> List[Task]:
        """Create minimal fallback task sequence"""
        return [
            Task(
                task_id="task_1",
                task_type=TaskType.QUERY_ANALYSIS,
                description="Analyze and understand the user query",
                agent_type="query_agent",
                parameters={'query': query},
                priority=1
            ),
            Task(
                task_id="task_2",
                task_type=TaskType.RESPONSE_GENERATION,
                description="Generate response",
                agent_type="generation_agent",
                parameters={
                    'query': query,
                    'conversation_history': conversation_history
                },
                dependencies=["task_1"],
                priority=2
            )
        ]

    def get_task_dependencies_met(self, task: Task, completed_tasks: List[str]) -> bool:
        """Check if all dependencies for a task are met"""
        return all(dep in completed_tasks for dep in task.dependencies)

    def get_ready_tasks(self, tasks: List[Task], completed_tasks: List[str]) -> List[Task]:
        """Get tasks that are ready to execute (dependencies met)"""
        ready_tasks = []
        for task in tasks:
            if (task.status == TaskStatus.PENDING and 
                self.get_task_dependencies_met(task, completed_tasks)):
                ready_tasks.append(task)
        
        # Sort by priority
        return sorted(ready_tasks, key=lambda t: t.priority)
