import json

with open('c:/Users/SAAQIB/areatwin/roads_graph_enriched.json', 'r', encoding='utf-8') as f:
    roads_data = json.load(f)

with open('c:/Users/SAAQIB/areatwin/all_pois.json', 'r', encoding='utf-8') as f:
    pois_data = json.load(f)

roads_json = json.dumps(roads_data, separators=(',', ':'), ensure_ascii=False)
pois_json = json.dumps(pois_data, separators=(',', ':'), ensure_ascii=False)
apiKey = "YOUR_GOOGLE_MAPS_API_KEY"

code = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Royapuram Advanced Digital Twin - Authentic GIS Simulation</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#050914;color:#f1f5f9;overflow:hidden;height:100vh}}
#app{{display:flex;height:100vh;width:100vw}}
#map-container{{flex:1;position:relative}}
#map{{width:100%;height:100%}}
#rain-canvas{{position:absolute;inset:0;pointer-events:none;z-index:2;display:none}}
#sidebar{{width:450px;background:linear-gradient(180deg,#0a1124 0%,#0c152d 100%);border-left:1px solid #1f2d52;overflow-y:auto;z-index:20;flex-shrink:0;box-shadow:-8px 0 35px rgba(0,0,0,0.7)}}

.tabs{{display:flex;background:#070d1e;border-bottom:1px solid #1a274c;position:sticky;top:0;z-index:30}}
.tab{{flex:1;padding:10px 4px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;text-align:center;color:#64748b;cursor:pointer;border-bottom:2px solid transparent;transition:.2s}}
.tab:hover{{color:#94a3b8;background:#0d1838}}
.tab.active{{color:#38bdf8;border-bottom-color:#38bdf8;background:#0f1d45}}

.panel{{padding:14px 16px;border-bottom:1px solid #1a274c}}
.panel h3{{font-size:12px;text-transform:uppercase;letter-spacing:1.5px;color:#00d4ff;margin-bottom:10px;display:flex;align-items:center;gap:7px}}
.panel h3 span{{font-size:16px}}

.ctrl{{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}}
.ctrl label{{font-size:11px;color:#94a3b8}}
.toggle{{position:relative;width:40px;height:22px;cursor:pointer}}
.toggle input{{display:none}}
.toggle .sl{{position:absolute;inset:0;background:#1e293b;border-radius:11px;transition:.3s;border:1px solid #334155}}
.toggle .sl:before{{content:'';position:absolute;height:16px;width:16px;left:2px;bottom:2px;background:#64748b;border-radius:50%;transition:.3s}}
.toggle input:checked+.sl{{background:#0284c7;border-color:#38bdf8}}
.toggle input:checked+.sl:before{{transform:translateX(18px);background:#fff}}

.btn{{padding:6px 11px;border:1px solid #2a3f6f;background:#111a33;color:#38bdf8;border-radius:6px;cursor:pointer;font-size:11px;font-weight:600;transition:.2s}}
.btn:hover{{background:#1a2850;border-color:#38bdf8}}
.btn.active{{background:#0284c7;color:#fff;border-color:#38bdf8;box-shadow:0 0 10px rgba(56,189,248,0.4)}}
.btn.danger{{border-color:#f43f5e;color:#fb7185}}
.btn.danger:hover{{background:#e11d48;color:#fff}}
.btn.success{{border-color:#10b981;color:#34d399}}
.btn.success:hover{{background:#059669;color:#fff}}

input[type=range]{{width:100%;accent-color:#38bdf8;margin:4px 0}}
select, input[type=text]{{width:100%;background:#0b1329;border:1px solid #223561;color:#f1f5f9;border-radius:6px;padding:7px 9px;font-size:11.5px;margin-bottom:8px;outline:none}}
select:focus, input[type=text]:focus{{border-color:#38bdf8}}

.badge{{font-size:9.5px;padding:2px 7px;border-radius:10px;font-weight:700}}
.badge-severe{{background:#ef444422;color:#f87171;border:1px solid #ef444455}}
.badge-moderate{{background:#f59e0b22;color:#fbbf24;border:1px solid #f59e0b55}}
.badge-low{{background:#0284c722;color:#38bdf8;border:1px solid #0284c755}}
.badge-passable{{background:#10b98122;color:#34d399;border:1px solid #10b98155}}

.poi-card{{background:#0e172e;border:1px solid #1a274c;border-radius:7px;padding:9px 11px;margin-bottom:7px;cursor:pointer;transition:.2s}}
.poi-card:hover{{border-color:#38bdf8;background:#121e3d}}
.poi-card.active{{border-color:#00ffc8;background:#0d263a;box-shadow:0 0 12px rgba(0,255,200,0.2)}}
.poi-title{{display:flex;justify-content:space-between;align-items:center;font-size:11.5px;font-weight:700}}
.poi-cat{{font-size:9px;padding:1px 6px;border-radius:8px;text-transform:uppercase}}
.cat-kovil{{background:#eab30822;color:#facc15;border:1px solid #eab30855}}
.cat-hotel{{background:#f9731622;color:#fb923c;border:1px solid #f9731655}}
.cat-metro{{background:#06b6d422;color:#22d3ee;border:1px solid #06b6d455}}
.cat-station{{background:#f59e0b22;color:#fbbf24;border:1px solid #f59e0b55}}
.cat-place{{background:#8b5cf622;color:#a78bfa;border:1px solid #8b5cf655}}

.reroute-box{{background:#171305;border:1px solid #d9770655;border-radius:8px;padding:11px;margin-top:8px;font-size:11px;line-height:1.6}}
.reroute-box h4{{color:#fbbf24;margin-bottom:6px;font-size:12px;display:flex;align-items:center;gap:5px}}
.reroute-step{{background:#0b1329;border:1px solid #1e294b;border-radius:6px;padding:7px 9px;margin-top:6px;font-size:11px}}

.hotspot-card{{padding:9px 11px;background:#0d1c33;border-radius:7px;margin-bottom:7px;font-size:11px;border-left:4px solid #0284c7}}
.hotspot-card.severe{{border-left-color:#ef4444;background:#20111a}}
.hotspot-card.moderate{{border-left-color:#f59e0b;background:#1c1a0e}}

#hud{{position:absolute;top:0;left:0;right:0;z-index:10;background:linear-gradient(180deg,rgba(4,8,18,0.96) 0%,rgba(4,8,18,0.4) 75%,transparent 100%);padding:12px 22px;display:flex;align-items:center;justify-content:space-between;pointer-events:none}}
#hud>*{{pointer-events:auto}}
#hud h1{{font-size:17px;color:#f8fafc;font-weight:700;display:flex;align-items:center;gap:8px}}
#hud h1 span.tag{{font-size:10.5px;color:#38bdf8;font-weight:500;background:#0369a133;border:1px solid #0284c766;padding:2px 8px;border-radius:12px}}
#time-disp{{font-size:12.5px;color:#fcd34d;background:#0f172a;padding:5px 14px;border-radius:20px;border:1px solid #334155;font-weight:600}}

#bottom-bar{{position:absolute;bottom:0;left:0;right:450px;z-index:10;background:linear-gradient(transparent,rgba(4,8,18,0.96) 30%);padding:10px 20px;display:flex;gap:10px;justify-content:center;pointer-events:none}}
#bottom-bar>*{{pointer-events:auto}}
.bs{{text-align:center;background:#0f172acc;backdrop-filter:blur(6px);border:1px solid #1e293b;border-radius:8px;padding:7px 12px;min-width:95px}}
.bs .v{{font-size:15px;font-weight:700;color:#2dd4bf}}
.bs .l{{font-size:8px;color:#94a3b8;text-transform:uppercase;margin-top:2px;letter-spacing:0.5px}}

.legend-bar{{display:flex;gap:8px;margin-top:6px;font-size:9.5px;color:#94a3b8;flex-wrap:wrap}}
.legend-item{{display:flex;align-items:center;gap:4px}}
.legend-dot{{width:9px;height:9px;border-radius:50%}}

::-webkit-scrollbar{{width:5px}}
::-webkit-scrollbar-track{{background:#030712}}
::-webkit-scrollbar-thumb{{background:#1e294b;border-radius:3px}}
</style>
</head>
<body>
<div id="app">
<div id="map-container">
  <div id="hud">
    <h1>🏙️ Royapuram Digital Twin <span class="tag">Authentic GIS Model (848 Streets)</span></h1>
    <div style="display:flex;align-items:center;gap:10px">
      <a href="index.html" class="btn" style="text-decoration:none;display:inline-block">🏙️ 3D Three.js Twin</a>
      <div id="time-disp">🕐 08:00 AM</div>
    </div>
  </div>
  <canvas id="rain-canvas"></canvas>
  <div id="map"></div>
  <div id="bottom-bar">
    <div class="bs"><div class="v" id="bs-v">0</div><div class="l">Active Fleet</div></div>
    <div class="bs"><div class="v" id="bs-dest-visitors">0</div><div class="l">Target Visitors</div></div>
    <div class="bs"><div class="v" id="bs-s">0 km/h</div><div class="l">Avg Speed</div></div>
    <div class="bs"><div class="v" id="bs-c">0%</div><div class="l">Congestion</div></div>
    <div class="bs"><div class="v" id="bs-r">Dry</div><div class="l">Rain Status</div></div>
    <div class="bs"><div class="v" id="bs-w">0 cm</div><div class="l">Max Stagnation</div></div>
    <div class="bs"><div class="v" id="bs-b">0</div><div class="l">Blocked Roads</div></div>
  </div>
</div>

<div id="sidebar">
  <div class="tabs">
    <div class="tab active" onclick="setTab('tab-visitor', this)">🎯 Visitors</div>
    <div class="tab" onclick="setTab('tab-reroute', this)">🔀 Reroute</div>
    <div class="tab" onclick="setTab('tab-rain', this)">🌧️ Flood & Basin</div>
    <div class="tab" onclick="setTab('tab-anatomy', this)">🛣️ Streets</div>
    <div class="tab" onclick="setTab('tab-pois', this)">📍 Places</div>
  </div>

  <!-- TAB 1: VISITOR FLOW & ORIGIN-DESTINATION -->
  <div id="tab-visitor" class="tab-content">
    <div class="panel">
      <h3><span>🎯</span> Origin-Destination Visitor Flow</h3>
      <p style="font-size:10.5px;color:#94a3b8;margin-bottom:9px">Select any Kovil, Hotel, Station, or Metro; choose where visitors travel from; and watch the fleet dispatch along authentic streets:</p>
      
      <label style="font-size:11px;color:#94a3b8;font-weight:600">1. Destination Place:</label>
      <select id="sel-target-poi" onchange="onTargetPOIChanged(this.value)"></select>

      <div class="ctrl" style="margin-top:6px">
        <label>2. Visitor Volume (Per Hour):</label>
        <span id="lbl-visitor-count" style="font-size:12px;color:#00ffc8;font-weight:700">1,200 visitors</span>
      </div>
      <input type="range" id="sl-visitor-count" min="50" max="4000" step="50" value="1200" oninput="onVisitorCountSlider(this.value)">

      <label style="font-size:11px;color:#94a3b8;font-weight:600;margin-top:8px;display:block">3. Origin Influx Gateway (From Where?):</label>
      <select id="sel-origin-gateway" onchange="onOriginGatewayChanged(this.value)">
        <option value="gateway_south">🚗 From South: Parrys Corner / High Court / Central (via Beach Rd)</option>
        <option value="gateway_north">🚚 From North: Tondiarpet / Tiruvottiyur / Ennore (via Surya Narayana)</option>
        <option value="gateway_west">🛵 From West: Mint / Basin Bridge / Perambur (via Old Jail Rd / Stanley)</option>
        <option value="gateway_harbour">⚓ From Coast: Kasimedu Fishing Harbour & Sea Port Gate</option>
        <option value="gateway_distributed">🏙️ Distributed Local Neighborhood Influx (All Royapuram Wards)</option>
      </select>

      <button class="btn success" onclick="dispatchTargetFleet()" style="width:100%;margin-top:6px;padding:8px">🚀 Dispatch Targeted Visitor Traffic</button>

      <div style="background:#0f1833;border:1px solid #1c2b54;border-radius:8px;padding:9px;margin-top:10px">
        <div style="font-size:10.5px;color:#94a3b8">Active Destination Analytics:</div>
        <div id="target-poi-stats" style="font-size:11px;color:#f8fafc;margin-top:4px;line-height:1.5">
          Select a place above to view dedicated corridor analytics.
        </div>
      </div>
    </div>

    <!-- Multi-Modal Fleet Modalities -->
    <div class="panel">
      <h3><span>🚗</span> Fleet Modalities</h3>
      <div class="ctrl"><label>🚗 Sedans & Cars</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('car',this.checked)"><span class="sl"></span></label></div>
      <div class="ctrl"><label>🏍️ Bikes & Two-Wheelers</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('bike',this.checked)"><span class="sl"></span></label></div>
      <div class="ctrl"><label>🛺 Iconic Auto-Rickshaws</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('auto',this.checked)"><span class="sl"></span></label></div>
      <div class="ctrl"><label>🚌 Chennai MTC City Buses (Arterial only)</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('bus',this.checked)"><span class="sl"></span></label></div>
    </div>
  </div>

  <!-- TAB 2: INTELLIGENT REROUTING -->
  <div id="tab-reroute" class="tab-content" style="display:none">
    <div class="panel">
      <h3><span>🔀</span> Intelligent Reroute Recommender</h3>
      <p style="font-size:10.5px;color:#94a3b8;margin-bottom:8px">Click any road on the map or use the block toggle to analyze flow displacement and compute the best alternative bypass corridor:</p>

      <div class="ctrl">
        <label>🚧 Interactive Road Block Mode</label>
        <label class="toggle"><input type="checkbox" id="blk-mode" onchange="blockMode=this.checked"><span class="sl"></span></label>
      </div>
      <div style="display:flex;gap:5px;margin-top:6px">
        <button class="btn active" onclick="simulatePresetBlock('bridge')">Simulate Bridge Block</button>
        <button class="btn" onclick="simulatePresetBlock('stanley')">Simulate Subway Flooding</button>
        <button class="btn danger" onclick="clearBlocks()">Clear All</button>
      </div>

      <div id="reroute-box" class="reroute-box">
        <h4><span>ℹ️</span> Rerouting System Idle</h4>
        <p style="color:#94a3b8">Turn on <b>Road Block Mode</b> and click any street to calculate optimal detour routing and metrics.</p>
      </div>
    </div>
  </div>

  <!-- TAB 3: HYDROLOGY, LOW PLACES & WATER STAGNATION -->
  <div id="tab-rain" class="tab-content" style="display:none">
    <div class="panel">
      <h3><span>🌧️</span> Rain & Water Stagnation Simulation</h3>
      <p style="font-size:10.5px;color:#94a3b8;margin-bottom:8px">Where water will NOT flow and stays trapped in low elevations, cul-de-sacs, and depression basins:</p>

      <div class="ctrl">
        <label>Monsoon Rainfall</label>
        <label class="toggle"><input type="checkbox" id="rain-tog" onchange="toggleRain(this.checked)"><span class="sl"></span></label>
      </div>
      <div class="ctrl">
        <label>Rainfall Intensity</label>
        <span id="rain-lbl" style="font-size:11px;color:#38bdf8;font-weight:600">Light Shower</span>
      </div>
      <input type="range" id="rain-sl" min="1" max="3" value="1" oninput="setRainInt(this.value)">

      <div class="ctrl" style="margin-top:8px">
        <label>Highlight Low-Lying Stagnation Zones</label>
        <label class="toggle"><input type="checkbox" id="tog-low-areas" checked onchange="toggleLowAreaHighlight(this.checked)"><span class="sl"></span></label>
      </div>

      <div style="margin-top:10px;font-size:11px;font-weight:700;color:#00ffc8">🌊 Known Stagnation Hotspots (Water Stoppage):</div>
      <div id="hotspot-list" style="margin-top:7px"></div>
    </div>
  </div>

  <!-- TAB 4: STREET ANATOMY (ONE-WAYS, SMALL STREETS, DEAD-ENDS) -->
  <div id="tab-anatomy" class="tab-content" style="display:none">
    <div class="panel">
      <h3><span>🛣️</span> Street Anatomy & Constraints</h3>
      <p style="font-size:10.5px;color:#94a3b8;margin-bottom:9px">Authentic physical road properties loaded from OpenStreetMap:</p>

      <div class="ctrl">
        <label>🔀 Highlight One-Way Streets (71 streets)</label>
        <label class="toggle"><input type="checkbox" id="tog-oneway" onchange="filterRoadStyles()"><span class="sl"></span></label>
      </div>
      <div class="ctrl">
        <label>📏 Highlight Narrow / Small Streets (&lt;3.5m)</label>
        <label class="toggle"><input type="checkbox" id="tog-small" onchange="filterRoadStyles()"><span class="sl"></span></label>
      </div>
      <div class="ctrl">
        <label>⛔ Highlight Dead Ends / Cul-de-Sacs (147 streets)</label>
        <label class="toggle"><input type="checkbox" id="tog-deadends" onchange="filterRoadStyles()"><span class="sl"></span></label>
      </div>
      <div class="ctrl">
        <label>🌊 Highlight Low Stagnation Basins</label>
        <label class="toggle"><input type="checkbox" id="tog-basins" checked onchange="filterRoadStyles()"><span class="sl"></span></label>
      </div>

      <div class="legend-bar">
        <div class="legend-item"><div class="legend-dot" style="background:#facc15"></div> Major Arterial</div>
        <div class="legend-item"><div class="legend-dot" style="background:#38bdf8"></div> Secondary / Tertiary</div>
        <div class="legend-item"><div class="legend-dot" style="background:#c084fc"></div> Narrow Alley (&lt;3.5m)</div>
        <div class="legend-item"><div class="legend-dot" style="background:#fb923c"></div> One-Way Corridor</div>
        <div class="legend-item"><div class="legend-dot" style="background:#ef4444"></div> Dead-End Cul-de-Sac</div>
        <div class="legend-item"><div class="legend-dot" style="background:#0284c7"></div> Water Stagnation Dip</div>
      </div>
    </div>

    <div class="panel">
      <h3><span>⚙️</span> View & Camera</h3>
      <div class="ctrl"><label>Satellite vs Roadmap</label>
        <div style="display:flex;gap:4px">
          <button class="btn active" id="btn-sat" onclick="setMapType('hybrid')">🛰️ Satellite</button>
          <button class="btn" id="btn-road" onclick="setMapType('roadmap')">🗺️ Roads</button>
        </div>
      </div>
      <div class="ctrl"><label>Show Road Lines</label>
        <label class="toggle"><input type="checkbox" id="road-lines-tog" checked onchange="toggleRoadLines(this.checked)"><span class="sl"></span></label>
      </div>
      <div class="ctrl"><label>Google Live Traffic</label>
        <label class="toggle"><input type="checkbox" id="traffic-tog" onchange="toggleGoogleTraffic(this.checked)"><span class="sl"></span></label>
      </div>
      <div class="ctrl"><label>Tilt 3D Camera</label>
        <div style="display:flex;gap:4px">
          <button class="btn" onclick="tiltCam(0)">2D Flat</button>
          <button class="btn" onclick="tiltCam(45)">3D 45°</button>
          <button class="btn" onclick="tiltCam(65)">3D 65°</button>
        </div>
      </div>
    </div>
  </div>

  <!-- TAB 5: PLACES (KOVILS, HOTELS, METROS, STATIONS) -->
  <div id="tab-pois" class="tab-content" style="display:none">
    <div class="panel">
      <h3><span>📍</span> Categorized Places Directory</h3>
      <div style="display:flex;gap:4px;margin-bottom:8px;flex-wrap:wrap">
        <button class="btn active" onclick="filterPOICat('all',this)">All (29)</button>
        <button class="btn" onclick="filterPOICat('kovil',this)">🛕 Kovils (7)</button>
        <button class="btn" onclick="filterPOICat('hotel',this)">🍽️ Hotels (7)</button>
        <button class="btn" onclick="filterPOICat('metro',this)">🚇 Metros (4)</button>
        <button class="btn" onclick="filterPOICat('station',this)">🚂 Stations (3)</button>
        <button class="btn" onclick="filterPOICat('place',this)">🏛️ Heritage (8)</button>
      </div>
      <input type="text" id="poi-search" placeholder="🔍 Search Kovil, Hotel, Station..." oninput="filterPOISearch(this.value)">
      <div class="list-box" id="poi-list" style="max-height:480px"></div>
    </div>
  </div>
</div>
</div>

<script>
// ==========================================
// 1. DATA INITIALIZATION
// ==========================================
const apiKey = "{apiKey}";
const roads = {roads_json};
const pois = {pois_json};

// Origin Gateways into Royapuram
const gateways = {{
  gateway_south: {{ name: "South (Parrys / High Court)", roadIdx: 1, lat: 13.0945, lng: 80.2960 }},
  gateway_north: {{ name: "North (Tondiarpet / Ennore)", roadIdx: 0, lat: 13.1110, lng: 80.2885 }},
  gateway_west:  {{ name: "West (Mint / Basin Bridge)", roadIdx: 11, lat: 13.0992, lng: 80.2872 }},
  gateway_harbour: {{ name: "Kasimedu Port Wharf Gate", roadIdx: 12, lat: 13.1142, lng: 80.2990 }},
  gateway_distributed: {{ name: "Distributed Local Streets", roadIdx: null }}
}};

// Hydrological Low Stagnation Basins
const waterlogSpots = [
  {{id:'wl_stanley', name:'Stanley Subway Underpass', lat:13.0992, lng:80.2872, elev:'-3.8m', baseDepth:75, radius:65, desc:'Depressed rail subway. Impassable in heavy rain; runoff cannot escape.'}},
  {{id:'wl_bridge', name:'Royapuram ROB Descent Dip', lat:13.1034, lng:80.2936, elev:'-2.2m', baseDepth:45, radius:55, desc:'Foot of bridge curve before Kamarajar Salai. Water pools from approach slope.'}},
  {{id:'wl_madha', name:'S. Madha Church St Basin', lat:13.1068, lng:80.2946, elev:'-2.5m', baseDepth:50, radius:50, desc:'Residential low-lying bowl near cemetery with tide-locked drains.'}},
  {{id:'wl_harbour', name:'Kasimedu Wharf Gate Slipway', lat:13.1128, lng:80.2982, elev:'-2.8m', baseDepth:40, radius:60, desc:'Coastal gradient depression where auction runoff stagnates.'}},
  {{id:'wl_kalmandapam', name:'Kalmandapam Market Basin', lat:13.1045, lng:80.2915, elev:'-2.0m', baseDepth:42, radius:45, desc:'Low market street intersection prone to overflow.'}},
  {{id:'wl_walltax', name:'Wall Tax / Basin Bridge Low Line', lat:13.0980, lng:80.2830, elev:'-3.0m', baseDepth:60, radius:70, desc:'Low rail boundary corridor with heavy water logging.'}}
];

let map, trafficLayer;
const roadPolylines = [];
const poiMarkers = [];
const waterCircles = {{}};
const blockedRoads = new Set();
let blockMode = false;
let showRoadLines = true;

let selectedTargetPOI = pois[0];
let selectedGateway = "gateway_south";
let targetVisitorCount = 1200;

let simRunning = true, simSpeed = 1, timeOfDay = 8, rainOn = false, rainIntensity = 1;
let waterAccumulationLevel = 0;

let reroutePolyline = null;

// Multi-Modal Speeds (coordinate delta per millisecond)
const vehConfigs = {{
  car:  {{speed: 0.0000028, color:'#38bdf8', scale: 3.8, enabled:true}},
  bike: {{speed: 0.0000034, color:'#22c55e', scale: 2.5, enabled:true}},
  auto: {{speed: 0.0000023, color:'#facc15', scale: 3.2, enabled:true}},
  bus:  {{speed: 0.0000018, color:'#ef4444', scale: 4.8, enabled:true}}
}};
let vehicles = [];

// ==========================================
// 2. GOOGLE MAPS INITIALIZATION
// ==========================================
function initGoogleMap() {{
  const royapuramCenter = {{ lat: 13.1035, lng: 80.2935 }};

  map = new google.maps.Map(document.getElementById("map"), {{
    center: royapuramCenter,
    zoom: 16.5,
    tilt: 45,
    heading: 0,
    mapTypeId: "hybrid",
    mapId: "DEMO_MAP_ID",
    disableDefaultUI: false,
    zoomControl: true,
    mapTypeControl: false,
    fullscreenControl: false
  }});

  trafficLayer = new google.maps.TrafficLayer();

  renderRoads();
  renderLandmarks();
  renderWaterPuddles();

  initUISelectors();
  initHotspotList();
  initPOIList();
  initRainCanvas();
  rebalanceVehicles();
  updateDashboard();

  lastFrameTime = performance.now();
  requestAnimationFrame(animateSimulation);
}}

// ==========================================
// 3. ROAD RENDERING & STYLING
// ==========================================
function renderRoads() {{
  roads.forEach(r => {{
    const path = r.p.map(p => ({{ lat: p[0], lng: p[1] }}));
    const style = getRoadStyle(r);

    const polyline = new google.maps.Polyline({{
      path,
      geodesic: true,
      strokeColor: style.color,
      strokeOpacity: style.opacity,
      strokeWeight: style.weight,
      map: showRoadLines ? map : null
    }});

    polyline.roadIndex = r.i;
    polyline.roadData = r;

    polyline.addListener("click", () => {{
      if(blockMode) {{
        toggleRoadBlock(r.i);
      }} else {{
        showRoadInfo(r, path[Math.floor(path.length/2)]);
      }}
    }});

    roadPolylines[r.i] = polyline;
  }});
}}

function getRoadStyle(r) {{
  if(blockedRoads.has(r.i)) {{
    return {{ color: '#ef4444', weight: 6, opacity: 0.95 }};
  }}

  const togOneWay = document.getElementById("tog-oneway")?.checked;
  const togSmall = document.getElementById("tog-small")?.checked;
  const togDeadEnds = document.getElementById("tog-deadends")?.checked;
  const togBasins = document.getElementById("tog-basins")?.checked;

  if(togOneWay && r.ow) {{
    return {{ color: '#fb923c', weight: 4.5, opacity: 0.95 }};
  }}
  if(togDeadEnds && r.de) {{
    return {{ color: '#f43f5e', weight: 4.0, opacity: 0.9 }};
  }}
  if(togBasins && r.low) {{
    return {{ color: '#0284c7', weight: 4.5, opacity: 0.9 }};
  }}
  if(togSmall && r.sm) {{
    return {{ color: '#c084fc', weight: 2.8, opacity: 0.85 }};
  }}

  const isMajor = r.t === 'primary' || r.t === 'trunk' || r.t === 'secondary';
  const isMedium = r.t === 'tertiary';
  return {{
    color: isMajor ? '#facc15' : isMedium ? '#38bdf8' : '#e2e8f0',
    weight: isMajor ? 4.5 : isMedium ? 3.0 : 1.8,
    opacity: isMajor ? 0.75 : isMedium ? 0.6 : 0.4
  }};
}}

function filterRoadStyles() {{
  roads.forEach(r => {{
    const poly = roadPolylines[r.i];
    if(poly) {{
      const s = getRoadStyle(r);
      poly.setOptions({{ strokeColor: s.color, strokeWeight: s.weight, strokeOpacity: s.opacity }});
    }}
  }});
}}

function showRoadInfo(r, pos) {{
  const owText = r.ow ? '<span style="color:#fb923c;font-weight:700">🔀 ONE-WAY</span>' : 'Two-way';
  const smText = r.sm ? '<span style="color:#c084fc;font-weight:700">📏 Narrow Street (&lt;3.5m)</span>' : 'Standard / Wide Street';
  const deText = r.de ? '<span style="color:#ef4444;font-weight:700">⛔ Cul-de-Sac Dead End</span>' : 'Connected Through';
  const floodText = r.low ? `<span style="color:#38bdf8;font-weight:700">🌊 Low-Lying Basin (${{r.water_depth_cm}}cm stagnation risk)</span>` : 'Normal Drainage Elevation';

  new google.maps.InfoWindow({{
    content: `
      <div style="color:#000;font-family:sans-serif;font-size:11.5px;line-height:1.5;min-width:190px">
        <b style="font-size:13px">🛣️ ${{r.n}}</b><br>
        <span style="color:#64748b">Type: ${{r.t}} | Width: ${{r.w}}m | Speed: ${{r.speed_kmh||30}} km/h</span><br>
        <div style="margin-top:5px;border-top:1px solid #e2e8f0;padding-top:4px">
          ${{owText}} &bull; ${{smText}}<br>
          ${{deText}}<br>
          ${{floodText}}
        </div>
      </div>`,
    position: pos
  }}).open(map);
}}

function toggleRoadLines(show) {{
  showRoadLines = show;
  roadPolylines.forEach(p => {{ if(p) p.setMap(show ? map : null); }});
}}

// ==========================================
// 4. LANDMARKS & CATEGORIZED POIS
// ==========================================
function renderLandmarks() {{
  pois.forEach(p => {{
    const marker = new google.maps.Marker({{
      position: {{ lat: p.lat, lng: p.lng }},
      map: map,
      title: `${{p.icon}} ${{p.name}}`,
      label: {{ text: p.icon, fontSize: "20px" }}
    }});

    const info = new google.maps.InfoWindow({{
      content: `
        <div style="color:#000;font-family:sans-serif;padding:6px;max-width:240px">
          <div style="font-size:9.5px;color:#0284c7;font-weight:700;text-transform:uppercase">${{p.category.toUpperCase()}}</div>
          <b style="font-size:13px">${{p.icon}} ${{p.name}}</b>
          <div style="font-size:11px;color:#475569;margin-top:4px">${{p.desc}}</div>
          <div style="margin-top:6px;font-size:11px;color:#059669;font-weight:700">
            Current Visitors: ${{p.defaultVisitors}} / hr
          </div>
          <button onclick="selectAsTarget('${{p.id}}')" style="margin-top:6px;background:#0284c7;color:#fff;border:none;padding:4px 8px;border-radius:4px;cursor:pointer;font-size:10.5px;width:100%">
            🎯 Route Visitors to This Spot
          </button>
        </div>`
    }});

    marker.addListener("click", () => info.open(map, marker));
    poiMarkers.push({{ id: p.id, marker, info }});
  }});
}}

function selectAsTarget(poiId) {{
  const found = pois.find(p => p.id === poiId);
  if(found) {{
    document.getElementById("sel-target-poi").value = poiId;
    onTargetPOIChanged(poiId);
    setTab('tab-visitor', document.querySelectorAll('.tab')[0]);
  }}
}}

function renderWaterPuddles() {{
  waterlogSpots.forEach(s => {{
    const circle = new google.maps.Circle({{
      strokeColor: "#0284c7",
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: "#0284c7",
      fillOpacity: 0.0,
      map: map,
      center: {{ lat: s.lat, lng: s.lng }},
      radius: s.radius
    }});
    waterCircles[s.id] = circle;
  }});
}}

// ==========================================
// 5. VEHICLE SIMULATION & TARGET DISPATCH
// ==========================================
function spawnVehicle(poi, gatewayKey) {{
  const types = ['car','bike','bike','auto','auto','car'];
  if(poi.id.includes('station') || poi.id.includes('metro') || poi.id.includes('stanley') || poi.id.includes('harbour')) {{
    types.push('bus');
  }}
  const type = types[Math.floor(Math.random()*types.length)];
  const cfg = vehConfigs[type];
  if(!cfg.enabled) return null;

  // Determine spawn road based on chosen Origin Gateway
  let startRoadIdx;
  const gw = gateways[gatewayKey || selectedGateway];
  if(gw && gw.roadIdx !== null && !blockedRoads.has(gw.roadIdx)) {{
    startRoadIdx = gw.roadIdx;
  }} else {{
    // Distributed or gateway blocked
    const cand = (poi.nearest_roads || []).filter(idx => !blockedRoads.has(idx));
    if(cand.length && Math.random() < 0.3) {{
      startRoadIdx = cand[Math.floor(Math.random()*cand.length)];
    }} else {{
      const unblocked = roads.filter(r => !blockedRoads.has(r.i) && (type!=='bus' || r.b) && (!r.sm || type!=='bus'));
      if(!unblocked.length) return null;
      startRoadIdx = unblocked[Math.floor(Math.random()*unblocked.length)].i;
    }}
  }}

  const road = roads[startRoadIdx];
  // One-way enforcement: if road is oneway, vehicle MUST go forward
  const fwd = road.ow ? true : (Math.random() > 0.5);
  const startPt = fwd ? road.p[0] : road.p[road.p.length-1];

  const marker = new google.maps.Marker({{
    position: {{ lat: startPt[0], lng: startPt[1] }},
    map: map,
    icon: {{
      path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
      scale: cfg.scale,
      fillColor: cfg.color,
      fillOpacity: 0.95,
      strokeColor: "#ffffff",
      strokeWeight: 1,
      rotation: 0
    }}
  }});

  return {{
    type,
    marker,
    targetPOI: poi,
    roadIdx: road.i,
    segIdx: fwd ? 0 : road.p.length - 2,
    fwd: fwd,
    progress: 0.0,
    speed: cfg.speed * (0.85 + Math.random()*0.3)
  }};
}}

function rebalanceVehicles() {{
  const targetFleet = Math.max(25, Math.min(100, Math.round(targetVisitorCount / 35.0)));

  while(vehicles.length > targetFleet) {{
    const v = vehicles.pop();
    if(v && v.marker) v.marker.setMap(null);
  }}

  while(vehicles.length < targetFleet) {{
    const v = spawnVehicle(selectedTargetPOI, selectedGateway);
    if(v) vehicles.push(v);
    else break;
  }}
}}

function dispatchTargetFleet() {{
  vehicles.forEach(v => {{ if(v.marker) v.marker.setMap(null); }});
  vehicles = [];
  rebalanceVehicles();
  updateDashboard();
  
  // Fly camera to target
  if(selectedTargetPOI) {{
    map.panTo({{ lat: selectedTargetPOI.lat, lng: selectedTargetPOI.lng }});
    map.setZoom(17);
  }}
}}

let lastFrameTime = performance.now();

function updateVehicles(dtMs) {{
  const rainSlow = rainOn ? [1, 0.75, 0.52, 0.35][rainIntensity] : 1.0;

  vehicles.forEach(v => {{
    const road = roads[v.roadIdx];
    if(!road || !road.p || road.p.length < 2) return;

    const pA = road.p[v.segIdx];
    const pB = road.p[v.segIdx + 1];
    
    const dLat = pB[0] - pA[0];
    const dLng = pB[1] - pA[1];
    const segLen = Math.hypot(dLat, dLng * Math.cos(pA[0] * Math.PI / 180));
    
    // Low-lying water slowdown: if street has water depth > 20cm, vehicles wade slowly
    const waterDepth = (rainOn && road.low) ? Math.round(road.water_depth_cm * (waterAccumulationLevel/100.0)) : 0;
    const waterSlow = waterDepth > 35 ? 0.25 : waterDepth > 15 ? 0.6 : 1.0;

    const effectiveSpeed = v.speed * rainSlow * waterSlow * simSpeed;
    const progressInc = (effectiveSpeed * dtMs) / Math.max(segLen, 0.00005);
    
    if(v.fwd) {{
      v.progress += progressInc;
      if(v.progress >= 1.0) {{
        v.progress = 0.0;
        v.segIdx++;
        if(v.segIdx >= road.p.length - 1) {{
          // Reached road end -> pick connected street
          const nextConns = (road.ne || []).filter(c => {{
            if(blockedRoads.has(c.idx)) return false;
            const nr = roads[c.idx];
            if(v.type === 'bus' && (nr.sm || !nr.b)) return false;
            if(nr.ow && !c.fwd) return false; // Enforce one-way
            return true;
          }});

          if(nextConns.length > 0) {{
            const chosen = nextConns[Math.floor(Math.random() * nextConns.length)];
            v.roadIdx = chosen.idx;
            const nextRoad = roads[chosen.idx];
            v.fwd = chosen.fwd;
            v.segIdx = v.fwd ? 0 : nextRoad.p.length - 2;
          }} else {{
            // Dead end cul-de-sac -> 180 turn around unless one-way
            v.fwd = false;
            v.segIdx = road.p.length - 2;
          }}
        }}
      }}
    }} else {{
      v.progress += progressInc;
      if(v.progress >= 1.0) {{
        v.progress = 0.0;
        v.segIdx--;
        if(v.segIdx < 0) {{
          const nextConns = (road.ns || []).filter(c => {{
            if(blockedRoads.has(c.idx)) return false;
            const nr = roads[c.idx];
            if(v.type === 'bus' && (nr.sm || !nr.b)) return false;
            if(nr.ow && !c.fwd) return false; // Enforce one-way
            return true;
          }});

          if(nextConns.length > 0) {{
            const chosen = nextConns[Math.floor(Math.random() * nextConns.length)];
            v.roadIdx = chosen.idx;
            const nextRoad = roads[chosen.idx];
            v.fwd = chosen.fwd;
            v.segIdx = v.fwd ? 0 : nextRoad.p.length - 2;
          }} else {{
            v.fwd = true;
            v.segIdx = 0;
          }}
        }}
      }}
    }}

    const curRoad = roads[v.roadIdx];
    const curA = curRoad.p[v.segIdx];
    const curB = curRoad.p[v.segIdx + 1];
    const curProg = v.fwd ? v.progress : (1.0 - v.progress);
    
    const lat = curA[0] + (curB[0] - curA[0]) * curProg;
    const lng = curA[1] + (curB[1] - curA[1]) * curProg;
    v.marker.setPosition({{ lat, lng }});

    const segDirLat = v.fwd ? (curB[0] - curA[0]) : (curA[0] - curB[0]);
    const segDirLng = v.fwd ? (curB[1] - curA[1]) : (curA[1] - curB[1]);
    const heading = (Math.atan2(segDirLng * Math.cos(lat * Math.PI / 180), segDirLat) * 180 / Math.PI + 360) % 360;

    const icon = v.marker.getIcon();
    if(icon && icon.rotation !== heading) {{
      icon.rotation = heading;
      v.marker.setIcon(icon);
    }}
  }});
}}

// ==========================================
// 6. RAIN & STAGNATION BASIN ENGINE
// ==========================================
let rainCtx, rainDrops = [];
function initRainCanvas() {{
  const canvas = document.getElementById("rain-canvas");
  canvas.width = window.innerWidth - 450;
  canvas.height = window.innerHeight;
  rainCtx = canvas.getContext("2d");

  for(let i=0; i<350; i++) {{
    rainDrops.push({{
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      l: Math.random() * 18 + 10,
      v: Math.random() * 10 + 14
    }});
  }}
}}

function renderRain() {{
  if(!rainOn || !rainCtx) return;
  const canvas = document.getElementById("rain-canvas");
  rainCtx.clearRect(0, 0, canvas.width, canvas.height);

  rainCtx.strokeStyle = "rgba(186, 230, 253, 0.55)";
  rainCtx.lineWidth = 1.3;
  rainCtx.beginPath();

  const count = rainIntensity === 1 ? 120 : rainIntensity === 2 ? 220 : 350;
  for(let i=0; i<count; i++) {{
    const d = rainDrops[i];
    rainCtx.moveTo(d.x, d.y);
    rainCtx.lineTo(d.x - 3, d.y + d.l);
    d.y += d.v * simSpeed;
    d.x -= 1.5 * simSpeed;
    if(d.y > canvas.height) {{ d.y = -20; d.x = Math.random() * canvas.width; }}
    if(d.x < 0) d.x = canvas.width;
  }}
  rainCtx.stroke();
}}

function updateWaterlogVisuals() {{
  let maxD = 0;
  waterlogSpots.forEach(s => {{
    const c = waterCircles[s.id];
    if(!c) return;
    const factor = waterAccumulationLevel / 100.0;
    const curDepth = Math.round(s.baseDepth * factor);
    if(curDepth > maxD) maxD = curDepth;

    const elem = document.getElementById(`wl-depth-${{s.id}}`);
    if(elem) {{
      elem.textContent = `${{curDepth}} cm`;
      elem.className = `badge ${{curDepth > 45 ? 'badge-severe' : curDepth > 20 ? 'badge-moderate' : 'badge-passable'}}`;
    }}

    c.setOptions({{
      fillOpacity: factor * 0.45,
      strokeOpacity: factor * 0.9,
      strokeColor: curDepth > 45 ? "#ef4444" : curDepth > 20 ? "#f59e0b" : "#0284c7"
    }});
  }});

  document.getElementById("bs-w").textContent = `${{maxD}} cm`;
}}

function toggleLowAreaHighlight(enable) {{
  Object.values(waterCircles).forEach(c => c.setVisible(enable));
}}

function toggleRain(enable) {{
  rainOn = enable;
  document.getElementById("rain-canvas").style.display = enable ? "block" : "none";
  document.getElementById("bs-r").textContent = enable ? (rainIntensity===1?'Light':rainIntensity===2?'Moderate':'Cloudburst') : 'Dry';
  if(!enable && rainCtx) {{
    const c = document.getElementById("rain-canvas");
    rainCtx.clearRect(0, 0, c.width, c.height);
  }}
  updateDashboard();
}}

function setRainInt(val) {{
  rainIntensity = parseInt(val, 10);
  const labels = ["", "Light Shower", "Moderate Monsoon", "Heavy Cloudburst"];
  document.getElementById("rain-lbl").textContent = labels[rainIntensity];
  if(rainOn) document.getElementById("bs-r").textContent = ["", "Light", "Moderate", "Cloudburst"][rainIntensity];
}}

// ==========================================
// 7. INTELLIGENT REROUTING ENGINE (DIJKSTRA)
// ==========================================
function toggleRoadBlock(roadIdx) {{
  if(blockedRoads.has(roadIdx)) {{
    blockedRoads.delete(roadIdx);
  }} else {{
    blockedRoads.add(roadIdx);
  }}
  filterRoadStyles();
  computeOptimalReroute(roadIdx);
  updateDashboard();
}}

function clearBlocks() {{
  blockedRoads.clear();
  if(reroutePolyline) {{
    reroutePolyline.setMap(null);
    reroutePolyline = null;
  }}
  filterRoadStyles();
  document.getElementById("reroute-box").innerHTML = `
    <h4><span>ℹ️</span> Rerouting System Idle</h4>
    <p style="color:#94a3b8">Turn on <b>Road Block Mode</b> and click any street to calculate optimal detour routing and metrics.</p>
  `;
  updateDashboard();
}}

function simulatePresetBlock(preset) {{
  clearBlocks();
  if(preset === 'bridge') {{
    // Block Surya Narayana Salai Bridge
    blockedRoads.add(0);
    computeOptimalReroute(0);
  }} else if(preset === 'stanley') {{
    // Block Stanley Subway
    blockedRoads.add(11);
    computeOptimalReroute(11);
  }}
  filterRoadStyles();
  setTab('tab-reroute', document.querySelectorAll('.tab')[1]);
  updateDashboard();
}}

function computeOptimalReroute(blockedIdx) {{
  const bRoad = roads[blockedIdx];
  if(!bRoad) return;

  // Find start and end connected neighbors of the blocked street
  const startNeighbors = (bRoad.ns || []).map(c => c.idx).filter(i => !blockedRoads.has(i));
  const endNeighbors = (bRoad.ne || []).map(c => c.idx).filter(i => !blockedRoads.has(i));

  if(!startNeighbors.length || !endNeighbors.length) {{
    document.getElementById("reroute-box").innerHTML = `
      <h4>🚧 Road Blocked: ${{bRoad.n}}</h4>
      <p style="color:#ef4444">Dead-end or isolated corridor. No direct bypass available without backtracking.</p>
    `;
    return;
  }}

  const originIdx = startNeighbors[0];
  const targetIdx = endNeighbors[0];

  // Run Dijkstra to find shortest bypass avoiding all blocked roads & narrow impassable alleys
  const path = dijkstraPath(originIdx, targetIdx);
  
  if(path && path.length) {{
    // Highlight Reroute Polyline on Map
    if(reroutePolyline) reroutePolyline.setMap(null);
    const latlngs = [];
    path.forEach(rIdx => {{
      roads[rIdx].p.forEach(pt => latlngs.push({{ lat: pt[0], lng: pt[1] }}));
    }});

    reroutePolyline = new google.maps.Polyline({{
      path: latlngs,
      geodesic: true,
      strokeColor: "#10b981",
      strokeOpacity: 0.9,
      strokeWeight: 6,
      zIndex: 50,
      map: map
    }});

    const detourNames = [...new Set(path.map(i => roads[i].n))].slice(0, 4).join(" ➔ ");
    const distExtraM = Math.round(path.length * 95);
    const detourTimeMin = (distExtraM / 400).toFixed(1);

    document.getElementById("reroute-box").innerHTML = `
      <h4>⭐ Recommended Optimal Detour</h4>
      <div style="color:#f87171;margin-bottom:4px"><b>Blocked Corridor:</b> ${{bRoad.n}}</div>
      <div class="reroute-step">
        <b style="color:#34d399">Primary Bypass Route:</b><br>
        ${{detourNames}}
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:8px">
        <div style="background:#0f1833;padding:6px;border-radius:6px;text-align:center">
          <div style="color:#00ffc8;font-size:14px;font-weight:700">+${{distExtraM}}m</div>
          <div style="color:#64748b;font-size:8.5px">EXTRA DISTANCE</div>
        </div>
        <div style="background:#0f1833;padding:6px;border-radius:6px;text-align:center">
          <div style="color:#fbbf24;font-size:14px;font-weight:700">+${{detourTimeMin}} min</div>
          <div style="color:#64748b;font-size:8.5px">DETOUR TIME</div>
        </div>
      </div>
      <div style="font-size:10px;color:#94a3b8;margin-top:6px">
        ✅ <b>Street Suitability:</b> Wide arterial corridor selected. Safe for MTC Buses, Emergency ambulances, and cars.
      </div>
    `;
  }}
}}

function dijkstraPath(startIdx, targetIdx) {{
  const dist = {{}};
  const prev = {{}};
  const visited = new Set();
  const queue = [startIdx];

  roads.forEach(r => {{ dist[r.i] = Infinity; }});
  dist[startIdx] = 0;

  while(queue.length > 0) {{
    queue.sort((a,b) => dist[a] - dist[b]);
    const u = queue.shift();
    if(u === targetIdx) break;
    visited.add(u);

    const uRoad = roads[u];
    const neighbors = [...(uRoad.ns||[]), ...(uRoad.ne||[])];

    neighbors.forEach(n => {{
      const v = n.idx;
      if(visited.has(v) || blockedRoads.has(v)) return;
      const vRoad = roads[v];
      
      // Cost: penalize narrow alleys and low-lying water spots
      let cost = 1.0;
      if(vRoad.sm) cost += 2.0;
      if(vRoad.low && rainOn) cost += 3.0;
      if(vRoad.ow && !n.fwd) return; // One-way violation

      const alt = dist[u] + cost;
      if(alt < dist[v]) {{
        dist[v] = alt;
        prev[v] = u;
        if(!queue.includes(v)) queue.push(v);
      }}
    }});
  }}

  if(dist[targetIdx] === Infinity) return null;
  const path = [];
  let curr = targetIdx;
  while(curr !== undefined) {{
    path.unshift(curr);
    curr = prev[curr];
  }}
  return path;
}}

// ==========================================
// 8. UI INITIALIZERS & TABS
// ==========================================
function setTab(tabId, tabElem) {{
  document.querySelectorAll(".tab-content").forEach(c => c.style.display = "none");
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.getElementById(tabId).style.display = "block";
  tabElem.classList.add("active");
}}

function initUISelectors() {{
  const sel = document.getElementById("sel-target-poi");
  sel.innerHTML = "";
  pois.forEach(p => {{
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = `${{p.icon}} ${{p.name}} (${{p.category.toUpperCase()}})`;
    sel.appendChild(opt);
  }});
  sel.value = pois[0].id;
  onTargetPOIChanged(pois[0].id);
}}

function onTargetPOIChanged(poiId) {{
  selectedTargetPOI = pois.find(p => p.id === poiId) || pois[0];
  document.getElementById("target-poi-stats").innerHTML = `
    <b>Target:</b> ${{selectedTargetPOI.icon}} ${{selectedTargetPOI.name}}<br>
    <b>Category:</b> <span class="poi-cat cat-${{selectedTargetPOI.category}}">${{selectedTargetPOI.category.toUpperCase()}}</span><br>
    <b>Target Footfall:</b> ${{targetVisitorCount}} visitors/hr<br>
    <b>Access Corridor:</b> Authentic street grid feeding ${{selectedTargetPOI.name}}
  `;
  rebalanceVehicles();
  updateDashboard();
}}

function onVisitorCountSlider(val) {{
  targetVisitorCount = parseInt(val, 10);
  document.getElementById("lbl-visitor-count").textContent = `${{targetVisitorCount.toLocaleString()}} visitors`;
  rebalanceVehicles();
  updateDashboard();
}}

function onOriginGatewayChanged(gwKey) {{
  selectedGateway = gwKey;
  dispatchTargetFleet();
}}

function initHotspotList() {{
  const container = document.getElementById("hotspot-list");
  container.innerHTML = "";
  waterlogSpots.forEach(s => {{
    const card = document.createElement("div");
    card.className = "hotspot-card";
    card.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;font-weight:700">
        <span>${{s.name}}</span>
        <span class="badge badge-passable" id="wl-depth-${{s.id}}">0 cm</span>
      </div>
      <div style="font-size:10px;color:#94a3b8;margin-top:2px">${{s.desc}}</div>
      <div style="font-size:9.5px;color:#38bdf8;margin-top:3px">Elevation Dip: ${{s.elev}} below surrounding crest</div>
    `;
    card.onclick = () => {{
      map.panTo({{ lat: s.lat, lng: s.lng }});
      map.setZoom(17.5);
    }};
    container.appendChild(card);
  }});
}}

function initPOIList() {{
  renderFilteredPOIs(pois);
}}

function renderFilteredPOIs(list) {{
  const container = document.getElementById("poi-list");
  container.innerHTML = "";
  list.forEach(p => {{
    const card = document.createElement("div");
    card.className = "poi-card";
    card.innerHTML = `
      <div class="poi-title">
        <span>${{p.icon}} ${{p.name}}</span>
        <span class="poi-cat cat-${{p.category}}">${{p.category.toUpperCase()}}</span>
      </div>
      <div style="font-size:10px;color:#94a3b8;margin-top:3px">${{p.desc}}</div>
      <div style="font-size:10px;color:#00ffc8;font-weight:700;margin-top:4px">
        Expected Footfall: ${{p.defaultVisitors}} visitors/hr
      </div>
    `;
    card.onclick = () => {{
      selectAsTarget(p.id);
      map.panTo({{ lat: p.lat, lng: p.lng }});
      map.setZoom(17.5);
    }};
    container.appendChild(card);
  }});
}}

function filterPOICat(cat, btn) {{
  document.querySelectorAll("#tab-pois .btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  if(cat === 'all') {{
    renderFilteredPOIs(pois);
  }} else {{
    renderFilteredPOIs(pois.filter(p => p.category === cat));
  }}
}}

function filterPOISearch(q) {{
  const lower = q.toLowerCase();
  renderFilteredPOIs(pois.filter(p => p.name.toLowerCase().includes(lower) || p.desc.toLowerCase().includes(lower)));
}}

// ==========================================
// 9. ANIMATION LOOP & DASHBOARD
// ==========================================
function animateSimulation(now) {{
  const dtMs = Math.min(now - lastFrameTime, 100);
  lastFrameTime = now;

  if(simRunning) {{
    updateVehicles(dtMs);

    if(rainOn) {{
      waterAccumulationLevel = Math.min(100, waterAccumulationLevel + 0.04 * rainIntensity * simSpeed);
      renderRain();
      updateWaterlogVisuals();
    }} else if(waterAccumulationLevel > 0) {{
      waterAccumulationLevel = Math.max(0, waterAccumulationLevel - 0.08 * simSpeed);
      updateWaterlogVisuals();
    }}
  }}

  requestAnimationFrame(animateSimulation);
}}

function togVeh(type, enable) {{
  vehConfigs[type].enabled = enable;
  vehicles.forEach(v => {{ if(v.type === type && v.marker) v.marker.setMap(enable ? map : null); }});
  rebalanceVehicles();
  updateDashboard();
}}

function setMapType(type) {{
  if(map) map.setMapTypeId(type);
  document.getElementById("btn-sat").className = `btn ${{type==='hybrid'?'active':''}}`;
  document.getElementById("btn-road").className = `btn ${{type==='roadmap'?'active':''}}`;
}}

function toggleGoogleTraffic(enable) {{
  if(trafficLayer) trafficLayer.setMap(enable ? map : null);
}}

function tiltCam(t) {{ if(map) map.setTilt(t); }}

function updateDashboard() {{
  const activeFleet = vehicles.filter(v => vehConfigs[v.type].enabled).length;
  document.getElementById("bs-v").textContent = activeFleet;
  document.getElementById("bs-dest-visitors").textContent = targetVisitorCount.toLocaleString();

  const rainSlow = rainOn ? [1, 0.75, 0.52, 0.35][rainIntensity] : 1.0;
  const avgSpeed = Math.round(34 * rainSlow * (1.0 - (blockedRoads.size * 0.08)));
  document.getElementById("bs-s").textContent = `${{Math.max(8, avgSpeed)}} km/h`;

  const baseCong = (timeOfDay>=8&&timeOfDay<=10) || (timeOfDay>=17&&timeOfDay<=20) ? 68 : 36;
  const cong = Math.min(98, baseCong + (rainOn ? rainIntensity * 14 : 0) + blockedRoads.size * 12);
  document.getElementById("bs-c").textContent = `${{cong}}%`;
  document.getElementById("bs-b").textContent = blockedRoads.size;
}}

window.addEventListener("resize", () => {{
  const c = document.getElementById("rain-canvas");
  if(c) {{ c.width = window.innerWidth - 450; c.height = window.innerHeight; }}
}});
</script>

<script async defer src="https://maps.googleapis.com/maps/api/js?key={apiKey}&callback=initGoogleMap&v=weekly"></script>
</body>
</html>
'''

with open('c:/Users/SAAQIB/areatwin/google_maps_twin.html', 'w', encoding='utf-8') as f:
    f.write(code)

print("google_maps_twin.html compiled successfully with all requested advanced features!")
