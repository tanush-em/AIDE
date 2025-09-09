#!/usr/bin/env python3
"""
Test script to verify the reindex functionality
"""

import requests
import time
import json

def test_reindex_endpoint():
    """Test the reindex endpoint"""
    print("🧪 Testing reindex endpoint...")
    
    try:
        # Test the reindex endpoint
        response = requests.post('http://localhost:5001/api/rag/rebuild', timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reindex successful: {data}")
            return True
        else:
            print(f"❌ Reindex failed with status {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint to see if reindex info is included"""
    print("🧪 Testing health endpoint...")
    
    try:
        response = requests.get('http://localhost:5001/api/health', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check successful")
            print(f"Features: {data.get('features', {})}")
            print(f"Reindex endpoint: {data.get('endpoints', {}).get('reindex', 'Not found')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check request failed: {e}")
        return False

def test_rag_status():
    """Test the RAG status endpoint"""
    print("🧪 Testing RAG status endpoint...")
    
    try:
        response = requests.get('http://localhost:5001/api/rag/status', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ RAG status check successful")
            print(f"Initialized: {data.get('initialized', False)}")
            if data.get('vector_store'):
                print(f"Vector store stats: {data['vector_store']}")
            return True
        else:
            print(f"❌ RAG status check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ RAG status request failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting reindex functionality tests...")
    print("=" * 50)
    
    # Wait a bit for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    print()
    
    # Test RAG status
    rag_ok = test_rag_status()
    print()
    
    # Test reindex endpoint
    reindex_ok = test_reindex_endpoint()
    print()
    
    # Summary
    print("=" * 50)
    print("📊 Test Results:")
    print(f"Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"RAG status: {'✅ PASS' if rag_ok else '❌ FAIL'}")
    print(f"Reindex endpoint: {'✅ PASS' if reindex_ok else '❌ FAIL'}")
    
    if all([health_ok, rag_ok, reindex_ok]):
        print("\n🎉 All tests passed! Reindex functionality is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the server logs.")

if __name__ == "__main__":
    main()
