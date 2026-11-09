import urllib.request
import json
import time

key = "YOUR_GOOGLE_MAPS_API_KEY"
url = f"https://tile.googleapis.com/v1/3dtiles/root.json?key={key}"

print("Testing Map Tiles API with key...")
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print("SUCCESS! Map Tiles API is ENABLED and WORKING! Status:", resp.status)
        print("Root asset:", data.get("asset"))
except urllib.error.HTTPError as e:
    err_body = e.read().decode("utf-8")
    print(f"Status: {e.code}")
    try:
        err_json = json.loads(err_body)
        print("Reason:", err_json.get("error", {}).get("message"))
        print("Details:", err_json.get("error", {}).get("details", [{}])[0].get("reason"))
    except:
        print("Error body:", err_body)
