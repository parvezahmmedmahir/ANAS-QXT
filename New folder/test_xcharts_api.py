"""
Test xcharts.live API for Quotex data
"""
import requests
import json

# Test the API
url = "https://xcharts.live/api/market/quotex/?symbol=EURUSD-OTCq&interval=1m&limit=10"
print(f"Testing: {url}\n")

response = requests.get(url)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"Data Type: {type(data)}")
    print(f"Number of candles: {len(data) if isinstance(data, list) else 'N/A'}")
    print(f"\nFirst candle:")
    print(json.dumps(data[0] if isinstance(data, list) and len(data) > 0 else data, indent=2))
else:
    print(f"Error: {response.text[:200]}")
