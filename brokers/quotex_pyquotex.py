"""
QUANTUM X PRO - PyQuotex Integration
Full Quotex API + WebSocket with Cloudflare Bypass
Email/Password Authentication - No Browser Needed
"""
import asyncio
import os
from datetime import datetime
from typing import Optional, Dict, List
import logging

try:
    from pyquotex import Quotex
    PYQUOTEX_AVAILABLE = True
except ImportError:
    PYQUOTEX_AVAILABLE = False
    print("[QUOTEX] ⚠️ PyQuotex not installed. Run: pip install pyquotex")

class QuotexPyQuotexAdapter:
    """
    Enterprise-grade Quotex adapter using PyQuotex library
    - Email/Password authentication
    - Full API access
    - Real-time WebSocket streams
    - Cloudflare bypass (built-in)
    - Automatic reconnection
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.email = self.config.get('email') or os.getenv('QUOTEX_EMAIL')
        self.password = self.config.get('password') or os.getenv('QUOTEX_PASSWORD')
        
        self.client: Optional[Quotex] = None
        self.connected = False
        self.sid = None
        self.balance = 0.0
        self.account_type = "DEMO"
        
        # Real-time data storage
        self.realtime_candles = {}
        self.realtime_prices = {}
        self.realtime_sentiment = {}
        
        # Connection status
        self.last_ping = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("QuotexPyQuotex")
    
    async def connect(self) -> bool:
        """
        Connect to Quotex using email/password
        Bypasses Cloudflare automatically through PyQuotex
        """
        if not PYQUOTEX_AVAILABLE:
            self.logger.error("PyQuotex library not available")
            return False
        
        if not self.email or not self.password:
            self.logger.error("Email/Password not configured. Set QUOTEX_EMAIL and QUOTEX_PASSWORD in .env")
            return False
        
        try:
            self.logger.info(f"[QUOTEX] Connecting with email: {self.email[:3]}***")
            
            # Initialize PyQuotex client
            self.client = Quotex(
                email=self.email,
                password=self.password,
                lang="en"  # Language
            )
            
            # Connect (handles Cloudflare automatically)
            check, reason = await self.client.connect()
            
            if check:
                self.connected = True
                self.reconnect_attempts = 0
                
                # Get account info
                try:
                    balance_data = await self.client.get_balance()
                    if balance_data:
                        self.balance = balance_data.get('balance', 0.0)
                        self.account_type = balance_data.get('demo', True) and "DEMO" or "REAL"
                except:
                    pass
                
                self.logger.info(f"[QUOTEX] ✅ Connected | Balance: ${self.balance} ({self.account_type})")
                self.last_ping = datetime.now()
                return True
            else:
                self.logger.error(f"[QUOTEX] ❌ Connection failed: {reason}")
                self.connected = False
                return False
                
        except Exception as e:
            self.logger.error(f"[QUOTEX] Connection error: {e}")
            self.connected = False
            return False
    
    async def reconnect(self) -> bool:
        """
        Automatic reconnection with retry logic
        """
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            self.logger.error(f"[QUOTEX] Max reconnection attempts ({self.max_reconnect_attempts}) reached")
            return False
        
        self.reconnect_attempts += 1
        self.logger.info(f"[QUOTEX] Reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts}")
        
        await asyncio.sleep(2 * self.reconnect_attempts)  # Exponential backoff
        return await self.connect()
    
    async def check_connection(self) -> bool:
        """
        Check if connection is alive
        """
        if not self.client:
            return False
        
        try:
            is_connected = await self.client.check_connect()
            if not is_connected and self.connected:
                self.logger.warning("[QUOTEX] Connection lost, attempting reconnect...")
                return await self.reconnect()
            return is_connected
        except:
            return False
    
    async def start_candles_stream(self, asset: str, period: int = 60):
        """
        Subscribe to real-time candle data
        
        Args:
            asset: Asset name (e.g., "EURUSD", "BTCUSD")
            period: Timeframe in seconds (60, 300, 900, etc.)
        """
        if not self.connected:
            await self.connect()
        
        if not self.connected:
            return None
        
        try:
            self.logger.info(f"[QUOTEX] Starting candles stream: {asset} ({period}s)")
            await self.client.start_candles_stream(asset, period)
            return True
        except Exception as e:
            self.logger.error(f"[QUOTEX] Candles stream error: {e}")
            return None
    
    async def get_realtime_candles(self, asset: str, period: int = 60) -> Optional[Dict]:
        """
        Get real-time candle data
        """
        try:
            await self.start_candles_stream(asset, period)
            
            # Wait for data
            for _ in range(10):  # 2 second timeout
                if self.client.realtime_candles.get(asset):
                    return self.client.realtime_candles[asset]
                await asyncio.sleep(0.2)
            
            return None
        except Exception as e:
            self.logger.error(f"[QUOTEX] Get candles error: {e}")
            return None
    
    async def get_realtime_price(self, asset: str) -> Optional[float]:
        """
        Get real-time price for asset
        """
        try:
            price_data = await self.client.start_realtime_price(asset)
            if price_data and asset in price_data:
                return price_data[asset]
            return None
        except Exception as e:
            self.logger.error(f"[QUOTEX] Get price error: {e}")
            return None
    
    async def get_realtime_sentiment(self, asset: str) -> Optional[Dict]:
        """
        Get market sentiment (buy/sell pressure)
        """
        try:
            sentiment = await self.client.start_realtime_sentiment(asset)
            return sentiment
        except Exception as e:
            self.logger.error(f"[QUOTEX] Get sentiment error: {e}")
            return None
    
    async def get_candles(self, asset: str, timeframe_seconds: int = 60, count: int = 100, end_ts: int = None) -> Optional[List]:
        """
        Get historical candles
        
        Args:
            asset: Asset name
            timeframe_seconds: Candle period (60, 300, 900, etc.)
            count: Number of candles
            end_ts: End timestamp (optional)
        """
        if not self.connected:
            await self.connect()
        
        if not self.connected:
            return None
        
        try:
            self.logger.info(f"[QUOTEX] Fetching {count} candles for {asset} ({timeframe_seconds}s)")
            
            candles = await self.client.get_candles(
                asset=asset,
                period=timeframe_seconds,
                count=count
            )
            
            if candles:
                self.logger.info(f"[QUOTEX] ✅ Retrieved {len(candles)} candles")
                return candles
            
            return None
            
        except Exception as e:
            self.logger.error(f"[QUOTEX] Get candles error: {e}")
            return None
    
    async def place_trade(self, asset: str, amount: float, direction: str, duration: int = 60) -> Optional[Dict]:
        """
        Place a binary options trade
        
        Args:
            asset: Asset name
            amount: Trade amount
            direction: "call" or "put"
            duration: Trade duration in seconds
        """
        if not self.connected:
            await self.connect()
        
        if not self.connected:
            return None
        
        try:
            self.logger.info(f"[QUOTEX] Placing {direction.upper()} trade: {asset} ${amount} {duration}s")
            
            result = await self.client.buy(
                amount=amount,
                asset=asset,
                direction=direction.lower(),
                duration=duration
            )
            
            if result:
                self.logger.info(f"[QUOTEX] ✅ Trade placed successfully")
                return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"[QUOTEX] Trade error: {e}")
            return None
    
    async def get_balance(self) -> float:
        """
        Get current account balance
        """
        if not self.connected:
            await self.connect()
        
        try:
            balance_data = await self.client.get_balance()
            if balance_data:
                self.balance = balance_data.get('balance', 0.0)
                return self.balance
            return 0.0
        except Exception as e:
            self.logger.error(f"[QUOTEX] Get balance error: {e}")
            return 0.0
    
    async def disconnect(self):
        """
        Gracefully disconnect
        """
        if self.client:
            try:
                await self.client.close()
                self.connected = False
                self.logger.info("[QUOTEX] Disconnected")
            except:
                pass
    
    def __del__(self):
        """
        Cleanup on deletion
        """
        if self.connected:
            try:
                asyncio.run(self.disconnect())
            except:
                pass


# Synchronous wrapper for compatibility with existing code
class QuotexWSAdapter:
    """
    Synchronous wrapper for QuotexPyQuotexAdapter
    Maintains compatibility with existing MarketDataFeed
    """
    
    def __init__(self, config=None):
        self.adapter = QuotexPyQuotexAdapter(config)
        self.connected = False
        self.sid = None
        self.loop = None
    
    def _get_loop(self):
        """Get or create event loop"""
        if self.loop is None:
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
        return self.loop
    
    def connect(self) -> bool:
        """Synchronous connect"""
        loop = self._get_loop()
        try:
            self.connected = loop.run_until_complete(self.adapter.connect())
            self.sid = "PYQUOTEX-CONNECTED" if self.connected else None
            return self.connected
        except Exception as e:
            print(f"[QUOTEX] Sync connect error: {e}")
            return False
    
    def get_candles(self, asset: str, timeframe_seconds: int = 60, count: int = 100, end_ts: int = None):
        """Synchronous get candles"""
        loop = self._get_loop()
        try:
            return loop.run_until_complete(
                self.adapter.get_candles(asset, timeframe_seconds, count, end_ts)
            )
        except Exception as e:
            print(f"[QUOTEX] Sync get_candles error: {e}")
            return None


if __name__ == "__main__":
    # Test the adapter
    async def test():
        print("="*60)
        print("   PYQUOTEX ADAPTER TEST")
        print("="*60)
        
        adapter = QuotexPyQuotexAdapter()
        
        # Test connection
        if await adapter.connect():
            print(f"✅ Connected | Balance: ${adapter.balance} ({adapter.account_type})")
            
            # Test candles
            candles = await adapter.get_candles("EURUSD", 60, 10)
            if candles:
                print(f"✅ Retrieved {len(candles)} candles")
            
            # Test price
            price = await adapter.get_realtime_price("EURUSD")
            if price:
                print(f"✅ EURUSD Price: {price}")
            
            await adapter.disconnect()
        else:
            print("❌ Connection failed")
    
    asyncio.run(test())
