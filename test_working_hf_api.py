#!/usr/bin/env python3
"""
Test the working HF Space API with proper Bulgarian text
"""
import requests
import json

HF_SPACE_URL = "https://dex7er999-calendar-nlp-api.hf.space"

def test_working_api():
    """Test the working /api/parse endpoint with Bulgarian calendar events"""
    
    test_cases = [
        "Йога клас утре сутринта",
        "Вечеря с Гери в Неделя от 18", 
        "тренировка с тате с колелета в събота в 9",
        "Онлайн лекция по програмиране в понеделник от 10 до 12"
    ]
    
    print("🚀 Testing Working HF Space API")
    print(f"📡 URL: {HF_SPACE_URL}/api/parse")
    print("=" * 60)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: '{text}'")
        
        try:
            response = requests.post(
                f"{HF_SPACE_URL}/api/parse",
                json={"text": text},
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success!")
                print(f"   📊 Response: {json.dumps(result, indent=4, ensure_ascii=False)}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   📊 Error: {json.dumps(error_data, indent=4, ensure_ascii=False)}")
                except:
                    print(f"   📊 Error text: {response.text}")
                    
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

def test_info_endpoint():
    """Test the /api info endpoint"""
    print(f"\n🔍 Testing info endpoint: {HF_SPACE_URL}/api")
    
    try:
        response = requests.get(f"{HF_SPACE_URL}/api", timeout=10)
        if response.status_code == 200:
            info = response.json()
            print("✅ API Info:")
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Info endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Info request failed: {e}")

if __name__ == "__main__":
    test_info_endpoint()
    test_working_api()
    print("\n✅ Testing complete!")