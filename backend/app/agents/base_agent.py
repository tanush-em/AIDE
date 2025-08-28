from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, llm_client, tools: List, knowledge_base, policy_manager):
        """Initialize base agent with required components"""
        self.name = name
        self.llm = llm_client
        self.tools = {tool.name: tool for tool in tools}
        self.kb = knowledge_base
        self.policy_manager = policy_manager
        self.logger = logging.getLogger(f"agent.{name}")
        
        # Agent state
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        
        self.logger.info(f"✅ Initialized agent: {name}")
    
    @abstractmethod
    async def process_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process user query and return structured response"""
        pass
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific tool with parameters"""
        try:
            if tool_name not in self.tools:
                raise ValueError(f"Tool {tool_name} not found in agent {self.name}")
            
            tool = self.tools[tool_name]
            result = await tool.execute(**parameters)
            
            self.last_activity = datetime.utcnow()
            self.logger.info(f"Executed tool {tool_name} with parameters: {parameters}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error executing tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    def get_relevant_policies(self, domain: str) -> Dict[str, Any]:
        """Get relevant policies for the domain"""
        try:
            policies = self.policy_manager.get_policies(domain)
            self.logger.info(f"Retrieved policies for domain: {domain}")
            return policies
        except Exception as e:
            self.logger.error(f"❌ Error retrieving policies for {domain}: {e}")
            return {}
    
    async def search_knowledge_base(self, query: str, collection: str = "policies", 
                                  n_results: int = 5) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant information"""
        try:
            results = await self.kb.semantic_search(query, collection, n_results)
            self.logger.info(f"Found {len(results)} relevant documents for query: {query}")
            return results
        except Exception as e:
            self.logger.error(f"❌ Error searching knowledge base: {e}")
            return []
    
    def validate_input(self, data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """Validate input data against required fields"""
        try:
            missing_fields = []
            for field in required_fields:
                if field not in data or data[field] is None:
                    missing_fields.append(field)
            
            if missing_fields:
                return {
                    "valid": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}",
                    "missing_fields": missing_fields
                }
            
            return {"valid": True}
            
        except Exception as e:
            self.logger.error(f"❌ Error validating input: {e}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    def format_response(self, success: bool, data: Any = None, error: str = None, 
                       metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format standardized response"""
        response = {
            "success": success,
            "agent": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        
        if error:
            response["error"] = error
        
        if metadata:
            response["metadata"] = metadata
        
        return response
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent"""
        return {
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "available_tools": list(self.tools.keys()),
            "agent_type": self.__class__.__name__
        }
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with their schemas"""
        tools_info = []
        for tool_name, tool in self.tools.items():
            tools_info.append({
                "name": tool_name,
                "description": tool.description,
                "schema": tool.get_schema(),
                "requires_auth": tool.requires_auth
            })
        return tools_info
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the agent"""
        try:
            # Check if LLM client is available
            llm_healthy = hasattr(self.llm, 'client') and self.llm.client is not None
            
            # Check if knowledge base is accessible
            kb_healthy = self.kb is not None
            
            # Check if policy manager is accessible
            policy_healthy = self.policy_manager is not None
            
            # Check if tools are available
            tools_healthy = len(self.tools) > 0
            
            overall_healthy = llm_healthy and kb_healthy and policy_healthy and tools_healthy
            
            return {
                "agent": self.name,
                "healthy": overall_healthy,
                "components": {
                    "llm": llm_healthy,
                    "knowledge_base": kb_healthy,
                    "policy_manager": policy_healthy,
                    "tools": tools_healthy
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed for {self.name}: {e}")
            return {
                "agent": self.name,
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate the agent"""
        self.is_active = False
        self.logger.info(f"Agent {self.name} deactivated")
    
    def activate(self):
        """Activate the agent"""
        self.is_active = True
        self.logger.info(f"Agent {self.name} activated")
