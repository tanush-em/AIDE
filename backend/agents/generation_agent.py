import sys
import os
from typing import Dict, Any
import logging

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent

# Setup logging
logger = logging.getLogger(__name__)

class ResponseGenerationAgent(BaseAgent):
    """Agent responsible for generating responses using the Groq LLM or fallback"""
    
    def __init__(self, api_key: str = None, model_name: str = "llama-3.1-8b-instant"):
        super().__init__(
            name="Response Generation Agent",
            description="Generates conversational responses using Groq LLM based on synthesized context"
        )
        
        self.api_key = api_key
        self.model_name = model_name
        self.llm = None
        self.use_fallback = False
        
        # Try to initialize Groq LLM if API key is available
        if api_key and api_key != "your_groq_api_key_here":
            try:
                from langchain_groq import ChatGroq
                self.llm = ChatGroq(
                    groq_api_key=api_key,
                    model_name=model_name,
                    temperature=0.7,
                    max_tokens=1000
                )
                logger.info("Groq LLM initialized successfully")
                print("Groq LLM initialized successfully")
            except ImportError:
                logger.warning("langchain-groq not available, using fallback mode")
                print("langchain-groq not available, using fallback mode")
                self.use_fallback = True
            except Exception as e:
                logger.warning(f"Failed to initialize Groq LLM: {e}, using fallback mode")
                print(f"Failed to initialize Groq LLM: {e}, using fallback mode")
                self.use_fallback = True
        else:
            logger.warning("No GROQ API key provided, using fallback mode")
            print("No GROQ API key provided, using fallback mode")
            self.use_fallback = True
        
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
        """Generate a response using the LLM or fallback"""
        query = input_data.get('query', '')
        comprehensive_context = input_data.get('comprehensive_context', '')
        query_analysis = input_data.get('query_analysis', {})
        information_sufficiency = input_data.get('information_sufficiency', {})
        synthesis_result = input_data.get('synthesis_result', {})
        
        # DEBUG: Print input data
        print(f"\n=== LLM DEBUG - Input Data ===")
        print(f"Query: {query}")
        print(f"Comprehensive Context Length: {len(comprehensive_context)}")
        print(f"Comprehensive Context: {comprehensive_context[:500]}...")
        print(f"Query Analysis: {query_analysis}")
        print(f"Information Sufficiency: {information_sufficiency}")
        print(f"LLM Available: {self.llm is not None}")
        print(f"Using Fallback: {self.use_fallback}")
        
        # Prepare the prompt
        prompt = self._prepare_prompt(query, comprehensive_context, query_analysis, information_sufficiency)
        
        # DEBUG: Print prompt
        print(f"\n=== LLM DEBUG - Prompt ===")
        print(f"Prompt Length: {len(prompt)}")
        print(f"Prompt: {prompt[:1000]}...")
        
        try:
            if self.llm and not self.use_fallback:
                # Generate response using Groq LLM
                print(f"\n=== LLM DEBUG - Calling Groq LLM ===")
                response = await self._generate_response(prompt)
                print(f"LLM Response: {response[:500]}...")
            else:
                # Use fallback response generation
                print(f"\n=== LLM DEBUG - Using Fallback ===")
                response = self._generate_fallback_response(query, comprehensive_context, information_sufficiency)
                print(f"Fallback Response: {response[:500]}...")
            
            # Process and enhance the response
            enhanced_response = self._enhance_response(response, query_analysis, information_sufficiency)
            
            # Extract document sources from synthesis result
            document_sources = []
            if synthesis_result and 'synthesized_context' in synthesis_result:
                sources = synthesis_result['synthesized_context'].get('sources', [])
                for source in sources:
                    document_sources.append({
                        'source': source.get('source', 'Unknown'),
                        'is_priority': source.get('is_priority', False),
                        'relevance_score': source.get('relevance_score', 0.0)
                    })
            
            return {
                'query': query,
                'response': enhanced_response['response'],
                'confidence': enhanced_response['confidence'],
                'suggestions': enhanced_response['suggestions'],
                'document_sources': document_sources,
                'response_metadata': {
                    'model_used': self.model_name if self.llm else 'fallback',
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
            prompt_parts.append(f"\nQuery Analysis:\n{query_analysis}")
        
        # Add information sufficiency
        if information_sufficiency:
            prompt_parts.append(f"\nInformation Sufficiency:\n{information_sufficiency}")
        
        # Add the user's query
        prompt_parts.append(f"\nUser Query: {query}")
        
        return "\n".join(prompt_parts)
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response using Groq LLM"""
        try:
            from langchain.schema import HumanMessage, SystemMessage
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = await self.llm.agenerate([messages])
            return response.generations[0][0].text
            
        except Exception as e:
            logger.error(f"Error generating response with Groq LLM: {e}")
            raise e
    
    def _generate_fallback_response(self, query: str, context: str = "", information_sufficiency: Dict[str, Any] = None) -> str:
        """Generate a fallback response when LLM is not available"""
        try:
            # Simple rule-based response generation
            query_lower = query.lower()
            
            # Check for common academic topics
            if any(word in query_lower for word in ['attendance', 'present', 'absent']):
                response = "Based on the academic rules, attendance is typically tracked and may affect your academic standing. "
                if context and len(context) > 200:
                    response += f"From the available information: {context[:200]}... "
                elif context:
                    response += f"From the available information: {context} "
                response += "For specific attendance policies, please consult your institution's academic handbook."
                
            elif any(word in query_lower for word in ['leave', 'vacation', 'time off']):
                response = "Leave management procedures vary by institution. "
                if context and len(context) > 200:
                    response += f"Here's what I found: {context[:200]}... "
                elif context:
                    response += f"Here's what I found: {context} "
                response += "Please check with your academic advisor for specific leave policies."
                
            elif any(word in query_lower for word in ['grade', 'grading', 'score']):
                response = "Grading policies are important for academic success. "
                if context and len(context) > 200:
                    response += f"Based on the information: {context[:200]}... "
                elif context:
                    response += f"Based on the information: {context} "
                response += "Refer to your course syllabus for specific grading criteria."
                
            elif any(word in query_lower for word in ['rule', 'policy', 'procedure']):
                response = "Academic policies and procedures are designed to ensure fair and consistent practices. "
                if context and len(context) > 200:
                    response += f"Here's relevant information: {context[:200]}... "
                elif context:
                    response += f"Here's relevant information: {context} "
                response += "For detailed policies, please consult your institution's official documentation."
                
            else:
                response = "I understand you're asking about academic management. "
                if context and len(context) > 200:
                    response += f"Here's what I found: {context[:200]}... "
                elif context:
                    response += f"Here's what I found: {context} "
                response += "Could you please provide more specific details about what you'd like to know?"
            
            return response
            
        except Exception as e:
            logger.error(f"Error in fallback response generation: {e}")
            return f"I'm here to help with academic management questions. Your query was: '{query}'. Please provide more specific details about what you need assistance with."
    
    def _enhance_response(self, response: str, query_analysis: Dict[str, Any], 
                         information_sufficiency: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance the response with additional context and suggestions"""
        enhanced = {
            'response': response,
            'confidence': 'medium',
            'suggestions': []
        }
        
        # Adjust confidence based on information sufficiency
        if information_sufficiency and information_sufficiency.get('sufficient', False):
            enhanced['confidence'] = 'high'
        elif information_sufficiency and not information_sufficiency.get('sufficient', True):
            enhanced['confidence'] = 'low'
        
        # Generate suggestions based on query analysis
        if query_analysis:
            domains = query_analysis.get('domains', [])
            if domains:
                enhanced['suggestions'].append(f"Consider asking about related {domains[0]} topics")
            
            intent = query_analysis.get('intent', '')
            if intent == 'information_request':
                enhanced['suggestions'].append("You can ask for more specific details")
            elif intent == 'procedure_help':
                enhanced['suggestions'].append("I can help you understand the step-by-step process")
        
        # Add general suggestions
        enhanced['suggestions'].extend([
            "Feel free to ask follow-up questions",
            "I can help with various academic management topics"
        ])
        
        return enhanced
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get the health status of the generation agent"""
        return {
            'status': 'healthy' if self.llm or self.use_fallback else 'error',
            'model_available': bool(self.llm),
            'fallback_mode': self.use_fallback,
            'model_name': self.model_name if self.llm else 'fallback',
            'api_key_configured': bool(self.api_key and self.api_key != "your_groq_api_key_here")
        }
