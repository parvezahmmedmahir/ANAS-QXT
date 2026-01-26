import requests
import json

BASE_URL = "http://localhost:5000" # Assume local for now, or use the onrender one

def test_bypass():
    print("Testing License Bypass...")
    
    # 1. Try to sync device with a random ID
    print("\n[1] Testing /api/check_device_sync with random ID...")
    resp = requests.post(f"{BASE_URL}/api/check_device_sync", json={"device_id": "RANDOM-123456"})
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.json()}")
    
    # 2. Try to validate with an empty key
    print("\n[2] Testing /api/validate_license with empty key...")
    resp = requests.post(f"{BASE_URL}/api/validate_license", json={"key": "", "device_id": "RANDOM-123456"})
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.json()}")

    # 3. Try to predict with no key
    print("\n[3] Testing /predict with no key...")
    resp = requests.post(f"{BASE_URL}/predict", json={"license_key": "", "device_id": "RANDOM-123456", "market": "EUR/USD"})
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.json()}")

if __name__ == "__main__":
    test_bypass()
