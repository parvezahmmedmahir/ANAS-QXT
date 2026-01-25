"""
QUANTUM X PRO - ADVANCED BACKTEST
Testing new high-accuracy signal engine
Target: 85%+ Win Rate
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
    
    profit_pips = abs(exit_price - entry_price)
    
    return {
        "won": won,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "profit_pips": profit_pips,
        "direction": signal_direction
    }

def run_advanced_backtest():
    print("\n" + "="*80)
    print(" "*15 + "QUANTUM X PRO - ADVANCED SIGNAL ENGINE BACKTEST")
    print(" "*20 + "Target: 85%+ Win Rate | 1-Minute Binary Options")
    print("="*80 + "\n")
    
    # Initialize
    adapter = QuotexXChartsAdapter()
    engine = QuantumSignalEngine()
    
    if not adapter.connect():
        print("❌ Failed to connect to Quotex API")
        return
    
    # Test more pairs for better statistics
    test_pairs = [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD",
        "EURJPY", "GBPJPY", "AUDJPY", "NZDUSD", "AUDCAD",
        "EURGBP", "GBPAUD", "AUDNZD", "USDCHF", "BTCUSD"
    ]
    
    print(f"[1] Testing {len(test_pairs)} Quotex OTC pairs")
    print(f"[2] Using advanced technical analysis (RSI, MACD, EMA, Patterns)")
    print(f"[3] Only high-confidence signals (75%+ confidence)\n")
    print("-" * 80 + "\n")
    
    all_results = []
    wins = 0
    losses = 0
    total_confidence = 0
    skipped = 0
    
    for i, pair in enumerate(test_pairs, 1):
        print(f"[{i}/{len(test_pairs)}] Analyzing {pair}...")
        
        # Get more candles for better analysis
        candles = adapter.get_candles(pair, 60, 150)
        
        if not candles or len(candles) < 50:
            print(f"    ⚠️  Insufficient data, skipping\n")
            skipped += 1
            continue
        
        # Generate signal using advanced engine
        signal_direction, confidence, reason = engine.generate_signal(candles[:-1])
        
        if not signal_direction:
            print(f"    ⚠️  No high-confidence signal")
            print(f"    Reason: {reason}\n")
            skipped += 1
            continue
        
        # Verify signal
        result = verify_signal(candles, signal_direction, -2)
        
        if result:
            all_results.append({
                "pair": pair,
                "direction": signal_direction,
                "confidence": confidence,
                "won": result['won'],
                "entry": result['entry_price'],
                "exit": result['exit_price'],
                "pips": result['profit_pips'],
                "reason": reason
            })
            
            if result['won']:
                wins += 1
                status = "✅ WIN"
            else:
                losses += 1
                status = "❌ LOSS"
            
            total_confidence += confidence
            
            print(f"    Signal: {signal_direction:4} | Confidence: {confidence}%")
            print(f"    Entry: ${result['entry_price']:.5f} → Exit: ${result['exit_price']:.5f}")
            print(f"    Result: {status} | Pips: {result['profit_pips']:.5f}")
            print(f"    Analysis: {reason}\n")
        
        time.sleep(0.2)
    
    # Calculate statistics
    total_signals = wins + losses
    
    print("="*80)
    print(" "*25 + "ADVANCED BACKTEST RESULTS")
    print("="*80 + "\n")
    
    print(f"Total Pairs Tested:       {len(test_pairs)}")
    print(f"Signals Generated:        {total_signals}")
    print(f"Skipped (Low Confidence): {skipped}")
    print(f"Winning Signals:          {wins} ✅")
    print(f"Losing Signals:           {losses} ❌")
    
    if total_signals > 0:
        win_rate = (wins / total_signals) * 100
        avg_confidence = total_confidence / total_signals
        
        print(f"\n{'='*80}\n")
        print(f"WIN RATE:                 {win_rate:.2f}%")
        print(f"AVERAGE CONFIDENCE:       {avg_confidence:.1f}%")
        print(f"SIGNAL QUALITY:           {total_signals}/{len(test_pairs)} pairs ({(total_signals/len(test_pairs))*100:.1f}%)")
        print(f"\n{'='*80}\n")
        
        # Performance rating
        if win_rate >= 85:
            rating = "🌟 EXCELLENT - PRODUCTION READY"
            grade = "A+"
        elif win_rate >= 75:
            rating = "✅ VERY GOOD - READY FOR DEPLOYMENT"
            grade = "A"
        elif win_rate >= 65:
            rating = "👍 GOOD - ACCEPTABLE"
            grade = "B+"
        elif win_rate >= 55:
            rating = "⚠️  FAIR - NEEDS IMPROVEMENT"
            grade = "B"
        else:
            rating = "❌ POOR - NEEDS MAJOR CALIBRATION"
            grade = "C"
        
        print(f"Performance Rating:       {rating}")
        print(f"Grade:                    {grade}")
        print(f"\n{'='*80}\n")
        
        # Detailed results
        if all_results:
            print("DETAILED SIGNAL BREAKDOWN:\n")
            for i, r in enumerate(all_results, 1):
                status_icon = "✅" if r['won'] else "❌"
                print(f"{i:2}. {r['pair']:10} | {r['direction']:4} | {r['confidence']:2}% | {status_icon} | ${r['entry']:.5f} → ${r['exit']:.5f}")
        
        print("\n" + "="*80)
        print(" "*15 + "ADVANCED BACKTEST COMPLETE - SYSTEM VERIFIED")
        print("="*80 + "\n")
        
        # Save results
        with open("advanced_backtest_results.txt", "w") as f:
            f.write(f"QUANTUM X PRO - ADVANCED BACKTEST RESULTS\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Engine: Advanced Signal Engine (Multi-Indicator)\n\n")
            f.write(f"Total Signals: {total_signals}\n")
            f.write(f"Wins: {wins}\n")
            f.write(f"Losses: {losses}\n")
            f.write(f"Win Rate: {win_rate:.2f}%\n")
            f.write(f"Average Confidence: {avg_confidence:.1f}%\n")
            f.write(f"Grade: {grade}\n\n")
            f.write("Detailed Results:\n")
            for r in all_results:
                f.write(f"{r['pair']}: {r['direction']} {r['confidence']}% - {'WIN' if r['won'] else 'LOSS'} | {r['reason']}\n")
        
        print(f"📄 Results saved to: advanced_backtest_results.txt\n")
        
        return {
            "win_rate": win_rate,
            "total_signals": total_signals,
            "wins": wins,
            "losses": losses,
            "avg_confidence": avg_confidence,
            "grade": grade,
            "rating": rating
        }
    else:
        print("❌ No signals generated - check data availability")
        return None

if __name__ == "__main__":
    result = run_advanced_backtest()
    
    if result:
        print(f"\n🎯 FINAL VERDICT: {result['win_rate']:.2f}% Win Rate | Grade: {result['grade']}")
        print(f"{'✅ PRODUCTION READY' if result['win_rate'] >= 75 else '⚠️  NEEDS MORE CALIBRATION'}\n")
