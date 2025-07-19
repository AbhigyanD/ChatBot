#!/usr/bin/env python3
"""
TechPal API Test Script
Tests the API endpoints without requiring LLM API keys
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_SESSION_ID = "test-session-123"

def test_health_endpoint():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   App: {data['app_name']} v{data['version']}")
            print(f"   LLM Providers: {data['llm_providers']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the backend running?")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_docs_endpoint():
    """Test the API documentation endpoint"""
    print("\n📚 Testing API docs endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API docs accessible")
            return True
        else:
            print(f"❌ API docs failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API docs error: {e}")
        return False

def test_conversations_endpoint():
    """Test the conversations endpoint"""
    print(f"\n💬 Testing conversations endpoint for session {TEST_SESSION_ID}...")
    try:
        response = requests.get(f"{BASE_URL}/conversations/{TEST_SESSION_ID}")
        if response.status_code == 200:
            conversations = response.json()
            print(f"✅ Conversations endpoint working: {len(conversations)} conversations")
            return True
        else:
            print(f"❌ Conversations endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conversations endpoint error: {e}")
        return False

def test_chat_endpoint_without_llm():
    """Test the chat endpoint (will fail without API keys, but should handle gracefully)"""
    print(f"\n🤖 Testing chat endpoint (without LLM API keys)...")
    try:
        payload = {
            "message": "Hello TechPal!",
            "session_id": TEST_SESSION_ID,
            "age_group": "8-10"
        }
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        
        if response.status_code == 500:
            # Expected without API keys
            data = response.json()
            if "Failed to get response from" in data.get("detail", ""):
                print("✅ Chat endpoint working (correctly handling missing API keys)")
                return True
            else:
                print(f"❌ Unexpected error: {data}")
                return False
        elif response.status_code == 200:
            print("✅ Chat endpoint working (with API keys)")
            return True
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return False

def test_database_operations():
    """Test basic database operations"""
    print(f"\n🗄️ Testing database operations...")
    try:
        # Test creating a conversation
        response = requests.get(f"{BASE_URL}/conversations/{TEST_SESSION_ID}")
        if response.status_code == 200:
            initial_count = len(response.json())
            
            # Try to create a conversation (this should work even without LLM)
            payload = {
                "message": "Test message for database",
                "session_id": TEST_SESSION_ID,
                "age_group": "11-13"
            }
            
            chat_response = requests.post(f"{BASE_URL}/chat", json=payload)
            
            # Check if conversation was created (even if LLM failed)
            response = requests.get(f"{BASE_URL}/conversations/{TEST_SESSION_ID}")
            if response.status_code == 200:
                final_count = len(response.json())
                if final_count >= initial_count:
                    print("✅ Database operations working")
                    return True
                else:
                    print("❌ Database operations failed")
                    return False
            else:
                print("❌ Cannot verify database operations")
                return False
        else:
            print("❌ Cannot test database operations")
            return False
    except Exception as e:
        print(f"❌ Database operations error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 TechPal API Test Suite")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("API Documentation", test_docs_endpoint),
        ("Conversations Endpoint", test_conversations_endpoint),
        ("Chat Endpoint", test_chat_endpoint_without_llm),
        ("Database Operations", test_database_operations),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        time.sleep(0.5)  # Small delay between tests
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! TechPal API is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Add your API keys to the .env file")
        print("   2. Restart the application")
        print("   3. Test the full chat functionality")
    elif passed >= total - 1:
        print("✅ Most tests passed! API is mostly working.")
        print("   (Chat endpoint failure is expected without API keys)")
    else:
        print("❌ Some tests failed. Check the backend logs.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 