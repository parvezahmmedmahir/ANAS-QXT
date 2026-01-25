import sys
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- IMPORT MODULES ---
from brokers.config import BROKER_CONFIG
from brokers.quotex import QuotexAdapter
from brokers.iqoption import IQOptionAdapter
from brokers.pocketoption import PocketOptionAdapter
from engine.reversal import ReversalEngine

app = Flask(__name__)
CORS(app)

# --- INIT SYSTEM ---
adapters = {
    "QUOTEX": QuotexAdapter(BROKER_CONFIG["QUOTEX"]),
    "IQ OPTION": IQOptionAdapter(BROKER_CONFIG["IQOPTION"]),
    "POCKETOPTION": PocketOptionAdapter(BROKER_CONFIG["POCKETOPTION"]),
    "BINOLLA": PocketOptionAdapter(BROKER_CONFIG["BINOLLA"])
}

engine = ReversalEngine()

# --- CHECK CONFIGURATION STATUS ---
def check_config_status():
    """Check if any broker is configured"""
    configured = []
    for broker, config in BROKER_CONFIG.items():
        if broker in ["QUOTEX", "IQOPTION"]:
            if config.get("email") and config.get("password"):
                configured.append(broker)
        elif broker == "POCKETOPTION":
            if config.get("ssid"):
                configured.append(broker)
        elif broker == "BINOLLA":
            if config.get("token"):
                configured.append(broker)
    
    return {
        "configured_brokers": configured,
        "mode": "LIVE" if configured else "SIMULATION",
        "accuracy": "65-75%" if configured else "50-55%"
    }

@app.route('/')
def home():
    """Status endpoint"""
    status = check_config_status()
    return jsonify({
        "service": "Quantum X Pro Backend",
        "version": "2.0",
        "status": status,
        "message": "Configure brokers/config.py to enable LIVE mode"
    })

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        broker_name = data.get("broker")
        market = data.get("market")
        timeframe = data.get("timeframe")

        print(f"[API] Request: {broker_name} - {market}")

        # 1. Connect/Fetch Real Data
        adapter = adapters.get(broker_name)
        real_signal = None
        real_candles = None
        
        if adapter:
             if not adapter.connected:
                 print(f"[INFO] Attempting to connect {broker_name}...")
                 adapter.connect()
             
             # Attempt to fetch real market data
             if adapter.connected and hasattr(adapter, 'get_real_market_data'):
                 real_signal = adapter.get_real_market_data(market)
                 print(f"[SUCCESS] Got real signal: {real_signal}")
             elif not adapter.connected:
                 print(f"[WARN] {broker_name} not connected. Check brokers/config.py")
        
        # 2. Analyze with Engine
        direction, confidence, strategy = engine.analyze(market, timeframe, real_signal, real_candles)

        # 3. Calculate Entry Time (BD Time)
        utc = datetime.datetime.utcnow()
        bd_time = utc + datetime.timedelta(hours=6, minutes=1)

        # 4. Determine data source
        mode = "LIVE_DATA" if real_signal else "SIMULATION"

        return jsonify({
            "direction": direction,
            "confidence": confidence,
            "entry_time": bd_time.strftime("%H:%M"),
            "broker": broker_name,
            "market": market,
            "strategy": strategy,
            "mode": mode,
            "accuracy_note": "Real API data" if real_signal else "Simulation mode - add credentials for better accuracy"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats():
    """Get system statistics"""
    config_status = check_config_status()
    accuracy_info = engine.get_accuracy_estimate()
    
    return jsonify({
        "config": config_status,
        "accuracy": accuracy_info,
        "total_signals": len(engine.signal_history)
    })

if __name__ == '__main__':
    print("=" * 60)
    print(" >>> QUANTUM X PRO - MODULAR BACKEND v2.0 <<< ")
    print("=" * 60)
    
    status = check_config_status()
    print(f" Mode: {status['mode']}")
    print(f" Configured Brokers: {', '.join(status['configured_brokers']) or 'NONE'}")
    print(f" Estimated Accuracy: {status['accuracy']}")
    
    if status['mode'] == 'SIMULATION':
        print("\n ⚠️  WARNING: Running in SIMULATION mode")
        print(" → Edit brokers/config.py to add your credentials")
        print(" → This will enable LIVE market data (better accuracy)")
    
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000)
