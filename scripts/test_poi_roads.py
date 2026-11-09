import json
import math

with open('c:/Users/SAAQIB/areatwin/roads_graph.json', 'r', encoding='utf-8') as f:
    roads = json.load(f)

pois = [
  {'id':'poi_station', 'name':'Royapuram Railway Station', 'lat':13.1068, 'lng':80.2922, 'icon':'🚂', 'color':'#f59e0b', 'defaultVeh':90},
  {'id':'poi_harbour', 'name':'Kasimedu Fishing Harbour', 'lat':13.1140, 'lng':80.2982, 'icon':'🐟', 'color':'#0284c7', 'defaultVeh':130},
  {'id':'poi_metro', 'name':'Mannadi Metro Station', 'lat':13.0945, 'lng':80.2902, 'icon':'🚇', 'color':'#06b6d4', 'defaultVeh':150},
  {'id':'poi_stanley', 'name':'Stanley Medical College & Hospital', 'lat':13.0990, 'lng':80.2875, 'icon':'🏥', 'color':'#10b981', 'defaultVeh':100},
  {'id':'poi_amman', 'name':'Arulmigu Angalaparameshwari Temple', 'lat':13.1082, 'lng':80.2910, 'icon':'🛕', 'color':'#eab308', 'defaultVeh':65},
  {'id':'poi_subramania', 'name':'Subramania Swamy Temple', 'lat':13.1042, 'lng':80.2928, 'icon':'🛕', 'color':'#facc15', 'defaultVeh':50},
  {'id':'poi_stpeters', 'name':'St. Peter’s Church', 'lat':13.1030, 'lng':80.2942, 'icon':'⛪', 'color':'#818cf8', 'defaultVeh':40},
  {'id':'poi_stanthony', 'name':'St. Anthony’s Church', 'lat':13.1028, 'lng':80.2938, 'icon':'⛪', 'color':'#a78bfa', 'defaultVeh':35},
  {'id':'poi_theagaraya', 'name':'Sir Theagaraya College', 'lat':13.1010, 'lng':80.2878, 'icon':'🎓', 'color':'#14b8a6', 'defaultVeh':45},
  {'id':'poi_fire_temple', 'name':'Parsi Fire Temple (Agiary)', 'lat':13.1035, 'lng':80.2936, 'icon':'🔥', 'color':'#f97316', 'defaultVeh':25}
]

def dist_m(p1, p2):
    dlat = (p2[0] - p1[0]) * 111000
    dlng = (p2[1] - p1[1]) * 111000 * math.cos(math.radians(p1[0]))
    return math.hypot(dlat, dlng)

for poi in pois:
    # Find closest 5 road indices
    closest = []
    for r in roads:
        min_d = min(dist_m([poi['lat'], poi['lng']], pt) for pt in r['p'])
        closest.append((min_d, r['i'], r['n']))
    closest.sort()
    poi['nearest_roads'] = [c[1] for c in closest[:5]]
    print(f"{poi['name']}: closest roads: {[c[2] + f' ({c[0]:.0f}m)' for c in closest[:3]]}")

with open('c:/Users/SAAQIB/areatwin/pois_with_roads.json', 'w', encoding='utf-8') as f:
    json.dump(pois, f, indent=2, ensure_ascii=False)
