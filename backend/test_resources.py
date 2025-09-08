#!/usr/bin/env python3
"""
Test script to verify resources functionality
"""

import requests
import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:5001"

def test_resources_endpoints():
    """Test resources related endpoints"""
    print("🧪 Testing Resources Integration")
    print("=" * 50)
    
    # Test resources list
    print("\n📁 Testing Resources List")
    try:
        response = requests.get(f"{BASE_URL}/api/resources")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Resources API working")
            print(f"   📊 Total files: {len(data['data'])}")
            for file in data['data'][:3]:  # Show first 3 files
                print(f"      - {file['name']} ({file['type']}, {file['size']} bytes)")
        else:
            print(f"   ❌ Resources API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing resources: {str(e)}")
    
    # Test resources stats
    print("\n📊 Testing Resources Stats")
    try:
        response = requests.get(f"{BASE_URL}/api/resources/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Stats API working")
            print(f"   📁 Total files: {data['data']['total_files']}")
            print(f"   💾 Total size: {data['data']['total_size']} bytes")
            print(f"   📋 File types: {data['data']['file_types']}")
        else:
            print(f"   ❌ Stats API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing stats: {str(e)}")
    
    # Test specific file info
    print("\n📄 Testing File Info")
    try:
        response = requests.get(f"{BASE_URL}/api/resources/sample_data.csv")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ File info API working")
            print(f"   📝 File: {data['data']['name']}")
            print(f"   📊 Type: {data['data']['type']}")
            print(f"   💾 Size: {data['data']['size']} bytes")
        else:
            print(f"   ❌ File info API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing file info: {str(e)}")
    
    # Test file viewing
    print("\n👁️ Testing File Viewing")
    try:
        response = requests.get(f"{BASE_URL}/api/resources/sample_data.csv/view")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ File view API working")
            print(f"   📝 File: {data['data']['name']}")
            print(f"   📊 Type: {data['data']['type']}")
            print(f"   📄 Content length: {len(data['data']['content'])} characters")
            if data['data']['parsed_content']:
                print(f"   📋 Parsed content: {len(data['data']['parsed_content'])} rows")
        else:
            print(f"   ❌ File view API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing file view: {str(e)}")
    
    # Test JSON file viewing
    print("\n📋 Testing JSON File Viewing")
    try:
        response = requests.get(f"{BASE_URL}/api/resources/course_schedule.json/view")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ JSON view API working")
            print(f"   📝 File: {data['data']['name']}")
            print(f"   📊 Type: {data['data']['type']}")
            if data['data']['parsed_content']:
                print(f"   📋 Parsed JSON keys: {list(data['data']['parsed_content'].keys())}")
        else:
            print(f"   ❌ JSON view API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing JSON view: {str(e)}")
    
    # Test text file viewing
    print("\n📝 Testing Text File Viewing")
    try:
        response = requests.get(f"{BASE_URL}/api/resources/academic_calendar.txt/view")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Text view API working")
            print(f"   📝 File: {data['data']['name']}")
            print(f"   📊 Type: {data['data']['type']}")
            print(f"   📄 Content preview: {data['data']['content'][:100]}...")
        else:
            print(f"   ❌ Text view API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing text view: {str(e)}")
    
    # Test file download (without actually downloading)
    print("\n⬇️ Testing File Download")
    try:
        response = requests.head(f"{BASE_URL}/api/resources/sample_data.csv/download")
        if response.status_code == 200:
            print(f"   ✅ Download API working")
            print(f"   📊 Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"   📊 Content-Length: {response.headers.get('Content-Length', 'Unknown')} bytes")
        else:
            print(f"   ❌ Download API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing download: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Resources Integration Test Complete!")
    print("\n📋 Summary:")
    print("   - Resources tab added to navigation")
    print("   - Backend APIs for file listing and viewing")
    print("   - Support for CSV, JSON, Excel, PDF, Word, Text files")
    print("   - File download functionality")
    print("   - File statistics and filtering")
    print("   - In-browser file viewing for supported formats")
    
    print("\n🚀 Next Steps:")
    print("   1. Start the main application: python app.py")
    print("   2. Start the frontend: cd frontend && npm run dev")
    print("   3. Click on 'Resources' tab in navigation")
    print("   4. View and download files from the resources folder")
    print("   5. Add more files to backend/data/knowledge/resources/")

if __name__ == "__main__":
    test_resources_endpoints()
