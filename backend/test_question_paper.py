#!/usr/bin/env python3
"""
Test script to verify question paper integration
"""

import requests
import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:5001"
QUESTION_PAPER_URL = "http://localhost:5890"

def test_question_paper_endpoints():
    """Test question paper related endpoints"""
    print("🧪 Testing Question Paper Integration")
    print("=" * 50)
    
    # Test question paper status
    print("\n📡 Testing Question Paper Service Status")
    try:
        response = requests.get(f"{BASE_URL}/api/question-paper/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status API working")
            print(f"   📊 Service running: {data['data']['is_running']}")
            if data['data']['is_running']:
                print(f"   🚀 Question Paper service is accessible at {QUESTION_PAPER_URL}")
            else:
                print(f"   ⚠️  Question Paper service is not running")
        else:
            print(f"   ❌ Status API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing status: {str(e)}")
    
    # Test question paper info
    print("\n📋 Testing Question Paper Info")
    try:
        response = requests.get(f"{BASE_URL}/api/question-paper/info")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Info API working")
            print(f"   📝 Name: {data['data']['name']}")
            print(f"   📄 Description: {data['data']['description']}")
            print(f"   🔗 URL: {data['data']['url']}")
            print(f"   📊 Status: {data['data']['status']}")
        else:
            print(f"   ❌ Info API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing info: {str(e)}")
    
    # Test available courses
    print("\n📚 Testing Available Courses")
    try:
        response = requests.get(f"{BASE_URL}/api/question-paper/courses")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Courses API working")
            print(f"   📊 Available courses: {len(data['data'])}")
            for course in data['data'][:3]:  # Show first 3 courses
                print(f"      - {course['code']}: {course['name']}")
        else:
            print(f"   ❌ Courses API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing courses: {str(e)}")
    
    # Test redirect functionality
    print("\n🔄 Testing Redirect Functionality")
    try:
        redirect_data = {
            "course_code": "CS101",
            "paper_type": "midterm"
        }
        response = requests.post(f"{BASE_URL}/api/question-paper/redirect", json=redirect_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Redirect API working")
            print(f"   🔗 Redirect URL: {data['data']['redirect_url']}")
            print(f"   📚 Course: {data['data']['course_code']}")
            print(f"   📄 Type: {data['data']['paper_type']}")
        else:
            print(f"   ❌ Redirect API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing redirect: {str(e)}")
    
    # Test direct connection to question paper service
    print("\n🌐 Testing Direct Connection to Question Paper Service")
    try:
        response = requests.get(QUESTION_PAPER_URL, timeout=5)
        print(f"   ✅ Direct connection successful")
        print(f"   📊 Status Code: {response.status_code}")
        print(f"   ⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
    except requests.exceptions.Timeout:
        print(f"   ⏰ Connection timeout - service may be slow or not responding")
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - service is not running on {QUESTION_PAPER_URL}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Question Paper Integration Test Complete!")
    print("\n📋 Summary:")
    print("   - Question Paper tab added to navigation")
    print("   - Dashboard quick action button added")
    print("   - Backend APIs for service status and info")
    print("   - Redirect functionality implemented")
    print("   - Course integration available")
    
    print("\n🚀 Next Steps:")
    print("   1. Start your Question Paper application on localhost:5890")
    print("   2. Start the main application: python app.py")
    print("   3. Start the frontend: cd frontend && npm run dev")
    print("   4. Click on 'Question Papers' tab or dashboard button")
    print("   5. The external application will open in a new tab!")

if __name__ == "__main__":
    test_question_paper_endpoints()
