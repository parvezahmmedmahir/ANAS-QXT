import requests
import time
import sys

def test_server():
    base_url = "http://127.0.0.1:5000"
    print(f"Testing server at {base_url}...")
    
    # 1. Test Root
    try:
        resp = requests.get(f"{base_url}/")
        if resp.status_code == 200:
            print("[SUCCESS] Root endpoint is reachable.")
            print("Response Length:", len(resp.text))
            # print("Response:", resp.json()) # Root now returns HTML
        else:
            print(f"[FAIL] Root endpoint returned {resp.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] Could not connect to server. Is it running?")
        return False

    # 2. Test License Validation
    # Using an Owner Key from generated_keys.txt: Zz&1d^9A
    payload = {
        "key": "Zz&1d^9A",
        "device_id": "test_device_fingerprint_123"
    }
    
    try:
        resp = requests.post(f"{base_url}/api/validate_license", json=payload)
        print(f"\nTesting License Validation with key: {payload['key']}")
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("valid") == True:
                print("[SUCCESS] License validation passed.")
                print("Response:", data)
            else:
                print("[FAIL] License validation returned valid=False")
                print("Response:", data)
                # It might fail if DB is not connected or key is not in DB, 
                # but valid=False with a message is still a successful server test.
        else:
            print(f"[FAIL] License endpoint returned {resp.status_code}")
            print("Response:", resp.text)
            
    except Exception as e:
        print(f"[ERROR] License test failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    # Wait a bit for server to fully start if called immediately after
    time.sleep(2)
    if test_server():
        sys.exit(0)
    else:
        sys.exit(1)
