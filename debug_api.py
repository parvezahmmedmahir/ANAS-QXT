import requests
import json

url = "https://mrbeaxt.site/Qx/Qx.php?pair=AUDCAD_otc&count=5"
try:
    resp = requests.get(url)
    print(f"Status: {resp.status_code}")
    print(f"Content: {resp.text}")
except Exception as e:
    print(f"Error: {e}")
