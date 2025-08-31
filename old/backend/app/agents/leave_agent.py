from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from ..rag.policy_manager import PolicyManager
from ..rag.knowledge_base import KnowledgeBaseManager
import groq
import os

logger = logging.getLogger(__name__)

class LeaveAgent(BaseAgent):
    """Specialized agent for handling leave-related queries and operations"""
    
    def __init__(self):
        super().__init__("LeaveAgent", "Handles leave requests, policy queries, and leave-related operations")
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
            "leave_policy_queries": "Answer questions about leave policies",
            "leave_request_validation": "Validate leave requests against policies",
            "leave_balance_calculation": "Calculate leave balance for students",
            "leave_approval_recommendation": "Provide recommendations for leave approval",
            "leave_statistics": "Generate leave-related statistics and insights",
            "leave_workflow_guidance": "Guide users through leave request process"
        }
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process leave-related queries using AI and RAG"""
        try:
            # Determine query type
            query_type = self._classify_query(query)
            
            # Get relevant context from knowledge base
            relevant_context = await self._get_relevant_context(query, query_type)
            
            # Process based on query type
            if query_type == "policy_query":
                return await self._handle_policy_query(query, relevant_context, context)
            elif query_type == "validation_request":
                return await self._handle_validation_request(query, relevant_context, context)
            elif query_type == "balance_query":
                return await self._handle_balance_query(query, relevant_context, context)
            elif query_type == "approval_recommendation":
                return await self._handle_approval_recommendation(query, relevant_context, context)
            elif query_type == "statistics_request":
                return await self._handle_statistics_request(query, relevant_context, context)
            elif query_type == "workflow_guidance":
                return await self._handle_workflow_guidance(query, relevant_context, context)
            else:
                return await self._handle_general_query(query, relevant_context, context)
                
        except Exception as e:
            logger.error(f"❌ LeaveAgent error: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing query: {str(e)}",
                "agent": self.name
            }
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of leave-related query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["policy", "rule", "regulation", "allowed", "permitted"]):
            return "policy_query"
        elif any(word in query_lower for word in ["validate", "check", "eligible", "valid"]):
            return "validation_request"
        elif any(word in query_lower for word in ["balance", "remaining", "used", "available"]):
            return "balance_query"
        elif any(word in query_lower for word in ["approve", "recommend", "suggestion", "decision"]):
            return "approval_recommendation"
        elif any(word in query_lower for word in ["statistics", "stats", "report", "analytics"]):
            return "statistics_request"
        elif any(word in query_lower for word in ["how to", "process", "submit", "apply"]):
            return "workflow_guidance"
        else:
            return "general_query"
    
    async def _get_relevant_context(self, query: str, query_type: str) -> Dict[str, Any]:
        """Get relevant context from knowledge base and policies"""
        try:
            # Get leave policies
            leave_policies = self.policy_manager.get_leave_policies()
            
            # Search knowledge base for relevant information
            search_results = await self.kb_manager.semantic_search(query, collection="policies", limit=5)
            
            # Get relevant policy sections
            relevant_policies = {}
            for result in search_results:
                if "leave" in result.get("metadata", {}).get("domain", "").lower():
                    relevant_policies[result["id"]] = result["content"]
            
            return {
                "leave_policies": leave_policies,
                "knowledge_base_results": search_results,
                "relevant_policies": relevant_policies,
                "query_type": query_type
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting relevant context: {e}")
            return {}
    
    async def _handle_policy_query(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle leave policy queries"""
        try:
            # Create prompt for policy query
            prompt = f"""
            You are a helpful AI assistant specializing in academic leave policies. 
            Answer the following question about leave policies based on the provided context.
            
            Question: {query}
            
            Context from policies:
            {self._format_policy_context(context)}
            
            User context: {user_context or {}}
            
            Provide a clear, accurate, and helpful response. If the information is not available in the context, say so.
            Include specific policy details when relevant.
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
    
    async def _handle_validation_request(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle leave request validation"""
        try:
            # Extract leave request details from query or context
            leave_details = self._extract_leave_details(query, user_context)
            
            if not leave_details:
                return {
                    "success": False,
                    "error": "Unable to extract leave request details from query"
                }
            
            # Validate against policies
            validation_result = self.policy_manager.validate_leave_request(leave_details)
            
            # Create AI prompt for detailed analysis
            prompt = f"""
            Analyze this leave request validation result and provide detailed feedback.
            
            Leave Request Details: {leave_details}
            Validation Result: {validation_result}
            
            Provide:
            1. Clear explanation of the validation result
            2. Specific policy references
            3. Recommendations for improvement if needed
            4. Next steps for the user
            """
            
            ai_analysis = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "validation_result": validation_result,
                "ai_analysis": ai_analysis,
                "query_type": "validation_request",
                "agent": self.name,
                "confidence": 0.95
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling validation request: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_balance_query(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle leave balance queries"""
        try:
            # Extract student information
            student_id = user_context.get("user_id") if user_context else None
            
            if not student_id:
                return {
                    "success": False,
                    "error": "Student ID required for balance query"
                }
            
            # Get leave balance (this would typically call the database)
            # For now, we'll provide a template response
            balance_info = {
                "student_id": student_id,
                "academic_year": "2024-2025",
                "leave_balances": [
                    {"leave_type": "medical", "total_allowed": 10, "used": 2, "remaining": 8},
                    {"leave_type": "personal", "total_allowed": 5, "used": 1, "remaining": 4},
                    {"leave_type": "academic", "total_allowed": 3, "used": 0, "remaining": 3}
                ]
            }
            
            # Create AI response
            prompt = f"""
            Explain the leave balance information for the student in a clear and helpful way.
            
            Leave Balance: {balance_info}
            Student Query: {query}
            
            Provide:
            1. Clear explanation of the balance
            2. Policy context for each leave type
            3. Recommendations for leave planning
            4. Any important notes or restrictions
            """
            
            ai_explanation = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "leave_balance": balance_info,
                "ai_explanation": ai_explanation,
                "query_type": "balance_query",
                "agent": self.name,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling balance query: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_approval_recommendation(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle leave approval recommendations"""
        try:
            # Extract leave request details
            leave_details = self._extract_leave_details(query, user_context)
            
            if not leave_details:
                return {
                    "success": False,
                    "error": "Unable to extract leave request details"
                }
            
            # Get policy context
            policies = context.get("leave_policies", {})
            
            # Create AI prompt for recommendation
            prompt = f"""
            As a faculty member reviewing a leave request, provide a recommendation based on policies and best practices.
            
            Leave Request: {leave_details}
            Leave Policies: {policies}
            
            Provide:
            1. Recommendation (approve/reject/request_more_info)
            2. Reasoning based on policies
            3. Specific policy references
            4. Suggested remarks for the student
            5. Any additional requirements or conditions
            """
            
            recommendation = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "recommendation": recommendation,
                "leave_details": leave_details,
                "query_type": "approval_recommendation",
                "agent": self.name,
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling approval recommendation: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_statistics_request(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle leave statistics requests"""
        try:
            # This would typically query the database for actual statistics
            # For now, we'll provide template statistics
            stats = {
                "total_requests": 150,
                "approved_requests": 120,
                "rejected_requests": 20,
                "pending_requests": 10,
                "average_processing_time": 2.5,
                "by_leave_type": {
                    "medical": {"total": 80, "approved": 75, "rejected": 5},
                    "personal": {"total": 50, "approved": 35, "rejected": 10},
                    "academic": {"total": 20, "approved": 10, "rejected": 5}
                }
            }
            
            # Create AI analysis
            prompt = f"""
            Analyze these leave request statistics and provide insights.
            
            Statistics: {stats}
            Query: {query}
            
            Provide:
            1. Key insights from the data
            2. Trends and patterns
            3. Recommendations for improvement
            4. Policy implications
            """
            
            ai_analysis = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "statistics": stats,
                "ai_analysis": ai_analysis,
                "query_type": "statistics_request",
                "agent": self.name,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling statistics request: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_workflow_guidance(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle leave workflow guidance"""
        try:
            # Create workflow guidance
            prompt = f"""
            Provide step-by-step guidance for the leave request process.
            
            User Query: {query}
            User Role: {user_context.get('role', 'student') if user_context else 'student'}
            
            Provide:
            1. Step-by-step process
            2. Required documents
            3. Timeline expectations
            4. Common mistakes to avoid
            5. Contact information for help
            """
            
            guidance = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "guidance": guidance,
                "query_type": "workflow_guidance",
                "agent": self.name,
                "confidence": 0.95
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling workflow guidance: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_general_query(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle general leave-related queries"""
        try:
            prompt = f"""
            Answer this general leave-related question based on the available context.
            
            Question: {query}
            Context: {self._format_policy_context(context)}
            User Context: {user_context or {}}
            
            Provide a helpful and accurate response. If you're unsure, say so.
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
                    {"role": "system", "content": "You are a helpful AI assistant specializing in academic leave policies and procedures."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Error getting AI response: {e}")
            return f"Sorry, I encountered an error while processing your request: {str(e)}"
    
    def _format_policy_context(self, context: Dict[str, Any]) -> str:
        """Format policy context for AI prompt"""
        try:
            policies = context.get("leave_policies", {})
            formatted = "Leave Policies:\n"
            
            for policy_type, policy_details in policies.get("leave_types", {}).items():
                formatted += f"\n{policy_type.upper()} LEAVE:\n"
                for key, value in policy_details.items():
                    formatted += f"  {key}: {value}\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Error formatting policy context: {e}")
            return "Policy information not available"
    
    def _extract_leave_details(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract leave request details from query or context"""
        # This is a simplified extraction - in practice, you'd use NLP
        details = {}
        
        if user_context and "leave_request" in user_context:
            details = user_context["leave_request"]
        
        # Add any details that can be extracted from the query
        query_lower = query.lower()
        
        if "medical" in query_lower:
            details["leave_type"] = "medical"
        elif "personal" in query_lower:
            details["leave_type"] = "personal"
        elif "academic" in query_lower:
            details["leave_type"] = "academic"
        
        return details
    
    def _extract_sources(self, context: Dict[str, Any]) -> List[str]:
        """Extract source information from context"""
        sources = []
        
        # Add policy sources
        if context.get("leave_policies"):
            sources.append("Institutional Leave Policies")
        
        # Add knowledge base sources
        kb_results = context.get("knowledge_base_results", [])
        for result in kb_results:
            if "metadata" in result and "source" in result["metadata"]:
                sources.append(result["metadata"]["source"])
        
        return sources
    
    def get_capabilities(self) -> Dict[str, str]:
        """Get agent capabilities"""
        return self.capabilities
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific tools for leave operations"""
        try:
            if tool_name == "validate_leave_request":
                return await self._validate_leave_request_tool(parameters)
            elif tool_name == "calculate_leave_balance":
                return await self._calculate_leave_balance_tool(parameters)
            elif tool_name == "get_leave_statistics":
                return await self._get_leave_statistics_tool(parameters)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"❌ Error executing tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _validate_leave_request_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tool for validating leave requests"""
        try:
            validation_result = self.policy_manager.validate_leave_request(parameters)
            return {
                "success": True,
                "validation_result": validation_result,
                "tool": "validate_leave_request"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _calculate_leave_balance_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tool for calculating leave balance"""
        try:
            student_id = parameters.get("student_id")
            if not student_id:
                return {"success": False, "error": "Student ID required"}
            
            # This would typically query the database
            # For now, return template data
            balance = {
                "student_id": student_id,
                "medical_leave": {"total": 10, "used": 2, "remaining": 8},
                "personal_leave": {"total": 5, "used": 1, "remaining": 4},
                "academic_leave": {"total": 3, "used": 0, "remaining": 3}
            }
            
            return {
                "success": True,
                "balance": balance,
                "tool": "calculate_leave_balance"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_leave_statistics_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tool for getting leave statistics"""
        try:
            # This would typically query the database
            # For now, return template data
            stats = {
                "total_requests": 150,
                "approved": 120,
                "rejected": 20,
                "pending": 10,
                "average_processing_time": 2.5
            }
            
            return {
                "success": True,
                "statistics": stats,
                "tool": "get_leave_statistics"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
