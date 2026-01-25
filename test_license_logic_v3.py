"""
TEST LICENSE LOGIC V3 (FLASK CONTEXT)
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, validate_license

print("Testing with Flask Request Context...")

with app.test_request_context(json={"license_key": "TEST-KEY", "hwid": "HWID-TEST"}):
    try:
        # validate_license() is likely the view function
        response = validate_license()
        print(f"Response Type: {type(response)}")
        
        # If it returns a Response object (flask.jsonify), we need get_json()
        if hasattr(response, 'get_json'):
             print(f"JSON: {response.get_json()}")
        else:
             print(f"Data: {response}")
             
        print("✅ License Logic Executed Successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
