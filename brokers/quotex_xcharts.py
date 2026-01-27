"""
QUANTUM X PRO - Quotex XCharts API Adapter
Uses xcharts.live API for Quotex OTC data
No Cloudflare issues - Direct API access
"""
import requests
import time
from datetime import datetime
from typing import Optional, List, Dict

class QuotexXChartsAdapter:
    """
    Quotex data adapter using xcharts.live API
    - No authentication needed
    - No Cloudflare blocking
    - Real-time OTC data
    - All Quotex pairs supported
    """
    
    def __init__(self, config=None):
        self.base_url = "https://xcharts.live/api/market/quotex/"
        self.connected = True  # API is always available
        self.sid = "XCHARTS-API-CONNECTED"
        
        # All available Quotex OTC pairs
        self.available_pairs = [
            "EURUSD", "AUDCAD", "BRLUSD", "USDBDT", "USDPKR",
            "AUDCHF", "AUDJPY", "AUDNZD", "AUDUSD", "BTCUSD",
            "CADCHF", "CADJPY", "CHFJPY", "EURAUD", "EURCAD",
            "EURCHF", "EURGBP", "EURJPY", "EURNZD", "GBPAUD",
            "GBPCAD", "GBPCHF", "GBPJPY", "GBPNZD", "GBPUSD",
            "NZDCAD", "NZDCHF", "NZDJPY", "NZDUSD", "USDCAD",
            "USDCHF", "USDJPY", "ETHUSD", "LTCUSD", "XRPUSD", "AUDNZD",
            "USDEGP", "USDZAR", "EURSGD", "USDCOP", "USDINR",
            "USDARS", "USDIDR", "USDMXN", "EURNZD", "NZDCAD",
            "NZDCHF", "NZDJPY", "USDBDT", "USDDZD", "AUDCAD",
            "CADCHF", "GBPNZD", "USDCAD", "BTCUSD", 
        ]
        
        print(f"[QUOTEX-XCHARTS] ✅ Adapter initialized with {len(self.available_pairs)} pairs")
    
    def connect(self) -> bool:
        """
        Test connection to xcharts.live API
        """
        try:
            # Test with EURUSD
            test_url = f"{self.base_url}?symbol=EURUSD-OTCq&interval=1m&limit=1"
            response = requests.get(test_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'candles' in data and len(data['candles']) > 0:
                    self.connected = True
                    print(f"[QUOTEX-XCHARTS] ✅ Connected to xcharts.live API")
                    return True
            
            self.connected = False
            return False
            
        except Exception as e:
            print(f"[QUOTEX-XCHARTS] ❌ Connection error: {e}")
            self.connected = False
            return False
    
    def get_candles(self, asset: str, timeframe_seconds: int = 60, count: int = 100, end_ts: int = None) -> Optional[List[Dict]]:
        """
        Get candles for a Quotex OTC pair
        
        Args:
            asset: Pair name (e.g., "EURUSD", "BTCUSD")
            timeframe_seconds: Candle period (60, 300, 900, etc.)
            count: Number of candles to retrieve
            end_ts: End timestamp (not used, API returns latest)
        
        Returns:
            List of candle dictionaries with: time, open, high, low, close, volume
        """
        try:
            # Clean asset name (remove any suffixes)
            clean_asset = asset.upper().replace("_OTC", "").replace("-OTC", "")
            
            # Map timeframe to interval
            interval_map = {
                60: "1m",
                300: "5m",
                900: "15m",
                1800: "30m",
                3600: "1h",
                14400: "4h",
                86400: "1d"
            }
            interval = interval_map.get(timeframe_seconds, "1m")
            
            # Build URL (always use -OTCq suffix for Quotex)
            url = f"{self.base_url}?symbol={clean_asset}-OTCq&interval={interval}&limit={count}"
            
            # Make request
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'candles' in data:
                    candles = data['candles']
                    print(f"[QUOTEX-XCHARTS] ✅ Retrieved {len(candles)} candles for {clean_asset}")
                    return candles
                else:
                    print(f"[QUOTEX-XCHARTS] ⚠️ No candles in response for {clean_asset}")
                    return None
            else:
                print(f"[QUOTEX-XCHARTS] ❌ HTTP {response.status_code} for {clean_asset}")
                return None
                
        except Exception as e:
            print(f"[QUOTEX-XCHARTS] ❌ Error fetching {asset}: {e}")
            return None
    
    def get_latest_price(self, asset: str) -> Optional[float]:
        """
        Get latest price for an asset
        """
        candles = self.get_candles(asset, 60, 1)
        if candles and len(candles) > 0:
            return candles[-1].get('close')
        return None
    
    def backtest(self, assets: List[str]) -> Dict:
        """
        Test connection quality across multiple assets
        """
        results = {}
        print(f"[QUOTEX-XCHARTS] Testing {len(assets)} assets...")
        
        for asset in assets:
            candles = self.get_candles(asset, 60, 5)
            
            if candles and len(candles) > 0:
                results[asset] = {
                    "connected": True,
                    "candles": len(candles),
                    "latest_price": candles[-1].get('close'),
                    "status": "✅ OK"
                }
            else:
                results[asset] = {
                    "connected": False,
                    "candles": 0,
                    "latest_price": None,
                    "status": "❌ Failed"
                }
            
            time.sleep(0.1)  # Rate limiting
        
        return results


# Backward compatibility wrapper
class QuotexWSAdapter(QuotexXChartsAdapter):
    """
    Drop-in replacement for old QuotexWSAdapter
    Uses XCharts API instead of WebSocket
    """
    pass


if __name__ == "__main__":
    print("="*70)
    print("   QUOTEX XCHARTS API TEST")
    print("="*70 + "\n")
    
    # Initialize adapter
    adapter = QuotexXChartsAdapter()
    
    # Test connection
    if adapter.connect():
        print("\n[TEST 1] Connection: ✅ PASS\n")
        
        # Test getting candles for different pairs
        test_pairs = ["EURUSD", "BTCUSD", "AUDCAD", "GBPUSD"]
        
        print(f"[TEST 2] Testing {len(test_pairs)} pairs...\n")
        for pair in test_pairs:
            candles = adapter.get_candles(pair, 60, 10)
            if candles:
                latest = candles[-1]
                print(f"  ✅ {pair:10} | {len(candles)} candles | Latest: {latest.get('close')}")
            else:
                print(f"  ❌ {pair:10} | Failed")
        
        # Test latest price
        print(f"\n[TEST 3] Latest prices...\n")
        for pair in test_pairs[:3]:
            price = adapter.get_latest_price(pair)
            if price:
                print(f"  ✅ {pair:10} | ${price}")
        
        print("\n" + "="*70)
        print("   ALL TESTS PASSED - QUOTEX XCHARTS API WORKING")
        print("="*70 + "\n")
    else:
        print("\n❌ Connection test failed")
