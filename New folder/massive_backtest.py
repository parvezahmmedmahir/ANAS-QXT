"""
QUANTUM X PRO - MASSIVE 600-CANDLE BACKTEST
Every Candle Signal Analysis
Direct Win | Direct Loss | MTG-1 Win | Accuracy
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brokers.quotex_xcharts import QuotexXChartsAdapter
from quantum_signal_engine import QuantumSignalEngine

def verify_win(entry_price, exit_price, direction):
    if direction == "CALL":
        return exit_price > entry_price
    else:
        return exit_price < entry_price

def run_massive_backtest():
    print("\n" + "="*80)
    print(" "*10 + "QUANTUM X PRO - MASSIVE EVERY-CANDLE BACKTEST")
    print(" "*15 + "600 Candle History | Continuous Signal Analysis")
    print("="*80 + "\n")
    
    adapter = QuotexXChartsAdapter()
    engine = QuantumSignalEngine()
    
    # We want signals on EVERY candle if possible, so we lower threshold to analyze flow
    # But still keep it reasonable to avoid noise. 
    # For "Every Candle" simulation, we process the loop continuously.
    engine.confidence_threshold = 55 
    
    if not adapter.connect():
        print("❌ Failed to connect")
        return

    # Verified working pairs only to ensure data integrity
    pairs = [
        "USDEGP", "USDCOP", "USDINR", "NZDCAD", 
        "CADCHF", "BA", "USDCAD", "USDARS", # Top performers
        "BTCUSD", "EURUSD", "GBPUSD" # Majors for volume
    ]
    
    print(f"Target: Analyze 600 candles history for {len(pairs)} pairs")
    print("Metrics: Direct Win | MTG-1 Win | Accuracy\n")
    
    # Global Stats
    g_direct_wins = 0
    g_direct_losses = 0
    g_mtg1_wins = 0
    g_total_losses = 0 # Loss after MTG-1
    g_total_signals = 0
    
    for i, pair in enumerate(pairs, 1):
        # Fetch MAX 600 candles
        candles = adapter.get_candles(pair, 60, 600)
        
        if not candles or len(candles) < 500:
            print(f"⚠️ {pair}: Insufficient history ({len(candles) if candles else 0})")
            continue
            
        p_direct_wins = 0
        p_direct_losses = 0
        p_mtg1_wins = 0
        p_signals = 0
        
        # Iterate through history
        # We need at least 50 candles for indicators
        # We stop 2 candles before end to verify MTG-1
        skip_steps = 0
        
        for idx in range(50, len(candles) - 2):
            if skip_steps > 0:
                skip_steps -= 1
                continue
                
            window = candles[idx-50:idx+1]
            signal, conf, _ = engine.generate_signal(window)
            
            if signal:
                p_signals += 1
                
                # Check Direct Result
                entry = candles[idx]['close']
                exit_direct = candles[idx+1]['close']
                
                is_direct_win = verify_win(entry, exit_direct, signal)
                
                if is_direct_win:
                    p_direct_wins += 1
                    # Win! Continue to next candle normally
                else:
                    p_direct_losses += 1
                    # Check MTG-1 (Next Candle)
                    mtg_entry = candles[idx+1]['close']
                    mtg_exit = candles[idx+2]['close']
                    
                    is_mtg_win = verify_win(mtg_entry, mtg_exit, signal)
                    
                    if is_mtg_win:
                        p_mtg1_wins += 1
                        skip_steps = 1 # Skip next candle analysis as we were trading MTG
                    else:
                        skip_steps = 1 # Skip anyway as we lost MTG
        
        # Pair stats
        total_p_losses = p_direct_losses - p_mtg1_wins
        acc_direct = (p_direct_wins/p_signals*100) if p_signals else 0
        acc_mtg = ((p_direct_wins + p_mtg1_wins)/p_signals*100) if p_signals else 0
        
        print(f"[{i:2}/{len(pairs)}] {pair:8} | Sig: {p_signals:3} | Dir: {acc_direct:4.1f}% | MTG-1: {acc_mtg:4.1f}%")
        
        # Add to global
        g_direct_wins += p_direct_wins
        g_direct_losses += p_direct_losses
        g_mtg1_wins += p_mtg1_wins
        g_total_losses += total_p_losses
        g_total_signals += p_signals
        
        time.sleep(0.1)

    # FINAL REPORT
    print("\n" + "="*80)
    print(" "*25 + "MASSIVE 600-CANDLE REPORT")
    print("="*80 + "\n")
    
    total_wins = g_direct_wins + g_mtg1_wins
    final_accuracy = (total_wins / g_total_signals * 100) if g_total_signals else 0
    direct_accuracy = (g_direct_wins / g_total_signals * 100) if g_total_signals else 0
    
    print(f"TOTAL SIGNALS ANALYZED:  {g_total_signals}\n")
    
    print(f"DIRECT WINS:             {g_direct_wins} ({direct_accuracy:.2f}%)")
    print(f"DIRECT LOSSES:           {g_direct_losses}")
    print(f"----------------------------------------")
    print(f"ONE STEP MTG WINS:       {g_mtg1_wins}")
    print(f"TOTAL LOSSES (After MTG):{g_total_losses}")
    print(f"----------------------------------------")
    print(f"\nFINAL ACCURACY (Dir+MTG): {final_accuracy:.2f}%")
    
    print("\n" + "="*80)
    
    # Save
    with open("massive_backtest.txt", "w") as f:
        f.write(f"MASSIVE BACKTEST - {datetime.now()}\n")
        f.write(f"Signals: {g_total_signals}\n")
        f.write(f"Direct Accuracy: {direct_accuracy:.2f}%\n")
        f.write(f"Final Accuracy (MTG-1): {final_accuracy:.2f}%\n")

if __name__ == "__main__":
    run_massive_backtest()
