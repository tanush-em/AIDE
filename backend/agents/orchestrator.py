import asyncio
import sys
import os
from typing import Dict, Any, List

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.query_agent import QueryUnderstandingAgent
from agents.retrieval_agent import KnowledgeRetrievalAgent
from agents.synthesis_agent import ContextSynthesisAgent
from agents.generation_agent import ResponseGenerationAgent
from agents.conversation_agent import ConversationManagerAgent

class RAGOrchestrator:
    """Orchestrates the execution of all RAG agents"""
    
    def __init__(self, 
                 query_agent: QueryUnderstandingAgent,
                 retrieval_agent: KnowledgeRetrievalAgent,
                 synthesis_agent: ContextSynthesisAgent,
                 generation_agent: ResponseGenerationAgent,
                 conversation_agent: ConversationManagerAgent):
        
        self.query_agent = query_agent
        self.retrieval_agent = retrieval_agent
        self.synthesis_agent = synthesis_agent
        self.generation_agent = generation_agent
        self.conversation_agent = conversation_agent
        
        self.agents = {
            'query': query_agent,
            'retrieval': retrieval_agent,
            'synthesis': synthesis_agent,
            'generation': generation_agent,
            'conversation': conversation_agent
        }
    
    async def process_query(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a query through the complete RAG workflow"""
        query = workflow_data.get('query', '')
        conversation_history = workflow_data.get('conversation_history', [])
        uploaded_documents = workflow_data.get('uploaded_documents', [])
        
        # Track agent status for UI updates
        agent_status = {}
        
        try:
            # Step 1: Query Understanding
            agent_status['query'] = 'processing'
            query_analysis = await self.query_agent.process({
                'query': query
            })
            agent_status['query'] = 'completed'
            
            # Step 2: Knowledge Retrieval
            agent_status['retrieval'] = 'processing'
            retrieval_result = await self.retrieval_agent.process({
                'query': query,
                'query_analysis': query_analysis,
                'max_results': 5,
                'threshold': 0.7,
                'priority_documents': uploaded_documents
            })
            agent_status['retrieval'] = 'completed'
            
            # Step 3: Context Synthesis
            agent_status['synthesis'] = 'processing'
            synthesis_result = await self.synthesis_agent.process({
                'query': query,
                'search_results': retrieval_result.get('search_results', []),
                'conversation_history': conversation_history,
                'query_analysis': query_analysis
            })
            agent_status['synthesis'] = 'completed'
            
            # Step 4: Response Generation
            agent_status['generation'] = 'processing'
            generation_result = await self.generation_agent.process({
                'query': query,
                'comprehensive_context': synthesis_result.get('comprehensive_context', ''),
                'query_analysis': query_analysis,
                'information_sufficiency': retrieval_result.get('information_sufficiency', {}),
                'synthesis_result': synthesis_result
            })
            agent_status['generation'] = 'completed'
            
            # Prepare final response
            final_response = {
                'response': generation_result.get('response', ''),
                'confidence': generation_result.get('confidence', 'medium'),
                'suggestions': generation_result.get('suggestions', []),
                'document_sources': generation_result.get('document_sources', []),
                'agent_status': agent_status,
                'workflow_metadata': {
                    'query_analysis': query_analysis,
                    'retrieval_metadata': retrieval_result.get('search_metadata', {}),
                    'synthesis_metadata': synthesis_result.get('context_metadata', {}),
                    'generation_metadata': generation_result.get('response_metadata', {})
                }
            }
            
            return final_response
            
        except Exception as e:
            # Handle errors and provide fallback response
            agent_status = {agent: 'error' for agent in self.agents.keys()}
            
            return {
                'response': f"I encountered an error while processing your request: {str(e)}. Please try again.",
                'confidence': 'low',
                'suggestions': ['Try rephrasing your question', 'Check your internet connection'],
                'agent_status': agent_status,
                'error': str(e)
            }
    
    async def process_query_parallel(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process query with some agents running in parallel for better performance"""
        query = workflow_data.get('query', '')
        conversation_history = workflow_data.get('conversation_history', [])
        uploaded_documents = workflow_data.get('uploaded_documents', [])
        
        agent_status = {}
        
        try:
            # Step 1: Query Understanding (must be first)
            agent_status['query'] = 'processing'
            query_analysis = await self.query_agent.process({
                'query': query
            })
            agent_status['query'] = 'completed'
            
            # Step 2: Knowledge Retrieval
            agent_status['retrieval'] = 'processing'
            retrieval_result = await self.retrieval_agent.process({
                'query': query,
                'query_analysis': query_analysis,
                'max_results': 5,
                'threshold': 0.3,  # Very low threshold for better retrieval
                'priority_documents': uploaded_documents
            })
            agent_status['retrieval'] = 'completed'
            
            # Step 3: Context Synthesis
            agent_status['synthesis'] = 'processing'
            synthesis_result = await self.synthesis_agent.process({
                'query': query,
                'search_results': retrieval_result.get('search_results', []),
                'conversation_history': conversation_history,
                'query_analysis': query_analysis
            })
            agent_status['synthesis'] = 'completed'
            
            # Step 4: Response Generation
            agent_status['generation'] = 'processing'
            generation_result = await self.generation_agent.process({
                'query': query,
                'comprehensive_context': synthesis_result.get('comprehensive_context', ''),
                'query_analysis': query_analysis,
                'information_sufficiency': retrieval_result.get('information_sufficiency', {}),
                'synthesis_result': synthesis_result
            })
            agent_status['generation'] = 'completed'
            
            return {
                'response': generation_result.get('response', ''),
                'confidence': generation_result.get('confidence', 'medium'),
                'suggestions': generation_result.get('suggestions', []),
                'document_sources': generation_result.get('document_sources', []),
                'agent_status': agent_status,
                'workflow_metadata': {
                    'query_analysis': query_analysis,
                    'retrieval_metadata': retrieval_result.get('search_metadata', {}),
                    'synthesis_metadata': synthesis_result.get('context_metadata', {}),
                    'generation_metadata': generation_result.get('response_metadata', {})
                }
            }
            
        except Exception as e:
            agent_status = {agent: 'error' for agent in self.agents.keys()}
            return {
                'response': f"I encountered an error while processing your request: {str(e)}. Please try again.",
                'confidence': 'low',
                'suggestions': ['Try rephrasing your question', 'Check your internet connection'],
                'agent_status': agent_status,
                'error': str(e)
            }
    
    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all agents"""
        return {
            name: agent.get_status() 
            for name, agent in self.agents.items()
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        agent_statuses = self.get_agent_status()
        
        # Check if all agents are healthy
        healthy_agents = sum(1 for status in agent_statuses.values() 
                           if status['status'] != 'error')
        
        return {
            'total_agents': len(self.agents),
            'healthy_agents': healthy_agents,
            'system_status': 'healthy' if healthy_agents == len(self.agents) else 'degraded',
            'agent_details': agent_statuses
        }
