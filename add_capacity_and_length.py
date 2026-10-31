import json
import math

with open('c:/Users/SAAQIB/areatwin/roads_graph_enriched.json', 'r', encoding='utf-8') as f:
    roads = json.load(f)

for r in roads:
    length_m = 0
    pts = r['p']
    for k in range(len(pts) - 1):
        dlat = (pts[k+1][0] - pts[k][0]) * 111000
        dlng = (pts[k+1][1] - pts[k][1]) * 111000 * math.cos(math.radians(pts[k][0]))
        length_m += math.hypot(dlat, dlng)
    
    r['len'] = round(length_m, 1)

    # Capacity (veh / hour)
    if r['t'] in ['primary', 'trunk']:
        cap = 2200 if r['w'] >= 6.0 else 1600
    elif r['t'] == 'secondary':
        cap = 1400
    elif r['t'] == 'tertiary':
        cap = 950
    elif r['sm']:
        cap = 300
    else:
        cap = 650
    
    r['cap'] = cap

with open('c:/Users/SAAQIB/areatwin/roads_graph_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(roads, f, separators=(',', ':'), ensure_ascii=False)

print("Updated roads_graph_enriched.json with len and cap!")
