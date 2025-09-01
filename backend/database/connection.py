import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MongoDBConnection:
    """MongoDB connection manager for both sync and async operations"""
    
    def __init__(self):
        self.async_client: Optional[AsyncIOMotorClient] = None
        self.sync_client: Optional[MongoClient] = None
        self.database_name: str = ""
        self.is_connected = False
        
    async def connect(self):
        """Initialize MongoDB connections"""
        try:
            # Get configuration from environment
            mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            self.database_name = os.getenv('MONGODB_DATABASE', 'aide_db')
            
            # Create async client
            self.async_client = AsyncIOMotorClient(mongodb_uri)
            self.async_database = self.async_client[self.database_name]
            
            # Create sync client for operations that need it
            self.sync_client = MongoClient(mongodb_uri)
            self.sync_database = self.sync_client[self.database_name]
            
            # Test connection
            await self.async_client.admin.command('ping')
            self.is_connected = True
            
            logger.info(f"Successfully connected to MongoDB database: {self.database_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            self.is_connected = False
            raise e
    
    async def disconnect(self):
        """Close MongoDB connections"""
        try:
            if self.async_client:
                self.async_client.close()
            if self.sync_client:
                self.sync_client.close()
            self.is_connected = False
            logger.info("MongoDB connections closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB connections: {str(e)}")
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        if not self.is_connected:
            raise ConnectionError("MongoDB not connected")
        return self.async_database[collection_name]
    
    def get_sync_collection(self, collection_name: str):
        """Get a sync collection from the database"""
        if not self.is_connected:
            raise ConnectionError("MongoDB not connected")
        return self.sync_database[collection_name]
    
    async def health_check(self) -> dict:
        """Check MongoDB connection health"""
        try:
            if not self.is_connected:
                return {"status": "disconnected", "message": "Not connected to MongoDB"}
            
            # Test connection
            await self.async_client.admin.command('ping')
            
            # Get database stats
            db_stats = await self.async_database.command('dbStats')
            
            return {
                "status": "healthy",
                "database": self.database_name,
                "collections": db_stats.get('collections', 0),
                "data_size": db_stats.get('dataSize', 0),
                "storage_size": db_stats.get('storageSize', 0)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"MongoDB health check failed: {str(e)}"
            }

# Global connection instance
mongodb_connection = MongoDBConnection()
