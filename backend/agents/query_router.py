import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from agents.mongodb_tools import mongodb_tools
from database.mongodb_service import mongodb_service

logger = logging.getLogger(__name__)

class QueryRouter:
    """Enhanced query router that intelligently chooses between RAG and MongoDB"""
    
    def __init__(self):
        self.mongodb_tools = mongodb_tools
        self.mongodb_service = mongodb_service
        
        # Query patterns for classification
        self.rag_patterns = [
            r"what (is|are|does|do)",
            r"how (to|does|do)",
            r"explain",
            r"describe",
            r"tell me about",
            r"what does the documentation say",
            r"what are the rules",
            r"what are the procedures",
            r"guide me through",
            r"help me understand",
            r"concept",
            r"definition",
            r"meaning",
            r"purpose",
            r"benefits",
            r"advantages",
            r"disadvantages"
        ]
        
        self.mongodb_patterns = [
            r"show me",
            r"find",
            r"search for",
            r"get",
            r"retrieve",
            r"list",
            r"display",
            r"view",
            r"count",
            r"sum",
            r"average",
            r"group by",
            r"filter",
            r"where",
            r"all users",
            r"all documents",
            r"recent",
            r"today",
            r"this week",
            r"status",
            r"type",
            r"category",
            r"author",
            r"created",
            r"updated",
            r"record",
            r"entry",
            r"data",
            r"statistics",
            r"analytics"
        ]
        
        self.combined_patterns = [
            r"explain.*and show",
            r"what.*and find",
            r"describe.*and list",
            r"tell me about.*and get",
            r"help me understand.*and search"
        ]
    
    async def route_query(self, query: str, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Route a query to the appropriate data source(s)
        
        Args:
            query: The user's query
            user_id: Optional user ID for context
            session_id: Optional session ID for context
            
        Returns:
            Dictionary with routing decision and metadata
        """
        try:
            start_time = datetime.utcnow()
            
            # Analyze query to determine routing strategy
            query_analysis = self._analyze_query(query)
            
            # Log the query for analytics
            await self._log_query(query, query_analysis, user_id, session_id)
            
            # Route based on analysis
            if query_analysis["route_type"] == "rag":
                result = await self._handle_rag_query(query, query_analysis)
            elif query_analysis["route_type"] == "mongodb":
                result = await self._handle_mongodb_query(query, query_analysis)
            elif query_analysis["route_type"] == "combined":
                result = await self._handle_combined_query(query, query_analysis)
            else:
                # Default to RAG for unknown query types
                result = await self._handle_rag_query(query, query_analysis)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Add metadata to result
            result.update({
                "query_analysis": query_analysis,
                "processing_time": processing_time,
                "user_id": user_id,
                "session_id": session_id
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in query routing: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "route_type": "error",
                "response": f"I encountered an error while processing your request: {str(e)}"
            }
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine routing strategy"""
        query_lower = query.lower()
        
        # Check for combined patterns first
        for pattern in self.combined_patterns:
            if re.search(pattern, query_lower):
                return {
                    "route_type": "combined",
                    "confidence": 0.9,
                    "reasoning": "Query contains both conceptual and data retrieval elements",
                    "patterns_matched": [pattern],
                    "query_type": "mixed"
                }
        
        # Check for MongoDB patterns
        mongodb_matches = []
        for pattern in self.mongodb_patterns:
            if re.search(pattern, query_lower):
                mongodb_matches.append(pattern)
        
        # Check for RAG patterns
        rag_matches = []
        for pattern in self.rag_patterns:
            if re.search(pattern, query_lower):
                rag_matches.append(pattern)
        
        # Determine route type based on pattern matches
        if mongodb_matches and not rag_matches:
            return {
                "route_type": "mongodb",
                "confidence": 0.8,
                "reasoning": "Query matches data retrieval patterns",
                "patterns_matched": mongodb_matches,
                "query_type": "data_retrieval"
            }
        elif rag_matches and not mongodb_matches:
            return {
                "route_type": "rag",
                "confidence": 0.8,
                "reasoning": "Query matches conceptual/explanation patterns",
                "patterns_matched": rag_matches,
                "query_type": "conceptual"
            }
        elif mongodb_matches and rag_matches:
            return {
                "route_type": "combined",
                "confidence": 0.7,
                "reasoning": "Query contains both conceptual and data retrieval elements",
                "patterns_matched": rag_matches + mongodb_matches,
                "query_type": "mixed"
            }
        else:
            # Default analysis for unknown patterns
            return {
                "route_type": "rag",
                "confidence": 0.5,
                "reasoning": "No specific patterns matched, defaulting to RAG",
                "patterns_matched": [],
                "query_type": "unknown"
            }
    
    async def _handle_rag_query(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle RAG-based queries"""
        return {
            "success": True,
            "route_type": "rag",
            "response": "This query will be processed by the RAG system for conceptual understanding and knowledge retrieval.",
            "data_source": "vector_store",
            "confidence": analysis["confidence"],
            "reasoning": analysis["reasoning"]
        }
    
    async def _handle_mongodb_query(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MongoDB-based queries"""
        try:
            # Determine the appropriate MongoDB tool to use
            tool_result = await self._select_mongodb_tool(query, analysis)
            
            return {
                "success": True,
                "route_type": "mongodb",
                "response": tool_result.get("response", "Data retrieved from database"),
                "data_source": "mongodb",
                "confidence": analysis["confidence"],
                "reasoning": analysis["reasoning"],
                "mongodb_result": tool_result
            }
            
        except Exception as e:
            logger.error(f"Error handling MongoDB query: {str(e)}")
            return {
                "success": False,
                "route_type": "mongodb",
                "response": f"Error retrieving data: {str(e)}",
                "data_source": "mongodb",
                "confidence": 0.0,
                "reasoning": f"Error occurred: {str(e)}"
            }
    
    async def _handle_combined_query(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle queries that need both RAG and MongoDB"""
        try:
            # Split query into conceptual and data parts
            conceptual_part, data_part = self._split_combined_query(query)
            
            # Process both parts
            rag_result = await self._handle_rag_query(conceptual_part, analysis)
            mongodb_result = await self._handle_mongodb_query(data_part, analysis)
            
            # Combine results
            combined_response = f"{rag_result['response']} Additionally, here's the relevant data: {mongodb_result.get('response', '')}"
            
            return {
                "success": True,
                "route_type": "combined",
                "response": combined_response,
                "data_source": "both",
                "confidence": analysis["confidence"],
                "reasoning": analysis["reasoning"],
                "rag_result": rag_result,
                "mongodb_result": mongodb_result
            }
            
        except Exception as e:
            logger.error(f"Error handling combined query: {str(e)}")
            return {
                "success": False,
                "route_type": "combined",
                "response": f"Error processing combined query: {str(e)}",
                "data_source": "both",
                "confidence": 0.0,
                "reasoning": f"Error occurred: {str(e)}"
            }
    
    async def _select_mongodb_tool(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Select the appropriate MongoDB tool based on query content"""
        query_lower = query.lower()
        
        # Determine collection and tool based on query content
        if any(word in query_lower for word in ["user", "users", "person", "people"]):
            collection = "users"
        elif any(word in query_lower for word in ["document", "documents", "file", "files"]):
            collection = "documents"
        elif any(word in query_lower for word in ["conversation", "conversations", "chat", "session"]):
            collection = "conversations"
        elif any(word in query_lower for word in ["analytics", "statistics", "metrics", "data"]):
            collection = "analytics"
        else:
            collection = "documents"  # Default
        
        # Select tool based on query type
        if any(word in query_lower for word in ["count", "sum", "average", "group by", "aggregate"]):
            return await self.mongodb_tools.aggregate_data_tool(query, collection)
        elif any(word in query_lower for word in ["show", "find", "search", "get", "retrieve", "list"]):
            return await self.mongodb_tools.search_database_tool(query, collection)
        elif any(word in query_lower for word in ["view", "see", "display"]):
            # Try to extract ID from query
            record_id = self._extract_record_id(query)
            if record_id:
                return await self.mongodb_tools.view_record_tool(record_id, collection)
            else:
                return await self.mongodb_tools.search_database_tool(query, collection)
        else:
            # Default to search
            return await self.mongodb_tools.search_database_tool(query, collection)
    
    def _split_combined_query(self, query: str) -> Tuple[str, str]:
        """Split a combined query into conceptual and data parts"""
        # Simple splitting logic - can be enhanced with NLP
        query_lower = query.lower()
        
        # Look for conjunction words that separate conceptual from data parts
        conjunctions = ["and show", "and find", "and list", "and get", "and search"]
        
        for conjunction in conjunctions:
            if conjunction in query_lower:
                parts = query.split(conjunction, 1)
                if len(parts) == 2:
                    return parts[0].strip(), parts[1].strip()
        
        # If no clear conjunction, split by length
        words = query.split()
        mid_point = len(words) // 2
        conceptual_part = " ".join(words[:mid_point])
        data_part = " ".join(words[mid_point:])
        
        return conceptual_part, data_part
    
    def _extract_record_id(self, query: str) -> Optional[str]:
        """Extract record ID from query"""
        # Look for ObjectId pattern
        object_id_pattern = r'[a-fA-F0-9]{24}'
        match = re.search(object_id_pattern, query)
        if match:
            return match.group(0)
        
        # Look for other ID patterns
        id_patterns = [
            r'id[:\s]+([a-zA-Z0-9_-]+)',
            r'ID[:\s]+([a-zA-Z0-9_-]+)',
            r'#([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in id_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        
        return None
    
    async def _log_query(self, query: str, analysis: Dict[str, Any], user_id: Optional[str], session_id: Optional[str]):
        """Log query for analytics"""
        try:
            log_data = {
                "query": query,
                "query_type": analysis["route_type"],
                "user_id": user_id,
                "session_id": session_id,
                "confidence": analysis["confidence"],
                "reasoning": analysis["reasoning"],
                "patterns_matched": analysis["patterns_matched"],
                "timestamp": datetime.utcnow(),
                "success": True
            }
            
            await self.mongodb_service.log_query(log_data)
            
        except Exception as e:
            logger.error(f"Error logging query: {str(e)}")

# Global query router instance
query_router = QueryRouter()
