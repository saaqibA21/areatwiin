import json
import math

with open('c:/Users/SAAQIB/areatwin/real_osm_roads.json', 'r', encoding='utf-8') as f:
    roads = json.load(f)

def dist_m(p1, p2):
    dlat = (p2[0] - p1[0]) * 111000
    dlng = (p2[1] - p1[1]) * 111000 * math.cos(math.radians(p1[0]))
    return math.hypot(dlat, dlng)

def dist_to_segment(p, a, b):
    # vector a -> b
    ab_lat = (b[0] - a[0]) * 111000
    ab_lng = (b[1] - a[1]) * 111000 * math.cos(math.radians(a[0]))
    seg_len_sq = ab_lat**2 + ab_lng**2
    if seg_len_sq == 0:
        return dist_m(p, a), a, 0.0
    
    # vector a -> p
    ap_lat = (p[0] - a[0]) * 111000
    ap_lng = (p[1] - a[1]) * 111000 * math.cos(math.radians(a[0]))
    t = max(0.0, min(1.0, (ap_lat * ab_lat + ap_lng * ab_lng) / seg_len_sq))
    
    proj_lat = a[0] + (b[0] - a[0]) * t
    proj_lng = a[1] + (b[1] - a[1]) * t
    proj = [proj_lat, proj_lng]
    return dist_m(p, proj), proj, t

# For each road, store connections at start (pts[0]) and at end (pts[-1])
for idx, r in enumerate(roads):
    r['next_start'] = []
    r['next_end'] = []

# Search connections between all roads
for i, r1 in enumerate(roads):
    p_start = r1['pts'][0]
    p_end = r1['pts'][-1]
    
    for j, r2 in enumerate(roads):
        if i == j:
            continue
        # Check start of r1 against r2
        # against r2 start/end
        d_s_s = dist_m(p_start, r2['pts'][0])
        if d_s_s < 25.0:
            r1['next_start'].append({'idx': j, 'fwd': True})
        d_s_e = dist_m(p_start, r2['pts'][-1])
        if d_s_e < 25.0:
            r1['next_start'].append({'idx': j, 'fwd': False})
            
        # Check end of r1 against r2
        d_e_s = dist_m(p_end, r2['pts'][0])
        if d_e_s < 25.0:
            r1['next_end'].append({'idx': j, 'fwd': True})
        d_e_e = dist_m(p_end, r2['pts'][-1])
        if d_e_e < 25.0:
            r1['next_end'].append({'idx': j, 'fwd': False})

# Also handle T-junctions: if a road has no next_start or no next_end, check if it terminates onto the middle of any road
for i, r1 in enumerate(roads):
    if not r1['next_start']:
        p_start = r1['pts'][0]
        for j, r2 in enumerate(roads):
            if i == j: continue
            for s_idx in range(len(r2['pts']) - 1):
                d, _, _ = dist_to_segment(p_start, r2['pts'][s_idx], r2['pts'][s_idx+1])
                if d < 20.0:
                    r1['next_start'].append({'idx': j, 'fwd': True})
                    r1['next_start'].append({'idx': j, 'fwd': False})
                    break
            if r1['next_start']: break

    if not r1['next_end']:
        p_end = r1['pts'][-1]
        for j, r2 in enumerate(roads):
            if i == j: continue
            for s_idx in range(len(r2['pts']) - 1):
                d, _, _ = dist_to_segment(p_end, r2['pts'][s_idx], r2['pts'][s_idx+1])
                if d < 20.0:
                    r1['next_end'].append({'idx': j, 'fwd': True})
                    r1['next_end'].append({'idx': j, 'fwd': False})
                    break
            if r1['next_end']: break

connected = sum(1 for r in roads if r['next_start'] or r['next_end'])
both_connected = sum(1 for r in roads if r['next_start'] and r['next_end'])
print(f"Total: {len(roads)}, Connected: {connected} ({connected/len(roads)*100:.1f}%), Both Ends: {both_connected}")

# Deduplicate connections
for r in roads:
    seen_start = set()
    clean_start = []
    for c in r['next_start']:
        key = (c['idx'], c['fwd'])
        if key not in seen_start:
            seen_start.add(key)
            clean_start.append(c)
    r['next_start'] = clean_start

    seen_end = set()
    clean_end = []
    for c in r['next_end']:
        key = (c['idx'], c['fwd'])
        if key not in seen_end:
            seen_end.add(key)
            clean_end.append(c)
    r['next_end'] = clean_end

# Save compact version (only essential fields for high performance in JS)
compact_roads = []
for idx, r in enumerate(roads):
    compact_roads.append({
        'i': idx,
        'id': r['id'],
        'n': r['name'],
        't': r['type'],
        'w': r['width'],
        'b': r['busRoute'],
        'p': r['pts'],
        'ns': r['next_start'],
        'ne': r['next_end']
    })

with open('c:/Users/SAAQIB/areatwin/roads_graph.json', 'w', encoding='utf-8') as f:
    json.dump(compact_roads, f, separators=(',', ':'), ensure_ascii=False)

import os
file_size = os.path.getsize('c:/Users/SAAQIB/areatwin/roads_graph.json')
print(f"Saved roads_graph.json ({file_size / 1024:.1f} KB)")
