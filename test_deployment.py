#!/usr/bin/env python3
"""
Test the deployed backend API
"""
import requests
import json
import time

BASE_URL = "https://mlcalendar-api.onrender.com"

def wait_for_backend():
    """Wait for backend to come online"""
    print("⏳ Waiting for backend to deploy...")
    
    for i in range(30):  # Wait up to 5 minutes
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                print("✅ Backend is online!")
                return True
        except Exception as e:
            print(f"   Attempt {i+1}/30: {e}")
        
        time.sleep(10)
    
    print("❌ Backend did not come online")
    return False

def test_login():
    """Test login functionality"""
    print("\n🧪 Testing login...")
    
    try:
        # Test registration first
        register_data = {
            "username": "testuser" + str(int(time.time())),
            "email": "test@example.com", 
            "password": "testpass123"
        }
        
        response = requests.post(f"{BASE_URL}/register", json=register_data, timeout=10)
        print(f"Registration: {response.status_code}")
        
        if response.status_code == 201:
            # Test login
            login_data = {
                "username": register_data["username"],
                "password": register_data["password"]
            }
            
            response = requests.post(f"{BASE_URL}/login", data=login_data, timeout=10)
            print(f"Login: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                print(f"✅ Login successful, got token: {token_data.get('access_token', 'N/A')[:20]}...")
                return token_data.get('access_token')
            else:
                print(f"❌ Login failed: {response.text}")
        else:
            print(f"❌ Registration failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Login test error: {e}")
    
    return None

def test_parse():
    """Test parse functionality"""
    print("\n🧪 Testing parse...")
    
    try:
        parse_data = {"text": "гейминг утре от 19"}
        response = requests.post(f"{BASE_URL}/parse", json=parse_data, timeout=30)
        
        print(f"Parse: {response.status_code}")
        result = response.json()
        print(f"Parse result: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and "title" in result:
            print("✅ Parse working!")
        else:
            print("❌ Parse failed!")
            
    except Exception as e:
        print(f"❌ Parse test error: {e}")

if __name__ == "__main__":
    print("🚀 Testing deployed backend")
    
    if wait_for_backend():
        test_login()
        test_parse()
    else:
        print("💡 Try again in a few minutes - Render deployments can take 5-10 minutes")
        
    print("\n✅ Backend testing complete!")