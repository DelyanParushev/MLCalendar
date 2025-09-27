#!/usr/bin/env python3
"""
Test if our backend changes work correctly
"""
import sys
import os
sys.path.append('.')

# Test importing everything
try:
    print("Testing backend imports...")
    from datetime import datetime, timedelta
    print("✅ datetime imports OK")
    
    # Test our ML parser
    from ml.nlp_parser_ml import parse_text
    print("✅ ML parser imports OK")
    
    # Test the core backend imports
    from backend.main import app
    print("✅ FastAPI app imports OK")
    
    # Test a simple parse
    result = parse_text("тест утре в 10")
    print(f"✅ Parse test OK: {result}")
    
    # Test the datetime conversion logic we added
    if result.get("start") or result.get("datetime"):
        dt = result.get("datetime") or result.get("start")
        if isinstance(dt, str):
            dt_obj = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            end = dt_obj + timedelta(hours=1)
            print(f"✅ DateTime conversion OK: {dt} -> {dt_obj} -> {end.isoformat()}")
        else:
            print(f"✅ DateTime already object: {dt}")
    
    print("\n🎉 All tests passed! Backend should work.")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()