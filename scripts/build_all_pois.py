import json
import math

with open('c:/Users/SAAQIB/areatwin/roads_graph_enriched.json', 'r', encoding='utf-8') as f:
    roads = json.load(f)

pois = [
    # --- KOVILS (TEMPLES) ---
    {"id": "kovil_angala", "name": "Arulmigu Angalaparameshwari Amman Temple", "category": "kovil", "icon": "🛕", "lat": 13.1082, "lng": 80.2910, "defaultVisitors": 650, "desc": "Famous Royapuram temple with major Friday & festival footfall."},
    {"id": "kovil_subramania", "name": "Arulmigu Subramania Swamy Temple", "category": "kovil", "icon": "🛕", "lat": 13.1042, "lng": 80.2928, "defaultVisitors": 480, "desc": "Historic temple on Surya Narayana Salai."},
    {"id": "kovil_salai_vinayagar", "name": "Salai Vinayagar Koil", "category": "kovil", "icon": "🛕", "lat": 13.1018, "lng": 80.2895, "defaultVisitors": 380, "desc": "Prominent neighborhood temple on Salai Vinayagar Koil St."},
    {"id": "kovil_kaligambal", "name": "Arulmigu Kaligambal Temple", "category": "kovil", "icon": "🛕", "lat": 13.0935, "lng": 80.2912, "defaultVisitors": 850, "desc": "Historic George Town temple visited by Chhatrapati Shivaji in 1677."},
    {"id": "kovil_kachaleeswarar", "name": "Kachaleeswarar Temple", "category": "kovil", "icon": "🛕", "lat": 13.0970, "lng": 80.2882, "defaultVisitors": 420, "desc": "18th-century Shiva temple in Armenian Street neighborhood."},
    {"id": "kovil_selvavinayagar", "name": "Sri Selvavinayagar Koil", "category": "kovil", "icon": "🛕", "lat": 13.1055, "lng": 80.2940, "defaultVisitors": 320, "desc": "Popular Ganesha kovil near Kalmandapam."},
    {"id": "kovil_venugopala", "name": "Sri Venugopalaswamy Temple", "category": "kovil", "icon": "🛕", "lat": 13.0995, "lng": 80.2890, "defaultVisitors": 350, "desc": "Traditional Vaishnavite shrine in North Chennai."},

    # --- HOTELS & RESTAURANTS ---
    {"id": "hotel_buhari", "name": "Buhari Hotel (Royapuram)", "category": "hotel", "icon": "🍽️", "lat": 13.1062, "lng": 80.2918, "defaultVisitors": 700, "desc": "Iconic Chennai restaurant famous for biryani and Chicken 65."},
    {"id": "hotel_seashell", "name": "Hotel Sea Shell (Beach Road)", "category": "hotel", "icon": "🦞", "lat": 13.1110, "lng": 80.2972, "defaultVisitors": 550, "desc": "Popular multi-cuisine & fresh seafood dining destination."},
    {"id": "hotel_sangeetha", "name": "Sangeetha Veg Restaurant (Mannadi)", "category": "hotel", "icon": "☕", "lat": 13.0950, "lng": 80.2905, "defaultVisitors": 620, "desc": "High footfall pure vegetarian restaurant & filter coffee hub."},
    {"id": "hotel_saravana", "name": "Hotel Saravana Bhavan (Parrys)", "category": "hotel", "icon": "🍛", "lat": 13.0930, "lng": 80.2918, "defaultVisitors": 780, "desc": "Major south Indian dining spot near High Court / Beach Rd."},
    {"id": "hotel_vinayaga_tea", "name": "Sri Vinayaga Tea & Cool Bar", "category": "hotel", "icon": "🍵", "lat": 13.1022, "lng": 80.2898, "defaultVisitors": 340, "desc": "Bustling local chai & snack spot on Salai Vinayagar Koil St."},
    {"id": "hotel_national", "name": "National Lodge & Residency", "category": "hotel", "icon": "🏨", "lat": 13.1005, "lng": 80.2872, "defaultVisitors": 260, "desc": "Historic transit lodge on Maniakara Choultry Road."},
    {"id": "hotel_royal_sandwich", "name": "Royal Sandwich & Snacks", "category": "hotel", "icon": "🥪", "lat": 13.1040, "lng": 80.2925, "defaultVisitors": 290, "desc": "Youth evening food hotspot near Kalmandapam."},

    # --- METROS ---
    {"id": "metro_mannadi", "name": "Mannadi Metro Station", "category": "metro", "icon": "🚇", "lat": 13.0945, "lng": 80.2902, "defaultVisitors": 1800, "desc": "Chennai Metro Blue Line underground station with dense commercial traffic."},
    {"id": "metro_washermanpet", "name": "Washermanpet Metro Station", "category": "metro", "icon": "🚇", "lat": 13.1065, "lng": 80.2825, "defaultVisitors": 2100, "desc": "Major Blue Line interchange terminus and suburban transit node."},
    {"id": "metro_highcourt", "name": "High Court Metro Station", "category": "metro", "icon": "🚇", "lat": 13.0910, "lng": 80.2885, "defaultVisitors": 2400, "desc": "Key transit hub connecting George Town legal & commercial district."},
    {"id": "metro_theagaraya", "name": "Sir Theagaraya College Metro", "category": "metro", "icon": "🚇", "lat": 13.1015, "lng": 80.2865, "defaultVisitors": 1300, "desc": "Subway stop serving colleges, hospitals, and residential wards."},

    # --- RAILWAY STATIONS ---
    {"id": "station_royapuram", "name": "Royapuram Railway Station", "category": "station", "icon": "🚂", "lat": 13.1068, "lng": 80.2922, "defaultVisitors": 1600, "desc": "Historic 1856 terminus; active suburban EMU station serving 40,000 daily commuters."},
    {"id": "station_washermanpet", "name": "Washermanpet Railway Station", "category": "station", "icon": "🚆", "lat": 13.1050, "lng": 80.2818, "defaultVisitors": 1400, "desc": "Suburban rail junction linking north Chennai lines."},
    {"id": "station_beach", "name": "Chennai Beach Junction", "category": "station", "icon": "🚉", "lat": 13.0940, "lng": 80.2965, "defaultVisitors": 3200, "desc": "Crucial terminal for MRTS & suburban lines, port cargo yards."},

    # --- IMPORTANT PLACES & LANDMARKS ---
    {"id": "place_harbour", "name": "Kasimedu Fishing Harbour", "category": "place", "icon": "🐟", "lat": 13.1140, "lng": 80.2982, "defaultVisitors": 2800, "desc": "Asia's premier fishing harbour with massive 4 AM to 11 AM seafood auction traffic."},
    {"id": "place_stanley", "name": "Stanley Medical College & Hospital", "category": "place", "icon": "🏥", "lat": 13.0990, "lng": 80.2875, "defaultVisitors": 2500, "desc": "Centuries-old medical teaching hospital with continuous emergency & OPD influx."},
    {"id": "place_theagaraya", "name": "Sir Theagaraya College", "category": "place", "icon": "🎓", "lat": 13.1010, "lng": 80.2878, "defaultVisitors": 950, "desc": "Historic arts and science college campus."},
    {"id": "place_stpeters", "name": "St. Peter's Church (Royapuram)", "category": "place", "icon": "⛪", "lat": 13.1030, "lng": 80.2942, "defaultVisitors": 450, "desc": "Heritage Gothic church built in 1829."},
    {"id": "place_stanthony", "name": "St. Anthony's Church", "category": "place", "icon": "⛪", "lat": 13.1028, "lng": 80.2938, "defaultVisitors": 520, "desc": "Prominent Catholic pilgrimage shrine with large Tuesday novena attendance."},
    {"id": "place_fire_temple", "name": "Parsi Fire Temple (Agiary)", "category": "place", "icon": "🔥", "lat": 13.1035, "lng": 80.2936, "defaultVisitors": 180, "desc": "Built in 1910; Chennai's only Zoroastrian sacred flame temple."},
    {"id": "place_market", "name": "Kalmandapam Market & Clock Tower", "category": "place", "icon": "🏪", "lat": 13.1048, "lng": 80.2918, "defaultVisitors": 1200, "desc": "Dense historic produce & meat marketplace."},
    {"id": "place_port_gate", "name": "Chennai Port Trust Zero Gate", "category": "place", "icon": "⚓", "lat": 13.1085, "lng": 80.2975, "defaultVisitors": 1100, "desc": "Heavy commercial trailer and logistics freight access."}
]

def dist_m(p1, p2):
    dlat = (p2[0] - p1[0]) * 111000
    dlng = (p2[1] - p1[1]) * 111000 * math.cos(math.radians(p1[0]))
    return math.hypot(dlat, dlng)

for p in pois:
    closest = []
    for r in roads:
        d = min(dist_m([p['lat'], p['lng']], pt) for pt in r['p'])
        closest.append((d, r['i'], r['n']))
    closest.sort()
    p['nearest_roads'] = [c[1] for c in closest[:6]]

print(f"Configured {len(pois)} comprehensive POIs across Kovils, Hotels, Metros, Stations, and Landmarks!")

with open('c:/Users/SAAQIB/areatwin/all_pois.json', 'w', encoding='utf-8') as f:
    json.dump(pois, f, indent=2, ensure_ascii=False)
