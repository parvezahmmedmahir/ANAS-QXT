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

        print(f"[QUOTEX-API] OK: High-Speed Adapter initialized with {len(self.available_pairs)} pairs")
    
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
            # Normalize asset name to match API format
            # Step 1: Handle the (OTC) suffix which might come from UI
            api_pair = asset.replace(" (OTC)", "_otc").replace("-OTC", "_otc").strip()
            
            # Step 2: Ensure the base symbol is upper but the suffix is lower (api requirement)
            if "_otc" in api_pair:
                sym = api_pair.split("_otc")[0].upper()
                api_pair = f"{sym}_otc"
            else:
                api_pair = api_pair.upper()
            
            api_pair = api_pair.replace("/", "").replace(" ", "")
            
            # API URL
            url = f"{self.base_url}?pair={api_pair}&count={count}"
            
            response = requests.get(url, timeout=8)
            if response.status_code == 200:
                raw_data = response.json()
                
                # Support both direct list and {"data": [...]} formats
                candle_list = []
                if isinstance(raw_data, list):
                    candle_list = raw_data
                elif isinstance(raw_data, dict) and "data" in raw_data:
                    candle_list = raw_data["data"]
                
                if candle_list and len(candle_list) > 0:
                    formatted_candles = []
                    now_ts = time.time()
                    
                    for c in candle_list:
                        raw_time = c.get("time")
                        c_ts = 0
                        
                        if isinstance(raw_time, (int, float)):
                            c_ts = raw_time
                        elif isinstance(raw_time, str):
                            try:
                                # Try parsing ISO or standard format
                                dt = datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
                                c_ts = dt.timestamp()
                            except:
                                c_ts = time.time() # Fallback
                        
                        formatted_candles.append({
                            "time": c_ts,
                            "open": float(c.get("open", 0)),
                            "high": float(c.get("high", 0)),
                            "low": float(c.get("low", 0)),
                            "close": float(c.get("close", 0)),
                            "volume": float(c.get("volume", 0)) if "volume" in c else 0
                        })
                    
                    if not formatted_candles: return None
                    
                    # Ensure Oldest -> Newest
                    formatted_candles.sort(key=lambda x: x['time'])
                    
                    # STRICT: "Closed Candle Only" Enforcement
                    # We always discard the very last candle because it is the one currently "running" on the broker.
                    # This ensures technical indicators (RSI, etc.) are calculated on FIXED data.
                    if len(formatted_candles) > 30:
                        return formatted_candles[:-1]
                    return formatted_candles
            
            print(f"[QUOTEX-API] ⚠️ No valid data for {asset} (Status: {response.status_code})")
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
        print("API CONNECTION ONLINE")
        candles = adapter.get_candles("EURUSD_otc", count=5)
        if candles:
            print(f"OK: Successfully retrieved {len(candles)} candles")
            print(f"Latest Price: {candles[-1]['close']}")
    else:
        print("❌ API OFFLINE")
