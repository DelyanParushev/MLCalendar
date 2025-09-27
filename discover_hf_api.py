#!/usr/bin/env python3
"""
Simple API endpoint discovery for HF Space
"""
import requests
import json

HF_SPACE_URL = "https://dex7er999-calendar-nlp-api.hf.space"

def discover_endpoints():
    """Try to discover available API endpoints"""
    print("🔍 Discovering HF Space API endpoints")
    print(f"📡 Base URL: {HF_SPACE_URL}")
    print("=" * 60)
    
    # Test various common endpoints
    endpoints = [
        "",
        "/",
        "/api",
        "/predict",
        "/api/predict", 
        "/parse",
        "/api/parse",
        "/run/predict",
        "/health",
        "/docs",
        "/gradio_api/call/predict",
        "/call/predict",
        "/api/v1/predict"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{HF_SPACE_URL}{endpoint}"
            print(f"\n🧪 Testing: {url}")
            
            # Try GET first
            try:
                response = requests.get(url, timeout=10)
                print(f"   GET: {response.status_code} - {response.headers.get('content-type', 'unknown')}")
                
                if response.status_code == 200:
                    content = response.text[:200] + "..." if len(response.text) > 200 else response.text
                    print(f"   Content preview: {content}")
                    
                    # If it looks like JSON, try to parse
                    if response.headers.get('content-type', '').startswith('application/json'):
                        try:
                            data = response.json()
                            print(f"   JSON: {json.dumps(data, indent=2)}")
                        except:
                            pass
                            
            except Exception as e:
                print(f"   GET failed: {e}")
            
            # Try POST with sample data
            try:
                test_data = {"text": "test"}
                response = requests.post(url, json=test_data, timeout=10)
                print(f"   POST: {response.status_code} - {response.headers.get('content-type', 'unknown')}")
                
                if response.status_code in [200, 422]:  # 422 might be validation error which is still useful
                    try:
                        data = response.json()
                        print(f"   POST JSON: {json.dumps(data, indent=2)}")
                    except:
                        content = response.text[:200] + "..." if len(response.text) > 200 else response.text
                        print(f"   POST Content: {content}")
                        
            except Exception as e:
                print(f"   POST failed: {e}")
                
        except Exception as e:
            print(f"   ❌ Both requests failed: {e}")
            
    print("\n" + "=" * 60)
    print("🎯 Look for endpoints that return 200 status code")
    print("💡 Gradio apps often use /gradio_api/call/predict")
    print("💡 FastAPI apps often use /docs for API documentation")

if __name__ == "__main__":
    discover_endpoints()