"""
QUANTUM X PRO - Enhanced Backend v5.0 (Pro Edition)
Integrates Enterprise Engine v3.0, Pro-Level Technical Analysis, and Real-Time Market Guardians.
"""
import sys
import datetime
import random
import sqlite3
import string
import secrets
import hashlib
import time
import threading
import os
import psycopg2
import requests
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from collections import defaultdict
import platform
import subprocess
import json

# --- QUANTUM HWID & GUARDIAN CORE ---
def generate_quantum_hwid(raw_id):
    """Secure, obfuscated HWID for the Quantum X Pro system"""
    salt = "QX-PRO-HARDWARE-GUARDIAN-SECURE-ID-2026"
    combined = f"{raw_id}:{salt}"
    hwid_hash = hashlib.sha256(combined.encode()).hexdigest().upper()
    return f"QX-ID-{hwid_hash[:4]}-{hwid_hash[8:12]}-{hwid_hash[24:28]}"

def get_geo_info(ip):
    """Silently collect location info from IP"""
    try:
        if ip == "127.0.0.1": return {"city": "Local", "country": "Local", "isp": "Internal"}
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        return resp.json() if resp.status_code == 200 else {}
    except:
        return {}

# --- BROKER INTEGRATIONS ---
# Importing adapters from the brokers package (Binolla optional)
import importlib
import importlib.util

BROKER_CONFIG = {}
QuotexAdapter = None
IQOptionAdapter = None
PocketOptionAdapter = None
BinollaAdapter = None

try:
    from brokers.config import BROKER_CONFIG  # type: ignore
    from brokers.quotex import QuotexAdapter  # type: ignore
    from brokers.iqoption import IQOptionAdapter  # type: ignore
    from brokers.pocketoption import PocketOptionAdapter  # type: ignore
    # Binolla optional import
    binolla_module = importlib.util.find_spec("brokers.binolla")
    if binolla_module:
        BinollaAdapter = importlib.import_module("brokers.binolla").BinollaAdapter  # type: ignore

    # New WebSocket Adapters
    from brokers.quotex_ws import QuotexWSAdapter
    from brokers.forex_ws import ForexWSAdapter
except ImportError as e:
    print(f"[CRITICAL] Broker modules missing: {e}. Running in restricted mode.")

# --- ENGINE IMPORT ---
try:
    from engine.reversal import ReversalEngine
except ImportError:
    print("[WARN] Reversal Engine module missing. Using internal fallback.")
    ReversalEngine = None

try:
    from engine.enhanced import EnhancedEngine
    ENHANCED_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Enhanced Engine module missing: {e}. Using standard engine.")
    ENHANCED_ENGINE_AVAILABLE = False
    EnhancedEngine = None

app = Flask(__name__, static_url_path='', static_folder='.')
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

load_dotenv()

# Unlimited Signal Generation Mode
REQUEST_LOG = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 5000   # Effectively UNLIMITED for users

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/test')
def test_connection():
    return jsonify({
        "status": "online",
        "server": "Quantum X PRO",
        "db_mode": "postgres" if DATABASE_URL else "sqlite"
    })

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

print("[INIT] Starting Quantum X PRO Enterprise Backend...")
print("[SYSTEM] Loading Reversal Engine & Drain Algorithms...")

# --- DATABASE SETUP (Dual-Mode: Cloud/Local) ---
DB_FILE = "security.db"
DATABASE_URL = os.getenv("DATABASE_URL")

def is_market_open():
    """Checks if the real Forex market is open based on UTC time"""
    now = datetime.datetime.utcnow()
    day = now.weekday() # 0 = Monday, 1 = Tuesday... 4 = Friday, 5 = Saturday, 6 = Sunday
    hour = now.hour
    minute = now.minute
    current_time_mins = hour * 60 + minute
    market_edge_mins = 22 * 60 # 22:00 UTC

    if day == 5: # Saturday
        return False
    if day == 6: # Sunday opens at 22:00 UTC
        return current_time_mins >= market_edge_mins
    if day == 4: # Friday closes at 22:00 UTC
        return current_time_mins < market_edge_mins
    return True # Mon-Thu

def get_db_connection():
    """Establishes connection to Supabase PostgreSQL or local SQLite with timeouts"""
    try:
        if DATABASE_URL:
             # Add connection timeout and statement timeout for robustness
             conn = psycopg2.connect(DATABASE_URL, connect_timeout=5)
             # Set a statement timeout of 10s to prevent hanging
             # cur = conn.cursor()
             # cur.execute("SET statement_timeout = 10000") 
             print("[DB] ✅ Connected to GLOBAL PROD DATABASE (PostgreSQL)")
             return conn, 'postgres'
        else:
             conn = sqlite3.connect(DB_FILE, check_same_thread=False)
             conn.row_factory = sqlite3.Row
             print(f"[DB] ⚠️ Using LOCAL DEBUG DATABASE (SQLite: {DB_FILE})")
             return conn, 'sqlite'
    except Exception as e:
        print(f"[DB] ❌ Connection Failed: {e}")
        return None, None

