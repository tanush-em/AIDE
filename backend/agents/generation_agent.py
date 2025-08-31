import sys
import os
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent

class ResponseGenerationAgent(BaseAgent):
    """Agent responsible for generating responses using the Groq LLM"""
    
    def __init__(self, api_key: str, model_name: str = "llama3-8b-8192"):
        super().__init__(
            name="Response Generation Agent",
            description="Generates conversational responses using Groq LLM based on synthesized context"
        )
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=0.7,
            max_tokens=1000
        )
        
        # System prompt for academic management context
        self.system_prompt = """You are an AI assistant for an academic management system. Your role is to help users with questions about academic policies, procedures, rules, and tools.

Key responsibilities:
1. Provide accurate information about academic management topics
2. Help users understand procedures and requirements
3. Offer guidance on attendance, leave management, events, and grading
4. Be conversational and helpful while maintaining professionalism
5. If you don't have enough information, ask for clarification
6. Cite relevant sources when possible

Important guidelines:
- Always be helpful and conversational
- Provide clear, actionable information
- If information is insufficient, suggest what additional details would help
- Maintain a professional but friendly tone
- Focus on academic management topics
- Be concise but comprehensive

Current context and relevant information will be provided to help you answer the user's question accurately."""
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response using the LLM"""
        query = input_data.get('query', '')
        comprehensive_context = input_data.get('comprehensive_context', '')
        query_analysis = input_data.get('query_analysis', {})
        information_sufficiency = input_data.get('information_sufficiency', {})
        
        # Prepare the prompt
        prompt = self._prepare_prompt(query, comprehensive_context, query_analysis, information_sufficiency)
        
        try:
            # Generate response
            response = await self._generate_response(prompt)
            
            # Process and enhance the response
            enhanced_response = self._enhance_response(response, query_analysis, information_sufficiency)
            
            return {
                'query': query,
                'response': enhanced_response['response'],
                'confidence': enhanced_response['confidence'],
                'suggestions': enhanced_response['suggestions'],
                'response_metadata': {
                    'model_used': self.llm.model_name,
                    'response_length': len(enhanced_response['response']),
                    'information_sufficiency': information_sufficiency.get('sufficient', False)
                }
            }
            
        except Exception as e:
            # Fallback response
            fallback_response = self._generate_fallback_response(query, information_sufficiency)
            return {
                'query': query,
                'response': fallback_response,
                'confidence': 'low',
                'suggestions': ['Try rephrasing your question'],
                'error': str(e),
                'response_metadata': {
                    'model_used': 'fallback',
                    'response_length': len(fallback_response),
                    'information_sufficiency': False
                }
            }
    
    def _prepare_prompt(self, query: str, context: str, query_analysis: Dict[str, Any], 
                       information_sufficiency: Dict[str, Any]) -> str:
        """Prepare the prompt for the LLM"""
        prompt_parts = [self.system_prompt]
        
        # Add context information
        if context:
            prompt_parts.append(f"\nContext Information:\n{context}")
        
        # Add query analysis
        if query_analysis:
            intent = query_analysis.get('intent', 'general_inquiry')
            domains = query_analysis.get('domains', ['general'])
            prompt_parts.append(f"\nQuery Analysis:")
            prompt_parts.append(f"- Intent: {intent}")
            prompt_parts.append(f"- Domains: {', '.join(domains)}")
        
        # Add information sufficiency status
        if information_sufficiency:
            sufficient = information_sufficiency.get('sufficient', False)
            reason = information_sufficiency.get('reason', '')
            suggestion = information_sufficiency.get('suggestion', '')
            
            prompt_parts.append(f"\nInformation Status:")
            prompt_parts.append(f"- Sufficient Information: {sufficient}")
            if reason:
                prompt_parts.append(f"- Reason: {reason}")
            if suggestion and not sufficient:
                prompt_parts.append(f"- Suggestion: {suggestion}")
        
        # Add the user query
        prompt_parts.append(f"\nUser Question: {query}")
        prompt_parts.append("\nPlease provide a helpful and accurate response:")
        
        return "\n".join(prompt_parts)
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response using the LLM"""
        messages = [
            SystemMessage(content=prompt)
        ]
        
        response = await self.llm.agenerate([messages])
        return response.generations[0][0].text.strip()
    
    def _enhance_response(self, response: str, query_analysis: Dict[str, Any], 
                         information_sufficiency: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance the generated response"""
        enhanced_response = response
        
        # Add clarification request if information is insufficient
        if not information_sufficiency.get('sufficient', True):
            suggestion = information_sufficiency.get('suggestion', '')
            if suggestion:
                enhanced_response += f"\n\n💡 Tip: {suggestion}"
        
        # Add domain-specific guidance
        domains = query_analysis.get('domains', [])
        if 'attendance' in domains:
            enhanced_response += "\n\n📊 For more detailed attendance information, you can check the attendance management tool."
        elif 'leave' in domains:
            enhanced_response += "\n\n📋 You can submit leave requests through the leave management system."
        elif 'events' in domains:
            enhanced_response += "\n\n📅 Event coordination can be managed through the event platform."
        
        # Calculate confidence based on response quality
        confidence = self._calculate_response_confidence(response, query_analysis, information_sufficiency)
        
        # Generate follow-up suggestions
        suggestions = self._generate_suggestions(query_analysis, information_sufficiency)
        
        return {
            'response': enhanced_response,
            'confidence': confidence,
            'suggestions': suggestions
        }
    
    def _calculate_response_confidence(self, response: str, query_analysis: Dict[str, Any], 
                                     information_sufficiency: Dict[str, Any]) -> str:
        """Calculate confidence in the generated response"""
        # Base confidence on information sufficiency
        if information_sufficiency.get('sufficient', False):
            base_confidence = 0.8
        else:
            base_confidence = 0.4
        
        # Adjust based on response length and quality
        if len(response) > 100:
            base_confidence += 0.1
        
        # Adjust based on query complexity
        complexity = query_analysis.get('complexity', 'moderate')
        if complexity == 'simple':
            base_confidence += 0.1
        elif complexity == 'complex':
            base_confidence -= 0.1
        
        # Determine confidence level
        if base_confidence >= 0.8:
            return 'high'
        elif base_confidence >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def _generate_suggestions(self, query_analysis: Dict[str, Any], 
                            information_sufficiency: Dict[str, Any]) -> list:
        """Generate follow-up suggestions"""
        suggestions = []
        
        domains = query_analysis.get('domains', [])
        
        if 'attendance' in domains:
            suggestions.append("Ask about attendance tracking procedures")
            suggestions.append("Inquire about attendance requirements")
        elif 'leave' in domains:
            suggestions.append("Ask about leave application process")
            suggestions.append("Inquire about leave types and policies")
        elif 'events' in domains:
            suggestions.append("Ask about event planning procedures")
            suggestions.append("Inquire about event approval process")
        elif 'grades' in domains:
            suggestions.append("Ask about grading policies")
            suggestions.append("Inquire about grade submission procedures")
        
        if not information_sufficiency.get('sufficient', True):
            suggestions.append("Try asking a more specific question")
            suggestions.append("Check if your topic is covered in our knowledge base")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def _generate_fallback_response(self, query: str, information_sufficiency: Dict[str, Any]) -> str:
        """Generate a fallback response when LLM fails"""
        if not information_sufficiency.get('sufficient', True):
            return "I'm having trouble finding specific information about your question. Could you please rephrase it or ask about a different aspect of academic management?"
        else:
            return "I'm experiencing technical difficulties right now. Please try asking your question again in a moment."
