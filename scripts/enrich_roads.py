import json
import math

with open('c:/Users/SAAQIB/areatwin/roads_graph.json', 'r', encoding='utf-8') as f:
    roads = json.load(f)

print(f"Loaded {len(roads)} roads.")

# Load raw OSM to grab oneway tags
with open('c:/Users/SAAQIB/areatwin/osm_royapuram_raw.json', 'r', encoding='utf-8') as f:
    osm_raw = json.load(f)

osm_tag_map = {}
for e in osm_raw.get('elements', []):
    if e.get('type') == 'way':
        osm_tag_map[f"osm_{e.get('id')}"] = e.get('tags', {})

# Key low-lying depression hotspots in Royapuram (lat, lng, radius_m, depth_offset_m)
depressions = [
    {'name': 'Stanley Subway Underpass', 'lat': 13.0992, 'lng': 80.2872, 'radius': 70, 'basin_depth': -3.5},
    {'name': 'Royapuram ROB Descent Dip', 'lat': 13.1034, 'lng': 80.2936, 'radius': 60, 'basin_depth': -2.2},
    {'name': 'S. Madha Church St Low Basin', 'lat': 13.1068, 'lng': 80.2946, 'radius': 55, 'basin_depth': -2.5},
    {'name': 'Kasimedu Wharf Gate Basin', 'lat': 13.1128, 'lng': 80.2982, 'radius': 65, 'basin_depth': -2.8},
    {'name': 'Kalmandapam Market Dip', 'lat': 13.1045, 'lng': 80.2915, 'radius': 50, 'basin_depth': -2.0},
    {'name': 'Wall Tax / Basin Bridge Low Line', 'lat': 13.0980, 'lng': 80.2830, 'radius': 80, 'basin_depth': -3.0}
]

def dist_m(p1, p2):
    dlat = (p2[0] - p1[0]) * 111000
    dlng = (p2[1] - p1[1]) * 111000 * math.cos(math.radians(p1[0]))
    return math.hypot(dlat, dlng)

dead_ends = 0
small_streets = 0
oneway_count = 0
flooded_roads = 0

for r in roads:
    tags = osm_tag_map.get(r['id'], {})
    
    # 1. Oneway
    oneway_val = tags.get('oneway', 'no')
    name_lower = r['n'].lower()
    # George Town one-way rules
    is_oneway = oneway_val in ['yes', '1'] or ('thambu chetty' in name_lower or 'linghi chetty' in name_lower or 'armenian' in name_lower)
    r['ow'] = is_oneway # oneway bool
    
    # 2. Small street vs main road
    is_small = r['w'] <= 3.5 or r['t'] in ['living_street', 'service', 'residential'] and r['w'] < 4.0
    r['sm'] = is_small
    if is_small: small_streets += 1
    
    # 3. Dead end (cul-de-sac)
    is_dead_end = len(r['ns']) == 0 or len(r['ne']) == 0
    r['de'] = is_dead_end
    if is_dead_end: dead_ends += 1
    
    # 4. Elevation & Water Stagnation calculation
    # Base terrain elevation for Royapuram is approx 4 to 6 meters above sea level
    # Proximity to depressions lowers the elevation
    mid_idx = len(r['p']) // 2
    mid_pt = r['p'][mid_idx]
    
    base_elev = 5.2 - (mid_pt[1] - 80.280) * 8.0 # gently slopes toward sea (east)
    min_basin_elev = base_elev
    is_low_area = False
    
    for dep in depressions:
        d = dist_m(mid_pt, [dep['lat'], dep['lng']])
        if d < dep['radius']:
            # Inside stagnation basin!
            severity = 1.0 - (d / dep['radius'])
            drop = dep['basin_depth'] * severity
            min_basin_elev = min(min_basin_elev, base_elev + drop)
            is_low_area = True
            
    r['el'] = round(min_basin_elev, 2)
    r['low'] = is_low_area # Flag whether water stays here
    if is_low_area: flooded_roads += 1
    if is_oneway: oneway_count += 1

print(f"Summary: {len(roads)} total roads:")
print(f"- Small streets: {small_streets}")
print(f"- One-way streets: {oneway_count}")
print(f"- Dead ends (cul-de-sacs): {dead_ends}")
print(f"- Low-lying water stagnation roads: {flooded_roads}")

with open('c:/Users/SAAQIB/areatwin/roads_graph_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(roads, f, separators=(',', ':'), ensure_ascii=False)
print("Saved roads_graph_enriched.json successfully!")
