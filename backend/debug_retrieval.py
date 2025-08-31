#!/usr/bin/env python3
"""
Debug script to test retrieval directly
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.rag_service import RAGService

async def debug_retrieval():
    """Debug the retrieval process"""
    print("🔍 Debugging RAG Retrieval...")
    print("=" * 50)
    
    try:
        # Initialize RAG service
        print("1. Initializing RAG service...")
        rag_service = RAGService()
        await rag_service.initialize()
        print("✅ RAG service initialized!")
        
        # Test direct vector store search
        print("\n2. Testing direct vector store search...")
        query = "What is the process for organizing events?"
        
        # Get search results directly
        search_results = rag_service.vector_store.similarity_search(
            query=query,
            k=5,
            threshold=0.3  # Very low threshold to see what's found
        )
        
        print(f"Found {len(search_results)} results:")
        for i, result in enumerate(search_results, 1):
            print(f"\nResult {i}:")
            print(f"  Similarity Score: {result['similarity_score']:.3f}")
            print(f"  Source: {result['metadata']['source']}")
            print(f"  Category: {result['metadata']['category']}")
            print(f"  Content Preview: {result['content'][:200]}...")
        
        # Test with different queries
        test_queries = [
            "event planning",
            "organizing events", 
            "event approval process",
            "attendance requirements",
            "leave application"
        ]
        
        print(f"\n3. Testing different queries...")
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = rag_service.vector_store.similarity_search(query, k=3, threshold=0.3)
            print(f"  Found {len(results)} results")
            if results:
                print(f"  Best score: {results[0]['similarity_score']:.3f}")
                print(f"  Best source: {results[0]['metadata']['source']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_retrieval())
    sys.exit(0 if success else 1)
