#!/usr/bin/env python3
"""
MongoDB Seeding Script
Populates the MongoDB database with sample data for testing the enhanced RAG system.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mongodb_service import mongodb_service
from database.models import User, Document, Conversation, Analytics

async def seed_mongodb():
    """Seed MongoDB with sample data"""
    try:
        print("Initializing MongoDB service...")
        await mongodb_service.initialize()
        
        print("Seeding users...")
        await seed_users()
        
        print("Seeding documents...")
        await seed_documents()
        
        print("Seeding conversations...")
        await seed_conversations()
        
        print("Seeding analytics...")
        await seed_analytics()
        
        print("MongoDB seeding completed successfully!")
        
        # Print database stats
        stats = await mongodb_service.get_database_stats()
        print(f"\nDatabase Statistics:")
        print(f"Collections: {stats.get('collection_counts', {})}")
        
    except Exception as e:
        print(f"Error seeding MongoDB: {str(e)}")
        raise e

async def seed_users():
    """Seed sample users"""
    users_data = [
        {
            "username": "john_doe",
            "email": "john.doe@example.com",
            "full_name": "John Doe",
            "role": "admin",
            "status": "active",
            "preferences": {"theme": "dark", "language": "en"}
        },
        {
            "username": "jane_smith",
            "email": "jane.smith@example.com",
            "full_name": "Jane Smith",
            "role": "user",
            "status": "active",
            "preferences": {"theme": "light", "language": "en"}
        },
        {
            "username": "bob_wilson",
            "email": "bob.wilson@example.com",
            "full_name": "Bob Wilson",
            "role": "moderator",
            "status": "active",
            "preferences": {"theme": "dark", "language": "en"}
        },
        {
            "username": "alice_brown",
            "email": "alice.brown@example.com",
            "full_name": "Alice Brown",
            "role": "user",
            "status": "inactive",
            "preferences": {"theme": "light", "language": "en"}
        }
    ]
    
    for user_data in users_data:
        try:
            await mongodb_service.create_user(user_data)
            print(f"Created user: {user_data['username']}")
        except Exception as e:
            print(f"Error creating user {user_data['username']}: {str(e)}")

async def seed_documents():
    """Seed sample documents"""
    documents_data = [
        {
            "title": "Employee Handbook",
            "content": "This handbook contains all the policies and procedures that employees must follow. It covers topics such as workplace conduct, benefits, and company policies.",
            "document_type": "policy",
            "category": "HR",
            "tags": ["employee", "handbook", "policies", "procedures"],
            "author": "HR Department",
            "version": "2.1",
            "status": "active"
        },
        {
            "title": "Data Security Guidelines",
            "content": "These guidelines outline the security measures that must be followed when handling sensitive data. All employees must adhere to these security protocols.",
            "document_type": "procedure",
            "category": "IT",
            "tags": ["security", "data", "guidelines", "IT"],
            "author": "IT Security Team",
            "version": "1.5",
            "status": "active"
        },
        {
            "title": "Project Management Best Practices",
            "content": "This guide provides best practices for managing projects effectively. It includes methodologies, tools, and techniques for successful project delivery.",
            "document_type": "guide",
            "category": "Management",
            "tags": ["project", "management", "best practices", "methodology"],
            "author": "Project Management Office",
            "version": "3.0",
            "status": "active"
        },
        {
            "title": "Customer Service Standards",
            "content": "These standards define the level of service that customers can expect from our organization. They cover communication, response times, and quality metrics.",
            "document_type": "procedure",
            "category": "Customer Service",
            "tags": ["customer", "service", "standards", "quality"],
            "author": "Customer Service Department",
            "version": "1.2",
            "status": "active"
        },
        {
            "title": "Quarterly Sales Report Q4 2023",
            "content": "This report summarizes the sales performance for Q4 2023. It includes revenue figures, growth metrics, and analysis of key performance indicators.",
            "document_type": "report",
            "category": "Sales",
            "tags": ["sales", "report", "Q4", "2023", "revenue"],
            "author": "Sales Analytics Team",
            "version": "1.0",
            "status": "active"
        },
        {
            "title": "Software Development Lifecycle",
            "content": "This document describes the software development lifecycle used by our development team. It covers planning, development, testing, and deployment phases.",
            "document_type": "procedure",
            "category": "Development",
            "tags": ["software", "development", "lifecycle", "SDLC"],
            "author": "Development Team",
            "version": "2.3",
            "status": "active"
        }
    ]
    
    for doc_data in documents_data:
        try:
            await mongodb_service.create_document(doc_data)
            print(f"Created document: {doc_data['title']}")
        except Exception as e:
            print(f"Error creating document {doc_data['title']}: {str(e)}")

async def seed_conversations():
    """Seed sample conversations"""
    conversations_data = [
        {
            "session_id": "session_001",
            "user_id": "john_doe",
            "title": "Employee Handbook Discussion",
            "messages": [
                {
                    "role": "user",
                    "content": "What are the main policies in the employee handbook?",
                    "timestamp": datetime.utcnow() - timedelta(hours=2)
                },
                {
                    "role": "assistant",
                    "content": "The employee handbook covers workplace conduct, benefits, and company policies. Would you like me to provide more specific details about any particular policy?",
                    "timestamp": datetime.utcnow() - timedelta(hours=2, minutes=1)
                }
            ],
            "status": "active"
        },
        {
            "session_id": "session_002",
            "user_id": "jane_smith",
            "title": "Security Guidelines Query",
            "messages": [
                {
                    "role": "user",
                    "content": "How do I handle sensitive data according to the security guidelines?",
                    "timestamp": datetime.utcnow() - timedelta(hours=1)
                },
                {
                    "role": "assistant",
                    "content": "According to the data security guidelines, you must follow specific protocols when handling sensitive data. Let me search for the exact procedures.",
                    "timestamp": datetime.utcnow() - timedelta(hours=1, minutes=30)
                }
            ],
            "status": "active"
        }
    ]
    
    for conv_data in conversations_data:
        try:
            await mongodb_service.create_conversation(conv_data)
            print(f"Created conversation: {conv_data['title']}")
        except Exception as e:
            print(f"Error creating conversation {conv_data['title']}: {str(e)}")

async def seed_analytics():
    """Seed sample analytics data"""
    analytics_data = [
        {
            "event_type": "query",
            "user_id": "john_doe",
            "session_id": "session_001",
            "query": "What are the main policies in the employee handbook?",
            "response": "The employee handbook covers workplace conduct, benefits, and company policies.",
            "source": "rag",
            "confidence": 0.85,
            "processing_time": 1.2
        },
        {
            "event_type": "query",
            "user_id": "jane_smith",
            "session_id": "session_002",
            "query": "How do I handle sensitive data according to the security guidelines?",
            "response": "According to the data security guidelines, you must follow specific protocols.",
            "source": "combined",
            "confidence": 0.92,
            "processing_time": 2.1
        },
        {
            "event_type": "user_action",
            "user_id": "bob_wilson",
            "session_id": "session_003",
            "query": "Show me all active users",
            "response": "Found 3 active users in the system.",
            "source": "mongodb",
            "confidence": 0.95,
            "processing_time": 0.8
        }
    ]
    
    for analytics_data_item in analytics_data:
        try:
            await mongodb_service.log_analytics(analytics_data_item)
            print(f"Created analytics event: {analytics_data_item['event_type']}")
        except Exception as e:
            print(f"Error creating analytics event: {str(e)}")

if __name__ == "__main__":
    print("Starting MongoDB seeding...")
    asyncio.run(seed_mongodb())
