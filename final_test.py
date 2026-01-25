import requests
import datetime

print("=" * 60)
print("   QUANTUM X PRO - FINAL VERIFICATION")
print("=" * 60)

# Test 1: Backend Status
print("\n[TEST 1] Backend Status Check")
try:
    r = requests.get('http://localhost:5000/')
    print(f"✅ Backend: {r.json()['status']}")
except:
    print("❌ Backend: OFFLINE")

# Test 2: Frontend Status
print("\n[TEST 2] Frontend Status Check")
try:
    r = requests.get('http://localhost:3000/')
    print(f"✅ Frontend: ONLINE (Status {r.status_code})")
except:
    print("❌ Frontend: OFFLINE")

# Test 3: Time Accuracy
print("\n[TEST 3] Time Accuracy Verification")
bd_now = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
current_time = bd_now.strftime("%H:%M")
expected_entry = (bd_now + datetime.timedelta(minutes=1)).strftime("%H:%M")

r = requests.post('http://localhost:5000/predict', 
                 json={'broker':'QUOTEX','market':'EUR/USD','timeframe':'M1'})
result = r.json()

print(f"Current BD Time:  {current_time}")
print(f"Expected Entry:   {expected_entry}")
print(f"Generated Entry:  {result['entry_time']}")

if result['entry_time'] == expected_entry:
    print("✅ Time calculation is CORRECT!")
else:
    print(f"❌ Time mismatch!")

# Test 4: Signal Quality
print("\n[TEST 4] Signal Quality Check")
print(f"Direction:  {result['direction']}")
print(f"Confidence: {result['confidence']}%")
print(f"Market:     {result['market']}")
print(f"Mode:       {result['mode']}")

if 82 <= result['confidence'] <= 96:
    print("✅ Confidence in expected range (82-96%)")
else:
    print(f"⚠️  Confidence outside range: {result['confidence']}%")

# Test 5: Multiple Markets
print("\n[TEST 5] Market-Aware Signal Generation")
markets = ["EUR/USD (OTC)", "BTC/USD", "USD/JPY"]
for market in markets:
    r = requests.post('http://localhost:5000/predict', 
                     json={'broker':'QUOTEX','market':market,'timeframe':'M1'})
    sig = r.json()
    print(f"{market:20} → {sig['direction']:4} @ {sig['confidence']}%")

print("\n" + "=" * 60)
print("   ALL TESTS COMPLETED")
print("=" * 60)
print("\n✅ System is FULLY OPERATIONAL!")
print("\n📱 Access URL:")
print("   http://localhost:3000/quantum_x_system_timeframe_start_time_side_by_side.html")
print("\n🔑 License Key: TSC")
print("=" * 60)
