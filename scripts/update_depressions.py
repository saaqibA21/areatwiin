import json
import math

with open('c:/Users/SAAQIB/areatwin/roads_graph_enriched.json', 'r', encoding='utf-8') as f:
    roads = json.load(f)

# Depressions with realistic urban basin sizes
depressions = [
    {'name': 'Stanley Subway Underpass & Approach', 'lat': 13.0992, 'lng': 80.2872, 'radius': 140, 'max_depth_cm': 75},
    {'name': 'Royapuram ROB Descent Dip', 'lat': 13.1034, 'lng': 80.2936, 'radius': 120, 'max_depth_cm': 45},
    {'name': 'S. Madha Church St Low Basin', 'lat': 13.1068, 'lng': 80.2946, 'radius': 130, 'max_depth_cm': 50},
    {'name': 'Kasimedu Wharf Gate Runoff Basin', 'lat': 13.1128, 'lng': 80.2982, 'radius': 150, 'max_depth_cm': 40},
    {'name': 'Kalmandapam Market Dip', 'lat': 13.1045, 'lng': 80.2915, 'radius': 110, 'max_depth_cm': 42},
    {'name': 'Wall Tax Rd / Basin Bridge Low Line', 'lat': 13.0980, 'lng': 80.2830, 'radius': 160, 'max_depth_cm': 60}
]

def dist_m(p1, p2):
    dlat = (p2[0] - p1[0]) * 111000
    dlng = (p2[1] - p1[1]) * 111000 * math.cos(math.radians(p1[0]))
    return math.hypot(dlat, dlng)

low_count = 0
for r in roads:
    is_low = False
    max_stagnation_depth = 0
    basin_name = ""
    
    # Check all points of this road
    for pt in r['p']:
        for dep in depressions:
            d = dist_m(pt, [dep['lat'], dep['lng']])
            if d < dep['radius']:
                is_low = True
                depth = round(dep['max_depth_cm'] * (1.0 - d / dep['radius']))
                if depth > max_stagnation_depth:
                    max_stagnation_depth = depth
                    basin_name = dep['name']
    
    # Also: dead-end alleys with low slope accumulate trapped water!
    if r['de'] and r['sm']:
        is_low = True
        if max_stagnation_depth < 25:
            max_stagnation_depth = 25
            basin_name = "Cul-de-sac trapped runoff"

    r['low'] = is_low
    r['water_depth_cm'] = max_stagnation_depth
    r['basin'] = basin_name
    if is_low: low_count += 1

print(f"Total low-lying water stagnation roads: {low_count} / {len(roads)}")

with open('c:/Users/SAAQIB/areatwin/roads_graph_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(roads, f, separators=(',', ':'), ensure_ascii=False)
