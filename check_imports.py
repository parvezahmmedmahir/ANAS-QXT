
from iqoptionapi.api import IQOptionAPI
import inspect

print("Inspecting IQOptionAPI methods:")
methods = [m for m in dir(IQOptionAPI) if not m.startswith("_")]
print(methods[:20]) # Print first 20 methods
