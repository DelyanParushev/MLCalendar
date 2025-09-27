#!/usr/bin/env python3
"""
Test script for the authentication API endpoints
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_register():
    """Test user registration"""
    print("Testing user registration...")
    
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    
    # Login using form data (as required by OAuth2PasswordRequestForm)
    data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/login", data=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    
    if response.status_code == 200:
        return result.get("access_token")
    return None

def test_me_endpoint(token):
    """Test the /me endpoint with token"""
    print("\nTesting /me endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_events_endpoint(token):
    """Test creating and retrieving events"""
    print("\nTesting events with authentication...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test getting events
    response = requests.get(f"{BASE_URL}/events", headers=headers)
    print(f"Get events status: {response.status_code}")
    events = response.json()
    print(f"Existing events: {len(events)}")
    
    # Test creating an event
    event_data = {
        "title": "Test Meeting",
        "start": "2025-09-28T10:00:00",
        "end": "2025-09-28T11:00:00",
        "raw_text": "Test meeting tomorrow at 10am"
    }
    
    response = requests.post(f"{BASE_URL}/events", json=event_data, headers=headers)
    print(f"Create event status: {response.status_code}")
    if response.status_code == 200:
        print(f"Created event: {response.json()}")
    else:
        print(f"Error: {response.text}")

def main():
    print("=== API Authentication Test ===\n")
    
    try:
        # Test registration
        register_success = test_register()
        if not register_success and "already registered" not in str(register_success):
            print("❌ Registration failed")
            return
        
        # Test login
        token = test_login()
        if not token:
            print("❌ Login failed")
            return
        
        print(f"✅ Login successful! Token: {token[:20]}...")
        
        # Test /me endpoint
        me_success = test_me_endpoint(token)
        if not me_success:
            print("❌ /me endpoint failed")
            return
        
        # Test events
        test_events_endpoint(token)
        
        print("\n✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()