import json

with open('c:/Users/SAAQIB/areatwin/osm_royapuram_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

elements = data.get('elements', [])
target_names = ['New', 'Ramaswamy', 'Coral', 'Vinayagar', 'Venkata', 'Thambu', 'Linghi', 'Surya', 'Beach', 'Kamarajar']
matched = set()
for e in elements:
    name = e.get('tags', {}).get('name', '')
    for t in target_names:
        if t.lower() in name.lower():
            if name not in matched:
                matched.add(name)
                print(f"Found: {name} (type: {e.get('tags', {}).get('highway')}, pts: {len(e.get('geometry', []))})")
            break
print(f"Total matched unique streets: {len(matched)}")
