"""
QUANTUM X PRO - TARGETED BACKTEST
Testing ONLY verified working markets (28 pairs)
Target: Honest accuracy & winning rate assessment
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brokers.quotex_xcharts import QuotexXChartsAdapter
from quantum_signal_engine import QuantumSignalEngine

def verify_signal(candles, signal_direction, entry_index=-1):
    """Verify if signal would have won"""
    if not candles or len(candles) < abs(entry_index) + 2:
        return None
    
    entry_candle = candles[entry_index]
    next_candle = candles[entry_index + 1] if entry_index < -1 else candles[0]
    
    entry_price = entry_candle['close']
    exit_price = next_candle['close']
    
    if signal_direction == "CALL":
        won = exit_price > entry_price
    else:  # PUT
        won = exit_price < entry_price
    
    return {
        "won": won,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "direction": signal_direction
    }

def run_targeted_backtest():
    print("\n" + "="*80)
    print(" "*20 + "QUANTUM X PRO - VERIFIED MARKET BACKTEST")
    print(" "*15 + "Testing 28 Working Pairs | Accuracy & Win Rate Analysis")
    print("="*80 + "\n")
    
    adapter = QuotexXChartsAdapter()
    engine = QuantumSignalEngine()
    
    # Override engine settings for better signal frequency 
    # (The previous 75% was too strict, lowering slightly to 65% for ample data)
    engine.confidence_threshold = 65
    
    if not adapter.connect():
        print("❌ Failed to connect")
        return

    # ONLY THE WORKING PAIRS
    verified_pairs = [
        # Currencies (19)
        "AUDNZD", "USDEGP", "USDZAR", "EURSGD", "USDCOP", 
        "USDINR", "USDARS", "USDIDR", "USDMXN", "EURNZD", 
        "NZDCAD", "NZDCHF", "NZDJPY", "USDBDT", "USDDZD", 
        "AUDCAD", "CADCHF", "GBPNZD", "USDCAD",
        # Crypto (1)
        "BTCUSD",
        # Stocks (8)
        "BA", "AXP", "MCD", "INTC", "PFE", "FB", "MSFT", "JNJ"
    ]
    
    print(f"Target: Generate signals from {len(verified_pairs)} verified working pairs")
    print("Engine: Quantum Advanced (RSI, MACD, Trend, Patterns)")
    print("Confidence Threshold: 65%+\n")
    
    results = []
    wins = 0
    losses = 0
    
    for i, pair in enumerate(verified_pairs, 1):
        # Fetch significant history
        candles = adapter.get_candles(pair, 60, 300)
        
        if not candles or len(candles) < 100:
            print(f"[{i:2}/{len(verified_pairs)}] {pair:10} | ⚠️  Insufficient data")
            continue
            
        # Analyze historical signals (simulate backtest over last 200 minutes)
        pair_signals = 0
        pair_wins = 0
        
        # Scan through history
        for idx in range(50, len(candles)-2):
            # Take a window of 50 candles ending at idx
            window = candles[idx-50:idx+1]
            next_real_candle_idx = idx + 1
            
            signal, conf, reason = engine.generate_signal(window)
            
            if signal:
                # Verify result
                res = verify_signal(candles, signal, idx)
                if res:
                    pair_signals += 1
                    is_win = res['won']
                    
                    if is_win:
                        wins += 1
                        pair_wins += 1
                    else:
                        losses += 1
                    
                    results.append({
                        "pair": pair,
                        "signal": signal,
                        "conf": conf,
                        "won": is_win,
                        "reason": reason
                    })

        win_pct = (pair_wins/pair_signals*100) if pair_signals > 0 else 0
        print(f"[{i:2}/{len(verified_pairs)}] {pair:10} | Signals: {pair_signals:3} | Win Rate: {win_pct:5.1f}%")
        time.sleep(0.05)

    total_signals = wins + losses
    overall_win_rate = (wins/total_signals*100) if total_signals > 0 else 0
    
    print("\n" + "="*80)
    print(" "*30 + "FINAL RESULTS")
    print("="*80 + "\n")
    
    print(f"Total Signals:      {total_signals}")
    print(f"Total Wins:         {wins}")
    print(f"Total Losses:       {losses}")
    print(f"\nOVERALL WIN RATE:   {overall_win_rate:.2f}%")
    
    # Grading
    if overall_win_rate >= 80: grade = "A+"
    elif overall_win_rate >= 70: grade = "A"
    elif overall_win_rate >= 60: grade = "B"
    elif overall_win_rate >= 50: grade = "C"
    else: grade = "D"
    
    print(f"System Grade:       {grade}")
    print("\n" + "="*80)

    # Save details
    with open("verified_backtest_results.txt", "w") as f:
        f.write(f"QUANTUM X PRO - VERIFIED MARKET BACKTEST\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Overall Win Rate: {overall_win_rate:.2f}% ({wins}/{total_signals})\n\n")
        for r in results:
            status = "WIN" if r['won'] else "LOSS"
            f.write(f"{r['pair']}: {r['signal']} ({r['conf']}%) - {status} | {r['reason']}\n")

if __name__ == "__main__":
    run_targeted_backtest()
