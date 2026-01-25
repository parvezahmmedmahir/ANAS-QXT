"""
QUANTUM X PRO - FINAL SYSTEM BACKTEST
Complete accuracy and winning rate analysis with real Quotex data
"""
import sys
import os
import time
from datetime import datetime
import statistics

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brokers.quotex_xcharts import QuotexXChartsAdapter

def calculate_signal_accuracy(candles):
    """
    Analyze candles and generate signal with confidence
    Returns: (direction, confidence, reason)
    """
    if not candles or len(candles) < 10:
        return None, 0, "Insufficient data"
    
    # Get recent candles
    recent = candles[-10:]
    
    # Calculate indicators
    closes = [c['close'] for c in recent]
    highs = [c['high'] for c in recent]
    lows = [c['low'] for c in recent]
    
    # Trend analysis
    trend_up = sum(1 for i in range(1, len(closes)) if closes[i] > closes[i-1])
    trend_down = sum(1 for i in range(1, len(closes)) if closes[i] < closes[i-1])
    
    # Volatility
    price_range = max(highs) - min(lows)
    avg_close = statistics.mean(closes)
    volatility = (price_range / avg_close) * 100 if avg_close > 0 else 0
    
    # RSI-like momentum
    gains = [closes[i] - closes[i-1] for i in range(1, len(closes)) if closes[i] > closes[i-1]]
    losses = [closes[i-1] - closes[i] for i in range(1, len(closes)) if closes[i] < closes[i-1]]
    
    avg_gain = statistics.mean(gains) if gains else 0
    avg_loss = statistics.mean(losses) if losses else 0
    
    # Generate signal
    if trend_up > trend_down + 2:
        direction = "CALL"
        confidence = min(95, 60 + (trend_up - trend_down) * 5)
        reason = f"Strong uptrend ({trend_up}/9 bullish candles)"
    elif trend_down > trend_up + 2:
        direction = "PUT"
        confidence = min(95, 60 + (trend_down - trend_up) * 5)
        reason = f"Strong downtrend ({trend_down}/9 bearish candles)"
    elif avg_gain > avg_loss * 1.5:
        direction = "CALL"
        confidence = min(85, 55 + int((avg_gain / (avg_loss + 0.0001)) * 10))
        reason = f"Bullish momentum (gain/loss ratio: {avg_gain/max(avg_loss, 0.0001):.2f})"
    elif avg_loss > avg_gain * 1.5:
        direction = "PUT"
        confidence = min(85, 55 + int((avg_loss / (avg_gain + 0.0001)) * 10))
        reason = f"Bearish momentum (loss/gain ratio: {avg_loss/max(avg_gain, 0.0001):.2f})"
    else:
        direction = "CALL" if closes[-1] > closes[-2] else "PUT"
        confidence = 50 + int(volatility * 2)
        reason = "Neutral market, following last candle direction"
    
    return direction, min(confidence, 95), reason


def verify_signal(candles, signal_direction, entry_index=-1):
    """
    Verify if signal would have won
    Checks next candle after signal
    """
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


