import urllib.request
import urllib.parse
import json
import os

bbox = "13.090,80.280,13.118,80.305"
query = f"""[out:json][timeout:30];
(
  way["highway"]({bbox});
);
out geom;"""

headers = {"User-Agent": "RoyapuramDigitalTwin/1.0"}

endpoints = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass-api.de/api/interpreter"
]

data = None
for ep in endpoints:
    try:
        print(f"Trying Overpass mirror: {ep}...")
        url = ep + "?data=" + urllib.parse.quote(query)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        print(f"Success from {ep}!")
        break
    except Exception as e:
        print(f"Failed {ep}: {e}")

if not data:
    raise RuntimeError("All Overpass endpoints failed")

elements = data.get("elements", [])
print(f"Total OSM roads/ways received: {len(elements)}")

# Filter and format roads for our 3D engine
valid_types = {
    "primary", "secondary", "tertiary", "residential", "unclassified",
    "trunk", "service", "living_street", "pedestrian"
}

formatted_roads = []
for el in elements:
    tags = el.get("tags", {})
    hw_type = tags.get("highway", "")
    if hw_type not in valid_types:
        continue
    geom = el.get("geometry", [])
    if len(geom) < 2:
        continue
    
    pts = [[pt["lat"], pt["lon"]] for pt in geom]
    name = tags.get("name:en") or tags.get("name") or f"{hw_type.capitalize()} Lane"
    
    # Capacity & base traffic heuristics by road hierarchy
    if hw_type in ["primary", "trunk"]:
        capacity = 2000
        traffic = 85
        width = 6.0
    elif hw_type in ["secondary", "tertiary"]:
        capacity = 1200
        traffic = 70
        width = 4.8
    elif hw_type in ["residential", "living_street"]:
        capacity = 500
        traffic = 45
        width = 3.6
    else:
        capacity = 300
        traffic = 30
        width = 3.0
        
    formatted_roads.append({
        "id": f"osm_{el['id']}",
        "name": name,
        "type": hw_type,
        "width": width,
        "capacity": capacity,
        "traffic": traffic,
        "busRoute": hw_type in ["primary", "secondary", "tertiary", "trunk"],
        "pts": pts
    })

print(f"Processed {len(formatted_roads)} driveable 3D roads/lanes across Royapuram!")
out_path = "c:/Users/SAAQIB/areatwin/royapuram_roads.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(formatted_roads, f, indent=2)

print(f"Saved to {out_path}")
