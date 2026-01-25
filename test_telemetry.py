"""
QUANTUM X PRO - TELEMETRY SYSTEM TEST
Tests the complete data collection flow
"""
import requests
import json

def test_telemetry():
    print("\n" + "="*70)
    print("   TELEMETRY SYSTEM TEST")
    print("="*70 + "\n")
    
    # Test data (simulating what JavaScript sends)
    test_payload = {
        "license_key": "!4QD^xc5",
        "device_id": "QX-HW-TEST-12345678",
        "geo": {
            "ip": "103.127.1.130",
            "country": "Bangladesh",
            "region": "Dhaka",
            "city": "Dhaka",
            "latitude": 23.8103,
            "longitude": 90.4125,
            "isp": "Grameenphone",
            "organization": "GP",
            "timezone": "Asia/Dhaka",
            "postal": "1000"
        },
        "browser": {
            "browserName": "Chrome",
            "browserVersion": "120.0.0.0",
            "osName": "Windows 10",
            "osVersion": "",
            "isMobile": False,
            "isTablet": False,
            "screenWidth": 1920,
            "screenHeight": 1080,
            "colorDepth": 24,
            "pixelRatio": 1.0,
            "touchSupport": False
        },
        "network": {
            "connectionType": "wifi",
            "effectiveType": "4g",
            "downlink": 10.0,
            "rtt": 50,
            "saveData": False
        },
        "fingerprint": {
            "canvas": "abc123def456",
            "webgl": "ANGLE (Intel HD Graphics 620)",
            "screen": "1920x1080",
            "cores": 4,
            "memory": 8,
            "platform": "Win32",
            "language": "en-US",
            "timezone": "Asia/Dhaka"
        }
    }
    
    # Test both local and cloud
    endpoints = [
        ("LOCAL", "http://127.0.0.1:5000"),
        ("CLOUD", "https://quantum-x-pro-backend.onrender.com")
    ]
    
    for name, base_url in endpoints:
        print(f"\n[{name}] Testing: {base_url}/api/telemetry/collect")
        print("-" * 70)
        
        try:
            response = requests.post(
                f"{base_url}/api/telemetry/collect",
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS")
                print(f"   Status: {result.get('status')}")
                print(f"   Message: {result.get('message')}")
                print(f"   Location: {result.get('location')}")
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Server OFFLINE or unreachable")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*70)
    print("   TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_telemetry()
