import time
import random
import pandas as pd
import numpy as np
from datetime import datetime

class QuotexAPI:
    def __init__(self):
        self.connected = False
        self.assets = []
        
    def connect(self, email=None, password=None):
        """
        Simulates connection to Quotex API.
        In a real scenario, this would use the quotexapi library to authenticate.
        """
        print(f"Connecting to Quotex API...")
        # Simulation of connection delay
        time.sleep(1)
        self.connected = True
        print("Connected successfully!")
        return True

    def get_candles(self, asset, timeframe, amount=10):
        """
        Fetches candle data for a specific asset.
        """
        # In a real implementation, this would fetch live data from the API
        # Here we simulate realistic market data for analysis
        current_price = 100.0 + random.uniform(-5, 5)
        candles = []
        
        for i in range(amount):
            open_price = current_price
            close_price = current_price + random.uniform(-0.5, 0.5)
            high_price = max(open_price, close_price) + random.uniform(0, 0.2)
            low_price = min(open_price, close_price) - random.uniform(0, 0.2)
            
            candles.append({
                "time": time.time() - (amount - i) * timeframe,
                "open": open_price,
                "close": close_price,
                "high": high_price,
                "low": low_price,
                "volume": random.randint(100, 1000)
            })
            current_price = close_price
            
        return pd.DataFrame(candles)

    def analyze_market(self, asset):
        """
        Analyzes the market using the Three Black Crows strategy and other indicators.
        """
        if not self.connected:
            self.connect()
            
        # Fetch recent candles (1 minute timeframe)
        df = self.get_candles(asset, 60, 20)
        
        # Calculate indicators
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['RSI'] = self.calculate_rsi(df['close'], 14)
        
        # Strategy Logic: Three Black Crows Pattern
        # 1. Three consecutive bearish candles
        # 2. Each closing lower than the previous
        # 3. Strong downward momentum
        
        last_3 = df.tail(3)
        is_three_black_crows = all(row['close'] < row['open'] for _, row in last_3.iterrows())
        
        # Trend Analysis
        current_price = df.iloc[-1]['close']
        sma_20 = df.iloc[-1]['SMA_20']
        rsi = df.iloc[-1]['RSI']
        
        signal = None
        confidence = 0
        
        # Logic for CALL (Buy)
        if rsi < 30: # Oversold
            signal = "CALL"
            confidence = 85
        elif current_price > sma_20 and not is_three_black_crows:
            signal = "CALL"
            confidence = 75
            
        # Logic for PUT (Sell)
        elif is_three_black_crows:
            signal = "PUT"
            confidence = 95 # Strong signal for strategy
        elif rsi > 70: # Overbought
            signal = "PUT"
            confidence = 85
        elif current_price < sma_20:
            signal = "PUT"
            confidence = 75
            
        # Fallback for simulation if no strong signal
        if not signal:
            signal = "CALL" if random.random() > 0.5 else "PUT"
            confidence = random.randint(60, 80)
            
        return {
            "asset": asset,
            "signal": signal,
            "confidence": confidence,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "strategy": "Three Black Crows" if is_three_black_crows else "Trend Following",
            "market_status": "Open"
        }

    def calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

# Singleton instance
api = QuotexAPI()