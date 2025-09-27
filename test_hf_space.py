#!/usr/bin/env python3
"""
Test script for Hugging Face Space API
"""
import requests
import json

# Your HF Space URL
HF_SPACE_URL = "https://dex7er999-calendar-nlp-api.hf.space"

def test_hf_space_api():
    """Test the HF Space API with various inputs"""
    
    test_cases = [
        "Йога клас утре сутринта",
        "Вечеря с Гери в Неделя от 18", 
        "тренировка с тате с колелета в събота в 9",
        "Онлайн лекция по програмиране в понеделник от 10 до 12"
    ]
    
    print("🚀 Testing Hugging Face Space API")
    print(f"📡 URL: {HF_SPACE_URL}")
    print("=" * 60)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: '{text}'")
        
        try:
            # Test different possible API endpoints
            endpoints_to_try = [
                "/api/parse",
                "/parse", 
                "/predict",
                "/api/predict",
                ""  # root endpoint
            ]
            
            success = False
            for endpoint in endpoints_to_try:
                try:
                    url = f"{HF_SPACE_URL}{endpoint}"
                    print(f"   Trying: {url}")
                    
                    # Try different payload formats
                    payloads = [
                        {"text": text},
                        {"inputs": text},
                        {"data": [text]}
                    ]
                    
                    for payload in payloads:
                        try:
                            response = requests.post(
                                url,
                                json=payload,
                                timeout=30,
                                headers={"Content-Type": "application/json"}
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                print(f"   ✅ Success!")
                                print(f"   📊 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                                success = True
                                break
                                
                        except Exception as e:
                            continue
                    
                    if success:
                        break
                        
                except Exception as e:
                    continue
            
            if not success:
                print(f"   ❌ All endpoints failed")
                
                # Try GET request to see if space is running
                try:
                    response = requests.get(HF_SPACE_URL, timeout=10)
                    print(f"   🔍 Space status: {response.status_code}")
                    if response.status_code == 200:
                        print(f"   📄 Space is running but API endpoints might be different")
                    else:
                        print(f"   ⚠️ Space might be sleeping or having issues")
                except:
                    print(f"   ❌ Cannot reach the space at all")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_space_health():
    """Test if the space is running"""
    print("\n🏥 Health Check:")
    try:
        response = requests.get(HF_SPACE_URL, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            print("   ✅ Space is running!")
            return True
        else:
            print("   ⚠️ Space returned non-200 status")
            return False
            
    except Exception as e:
        print(f"   ❌ Cannot connect: {e}")
        return False

if __name__ == "__main__":
    print("🧪 HF Space API Testing Tool")
    print("=" * 60)
    
    # First check if space is healthy
    is_healthy = test_space_health()
    
    if is_healthy:
        # Run API tests
        test_hf_space_api()
    else:
        print("\n💡 Suggestions:")
        print("1. Check if your HF Space is running")
        print("2. Visit the space URL in browser to wake it up")
        print("3. Check the space logs for any errors")
        
    print("\n✅ Testing complete!")