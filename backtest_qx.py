import sys
import os
import time
import json
import datetime

# Add current directory to path for imports
sys.path.append(os.getcwd())

try:
    from brokers.quotex_xcharts import QuotexMrBeastAdapter
    from engine.enhanced import EnhancedEngine
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def perform_backtest():
    print("="*80)
    print("   QUANTUM X PRO - INSTITUTIONAL BACKTEST ENGINE V9.0")
    print("   Asset Source: Official Quotex Broker Bridge (mrbeaxt.site)")
    print("="*80 + "\n")

    adapter = QuotexMrBeastAdapter()
    engine = EnhancedEngine()
    
    # Load assets from markets.json
    try:
        with open('markets.json', 'r') as f:
            market_data = json.load(f)
            assets = [m['pair'] for m in market_data.get('markets', [])]
    except Exception as e:
        print(f"Error loading assets: {e}")
        return

    # Limiting to top 20 assets for speed in this report, or all if requested
    # We will test all to be thorough as requested
    results = []
    total_wins = 0
    total_signals = 0

    print(f"{'ASSET':20} | {'SIGNALS':8} | {'WINS':6} | {'LOSSES':6} | {'ACCURACY':8}")
    print("-" * 65)

    for asset in assets:
        # Fetch 100 historical candles
        # Note: We replace the name to match the API expectation in the adapter
        candles = adapter.get_candles(asset, count=100)
        
        if not candles or len(candles) < 30:
            print(f"{asset:20} | NO DATA")
            continue

        wins = 0
        losses = 0
        signals_count = 0

        # We use a sliding window: use 20 candles as history to predict the 21st
        # We can do this for the last 20 candles in the 100-count set
        for i in range(70, 99):
            history = candles[:i]
            target_candle = candles[i] # The "next" candle we are predicting for
            
            # Predict
            direction, confidence, strategy = engine.analyze("QUOTEX", asset, 1, candles=history)
            
            # Result Check
            # If CALL, we win if target_candle close > last history candle close
            last_price = history[-1]['close']
            target_price = target_candle['close']
            
            is_win = False
            if direction == "CALL" and target_price > last_price:
                is_win = True
            elif direction == "PUT" and target_price < last_price:
                is_win = True
            
            if is_win:
                wins += 1
            else:
                losses += 1
            
            signals_count += 1

        accuracy = (wins / signals_count * 100) if signals_count > 0 else 0
        print(f"{asset:20} | {signals_count:8} | {wins:6} | {losses:6} | {accuracy:7.1f}%")
        
        results.append({
            "asset": asset,
            "wins": wins,
            "signals": signals_count,
            "accuracy": accuracy
        })
        
        total_wins += wins
        total_signals += signals_count
        
        # Small delay to avoid API rate limiting
        time.sleep(0.05)

    if total_signals > 0:
        overall_accuracy = (total_wins / total_signals) * 100
        print("\n" + "="*80)
        print(f"   OVERALL BACKTEST ACCURACY: {overall_accuracy:.2f}%")
        print(f"   TOTAL SIGNALS PROCESSED: {total_signals}")
        print("="*80)
    else:
        print("\nNo signals were processed. Check API connectivity.")

if __name__ == "__main__":
    perform_backtest()
