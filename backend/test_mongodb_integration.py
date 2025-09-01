#!/usr/bin/env python3
"""
MongoDB Integration Test Script
Tests the MongoDB integration and enhanced RAG system functionality.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mongodb_service import mongodb_service
from agents.mongodb_tools import mongodb_tools
from agents.query_router import query_router
from rag.enhanced_rag_service import enhanced_rag_service

async def test_mongodb_connection():
    """Test MongoDB connection"""
    print("Testing MongoDB connection...")
    try:
        await mongodb_service.initialize()
        stats = await mongodb_service.get_database_stats()
        print(f"✅ MongoDB connection successful")
        print(f"   Database: {stats.get('database', 'Unknown')}")
        print(f"   Collections: {stats.get('collection_counts', {})}")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        return False

async def test_mongodb_tools():
    """Test MongoDB tools functionality"""
    print("\nTesting MongoDB tools...")
    
    # Test search tool
    try:
        result = await mongodb_tools.search_database_tool("employee handbook", "documents", 5)
        print(f"✅ Search tool working - Found {result.get('count', 0)} documents")
    except Exception as e:
        print(f"❌ Search tool failed: {str(e)}")
    
    # Test aggregation tool
    try:
        result = await mongodb_tools.aggregate_data_tool("count all documents", "documents")
        print(f"✅ Aggregation tool working - {result.get('count', 0)} results")
    except Exception as e:
        print(f"❌ Aggregation tool failed: {str(e)}")

async def test_query_router():
    """Test query routing functionality"""
    print("\nTesting query router...")
    
    test_queries = [
        "What is the employee handbook?",
        "Show me all active users",
        "Explain the security guidelines and show me related documents",
        "Count the number of policies"
    ]
    
    for query in test_queries:
        try:
            result = await query_router.route_query(query, "test_user", "test_session")
            route_type = result.get("route_type", "unknown")
            confidence = result.get("query_analysis", {}).get("confidence", 0)
            print(f"✅ Query: '{query[:50]}...' -> {route_type} (confidence: {confidence})")
        except Exception as e:
            print(f"❌ Query routing failed for '{query}': {str(e)}")

async def test_enhanced_rag_service():
    """Test enhanced RAG service"""
    print("\nTesting enhanced RAG service...")
    
    try:
        await enhanced_rag_service.initialize()
        print("✅ Enhanced RAG service initialized")
        
        # Test different types of queries
        test_queries = [
            "What is the employee handbook?",
            "Show me all active users",
            "Explain security guidelines and find related documents"
        ]
        
        for query in test_queries:
            try:
                result = await enhanced_rag_service.process_query("test_session", query, "test_user")
                route_type = result.get("route_type", "unknown")
                data_source = result.get("data_source", "unknown")
                print(f"✅ Query: '{query[:40]}...' -> {route_type} ({data_source})")
            except Exception as e:
                print(f"❌ Enhanced RAG failed for '{query}': {str(e)}")
                
    except Exception as e:
        print(f"❌ Enhanced RAG service initialization failed: {str(e)}")

async def test_api_endpoints():
    """Test API endpoints (simulated)"""
    print("\nTesting API endpoints (simulated)...")
    
    # Simulate API calls
    endpoints_to_test = [
        "/api/mongodb/health",
        "/api/mongodb/stats",
        "/api/mongodb/documents",
        "/api/mongodb/users",
        "/api/enhanced-chat"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"✅ Endpoint {endpoint} would be available")

async def run_integration_tests():
    """Run all integration tests"""
    print("🚀 Starting MongoDB Integration Tests")
    print("=" * 50)
    
    # Test MongoDB connection
    connection_ok = await test_mongodb_connection()
    if not connection_ok:
        print("❌ Cannot proceed without MongoDB connection")
        return
    
    # Test MongoDB tools
    await test_mongodb_tools()
    
    # Test query router
    await test_query_router()
    
    # Test enhanced RAG service
    await test_enhanced_rag_service()
    
    # Test API endpoints
    await test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("✅ MongoDB Integration Tests Completed")
    print("\nNext steps:")
    print("1. Start the Flask server: python app.py")
    print("2. Test the enhanced chat endpoint: POST /api/enhanced-chat")
    print("3. Test MongoDB endpoints: GET /api/mongodb/health")
    print("4. Check the documentation: MONGODB_INTEGRATION.md")

if __name__ == "__main__":
    asyncio.run(run_integration_tests())
