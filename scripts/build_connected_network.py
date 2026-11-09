import json
import math

with open('c:/Users/SAAQIB/areatwin/real_osm_roads.json', 'r', encoding='utf-8') as f:
    roads = json.load(f)

print(f"Total roads: {len(roads)}")

# Build spatial index of endpoints & vertices for fast adjacency
# Endpoints are pts[0] and pts[-1]
# An intersection occurs if endpoint of road A is within 20m of any endpoint/vertex of road B.

def dist_m(p1, p2):
    dlat = (p2[0] - p1[0]) * 111000
    dlng = (p2[1] - p1[1]) * 111000 * math.cos(math.radians(p1[0]))
    return math.hypot(dlat, dlng)

# Connect roads into graph
# For each road, road['conn_start'] = list of {roadIdx, atStart: bool}
# and road['conn_end'] = list of {roadIdx, atStart: bool}

connections = {i: {'start': [], 'end': []} for i in range(len(roads))}

# Spatial buckets (cell size approx 50m)
bucket_size = 0.0005 # ~55m
buckets = {}

for idx, r in enumerate(roads):
    p_start = r['pts'][0]
    p_end = r['pts'][-1]
    
    b_start = (int(p_start[0] / bucket_size), int(p_start[1] / bucket_size))
    b_end = (int(p_end[0] / bucket_size), int(p_end[1] / bucket_size))
    
    buckets.setdefault(b_start, []).append((idx, True, p_start))
    buckets.setdefault(b_end, []).append((idx, False, p_end))

for idx, r in enumerate(roads):
    for is_start, pt in [(True, r['pts'][0]), (False, r['pts'][-1])]:
        b = (int(pt[0] / bucket_size), int(pt[1] / bucket_size))
        # Search 3x3 neighboring buckets
        for dbx in (-1, 0, 1):
            for dby in (-1, 0, 1):
                neigh_b = (b[0] + dbx, b[1] + dby)
                for o_idx, o_is_start, o_pt in buckets.get(neigh_b, []):
                    if o_idx == idx:
                        continue
                    if dist_m(pt, o_pt) <= 25.0: # within 25 meters -> connected intersection!
                        conn_key = 'start' if is_start else 'end'
                        connections[idx][conn_key].append({
                            'idx': o_idx,
                            'enterAtStart': o_is_start,
                            'dist': round(dist_m(pt, o_pt), 1)
                        })

# Attach connections to roads
for idx, r in enumerate(roads):
    r['next_at_start'] = connections[idx]['start']
    r['next_at_end'] = connections[idx]['end']

connected_roads = sum(1 for r in roads if len(r['next_at_start']) > 0 or len(r['next_at_end']) > 0)
print(f"Connected roads in network: {connected_roads} / {len(roads)} ({connected_roads/len(roads)*100:.1f}%)")

with open('c:/Users/SAAQIB/areatwin/real_osm_roads_connected.json', 'w', encoding='utf-8') as f:
    json.dump(roads, f, ensure_ascii=False)
print("Saved connected road network to c:/Users/SAAQIB/areatwin/real_osm_roads_connected.json")
