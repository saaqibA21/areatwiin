import json

with open('c:/Users/SAAQIB/areatwin/roads_graph_enriched.json', 'r', encoding='utf-8') as f:
    roads_data = json.load(f)

with open('c:/Users/SAAQIB/areatwin/all_pois.json', 'r', encoding='utf-8') as f:
    pois_data = json.load(f)

roads_json = json.dumps(roads_data, separators=(',', ':'), ensure_ascii=False)
pois_json = json.dumps(pois_data, separators=(',', ':'), ensure_ascii=False)
apiKey = "AIzaSyBFzf4K4xzSL2bgBoGUgFUfHY6DxFwa7Ks"

print(f"Loaded {len(roads_data)} roads and {len(pois_data)} POIs.")
