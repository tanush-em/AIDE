from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from ..rag.policy_manager import PolicyManager
from ..rag.knowledge_base import KnowledgeBaseManager
import groq
import os

logger = logging.getLogger(__name__)

class QAAgent(BaseAgent):
    """Specialized agent for general question answering using RAG"""
    
    def __init__(self):
        super().__init__("QAAgent", "Handles general academic queries and question answering")
        self.policy_manager = PolicyManager()
        self.kb_manager = KnowledgeBaseManager()
        
        # Initialize Groq client
        self.groq_client = groq.Groq(
            api_key=os.getenv('GROQ_API_KEY'),
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = os.getenv('GROQ_MODEL', 'llama3-8b-8192')
        
        # Agent capabilities
        self.capabilities = {
            "general_qa": "Answer general academic questions",
            "policy_queries": "Answer questions about institutional policies",
            "academic_guidance": "Provide academic guidance and information",
            "procedural_queries": "Answer questions about academic procedures",
            "resource_finding": "Help find academic resources and information",
            "multi_domain_qa": "Handle queries across multiple academic domains"
        }
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process general queries using AI and RAG"""
        try:
            # Determine query type
            query_type = self._classify_query(query)
            
            # Get relevant context from knowledge base
            relevant_context = await self._get_relevant_context(query, query_type)
            
            # Process based on query type
            if query_type == "policy_query":
                return await self._handle_policy_query(query, relevant_context, context)
            elif query_type == "academic_guidance":
                return await self._handle_academic_guidance(query, relevant_context, context)
            elif query_type == "procedural_query":
                return await self._handle_procedural_query(query, relevant_context, context)
            elif query_type == "resource_query":
                return await self._handle_resource_query(query, relevant_context, context)
            elif query_type == "multi_domain_query":
                return await self._handle_multi_domain_query(query, relevant_context, context)
            else:
                return await self._handle_general_query(query, relevant_context, context)
                
        except Exception as e:
            logger.error(f"❌ QAAgent error: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing query: {str(e)}",
                "agent": self.name
            }
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["policy", "rule", "regulation", "allowed", "permitted", "required"]):
            return "policy_query"
        elif any(word in query_lower for word in ["guidance", "advice", "help", "how to", "what should"]):
            return "academic_guidance"
        elif any(word in query_lower for word in ["procedure", "process", "step", "form", "application"]):
            return "procedural_query"
        elif any(word in query_lower for word in ["resource", "find", "where", "location", "contact"]):
            return "resource_query"
        elif any(word in query_lower for word in ["attendance", "leave", "event", "notice", "resource"]):
            return "multi_domain_query"
        else:
            return "general_query"
    
    async def _get_relevant_context(self, query: str, query_type: str) -> Dict[str, Any]:
        """Get relevant context from knowledge base and policies"""
        try:
            # Search across all collections
            search_results = await self.kb_manager.semantic_search(query, collection="policies", limit=3)
            notice_results = await self.kb_manager.semantic_search(query, collection="notices", limit=2)
            faq_results = await self.kb_manager.semantic_search(query, collection="faqs", limit=2)
            
            # Get all policy types
            leave_policies = self.policy_manager.get_leave_policies()
            attendance_policies = self.policy_manager.get_attendance_policies()
            event_policies = self.policy_manager.get_event_policies()
            
            # Combine all results
            all_results = search_results + notice_results + faq_results
            
            return {
                "leave_policies": leave_policies,
                "attendance_policies": attendance_policies,
                "event_policies": event_policies,
                "knowledge_base_results": all_results,
                "query_type": query_type
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting relevant context: {e}")
            return {}
    
    async def _handle_policy_query(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle policy-related queries"""
        try:
            # Create prompt for policy query
            prompt = f"""
            You are a helpful AI assistant specializing in academic policies and procedures. 
            Answer the following question about academic policies based on the provided context.
            
            Question: {query}
            
            Available Policy Context:
            {self._format_all_policies(context)}
            
            Knowledge Base Results:
            {self._format_kb_results(context)}
            
            User context: {user_context or {}}
            
            Provide a clear, accurate, and helpful response. If the information is not available in the context, say so.
            Include specific policy details when relevant. Cite sources when possible.
            """
            
            # Get AI response
            response = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "response": response,
                "query_type": "policy_query",
                "agent": self.name,
                "confidence": 0.9,
                "sources": self._extract_sources(context)
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling policy query: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_academic_guidance(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle academic guidance queries"""
        try:
            # Create prompt for academic guidance
            prompt = f"""
            You are a helpful AI assistant providing academic guidance and advice.
            Answer the following question about academic guidance based on the available information.
            
            Question: {query}
            
            Available Information:
            {self._format_all_policies(context)}
            {self._format_kb_results(context)}
            
            User Role: {user_context.get('role', 'student') if user_context else 'student'}
            User Context: {user_context or {}}
            
            Provide:
            1. Clear and actionable guidance
            2. Relevant policy information
            3. Step-by-step instructions if applicable
            4. Best practices and recommendations
            5. Contact information for further assistance
            """
            
            guidance = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "guidance": guidance,
                "query_type": "academic_guidance",
                "agent": self.name,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling academic guidance: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_procedural_query(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle procedural queries"""
        try:
            # Create prompt for procedural guidance
            prompt = f"""
            You are a helpful AI assistant providing procedural guidance for academic processes.
            Answer the following question about academic procedures based on the available information.
            
            Question: {query}
            
            Available Information:
            {self._format_all_policies(context)}
            {self._format_kb_results(context)}
            
            User Role: {user_context.get('role', 'student') if user_context else 'student'}
            User Context: {user_context or {}}
            
            Provide:
            1. Step-by-step procedure explanation
            2. Required documents and forms
            3. Timeline and deadlines
            4. Contact points and responsible parties
            5. Common issues and solutions
            6. Policy compliance requirements
            """
            
            procedure_guide = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "procedure_guide": procedure_guide,
                "query_type": "procedural_query",
                "agent": self.name,
                "confidence": 0.95
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling procedural query: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_resource_query(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle resource finding queries"""
        try:
            # Create prompt for resource finding
            prompt = f"""
            You are a helpful AI assistant helping users find academic resources and information.
            Answer the following question about finding resources based on the available information.
            
            Question: {query}
            
            Available Information:
            {self._format_all_policies(context)}
            {self._format_kb_results(context)}
            
            User Role: {user_context.get('role', 'student') if user_context else 'student'}
            User Context: {user_context or {}}
            
            Provide:
            1. Specific resource recommendations
            2. Location and access information
            3. Contact details for resource providers
            4. Alternative resources if needed
            5. Access requirements and restrictions
            6. Usage guidelines and best practices
            """
            
            resource_info = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "resource_info": resource_info,
                "query_type": "resource_query",
                "agent": self.name,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling resource query: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_multi_domain_query(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle queries that span multiple domains"""
        try:
            # Create prompt for multi-domain query
            prompt = f"""
            You are a helpful AI assistant handling queries that may span multiple academic domains.
            Answer the following question comprehensively using all available information.
            
            Question: {query}
            
            Available Information from Multiple Domains:
            {self._format_all_policies(context)}
            {self._format_kb_results(context)}
            
            User Role: {user_context.get('role', 'student') if user_context else 'student'}
            User Context: {user_context or {}}
            
            Provide:
            1. Comprehensive answer covering all relevant domains
            2. Cross-domain connections and implications
            3. Policy interactions and requirements
            4. Step-by-step guidance if applicable
            5. Important considerations and warnings
            6. Contact information for domain-specific help
            """
            
            comprehensive_answer = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "comprehensive_answer": comprehensive_answer,
                "query_type": "multi_domain_query",
                "agent": self.name,
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling multi-domain query: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_general_query(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle general queries"""
        try:
            prompt = f"""
            You are a helpful AI assistant for academic institutions. 
            Answer this general question based on the available context and your knowledge.
            
            Question: {query}
            
            Available Context:
            {self._format_all_policies(context)}
            {self._format_kb_results(context)}
            
            User Context: {user_context or {}}
            
            Provide a helpful and accurate response. If you're unsure about specific institutional details, say so.
            Focus on providing useful information and guidance.
            """
            
            response = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "response": response,
                "query_type": "general_query",
                "agent": self.name,
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling general query: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from Groq LLM"""
        try:
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for academic institutions, providing accurate and helpful information about policies, procedures, and academic matters."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Error getting AI response: {e}")
            return f"Sorry, I encountered an error while processing your request: {str(e)}"
    
    def _format_all_policies(self, context: Dict[str, Any]) -> str:
        """Format all available policies for AI prompt"""
        try:
            formatted = "Available Policies:\n"
            
            # Leave policies
            if context.get("leave_policies"):
                formatted += "\nLEAVE POLICIES:\n"
                leave_policies = context["leave_policies"]
                for policy_type, details in leave_policies.get("leave_types", {}).items():
                    formatted += f"  {policy_type.upper()} LEAVE:\n"
                    for key, value in details.items():
                        formatted += f"    {key}: {value}\n"
            
            # Attendance policies
            if context.get("attendance_policies"):
                formatted += "\nATTENDANCE POLICIES:\n"
                attendance_policies = context["attendance_policies"]
                for section, details in attendance_policies.items():
                    formatted += f"  {section.upper()}:\n"
                    if isinstance(details, dict):
                        for key, value in details.items():
                            formatted += f"    {key}: {value}\n"
                    else:
                        formatted += f"    {details}\n"
            
            # Event policies
            if context.get("event_policies"):
                formatted += "\nEVENT POLICIES:\n"
                event_policies = context["event_policies"]
                for section, details in event_policies.items():
                    formatted += f"  {section.upper()}:\n"
                    if isinstance(details, dict):
                        for key, value in details.items():
                            formatted += f"    {key}: {value}\n"
                    else:
                        formatted += f"    {details}\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Error formatting policies: {e}")
            return "Policy information not available"
    
    def _format_kb_results(self, context: Dict[str, Any]) -> str:
        """Format knowledge base results for AI prompt"""
        try:
            kb_results = context.get("knowledge_base_results", [])
            if not kb_results:
                return "No additional knowledge base results available."
            
            formatted = "Knowledge Base Results:\n"
            for i, result in enumerate(kb_results, 1):
                formatted += f"\n{i}. Source: {result.get('metadata', {}).get('source', 'Unknown')}\n"
                formatted += f"   Content: {result.get('content', 'No content')[:200]}...\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Error formatting KB results: {e}")
            return "Knowledge base results not available"
    
    def _extract_sources(self, context: Dict[str, Any]) -> List[str]:
        """Extract source information from context"""
        sources = []
        
        # Add policy sources
        if context.get("leave_policies"):
            sources.append("Leave Policies")
        if context.get("attendance_policies"):
            sources.append("Attendance Policies")
        if context.get("event_policies"):
            sources.append("Event Policies")
        
        # Add knowledge base sources
        kb_results = context.get("knowledge_base_results", [])
        for result in kb_results:
            if "metadata" in result and "source" in result["metadata"]:
                sources.append(result["metadata"]["source"])
        
        return list(set(sources))  # Remove duplicates
    
    def get_capabilities(self) -> Dict[str, str]:
        """Get agent capabilities"""
        return self.capabilities
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific tools for QA operations"""
        try:
            if tool_name == "search_knowledge_base":
                return await self._search_knowledge_base_tool(parameters)
            elif tool_name == "get_policy_info":
                return await self._get_policy_info_tool(parameters)
            elif tool_name == "generate_summary":
                return await self._generate_summary_tool(parameters)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"❌ Error executing tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _search_knowledge_base_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tool for searching knowledge base"""
        try:
            query = parameters.get("query")
            if not query:
                return {"success": False, "error": "Query parameter required"}
            
            # Search across all collections
            results = await self.kb_manager.semantic_search(query, collection="policies", limit=5)
            
            return {
                "success": True,
                "results": results,
                "tool": "search_knowledge_base"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_policy_info_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tool for getting policy information"""
        try:
            policy_type = parameters.get("policy_type", "all")
            
            policies = {}
            if policy_type in ["all", "leave"]:
                policies["leave"] = self.policy_manager.get_leave_policies()
            if policy_type in ["all", "attendance"]:
                policies["attendance"] = self.policy_manager.get_attendance_policies()
            if policy_type in ["all", "event"]:
                policies["event"] = self.policy_manager.get_event_policies()
            
            return {
                "success": True,
                "policies": policies,
                "tool": "get_policy_info"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_summary_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tool for generating summaries"""
        try:
            content = parameters.get("content")
            if not content:
                return {"success": False, "error": "Content parameter required"}
            
            prompt = f"Please provide a concise summary of the following content:\n\n{content}"
            summary = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "summary": summary,
                "tool": "generate_summary"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
