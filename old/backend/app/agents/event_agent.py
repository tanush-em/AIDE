from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from ..rag.policy_manager import PolicyManager
from ..rag.knowledge_base import KnowledgeBaseManager
import groq
import os

logger = logging.getLogger(__name__)

class EventAgent(BaseAgent):
    """Specialized agent for handling event-related queries and operations"""
    
    def __init__(self):
        super().__init__("EventAgent", "Handles event management, registration, and coordination")
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
            "event_policy_queries": "Answer questions about event policies",
            "event_creation_guidance": "Guide users through event creation process",
            "registration_management": "Handle event registration queries and issues",
            "event_analytics": "Generate event analytics and insights",
            "capacity_planning": "Provide capacity planning recommendations",
            "event_coordination": "Assist with event coordination and logistics"
        }
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process event-related queries using AI and RAG"""
        try:
            # Determine query type
            query_type = self._classify_query(query)
            
            # Get relevant context from knowledge base
            relevant_context = await self._get_relevant_context(query, query_type)
            
            # Process based on query type
            if query_type == "policy_query":
                return await self._handle_policy_query(query, relevant_context, context)
            elif query_type == "creation_guidance":
                return await self._handle_creation_guidance(query, relevant_context, context)
            elif query_type == "registration_query":
                return await self._handle_registration_query(query, relevant_context, context)
            elif query_type == "analytics_request":
                return await self._handle_analytics_request(query, relevant_context, context)
            elif query_type == "capacity_planning":
                return await self._handle_capacity_planning(query, relevant_context, context)
            elif query_type == "coordination_request":
                return await self._handle_coordination_request(query, relevant_context, context)
            else:
                return await self._handle_general_query(query, relevant_context, context)
                
        except Exception as e:
            logger.error(f"❌ EventAgent error: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing query: {str(e)}",
                "agent": self.name
            }
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of event-related query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["policy", "rule", "regulation", "allowed", "permitted"]):
            return "policy_query"
        elif any(word in query_lower for word in ["create", "organize", "setup", "plan", "arrange"]):
            return "creation_guidance"
        elif any(word in query_lower for word in ["register", "signup", "enroll", "join", "participate"]):
            return "registration_query"
        elif any(word in query_lower for word in ["analytics", "statistics", "report", "insights"]):
            return "analytics_request"
        elif any(word in query_lower for word in ["capacity", "limit", "space", "room", "seats"]):
            return "capacity_planning"
        elif any(word in query_lower for word in ["coordinate", "manage", "organize", "logistics"]):
            return "coordination_request"
        else:
            return "general_query"
    
    async def _get_relevant_context(self, query: str, query_type: str) -> Dict[str, Any]:
        """Get relevant context from knowledge base and policies"""
        try:
            # Get event policies
            event_policies = self.policy_manager.get_event_policies()
            
            # Search knowledge base for relevant information
            search_results = await self.kb_manager.semantic_search(query, collection="policies", limit=5)
            
            # Get relevant policy sections
            relevant_policies = {}
            for result in search_results:
                if "event" in result.get("metadata", {}).get("domain", "").lower():
                    relevant_policies[result["id"]] = result["content"]
            
            return {
                "event_policies": event_policies,
                "knowledge_base_results": search_results,
                "relevant_policies": relevant_policies,
                "query_type": query_type
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting relevant context: {e}")
            return {}
    
    async def _handle_policy_query(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle event policy queries"""
        try:
            # Create prompt for policy query
            prompt = f"""
            You are a helpful AI assistant specializing in academic event policies. 
            Answer the following question about event policies based on the provided context.
            
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
    
    async def _handle_creation_guidance(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle event creation guidance"""
        try:
            # Extract event details from query
            event_details = self._extract_event_details(query, user_context)
            
            # Create AI prompt for creation guidance
            prompt = f"""
            Provide comprehensive guidance for creating an academic event.
            
            User Query: {query}
            Event Details: {event_details}
            User Role: {user_context.get('role', 'faculty') if user_context else 'faculty'}
            
            Event Policies: {self._format_policy_context(context)}
            
            Provide:
            1. Step-by-step event creation process
            2. Required information and documents
            3. Policy compliance requirements
            4. Best practices for event planning
            5. Common mistakes to avoid
            6. Timeline recommendations
            7. Resource requirements
            """
            
            guidance = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "guidance": guidance,
                "event_details": event_details,
                "query_type": "creation_guidance",
                "agent": self.name,
                "confidence": 0.95
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling creation guidance: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_registration_query(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle event registration queries"""
        try:
            # Extract registration details
            registration_details = self._extract_registration_details(query, user_context)
            
            # Generate registration data (this would typically query the database)
            registration_data = self._generate_registration_data(registration_details)
            
            # Create AI prompt for registration guidance
            prompt = f"""
            Provide guidance on event registration and participation.
            
            Query: {query}
            Registration Details: {registration_details}
            Registration Data: {registration_data}
            User Context: {user_context or {}}
            
            Provide:
            1. Registration process explanation
            2. Requirements and eligibility
            3. Timeline and deadlines
            4. Capacity and availability
            5. Cancellation policies
            6. Contact information for issues
            """
            
            guidance = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "guidance": guidance,
                "registration_data": registration_data,
                "query_type": "registration_query",
                "agent": self.name,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling registration query: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_analytics_request(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle event analytics requests"""
        try:
            # Generate analytics data (this would typically query the database)
            analytics_data = self._generate_analytics_data(user_context)
            
            # Create AI prompt for analytics analysis
            prompt = f"""
            Analyze these event analytics and provide insights.
            
            Query: {query}
            Analytics Data: {analytics_data}
            User Context: {user_context or {}}
            
            Provide:
            1. Key insights from the data
            2. Registration trends and patterns
            3. Popular event types and topics
            4. Capacity utilization analysis
            5. Recommendations for improvement
            6. Success metrics and KPIs
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
    
    async def _handle_capacity_planning(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle capacity planning requests"""
        try:
            # Extract capacity requirements
            capacity_details = self._extract_capacity_details(query, user_context)
            
            # Generate capacity recommendations
            capacity_data = self._generate_capacity_data(capacity_details)
            
            # Create AI prompt for capacity planning
            prompt = f"""
            Provide capacity planning recommendations for academic events.
            
            Query: {query}
            Capacity Details: {capacity_details}
            Capacity Data: {capacity_data}
            User Context: {user_context or {}}
            
            Provide:
            1. Capacity recommendations based on event type
            2. Venue and resource requirements
            3. Registration limit suggestions
            4. Waitlist management strategies
            5. Scaling considerations
            6. Risk mitigation for capacity issues
            """
            
            recommendations = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "recommendations": recommendations,
                "capacity_data": capacity_data,
                "query_type": "capacity_planning",
                "agent": self.name,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling capacity planning: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_coordination_request(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle event coordination requests"""
        try:
            # Create coordination guidance
            prompt = f"""
            Provide event coordination and logistics guidance.
            
            Query: {query}
            User Role: {user_context.get('role', 'faculty') if user_context else 'faculty'}
            User Context: {user_context or {}}
            
            Provide:
            1. Event coordination checklist
            2. Timeline management
            3. Resource allocation
            4. Communication strategies
            5. Contingency planning
            6. Stakeholder management
            7. Post-event follow-up
            """
            
            guidance = await self._get_ai_response(prompt)
            
            return {
                "success": True,
                "guidance": guidance,
                "query_type": "coordination_request",
                "agent": self.name,
                "confidence": 0.95
            }
            
        except Exception as e:
            logger.error(f"❌ Error handling coordination request: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_general_query(self, query: str, context: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle general event-related queries"""
        try:
            prompt = f"""
            Answer this general event-related question based on the available context.
            
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
                    {"role": "system", "content": "You are a helpful AI assistant specializing in academic event management and coordination."},
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
            policies = context.get("event_policies", {})
            formatted = "Event Policies:\n"
            
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
    
    def _extract_event_details(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract event details from query or context"""
        details = {}
        
        if user_context and "event_data" in user_context:
            details = user_context["event_data"]
        
        # Add any details that can be extracted from the query
        query_lower = query.lower()
        
        if "workshop" in query_lower:
            details["event_type"] = "workshop"
        elif "seminar" in query_lower:
            details["event_type"] = "seminar"
        elif "conference" in query_lower:
            details["event_type"] = "conference"
        elif "lecture" in query_lower:
            details["event_type"] = "lecture"
        
        return details
    
    def _extract_registration_details(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract registration details from query or context"""
        details = {}
        
        if user_context and "registration_data" in user_context:
            details = user_context["registration_data"]
        
        return details
    
    def _extract_capacity_details(self, query: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract capacity details from query or context"""
        details = {}
        
        if user_context and "capacity_data" in user_context:
            details = user_context["capacity_data"]
        
        # Extract capacity numbers if mentioned
        import re
        capacity_match = re.search(r'(\d+)\s*(people|students|participants)', query.lower())
        if capacity_match:
            details["expected_capacity"] = int(capacity_match.group(1))
        
        return details
    
    def _extract_sources(self, context: Dict[str, Any]) -> List[str]:
        """Extract source information from context"""
        sources = []
        
        # Add policy sources
        if context.get("event_policies"):
            sources.append("Institutional Event Policies")
        
        # Add knowledge base sources
        kb_results = context.get("knowledge_base_results", [])
        for result in kb_results:
            if "metadata" in result and "source" in result["metadata"]:
                sources.append(result["metadata"]["source"])
        
        return sources
    
    def _generate_registration_data(self, registration_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate registration data (template - would query database in practice)"""
        return {
            "total_events": 25,
            "active_registrations": 180,
            "registration_success_rate": 92.5,
            "popular_event_types": {
                "workshop": {"count": 8, "avg_registrations": 15},
                "seminar": {"count": 12, "avg_registrations": 25},
                "conference": {"count": 5, "avg_registrations": 50}
            },
            "capacity_utilization": 78.3,
            "waitlist_requests": 12
        }
    
    def _generate_analytics_data(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate analytics data (template - would query database in practice)"""
        return {
            "total_events": 150,
            "total_registrations": 2500,
            "average_registration_rate": 85.2,
            "event_type_distribution": {
                "workshop": 45,
                "seminar": 60,
                "conference": 25,
                "lecture": 20
            },
            "registration_trends": {
                "monthly_growth": 12.5,
                "popular_topics": ["AI", "Data Science", "Research Methods"],
                "peak_registration_days": ["Monday", "Tuesday"]
            },
            "participant_satisfaction": 4.2,
            "repeat_participants": 35.8
        }
    
    def _generate_capacity_data(self, capacity_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate capacity data (template - would query database in practice)"""
        return {
            "venue_capacity": {
                "small_room": 30,
                "medium_room": 60,
                "large_room": 120,
                "auditorium": 300
            },
            "recommended_capacity": {
                "workshop": 25,
                "seminar": 40,
                "conference": 80,
                "lecture": 100
            },
            "capacity_utilization": {
                "current": 78.3,
                "optimal": 85.0,
                "overbooked": 12.5
            },
            "waitlist_management": {
                "active_waitlists": 8,
                "avg_waitlist_size": 15,
                "conversion_rate": 65.2
            }
        }
    
    def get_capabilities(self) -> Dict[str, str]:
        """Get agent capabilities"""
        return self.capabilities
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific tools for event operations"""
        try:
            if tool_name == "validate_event":
                return await self._validate_event_tool(parameters)
            elif tool_name == "generate_analytics":
                return await self._generate_analytics_tool(parameters)
            elif tool_name == "get_event_statistics":
                return await self._get_event_statistics_tool(parameters)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"❌ Error executing tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _validate_event_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tool for validating event requirements"""
        try:
            validation_result = self.policy_manager.validate_event_registration(parameters)
            return {
                "success": True,
                "validation_result": validation_result,
                "tool": "validate_event"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_analytics_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tool for generating event analytics"""
        try:
            analytics_data = self._generate_analytics_data(parameters)
            
            return {
                "success": True,
                "analytics": analytics_data,
                "tool": "generate_analytics"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_event_statistics_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Tool for getting event statistics"""
        try:
            stats_data = self._generate_analytics_data(parameters)
            
            return {
                "success": True,
                "statistics": stats_data,
                "tool": "get_event_statistics"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
