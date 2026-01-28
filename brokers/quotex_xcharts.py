"""
QUANTUM X PRO - Quotex MrBeast API Adapter
Uses mrbeaxt.site API for Official Quotex broker data.
High-speed, direct access, no Cloudflare blocking.
"""
import requests
import time
import json
import os
from datetime import datetime
from typing import Optional, List, Dict

class QuotexMrBeastAdapter:
    """
    Official Quotex data adapter using mrbeaxt.site bridge.
    - High-precision broker data
    - Direct API access
    - 100% OTC & Real Market support
    """
    
    def __init__(self, config=None):
        self.base_url = "https://mrbeaxt.site/Qx/Qx.php"
        self.connected = True
        self.sid = "MRBEAST-PRO-API"
        
        # Load available pairs from markets.json if possible, otherwise use fallback
        try:
            markets_path = os.path.join(os.getcwd(), 'markets.json')
            if os.path.exists(markets_path):
                with open(markets_path, 'r') as f:
                    market_data = json.load(f)
                    self.available_pairs = [m['pair'] for m in market_data.get('markets', [])]
            else:
                self.available_pairs = [
                    "AUDCAD_otc", "AUDCHF_otc", "AUDJPY_otc", "AUDNZD_otc", "AUDUSD_otc",
                    "AXP_otc", "BCHUSD_otc", "BRLUSD_otc", "BTCUSD_otc", "CADCHF_otc",
                    "CADJPY_otc", "CHFJPY_otc", "EURAUD_otc", "EURCAD_otc", "EURCHF_otc",
                    "EURGBP_otc", "EURJPY_otc", "EURNZD_otc", "EURSGD_otc", "EURUSD",
                    "EURUSD_otc", "FAANG_otc", "GBPAUD_otc", "GBPCAD_otc", "GBPCHF_otc",
                    "GBPJPY_otc", "GBPNZD_otc", "GBPUSD_otc", "INTC_otc", "JNJ_otc",
                    "MCD_otc", "MSFT_otc", "NZDCAD_otc", "NZDCHF_otc", "NZDJPY_otc",
                    "NZDUSD_otc", "PFE_otc", "USDCAD_otc", "USDBDT_otc", "USDCHF_otc",
                    "USDCOP_otc", "USDDZD_otc", "USDEGP_otc", "USDIDR_otc", "USDINR_otc",
                    "USDJPY_otc", "USDMXN_otc", "USDNGN_otc", "USDPKR_otc", "USDTRY_otc",
                    "USDZAR_otc", "XAUUSD_otc"
                ]
        except Exception as e:
            print(f"[QUOTEX-API] Warning loading markets.json: {e}")
            self.available_pairs = []

        print(f"[QUOTEX-API] ✅ High-Speed Adapter initialized with {len(self.available_pairs)} pairs")
    
    def connect(self) -> bool:
        """
        Test connection to the new API
        """
        try:
            test_url = f"{self.base_url}?pair=EURUSD_otc&count=1"
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                self.connected = True
                return True
            return False
        except:
            self.connected = False
            return False
    
    def get_candles(self, asset: str, timeframe_seconds: int = 60, count: int = 100, end_ts: int = None) -> Optional[List[Dict]]:
        """
        Fetches official broker candles from mrbeaxt.site
        """
        try:
            # Normalize asset name to match API format (e.g., EURUSD_otc)
            api_pair = asset.upper().replace(" (OTC)", "_otc").replace("-OTC", "_otc").replace("/", "").replace(" ", "").strip()
            
            # API URL
            url = f"{self.base_url}?pair={api_pair}&count={count}"
            
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Sort and format candles if necessary
                    # Assuming API returns: [{"open":..., "close":..., "high":..., "low":..., "time":...}]
                    formatted_candles = []
                    for c in data:
                        formatted_candles.append({
                            "time": c.get("time") or time.time(),
                            "open": float(c.get("open", 0)),
                            "high": float(c.get("high", 0)),
                            "low": float(c.get("low", 0)),
                            "close": float(c.get("close", 0)),
                            "volume": float(c.get("volume", 0)) if "volume" in c else 0
                        })
                    return formatted_candles
            
            print(f"[QUOTEX-API] ⚠️ No data for {asset} (Status: {response.status_code})")
            return None
                
        except Exception as e:
            # print(f"[QUOTEX-API] ❌ Fetch Error: {e}")
            return None
    
    def get_latest_price(self, asset: str) -> Optional[float]:
        candles = self.get_candles(asset, 60, 1)
        if candles and len(candles) > 0:
            return candles[-1].get('close')
        return None

# Backward compatibility wrappers
class QuotexXChartsAdapter(QuotexMrBeastAdapter): pass
class QuotexWSAdapter(QuotexMrBeastAdapter): pass

if __name__ == "__main__":
    adapter = QuotexMrBeastAdapter()
    print(f"Testing connectivity...")
    if adapter.connect():
        print("✅ API CONNECTION ONLINE")
        candles = adapter.get_candles("EURUSD_otc", count=5)
        if candles:
            print(f"✅ Successfully retrieved {len(candles)} candles")
            print(f"Latest Price: {candles[-1]['close']}")
    else:
        print("❌ API OFFLINE")
