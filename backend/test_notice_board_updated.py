#!/usr/bin/env python3
"""
Test script to verify updated notice board functionality with new data structure
"""

import requests
import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

BASE_URL = "http://localhost:5001"

def test_notice_board_endpoints():
    """Test notice board related endpoints with new data structure"""
    print("🧪 Testing Updated Notice Board Integration")
    print("=" * 50)
    
    # Test notices list
    print("\n📋 Testing Notices List")
    try:
        response = requests.get(f"{BASE_URL}/api/notices")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Notices API working")
            print(f"   📊 Total notices: {len(data['data'])}")
            
            # Show first few notices with new structure
            for notice in data['data'][:3]:
                print(f"      - {notice['title']}")
                print(f"        Type: {notice['type']}, Priority: {notice['priority']}")
                print(f"        Author: {notice['author']}")
                print(f"        Target Audience: {notice.get('targetAudience', 'Not specified')}")
                if notice.get('course'):
                    print(f"        Course: {notice['course']}")
                if notice.get('tags'):
                    print(f"        Tags: {', '.join(notice['tags'])}")
                if notice.get('readBy'):
                    print(f"        Read by: {len(notice['readBy'])} people")
                print()
        else:
            print(f"   ❌ Notices API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing notices: {str(e)}")
    
    # Test notice stats
    print("\n📊 Testing Notice Stats")
    try:
        response = requests.get(f"{BASE_URL}/api/notices/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Stats API working")
            print(f"   📁 Total notices: {data['data']['totalNotices']}")
            print(f"   ✅ Active notices: {data['data']['activeNotices']}")
            print(f"   🚨 Urgent notices: {data['data']['urgentNotices']}")
            print(f"   ⏰ Expired notices: {data['data']['expiredNotices']}")
        else:
            print(f"   ❌ Stats API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing stats: {str(e)}")
    
    # Test specific notice
    print("\n📄 Testing Specific Notice")
    try:
        response = requests.get(f"{BASE_URL}/api/notices/1")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Notice detail API working")
            notice = data['data']
            print(f"   📝 Title: {notice['title']}")
            print(f"   📊 Type: {notice['type']}")
            print(f"   🎯 Priority: {notice['priority']}")
            print(f"   👥 Target Audience: {notice.get('targetAudience', 'Not specified')}")
            if notice.get('course'):
                print(f"   📚 Course: {notice['course']}")
            if notice.get('tags'):
                print(f"   🏷️ Tags: {', '.join(notice['tags'])}")
            if notice.get('readBy'):
                print(f"   👀 Read by: {len(notice['readBy'])} people")
            print(f"   📅 Created: {notice['createdAt']}")
            if notice.get('updatedAt'):
                print(f"   📝 Updated: {notice['updatedAt']}")
            if notice.get('expiresAt'):
                print(f"   ⏰ Expires: {notice['expiresAt']}")
        else:
            print(f"   ❌ Notice detail API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing notice detail: {str(e)}")
    
    # Test notice creation with new structure
    print("\n➕ Testing Notice Creation")
    try:
        new_notice = {
            "title": "Test Notice with New Structure",
            "content": "This is a test notice to verify the new data structure works correctly.",
            "type": "announcement",
            "priority": "medium",
            "targetAudience": "students",
            "author": "Test Author",
            "authorId": "TEST001",
            "expiresAt": "2024-12-31T23:59:59Z",
            "tags": ["test", "new-structure", "verification"]
        }
        
        response = requests.post(f"{BASE_URL}/api/notices", json=new_notice)
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Notice creation API working")
            print(f"   📝 Created notice ID: {data['data']['id']}")
            print(f"   📊 Type: {data['data']['type']}")
            print(f"   🎯 Target Audience: {data['data']['targetAudience']}")
            print(f"   🏷️ Tags: {', '.join(data['data']['tags'])}")
        else:
            print(f"   ❌ Notice creation API failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error testing notice creation: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Updated Notice Board Integration Test Complete!")
    print("\n📋 Summary of Changes:")
    print("   - Updated Notice interface to handle optional fields")
    print("   - Added support for targetAudience field")
    print("   - Added support for course field")
    print("   - Added support for updatedAt field")
    print("   - Added support for readBy array")
    print("   - Added support for tags array")
    print("   - Updated UI to display new fields")
    print("   - Added proper null checks for optional fields")
    print("   - Enhanced filtering and search functionality")
    
    print("\n🎨 UI Improvements:")
    print("   - Target audience badges (All, Students, Faculty, Course Specific)")
    print("   - Course-specific notices show course code")
    print("   - Tags display with proper styling")
    print("   - Read count display")
    print("   - Updated timestamp display")
    print("   - Enhanced modal view with all new fields")
    
    print("\n🚀 Next Steps:")
    print("   1. Start the main application: python app.py")
    print("   2. Start the frontend: cd frontend && npm run dev")
    print("   3. Click on 'Notice Board' tab in navigation")
    print("   4. View notices with new structure and enhanced UI")
    print("   5. Test filtering by target audience and course")

if __name__ == "__main__":
    test_notice_board_endpoints()
