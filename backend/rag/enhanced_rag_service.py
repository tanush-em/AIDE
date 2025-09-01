import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from rag.rag_service import RAGService
from agents.query_router import query_router
from database.mongodb_service import mongodb_service
from agents.mongodb_tools import mongodb_tools

logger = logging.getLogger(__name__)

class EnhancedRAGService:
    """Enhanced RAG service that integrates MongoDB alongside vector store"""
    
    def __init__(self):
        self.rag_service = RAGService()
        self.query_router = query_router
        self.mongodb_service = mongodb_service
        self.mongodb_tools = mongodb_tools
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize both RAG and MongoDB services"""
        try:
            # Initialize RAG service
            await self.rag_service.initialize()
            
            # Initialize MongoDB service
            await self.mongodb_service.initialize()
            
            self.is_initialized = True
            logger.info("Enhanced RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced RAG service: {str(e)}")
            self.is_initialized = False
            raise e
    
    async def process_query(self, session_id: str, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a query using intelligent routing between RAG and MongoDB
        
        Args:
            session_id: Session identifier
            query: User's query
            user_id: Optional user identifier
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            start_time = datetime.utcnow()
            
            # Route the query to determine the best approach
            routing_result = await self.query_router.route_query(query, user_id, session_id)
            
            # Process based on routing decision
            if routing_result["route_type"] == "rag":
                result = await self._process_rag_query(session_id, query, user_id, routing_result)
            elif routing_result["route_type"] == "mongodb":
                result = await self._process_mongodb_query(session_id, query, user_id, routing_result)
            elif routing_result["route_type"] == "combined":
                result = await self._process_combined_query(session_id, query, user_id, routing_result)
            else:
                # Fallback to RAG
                result = await self._process_rag_query(session_id, query, user_id, routing_result)
            
            # Add processing metadata
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result["processing_time"] = processing_time
            result["route_type"] = routing_result["route_type"]
            result["query_analysis"] = routing_result.get("query_analysis", {})
            
            # Log analytics
            await self._log_analytics(query, result, user_id, session_id, processing_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "response": f"I encountered an error while processing your request: {str(e)}",
                "confidence": "low",
                "suggestions": ["Try rephrasing your question", "Check your internet connection"],
                "error": str(e),
                "route_type": "error"
            }
    
    async def _process_rag_query(self, session_id: str, query: str, user_id: Optional[str], routing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process query using RAG system"""
        try:
            # Use existing RAG service
            rag_result = await self.rag_service.process_query(session_id, query, user_id)
            
            # Add MongoDB context if available
            enhanced_result = await self._enhance_with_mongodb_context(rag_result, query)
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Error in RAG processing: {str(e)}")
            return {
                "response": f"Error in knowledge retrieval: {str(e)}",
                "confidence": "low",
                "suggestions": ["Try rephrasing your question"],
                "error": str(e)
            }
    
    async def _process_mongodb_query(self, session_id: str, query: str, user_id: Optional[str], routing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process query using MongoDB tools"""
        try:
            mongodb_result = routing_result.get("mongodb_result", {})
            
            if not mongodb_result.get("success", False):
                return {
                    "response": f"Error retrieving data: {mongodb_result.get('error', 'Unknown error')}",
                    "confidence": "low",
                    "suggestions": ["Try rephrasing your query", "Check if the data exists"],
                    "error": mongodb_result.get("error", "Unknown error")
                }
            
            # Format the response based on the type of data retrieved
            formatted_response = self._format_mongodb_response(mongodb_result)
            
            return {
                "response": formatted_response,
                "confidence": "high" if mongodb_result.get("count", 0) > 0 else "medium",
                "suggestions": self._generate_mongodb_suggestions(mongodb_result),
                "data_source": "mongodb",
                "result_count": mongodb_result.get("count", 0),
                "mongodb_metadata": {
                    "collection": mongodb_result.get("collection"),
                    "search_type": mongodb_result.get("search_type"),
                    "processing_time": mongodb_result.get("processing_time")
                }
            }
            
        except Exception as e:
            logger.error(f"Error in MongoDB processing: {str(e)}")
            return {
                "response": f"Error retrieving data: {str(e)}",
                "confidence": "low",
                "suggestions": ["Try rephrasing your query"],
                "error": str(e)
            }
    
    async def _process_combined_query(self, session_id: str, query: str, user_id: Optional[str], routing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process query using both RAG and MongoDB"""
        try:
            # Get both RAG and MongoDB results
            rag_result = routing_result.get("rag_result", {})
            mongodb_result = routing_result.get("mongodb_result", {})
            
            # Combine the responses
            combined_response = self._combine_responses(rag_result, mongodb_result)
            
            return {
                "response": combined_response,
                "confidence": "high",
                "suggestions": self._generate_combined_suggestions(rag_result, mongodb_result),
                "data_source": "both",
                "rag_metadata": rag_result.get("workflow_metadata", {}),
                "mongodb_metadata": mongodb_result.get("mongodb_metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Error in combined processing: {str(e)}")
            return {
                "response": f"Error processing combined query: {str(e)}",
                "confidence": "low",
                "suggestions": ["Try rephrasing your question"],
                "error": str(e)
            }
    
    async def _enhance_with_mongodb_context(self, rag_result: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Enhance RAG result with relevant MongoDB context"""
        try:
            # Look for specific entities in the query that might have database records
            entities = self._extract_entities(query)
            
            if not entities:
                return rag_result
            
            # Search for related data in MongoDB
            enhanced_context = []
            for entity in entities:
                try:
                    search_result = await self.mongodb_tools.search_database_tool(
                        entity, "documents", limit=3
                    )
                    if search_result.get("success") and search_result.get("count", 0) > 0:
                        enhanced_context.append({
                            "entity": entity,
                            "related_data": search_result.get("results", [])
                        })
                except Exception as e:
                    logger.warning(f"Error enhancing with MongoDB context for entity {entity}: {str(e)}")
            
            if enhanced_context:
                # Add enhanced context to the response
                enhanced_response = rag_result.get("response", "")
                enhanced_response += "\n\n**Related Data:**\n"
                
                for context in enhanced_context:
                    enhanced_response += f"\n**{context['entity']}:**\n"
                    for item in context['related_data'][:2]:  # Limit to 2 items
                        enhanced_response += f"- {item.get('title', 'Untitled')}\n"
                
                rag_result["response"] = enhanced_response
                rag_result["enhanced_with_mongodb"] = True
                rag_result["enhanced_context"] = enhanced_context
            
            return rag_result
            
        except Exception as e:
            logger.error(f"Error enhancing with MongoDB context: {str(e)}")
            return rag_result
    
    def _format_mongodb_response(self, mongodb_result: Dict[str, Any]) -> str:
        """Format MongoDB results into a readable response"""
        results = mongodb_result.get("results", [])
        collection = mongodb_result.get("collection", "data")
        count = mongodb_result.get("count", 0)
        
        if count == 0:
            return f"No {collection} found matching your query."
        
        response = f"Found {count} {collection}:\n\n"
        
        for i, item in enumerate(results[:5], 1):  # Limit to 5 items
            if collection == "users":
                response += f"{i}. **{item.get('full_name', item.get('username', 'Unknown'))}**\n"
                response += f"   Email: {item.get('email', 'N/A')}\n"
                response += f"   Role: {item.get('role', 'N/A')}\n"
            elif collection == "documents":
                response += f"{i}. **{item.get('title', 'Untitled')}**\n"
                response += f"   Type: {item.get('document_type', 'N/A')}\n"
                response += f"   Category: {item.get('category', 'N/A')}\n"
                response += f"   Content: {item.get('content', '')[:100]}...\n"
            elif collection == "conversations":
                response += f"{i}. **Session: {item.get('session_id', 'Unknown')}**\n"
                response += f"   Messages: {len(item.get('messages', []))}\n"
                response += f"   Created: {item.get('created_at', 'N/A')}\n"
            else:
                response += f"{i}. {str(item)[:100]}...\n"
            
            response += "\n"
        
        if count > 5:
            response += f"... and {count - 5} more results."
        
        return response
    
    def _generate_mongodb_suggestions(self, mongodb_result: Dict[str, Any]) -> List[str]:
        """Generate suggestions based on MongoDB results"""
        suggestions = []
        count = mongodb_result.get("count", 0)
        collection = mongodb_result.get("collection", "data")
        
        if count == 0:
            suggestions.extend([
                "Try broadening your search terms",
                "Check if the data exists in the database",
                "Try different keywords"
            ])
        elif count > 10:
            suggestions.extend([
                "Try more specific search terms",
                "Add filters to narrow down results",
                f"Use 'count' to see total number of {collection}"
            ])
        else:
            suggestions.extend([
                "You can view specific records by ID",
                "Try aggregating data for insights",
                "Use filters to refine your search"
            ])
        
        return suggestions
    
    def _generate_combined_suggestions(self, rag_result: Dict[str, Any], mongodb_result: Dict[str, Any]) -> List[str]:
        """Generate suggestions for combined queries"""
        suggestions = []
        
        # Add RAG suggestions
        rag_suggestions = rag_result.get("suggestions", [])
        suggestions.extend(rag_suggestions[:2])
        
        # Add MongoDB suggestions
        mongodb_suggestions = self._generate_mongodb_suggestions(mongodb_result)
        suggestions.extend(mongodb_suggestions[:2])
        
        # Add combined suggestions
        suggestions.extend([
            "You can ask for more specific data",
            "Try asking for explanations with examples"
        ])
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _combine_responses(self, rag_result: Dict[str, Any], mongodb_result: Dict[str, Any]) -> str:
        """Combine RAG and MongoDB responses"""
        rag_response = rag_result.get("response", "")
        mongodb_response = self._format_mongodb_response(mongodb_result)
        
        combined = f"{rag_response}\n\n**Related Data:**\n{mongodb_response}"
        return combined
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract potential entities from query for MongoDB enhancement"""
        # Simple entity extraction - can be enhanced with NLP
        entities = []
        
        # Look for capitalized words that might be entities
        words = query.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                entities.append(word)
        
        # Look for quoted strings
        import re
        quoted = re.findall(r'"([^"]*)"', query)
        entities.extend(quoted)
        
        return entities[:3]  # Limit to 3 entities
    
    async def _log_analytics(self, query: str, result: Dict[str, Any], user_id: Optional[str], session_id: Optional[str], processing_time: float):
        """Log analytics for the query"""
        try:
            analytics_data = {
                "event_type": "query",
                "user_id": user_id,
                "session_id": session_id,
                "query": query,
                "response": result.get("response", "")[:500],  # Truncate long responses
                "source": result.get("route_type", "unknown"),
                "confidence": result.get("confidence", "medium"),
                "processing_time": processing_time,
                "timestamp": datetime.utcnow(),
                "metadata": {
                    "data_source": result.get("data_source", "unknown"),
                    "result_count": result.get("result_count", 0),
                    "enhanced_with_mongodb": result.get("enhanced_with_mongodb", False)
                }
            }
            
            await self.mongodb_service.log_analytics(analytics_data)
            
        except Exception as e:
            logger.error(f"Error logging analytics: {str(e)}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status including both RAG and MongoDB"""
        try:
            rag_status = self.rag_service.get_system_status()
            mongodb_status = asyncio.run(self.mongodb_service.get_database_stats())
            
            return {
                "enhanced_rag_status": "healthy" if self.is_initialized else "not_initialized",
                "rag_system": rag_status,
                "mongodb_system": mongodb_status,
                "is_initialized": self.is_initialized
            }
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            return {
                "enhanced_rag_status": "error",
                "error": str(e),
                "is_initialized": self.is_initialized
            }

# Global enhanced RAG service instance
enhanced_rag_service = EnhancedRAGService()
