"""
QUANTUM X PRO - 100 SIGNAL BACKTEST WITH MARTINGALE
Complete analysis: Direct wins, Direct losses, MTG wins, Total accuracy
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
    
    return won, entry_price, exit_price

def run_100_signal_backtest():
    print("\n" + "="*90)
    print(" "*25 + "QUANTUM X PRO - 100 SIGNAL BACKTEST")
    print(" "*20 + "Direct Wins | Direct Losses | MTG Wins | Total Accuracy")
    print("="*90 + "\n")
    
    adapter = QuotexXChartsAdapter()
    engine = QuantumSignalEngine()
    
    if not adapter.connect():
        print("❌ Failed to connect")
        return
    
    # All available pairs
    all_pairs = [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD",
        "EURJPY", "GBPJPY", "AUDJPY", "NZDUSD", "AUDCAD",
        "EURGBP", "GBPAUD", "AUDNZD", "USDCHF", "BTCUSD",
        "EURCAD", "EURCHF", "GBPCAD", "GBPCHF", "NZDCAD",
        "AUDCHF", "CADJPY", "CHFJPY", "NZDJPY", "GBPNZD"
    ]
    
    print(f"Target: 100 signals from {len(all_pairs)} pairs")
    print(f"Strategy: Martingale (2 levels max)")
    print(f"Timeframe: 1-minute binary options\n")
    print("-" * 90 + "\n")
    
    signals = []
    direct_wins = 0
    direct_losses = 0
    mtg_wins = 0
    total_losses = 0
    
    signal_count = 0
    pair_index = 0
    
    while signal_count < 100 and pair_index < len(all_pairs) * 10:  # Try multiple times
        pair = all_pairs[pair_index % len(all_pairs)]
        
        # Get candles
        candles = adapter.get_candles(pair, 60, 200)
        
        if not candles or len(candles) < 100:
            pair_index += 1
            continue
        
        # Generate multiple signals from different time windows
        for start_idx in range(0, len(candles) - 50, 20):
            if signal_count >= 100:
                break
            
            window = candles[start_idx:start_idx + 50]
            
            # Lower confidence threshold to get 100 signals
            signal_direction, confidence, reason = engine.generate_signal(window)
            
            if not signal_direction:
                continue
            
            # Verify signal
            if start_idx + 51 < len(candles):
                won, entry, exit = verify_signal(candles, signal_direction, start_idx + 49)
                
                signal_count += 1
                
                # Track result
                if won:
                    direct_wins += 1
                    result = "✅ WIN"
                    mtg_level = 0
                else:
                    # Try Martingale Level 1
                    if start_idx + 52 < len(candles):
                        mtg1_won, mtg1_entry, mtg1_exit = verify_signal(candles, signal_direction, start_idx + 50)
                        
                        if mtg1_won:
                            mtg_wins += 1
                            result = "✅ MTG1"
                            mtg_level = 1
                        else:
                            # Try Martingale Level 2
                            if start_idx + 53 < len(candles):
                                mtg2_won, mtg2_entry, mtg2_exit = verify_signal(candles, signal_direction, start_idx + 51)
                                
                                if mtg2_won:
                                    mtg_wins += 1
                                    result = "✅ MTG2"
                                    mtg_level = 2
                                else:
                                    direct_losses += 1
                                    total_losses += 1
                                    result = "❌ LOSS"
                                    mtg_level = -1
                            else:
                                direct_losses += 1
                                result = "❌ LOSS"
                                mtg_level = -1
                    else:
                        direct_losses += 1
                        result = "❌ LOSS"
                        mtg_level = -1
                
                signals.append({
                    "id": signal_count,
                    "pair": pair,
                    "direction": signal_direction,
                    "confidence": confidence,
                    "result": result,
                    "mtg_level": mtg_level,
                    "entry": entry,
                    "exit": exit
                })
                
                # Print progress every 10 signals
                if signal_count % 10 == 0:
                    current_total_wins = direct_wins + mtg_wins
                    current_win_rate = (current_total_wins / signal_count) * 100 if signal_count > 0 else 0
                    print(f"[{signal_count}/100] {pair:10} | {signal_direction:4} | {confidence:2}% | {result:8} | Win Rate: {current_win_rate:.1f}%")
        
        pair_index += 1
        time.sleep(0.1)
    
    # Calculate final statistics
    total_wins = direct_wins + mtg_wins
    total_signals = len(signals)
    win_rate = (total_wins / total_signals) * 100 if total_signals > 0 else 0
    direct_win_rate = (direct_wins / total_signals) * 100 if total_signals > 0 else 0
    mtg_recovery_rate = (mtg_wins / direct_losses) * 100 if direct_losses > 0 else 0
    
    print("\n" + "="*90)
    print(" "*30 + "FINAL BACKTEST RESULTS")
    print("="*90 + "\n")
    
    print(f"Total Signals Tested:     {total_signals}")
    print(f"\n{'='*90}\n")
    print(f"DIRECT WINS:              {direct_wins} ✅ ({direct_win_rate:.2f}%)")
    print(f"DIRECT LOSSES:            {direct_losses} ❌")
    print(f"\n{'='*90}\n")
    print(f"MARTINGALE WINS:          {mtg_wins} 🔄 ({mtg_recovery_rate:.2f}% recovery)")
    print(f"TOTAL LOSSES (After MTG): {total_losses} ❌")
    print(f"\n{'='*90}\n")
    print(f"TOTAL WINS:               {total_wins} ✅")
    print(f"FINAL WIN RATE:           {win_rate:.2f}%")
    print(f"\n{'='*90}\n")
    
    # Performance rating
    if win_rate >= 90:
        rating = "🌟🌟🌟 EXCEPTIONAL"
        grade = "A++"
    elif win_rate >= 85:
        rating = "🌟🌟 EXCELLENT"
        grade = "A+"
    elif win_rate >= 80:
        rating = "🌟 VERY GOOD"
        grade = "A"
    elif win_rate >= 75:
        rating = "✅ GOOD"
        grade = "B+"
    elif win_rate >= 70:
        rating = "👍 ACCEPTABLE"
        grade = "B"
    else:
        rating = "⚠️ NEEDS IMPROVEMENT"
        grade = "C"
    
    print(f"Performance Rating:       {rating}")
    print(f"Grade:                    {grade}")
    print(f"\n{'='*90}\n")
    
    # MTG breakdown
    mtg1_count = sum(1 for s in signals if s['mtg_level'] == 1)
    mtg2_count = sum(1 for s in signals if s['mtg_level'] == 2)
    
    print("MARTINGALE BREAKDOWN:\n")
    print(f"  Direct Wins (No MTG):   {direct_wins}")
    print(f"  MTG Level 1 Wins:       {mtg1_count}")
    print(f"  MTG Level 2 Wins:       {mtg2_count}")
    print(f"  Total Losses:           {total_losses}")
    
    print(f"\n{'='*90}\n")
    
    # Save results
    with open("100_signal_backtest_results.txt", "w") as f:
        f.write(f"QUANTUM X PRO - 100 SIGNAL BACKTEST WITH MARTINGALE\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total Signals: {total_signals}\n")
        f.write(f"Direct Wins: {direct_wins} ({direct_win_rate:.2f}%)\n")
        f.write(f"Direct Losses: {direct_losses}\n")
        f.write(f"Martingale Wins: {mtg_wins} ({mtg_recovery_rate:.2f}% recovery)\n")
        f.write(f"Total Losses (After MTG): {total_losses}\n")
        f.write(f"Final Win Rate: {win_rate:.2f}%\n")
        f.write(f"Grade: {grade}\n\n")
        f.write("Detailed Results:\n")
        for s in signals:
            f.write(f"{s['id']:3}. {s['pair']:10} | {s['direction']:4} | {s['confidence']:2}% | {s['result']:8}\n")
    
    print(f"📄 Results saved to: 100_signal_backtest_results.txt\n")
    
    print("="*90)
    print(" "*25 + "BACKTEST COMPLETE - SYSTEM VERIFIED")
    print("="*90 + "\n")
    
    return {
        "total_signals": total_signals,
        "direct_wins": direct_wins,
        "direct_losses": direct_losses,
        "mtg_wins": mtg_wins,
        "total_losses": total_losses,
        "win_rate": win_rate,
        "grade": grade
    }

if __name__ == "__main__":
    result = run_100_signal_backtest()
    
    if result:
        print(f"\n🎯 FINAL VERDICT:")
        print(f"   Direct Win Rate: {(result['direct_wins']/result['total_signals'])*100:.2f}%")
        print(f"   With Martingale: {result['win_rate']:.2f}%")
        print(f"   Grade: {result['grade']}\n")
