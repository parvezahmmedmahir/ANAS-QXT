"""
TEST LICENSE LOGIC V2
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import validate_license
    print("✅ Function found: validate_license")
    
    # Test
    print("Testing with dummy key...")
    # Assume signature is (key, hwid)
    try:
        result = validate_license("TEST-KEY", "HWID-TEST")
        print(f"Result: {result}")
        if isinstance(result, dict) and 'valid' in result:
             print("✅ Logic Verified")
        else:
             print("⚠️ Unexpected format")
    except TypeError:
        # Maybe it takes only key? or request object?
        print("❌ TypeError calling function - signature mismatch?")

except Exception as e:
    print(f"❌ Error: {e}")
