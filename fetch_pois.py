import urllib.request
import json

bbox = '13.090,80.280,13.120,80.302' # Royapuram & George Town North
query = f"""[out:json][timeout:30];
(
  node["amenity"="place_of_worship"]({bbox});
  way["amenity"="place_of_worship"]({bbox});
  node["tourism"~"hotel|guest_house"]({bbox});
  node["amenity"~"restaurant|cafe|fast_food|hotel"]({bbox});
  node["railway"~"station|subway_entrance|halt"]({bbox});
  way["railway"="station"]({bbox});
  node["amenity"~"hospital|college|school|marketplace"]({bbox});
  way["amenity"~"hospital|college|school|marketplace"]({bbox});
);
out center;
"""

endpoints = [
  'https://maps.mail.ru/osm/tools/overpass/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter',
  'https://overpass-api.de/api/interpreter'
]

for ep in endpoints:
    print(f"Trying {ep}...")
    try:
        req = urllib.request.Request(
            ep, 
            data=query.encode('utf-8'), 
            headers={'User-Agent': 'Mozilla/5.0 AreaTwin/1.0'}
        )
        with urllib.request.urlopen(req, timeout=25) as res:
            data = json.loads(res.read().decode('utf-8'))
            elements = data.get('elements', [])
            print(f"SUCCESS with {ep}! Downloaded {len(elements)} POI elements.")
            with open('c:/Users/SAAQIB/areatwin/osm_pois_raw.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            break
    except Exception as e:
        print(f"Failed {ep}: {e}")
