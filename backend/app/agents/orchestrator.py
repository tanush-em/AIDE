from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from .base_agent import BaseAgent
from .leave_agent import LeaveAgent
from .attendance_agent import AttendanceAgent
from .event_agent import EventAgent
from .qa_agent import QAAgent
import asyncio

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates multiple AI agents for comprehensive query handling"""
    
    def __init__(self):
        self.agents = {}
        self.agent_health = {}
        self.initialize_agents()
    
    def initialize_agents(self):
        """Initialize all available agents"""
        try:
            self.agents = {
                "leave": LeaveAgent(),
                "attendance": AttendanceAgent(),
                "event": EventAgent(),
                "qa": QAAgent()
            }
            
            # Initialize health status
            for agent_name, agent in self.agents.items():
                self.agent_health[agent_name] = {
                    "status": "active",
                    "last_used": None,
                    "usage_count": 0,
                    "error_count": 0
                }
            
            logger.info(f"✅ Initialized {len(self.agents)} agents: {list(self.agents.keys())}")
            
        except Exception as e:
            logger.error(f"❌ Error initializing agents: {e}")
    
    async def route_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Route query to the most appropriate agent(s)"""
        try:
            # Determine which agent(s) should handle the query
            target_agents = self._determine_target_agents(query)
            
            if not target_agents:
                # Default to QA agent if no specific agent is identified
                target_agents = ["qa"]
            
            # Process with the primary agent
            primary_agent = target_agents[0]
            result = await self._process_with_agent(primary_agent, query, context)
            
            # If multiple agents are relevant, get additional insights
            if len(target_agents) > 1:
                additional_insights = await self._get_additional_insights(target_agents[1:], query, context)
                result["additional_insights"] = additional_insights
            
            # Add orchestration metadata
            result["orchestration"] = {
                "primary_agent": primary_agent,
                "target_agents": target_agents,
                "routing_confidence": self._calculate_routing_confidence(query, target_agents),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in query routing: {e}")
            return {
                "success": False,
                "error": f"Error routing query: {str(e)}",
                "orchestrator": "AgentOrchestrator"
            }
    
    def _determine_target_agents(self, query: str) -> List[str]:
        """Determine which agents should handle the query"""
        query_lower = query.lower()
        target_agents = []
        
        # Check for leave-related keywords
        leave_keywords = ["leave", "vacation", "sick", "medical", "personal", "absence", "time off"]
        if any(keyword in query_lower for keyword in leave_keywords):
            target_agents.append("leave")
        
        # Check for attendance-related keywords
        attendance_keywords = ["attendance", "present", "absent", "late", "mark", "track", "percentage"]
        if any(keyword in query_lower for keyword in attendance_keywords):
            target_agents.append("attendance")
        
        # Check for event-related keywords
        event_keywords = ["event", "workshop", "seminar", "conference", "register", "participate", "capacity"]
        if any(keyword in query_lower for keyword in event_keywords):
            target_agents.append("event")
        
        # If no specific domain is identified, use QA agent
        if not target_agents:
            target_agents.append("qa")
        
        return target_agents
    
    async def _process_with_agent(self, agent_name: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process query with a specific agent"""
        try:
            if agent_name not in self.agents:
                return {
                    "success": False,
                    "error": f"Agent {agent_name} not found"
                }
            
            agent = self.agents[agent_name]
            
            # Update health status
            self.agent_health[agent_name]["last_used"] = datetime.utcnow()
            self.agent_health[agent_name]["usage_count"] += 1
            
            # Process query
            result = await agent.process_query(query, context)
            
            # Update health status based on result
            if result.get("success", False):
                self.agent_health[agent_name]["error_count"] = 0
            else:
                self.agent_health[agent_name]["error_count"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing with agent {agent_name}: {e}")
            self.agent_health[agent_name]["error_count"] += 1
            
            return {
                "success": False,
                "error": f"Error processing with {agent_name} agent: {str(e)}",
                "agent": agent_name
            }
    
    async def _get_additional_insights(self, agent_names: List[str], query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get additional insights from other relevant agents"""
        insights = []
        
        for agent_name in agent_names:
            try:
                result = await self._process_with_agent(agent_name, query, context)
                if result.get("success", False):
                    insights.append({
                        "agent": agent_name,
                        "insight": result.get("response") or result.get("guidance") or result.get("analysis"),
                        "confidence": result.get("confidence", 0.8)
                    })
            except Exception as e:
                logger.error(f"❌ Error getting insight from {agent_name}: {e}")
        
        return insights
    
    def _calculate_routing_confidence(self, query: str, target_agents: List[str]) -> float:
        """Calculate confidence in routing decision"""
        # Simple confidence calculation based on keyword matches
        query_lower = query.lower()
        keyword_matches = 0
        total_keywords = 0
        
        # Define keywords for each agent
        agent_keywords = {
            "leave": ["leave", "vacation", "sick", "medical", "personal", "absence", "time off"],
            "attendance": ["attendance", "present", "absent", "late", "mark", "track", "percentage"],
            "event": ["event", "workshop", "seminar", "conference", "register", "participate", "capacity"],
            "qa": ["policy", "rule", "guidance", "help", "information", "procedure"]
        }
        
        for agent in target_agents:
            if agent in agent_keywords:
                keywords = agent_keywords[agent]
                total_keywords += len(keywords)
                for keyword in keywords:
                    if keyword in query_lower:
                        keyword_matches += 1
        
        if total_keywords == 0:
            return 0.5  # Default confidence
        
        return min(1.0, keyword_matches / total_keywords + 0.3)  # Add base confidence
    
    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """Get capabilities of all agents"""
        capabilities = {}
        
        for agent_name, agent in self.agents.items():
            try:
                capabilities[agent_name] = {
                    "name": agent.name,
                    "description": agent.description,
                    "capabilities": agent.get_capabilities(),
                    "health": self.agent_health[agent_name]
                }
            except Exception as e:
                logger.error(f"❌ Error getting capabilities for {agent_name}: {e}")
                capabilities[agent_name] = {
                    "error": f"Unable to get capabilities: {str(e)}"
                }
        
        return capabilities
    
    async def execute_tool(self, agent_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool on a specific agent"""
        try:
            if agent_name not in self.agents:
                return {
                    "success": False,
                    "error": f"Agent {agent_name} not found"
                }
            
            agent = self.agents[agent_name]
            result = await agent.execute_tool(tool_name, parameters)
            
            # Update health status
            self.agent_health[agent_name]["last_used"] = datetime.utcnow()
            self.agent_health[agent_name]["usage_count"] += 1
            
            if not result.get("success", False):
                self.agent_health[agent_name]["error_count"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error executing tool {tool_name} on {agent_name}: {e}")
            self.agent_health[agent_name]["error_count"] += 1
            
            return {
                "success": False,
                "error": f"Error executing tool: {str(e)}",
                "agent": agent_name,
                "tool": tool_name
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all agents"""
        return {
            "agents": self.agent_health,
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agent_health.values() if a["status"] == "active"]),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents"""
        health_results = {}
        
        for agent_name, agent in self.agents.items():
            try:
                # Simple health check - try to get capabilities
                capabilities = agent.get_capabilities()
                health_results[agent_name] = {
                    "status": "healthy",
                    "capabilities_count": len(capabilities),
                    "last_check": datetime.utcnow().isoformat()
                }
                
                # Update agent health status
                self.agent_health[agent_name]["status"] = "active"
                
            except Exception as e:
                logger.error(f"❌ Health check failed for {agent_name}: {e}")
                health_results[agent_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
                
                # Update agent health status
                self.agent_health[agent_name]["status"] = "error"
        
        return {
            "health_results": health_results,
            "overall_status": "healthy" if all(r["status"] == "healthy" for r in health_results.values()) else "degraded",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_agent_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for all agents"""
        stats = {}
        
        for agent_name, health in self.agent_health.items():
            stats[agent_name] = {
                "usage_count": health["usage_count"],
                "error_count": health["error_count"],
                "success_rate": (health["usage_count"] - health["error_count"]) / max(health["usage_count"], 1),
                "last_used": health["last_used"].isoformat() if health["last_used"] else None,
                "status": health["status"]
            }
        
        return {
            "agent_statistics": stats,
            "total_queries": sum(h["usage_count"] for h in self.agent_health.values()),
            "total_errors": sum(h["error_count"] for h in self.agent_health.values()),
            "overall_success_rate": sum(h["usage_count"] - h["error_count"] for h in self.agent_health.values()) / max(sum(h["usage_count"] for h in self.agent_health.values()), 1),
            "timestamp": datetime.utcnow().isoformat()
        }
