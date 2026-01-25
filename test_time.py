import requests
import datetime

# Test signal generation
response = requests.post('http://localhost:5000/predict', 
                        json={'broker':'QUOTEX','market':'EUR/USD','timeframe':'M1'})
result = response.json()

# Calculate current BD time
bd_now = datetime.datetime.utcnow() + datetime.timedelta(hours=6)
current_time = bd_now.strftime("%H:%M")
next_minute = (bd_now + datetime.timedelta(minutes=1)).strftime("%H:%M")

print("=" * 50)
print("   TIME VERIFICATION TEST")
print("=" * 50)
print(f"Current BD Time: {current_time}")
print(f"Expected Entry:  {next_minute}")
print(f"Generated Entry: {result['entry_time']}")
print()
print("=" * 50)
print("   SIGNAL DETAILS")
print("=" * 50)
print(f"Direction:  {result['direction']}")
print(f"Confidence: {result['confidence']}%")
print(f"Market:     {result['market']}")
print(f"Mode:       {result['mode']}")
print("=" * 50)

# Verify time is correct
if result['entry_time'] == next_minute:
    print("✅ TIME IS CORRECT!")
else:
    print(f"⚠️  Time mismatch: Expected {next_minute}, Got {result['entry_time']}")
