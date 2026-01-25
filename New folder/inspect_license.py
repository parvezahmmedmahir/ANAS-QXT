"""
INSPECT LICENSE FUNCTION
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import validate_license
import inspect

print(f"Function: {validate_license}")
try:
    print(f"Arguments: {inspect.signature(validate_license)}")
except:
    print("Could not get signature")

# If it's a Flask route, it might wrap the actual function
print(f"Doc: {validate_license.__doc__}")
