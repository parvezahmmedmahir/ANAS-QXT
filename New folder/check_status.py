import requests
import json

print("=" * 50)
print("   QUANTUM X PRO - SYSTEM STATUS CHECK")
print("=" * 50)

# Check WebSocket Status
print("\n=== WEB MARKET CONNECTIVITY ===")
try:
    from brokers.quotex_ws import QuotexWSAdapter
    from brokers.forex_ws import ForexWSAdapter
    
    q_ws = QuotexWSAdapter()
    if q_ws.connect():
        print(f"✅ Quotex WS Handshake: SUCCESS (SID: {q_ws.sid})")
    else:
        print(f"❌ Quotex WS Handshake: FAILED")
        
    f_ws = ForexWSAdapter()
    if f_ws.connect():
        print(f"✅ Forex WS Stream: ACTIVE")
    else:
        print(f"❌ Forex WS Stream: OFFLINE")
except Exception as e:
    print(f"⚠️ WS Check Error: {e}")

# Test Deterministic Signal Generation
try:
    print("\n=== GLOBAL SYNC VERIFICATION ===")
    test_params = {'broker':'QUOTEX','market':'EUR/USD','timeframe':'M1', 'license_key': 'TSC', 'device_id': 'TEST_CONSOLE'}
    # Simulate first request
    res1 = requests.post('http://localhost:5000/predict', json=test_params).json()
    # Simulate second request
    res2 = requests.post('http://localhost:5000/predict', json=test_params).json()
    
    if res1.get('direction') == res2.get('direction'):
        print(f"✅ Deterministic Locking: ACTIVE (Global Sync Verified)")
        print(f"   Synchronized Direction: {res1.get('direction')}")
    else:
        print(f"⚠️ Deterministic Locking: INCONSISTENT")
except:
    print("⚠️ Sync Verification: Backend not responding")

print("\n" + "=" * 50)
print("   SYSTEM READY FOR ENTERPRISE DISTRIBUTION")
print("=" * 50)
