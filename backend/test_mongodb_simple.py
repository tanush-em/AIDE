#!/usr/bin/env python3
"""
Simple MongoDB Integration Test
Tests the MongoDB integration without the full RAG system.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mongodb_service import mongodb_service
from agents.mongodb_tools import mongodb_tools

async def test_mongodb_basic():
    """Test basic MongoDB functionality"""
    print("🚀 Testing MongoDB Integration")
    print("=" * 40)
    
    try:
        # Initialize MongoDB service
        print("1. Initializing MongoDB service...")
        await mongodb_service.initialize()
        print("✅ MongoDB service initialized")
        
        # Test database stats
        print("\n2. Getting database statistics...")
        stats = await mongodb_service.get_database_stats()
        print(f"✅ Database: {stats.get('database', 'Unknown')}")
        print(f"✅ Collections: {stats.get('collection_counts', {})}")
        
        # Test search functionality
        print("\n3. Testing search functionality...")
        result = await mongodb_tools.search_database_tool("employee handbook", "documents", 5)
        print(f"✅ Search result: {result.get('count', 0)} documents found")
        
        if result.get('count', 0) > 0:
            print("✅ Sample document titles:")
            for i, doc in enumerate(result.get('results', [])[:3]):
                print(f"   {i+1}. {doc.get('title', 'Untitled')}")
        
        # Test aggregation
        print("\n4. Testing aggregation...")
        agg_result = await mongodb_tools.aggregate_data_tool("count all documents", "documents")
        print(f"✅ Aggregation result: {agg_result.get('count', 0)} results")
        
        print("\n" + "=" * 40)
        print("✅ MongoDB Integration Test Completed Successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mongodb_basic())
    if success:
        print("\n🎉 MongoDB is working correctly!")
        print("You can now start the Flask server and test the API endpoints.")
    else:
        print("\n❌ MongoDB integration test failed.")
        print("Please check your MongoDB connection and try again.")
