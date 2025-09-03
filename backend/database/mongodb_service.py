import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import PyMongoError

from .connection import mongodb_connection
from .models import User, Document, Conversation, Analytics, QueryLog, model_to_dict, dict_to_model

def utc_now():
    """Get current UTC datetime (replacement for deprecated datetime.utcnow())"""
    return datetime.now(timezone.utc)

logger = logging.getLogger(__name__)

class MongoDBService:
    """MongoDB service for database operations"""
    
    def __init__(self):
        self.connection = mongodb_connection
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the MongoDB service"""
        try:
            await self.connection.connect()
            self.is_initialized = True
            logger.info("MongoDB service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB service: {str(e)}")
            raise e
    
    async def close(self):
        """Close MongoDB connections"""
        await self.connection.disconnect()
        self.is_initialized = False
    
    # User Operations
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        try:
            user = User(**user_data)
            collection = self.connection.get_collection("users")
            result = await collection.insert_one(model_to_dict(user))
            user.id = result.inserted_id
            return model_to_dict(user)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise e
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            collection = self.connection.get_collection("users")
            user_data = await collection.find_one({"_id": ObjectId(user_id)})
            return user_data
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            raise e
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user"""
        try:
            update_data["updated_at"] = utc_now()
            collection = self.connection.get_collection("users")
            result = await collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                return await self.get_user(user_id)
            return None
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise e
    
    async def search_users(self, query: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Search users with filters"""
        try:
            collection = self.connection.get_collection("users")
            cursor = collection.find(query).limit(limit)
            users = await cursor.to_list(length=limit)
            return users
        except Exception as e:
            logger.error(f"Error searching users: {str(e)}")
            raise e
    
    # Document Operations
    async def create_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        try:
            document = Document(**document_data)
            collection = self.connection.get_collection("documents")
            result = await collection.insert_one(model_to_dict(document))
            document.id = result.inserted_id
            return model_to_dict(document)
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise e
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        try:
            collection = self.connection.get_collection("documents")
            document_data = await collection.find_one({"_id": ObjectId(document_id)})
            return document_data
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise e
    
    async def update_document(self, document_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update document"""
        try:
            update_data["updated_at"] = utc_now()
            collection = self.connection.get_collection("documents")
            result = await collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                return await self.get_document(document_id)
            return None
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            raise e
    
    async def search_documents(self, query: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents with filters"""
        try:
            collection = self.connection.get_collection("documents")
            cursor = collection.find(query).limit(limit)
            documents = await cursor.to_list(length=limit)
            return documents
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise e
    
    async def search_documents_by_text(self, text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents by text content"""
        try:
            collection = self.connection.get_collection("documents")
            # Create text search query
            search_query = {
                "$or": [
                    {"title": {"$regex": text, "$options": "i"}},
                    {"content": {"$regex": text, "$options": "i"}},
                    {"tags": {"$in": [text]}}
                ]
            }
            cursor = collection.find(search_query).limit(limit)
            documents = await cursor.to_list(length=limit)
            return documents
        except Exception as e:
            logger.error(f"Error searching documents by text: {str(e)}")
            raise e
    
    # Conversation Operations
    async def create_conversation(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new conversation"""
        try:
            conversation = Conversation(**conversation_data)
            collection = self.connection.get_collection("conversations")
            result = await collection.insert_one(model_to_dict(conversation))
            conversation.id = result.inserted_id
            return model_to_dict(conversation)
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise e
    
    async def get_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation by session ID"""
        try:
            collection = self.connection.get_collection("conversations")
            conversation_data = await collection.find_one({"session_id": session_id})
            return conversation_data
        except Exception as e:
            logger.error(f"Error getting conversation: {str(e)}")
            raise e
    
    async def update_conversation(self, session_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update conversation"""
        try:
            update_data["updated_at"] = utc_now()
            collection = self.connection.get_collection("conversations")
            result = await collection.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                return await self.get_conversation(session_id)
            return None
        except Exception as e:
            logger.error(f"Error updating conversation: {str(e)}")
            raise e
    
    async def add_message_to_conversation(self, session_id: str, message: Dict[str, Any]) -> bool:
        """Add a message to an existing conversation"""
        try:
            collection = self.connection.get_collection("conversations")
            result = await collection.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": utc_now()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding message to conversation: {str(e)}")
            raise e
    
    # Analytics Operations
    async def log_analytics(self, analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log analytics event"""
        try:
            analytics = Analytics(**analytics_data)
            collection = self.connection.get_collection("analytics")
            result = await collection.insert_one(model_to_dict(analytics))
            analytics.id = result.inserted_id
            return model_to_dict(analytics)
        except Exception as e:
            logger.error(f"Error logging analytics: {str(e)}")
            raise e
    
    async def get_analytics(self, filters: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Get analytics with filters"""
        try:
            collection = self.connection.get_collection("analytics")
            cursor = collection.find(filters).sort("timestamp", DESCENDING).limit(limit)
            analytics = await cursor.to_list(length=limit)
            return analytics
        except Exception as e:
            logger.error(f"Error getting analytics: {str(e)}")
            raise e
    
    # Query Log Operations
    async def log_query(self, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log a query"""
        try:
            query_log = QueryLog(**query_data)
            collection = self.connection.get_collection("query_logs")
            result = await collection.insert_one(model_to_dict(query_log))
            query_log.id = result.inserted_id
            return model_to_dict(query_log)
        except Exception as e:
            logger.error(f"Error logging query: {str(e)}")
            raise e
    
    async def get_query_logs(self, filters: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Get query logs with filters"""
        try:
            collection = self.connection.get_collection("query_logs")
            cursor = collection.find(filters).sort("timestamp", DESCENDING).limit(limit)
            logs = await cursor.to_list(length=limit)
            return logs
        except Exception as e:
            logger.error(f"Error getting query logs: {str(e)}")
            raise e
    
    # Aggregation Operations
    async def aggregate_data(self, collection_name: str, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform aggregation on any collection"""
        try:
            collection = self.connection.get_collection(collection_name)
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            return results
        except Exception as e:
            logger.error(f"Error performing aggregation: {str(e)}")
            raise e
    
    # Health and Status
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = await self.connection.health_check()
            
            # Get collection counts
            collections = ["users", "documents", "conversations", "analytics", "query_logs"]
            collection_counts = {}
            
            for collection_name in collections:
                try:
                    collection = self.connection.get_collection(collection_name)
                    count = await collection.count_documents({})
                    collection_counts[collection_name] = count
                except Exception as e:
                    collection_counts[collection_name] = f"Error: {str(e)}"
            
            stats["collection_counts"] = collection_counts
            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            raise e

# Global MongoDB service instance
mongodb_service = MongoDBService()
