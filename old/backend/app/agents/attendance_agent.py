from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from ..rag.policy_manager import PolicyManager
from ..rag.knowledge_base import KnowledgeBaseManager
import groq
import os

logger = logging.getLogger(__name__)

class AttendanceAgent(BaseAgent):
    """Specialized agent for handling attendance-related queries and operations"""
    
    def __init__(self):
        super().__init__("AttendanceAgent", "Handles attendance tracking, analytics, and policy queries")
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
            "attendance_policy_queries": "Answer questions about attendance policies",
            "attendance_analytics": "Generate attendance analytics and insights",
            "attendance_validation": "Validate attendance requirements against policies",
            "attendance_alerts": "Generate attendance alerts and recommendations",
            "attendance_statistics": "Provide detailed attendance statistics",
            "attendance_guidance": "Guide users on attendance requirements"
        }
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process attendance-related queries using AI and RAG"""
        try:
            # Determine query type
            query_type = self._classify_query(query)
            
            # Get relevant context from knowledge base
            relevant_context = await self._get_relevant_context(query, query_type)
            
            # Process based on query type
            if query_type == "policy_query":
                return await self._handle_policy_query(query, relevant_context, context)
            elif query_type == "analytics_request":
                return await self._handle_analytics_request(query, relevant_context, context)
            elif query_type == "validation_request":
                return await self._handle_validation_request(query, relevant_context, context)
            elif query_type == "alerts_request":
                return await self._handle_alerts_request(query, relevant_context, context)
            elif query_type == "statistics_request":
                return await self._handle_statistics_request(query, relevant_context, context)
            elif query_type == "guidance_request":
                return await self._handle_guidance_request(query, relevant_context, context)
            else:
                return await self._handle_general_query(query, relevant_context, context)
                
        except Exception as e:
            logger.error(f"❌ AttendanceAgent error: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing query: {str(e)}",
                "agent": self.name
            }
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of attendance-related query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["policy", "rule", "requirement", "minimum", "allowed"]):
            return "policy_query"
        elif any(word in query_lower for word in ["analytics", "analysis", "trend", "pattern", "insight"]):
            return "analytics_request"
        elif any(word in query_lower for word in ["validate", "check", "compliance", "meet"]):
            return "validation_request"
        elif any(word in query_lower for word in ["alert", "warning", "low", "poor", "concern"]):
            return "alerts_request"
        elif any(word in query_lower for word in ["statistics", "stats", "report", "percentage"]):
            return "statistics_request"
        elif any(word in query_lower for word in ["how to", "improve", "guidance", "help"]):
            return "guidance_request"
        else:
            return "general_query"
    
    async def _get_relevant_context(self, query: str, query_type: str) -> Dict[str, Any]:
        """Get relevant context from knowledge base and policies"""
        try:
            # Get attendance policies
            attendance_policies = self.policy_manager.get_attendance_policies()
            
            # Search knowledge base for relevant information
            search_results = await self.kb_manager.semantic_search(query, collection="policies", limit=5)
            
            # Get relevant policy sections
            relevant_policies = {}
            for result in search_results:
                if "attendance" in result.get("metadata", {}).get("domain", "").lower():
                    relevant_policies[result["id"]] = result["content"]
            
            return {
                "attendance_policies": attendance_policies,
                "knowledge_base_results": search_results,
                "relevant_policies": relevant_policies,
                "query_type": query_type
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting relevant context: {e}")
            return {}
    
    async def _handle_policy_query(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle attendance policy queries"""
        try:
            # Create prompt for policy query
            prompt = f"""
            You are a helpful AI assistant specializing in academic attendance policies. 
            Answer the following question about attendance policies based on the provided context.
            
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
    
    async def _handle_analytics_request(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle attendance analytics requests"""
        try:
            # Extract student/course information
            student_id = user_context.get("user_id") if user_context else None
            course_code = user_context.get("course_code") if user_context else None
            
            # Generate analytics data (this would typically query the database)
            analytics_data = self._generate_analytics_data(student_id, course_code)
            
            # Create AI prompt for analysis
            prompt = f"""
            Analyze this attendance data and provide insights.
            
            Query: {query}
            Analytics Data: {analytics_data}
            User Context: {user_context or {}}
            
            Provide:
            1. Key insights from the data
            2. Trends and patterns
            3. Areas of concern
            4. Recommendations for improvement
            5. Policy compliance analysis
            """
            
            ai_analysis = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "analytics_data": analytics_data,
                "ai_analysis": ai_analysis,
                "query_type": "analytics_request",
                "agent": self.name,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling analytics request: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_validation_request(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle attendance validation requests"""
        try:
            # Extract attendance details
            attendance_details = self._extract_attendance_details(query, user_context)
            
            if not attendance_details:
                return {
                    "success": False,
                    "error": "Unable to extract attendance details from query"
                }
            
            # Validate against policies
            validation_result = self.policy_manager.validate_attendance_requirements(attendance_details)
            
            # Create AI prompt for detailed analysis
            prompt = f"""
            Analyze this attendance validation result and provide detailed feedback.
            
            Attendance Details: {attendance_details}
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
    
    async def _handle_alerts_request(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle attendance alerts requests"""
        try:
            # Generate alerts data (this would typically query the database)
            alerts_data = self._generate_alerts_data(user_context)
            
            # Create AI prompt for alerts analysis
            prompt = f"""
            Analyze these attendance alerts and provide recommendations.
            
            Query: {query}
            Alerts Data: {alerts_data}
            User Context: {user_context or {}}
            
            Provide:
            1. Summary of attendance concerns
            2. Priority of alerts
            3. Specific recommendations for each alert
            4. Preventive measures
            5. Policy compliance notes
            """
            
            ai_analysis = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "alerts_data": alerts_data,
                "ai_analysis": ai_analysis,
                "query_type": "alerts_request",
                "agent": self.name,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling alerts request: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_statistics_request(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle attendance statistics requests"""
        try:
            # Generate statistics data (this would typically query the database)
            stats_data = self._generate_statistics_data(user_context)
            
            # Create AI prompt for statistics analysis
            prompt = f"""
            Analyze these attendance statistics and provide insights.
            
            Query: {query}
            Statistics: {stats_data}
            User Context: {user_context or {}}
            
            Provide:
            1. Key statistical insights
            2. Performance indicators
            3. Comparative analysis
            4. Trends and patterns
            5. Recommendations based on statistics
            """
            
            ai_analysis = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "statistics": stats_data,
                "ai_analysis": ai_analysis,
                "query_type": "statistics_request",
                "agent": self.name,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling statistics request: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_guidance_request(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle attendance guidance requests"""
        try:
            # Create guidance prompt
            prompt = f"""
            Provide guidance on attendance requirements and improvement strategies.
            
            Query: {query}
            User Role: {user_context.get('role', 'student') if user_context else 'student'}
            User Context: {user_context or {}}
            
            Provide:
            1. Clear attendance requirements
            2. Strategies for improvement
            3. Policy compliance guidance
            4. Common mistakes to avoid
            5. Resources for help
            """
            
            guidance = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "guidance": guidance,
                "query_type": "guidance_request",
                "agent": self.name,
                "confidence": 0.95
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling guidance request: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_general_query(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle general attendance-related queries"""
        try:
            prompt = f"""
            Answer this general attendance-related question based on the available context.
            
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
                    {"role": "system", "content": "You are a helpful AI assistant specializing in academic attendance policies and analytics."},
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
            policies = context.get("attendance_policies", {})
            formatted = "Attendance Policies:\n"
            
            for section, details in policies.items():
                formatted += f"\n{section.upper()}:\n"
                if isinstance(details, dict):
                    for key, value in details.items():
                        formatted += f"  {key}: {value}\n"
                else:
                    formatted += f"  {details}\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Error formatting policy context: {e}")
            return "Policy information not available"
    
    def _extract_attendance_details(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract attendance details from query or context"""
        details = {}
        
        if user_context and "attendance_data" in user_context:
            details = user_context["attendance_data"]
        
        # Add any details that can be extracted from the query
        query_lower = query.lower()
        
        if "percentage" in query_lower or "%" in query_lower:
            # Extract percentage if mentioned
            import re
            percentage_match = re.search(r'(\d+)%', query)
            if percentage_match:
                details["attendance_percentage"] = int(percentage_match.group(1))
        
        return details
    
    def _extract_sources(self, context: Dict[str, Any]) -> List[str]:
        """Extract source information from context"""
        sources = []
        
        # Add policy sources
        if context.get("attendance_policies"):
            sources.append("Institutional Attendance Policies")
        
        # Add knowledge base sources
        kb_results = context.get("knowledge_base_results", [])
        for result in kb_results:
            if "metadata" in result and "source" in result["metadata"]:
                sources.append(result["metadata"]["source"])
        
        return sources
    
    def _generate_analytics_data(self, student_id: str = None, course_code: str = None) -> Dict[str, Any]:
        """Generate analytics data (template - would query database in practice)"""
        return {
            "student_id": student_id,
            "course_code": course_code,
            "overall_attendance": 85.5,
            "lecture_attendance": 88.2,
            "lab_attendance": 82.1,
            "tutorial_attendance": 90.0,
            "attendance_trend": "improving",
            "missed_sessions": 8,
            "late_arrivals": 3,
            "policy_compliance": "compliant",
            "recommendations": [
                "Continue current attendance pattern",
                "Focus on lab sessions",
                "Maintain punctuality"
            ]
        }
    
    def _generate_alerts_data(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate alerts data (template - would query database in practice)"""
        return {
            "low_attendance_alerts": [
                {
                    "student_id": "STU001",
                    "course_code": "CS101",
                    "attendance_percentage": 65.0,
                    "threshold": 75.0,
                    "severity": "medium"
                },
                {
                    "student_id": "STU002",
                    "course_code": "MATH101",
                    "attendance_percentage": 45.0,
                    "threshold": 75.0,
                    "severity": "high"
                }
            ],
            "consecutive_absences": [
                {
                    "student_id": "STU003",
                    "course_code": "PHY101",
                    "consecutive_days": 5,
                    "severity": "high"
                }
            ],
            "total_alerts": 3
        }
    
    def _generate_statistics_data(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate statistics data (template - would query database in practice)"""
        return {
            "total_students": 150,
            "average_attendance": 82.5,
            "attendance_distribution": {
                "excellent": 45,
                "good": 60,
                "fair": 30,
                "poor": 15
            },
            "course_performance": {
                "CS101": {"average": 85.2, "total_students": 30},
                "MATH101": {"average": 78.9, "total_students": 25},
                "PHY101": {"average": 81.3, "total_students": 28}
            },
            "session_type_stats": {
                "lecture": {"average": 84.1, "total_sessions": 45},
                "lab": {"average": 79.8, "total_sessions": 30},
                "tutorial": {"average": 87.2, "total_sessions": 20}
            }
        }
    
    def get_capabilities(self) -> Dict[str, str]:
        """Get agent capabilities"""
        return self.capabilities
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific tools for attendance operations"""
        try:
            if tool_name == "validate_attendance":
                return await self._validate_attendance_tool(parameters)
            elif tool_name == "generate_analytics":
                return await self._generate_analytics_tool(parameters)
            elif tool_name == "get_attendance_statistics":
                return await self._get_attendance_statistics_tool(parameters)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"❌ Error executing tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _validate_attendance_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tool for validating attendance requirements"""
        try:
            validation_result = self.policy_manager.validate_attendance_requirements(parameters)
            return {
                "success": True,
                "validation_result": validation_result,
                "tool": "validate_attendance"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_analytics_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tool for generating attendance analytics"""
        try:
            student_id = parameters.get("student_id")
            course_code = parameters.get("course_code")
            
            analytics_data = self._generate_analytics_data(student_id, course_code)
            
            return {
                "success": True,
                "analytics": analytics_data,
                "tool": "generate_analytics"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_attendance_statistics_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tool for getting attendance statistics"""
        try:
            stats_data = self._generate_statistics_data(parameters)
            
            return {
                "success": True,
                "statistics": stats_data,
                "tool": "get_attendance_statistics"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
