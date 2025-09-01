#!/usr/bin/env python3
"""
MongoDB Test Questions Script
Tests various MongoDB queries and operations with sample questions.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mongodb_service import mongodb_service
from agents.mongodb_tools import mongodb_tools

async def test_mongodb_questions():
    """Test various MongoDB queries with different question types"""
    print("🧪 MongoDB Test Questions")
    print("=" * 50)
    
    try:
        # Initialize MongoDB service
        await mongodb_service.initialize()
        print("✅ MongoDB service initialized\n")
        
        # Test Questions Categories
        test_categories = {
            "User Queries": [
                "Show me all users",
                "Find users with admin role",
                "List all active users",
                "Show me users with email addresses",
                "Find inactive users"
            ],
            
            "Document Queries": [
                "Show me all documents",
                "Find documents about security",
                "List policy documents",
                "Show me documents by HR Department",
                "Find recent documents",
                "Search for employee handbook",
                "Show me documents with 'guidelines' in the title"
            ],
            
            "Aggregation Queries": [
                "Count all documents",
                "Count users by role",
                "Count documents by type",
                "Show me document statistics",
                "How many active users do we have?"
            ],
            
            "Filtered Queries": [
                "Show me documents created this week",
                "Find users with admin status",
                "List documents with version 2.0 or higher",
                "Show me documents in the IT category",
                "Find conversations from user john_doe"
            ],
            
            "Search Queries": [
                "Search for 'employee handbook'",
                "Find documents containing 'security'",
                "Search for 'project management'",
                "Look for 'customer service' documents",
                "Find anything about 'data'"
            ]
        }
        
        # Run tests for each category
        for category, questions in test_categories.items():
            print(f"\n📋 {category}")
            print("-" * 30)
            
            for i, question in enumerate(questions, 1):
                try:
                    print(f"\n{i}. Question: {question}")
                    
                    # Determine collection based on question
                    if any(word in question.lower() for word in ["user", "admin", "role"]):
                        collection = "users"
                    elif any(word in question.lower() for word in ["document", "policy", "handbook", "security"]):
                        collection = "documents"
                    elif any(word in question.lower() for word in ["conversation", "chat"]):
                        collection = "conversations"
                    else:
                        collection = "documents"  # Default
                    
                    # Execute search
                    result = await mongodb_tools.search_database_tool(question, collection, 5)
                    
                    if result.get("success"):
                        count = result.get("count", 0)
                        print(f"   ✅ Found {count} results")
                        
                        if count > 0:
                            results = result.get("results", [])
                            for j, item in enumerate(results[:3], 1):  # Show first 3 results
                                if collection == "users":
                                    name = item.get("full_name", item.get("username", "Unknown"))
                                    role = item.get("role", "N/A")
                                    print(f"      {j}. {name} ({role})")
                                elif collection == "documents":
                                    title = item.get("title", "Untitled")
                                    doc_type = item.get("document_type", "N/A")
                                    print(f"      {j}. {title} ({doc_type})")
                                else:
                                    print(f"      {j}. {str(item)[:50]}...")
                    else:
                        print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"   ❌ Exception: {str(e)}")
        
        # Test specific aggregation queries
        print(f"\n📊 Aggregation Tests")
        print("-" * 30)
        
        aggregation_tests = [
            ("Count all documents", "documents"),
            ("Count users by role", "users"),
            ("Count documents by type", "documents"),
            ("Show analytics data", "analytics")
        ]
        
        for question, collection in aggregation_tests:
            try:
                print(f"\nQuestion: {question}")
                result = await mongodb_tools.aggregate_data_tool(question, collection)
                
                if result.get("success"):
                    count = result.get("count", 0)
                    print(f"   ✅ Aggregation result: {count} results")
                else:
                    print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
        
        print("\n" + "=" * 50)
        print("✅ MongoDB Test Questions Completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

def print_test_questions():
    """Print all test questions for manual testing"""
    print("\n📝 Manual Test Questions for API/UI Testing")
    print("=" * 60)
    
    questions = [
        # User Management
        "Show me all users",
        "Find users with admin role", 
        "List all active users",
        "Show me users with email addresses",
        "Find inactive users",
        
        # Document Management
        "Show me all documents",
        "Find documents about security",
        "List policy documents", 
        "Show me documents by HR Department",
        "Find recent documents",
        "Search for employee handbook",
        "Show me documents with 'guidelines' in the title",
        
        # Aggregation
        "Count all documents",
        "Count users by role",
        "Count documents by type",
        "Show me document statistics",
        "How many active users do we have?",
        
        # Filtered Queries
        "Show me documents created this week",
        "Find users with admin status",
        "List documents with version 2.0 or higher",
        "Show me documents in the IT category",
        "Find conversations from user john_doe",
        
        # Search Queries
        "Search for 'employee handbook'",
        "Find documents containing 'security'",
        "Search for 'project management'",
        "Look for 'customer service' documents",
        "Find anything about 'data'"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"{i:2d}. {question}")
    
    print("\n🔧 API Endpoints to Test:")
    print("GET  /api/mongodb/health")
    print("GET  /api/mongodb/stats")
    print("GET  /api/mongodb/documents")
    print("GET  /api/mongodb/users")
    print("POST /api/mongodb/tools/search")
    print("POST /api/mongodb/tools/aggregate")
    print("POST /api/enhanced-chat")

if __name__ == "__main__":
    print("🚀 MongoDB Test Questions")
    print("1. Run automated tests")
    print("2. Show manual test questions")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        success = asyncio.run(test_mongodb_questions())
        if success:
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n❌ Some tests failed.")
    elif choice == "2":
        print_test_questions()
    else:
        print("Invalid choice. Running automated tests...")
        success = asyncio.run(test_mongodb_questions())
