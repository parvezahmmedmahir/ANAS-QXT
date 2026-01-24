import subprocess
import json
import time
import threading
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class QuotexWSAdapter:
    def __init__(self, config=None):
        self.nodes = [
            "https://ws2.market-qx.trade",
            "https://ws.qxbroker.com",
            "https://ws.market-qx.trade"
        ]
        self.current_node = self.nodes[0]
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://qxbroker.com",
            "Referer": "https://qxbroker.com/en/trade",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
        }
        self.sid = None
        self.connected = False
        self.config = config or {}
        self.lock = threading.Lock()
        self.session = requests.Session()

    def connect(self):
        """Quantum Stealth Handshake: Bypasses Cloudflare via Node Rotation & Header Spoofing"""
        with self.lock:
            for node in self.nodes:
                self.current_node = node
                print(f"[QUOTEX-WS] Handshake Attempt: {node}")
                
                try:
                    timestamp = int(time.time() * 1000)
                    handshake_url = f"{node}/socket.io/?EIO=3&transport=polling&t={timestamp}"
                    
                    # Attempt 1: Direct Requests with Bypass (Ignore SSL for Cert Issues)
                    resp = self.session.get(handshake_url, headers=self.headers, timeout=10, verify=False)
                    output = resp.text
                    
                    if resp.status_code == 200 and "sid" in output:
                        if self._parse_sid(output):
                            print(f"[QUOTEX-WS] ✅ Handshake Successful via Node: {node}")
                            self.connected = True
                            return True

                    # Attempt 2: Fallback to Curl with -k (Insecure) flag
                    if "Just a moment" in output or resp.status_code == 403 or "SSLError" in str(output):
                        print(f"[QUOTEX-WS] ⚠️ SSL/CF Block on {node}. Using Insecure TLS Bridge...")
                        headers_curl = []
                        for k, v in self.headers.items():
                            headers_curl.extend(["-H", f"{k}: {v}"])
                        
                        cmd = ["curl", "-k", "-s", "-L"] + headers_curl + [handshake_url]
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                        if result.returncode == 0 and "sid" in result.stdout:
                            if self._parse_sid(result.stdout):
                                print(f"[QUOTEX-WS] ✅ SSL Tunnel Bypass Success on: {node}")
                                self.connected = True
                                return True
                    
                except Exception as e:
                    print(f"[QUOTEX-WS] Node {node} Error: {e}")
                    continue

            print("[QUOTEX-WS] ❌ Critical: All Handshake Nodes Blocked by Cloudflare. Fallback to Simulated Data.")
            self.connected = False
            return False

    def _parse_sid(self, output):
        try:
            json_start = output.find("{")
            json_end = output.rfind("}") + 1
            if json_start != -1 and json_end != -1:
                data = json.loads(output[json_start:json_end])
                self.sid = data.get("sid")
                return True
        except:
            pass
        return False

    def get_candles(self, asset, timeframe_seconds=60, count=20, end_ts=None):
        """
        Fetches candles from the WS host if connected.
        Note: This is a placeholder for actual data fetching via the authenticated session.
        The user specifically asked to use the curl handshake for connection.
        """
        if not self.connected:
            if not self.connect():
                return None

        # Implementation for fetching real candles from Quotex WS API would go here.
        # For now, we return None to allow fallback to simulation or other adapters
        # until the full WS protocol (v3) is implemented.
        return None

    def backtest(self, assets):
        """
        Performs a backtest of the connection across multiple assets.
        """
        results = {}
        print("[BACKTEST] Starting Connection Accuracy Assessment...")
        
        for asset in assets:
            if not self.connected:
                self.connect()
            
            # Use connection state as a metric of quality
            quality = "HIGH" if self.connected else "OFFLINE"
            # Return realistic status
            results[asset] = {
                "connected": self.connected,
                "win_rate": "Verify Live" if self.connected else "0.0%",
                "status": "Handshake OK" if self.connected else "Failed"
            }
            time.sleep(0.05)
            
        print("[BACKTEST] Assessment Complete.")
        return results

if __name__ == "__main__":
    # Test the connection directly
    adapter = QuotexWSAdapter()
    print("--- QUANTUM HANDSHAKE TEST ---")
    if adapter.connect():
        print("✅ SUCCESS: Cloudflare Bypass Active.")
        print(f"SID: {adapter.sid}")
    else:
        print("❌ FAILED: Still blocked or node down.")
