"""
Test xcharts.live API for ALL Quotex markets
Currencies, Crypto, Commodities, Stocks
"""
import requests
import time

def test_market(symbol):
    """Test if xcharts API has data for this market"""
    # The user specified URL pattern: https://xcharts.live/api/market/quotex/?symbol={SYMBOL}-OTCq&interval=1m&limit=600
    # We use limit=5 for faster testing
    url = f"https://xcharts.live/api/market/quotex/?symbol={symbol}-OTCq&interval=1m&limit=5"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'candles' in data and len(data['candles']) > 0:
                latest_price = data['candles'][-1]['close']
                return True, latest_price
        return False, None
    except:
        return False, None

# Test all markets
print("\n" + "="*80)
print(" "*20 + "XCHARTS API - COMPLETE MARKET TEST")
print("="*80 + "\n")

# Mapped based on user provided names to likely Quotex Tickers
markets = {
    "CURRENCIES (OTC)": [
        "AUDNZD", "USDBRL", "USDEGP", "USDZAR", "EURSGD",
        "USDCOP", "USDINR", "USDARS", "USDIDR", "USDMXN",
        "USDTRY", "EURNZD", "NZDCAD", "NZDCHF", "NZDJPY",
        "USDBDT", "USDDZD", "USDNGN", "USDPHP", "AUDCAD",
        "CADCHF", "GBPNZD", "USDCAD"
    ],
    "CRYPTO (OTC)": [
        "AVAXUSD", "BCHUSD", "GALAUSD", "HMSTRUSD", # Hamster Kombat might need verification
        "LINKUSD", "LTCUSD", "MANAUSD", "MELANIAUSD", # Melania Meme
        "SHIBUSD", "SOLUSD", "TIAUSD", "TONUSD", "TRUMPUSD",
        "TRXUSD", "XRPUSD", "ARBUSD", "ADAUSD", "BTCUSD",
        "DOGEUSD", "DASHUSD", "PEPEUSD", "FLOKIUSD", "ZECUSD",
        "DOTUSD", "ATOMUSD", "WIFUSD", "APTUSD", "AXSUSD",
        "BNBUSD", "ETHUSD", "BEAMUSD", "BONKUSD", "ETCUSD"
    ],
    "COMMODITIES (OTC)": [
        "UKBRENT", "XAUUSD", "USCRUDE", "XAGUSD"
    ],
    "STOCKS (OTC)": [
        "BA", "AXP", "MCD", "INTC",
        "PFE", "FB", "MSFT", "JNJ"
    ]
}

total_tested = 0
total_working = 0
results = {}

for category, symbols in markets.items():
    print(f"\n[{category}]")
    print("-" * 80)
    
    working = 0
    not_working = 0
    
    for symbol in symbols:
        total_tested += 1
        works, price = test_market(symbol)
        
        if works:
            working += 1
            total_working += 1
            print(f"  ✅ {symbol:15} | Price: ${price}")
        else:
            # Try alt format for crypto if failed (e.g. just BTC) - unlikely for Quotex OTC but possible
            not_working += 1
            print(f"  ❌ {symbol:15} | No data")
        
        time.sleep(0.1)  # Rate limiting
    
    results[category] = {
        "working": working,
        "not_working": not_working,
        "total": len(symbols)
    }
    
    print(f"\n  Summary: {working}/{len(symbols)} working ({(working/len(symbols)*100):.1f}%)\n")

# Final summary
print("\n" + "="*80)
print(" "*25 + "FINAL SUMMARY")
print("="*80 + "\n")

for category, stats in results.items():
    percentage = (stats['working'] / stats['total']) * 100
    status = "✅" if percentage == 100 else "⚠️" if percentage >= 50 else "❌"
    print(f"{status} {category:25} : {stats['working']:2}/{stats['total']:2} ({percentage:5.1f}%)")

overall_percentage = (total_working / total_tested) * 100
print(f"\n{'='*80}")
print(f"OVERALL: {total_working}/{total_tested} markets working ({overall_percentage:.1f}%)")
print(f"{'='*80}\n")
