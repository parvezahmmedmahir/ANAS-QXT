from brokers.quotex_ws import QuotexWSAdapter
import os
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print(" QUANTUM X PRO - QUOTEX WS HANDSHAKE TEST ")
print("="*60)

adapter = QuotexWSAdapter()
success = adapter.connect()

if success:
    print(f"\n✅ HANDSHAKE SUCCESSFUL!")
    print(f"   SID: {adapter.sid}")
    print(f"   Status: VERIFIED")
else:
    print(f"\n❌ HANDSHAKE FAILED!")
    print(f"   Check if curl.exe is available and if the domain is accessible.")

print("="*60)
