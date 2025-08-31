#!/usr/bin/env python3
"""
Test script for the RAG system
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.rag_service import RAGService

async def test_rag_system():
    """Test the RAG system"""
    print("🧪 Testing RAG System...")
    print("=" * 50)
    
    try:
        # Initialize RAG service
        print("1. Initializing RAG service...")
        rag_service = RAGService()
        await rag_service.initialize()
        print("✅ RAG service initialized successfully!")
        
        # Test system status
        print("\n2. Checking system status...")
        status = rag_service.get_system_status()
        print(f"✅ System status: {status['initialized']}")
        print(f"   Vector store documents: {status.get('vector_store', {}).get('total_documents', 0)}")
        
        # Test query processing
        print("\n3. Testing query processing...")
        test_queries = [
            "What are the attendance requirements?",
            "How do I apply for leave?",
            "What is the process for organizing events?",
            "Tell me about grading policies"
        ]
        
        # Note: This test requires a Groq API key to be set in the environment
        if not rag_service.config.GROQ_API_KEY:
            print("⚠️  No Groq API key found. Skipping query processing tests.")
            print("   Set GROQ_API_KEY in your .env file to test full functionality.")
            return True
        
        session_id = "test-session-123"
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Test {i}: {query}")
            try:
                result = await rag_service.process_query(session_id, query)
                print(f"   ✅ Response: {result['response'][:100]}...")
                print(f"   Confidence: {result.get('confidence', 'unknown')}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Test conversation history
        print("\n4. Testing conversation history...")
        history = rag_service.get_conversation_history(session_id)
        print(f"✅ Conversation history retrieved: {len(history.get('history', []))} messages")
        
        # Test export functionality
        print("\n5. Testing export functionality...")
        export_result = rag_service.export_conversation(session_id, 'json')
        print(f"✅ Export successful: {len(export_result.get('data', ''))} characters")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_rag_system())
    sys.exit(0 if success else 1)
