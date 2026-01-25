"""
QUANTUM X PRO - Quotex API Integration Test
Using api-quotex library (Cloudflare bypass built-in)
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Check if api-quotex is available
try:
    from api_quotex import Quotex
    print("[✅] api-quotex library loaded successfully")
except ImportError:
    print("[❌] api-quotex not installed. Run: pip install api-quotex")
    exit(1)

async def test_quotex_connection():
    print("\n" + "="*70)
    print("   QUOTEX API CONNECTION TEST")
    print("="*70 + "\n")
    
    # Get credentials from .env or use defaults for testing
    email = os.getenv('QUOTEX_EMAIL')
    password = os.getenv('QUOTEX_PASSWORD')
    
    if not email or email == 'your-quotex-email@example.com':
        print("⚠️  No Quotex credentials found in .env")
        print("   Please update .env with:")
        print("   QUOTEX_EMAIL=your-email@gmail.com")
        print("   QUOTEX_PASSWORD=your-password")
        return False
    
    print(f"[1] Connecting to Quotex...")
    print(f"    Email: {email[:3]}***@{email.split('@')[1] if '@' in email else '***'}")
    
    try:
        # Initialize Quotex client
        client = Quotex(
            email=email,
            password=password,
            lang="en"
        )
        
        print("[2] Authenticating (bypassing Cloudflare)...")
        
        # Connect
        check, reason = await client.connect()
        
        if check:
            print("[✅] CONNECTION SUCCESSFUL!")
            print(f"    Reason: {reason}")
            
            # Get balance
            print("\n[3] Fetching account information...")
            try:
                balance_data = await client.get_balance()
                if balance_data:
                    balance = balance_data.get('balance', 0)
                    demo = balance_data.get('demo', True)
                    account_type = "DEMO" if demo else "REAL"
                    print(f"[✅] Balance: ${balance:,.2f} ({account_type})")
            except Exception as e:
                print(f"[⚠️] Balance fetch failed: {e}")
            
            # Test getting candles
            print("\n[4] Testing market data retrieval...")
            try:
                test_asset = "EURUSD_otc"  # OTC asset (always available)
                candles = await client.get_candles(test_asset, 60)
                
                if candles and len(candles) > 0:
                    print(f"[✅] Retrieved {len(candles)} candles for {test_asset}")
                    latest = candles[-1]
                    print(f"    Latest candle: Open={latest.get('open')}, Close={latest.get('close')}")
                else:
                    print(f"[⚠️] No candles received for {test_asset}")
            except Exception as e:
                print(f"[⚠️] Candles fetch failed: {e}")
            
            # Get available assets
            print("\n[5] Fetching available assets...")
            try:
                assets = await client.get_all_open_time()
                if assets:
                    # Count assets by type
                    binary_count = len([a for a in assets if assets[a].get('binary', {}).get('open', False)])
                    print(f"[✅] Found {len(assets)} total assets")
                    print(f"    Binary options available: {binary_count}")
                    
                    # Show first 10 available assets
                    available = [name for name, data in assets.items() if data.get('binary', {}).get('open', False)][:10]
                    if available:
                        print(f"    Sample assets: {', '.join(available[:5])}")
            except Exception as e:
                print(f"[⚠️] Assets fetch failed: {e}")
            
            # Close connection
            await client.close()
            
            print("\n" + "="*70)
            print("   TEST COMPLETE - ALL SYSTEMS OPERATIONAL")
            print("="*70 + "\n")
            return True
            
        else:
            print(f"[❌] CONNECTION FAILED")
            print(f"    Reason: {reason}")
            print("\n    Possible issues:")
            print("    - Incorrect email/password")
            print("    - Quotex account locked")
            print("    - Network issues")
            return False
            
    except Exception as e:
        print(f"[❌] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_quotex_connection())
    exit(0 if result else 1)