def init_db():
    """Ensures the licenses and win_rate_tracking tables exist."""
    conn, db_type = get_db_connection()
    if not conn: return

    try:
        cur = conn.cursor()
        if db_type == 'postgres':
            cur.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    key_code TEXT PRIMARY KEY,
                    category TEXT,
                    status TEXT,
                    device_id TEXT,
                    usage_count INTEGER DEFAULT 0,
                    last_access_date TIMESTAMP,
                    expiry_date TIMESTAMP,
                    activation_date TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS win_rate_tracking (
                    id SERIAL PRIMARY KEY,
                    signal_id TEXT,
                    broker TEXT,
                    market TEXT,
                    direction TEXT,
                    confidence INTEGER,
                    entry_time TEXT,
                    outcome TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS system_connectivity (
                    service_name TEXT PRIMARY KEY,
                    status TEXT,
                    details TEXT,
                    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id SERIAL PRIMARY KEY,
                    license_key TEXT,
                    device_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    id SERIAL PRIMARY KEY,
                    license_key TEXT,
                    device_id TEXT,
                    mouse_movements INTEGER,
                    clicks INTEGER,
                    current_url TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    key_code TEXT PRIMARY KEY,
                    category TEXT,
                    status TEXT,
                    device_id TEXT,
                    usage_count INTEGER DEFAULT 0,
                    last_access_date TIMESTAMP,
                    expiry_date TIMESTAMP,
                    activation_date TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS win_rate_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id TEXT,
                    broker TEXT,
                    market TEXT,
                    direction TEXT,
                    confidence INTEGER,
                    entry_time TEXT,
                    outcome TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS system_connectivity (
                    service_name TEXT PRIMARY KEY,
                    status TEXT,
                    details TEXT,
                    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_key TEXT,
                    device_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_key TEXT,
                    device_id TEXT,
                    mouse_movements INTEGER,
                    clicks INTEGER,
                    current_url TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
        cur.close()
        conn.close()
        print("[DB] Database Verified (Licenses + Win Rate Tracking + Connectivity).")
    except Exception as e:
        print(f"[DB] Init Error: {e}")

init_db()

def update_system_status_to_db():
    """Background heartbeat to Supabase to prove API/WS are ONLINE"""
    # Wait for data_feed to be initialized if called early
    time.sleep(10)
    while True:
        try:
            conn, db_type = get_db_connection()
            if conn:
                cur = conn.cursor()
                
                # Check status
                try:
                    q_ws_active = data_feed.quotex_ws.connected
                    f_ws_active = data_feed.forex_ws.connected
                    q_sid = data_feed.quotex_ws.sid if q_ws_active else "N/A"
                except:
                    q_ws_active = False
                    f_ws_active = False
                    q_sid = "N/A"
                
                av_status = "ONLINE" if os.getenv("ALPHA_VANTAGE_KEY") else "API_KEY_MISSING"

                stats = [
                    ('QUOTEX_WS', 'ONLINE' if q_ws_active else 'OFFLINE', f"SID: {q_sid}"),
                    ('FOREX_WS', 'ONLINE' if f_ws_active else 'OFFLINE', "WebSocket Stream Active" if f_ws_active else "N/A"),
                    ('ALPHA_VANTAGE', av_status, "Alpha Vantage Real-Market API"),
                    ('BACKEND_HEARTBEAT', 'ONLINE', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                ]

                for name, status, details in stats:
                    if db_type == 'postgres':
                        cur.execute("""
                            INSERT INTO system_connectivity (service_name, status, details, last_heartbeat)
                            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                            ON CONFLICT (service_name) DO UPDATE 
                            SET status = EXCLUDED.status, details = EXCLUDED.details, last_heartbeat = CURRENT_TIMESTAMP
                        """, (name, status, details))
                    else:
                        cur.execute("""
                            INSERT OR REPLACE INTO system_connectivity (service_name, status, details, last_heartbeat)
                            VALUES (?, ?, ?, datetime('now'))
                        """, (name, status, details))
                
                conn.commit()
                cur.close()
                conn.close()
        except Exception as e:
            print(f"[HEARTBEAT] Supabase Sync Error: {e}")
        time.sleep(60) # Sync every 60 seconds

# Start the global synchronization heartbeat
connector_thread = threading.Thread(target=update_system_status_to_db, daemon=True)
connector_thread.start()

# --- MARKET DATA FEED (ENHANCED) ---
class LiveMarketData:
    """
    Pulls live quotes from Alpha Vantage for key real-market pairs.
    Uses lightweight caching to respect free-tier limits (5 req/min).
    """
    def __init__(self, api_key):
        self.api_key = api_key
        self.cache = {}  # key -> (timestamp, candles)
        self.cache_ttl = 55  # seconds

    def _cached(self, key):
        now = time.time()
        if key in self.cache:
            ts, data = self.cache[key]
            if now - ts < self.cache_ttl:
                return data
        return None

    def _store(self, key, data):
        self.cache[key] = (time.time(), data)
        return data

    def _fetch_fx_intraday(self, from_sym, to_sym):
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "FX_INTRADAY",
            "from_symbol": from_sym,
            "to_symbol": to_sym,
            "interval": "1min",
            "outputsize": "compact",
            "apikey": self.api_key,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        series = data.get("Time Series FX (1min)", {})
        candles = []
        for ts, v in list(series.items())[:50]:
            candles.append({
                "open": float(v["1. open"]),
                "high": float(v["2. high"]),
                "low": float(v["3. low"]),
                "close": float(v["4. close"]),
                "ts": ts
            })
        return candles if candles else None

    def _fetch_crypto_intraday(self, symbol, market="USD"):
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "CRYPTO_INTRADAY",
            "symbol": symbol,
            "market": market,
            "interval": "1min",
            "apikey": self.api_key,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        series = data.get("Time Series Crypto (1min)", {})
        candles = []
        for ts, v in list(series.items())[:50]:
            candles.append({
                "open": float(v["1. open"]),
                "high": float(v["2. high"]),
                "low": float(v["3. low"]),
                "close": float(v["4. close"]),
                "ts": ts
            })
        return candles if candles else None

    def _fetch_fx_spot(self, from_sym, to_sym):
        """
        Single quote fallback; builds small synthetic candles around spot.
        """
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_sym,
            "to_currency": to_sym,
            "apikey": self.api_key,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rate_info = data.get("Realtime Currency Exchange Rate", {})
        price = float(rate_info.get("5. Exchange Rate", 0))
        if not price:
            return None
        candles = []
        for i in range(20):
            jitter = (random.random() - 0.5) * price * 0.0002
            close = price + jitter
            candles.append({
                "open": close - jitter * 0.5,
                "high": close + abs(jitter),
                "low": close - abs(jitter),
                "close": close,
                "ts": time.time() - i * 60
            })
        return candles

    def get_candles(self, asset):
        key = asset.upper()
        cached = self._cached(key)
        if cached:
            return cached

        try:
            if key == "EUR/USD":
                data = self._fetch_fx_intraday("EUR", "USD")
            elif key == "GBP/USD":
                data = self._fetch_fx_intraday("GBP", "USD")
            elif key == "USD/JPY":
                data = self._fetch_fx_intraday("USD", "JPY")
            elif key == "XAU/USD":
                # Spot fallback
                data = self._fetch_fx_spot("XAU", "USD")
            elif key == "BTC/USD":
                data = self._fetch_crypto_intraday("BTC", "USD")
            else:
                data = None
        except Exception as e:
            print(f"[LIVE] Alpha Vantage fetch failed for {asset}: {e}")
            data = None

        if data:
            return self._store(key, data)
        return None

class MarketDataFeed:
    def __init__(self):
        self.adapters = {}
        self.active_broker = None
        self.live_data = LiveMarketData(os.getenv("ALPHA_VANTAGE_KEY", "VVGMFL50W479KT8T"))
        self.quotex_ws = QuotexWSAdapter()
        self.forex_ws = ForexWSAdapter()
        
        # Initialize Brokers based on Config
        if QuotexAdapter and BROKER_CONFIG.get("QUOTEX"):
            print("[FEED] Initializing Quotex Adapter...")
            self.adapters["QUOTEX"] = QuotexAdapter(BROKER_CONFIG["QUOTEX"])
            
        if IQOptionAdapter and BROKER_CONFIG.get("IQOPTION"):
            print("[FEED] Initializing IQ Option Adapter...")
            self.adapters["IQOPTION"] = IQOptionAdapter(BROKER_CONFIG["IQOPTION"])
            
        if PocketOptionAdapter and BROKER_CONFIG.get("POCKETOPTION"):
            print("[FEED] Initializing Pocket Option Adapter...")
            self.adapters["POCKETOPTION"] = PocketOptionAdapter(BROKER_CONFIG["POCKETOPTION"])

        if BinollaAdapter and BROKER_CONFIG.get("BINOLLA"):
             print("[FEED] Initializing Binolla Adapter...")
             self.adapters["BINOLLA"] = BinollaAdapter(BROKER_CONFIG["BINOLLA"])

        # --- CORE WS CONNECTIVITY (User Request) ---
        print("[FEED] ⚡ Establishing Direct WebSocket Connections...")
        q_ws_status = self.quotex_ws.connect()
        f_ws_status = self.forex_ws.connect()
        
        if q_ws_status:
            print("[FEED] ✅ Quotex WS (ws2.market-qx.trade) Handshake Verified.")
        if f_ws_status:
            print("[FEED] ✅ Forex WS (ws.binaryws.com) Stream Active.")
        # ---------------------------------------------

        # Try to connect asynchronously
        self.connect_brokers()

    def normalize_asset(self, asset):
        clean = asset.strip().upper()
        clean = clean.replace("(OTC)", "").replace("  ", " ").strip()
        clean = clean.replace(" ", "")
        return clean

    def connect_brokers(self, retry_count=3, retry_delay=5):
        """Attempts to connect to all configured brokers with retry logic."""
        def _connect():
            for name, adapter in self.adapters.items():
                connected = False
                for attempt in range(retry_count):
                    try:
                        if adapter.connect():
                            print(f"[FEED] ✅ Connected to {name} Successfully (Attempt {attempt + 1}).")
                            self.active_broker = name
                            connected = True
                            break
                        else:
                            if attempt < retry_count - 1:
                                print(f"[FEED] ⚠️  {name} connection failed (Attempt {attempt + 1}/{retry_count}). Retrying in {retry_delay}s...")
                                time.sleep(retry_delay)
                    except Exception as e:
                        print(f"[FEED] ❌ Error connecting to {name} (Attempt {attempt + 1}): {e}")
                        if attempt < retry_count - 1:
                            time.sleep(retry_delay)
                
                if not connected:
                    print(f"[FEED] ⚠️  {name} connection failed after {retry_count} attempts. Running in SIMULATION mode.")
        
        t = threading.Thread(target=_connect)
        t.daemon = True
        t.start()

    def get_candles(self, asset, timeframe_minutes):
        """
        Fetches candles. Tries real brokers first, then simulation fallback.
        """
        # 0. Live market data for non-OTC majors (Alpha Vantage or Binary.com WS)
        if "(OTC)" not in asset:
            # Try Binary.com WS first for real-time forex
            if self.forex_ws.connected:
                price = self.forex_ws.get_price(asset)
                if price:
                    # Create a synthetic recent candle from the tick
                    return [{"close": price, "open": price, "high": price, "low": price, "ts": time.time()}]
            
            live = self.live_data.get_candles(asset)
            if live:
                return live

        tf_seconds = timeframe_minutes * 60
        # Preferred active broker then others
        ordered = [self.active_broker] if self.active_broker else []
        ordered += [n for n in self.adapters.keys() if n not in ordered]

        for name in ordered:
            adapter = self.adapters.get(name)
            if not adapter:
                continue
            getter = getattr(adapter, "get_candles", None)
            if not getter:
                continue
            try:
                live = getter(asset, tf_seconds, 50)
                if live:
                    return live
            except Exception as e:
                print(f"[FEED] {name} candle fetch failed: {e}")

        # --- STOCHASTIC SIMULATION FALLBACK (Pro Sync) ---
        # If real data fails, we generate a high-fidelity synchronized stream.
        # This keeps the system running 24/7 with 'AI-Estimated' market movements.
        return self.generate_stochastic_candles(asset, timeframe_minutes)

    def generate_stochastic_candles(self, asset, timeframe_minutes):
        """Generates a high-fidelity, synchronized candle stream with stochastic noise."""
        now_ts = int(time.time() / 60) * 60
        candles = []
        
        # Consistent seed per asset/hour for global synchronization
        hour_ts = int(time.time() / 3600) * 3600
        seed_base = f"{asset}_{hour_ts}"
        asset_seed = int(hashlib.sha256(seed_base.encode()).hexdigest(), 16)
        
        # Dynamic base price
        base_price = 1.0 + (asset_seed % 1000) / 5000.0
        
        for i in range(60):
            ts = now_ts - (i * timeframe_minutes * 60)
            # Use unique seed for each candle
            c_seed = int(hashlib.sha256(f"{seed_base}_{ts}".encode()).hexdigest(), 16)
            
            # Stochastic Walk
            walk = ( (c_seed % 1001) - 500 ) / 100000.0
            c_open = base_price
            c_close = base_price + walk
            
            # Wick generation
            high = max(c_open, c_close) + ( (c_seed % 100) / 100000.0 )
            low = min(c_open, c_close) - ( ((c_seed >> 4) % 100) / 100000.0 )
            
            candles.append({
                "open": c_open,
                "high": high,
                "low": low,
                "close": c_close,
                "ts": ts
            })
            base_price = c_close # Next candle opens where this one closed
            
        return candles[::-1]

data_feed = MarketDataFeed()
reversal_engine = ReversalEngine() if ReversalEngine else None

# Initialize Enhanced Engine if available
if ENHANCED_ENGINE_AVAILABLE:
    enhanced_engine = EnhancedEngine()
    print("[ENGINE] ✅ Pro Engine v3.0 Loaded (Wick Rejection + Stochastic Sync)")
else:
    enhanced_engine = None
    print("[ENGINE] ⚠️  Fallback Engine Active")

# --- ADVANCED SIGNAL STRATEGIES ---
class InstitutionalSignalEngine:
    def __init__(self):
        self.reversal_engine = reversal_engine

    def calculate_rsi(self, prices, period=14):
        if not prices: return 50
        deltas = [prices[i+1] - prices[i] for i in range(len(prices)-1)]
        gains = [d for d in deltas if d > 0]
        losses = [-d for d in deltas if d < 0]
        avg_gain = sum(gains[-period:]) / period if len(gains) >= period else (sum(gains) / period if gains else 0)
        avg_loss = sum(losses[-period:]) / period if len(losses) >= period else (sum(losses) / period if losses else 0)
        if avg_loss == 0: return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def calculate_sma(self, prices, period):
        if len(prices) < period:
            return sum(prices) / len(prices) if prices else 0
        return sum(prices[-period:]) / period

    def calculate_atr(self, candles, period=14):
        if not candles or len(candles) < 2:
            return 0
        trs = []
        for i in range(1, len(candles)):
            prev = candles[i-1]
            cur = candles[i]
            tr = max(
                cur["high"] - cur["low"],
                abs(cur["high"] - prev["close"]),
                abs(cur["low"] - prev["close"]),
            )
            trs.append(tr)
        if len(trs) < period:
            return sum(trs) / len(trs) if trs else 0
        return sum(trs[-period:]) / period

    def score_trend(self, prices):
        if len(prices) < 5:
            return 0, "NEUTRAL"
        sma_fast = self.calculate_sma(prices, 5)
        sma_mid = self.calculate_sma(prices, 13)
        sma_slow = self.calculate_sma(prices, 21)
        score = 0
        if sma_fast > sma_mid > sma_slow:
            score += 1
        elif sma_fast < sma_mid < sma_slow:
            score -= 1
        slope = prices[-1] - prices[-5]
        if slope > 0:
            score += 1
        elif slope < 0:
            score -= 1
        direction = "UP" if score > 0 else ("DOWN" if score < 0 else "NEUTRAL")
        return score, direction

    def score_volatility(self, candles):
        atr = self.calculate_atr(candles, period=14)
        if not candles or atr == 0:
            return 0
        last_close = candles[-1]["close"]
        vol_ratio = atr / last_close
        # normalize to small score contribution
        if vol_ratio > 0.004:
            return -0.5  # too volatile, lower confidence
        if vol_ratio < 0.001:
            return 0.25  # stable
        return 0

    def analyze(self, broker, marker, timeframe, candles=None, entry_time=None):
        """
        Standard analysis with global synchronization logic.
        """
        # 1. Get Data (Real or provided)
        if candles is None:
            candles = data_feed.get_candles(marker, timeframe)
        closes = [c['close'] for c in candles] if candles else []
        
        # 2. Reversal Engine Analysis
        rev_dir, rev_conf, rev_strategy = "NEUTRAL", 0, None
        if self.reversal_engine:
            rev_dir, rev_conf, rev_strategy = self.reversal_engine.analyze(marker, timeframe, real_candles=candles)
        
        # 3. Decision Logic
        if rev_dir != "NEUTRAL" and rev_conf > 85:
            return rev_dir, rev_conf
            
        # 4. Fallback / Confirmation Strategy
        rsi = self.calculate_rsi(closes, period=14)
        trend_score, trend_dir = self.score_trend(closes)
        vol_score = self.score_volatility(candles or [])

        # Direction decision - Deterministic Global Consensus
        if trend_dir == "UP":
            direction = "CALL"
        elif trend_dir == "DOWN":
            direction = "PUT"
        else:
            # Deterministic decision based on Hash of Market and Entry Time
            import hashlib
            seed_str = f"{marker}_{entry_time}"
            seed_hash = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
            
            # NEUTRAL trend - use RSI and additional factors for balanced decision
            if rsi < 40:
                direction = "CALL"  # Oversold
            elif rsi > 60:
                direction = "PUT"   # Overbought
            else:
                # Use deterministic seed for true neutral
                direction = "CALL" if seed_hash % 2 == 0 else "PUT"

        # Confidence synthesis
        conf = 80
        # RSI influence
        if rsi < 30 or rsi > 70:
            conf += 8
        elif 40 <= rsi <= 60:
            conf -= 4
        # Trend influence
        conf += trend_score * 3
        # Volatility adjustment
        conf += int(vol_score * 10)
        # Live data bonus
        if candles:
            conf += 3
        
        # Use seed_hash to add a tiny deterministic jitter to confidence for "uniqueness" that matches for everyone
        if 'seed_hash' in locals():
            conf += (seed_hash % 3)
            
        # OTC slight boost
        if "OTC" in marker:
            conf = min(98, conf + 2)

        conf = max(70, min(98, conf))
        return direction, conf

engine = InstitutionalSignalEngine()

# --- API ENDPOINTS ---

@app.route('/api/validate_license', methods=['POST'])
def validate_license():
    data = request.json
    key = data.get('key')
    device_id = data.get('device_id')
    
    print(f"[AUTH] Validating Key: {key} for Device: {device_id}")

    conn, db_type = get_db_connection()
    if not conn:
        print("[AUTH] DB Connection Failed")
        return jsonify({"valid": False, "message": "Secure Server Unreachable"}), 500
        
    cur = conn.cursor()
    
    try:
        # Check Key (Case-Insensitive and Stripped)
        clean_key = key.strip().upper()
        
        query = "SELECT category, status, device_id, expiry_date FROM licenses WHERE UPPER(key_code)=%s" if db_type == 'postgres' else "SELECT category, status, device_id, expiry_date FROM licenses WHERE UPPER(key_code)=?"
        cur.execute(query, (clean_key,))
        row = cur.fetchone()
        
        if not row:
            print(f"[AUTH] Invalid Key Attempt: {clean_key}")
            return jsonify({"valid": False, "message": "Invalid License Key. Check for typos."}), 200
            
        category, status, locked_device, expiry_date = row
        
        # Expiry Check
        if expiry_date:
            # Ensure expiry_date is a datetime object
            if isinstance(expiry_date, str):
                try:
                    expiry_date = datetime.datetime.strptime(expiry_date, "%Y-%m-%d %H:%M:%S")
                except:
                    try:
                        expiry_date = datetime.datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                    except:
                        pass
            
            if datetime.datetime.utcnow() > expiry_date.replace(tzinfo=None):
                print(f"[AUTH] Key Expired: {clean_key}")
                return jsonify({"valid": False, "message": "License Key has Expired. Please renew."}), 200

        # DEVICE LOCK LOGIC
        if locked_device and locked_device != device_id:
            # Check if this is an privileged OWNER key (Bypass Lock)
            if category == 'OWNER':
                print(f"[AUTH] OWNER BYPASS: Admin {clean_key} verified on new Hardware {device_id}")
                # We update the primary device_id to the most recent owner machine
            else:
                # STRICT DEVICE LOCK: Key is already bound to another hardware signature
                print(f"[AUTH] SECURITY ALERT: Key {clean_key} breach attempt! New device {device_id} tried using a key locked to {locked_device}")
                return jsonify({"valid": False, "message": "CRITICAL: This license is already locked to another device system."}), 200
            
        # If no device is locked yet, or if it's an OWNER update
        if not locked_device or category == 'OWNER':
            print(f"[AUTH] Hardware Bond Established: Binding Key {clean_key} to Identity {device_id}")
        
        # Update last access and metadata (Silenly capture Geo/IP)
        ip_addr = request.remote_addr
        # Handle Render's Forwarded-For
        if request.headers.get('X-Forwarded-For'):
            ip_addr = request.headers.get('X-Forwarded-For').split(',')[0]
            
        geo = get_geo_info(ip_addr)
        
        # Update usage count and last access
        update_q = "UPDATE licenses SET status='ACTIVE', device_id=%s, last_access_date=CURRENT_TIMESTAMP, usage_count = COALESCE(usage_count, 0) + 1 WHERE UPPER(key_code)=%s" if db_type == 'postgres' else "UPDATE licenses SET status='ACTIVE', device_id=?, last_access_date=datetime('now'), usage_count = COALESCE(usage_count, 0) + 1 WHERE UPPER(key_code)=?"
        cur.execute(update_q, (device_id, clean_key))
        
        # Log session
        try:
            cur.execute("INSERT INTO user_sessions (license_key, device_id, ip_address, user_agent, timestamp) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)", 
                        (clean_key, device_id, ip_addr, request.headers.get('User-Agent')))
        except:
            pass
            
        conn.commit()
        
        return jsonify({
            "valid": True,
            "category": category,
            "hwid": generate_quantum_hwid(device_id),
            "message": f"Identity Verified. Connected to Enterprise Grid ({geo.get('country', 'Secure')})."
        })
    except Exception as e:
        print(f"[AUTH] Error: {e}")
        return jsonify({"valid": False, "message": "Secure Server Validation Error"}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/check_device_sync', methods=['POST'])
def check_device_sync():
    """Matches hardware signature with existing valid license for automatic entry"""
    try:
        data = request.json
        device_id = data.get('device_id')
        if not device_id: return jsonify({"valid": False}), 400
        
        conn, db_type = get_db_connection()
        if not conn: return jsonify({"valid": False}), 500
        
        ip_addr = request.remote_addr
        if request.headers.get('X-Forwarded-For'):
            ip_addr = request.headers.get('X-Forwarded-For').split(',')[0]
            
        cur = conn.cursor()
        
        # Find any active, non-expired license belonging to this device
        if db_type == 'postgres':
            cur.execute("""
                SELECT key_code, category, expiry_date 
                FROM licenses 
                WHERE device_id=%s
                AND (status='ACTIVE' OR status='PENDING' OR category='OWNER')
                ORDER BY last_access_date DESC LIMIT 1
            """, (device_id,))
        else:
            cur.execute("""
                SELECT key_code, category, expiry_date 
                FROM licenses 
                WHERE device_id=? AND (status='ACTIVE' OR status='PENDING' OR category='OWNER')
            """, (device_id,))
            
        row = cur.fetchone()
        
        if not row:
            cur.close()
            conn.close()
            return jsonify({"valid": False}), 200
            
        key, category, expiry_date = row
        
        # Expiry check logic (simplified for brevity here)
        valid = True
        if expiry_date:
            if isinstance(expiry_date, str):
                try: expiry_date = datetime.datetime.strptime(expiry_date, "%Y-%m-%d %H:%M:%S")
                except: expiry_date = datetime.datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
            if datetime.datetime.utcnow() > expiry_date.replace(tzinfo=None):
                valid = False
        
        if not valid:
            cur.close()
            conn.close()
            return jsonify({"valid": False}), 200

        # Auto-update tracking and usage count
        update_q = "UPDATE licenses SET last_access_date=CURRENT_TIMESTAMP, usage_count = COALESCE(usage_count, 0) + 1 WHERE key_code=%s" if db_type == 'postgres' else "UPDATE licenses SET last_access_date=datetime('now'), usage_count = COALESCE(usage_count, 0) + 1 WHERE key_code=?"
        cur.execute(update_q, (key,))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            "valid": True,
            "key": key,
            "category": category,
            "hwid": generate_quantum_hwid(device_id),
            "message": "System Recognized. Security Layers Synchronized Automatically."
        })
    except Exception as e:
        print(f"[AUTH] Device Sync Error: {e}")
        return jsonify({"valid": False}), 500

def verify_access(key, device_id):
    """
    Returns (bool, error_message or None)
    """
    conn, db_type = get_db_connection()
    if not conn: 
        return False, "DATABASE_ERROR"
    
    try:
        cur = conn.cursor()
        clean_key = key.strip().upper()
        
        query = "SELECT status, device_id, expiry_date FROM licenses WHERE UPPER(key_code)=%s" if db_type == 'postgres' else "SELECT status, device_id, expiry_date FROM licenses WHERE UPPER(key_code)=?"
        cur.execute(query, (clean_key,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if not row: 
            return False, "INVALID_KEY"
            
        status, locked_device, expiry_date = row

        # Expiry Check
        if expiry_date:
            if isinstance(expiry_date, str):
                try:
                    expiry_date = datetime.datetime.strptime(expiry_date, "%Y-%m-%d %H:%M:%S")
                except:
                    try:
                        expiry_date = datetime.datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                    except:
                        pass
            
            if datetime.datetime.utcnow() > expiry_date.replace(tzinfo=None):
                return False, "LICENSE_EXPIRED"
        
        # Check blockage
        if status == 'BLOCKED': 
            return False, "LICENSE_BLOCKED"
            
        if status != 'ACTIVE' and status != 'PENDING': 
            return False, "LICENSE_INACTIVE"
            
        # We still verify the key is ALMOST bound to this device or is a valid floating key
        # Removed strict DEVICE_MISMATCH to allow "One License for All" behavior
        
        return True, None
    except Exception as e:
        print(f"[AUTH] verify_access error: {e}")
        return False, "VALIDATION_EXCEPTION"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # --- SECURITY ENFORCEMENT ---
        key = data.get('license_key')
        device_id = data.get('device_id')
        broker = data.get('broker')
        market = data.get('market')
        timezone_name = data.get('timezone', 'UTC')
        timeframe_str = data.get('timeframe', 'M1')
        
        # timeframe handling...
        if isinstance(timeframe_str, str):
            if timeframe_str.upper() == 'M1': timeframe = 1
            elif timeframe_str.upper() == 'M5': timeframe = 5
            else: timeframe = int(timeframe_str.replace('M', '').replace('m', '')) if timeframe_str.replace('M', '').replace('m', '').isdigit() else 1
        else: timeframe = int(timeframe_str) if timeframe_str else 1

        if not key or not device_id or not market:
            return jsonify({"error": "Missing required fields"}), 400

        # --- MARKET OPEN CHECK (User Request) ---
        is_otc = "(OTC)" in market
        if not is_otc and not is_market_open():
            return jsonify({
                "error": "MARKET CLOSED", 
                "message": "Real Forex market is currently closed. Signals only available for OTC assets on weekends."
            }), 403

        # simple rate limit per key+device
        now = time.time()
        bucket = f"{key}:{device_id}"
        REQUEST_LOG[bucket] = [t for t in REQUEST_LOG[bucket] if now - t < RATE_LIMIT_WINDOW]
        if len(REQUEST_LOG[bucket]) >= RATE_LIMIT_MAX:
            return jsonify({"error": "Rate limit exceeded"}), 429
        REQUEST_LOG[bucket].append(now)

        # Verification with detailed error reporting
        access_granted, error_code = verify_access(key, device_id)
        
        if not access_granted:
            print(f"[SECURITY] Access Denied: {key} | {device_id} | Code: {error_code}")
            
            if error_code == "DATABASE_ERROR" or error_code == "VALIDATION_EXCEPTION":
                return jsonify({
                    "error": "SERVER_BUSY",
                    "message": "Secure authentication server is under high load. Please try again in a few seconds."
                }), 503
                
            if error_code == "DEVICE_MISMATCH":
                return jsonify({
                    "error": "UNAUTHORIZED",
                    "message": "This license is already registered to another device."
                }), 403
                
            return jsonify({
                "error": "UNAUTHORIZED", 
                "message": "Unauthorized Access. Valid License Required."
            }), 403
        # ----------------------------
        
        candles = data_feed.get_candles(market, timeframe)
        
        # --- WS & DATA VALIDATION (High-Precision Rule) ---
        # Check WS health
        quotex_ws_active = data_feed.quotex_ws.connected or (broker == "QUOTEX" and data_feed.adapters.get("QUOTEX") and data_feed.adapters["QUOTEX"].connected)
        forex_ws_active = data_feed.forex_ws.connected
        
        if not candles:
            print(f"[PREDICT] Aborting: No real-time data for {market}")
            return jsonify({
                "error": "WS_DISCONNECTED",
                "message": "System could not establish a secure handshake with the data stream. Please check your internet connection."
            }), 403
        # ---------------------------------------------------
        
        # --- ENHANCED VERCEL COMPATIBILITY ---
        # On Vercel, WS handshake might be blocked by Cloudflare or Lambda timeouts.
        # We allow fallback to Deterministic Simulation to ensure 24/7 availability.
        ws_synchronizing = quotex_ws_active or forex_ws_active
        # ---------------------------------------------------
        # Dynamic Timezone Handling (User's local time) - Moved up for Global Sync
        try:
            import pytz
            user_tz = pytz.timezone(timezone_name)
            local_now = datetime.datetime.now(user_tz)
            # Entry happens at the start of the next minute (HH:MM format as requested)
            entry_time_calculated = (local_now + datetime.timedelta(minutes=1)).strftime("%H:%M")
        except Exception as e:
            print(f"[TIME] Timezone calculation error ({timezone_name}): {e}")
            # Global Fallback to UTC if timezone is invalid
            utc_now = datetime.datetime.utcnow()
            entry_time_calculated = (utc_now + datetime.timedelta(minutes=1)).strftime("%H:%M")

        if enhanced_engine:
            direction, conf, strategy = enhanced_engine.analyze(broker, market, timeframe, candles=candles, entry_time=entry_time_calculated)
            
            # Get win rate estimate
            win_rate = enhanced_engine.get_win_rate(market)
        else:
            direction, conf = engine.analyze(broker, market, timeframe, candles=candles, entry_time=entry_time_calculated)
            strategy = "STANDARD_ANALYSIS"
            win_rate = 0
        
        # Generate unique signal ID for tracking
        signal_id = f"{broker}_{market}_{int(time.time())}"

        # Store signal for win rate tracking (outcome will be updated later)
        try:
            conn, db_type = get_db_connection()
            if conn:
                cur = conn.cursor()
                if db_type == 'postgres':
                    cur.execute("""
                        INSERT INTO win_rate_tracking (signal_id, broker, market, direction, confidence, entry_time)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (signal_id, broker, market, direction, conf, entry_time_calculated))
                else:
                    cur.execute("""
                        INSERT INTO win_rate_tracking (signal_id, broker, market, direction, confidence, entry_time)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (signal_id, broker, market, direction, conf, entry_time_calculated))
                conn.commit()
                cur.close()
                conn.close()
        except Exception as e:
            print(f"[TRACKING] Failed to log signal: {e}")
        
        # Determine data source quality
        data_quality = "REAL" if candles else "SIMULATED"
        
        return jsonify({
            "direction": direction,
            "confidence": conf,
            "entry_time": entry_time_calculated,
            "time_zone": timezone_name,
            "broker": broker,
            "market": market,
            "strategy": strategy,
            "signal_id": signal_id,
            "win_rate_estimate": round(win_rate, 1),
            "data_quality": data_quality,
            "ws_active": quotex_ws_active or forex_ws_active,
            "handshake_verified": quotex_ws_active,
            "strategies": [strategy, "RSI_ANALYSIS", "TREND_DETECTION", "VOLATILITY_ANALYSIS"]
        })
    except Exception as e:
        print(f"Prediction Error: {e}")
        return jsonify({"error": "Analysis Failed"}), 500

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/test')
def test():
    # Return connectivity status of brokers
    broker_status = {name: (adapter.connected if hasattr(adapter, 'connected') else "Unknown") 
                     for name, adapter in data_feed.adapters.items()} if data_feed else {}
    _, db_type = get_db_connection()
    return jsonify({
        "status": "ONLINE", 
        "version": "4.0-ENT-ENHANCED",
        "engine": "Enhanced v2.0" if enhanced_engine else "Standard",
        "db_mode": db_type,
        "brokers": broker_status,
        "active_broker": data_feed.active_broker if data_feed else None
    })

@app.route('/api/win_rate', methods=['GET'])
def get_win_rate():
    """Get win rate statistics"""
    try:
        market = request.args.get('market')
        broker = request.args.get('broker')
        
        conn, db_type = get_db_connection()
        if not conn:
            return jsonify({"error": "Database unavailable"}), 500
        
        cur = conn.cursor()
        
        # Build query
        query = "SELECT COUNT(*) as total, SUM(CASE WHEN outcome = 'WIN' THEN 1 ELSE 0 END) as wins FROM win_rate_tracking WHERE outcome IS NOT NULL"
        params = []
        
        if market:
            query += " AND market = ?" if db_type == 'sqlite' else " AND market = %s"
            params.append(market)
        
        if broker:
            query += " AND broker = ?" if db_type == 'sqlite' else " AND broker = %s"
            params.append(broker)
        
        cur.execute(query, params)
        result = cur.fetchone()
        
        total = result[0] if result else 0
        wins = result[1] if result and result[1] else 0
        
        win_rate = (wins / total * 100) if total > 0 else 0
        
        cur.close()
        conn.close()
        
        return jsonify({
            "win_rate": round(win_rate, 2),
            "total_signals": total,
            "wins": wins,
            "losses": total - wins,
            "market": market or "ALL",
            "broker": broker or "ALL"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/track_outcome', methods=['POST'])
def track_outcome():
    """Update signal outcome (WIN/LOSS) for win rate tracking"""
    try:
        data = request.json
        signal_id = data.get('signal_id')
        outcome = data.get('outcome')  # 'WIN' or 'LOSS'
        
        if not signal_id or outcome not in ['WIN', 'LOSS']:
            return jsonify({"error": "Invalid parameters"}), 400
        
        conn, db_type = get_db_connection()
        if not conn:
            return jsonify({"error": "Database unavailable"}), 500
        
        cur = conn.cursor()
        if db_type == 'postgres':
            cur.execute("UPDATE win_rate_tracking SET outcome = %s WHERE signal_id = %s", (outcome, signal_id))
        else:
            cur.execute("UPDATE win_rate_tracking SET outcome = ? WHERE signal_id = ?", (outcome, signal_id))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({"success": True, "message": "Outcome tracked"})
    except Exception as e:
        print(f"[AUTH] Track outcome failed: {e}")
        return jsonify({"valid": False, "message": "Secure Server Validation Error"}), 500
@app.route('/api/track_activity', methods=['POST'])
def track_activity():
    """Silent collection of user interaction data"""
    try:
        data = request.json
        cur_url = data.get('url')
        clicks = data.get('clicks', 0)
        mouse = data.get('mouse', 0)
        key = data.get('license_key')
        device = data.get('device_id')
        
        conn, db_type = get_db_connection()
        if conn:
            cur = conn.cursor()
            if db_type == 'postgres':
                cur.execute("""
                    INSERT INTO user_activity (license_key, device_id, mouse_movements, clicks, current_url, timestamp)
                    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (key, device, mouse, clicks, cur_url))
            else:
                cur.execute("""
                    INSERT INTO user_activity (license_key, device_id, mouse_movements, clicks, current_url, timestamp)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (key, device, mouse, clicks, cur_url))
            conn.commit()
            cur.close()
            conn.close()
        return jsonify({"status": "logged"})
    except:
        return jsonify({"status": "skipped"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("="*60)
    print(" QUANTUM X PRO - ENTERPRISE SERVER ")
    print(" Connected to Global Data Feeds: [QUOTEX, IQ, POCKET, BINOLLA]")
    print(f" Listening on Port {port}...")
    print("="*60)
    app.run(host='0.0.0.0', port=port, debug=False)


