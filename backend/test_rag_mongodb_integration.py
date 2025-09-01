#!/usr/bin/env python3
"""
RAG + MongoDB Integration Test
Tests whether the RAG system can access and use MongoDB data.
"""

import asyncio
import sys
import os
import requests
import json

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_rag_mongodb_integration():
    """Test RAG system's knowledge of MongoDB data"""
    print("🧪 Testing RAG + MongoDB Integration")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # Test questions that should access MongoDB data
    test_questions = [
        # Questions that should use RAG (conceptual)
        {
            "question": "What is the employee handbook about?",
            "expected_source": "rag",
            "description": "Conceptual question about handbook content"
        },
        {
            "question": "How do I follow security guidelines?",
            "expected_source": "rag", 
            "description": "Procedural question about security"
        },
        
        # Questions that should use MongoDB (data retrieval)
        {
            "question": "Show me all users in the system",
            "expected_source": "mongodb",
            "description": "Data retrieval question"
        },
        {
            "question": "List all documents",
            "expected_source": "mongodb",
            "description": "Document listing question"
        },
        {
            "question": "Find users with admin role",
            "expected_source": "mongodb",
            "description": "Filtered user query"
        },
        
        # Questions that should use both (combined)
        {
            "question": "Explain the employee handbook and show me related documents",
            "expected_source": "combined",
            "description": "Combined conceptual and data query"
        },
        {
            "question": "What are security guidelines and find examples in our database",
            "expected_source": "combined",
            "description": "Combined explanation and data retrieval"
        }
    ]
    
    print("Testing different types of queries...\n")
    
    for i, test in enumerate(test_questions, 1):
        print(f"Test {i}: {test['description']}")
        print(f"Question: {test['question']}")
        print(f"Expected source: {test['expected_source']}")
        
        try:
            # Test with enhanced chat endpoint
            response = requests.post(
                f"{base_url}/api/enhanced-chat",
                json={
                    "message": test["question"],
                    "user_id": "test_user"
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                route_type = result.get("route_type", "unknown")
                data_source = result.get("data_source", "unknown")
                response_text = result.get("response", "")
                
                print(f"✅ Response received")
                print(f"   Route type: {route_type}")
                print(f"   Data source: {data_source}")
                print(f"   Response preview: {response_text[:100]}...")
                
                # Check if the response contains MongoDB data
                if "mongodb" in data_source.lower() or "both" in data_source.lower():
                    print(f"   ✅ MongoDB data accessed")
                else:
                    print(f"   ⚠️  No MongoDB data detected")
                    
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("-" * 40)
    
    # Test specific MongoDB queries
    print("\n🔍 Testing Specific MongoDB Queries")
    print("=" * 40)
    
    mongodb_queries = [
        "Show me all users",
        "Find documents about security",
        "Count the number of documents",
        "List all active users",
        "Search for employee handbook"
    ]
    
    for query in mongodb_queries:
        print(f"\nQuery: {query}")
        try:
            response = requests.post(
                f"{base_url}/api/enhanced-chat",
                json={
                    "message": query,
                    "user_id": "test_user"
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                route_type = result.get("route_type", "unknown")
                response_text = result.get("response", "")
                
                print(f"   Route: {route_type}")
                print(f"   Response: {response_text[:150]}...")
                
                # Check if response contains actual data
                if any(keyword in response_text.lower() for keyword in ["john", "jane", "employee", "security", "document", "user"]):
                    print(f"   ✅ Contains MongoDB data")
                else:
                    print(f"   ⚠️  No specific data found")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

def test_mongodb_direct_access():
    """Test direct MongoDB access"""
    print("\n🔧 Testing Direct MongoDB Access")
    print("=" * 40)
    
    base_url = "http://localhost:5001"
    
    # Test MongoDB health
    try:
        response = requests.get(f"{base_url}/api/mongodb/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ MongoDB Health: {health_data.get('status', 'unknown')}")
            print(f"   Database: {health_data.get('database', 'unknown')}")
            print(f"   Collections: {health_data.get('collections', 'unknown')}")
        else:
            print(f"❌ MongoDB Health Check Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ MongoDB Health Check Error: {str(e)}")
    
    # Test MongoDB tools
    try:
        response = requests.post(
            f"{base_url}/api/mongodb/tools/search",
            json={
                "query": "employee handbook",
                "collection": "documents",
                "limit": 3
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            count = result.get("count", 0)
            print(f"✅ MongoDB Search: Found {count} documents")
        else:
            print(f"❌ MongoDB Search Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ MongoDB Search Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 RAG + MongoDB Integration Test")
    print("Make sure the backend server is running on port 5001")
    print("Make sure the frontend is running on port 3000")
    print("=" * 60)
    
    # Test direct MongoDB access first
    test_mongodb_direct_access()
    
    # Test RAG + MongoDB integration
    test_rag_mongodb_integration()
    
    print("\n" + "=" * 60)
    print("✅ Integration Test Completed!")
    print("\nNext steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Try the test questions in the chat interface")
    print("3. Check if responses contain MongoDB data")
