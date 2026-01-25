
from pyquotex.stable_api import Quotex
import inspect

print("Checking Quotex class methods:")
# List methods of the Quotex class to see if 'get_candles' exists
print([m for m in dir(Quotex) if "candle" in m or "get" in m])
