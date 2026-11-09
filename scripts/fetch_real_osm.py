import urllib.request
import json

bbox = '13.090,80.280,13.120,80.302' # Royapuram bbox: minLat, minLon, maxLat, maxLon
query = f"""[out:json][timeout:30];
(
  way["highway"]["highway"~"primary|secondary|tertiary|residential|unclassified|living_street"]({bbox});
);
out geom;
"""

endpoints = [
  'https://overpass-api.de/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter',
  'https://maps.mail.ru/osm/tools/overpass/api/interpreter',
  'https://lz4.overpass-api.de/api/interpreter'
]

success = False
for ep in endpoints:
    print(f"Trying {ep}...")
    try:
        req = urllib.request.Request(
            ep, 
            data=query.encode('utf-8'), 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AreaTwin/1.0'}
        )
        with urllib.request.urlopen(req, timeout=25) as res:
            data = json.loads(res.read().decode('utf-8'))
            elements = data.get('elements', [])
            print(f"SUCCESS with {ep}! Downloaded {len(elements)} real road elements.")
            with open('c:/Users/SAAQIB/areatwin/osm_royapuram_raw.json', 'w', encoding='utf-8') as f:
                json.dump(data, f)
            success = True
            break
    except Exception as e:
        print(f"Failed {ep}: {e}")

if not success:
    print("Could not query Overpass endpoints.")
