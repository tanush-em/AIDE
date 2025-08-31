#!/usr/bin/env python3
"""
Test script to verify the Flask backend setup
"""

import requests
import time
import sys
import os

def test_backend():
    """Test the Flask backend endpoints"""
    base_url = "http://localhost:5000"
    
    print("Testing Flask Backend...")
    print("=" * 40)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test data endpoint
    try:
        response = requests.get(f"{base_url}/api/data", timeout=5)
        if response.status_code == 200:
            print("✅ Data endpoint working")
            data = response.json()
            print(f"   Found {len(data.get('data', []))} items")
        else:
            print(f"❌ Data endpoint failed with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Data endpoint error: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Root endpoint error: {e}")
        return False
    
    print("=" * 40)
    print("🎉 All backend tests passed!")
    return True

if __name__ == "__main__":
    print("Make sure the Flask backend is running on http://localhost:5000")
    print("You can start it with: cd backend && source venv/bin/activate && python app.py")
    print()
    
    success = test_backend()
    sys.exit(0 if success else 1)
