# Data-preparation scripts

One-off generators that were used to fetch and process the OpenStreetMap data behind the twin
(`fetch_*`, `build_*`, `process_*`, `enrich_*`) and the older single-file HTML builders
(`generate_*`, `build_*_twin.py`).

They are kept for provenance. Several still contain absolute paths from the original author's
machine (`c:/Users/SAAQIB/areatwin/...`), so edit the paths before re-running them. The app itself
does **not** depend on them: it reads `data/roads.json` and `data/pois.json` directly.

| Script | Purpose |
| --- | --- |
| `fetch_real_osm.py`, `fetch_roads.py`, `fetch_pois.py` | Download street geometry and places from OpenStreetMap |
| `process_osm_roads.py`, `build_connected_network.py`, `build_graph.py` | Clean the geometry and derive junction connectivity |
| `enrich_roads.py`, `add_capacity_and_length.py`, `update_depressions.py` | Add capacity, length, elevation and flood-basin attributes |
| `build_all_pois.py` | Assemble the 29 places of interest |
| `generate_*.py`, `build_*_twin.py` | Earlier HTML generators (Google Maps and Three.js editions) |
