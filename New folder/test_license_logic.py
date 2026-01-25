"""
TEST LICENSE LOGIC
"""
import sys
import os
import json

# Add current dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import validate_license_key
    print("✅ Function found: validate_license_key")
    
    # Test
    print("Testing with dummy key...")
    result = validate_license_key("TEST-KEY", "HWID-TEST")
    print(f"Result Type: {type(result)}")
    print(f"Result Content: {result}")
    
    if isinstance(result, dict) and 'valid' in result:
        print("✅ License logic returning correct format")
    else:
        print("❌ License logic returning unexpected format")

except ImportError:
    print("❌ Could not import validate_license_key from app")
    # Try to inspect what is in app
    import app
    print("App dir:", dir(app))
except Exception as e:
    print(f"❌ Error: {e}")
