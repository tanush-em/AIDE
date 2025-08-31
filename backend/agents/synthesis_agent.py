import sys
import os
from typing import Dict, Any, List

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent

class ContextSynthesisAgent(BaseAgent):
    """Agent responsible for synthesizing context from retrieved information and conversation history"""
    
    def __init__(self):
        super().__init__(
            name="Context Synthesis Agent",
            description="Combines retrieved information with conversation history to create comprehensive context"
        )
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize context from multiple sources"""
        query = input_data.get('query', '')
        search_results = input_data.get('search_results', [])
        conversation_history = input_data.get('conversation_history', [])
        query_analysis = input_data.get('query_analysis', {})
        
        # Synthesize context from search results
        synthesized_context = self._synthesize_search_context(search_results, query_analysis)
        
        # Integrate conversation history
        contextualized_history = self._integrate_conversation_history(conversation_history, query)
        
        # Create comprehensive context
        comprehensive_context = self._create_comprehensive_context(
            query, synthesized_context, contextualized_history, query_analysis
        )
        
        return {
            'query': query,
            'synthesized_context': synthesized_context,
            'contextualized_history': contextualized_history,
            'comprehensive_context': comprehensive_context,
            'context_metadata': {
                'sources_used': len(search_results),
                'history_length': len(conversation_history),
                'context_quality': self._assess_context_quality(comprehensive_context)
            }
        }
    
    def _synthesize_search_context(self, search_results: List[Dict[str, Any]], query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize context from search results"""
        if not search_results:
            return {
                'relevant_information': [],
                'key_points': [],
                'sources': [],
                'confidence': 'low'
            }
        
        # Extract key information from search results
        relevant_info = []
        key_points = []
        sources = []
        
        for result in search_results:
            # Add relevant information
            relevant_info.append({
                'content': result['content'],
                'relevance_score': result['relevance_score'],
                'source': result['source'],
                'category': result['category']
            })
            
            # Add key points
            key_points.extend(result.get('key_information', []))
            
            # Add source
            sources.append({
                'source': result['source'],
                'category': result['category'],
                'relevance_score': result['relevance_score']
            })
        
        # Remove duplicate key points
        key_points = list(set(key_points))
        
        # Calculate overall confidence
        avg_relevance = sum(r['relevance_score'] for r in search_results) / len(search_results)
        confidence = 'high' if avg_relevance > 0.8 else 'medium' if avg_relevance > 0.6 else 'low'
        
        return {
            'relevant_information': relevant_info,
            'key_points': key_points,
            'sources': sources,
            'confidence': confidence,
            'average_relevance': avg_relevance
        }
    
    def _integrate_conversation_history(self, conversation_history: List[Dict[str, Any]], current_query: str) -> Dict[str, Any]:
        """Integrate conversation history with current query"""
        if not conversation_history:
            return {
                'relevant_history': [],
                'contextual_clues': [],
                'continuity_indicators': []
            }
        
        # Find relevant historical context
        relevant_history = []
        contextual_clues = []
        continuity_indicators = []
        
        # Look for continuity indicators in the current query
        continuity_words = ['previous', 'earlier', 'before', 'last time', 'as mentioned', 'following up']
        has_continuity = any(word in current_query.lower() for word in continuity_words)
        
        if has_continuity:
            # Include recent conversation history
            recent_history = conversation_history[-3:]  # Last 3 exchanges
            relevant_history = recent_history
            
            # Extract contextual clues
            for exchange in recent_history:
                if exchange.get('role') == 'assistant':
                    contextual_clues.append(exchange.get('content', ''))
        
        # Look for topic continuity
        current_topics = self._extract_topics(current_query)
        for exchange in conversation_history[-5:]:  # Check last 5 exchanges
            if exchange.get('role') == 'user':
                exchange_topics = self._extract_topics(exchange.get('content', ''))
                if any(topic in current_topics for topic in exchange_topics):
                    continuity_indicators.append(exchange)
        
        return {
            'relevant_history': relevant_history,
            'contextual_clues': contextual_clues,
            'continuity_indicators': continuity_indicators,
            'has_continuity': has_continuity
        }
    
    def _create_comprehensive_context(self, query: str, search_context: Dict[str, Any], 
                                    history_context: Dict[str, Any], query_analysis: Dict[str, Any]) -> str:
        """Create comprehensive context for the LLM"""
        context_parts = []
        
        # Add query analysis context
        context_parts.append(f"User Query: {query}")
        context_parts.append(f"Query Intent: {query_analysis.get('intent', 'general_inquiry')}")
        context_parts.append(f"Relevant Domains: {', '.join(query_analysis.get('domains', ['general']))}")
        
        # Add search results context
        if search_context['relevant_information']:
            context_parts.append("\nRelevant Information from Knowledge Base:")
            for info in search_context['relevant_information'][:3]:  # Top 3 results
                context_parts.append(f"- {info['content'][:200]}... (Source: {info['source']})")
        
        # Add key points
        if search_context['key_points']:
            context_parts.append("\nKey Points:")
            for point in search_context['key_points'][:5]:  # Top 5 points
                context_parts.append(f"- {point}")
        
        # Add conversation history context
        if history_context['relevant_history']:
            context_parts.append("\nRelevant Conversation History:")
            for exchange in history_context['relevant_history']:
                role = exchange.get('role', 'unknown')
                content = exchange.get('content', '')[:100]  # Truncate long content
                context_parts.append(f"{role.title()}: {content}...")
        
        # Add contextual clues
        if history_context['contextual_clues']:
            context_parts.append("\nContextual Clues:")
            for clue in history_context['contextual_clues'][:2]:  # Top 2 clues
                context_parts.append(f"- {clue[:150]}...")
        
        return "\n".join(context_parts)
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text"""
        # Simple topic extraction - could be enhanced with NLP
        topics = []
        academic_terms = [
            'attendance', 'leave', 'event', 'grade', 'procedure', 'rule',
            'student', 'faculty', 'course', 'exam', 'assignment'
        ]
        
        text_lower = text.lower()
        for term in academic_terms:
            if term in text_lower:
                topics.append(term)
        
        return topics
    
    def _assess_context_quality(self, context: str) -> str:
        """Assess the quality of the synthesized context"""
        if not context:
            return 'poor'
        
        # Simple quality assessment based on length and structure
        lines = context.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if len(non_empty_lines) < 3:
            return 'poor'
        elif len(non_empty_lines) < 8:
            return 'fair'
        else:
            return 'good'
