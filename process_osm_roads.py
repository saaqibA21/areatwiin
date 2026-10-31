import json
import math

with open('c:/Users/SAAQIB/areatwin/osm_royapuram_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

elements = data.get('elements', [])
print(f"Total raw elements: {len(elements)}")

valid_highways = {
    'primary', 'secondary', 'tertiary', 'residential', 
    'living_street', 'unclassified', 'trunk', 'trunk_link', 
    'primary_link', 'secondary_link', 'tertiary_link'
}

roads = []
node_to_ways = {} # (round_lat, round_lon) -> list of road indices

for e in elements:
    if e.get('type') != 'way':
        continue
    tags = e.get('tags', {})
    hw = tags.get('highway')
    if hw not in valid_highways:
        continue
    
    geom = e.get('geometry', [])
    if len(geom) < 2:
        continue
    
    pts = [[round(p['lat'], 6), round(p['lon'], 6)] for p in geom]
    
    # Calculate road length
    length_m = 0
    for i in range(len(pts) - 1):
        dlat = (pts[i+1][0] - pts[i][0]) * 111000
        dlng = (pts[i+1][1] - pts[i][1]) * 111000 * math.cos(math.radians(pts[i][0]))
        length_m += math.hypot(dlat, dlng)
    
    # Ignore tiny segments under 10 meters if not named
    name = tags.get('name', '')
    if length_m < 10 and not name:
        continue
    
    # Determine width and speed
    width = 3.5
    speed_kmh = 30
    if hw in ['primary', 'trunk']:
        width = 6.5
        speed_kmh = 50
    elif hw in ['secondary']:
        width = 5.5
        speed_kmh = 40
    elif hw in ['tertiary']:
        width = 4.5
        speed_kmh = 35
    elif hw in ['living_street']:
        width = 3.0
        speed_kmh = 20

    road_id = f"osm_{e.get('id')}"
    bus_route = hw in ['primary', 'secondary', 'tertiary'] or ('salai' in name.lower() or 'beach' in name.lower() or 'broadway' in name.lower())
    
    roads.append({
        'id': road_id,
        'osm_id': e.get('id'),
        'name': name if name else f"{hw.capitalize()} Road",
        'type': hw,
        'width': width,
        'speed_kmh': speed_kmh,
        'busRoute': bus_route,
        'pts': pts,
        'length_m': round(length_m, 1)
    })

print(f"Processed {len(roads)} drivable real road corridors!")

# Let's inspect how many named roads and total road length
named_count = sum(1 for r in roads if not r['name'].endswith('Road') or r['name'] != f"{r['type'].capitalize()} Road")
total_km = sum(r['length_m'] for r in roads) / 1000.0
print(f"Named roads: {named_count}, Total road network length: {total_km:.2f} km")

with open('c:/Users/SAAQIB/areatwin/real_osm_roads.json', 'w', encoding='utf-8') as f:
    json.dump(roads, f, indent=2, ensure_ascii=False)
print("Saved to c:/Users/SAAQIB/areatwin/real_osm_roads.json")
