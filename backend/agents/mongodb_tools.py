import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import re

from database.mongodb_service import mongodb_service
from database.models import User, Document, Conversation, Analytics, QueryLog

def utc_now():
    """Get current UTC datetime (replacement for deprecated datetime.utcnow())"""
    return datetime.now(timezone.utc)

logger = logging.getLogger(__name__)

class MongoDBTools:
    """MongoDB tools for agent operations"""
    
    def __init__(self):
        self.service = mongodb_service
    
    async def search_database_tool(self, query: str, collection: str = "documents", limit: int = 10) -> Dict[str, Any]:
        """
        Search database collections with natural language queries
        
        Args:
            query: Natural language search query
            collection: Collection to search (users, documents, conversations, analytics)
            limit: Maximum number of results
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            start_time = utc_now()
            
            # Parse natural language query to determine search type
            search_type = self._determine_search_type(query, collection)
            
            if search_type == "text_search":
                results = await self._text_search(query, collection, limit)
            elif search_type == "filtered_search":
                results = await self._filtered_search(query, collection, limit)
            elif search_type == "aggregation":
                results = await self._aggregation_search(query, collection, limit)
            else:
                results = await self._general_search(query, collection, limit)
            
            processing_time = (utc_now() - start_time).total_seconds()
            
            return {
                "success": True,
                "results": results,
                "count": len(results),
                "collection": collection,
                "search_type": search_type,
                "processing_time": processing_time,
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error in search_database_tool: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "count": 0
            }
    
    async def view_record_tool(self, record_id: str, collection: str = "documents") -> Dict[str, Any]:
        """
        Retrieve a specific record by ID
        
        Args:
            record_id: The ID of the record to retrieve
            collection: Collection to search in
            
        Returns:
            Dictionary with record data
        """
        try:
            start_time = utc_now()
            
            if collection == "users":
                result = await self.service.get_user(record_id)
            elif collection == "documents":
                result = await self.service.get_document(record_id)
            elif collection == "conversations":
                result = await self.service.get_conversation(record_id)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported collection: {collection}",
                    "result": None
                }
            
            processing_time = (utc_now() - start_time).total_seconds()
            
            return {
                "success": True,
                "result": result,
                "collection": collection,
                "record_id": record_id,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error in view_record_tool: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    async def edit_record_tool(self, record_id: str, update_data: Dict[str, Any], collection: str = "documents") -> Dict[str, Any]:
        """
        Update a record in the database
        
        Args:
            record_id: The ID of the record to update
            update_data: Dictionary with fields to update
            collection: Collection containing the record
            
        Returns:
            Dictionary with update result
        """
        try:
            start_time = utc_now()
            
            if collection == "users":
                result = await self.service.update_user(record_id, update_data)
            elif collection == "documents":
                result = await self.service.update_document(record_id, update_data)
            elif collection == "conversations":
                result = await self.service.update_conversation(record_id, update_data)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported collection: {collection}",
                    "result": None
                }
            
            processing_time = (utc_now() - start_time).total_seconds()
            
            return {
                "success": True,
                "result": result,
                "collection": collection,
                "record_id": record_id,
                "processing_time": processing_time,
                "updated_fields": list(update_data.keys())
            }
            
        except Exception as e:
            logger.error(f"Error in edit_record_tool: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    async def aggregate_data_tool(self, query: str, collection: str = "analytics") -> Dict[str, Any]:
        """
        Perform complex aggregation queries
        
        Args:
            query: Natural language description of aggregation
            collection: Collection to aggregate
            
        Returns:
            Dictionary with aggregation results
        """
        try:
            start_time = utc_now()
            
            # Parse natural language to aggregation pipeline
            pipeline = self._parse_aggregation_query(query, collection)
            
            if not pipeline:
                return {
                    "success": False,
                    "error": "Could not parse aggregation query",
                    "results": []
                }
            
            results = await self.service.aggregate_data(collection, pipeline)
            processing_time = (utc_now() - start_time).total_seconds()
            
            return {
                "success": True,
                "results": results,
                "count": len(results),
                "collection": collection,
                "pipeline": pipeline,
                "processing_time": processing_time,
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error in aggregate_data_tool: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    async def create_record_tool(self, record_data: Dict[str, Any], collection: str = "documents") -> Dict[str, Any]:
        """
        Create a new record in the database
        
        Args:
            record_data: Dictionary with record data
            collection: Collection to create record in
            
        Returns:
            Dictionary with created record
        """
        try:
            start_time = utc_now()
            
            if collection == "users":
                result = await self.service.create_user(record_data)
            elif collection == "documents":
                result = await self.service.create_document(record_data)
            elif collection == "conversations":
                result = await self.service.create_conversation(record_data)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported collection: {collection}",
                    "result": None
                }
            
            processing_time = (utc_now() - start_time).total_seconds()
            
            return {
                "success": True,
                "result": result,
                "collection": collection,
                "processing_time": processing_time,
                "created_fields": list(record_data.keys())
            }
            
        except Exception as e:
            logger.error(f"Error in create_record_tool: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "result": None
            }
    
    # Helper methods for query parsing and processing
    def _determine_search_type(self, query: str, collection: str) -> str:
        """Determine the type of search based on query content"""
        query_lower = query.lower()
        
        # Check for aggregation keywords
        if any(word in query_lower for word in ["count", "sum", "average", "group by", "aggregate", "statistics"]):
            return "aggregation"
        
        # Check for specific filters
        if any(word in query_lower for word in ["status", "type", "category", "author", "date", "created"]):
            return "filtered_search"
        
        # Default to text search
        return "text_search"
    
    async def _text_search(self, query: str, collection: str, limit: int) -> List[Dict[str, Any]]:
        """Perform text-based search"""
        if collection == "documents":
            return await self.service.search_documents_by_text(query, limit)
        else:
            # For other collections, use general search
            return await self._general_search(query, collection, limit)
    
    async def _filtered_search(self, query: str, collection: str, limit: int) -> List[Dict[str, Any]]:
        """Perform filtered search based on specific criteria"""
        filters = self._extract_filters(query)
        return await self.service.search_documents(filters, limit)
    
    async def _general_search(self, query: str, collection: str, limit: int) -> List[Dict[str, Any]]:
        """Perform general search across all fields"""
        # Create a general search query
        search_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}},
                {"name": {"$regex": query, "$options": "i"}},
                {"username": {"$regex": query, "$options": "i"}},
                {"email": {"$regex": query, "$options": "i"}}
            ]
        }
        return await self.service.search_documents(search_query, limit)
    
    async def _aggregation_search(self, query: str, collection: str, limit: int) -> List[Dict[str, Any]]:
        """Perform aggregation search"""
        pipeline = self._parse_aggregation_query(query, collection)
        if pipeline:
            return await self.service.aggregate_data(collection, pipeline)
        return []
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract filters from natural language query"""
        filters = {}
        query_lower = query.lower()
        
        # Extract status filters
        if "active" in query_lower:
            filters["status"] = "active"
        elif "inactive" in query_lower or "disabled" in query_lower:
            filters["status"] = "inactive"
        
        # Extract type filters
        type_patterns = {
            "policy": "policy",
            "procedure": "procedure", 
            "guide": "guide",
            "report": "report"
        }
        
        for pattern, doc_type in type_patterns.items():
            if pattern in query_lower:
                filters["document_type"] = doc_type
                break
        
        # Extract date filters
        if "recent" in query_lower or "today" in query_lower:
            filters["created_at"] = {"$gte": utc_now().replace(hour=0, minute=0, second=0, microsecond=0)}
        elif "this week" in query_lower:
            # Calculate start of week
            from datetime import timedelta
            today = utc_now()
            start_of_week = today - timedelta(days=today.weekday())
            filters["created_at"] = {"$gte": start_of_week}
        
        return filters
    
    def _parse_aggregation_query(self, query: str, collection: str) -> List[Dict[str, Any]]:
        """Parse natural language to MongoDB aggregation pipeline"""
        query_lower = query.lower()
        pipeline = []
        
        # Count operations
        if "count" in query_lower:
            pipeline.append({"$count": "total"})
        
        # Group by operations
        if "group by" in query_lower:
            group_field = self._extract_group_field(query)
            if group_field:
                pipeline.append({
                    "$group": {
                        "_id": f"${group_field}",
                        "count": {"$sum": 1}
                    }
                })
        
        # Sum operations
        if "sum" in query_lower:
            sum_field = self._extract_sum_field(query)
            if sum_field:
                pipeline.append({
                    "$group": {
                        "_id": None,
                        "total": {"$sum": f"${sum_field}"}
                    }
                })
        
        # Average operations
        if "average" in query_lower or "avg" in query_lower:
            avg_field = self._extract_average_field(query)
            if avg_field:
                pipeline.append({
                    "$group": {
                        "_id": None,
                        "average": {"$avg": f"${avg_field}"}
                    }
                })
        
        # If no specific aggregation, return empty pipeline
        if not pipeline:
            return []
        
        return pipeline
    
    def _extract_group_field(self, query: str) -> Optional[str]:
        """Extract group by field from query"""
        # Simple pattern matching - can be enhanced
        if "status" in query.lower():
            return "status"
        elif "type" in query.lower():
            return "document_type"
        elif "category" in query.lower():
            return "category"
        return None
    
    def _extract_sum_field(self, query: str) -> Optional[str]:
        """Extract sum field from query"""
        # Simple pattern matching - can be enhanced
        if "processing_time" in query.lower():
            return "processing_time"
        return None
    
    def _extract_average_field(self, query: str) -> Optional[str]:
        """Extract average field from query"""
        # Simple pattern matching - can be enhanced
        if "processing_time" in query.lower():
            return "processing_time"
        elif "confidence" in query.lower():
            return "confidence"
        return None

# Global MongoDB tools instance
mongodb_tools = MongoDBTools()
