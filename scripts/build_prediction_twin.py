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
<title>Royapuram Digital Twin - Speed Telemetry, Anti-Collision & Traffic Prediction</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#050914;color:#f1f5f9;overflow:hidden;height:100vh}}
#app{{display:flex;height:100vh;width:100vw}}
#map-container{{flex:1;position:relative}}
#map{{width:100%;height:100%}}
#rain-canvas{{position:absolute;inset:0;pointer-events:none;z-index:2;display:none}}
#sidebar{{width:460px;background:linear-gradient(180deg,#0a1124 0%,#0c152d 100%);border-left:1px solid #1f2d52;overflow-y:auto;z-index:20;flex-shrink:0;box-shadow:-8px 0 35px rgba(0,0,0,0.7)}}

.tabs{{display:flex;background:#070d1e;border-bottom:1px solid #1a274c;position:sticky;top:0;z-index:30}}
.tab{{flex:1;padding:10px 3px;font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:0.7px;text-align:center;color:#64748b;cursor:pointer;border-bottom:2px solid transparent;transition:.2s}}
.tab:hover{{color:#94a3b8;background:#0d1838}}
.tab.active{{color:#38bdf8;border-bottom-color:#38bdf8;background:#0f1d45}}

.panel{{padding:13px 16px;border-bottom:1px solid #1a274c}}
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
.btn.warn{{border-color:#f59e0b;color:#fbbf24}}
.btn.warn:hover{{background:#d97706;color:#fff}}

input[type=range]{{width:100%;accent-color:#38bdf8;margin:4px 0}}
select, input[type=text]{{width:100%;background:#0b1329;border:1px solid #223561;color:#f1f5f9;border-radius:6px;padding:7px 9px;font-size:11px;margin-bottom:8px;outline:none}}
select:focus, input[type=text]:focus{{border-color:#38bdf8}}

.badge{{font-size:9.5px;padding:2px 7px;border-radius:10px;font-weight:700}}
.badge-severe{{background:#ef444422;color:#f87171;border:1px solid #ef444455}}
.badge-moderate{{background:#f59e0b22;color:#fbbf24;border:1px solid #f59e0b55}}
.badge-low{{background:#0284c722;color:#38bdf8;border:1px solid #0284c755}}
.badge-passable{{background:#10b98122;color:#34d399;border:1px solid #10b98155}}

.predict-card{{background:#13182e;border:1px solid #2a3b6b;border-radius:8px;padding:10px;margin-bottom:8px}}
.predict-header{{display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:11.5px}}
.surge-val{{font-size:13px;font-weight:800;color:#ef4444}}

.telemetry-card{{background:#0c1730;border:1px solid #1d3363;border-radius:7px;padding:9px;margin-top:6px;font-size:11px}}
.telemetry-grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-top:6px;text-align:center}}
.telemetry-box{{background:#070d1e;border:1px solid #16264d;border-radius:6px;padding:6px 4px}}
.telemetry-val{{font-size:15px;font-weight:700;color:#38bdf8}}
.telemetry-lbl{{font-size:8.5px;color:#64748b;text-transform:uppercase;margin-top:2px}}

.poi-card{{background:#0e172e;border:1px solid #1a274c;border-radius:7px;padding:8px 10px;margin-bottom:6px;cursor:pointer;transition:.2s}}
.poi-card:hover{{border-color:#38bdf8;background:#121e3d}}
.poi-title{{display:flex;justify-content:space-between;align-items:center;font-size:11px;font-weight:700}}
.poi-cat{{font-size:8.5px;padding:1px 5px;border-radius:8px;text-transform:uppercase}}
.cat-kovil{{background:#eab30822;color:#facc15;border:1px solid #eab30855}}
.cat-hotel{{background:#f9731622;color:#fb923c;border:1px solid #f9731655}}
.cat-metro{{background:#06b6d422;color:#22d3ee;border:1px solid #06b6d455}}
.cat-station{{background:#f59e0b22;color:#fbbf24;border:1px solid #f59e0b55}}
.cat-place{{background:#8b5cf622;color:#a78bfa;border:1px solid #8b5cf655}}

#hud{{position:absolute;top:0;left:0;right:0;z-index:10;background:linear-gradient(180deg,rgba(4,8,18,0.96) 0%,rgba(4,8,18,0.4) 75%,transparent 100%);padding:11px 20px;display:flex;align-items:center;justify-content:space-between;pointer-events:none}}
#hud>*{{pointer-events:auto}}
#hud h1{{font-size:16.5px;color:#f8fafc;font-weight:700;display:flex;align-items:center;gap:8px}}
#hud h1 span.tag{{font-size:10px;color:#38bdf8;font-weight:500;background:#0369a133;border:1px solid #0284c766;padding:2px 7px;border-radius:12px}}
#time-disp{{font-size:12px;color:#fcd34d;background:#0f172a;padding:4px 12px;border-radius:20px;border:1px solid #334155;font-weight:600}}

#bottom-bar{{position:absolute;bottom:0;left:0;right:460px;z-index:10;background:linear-gradient(transparent,rgba(4,8,18,0.96) 30%);padding:10px 18px;display:flex;gap:9px;justify-content:center;pointer-events:none}}
#bottom-bar>*{{pointer-events:auto}}
.bs{{text-align:center;background:#0f172acc;backdrop-filter:blur(6px);border:1px solid #1e293b;border-radius:8px;padding:6px 11px;min-width:85px}}
.bs .v{{font-size:14px;font-weight:700;color:#2dd4bf}}
.bs .l{{font-size:7.5px;color:#94a3b8;text-transform:uppercase;margin-top:2px;letter-spacing:0.4px}}

.legend-bar{{display:flex;gap:7px;margin-top:6px;font-size:9px;color:#94a3b8;flex-wrap:wrap}}
.legend-item{{display:flex;align-items:center;gap:4px}}
.legend-dot{{width:8px;height:8px;border-radius:50%}}

::-webkit-scrollbar{{width:5px}}
::-webkit-scrollbar-track{{background:#030712}}
::-webkit-scrollbar-thumb{{background:#1e294b;border-radius:3px}}
</style>
</head>
<body>
<div id="app">
<div id="map-container">
  <div id="hud">
    <h1>🏙️ Royapuram Digital Twin <span class="tag">Anti-Collision & Traffic Prediction Model</span></h1>
    <div style="display:flex;align-items:center;gap:9px">
      <a href="index.html" class="btn" style="text-decoration:none;display:inline-block">🏙️ 3D Three.js Twin</a>
      <div id="time-disp">🕐 08:00 AM</div>
    </div>
  </div>
  <canvas id="rain-canvas"></canvas>
  <div id="map"></div>
  <div id="bottom-bar">
    <div class="bs"><div class="v" id="bs-v">0</div><div class="l">Active Fleet</div></div>
    <div class="bs"><div class="v" id="bs-s" style="color:#38bdf8">0 km/h</div><div class="l">Avg Fleet Speed</div></div>
    <div class="bs"><div class="v" id="bs-q" style="color:#fbbf24">0</div><div class="l">Queued / Braking</div></div>
    <div class="bs"><div class="v" id="bs-c">0%</div><div class="l">City Congestion</div></div>
    <div class="bs"><div class="v" id="bs-pred" style="color:#ef4444">Normal</div><div class="l">Prediction Status</div></div>
    <div class="bs"><div class="v" id="bs-r">Dry</div><div class="l">Monsoon Rain</div></div>
    <div class="bs"><div class="v" id="bs-w">0 cm</div><div class="l">Max Stagnation</div></div>
  </div>
</div>

<div id="sidebar">
  <div class="tabs">
    <div class="tab active" onclick="setTab('tab-predict', this)">🔮 Predict Traffic</div>
    <div class="tab" onclick="setTab('tab-telemetry', this)">⚡ Speed & Anti-Collision</div>
    <div class="tab" onclick="setTab('tab-visitor', this)">🎯 Visitors</div>
    <div class="tab" onclick="setTab('tab-rain', this)">🌧️ Flood & Basin</div>
    <div class="tab" onclick="setTab('tab-anatomy', this)">🛣️ Streets</div>
    <div class="tab" onclick="setTab('tab-pois', this)">📍 Places</div>
  </div>

  <!-- TAB 1: TRAFFIC PREDICTION ENGINE -->
  <div id="tab-predict" class="tab-content">
    <div class="panel">
      <h3><span>🔮</span> Blockage Traffic Prediction Engine</h3>
      <p style="font-size:10.5px;color:#94a3b8;margin-bottom:9px">
        Select any road corridor to <b>simulate and predict where congestion will accumulate</b>, which parallel bypasses will choke, and expected tailback queues:
      </p>

      <label style="font-size:11px;color:#94a3b8;font-weight:600">Simulate Incident / Road Blockage On:</label>
      <select id="sel-predict-road" onchange="runTrafficPrediction(this.value)"></select>

      <div class="ctrl" style="margin-top:4px">
        <label>🔥 Congestion Prediction Heatmap</label>
        <label class="toggle"><input type="checkbox" id="tog-heatmap" checked onchange="togglePredictionHeatmap(this.checked)"><span class="sl"></span></label>
      </div>

      <div style="display:flex;gap:5px;margin-top:6px">
        <button class="btn warn" onclick="predictPresetBlock('bridge')">Simulate Bridge Collapse</button>
        <button class="btn danger" onclick="predictPresetBlock('subway')">Simulate Flooded Subway</button>
        <button class="btn" onclick="clearPrediction()">Clear</button>
      </div>
    </div>

    <!-- Prediction Results Card -->
    <div class="panel" id="panel-prediction-results">
      <div id="prediction-report">
        <div style="color:#64748b;font-size:11px;text-align:center;padding:12px">
          Select a road corridor above or click any street on the map to run the predictive congestion assignment model.
        </div>
      </div>
    </div>
  </div>

  <!-- TAB 2: SPEED TELEMETRY & ANTI-COLLISION -->
  <div id="tab-telemetry" class="tab-content" style="display:none">
    <div class="panel">
      <h3><span>⚡</span> Vehicle Speed & Anti-Collision Headway</h3>
      <p style="font-size:10.5px;color:#94a3b8;margin-bottom:8px">
        Every vehicle runs an individual speed controller and <b>Intelligent Car-Following Model</b>. Vehicles keep safe headway distance and never collide or overlap:
      </p>

      <div class="ctrl">
        <label>🛡️ Intelligent Anti-Collision System</label>
        <label class="toggle"><input type="checkbox" id="tog-anticollision" checked onchange="antiCollisionEnabled=this.checked"><span class="sl"></span></label>
      </div>

      <div class="ctrl">
        <label>Simulation Speed Multiplier</label>
        <div style="display:flex;gap:4px">
          <button class="btn active" onclick="setSpd(1,this)">1×</button>
          <button class="btn" onclick="setSpd(2,this)">2×</button>
          <button class="btn" onclick="setSpd(4,this)">4×</button>
        </div>
      </div>

      <div class="telemetry-card">
        <div style="font-size:11px;font-weight:700;color:#00ffc8;display:flex;justify-content:space-between">
          <span>📊 Live Fleet Telemetry</span>
          <span id="telemetry-status">All Moving Smoothly</span>
        </div>
        <div class="telemetry-grid">
          <div class="telemetry-box">
            <div class="telemetry-val" id="tel-avg-spd">38</div>
            <div class="telemetry-lbl">Avg Speed (km/h)</div>
          </div>
          <div class="telemetry-box">
            <div class="telemetry-val" id="tel-top-spd" style="color:#10b981">52</div>
            <div class="telemetry-lbl">Top Speed (km/h)</div>
          </div>
          <div class="telemetry-box">
            <div class="telemetry-val" id="tel-braking" style="color:#f59e0b">0</div>
            <div class="telemetry-lbl">Vehicles in Queue</div>
          </div>
        </div>
      </div>

      <div style="margin-top:10px;font-size:10.5px;color:#94a3b8;line-height:1.5">
        💡 <b>Click any vehicle marker</b> on Google Maps to inspect its live speedometer, trailing distance to leader, and braking telemetry in real time.
      </div>
    </div>

    <!-- Modalities -->
    <div class="panel">
      <h3><span>🚗</span> Fleet Modalities & Speed Limits</h3>
      <div class="ctrl"><label>🚗 Sedans & Cars (Max 55 km/h)</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('car',this.checked)"><span class="sl"></span></label></div>
      <div class="ctrl"><label>🏍️ Bikes & Two-Wheelers (Max 52 km/h)</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('bike',this.checked)"><span class="sl"></span></label></div>
      <div class="ctrl"><label>🛺 Iconic Auto-Rickshaws (Max 40 km/h)</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('auto',this.checked)"><span class="sl"></span></label></div>
      <div class="ctrl"><label>🚌 Chennai MTC Buses (Max 34 km/h)</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('bus',this.checked)"><span class="sl"></span></label></div>
    </div>
  </div>

  <!-- TAB 3: VISITOR FLOW -->
  <div id="tab-visitor" class="tab-content" style="display:none">
    <div class="panel">
      <h3><span>🎯</span> Origin-Destination Visitor Flow</h3>
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
    </div>
  </div>

  <!-- TAB 4: RAIN & WATER STAGNATION -->
  <div id="tab-rain" class="tab-content" style="display:none">
    <div class="panel">
      <h3><span>🌧️</span> Rain & Water Stoppage Simulation</h3>
      <div class="ctrl">
        <label>Monsoon Rainfall</label>
        <label class="toggle"><input type="checkbox" id="rain-tog" onchange="toggleRain(this.checked)"><span class="sl"></span></label>
      </div>
      <div class="ctrl">
        <label>Rainfall Intensity</label>
        <span id="rain-lbl" style="font-size:11px;color:#38bdf8;font-weight:600">Light Shower</span>
      </div>
      <input type="range" id="rain-sl" min="1" max="3" value="1" oninput="setRainInt(this.value)">

      <div style="margin-top:10px;font-size:11px;font-weight:700;color:#00ffc8">🌊 Known Stagnation Hotspots (Low Basins):</div>
      <div id="hotspot-list" style="margin-top:7px"></div>
    </div>
  </div>

  <!-- TAB 5: STREET ANATOMY -->
  <div id="tab-anatomy" class="tab-content" style="display:none">
    <div class="panel">
      <h3><span>🛣️</span> Street Anatomy & Physical Constraints</h3>
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
    </div>
  </div>

  <!-- TAB 6: PLACES -->
  <div id="tab-pois" class="tab-content" style="display:none">
    <div class="panel">
      <h3><span>📍</span> Categorized Places Directory</h3>
      <div style="display:flex;gap:4px;margin-bottom:8px;flex-wrap:wrap">
        <button class="btn active" onclick="filterPOICat('all',this)">All (29)</button>
        <button class="btn" onclick="filterPOICat('kovil',this)">🛕 Kovils</button>
        <button class="btn" onclick="filterPOICat('hotel',this)">🍽️ Hotels</button>
        <button class="btn" onclick="filterPOICat('metro',this)">🚇 Metros</button>
        <button class="btn" onclick="filterPOICat('station',this)">🚂 Stations</button>
      </div>
      <input type="text" id="poi-search" placeholder="🔍 Search place..." oninput="filterPOISearch(this.value)">
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

const gateways = {{
  gateway_south: {{ name: "South (Parrys / High Court)", roadIdx: 1, lat: 13.0945, lng: 80.2960 }},
  gateway_north: {{ name: "North (Tondiarpet / Ennore)", roadIdx: 0, lat: 13.1110, lng: 80.2885 }},
  gateway_west:  {{ name: "West (Mint / Basin Bridge)", roadIdx: 11, lat: 13.0992, lng: 80.2872 }},
  gateway_harbour: {{ name: "Kasimedu Port Wharf Gate", roadIdx: 12, lat: 13.1142, lng: 80.2990 }},
  gateway_distributed: {{ name: "Distributed Local Streets", roadIdx: null }}
}};

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
let antiCollisionEnabled = true;
let showPredictionHeatmap = true;
let activePredictedRoadIdx = null;

// Vehicle Modality Specs & Top Speeds
const vehConfigs = {{
  car:  {{topSpeedKmh: 52, scale: 3.8, color: '#38bdf8', minGap: 11, enabled: true}},
  bike: {{topSpeedKmh: 48, scale: 2.5, color: '#22c55e', minGap: 5.5, enabled: true}},
  auto: {{topSpeedKmh: 38, scale: 3.2, color: '#facc15', minGap: 8.5, enabled: true}},
  bus:  {{topSpeedKmh: 32, scale: 4.8, color: '#ef4444', minGap: 16, enabled: true}}
}};
let vehicles = [];
let nextVehId = 101;

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

  initPredictRoadSelector();
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
// 3. ROAD RENDERING & PREDICTION HEATMAP
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
      zIndex: style.zIndex || 1,
      map: showRoadLines ? map : null
    }});

    polyline.roadIndex = r.i;
    polyline.roadData = r;

    polyline.addListener("click", () => {{
      if(blockMode) {{
        toggleRoadBlock(r.i);
      }} else {{
        // Run prediction on clicked road
        document.getElementById("sel-predict-road").value = r.i;
        runTrafficPrediction(r.i);
        setTab('tab-predict', document.querySelectorAll('.tab')[0]);
      }}
    }});

    roadPolylines[r.i] = polyline;
  }});
}}

function getRoadStyle(r) {{
  if(blockedRoads.has(r.i)) {{
    return {{ color: '#ef4444', weight: 6, opacity: 0.95, zIndex: 10 }};
  }}

  // If heatmap is active and road has predicted congestion:
  if(showPredictionHeatmap && r.predVC !== undefined && r.predVC > 0.5) {{
    if(r.predVC >= 1.1) {{
      return {{ color: '#dc2626', weight: 6.5, opacity: 0.95, zIndex: 8 }}; // Red Gridlock
    }} else if(r.predVC >= 0.85) {{
      return {{ color: '#f97316', weight: 5.0, opacity: 0.9, zIndex: 6 }}; // Orange Severe
    }} else if(r.predVC >= 0.65) {{
      return {{ color: '#eab308', weight: 4.0, opacity: 0.85, zIndex: 4 }}; // Yellow Moderate
    }}
  }}

  const togOneWay = document.getElementById("tog-oneway")?.checked;
  const togSmall = document.getElementById("tog-small")?.checked;
  const togDeadEnds = document.getElementById("tog-deadends")?.checked;
  const togBasins = document.getElementById("tog-basins")?.checked;

  if(togOneWay && r.ow) return {{ color: '#fb923c', weight: 4.5, opacity: 0.95 }};
  if(togDeadEnds && r.de) return {{ color: '#f43f5e', weight: 4.0, opacity: 0.9 }};
  if(togBasins && r.low) return {{ color: '#0284c7', weight: 4.5, opacity: 0.9 }};
  if(togSmall && r.sm) return {{ color: '#c084fc', weight: 2.8, opacity: 0.85 }};

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
      poly.setOptions({{
        strokeColor: s.color,
        strokeWeight: s.weight,
        strokeOpacity: s.opacity,
        zIndex: s.zIndex || 1
      }});
    }}
  }});
}}

function toggleRoadLines(show) {{
  showRoadLines = show;
  roadPolylines.forEach(p => {{ if(p) p.setMap(show ? map : null); }});
}}

// ==========================================
// 4. VEHICLE SPEED & ANTI-COLLISION ENGINE
// ==========================================
function spawnVehicle(poi, gatewayKey) {{
  const types = ['car','bike','bike','auto','auto','car'];
  if(poi.id.includes('station') || poi.id.includes('metro') || poi.id.includes('stanley') || poi.id.includes('harbour')) {{
    types.push('bus');
  }}
  const type = types[Math.floor(Math.random()*types.length)];
  const cfg = vehConfigs[type];
  if(!cfg.enabled) return null;

  let startRoadIdx;
  const gw = gateways[gatewayKey || selectedGateway];
  if(gw && gw.roadIdx !== null && !blockedRoads.has(gw.roadIdx)) {{
    startRoadIdx = gw.roadIdx;
  }} else {{
    const unblocked = roads.filter(r => !blockedRoads.has(r.i) && (type!=='bus' || r.b) && (!r.sm || type!=='bus'));
    if(!unblocked.length) return null;
    startRoadIdx = unblocked[Math.floor(Math.random()*unblocked.length)].i;
  }}

  const road = roads[startRoadIdx];
  const fwd = road.ow ? true : (Math.random() > 0.5);
  const startPt = fwd ? road.p[0] : road.p[road.p.length-1];

  const vehId = `V-${{nextVehId++}}`;
  const baseSpeed = cfg.topSpeedKmh * (0.85 + Math.random() * 0.25);

  const marker = new google.maps.Marker({{
    position: {{ lat: startPt[0], lng: startPt[1] }},
    map: map,
    title: `${{type.toUpperCase()}} [${{vehId}}]`,
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

  const veh = {{
    id: vehId,
    type,
    marker,
    targetPOI: poi,
    roadIdx: road.i,
    segIdx: fwd ? 0 : road.p.length - 2,
    fwd: fwd,
    progress: 0.0,
    baseSpeedKmh: baseSpeed,
    currentSpeedKmh: baseSpeed,
    targetSpeedKmh: baseSpeed,
    isBraking: false,
    headwayMeters: 999,
    longPos: 0
  }};

  marker.addListener("click", () => {{
    showVehicleTelemetry(veh);
  }});

  return veh;
}}

function showVehicleTelemetry(v) {{
  const road = roads[v.roadIdx];
  const speedColor = v.currentSpeedKmh > 35 ? '#10b981' : v.currentSpeedKmh > 15 ? '#f59e0b' : '#ef4444';
  const stateText = v.currentSpeedKmh < 3 ? '🔴 Stopped in Queue / Block' : v.isBraking ? '🟡 Decelerating (Safe Headway)' : '🟢 Free Cruising';

  const content = `
    <div style="color:#000;font-family:sans-serif;padding:6px;min-width:210px">
      <div style="font-size:10px;color:#64748b;font-weight:700">VEHICLE TELEMETRY & ANTI-COLLISION</div>
      <b style="font-size:13px">${{v.type==='bus'?'🚌 MTC City Bus':v.type==='car'?'🚗 Sedan':v.type==='auto'?'🛺 Auto Rickshaw':'🏍️ Two-Wheeler'}} [${{v.id}}]</b>
      <div style="margin-top:6px;background:#f8fafc;padding:6px;border-radius:6px;border:1px solid #e2e8f0">
        <div style="display:flex;justify-content:space-between">
          <span>Speed:</span>
          <b style="color:${{speedColor}}">${{v.currentSpeedKmh.toFixed(1)}} km/h</b>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:3px">
          <span>Safe Headway Gap:</span>
          <b>${{v.headwayMeters < 500 ? v.headwayMeters.toFixed(1) + ' m' : 'Clear road'}}</b>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:3px">
          <span>Current State:</span>
          <b>${{stateText}}</b>
        </div>
      </div>
      <div style="margin-top:5px;font-size:10.5px;color:#475569">
        🛣️ <b>Road:</b> ${{road.n}}<br>
        🎯 <b>Heading To:</b> ${{v.targetPOI.name}}
      </div>
    </div>`;

  new google.maps.InfoWindow({{
    content,
    position: v.marker.getPosition()
  }}).open(map, v.marker);
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
  if(selectedTargetPOI) {{
    map.panTo({{ lat: selectedTargetPOI.lat, lng: selectedTargetPOI.lng }});
    map.setZoom(17);
  }}
}}

let lastFrameTime = performance.now();

function updateVehicles(dtMs) {{
  const rainSlow = rainOn ? [1, 0.75, 0.52, 0.35][rainIntensity] : 1.0;

  // 1. Calculate longitudinal positions and Anti-Collision Spacing
  if(antiCollisionEnabled) {{
    runAntiCollisionModel();
  }}

  // 2. Advance vehicles along road geometry
  let totalSpeed = 0;
  let maxSpeed = 0;
  let brakingCount = 0;

  vehicles.forEach(v => {{
    const road = roads[v.roadIdx];
    if(!road || !road.p || road.p.length < 2) return;

    // Road speed limits: narrow alleys (<3.5m) cap speed at 22 km/h
    const roadSpeedCap = road.sm ? 22 : (road.t === 'primary' ? 55 : 40);
    const targetSpd = Math.min(v.baseSpeedKmh, roadSpeedCap);

    // Rain and water depth factor
    const waterDepth = (rainOn && road.low) ? Math.round(road.water_depth_cm * (waterAccumulationLevel/100.0)) : 0;
    const waterFactor = waterDepth > 35 ? 0.22 : waterDepth > 15 ? 0.55 : 1.0;

    // If anti-collision didn't set speed, smooth toward target
    if(!v.isBraking) {{
      v.currentSpeedKmh += (targetSpd * rainSlow * waterFactor - v.currentSpeedKmh) * 0.08;
    }}

    totalSpeed += v.currentSpeedKmh;
    if(v.currentSpeedKmh > maxSpeed) maxSpeed = v.currentSpeedKmh;
    if(v.isBraking || v.currentSpeedKmh < 10) brakingCount++;

    // Convert km/h to coordinate progress delta
    const speedRatio = (v.currentSpeedKmh / 3600.0) * 0.001; // km per ms
    const pA = road.p[v.segIdx];
    const pB = road.p[v.segIdx + 1];
    const dLat = pB[0] - pA[0];
    const dLng = pB[1] - pA[1];
    const segLenKm = Math.hypot(dLat * 111, dLng * 111 * Math.cos(pA[0] * Math.PI / 180));

    const progressInc = (speedRatio * simSpeed * dtMs) / Math.max(segLenKm, 0.00005);

    if(v.fwd) {{
      v.progress += progressInc;
      if(v.progress >= 1.0) {{
        v.progress = 0.0;
        v.segIdx++;
        if(v.segIdx >= road.p.length - 1) {{
          // At road end: choose next street
          const nextConns = (road.ne || []).filter(c => {{
            if(blockedRoads.has(c.idx)) return false;
            const nr = roads[c.idx];
            if(v.type === 'bus' && (nr.sm || !nr.b)) return false;
            if(nr.ow && !c.fwd) return false;
            return true;
          }});

          if(nextConns.length > 0) {{
            const chosen = nextConns[Math.floor(Math.random() * nextConns.length)];
            v.roadIdx = chosen.idx;
            const nextRoad = roads[chosen.idx];
            v.fwd = chosen.fwd;
            v.segIdx = v.fwd ? 0 : nextRoad.p.length - 2;
          }} else {{
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
            if(nr.ow && !c.fwd) return false;
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

    // Update position strictly on real asphalt
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

  // Update Telemetry Panel
  const n = vehicles.length || 1;
  const avg = Math.round(totalSpeed / n);
  document.getElementById("bs-s").textContent = `${{avg}} km/h`;
  document.getElementById("tel-avg-spd").textContent = avg;
  document.getElementById("tel-top-spd").textContent = Math.round(maxSpeed);
  document.getElementById("tel-braking").textContent = brakingCount;
  document.getElementById("bs-q").textContent = brakingCount;

  const telStatus = document.getElementById("telemetry-status");
  if(brakingCount > 8) {{
    telStatus.textContent = `⚠️ ${{brakingCount}} in Queues (Traffic Accumulating)`;
    telStatus.style.color = "#f87171";
  }} else if(brakingCount > 2) {{
    telStatus.textContent = `🟡 Minor Deceleration`;
    telStatus.style.color = "#fbbf24";
  }} else {{
    telStatus.textContent = `🟢 All Clear Free Flow`;
    telStatus.style.color = "#34d399";
  }}
}}

// ==========================================
// 5. ANTI-COLLISION & CAR-FOLLOWING MODEL
// ==========================================
function runAntiCollisionModel() {{
  const groups = {{}};
  vehicles.forEach(v => {{
    const key = `${{v.roadIdx}}_${{v.fwd ? 'f' : 'r'}}`;
    if(!groups[key]) groups[key] = [];
    groups[key].push(v);
  }});

  for(const key in groups) {{
    const list = groups[key];
    const road = roads[list[0].roadIdx];
    const nSegs = Math.max(1, road.p.length - 1);
    const avgSegLenM = (road.len || 100) / nSegs;

    // Calculate longitudinal position in meters from road start
    list.forEach(v => {{
      const segIndexFromStart = v.fwd ? v.segIdx : (nSegs - 1 - v.segIdx);
      v.longPos = segIndexFromStart * avgSegLenM + (v.fwd ? v.progress : (1.0 - v.progress)) * avgSegLenM;
    }});

    // Sort descending: index 0 is furthest along road (the leader)
    list.sort((a, b) => b.longPos - a.longPos);

    const isRoadBlocked = blockedRoads.has(road.i);

    for(let i = 0; i < list.length; i++) {{
      const follower = list[i];
      let leaderGap = 9999;
      let leaderSpeed = follower.baseSpeedKmh;

      if(i === 0) {{
        // Leader of this road segment
        if(isRoadBlocked) {{
          leaderGap = Math.max(0, (road.len || 100) - follower.longPos);
          leaderSpeed = 0;
        }}
      }} else {{
        const leader = list[i - 1];
        leaderGap = leader.longPos - follower.longPos;
        leaderSpeed = leader.currentSpeedKmh;
      }}

      follower.headwayMeters = leaderGap;
      const minSafeGap = vehConfigs[follower.type].minGap;

      if(leaderGap <= minSafeGap) {{
        // STOP to prevent collision
        follower.currentSpeedKmh = Math.max(0, Math.min(follower.currentSpeedKmh, leaderSpeed));
        follower.isBraking = true;
        // Hold spacing buffer
        if(i > 0) {{
          follower.longPos = list[i - 1].longPos - minSafeGap;
        }} else if(isRoadBlocked) {{
          follower.longPos = Math.max(0, (road.len || 100) - minSafeGap);
        }}
      }} else if(leaderGap < minSafeGap * 2.8) {{
        // Smooth deceleration headway
        const ratio = (leaderGap - minSafeGap) / (minSafeGap * 1.8);
        follower.currentSpeedKmh = Math.min(follower.currentSpeedKmh, Math.max(5, leaderSpeed + (follower.baseSpeedKmh - leaderSpeed) * ratio));
        follower.isBraking = true;
      }} else {{
        follower.isBraking = false;
      }}
    }}
  }}
}}

// ==========================================
// 6. TRAFFIC PREDICTION ENGINE (SPILLOVER & BOTTLENECK FORECAST)
// ==========================================
function initPredictRoadSelector() {{
  const sel = document.getElementById("sel-predict-road");
  sel.innerHTML = "<option value=''>-- Select Road Corridor to Simulate Block --</option>";
  roads.filter(r => r.cap >= 800 || r.n.includes('Salai') || r.n.includes('Road') || r.n.includes('Street')).slice(0, 45).forEach(r => {{
    const opt = document.createElement("option");
    opt.value = r.i;
    opt.textContent = `${{r.n}} (Cap: ${{r.cap}} veh/hr, ${{r.w}}m)`;
    sel.appendChild(opt);
  }});
}}

function runTrafficPrediction(roadIdxStr) {{
  if(!roadIdxStr) {{ clearPrediction(); return; }}
  const roadIdx = parseInt(roadIdxStr, 10);
  activePredictedRoadIdx = roadIdx;
  const bRoad = roads[roadIdx];
  if(!bRoad) return;

  // Clear previous predictions
  roads.forEach(r => {{ delete r.predVC; delete r.predSurge; }});

  // Calculate displaced flow
  const displacedVolume = Math.round(bRoad.cap * 0.85);

  // Find bypass streets using topological adjacency and Dijkstra detour
  const directDetour = dijkstraPath(
    (bRoad.ns && bRoad.ns[0]) ? bRoad.ns[0].idx : 0,
    (bRoad.ne && bRoad.ne[0]) ? bRoad.ne[0].idx : 1
  ) || [];

  const secondaryDetour = [];
  roads.forEach(r => {{
    if(r.i !== roadIdx && !directDetour.includes(r.i)) {{
      // Proximity to blocked road
      const d = Math.hypot(r.p[0][0] - bRoad.p[0][0], r.p[0][1] - bRoad.p[0][1]);
      if(d < 0.008 && (r.t === 'primary' || r.t === 'secondary' || r.t === 'tertiary')) {{
        secondaryDetour.push(r.i);
      }}
    }}
  }});

  // Assign predicted volumes:
  // Primary bypass absorbs 60% of displaced flow
  // Secondary roads absorb 30%
  // Local network absorbs 10%
  const bottlenecks = [];

  directDetour.forEach(rIdx => {{
    const r = roads[rIdx];
    const surge = Math.round((displacedVolume * 0.6) / Math.max(1, directDetour.length));
    const baseFlow = Math.round(r.cap * 0.45);
    const predTotal = baseFlow + surge;
    const vc = Number((predTotal / r.cap).toFixed(2));
    r.predVC = vc;
    r.predSurge = Math.round((surge / baseFlow) * 100);
    bottlenecks.push({{ r, vc, surge: r.predSurge, rank: 1 }});
  }});

  secondaryDetour.forEach(rIdx => {{
    const r = roads[rIdx];
    const surge = Math.round((displacedVolume * 0.3) / Math.max(1, secondaryDetour.length));
    const baseFlow = Math.round(r.cap * 0.4);
    const predTotal = baseFlow + surge;
    const vc = Number((predTotal / r.cap).toFixed(2));
    r.predVC = vc;
    r.predSurge = Math.round((surge / baseFlow) * 100);
    bottlenecks.push({{ r, vc, surge: r.predSurge, rank: 2 }});
  }});

  // Sort bottlenecks by V/C ratio descending
  bottlenecks.sort((a,b) => b.vc - a.vc);

  // Render prediction report
  renderPredictionReport(bRoad, bottlenecks);
  filterRoadStyles();

  // Focus map on blocked corridor
  map.panTo({{ lat: bRoad.p[0][0], lng: bRoad.p[0][1] }});
  map.setZoom(16.5);

  document.getElementById("bs-pred").textContent = `Choke (${{bottlenecks.filter(b=>b.vc>=1.0).length}} Gridlocks)`;
  document.getElementById("bs-pred").style.color = "#ef4444";
}}

function renderPredictionReport(bRoad, bottlenecks) {{
  const reportContainer = document.getElementById("prediction-report");
  const severe = bottlenecks.filter(b => b.vc >= 1.05);
  const heavy = bottlenecks.filter(b => b.vc >= 0.85 && b.vc < 1.05);

  const topChokeList = bottlenecks.slice(0, 4).map((b, idx) => `
    <div class="predict-card" style="border-left:4px solid ${{b.vc>=1.1?'#ef4444':b.vc>=0.85?'#f97316':'#eab308'}}">
      <div class="predict-header">
        <span>#${{idx+1}} ${{b.r.n}}</span>
        <span class="surge-val" style="color:${{b.vc>=1.1?'#ef4444':'#fbbf24'}}">+${{b.surge}}% SURGE</span>
      </div>
      <div style="font-size:10px;color:#94a3b8;margin-top:2px">
        Capacity: ${{b.r.cap}} veh/hr | Predicted V/C: <b style="color:#fff">${{b.vc}}</b> (${{b.vc>=1.1?'🔴 SEVERE GRIDLOCK':b.vc>=0.85?'🟠 HEAVY CHOKE':'🟡 MODERATE'}})
      </div>
    </div>
  `).join('');

  const estQueueMeters = Math.min(1400, Math.round(bottlenecks.length * 180 + 350));
  const estOnsetMins = Math.max(5, Math.round(18 - (bottlenecks.length * 1.5)));

  reportContainer.innerHTML = `
    <div style="background:#20111a;border:1px solid #ef444466;border-radius:8px;padding:10px;margin-bottom:9px">
      <div style="font-size:11px;font-weight:700;color:#f87171">⚠️ INCIDENT IMPACT FORECAST</div>
      <b style="font-size:13px;color:#fff">${{bRoad.n}}</b>
      <div style="font-size:10px;color:#cbd5e1;margin-top:3px">
        Capacity: ${{bRoad.cap}} veh/h | Displaced Traffic: ~${{Math.round(bRoad.cap*0.85)}} veh/h
      </div>
    </div>

    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px">
      <div style="background:#0f1833;padding:8px;border-radius:7px;text-align:center;border:1px solid #1e2d54">
        <div style="font-size:16px;font-weight:800;color:#ef4444">${{estQueueMeters}} m</div>
        <div style="font-size:8px;color:#94a3b8;text-transform:uppercase">Projected Tailback Queue</div>
      </div>
      <div style="background:#0f1833;padding:8px;border-radius:7px;text-align:center;border:1px solid #1e2d54">
        <div style="font-size:16px;font-weight:800;color:#fbbf24">${{estOnsetMins}} mins</div>
        <div style="font-size:8px;color:#94a3b8;text-transform:uppercase">Gridlock Onset Window</div>
      </div>
    </div>

    <div style="font-size:11px;font-weight:700;color:#00ffc8;margin-bottom:6px">🚨 Top Predicted Choke Points:</div>
    ${{topChokeList || '<p style="color:#64748b;font-size:11px">Local cul-de-sac. Minimal network spillover.</p>'}}

    <div style="background:#0b1329;border:1px solid #1e294b;border-radius:7px;padding:9px;margin-top:8px;font-size:10.5px;line-height:1.5">
      👮 <b>Traffic Police Mitigation Plan:</b><br>
      &bull; Deploy wardens immediately at <b>Kalmandapam Junction</b>.<br>
      &bull; Divert commercial trucks to <b>Kamarajar Salai (Beach Rd)</b>.<br>
      &bull; Suspend curbside parking along <b>Cemetery Road</b> to preserve 2 full lanes.
    </div>
  `;
}}

function clearPrediction() {{
  roads.forEach(r => {{ delete r.predVC; delete r.predSurge; }});
  activePredictedRoadIdx = null;
  document.getElementById("sel-predict-road").value = "";
  document.getElementById("prediction-report").innerHTML = `
    <div style="color:#64748b;font-size:11px;text-align:center;padding:12px">
      Select a road corridor above or click any street on the map to run the predictive congestion assignment model.
    </div>
  `;
  document.getElementById("bs-pred").textContent = "Normal";
  document.getElementById("bs-pred").style.color = "#2dd4bf";
  filterRoadStyles();
}}

function predictPresetBlock(preset) {{
  if(preset === 'bridge') {{
    document.getElementById("sel-predict-road").value = 0;
    runTrafficPrediction(0);
  }} else if(preset === 'subway') {{
    document.getElementById("sel-predict-road").value = 11;
    runTrafficPrediction(11);
  }}
}}

function togglePredictionHeatmap(enable) {{
  showPredictionHeatmap = enable;
  filterRoadStyles();
}}

// ==========================================
// 7. DIJKSTRA PATHFINDING
// ==========================================
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
      
      let cost = 1.0;
      if(vRoad.sm) cost += 2.2;
      if(vRoad.low && rainOn) cost += 3.5;
      if(vRoad.ow && !n.fwd) return;

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
// 8. RAIN CANVAS & STAGNATION
// ==========================================
let rainCtx, rainDrops = [];
function initRainCanvas() {{
  const canvas = document.getElementById("rain-canvas");
  canvas.width = window.innerWidth - 460;
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
// 9. ANIMATION LOOP & UI
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

function setTab(tabId, tabElem) {{
  document.querySelectorAll(".tab-content").forEach(c => c.style.display = "none");
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.getElementById(tabId).style.display = "block";
  tabElem.classList.add("active");
}}

function setSpd(s, btn) {{
  simSpeed = s;
  document.querySelectorAll(".ctrl button").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
}}

function togVeh(type, enable) {{
  vehConfigs[type].enabled = enable;
  vehicles.forEach(v => {{ if(v.type === type && v.marker) v.marker.setMap(enable ? map : null); }});
  rebalanceVehicles();
  updateDashboard();
}}

function updateDashboard() {{
  const activeFleet = vehicles.filter(v => vehConfigs[v.type].enabled).length;
  document.getElementById("bs-v").textContent = activeFleet;

  const baseCong = (timeOfDay>=8&&timeOfDay<=10) || (timeOfDay>=17&&timeOfDay<=20) ? 68 : 36;
  const cong = Math.min(98, baseCong + (rainOn ? rainIntensity * 14 : 0) + blockedRoads.size * 12);
  document.getElementById("bs-c").textContent = `${{cong}}%`;
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
}}

function onTargetPOIChanged(poiId) {{
  selectedTargetPOI = pois.find(p => p.id === poiId) || pois[0];
  rebalanceVehicles();
}}

function onVisitorCountSlider(val) {{
  targetVisitorCount = parseInt(val, 10);
  document.getElementById("lbl-visitor-count").textContent = `${{targetVisitorCount.toLocaleString()}} visitors`;
  rebalanceVehicles();
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
    card.style.cssText = "padding:8px 10px;background:#0d1c33;border-radius:7px;margin-bottom:6px;font-size:11px;border-left:4px solid #0284c7;cursor:pointer";
    card.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;font-weight:700">
        <span>${{s.name}}</span>
        <span class="badge badge-passable" id="wl-depth-${{s.id}}">0 cm</span>
      </div>
      <div style="font-size:9.5px;color:#94a3b8;margin-top:2px">${{s.desc}}</div>
    `;
    card.onclick = () => {{
      map.panTo({{ lat: s.lat, lng: s.lng }});
      map.setZoom(17.5);
    }};
    container.appendChild(card);
  }});
}}

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
        <div style="color:#000;font-family:sans-serif;padding:6px;max-width:230px">
          <div style="font-size:9.5px;color:#0284c7;font-weight:700">${{p.category.toUpperCase()}}</div>
          <b style="font-size:13px">${{p.icon}} ${{p.name}}</b>
          <div style="font-size:11px;color:#475569;margin-top:4px">${{p.desc}}</div>
        </div>`
    }});

    marker.addListener("click", () => info.open(map, marker));
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
    `;
    card.onclick = () => {{
      document.getElementById("sel-target-poi").value = p.id;
      onTargetPOIChanged(p.id);
      map.panTo({{ lat: p.lat, lng: p.lng }});
      map.setZoom(17.5);
    }};
    container.appendChild(card);
  }});
}}

function filterPOICat(cat, btn) {{
  document.querySelectorAll("#tab-pois .btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  renderFilteredPOIs(cat === 'all' ? pois : pois.filter(p => p.category === cat));
}}

function filterPOISearch(q) {{
  const lower = q.toLowerCase();
  renderFilteredPOIs(pois.filter(p => p.name.toLowerCase().includes(lower) || p.desc.toLowerCase().includes(lower)));
}}

window.addEventListener("resize", () => {{
  const c = document.getElementById("rain-canvas");
  if(c) {{ c.width = window.innerWidth - 460; c.height = window.innerHeight; }}
}});
</script>

<script async defer src="https://maps.googleapis.com/maps/api/js?key={apiKey}&callback=initGoogleMap&v=weekly"></script>
</body>
</html>
'''

with open('c:/Users/SAAQIB/areatwin/google_maps_twin.html', 'w', encoding='utf-8') as f:
    f.write(code)

print("google_maps_twin.html compiled successfully with Speed Telemetry, Anti-Collision & Traffic Prediction!")
