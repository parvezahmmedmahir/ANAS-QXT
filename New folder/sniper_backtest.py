"""
QUANTUM X PRO - SNIPER BACKTEST (V2)
Testing 90%+ Win Rate Strategy
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from brokers.quotex_xcharts import QuotexXChartsAdapter
from quantum_signal_engine import QuantumSignalEngine

def verify_win(entry, exit_price, direction):
    return (exit_price > entry) if direction == "CALL" else (exit_price < entry)

def run_sniper_test():
    print("\n" + "="*80)
    print(" "*25 + "QUANTUM SNIPER MODE BACKTEST")
    print(" "*20 + "Target: 90%+ Accuracy | Strict Filtering")
    print("="*80 + "\n")
    
    adapter = QuotexXChartsAdapter()
    engine = QuantumSignalEngine()
    
    if not adapter.connect(): return

    # Top performing Golden Pairs + Majors
    pairs = ["CADCHF", "NZDCAD", "BTCUSD", "USDINR", "USDCAD", "EURUSD", "GBPUSD", "BA"]
    
    g_direct_wins = 0
    g_direct_losses = 0
    g_mtg1_wins = 0
    g_signals = 0
    
    for pair in pairs:
        candles = adapter.get_candles(pair, 60, 400) # 400 candles history
        if not candles or len(candles) < 200: continue
            
        p_wins = 0
        p_mtg = 0
        p_sigs = 0
        skip = 0
        
        for idx in range(50, len(candles)-2):
            if skip > 0: skip -= 1; continue
            
            window = candles[idx-50:idx+1]
            sig, conf, reason = engine.generate_signal(window)
            
            if sig:
                p_sigs += 1
                
                # Check Direct
                direct_win = verify_win(candles[idx]['close'], candles[idx+1]['close'], sig)
                if direct_win: 
                    p_wins += 1
                else:
                    # Check MTG-1
                    mtg_win = verify_win(candles[idx+1]['close'], candles[idx+2]['close'], sig)
                    if mtg_win:
                        p_mtg += 1
                        skip = 1
                
        if p_sigs > 0:
            acc = (p_wins + p_mtg)/p_sigs*100
            print(f"{pair:8} | Signals: {p_sigs:2} | Accuracy: {acc:.1f}% | Best Reason: Sniper")
            
            g_direct_wins += p_wins
            g_mtg1_wins += p_mtg
            g_signals += p_sigs
            
    print("\n" + "="*80)
    total_wins = g_direct_wins + g_mtg1_wins
    final_acc = (total_wins/g_signals*100) if g_signals else 0
    
    print(f"TOTAL SNIPER SIGNALS: {g_signals}")
    print(f"TOTAL WINS:           {total_wins}")
    print(f"FINAL ACCURACY:       {final_acc:.2f}%")
    print("="*80)
    
    with open("sniper_results.txt", "w") as f:
        f.write(f"SNIPER MODE RESULTS\nAccuracy: {final_acc:.2f}%\nSignals: {g_signals}")

if __name__ == "__main__":
    run_sniper_test()
