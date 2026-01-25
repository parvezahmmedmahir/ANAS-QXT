"""
QUANTUM X PRO - DIRECT API TEST
Tests the license validation endpoint directly without the browser
"""
import requests
import json
import hashlib

def test_api():
    print("\n" + "="*70)
    print("   DIRECT API CONNECTION TEST")
    print("="*70 + "\n")
    
    # Test both local and cloud
    endpoints = [
        ("LOCAL SERVER", "http://127.0.0.1:5000"),
        ("CLOUD SERVER", "https://quantum-x-pro-backend.onrender.com")
    ]
    
    # Generate a test device ID (similar to frontend)
    test_device_id = hashlib.md5(b"test-device-12345").hexdigest()
    
    # Test keys
    test_keys = [
        "TSCC1",
        "KTXKTM77",
        "QXMASTER",
        "QX-MASTER-2026"
    ]
    
    for server_name, base_url in endpoints:
        print(f"\n[{server_name}] Testing: {base_url}")
        print("-" * 70)
        
        # First, test if server is reachable
        try:
            test_response = requests.get(f"{base_url}/test", timeout=5)
            if test_response.status_code == 200:
                data = test_response.json()
                print(f"✅ Server is ONLINE")
                print(f"   Database: {data.get('db_mode', 'unknown')}")
            else:
                print(f"⚠️  Server responded with code: {test_response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Server is OFFLINE or unreachable")
            continue
        except Exception as e:
            print(f"❌ Connection error: {e}")
            continue
        
        # Now test license validation
        print(f"\n   Testing license validation:")
        for key in test_keys:
            try:
                payload = {
                    "key": key,
                    "device_id": test_device_id
                }
                
                response = requests.post(
                    f"{base_url}/api/validate_license",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                result = response.json()
                
                if result.get("valid"):
                    print(f"   ✅ {key:20} - VALID ({result.get('category')})")
                else:
                    print(f"   ❌ {key:20} - {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ {key:20} - Request failed: {e}")
    
    print("\n" + "="*70)
    print("   TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_api()