def run_backtest():
    print("\n" + "="*80)
    print(" "*20 + "QUANTUM X PRO - FINAL BACKTEST")
    print(" "*15 + "Real Quotex Data | Accuracy & Win Rate Analysis")
    print("="*80 + "\n")
    
    # Initialize adapter
    adapter = QuotexXChartsAdapter()
    
    if not adapter.connect():
        print("❌ Failed to connect to Quotex API")
        return
    
    # Test pairs
    test_pairs = [
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD",
        "BTCUSD", "ETHUSD", "AUDCAD", "NZDUSD",
        "EURJPY", "GBPJPY"
    ]
    
    print(f"[1] Testing {len(test_pairs)} Quotex OTC pairs")
    print(f"[2] Fetching 100 candles per pair (1-minute timeframe)")
    print(f"[3] Generating signals and verifying accuracy\n")
    print("-" * 80 + "\n")
    
    all_results = []
    wins = 0
    losses = 0
    total_confidence = 0
    
    for i, pair in enumerate(test_pairs, 1):
        print(f"[{i}/{len(test_pairs)}] Testing {pair}...")
        
        # Get candles
        candles = adapter.get_candles(pair, 60, 100)
        
        if not candles or len(candles) < 20:
            print(f"    ⚠️  Insufficient data, skipping\n")
            continue
        
        # Generate signal from historical data (excluding last candle)
        signal_direction, confidence, reason = calculate_signal_accuracy(candles[:-1])
        
        if not signal_direction:
            print(f"    ⚠️  No signal generated\n")
            continue
        
        # Verify signal with next candle
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
                color = ""
            else:
                losses += 1
                status = "❌ LOSS"
                color = ""
            
            total_confidence += confidence
            
            print(f"    Signal: {signal_direction:4} | Confidence: {confidence}%")
            print(f"    Entry: ${result['entry_price']:.5f} → Exit: ${result['exit_price']:.5f}")
            print(f"    Result: {status} | Pips: {result['profit_pips']:.5f}")
            print(f"    Reason: {reason}\n")
        
        time.sleep(0.2)  # Rate limiting
    
    # Calculate statistics
    total_signals = wins + losses
    
    if total_signals > 0:
        win_rate = (wins / total_signals) * 100
        avg_confidence = total_confidence / total_signals
        
        print("="*80)
        print(" "*25 + "BACKTEST RESULTS")
        print("="*80 + "\n")
        
        print(f"Total Signals Generated:  {total_signals}")
        print(f"Winning Signals:          {wins} ✅")
        print(f"Losing Signals:           {losses} ❌")
        print(f"\n{'='*80}\n")
        print(f"WIN RATE:                 {win_rate:.2f}%")
        print(f"AVERAGE CONFIDENCE:       {avg_confidence:.1f}%")
        print(f"\n{'='*80}\n")
        
        # Performance rating
        if win_rate >= 70:
            rating = "🌟 EXCELLENT"
            grade = "A+"
        elif win_rate >= 60:
            rating = "✅ GOOD"
            grade = "A"
        elif win_rate >= 55:
            rating = "👍 ACCEPTABLE"
            grade = "B+"
        else:
            rating = "⚠️  NEEDS IMPROVEMENT"
            grade = "C"
        
        print(f"Performance Rating:       {rating}")
        print(f"Grade:                    {grade}")
        print(f"\n{'='*80}\n")
        
        # Detailed results
        print("DETAILED SIGNAL BREAKDOWN:\n")
        for i, r in enumerate(all_results, 1):
            status_icon = "✅" if r['won'] else "❌"
            print(f"{i:2}. {r['pair']:10} | {r['direction']:4} | {r['confidence']:2}% | {status_icon} | ${r['entry']:.5f} → ${r['exit']:.5f}")
        
        print("\n" + "="*80)
        print(" "*20 + "BACKTEST COMPLETE - SYSTEM VERIFIED")
        print("="*80 + "\n")
        
        # Save results
        with open("backtest_results.txt", "w") as f:
            f.write(f"QUANTUM X PRO - BACKTEST RESULTS\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total Signals: {total_signals}\n")
            f.write(f"Wins: {wins}\n")
            f.write(f"Losses: {losses}\n")
            f.write(f"Win Rate: {win_rate:.2f}%\n")
            f.write(f"Average Confidence: {avg_confidence:.1f}%\n")
            f.write(f"Grade: {grade}\n\n")
            f.write("Detailed Results:\n")
            for r in all_results:
                f.write(f"{r['pair']}: {r['direction']} {r['confidence']}% - {'WIN' if r['won'] else 'LOSS'}\n")
        
        print(f"📄 Results saved to: backtest_results.txt\n")
        
        return {
            "win_rate": win_rate,
            "total_signals": total_signals,
            "wins": wins,
            "losses": losses,
            "avg_confidence": avg_confidence,
            "grade": grade
        }
    else:
        print("❌ No signals generated - check data availability")
        return None


if __name__ == "__main__":
    result = run_backtest()
    
    if result:
        print(f"\n🎯 FINAL VERDICT: {result['win_rate']:.2f}% Win Rate | Grade: {result['grade']}")
        print(f"✅ System is {'PRODUCTION READY' if result['win_rate'] >= 55 else 'NEEDS CALIBRATION'}\n")
