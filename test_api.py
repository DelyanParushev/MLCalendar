#!/usr/bin/env python3
"""
Test the backend parse endpoint with string datetime conversion
"""
import sys
import os
sys.path.append('.')
os.chdir('d:\\Delyan\\UNI\\calendar-ai - Upgrade')

# Set up the environment for testing
import os
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
import json

def test_parse_endpoint_mock():
    """Test the parse endpoint with mock data"""
    
    # Import the parse function directly
    from ml.nlp_parser_ml import parse_text
    
    test_cases = [
        "гейминг утре от 19",
        "Йога клас утре сутринта", 
        "Вечеря с Гери в Неделя от 18"
    ]
    
    print("🧪 Testing ML Parser with HF Space API")
    print("=" * 60)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: '{text}'")
        
        try:
            # Get the raw result from ML parser
            result = parse_text(text)
            print(f"   📊 Raw result: {json.dumps(result, indent=2, ensure_ascii=False, default=str)}")
            
            # Test the datetime conversion logic
            dt = result.get("datetime") or result.get("start")
            if dt:
                if isinstance(dt, str):
                    try:
                        dt_obj = datetime.fromisoformat(dt.replace('Z', '+00:00'))
                        print(f"   ✅ DateTime conversion successful: {dt} -> {dt_obj}")
                    except ValueError as e:
                        print(f"   ❌ DateTime conversion failed: {e}")
                else:
                    print(f"   📅 DateTime already object: {dt} (type: {type(dt)})")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_parse_endpoint_mock()
    print("\n✅ Backend parse endpoint testing complete!")
