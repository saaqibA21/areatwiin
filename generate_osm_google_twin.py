import json

apiKey = "AIzaSyBFzf4K4xzSL2bgBoGUgFUfHY6DxFwa7Ks"

# Load the real OSM roads graph
with open('c:/Users/SAAQIB/areatwin/roads_graph.json', 'r', encoding='utf-8') as f:
    roads_data = json.load(f)

with open('c:/Users/SAAQIB/areatwin/pois_with_roads.json', 'r', encoding='utf-8') as f:
    pois_data = json.load(f)

roads_json = json.dumps(roads_data, separators=(',', ':'), ensure_ascii=False)
pois_json = json.dumps(pois_data, separators=(',', ':'), ensure_ascii=False)

html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Royapuram Digital Twin - Authentic Real-Road Network Simulation</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#050914;color:#f1f5f9;overflow:hidden;height:100vh}}
#app{{display:flex;height:100vh;width:100vw}}
#map-container{{flex:1;position:relative}}
#map{{width:100%;height:100%}}
#rain-canvas{{position:absolute;inset:0;pointer-events:none;z-index:2;display:none}}
#sidebar{{width:420px;background:linear-gradient(180deg,#0a1124 0%,#0c152d 100%);border-left:1px solid #1f2d52;overflow-y:auto;z-index:20;flex-shrink:0;box-shadow:-8px 0 35px rgba(0,0,0,0.7)}}
.panel{{padding:13px 16px;border-bottom:1px solid #1a274c}}
.panel h3{{font-size:12px;text-transform:uppercase;letter-spacing:1.5px;color:#00d4ff;margin-bottom:10px;display:flex;align-items:center;gap:7px}}
.panel h3 span{{font-size:16px}}
.stat-grid{{display:grid;grid-template-columns:1fr 1fr;gap:7px}}
.stat-card{{background:#0f1833;border:1px solid #1c2b54;border-radius:8px;padding:9px;text-align:center}}
.stat-card .val{{font-size:20px;font-weight:700;color:#00ffc8}}
.stat-card .lbl{{font-size:9px;color:#7e8ea8;margin-top:2px;text-transform:uppercase;letter-spacing:0.5px}}
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
.speed-btns{{display:flex;gap:4px}}
input[type=range]{{width:100%;accent-color:#38bdf8;margin:3px 0}}
.list-box{{max-height:220px;overflow-y:auto;padding-right:3px}}
.dest-item{{background:#0e172e;border:1px solid #1a274c;border-radius:7px;padding:8px 10px;margin-bottom:6px}}
.dest-header{{display:flex;justify-content:space-between;align-items:center;font-size:11px;font-weight:600}}
.dest-badge{{font-size:9.5px;padding:2px 7px;border-radius:10px;background:#0369a133;color:#38bdf8;border:1px solid #0284c755;font-weight:700}}
.water-item{{padding:8px 10px;background:#0d1c33;border-radius:7px;margin-bottom:6px;font-size:11px;border-left:4px solid #0284c7}}
.water-item.severe{{border-left-color:#ef4444;background:#20111a}}
.water-item.moderate{{border-left-color:#f59e0b;background:#1c1a0e}}
.water-item .top-row{{display:flex;justify-content:space-between;font-weight:600;margin-bottom:2px}}
.water-item .desc{{font-size:9.5px;color:#94a3b8}}
.water-item .depth-badge{{padding:1px 6px;border-radius:10px;font-size:9.5px;font-weight:700}}
.badge-severe{{background:#ef444422;color:#f87171;border:1px solid #ef444455}}
.badge-moderate{{background:#f59e0b22;color:#fbbf24;border:1px solid #f59e0b55}}
.badge-low{{background:#0284c722;color:#38bdf8;border:1px solid #0284c755}}
.reroute-box{{background:#171305;border:1px solid #d9770655;border-radius:8px;padding:10px;margin-top:8px;font-size:11px;line-height:1.6}}
.reroute-box h4{{color:#fbbf24;margin-bottom:6px;font-size:12px;display:flex;align-items:center;gap:5px}}
#hud{{position:absolute;top:0;left:0;right:0;z-index:10;background:linear-gradient(180deg,rgba(4,8,18,0.96) 0%,rgba(4,8,18,0.4) 75%,transparent 100%);padding:12px 22px;display:flex;align-items:center;justify-content:space-between;pointer-events:none}}
#hud>*{{pointer-events:auto}}
#hud h1{{font-size:18px;color:#f8fafc;font-weight:700;display:flex;align-items:center;gap:8px}}
#hud h1 span.tag{{font-size:11px;color:#38bdf8;font-weight:500;background:#0369a133;border:1px solid #0284c766;padding:2px 8px;border-radius:12px}}
#time-disp{{font-size:13px;color:#fcd34d;background:#0f172a;padding:5px 14px;border-radius:20px;border:1px solid #334155;font-weight:600;box-shadow:0 0 15px rgba(0,0,0,0.5)}}
#bottom-bar{{position:absolute;bottom:0;left:0;right:420px;z-index:10;background:linear-gradient(transparent,rgba(4,8,18,0.96) 30%);padding:10px 20px;display:flex;gap:12px;justify-content:center;pointer-events:none}}
#bottom-bar>*{{pointer-events:auto}}
.bs{{text-align:center;background:#0f172acc;backdrop-filter:blur(6px);border:1px solid #1e293b;border-radius:8px;padding:8px 15px;min-width:105px}}
.bs .v{{font-size:16px;font-weight:700;color:#2dd4bf}}
.bs .l{{font-size:8.5px;color:#94a3b8;text-transform:uppercase;margin-top:2px;letter-spacing:0.5px}}
.cbar{{width:100%;height:6px;background:#1e293b;border-radius:3px;margin-top:6px;overflow:hidden}}
.cfill{{height:100%;border-radius:3px;transition:width .5s,background .5s}}
::-webkit-scrollbar{{width:5px}}
::-webkit-scrollbar-track{{background:#030712}}
::-webkit-scrollbar-thumb{{background:#1e294b;border-radius:3px}}
</style>
</head>
<body>
<div id="app">
<div id="map-container">
  <div id="hud">
    <h1>🏙️ Royapuram Digital Twin <span class="tag">Authentic Real-Road Network (848 Streets)</span></h1>
    <div style="display:flex;align-items:center;gap:10px">
      <a href="index.html" class="btn" style="text-decoration:none;display:inline-block">🏙️ Switch to 3D Three.js Twin</a>
      <div id="time-disp">🕐 08:00 AM</div>
    </div>
  </div>
  <canvas id="rain-canvas"></canvas>
  <div id="map"></div>
  <div id="bottom-bar">
    <div class="bs"><div class="v" id="bs-v">0</div><div class="l">Live Fleet</div></div>
    <div class="bs"><div class="v" id="bs-s">0 km/h</div><div class="l">Avg Speed</div></div>
    <div class="bs"><div class="v" id="bs-c">0%</div><div class="l">Congestion</div></div>
    <div class="bs"><div class="v" id="bs-r">Dry</div><div class="l">Monsoon Rain</div></div>
    <div class="bs"><div class="v" id="bs-w">0 cm</div><div class="l">Water Stagnant</div></div>
    <div class="bs"><div class="v" id="bs-b">0</div><div class="l">Blocked Roads</div></div>
  </div>
</div>
<div id="sidebar">
  <!-- Simulation Controls -->
  <div class="panel">
    <h3><span>⚙️</span> Simulation Controls</h3>
    <div class="ctrl"><label>Map View Mode</label>
      <div style="display:flex;gap:4px">
        <button class="btn active" id="btn-sat" onclick="setMapType('hybrid')">🛰️ Satellite</button>
        <button class="btn" id="btn-road" onclick="setMapType('roadmap')">🗺️ Roads</button>
      </div>
    </div>
    <div class="ctrl"><label>Show Road Track Overlays</label>
      <label class="toggle"><input type="checkbox" id="road-lines-tog" checked onchange="toggleRoadLines(this.checked)"><span class="sl"></span></label>
    </div>
    <div class="ctrl"><label>Google Live Traffic Layer</label>
      <label class="toggle"><input type="checkbox" id="traffic-tog" onchange="toggleGoogleTraffic(this.checked)"><span class="sl"></span></label>
    </div>
    <div class="ctrl"><label>Simulation State</label>
      <div style="display:flex;gap:5px">
        <button class="btn active" id="btn-play" onclick="toggleSim(true)">▶ Play</button>
        <button class="btn" id="btn-pause" onclick="toggleSim(false)">⏸ Pause</button>
      </div>
    </div>
    <div class="ctrl"><label>Speed Multiplier</label>
      <div class="speed-btns">
        <button class="btn active" onclick="setSpd(1,this)">1×</button>
        <button class="btn" onclick="setSpd(2,this)">2×</button>
        <button class="btn" onclick="setSpd(4,this)">4×</button>
      </div>
    </div>
    <div class="ctrl"><label>Time of Day</label><span id="tod-lbl" style="font-size:11px;color:#fcd34d;font-weight:600">Morning Rush</span></div>
    <input type="range" id="tod-sl" min="0" max="23" value="8" oninput="setTOD(this.value)">
    <div class="ctrl" style="margin-top:6px"><label>🚧 Interactive Road Block Mode</label>
      <label class="toggle"><input type="checkbox" id="blk-mode" onchange="blockMode=this.checked"><span class="sl"></span></label>
    </div>
    <button class="btn danger" onclick="clearBlocks()" style="width:100%;margin-top:4px">✖ Clear All Blocked Roads</button>
    <div class="ctrl" style="margin-top:8px"><label>🎥 3D Camera Angles</label>
      <div style="display:flex;gap:3px;flex-wrap:wrap">
        <button class="btn" onclick="tiltCam(0)">2D Flat</button>
        <button class="btn" onclick="tiltCam(45)">3D Tilt 45°</button>
        <button class="btn" onclick="tiltCam(65)">3D Tilt 65°</button>
        <button class="btn" onclick="rotateCam()">Rotate 45°</button>
      </div>
    </div>
  </div>

  <!-- Target Destination Traffic Allocator -->
  <div class="panel">
    <h3><span>🎯</span> Destination Traffic Allocator</h3>
    <p style="font-size:10px;color:#94a3b8;margin-bottom:8px">Change vehicles dispatched to each landmark — watch vehicles route dynamically through authentic streets:</p>
    <div class="list-box" id="dest-sliders"></div>
  </div>

  <!-- Rain & Water Stagnation Simulation -->
  <div class="panel">
    <h3><span>🌧️</span> Rain & Water Stoppage (Flooding)</h3>
    <div class="ctrl"><label>Monsoon Rainfall</label><label class="toggle"><input type="checkbox" id="rain-tog" onchange="toggleRain(this.checked)"><span class="sl"></span></label></div>
    <div class="ctrl"><label>Rainfall Intensity</label><span id="rain-lbl" style="font-size:11px;color:#38bdf8;font-weight:600">Light Shower</span></div>
    <input type="range" id="rain-sl" min="1" max="3" value="1" oninput="setRainInt(this.value)">
    <div style="margin-top:8px;font-size:11px;color:#94a3b8;font-weight:600">🌊 Known Stagnation Hotspots:</div>
    <div id="water-list" style="margin-top:6px"></div>
  </div>

  <!-- Multi-Modal Fleet -->
  <div class="panel">
    <h3><span>🚗</span> Multi-Modal Vehicle Fleet</h3>
    <div class="ctrl"><label>🚗 Sedans & Cars</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('car',this.checked)"><span class="sl"></span></label></div>
    <div class="ctrl"><label>🏍️ Bikes / Two-Wheelers</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('bike',this.checked)"><span class="sl"></span></label></div>
    <div class="ctrl"><label>🛺 Iconic Auto-Rickshaws</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('auto',this.checked)"><span class="sl"></span></label></div>
    <div class="ctrl"><label>🚌 Chennai MTC City Buses</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('bus',this.checked)"><span class="sl"></span></label></div>
    <div class="stat-grid" style="margin-top:8px">
      <div class="stat-card"><div class="val" id="c-car">0</div><div class="lbl">Cars</div></div>
      <div class="stat-card"><div class="val" id="c-bike">0</div><div class="lbl">Bikes</div></div>
      <div class="stat-card"><div class="val" id="c-auto">0</div><div class="lbl">Autos</div></div>
      <div class="stat-card"><div class="val" id="c-bus">0</div><div class="lbl">Buses</div></div>
    </div>
  </div>

  <!-- Rerouting Analysis -->
  <div class="panel">
    <h3><span>🔀</span> Dynamic Rerouting Engine</h3>
    <div id="reroute-box" class="reroute-box">
      <p style="color:#94a3b8">Turn on <b style="color:#fcd34d">Road Block Mode</b> and click any road on Google Maps to analyze traffic displacement & alternate bypasses.</p>
    </div>
  </div>
</div>
</div>

<script>
// ==========================================
// 1. DATA INITIALIZATION (848 REAL ROADS)
// ==========================================
const apiKey = "AIzaSyBFzf4K4xzSL2bgBoGUgFUfHY6DxFwa7Ks";
const roads = {roads_json};
const pois = {pois_json};

const waterlogSpots = [
  {{id:'wl_stanley',name:'Stanley Subway Underpass',lat:13.0992,lng:80.2872,baseDepth:65,radius:50,
   desc:'Depressed railway underpass; chronic drainage blockage. Impassable in heavy rain.'}},
  {{id:'wl_bridge_descent',name:'Royapuram ROB Bridge Slope',lat:13.1034,lng:80.2936,baseDepth:35,radius:45,
   desc:'Water collects at the foot of Royapuram bridge slope curve before joining Beach Rd.'}},
  {{id:'wl_s_madha',name:'S. Madha Church St Dip',lat:13.1068,lng:80.2946,baseDepth:40,radius:40,
   desc:'Low-lying residential basin near cemetery.'}},
  {{id:'wl_harbour',name:'Kasimedu Wharf Gate Basin',lat:13.1128,lng:80.2982,baseDepth:30,radius:50,
   desc:'Coastal runoff from fish auction sheds.'}}
];

let map, trafficLayer;
const roadPolylines = [];
const blockedRoads = new Set();
let blockMode = false;
let showRoadLines = true;
const destVehTargets = {{}};
const waterCircles = {{}};
let waterAccumulationLevel = 0;

let simRunning = true, simSpeed = 1, timeOfDay = 8, rainOn = false, rainIntensity = 1;

// Modality configs: speeds in coordinate delta per millisecond
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

  // Render 848 Real Street Centerlines aligned exactly with satellite asphalt
  renderRoads();

  // Render Distinct Landmarks
  renderLandmarks();

  // Render Water Puddles
  renderWaterPuddles();

  // UI Setup
  initDestinationSliders();
  initWaterList();
  initRainCanvas();
  rebalanceVehicles();
  updateDashboard();

  lastFrameTime = performance.now();
  requestAnimationFrame(animateSimulation);
}}

function renderRoads() {{
  roads.forEach(r => {{
    const path = r.p.map(p => ({{ lat: p[0], lng: p[1] }}));
    const isMajor = r.t === 'primary' || r.t === 'trunk' || r.t === 'secondary';
    const isMedium = r.t === 'tertiary';
    const color = isMajor ? '#facc15' : isMedium ? '#38bdf8' : '#e2e8f0';
    const weight = isMajor ? 4.5 : isMedium ? 3.0 : 1.8;
    const opacity = isMajor ? 0.75 : isMedium ? 0.6 : 0.4;

    const polyline = new google.maps.Polyline({{
      path,
      geodesic: true,
      strokeColor: color,
      strokeOpacity: opacity,
      strokeWeight: weight,
      map: showRoadLines ? map : null
    }});

    polyline.roadIndex = r.i;
    polyline.roadId = r.id;
    polyline.roadName = r.n;

    polyline.addListener("click", () => {{
      if(blockMode) {{
        toggleRoadBlock(r.i);
      }} else {{
        new google.maps.InfoWindow({{
          content: `<div style="color:#000;font-size:12px"><b>🛣️ ${{r.n}}</b><br><span style="color:#64748b">Type: ${{r.t}} | Width: ${{r.w}}m</span></div>`,
          position: path[Math.floor(path.length/2)]
        }}).open(map);
      }}
    }});

    roadPolylines[r.i] = polyline;
  }});
}}

function toggleRoadLines(show) {{
  showRoadLines = show;
  roadPolylines.forEach(p => {{
    if(p) p.setMap(show ? map : null);
  }});
}}

function renderLandmarks() {{
  pois.forEach(p => {{
    destVehTargets[p.id] = p.defaultVeh;

    const marker = new google.maps.Marker({{
      position: {{ lat: p.lat, lng: p.lng }},
      map: map,
      title: `${{p.icon}} ${{p.name}}`,
      label: {{
        text: p.icon,
        fontSize: "20px"
      }}
    }});

    const infoWindow = new google.maps.InfoWindow({{
      content: `
        <div style="color:#000;font-family:sans-serif;padding:6px">
          <b style="font-size:13px">${{p.icon}} ${{p.name}}</b><br>
          <span style="font-size:11px;color:#0284c7;font-weight:700">Dispatched Traffic: ${{p.defaultVeh}} veh/hr</span>
        </div>`
    }});

    marker.addListener("click", () => {{
      infoWindow.open(map, marker);
    }});
  }});
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
// 3. VEHICLE GRAPH NAVIGATION (100% ON-STREET)
// ==========================================
function spawnVehicle(poiId) {{
  const poi = pois.find(p => p.id === poiId) || pois[0];
  const types = ['car','bike','bike','auto','auto','car'];
  if(poi.id==='poi_station' || poi.id==='poi_metro' || poi.id==='poi_stanley') types.push('bus');
  const type = types[Math.floor(Math.random()*types.length)];
  const cfg = vehConfigs[type];
  if(!cfg.enabled) return null;

  // Pick a road near the destination or any valid road
  let candidateIndices = poi.nearest_roads ? [...poi.nearest_roads] : [];
  candidateIndices = candidateIndices.filter(idx => !blockedRoads.has(idx));
  
  let roadIdx;
  if(candidateIndices.length && Math.random() < 0.6) {{
    roadIdx = candidateIndices[Math.floor(Math.random()*candidateIndices.length)];
  }} else {{
    // Pick any connected road in the city
    const unblocked = roads.filter(r => !blockedRoads.has(r.i) && (type!=='bus' || r.b));
    if(!unblocked.length) return null;
    roadIdx = unblocked[Math.floor(Math.random()*unblocked.length)].i;
  }}

  const road = roads[roadIdx];
  const fwd = Math.random() > 0.5;
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
  let totalDesired = 0;
  pois.forEach(p => {{ totalDesired += destVehTargets[p.id] || 0; }});
  const targetFleet = Math.max(20, Math.min(90, Math.round(totalDesired / 7.0)));

  while(vehicles.length > targetFleet) {{
    const v = vehicles.pop();
    if(v && v.marker) v.marker.setMap(null);
  }}

  while(vehicles.length < targetFleet) {{
    let r = Math.random() * totalDesired;
    let chosenPOI = pois[0];
    for(const p of pois) {{
      r -= (destVehTargets[p.id] || 0);
      if(r <= 0) {{ chosenPOI = p; break; }}
    }}
    const v = spawnVehicle(chosenPOI.id);
    if(v) vehicles.push(v);
    else break;
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
    
    // Segment vector from pA to pB
    const dLat = pB[0] - pA[0];
    const dLng = pB[1] - pA[1];
    const segLen = Math.hypot(dLat, dLng * Math.cos(pA[0] * Math.PI / 180));
    
    // Speed along segment
    const effectiveSpeed = v.speed * rainSlow * simSpeed;
    const progressInc = (effectiveSpeed * dtMs) / Math.max(segLen, 0.00005);
    
    if(v.fwd) {{
      v.progress += progressInc;
      if(v.progress >= 1.0) {{
        v.progress = 0.0;
        v.segIdx++;
        // Check if road finished
        if(v.segIdx >= road.p.length - 1) {{
          // At road end -> choose connected street from r.ne
          const nextConns = (road.ne || []).filter(c => !blockedRoads.has(c.idx) && (v.type!=='bus' || roads[c.idx].b));
          if(nextConns.length > 0) {{
            const chosen = nextConns[Math.floor(Math.random() * nextConns.length)];
            v.roadIdx = chosen.idx;
            const nextRoad = roads[chosen.idx];
            v.fwd = chosen.fwd;
            v.segIdx = v.fwd ? 0 : nextRoad.p.length - 2;
          }} else {{
            // Dead end or all next blocked -> U-turn
            v.fwd = false;
            v.segIdx = road.p.length - 2;
          }}
        }}
      }}
    }} else {{
      // Moving backward along segments (from end to start)
      v.progress += progressInc;
      if(v.progress >= 1.0) {{
        v.progress = 0.0;
        v.segIdx--;
        // Check if reached start of road
        if(v.segIdx < 0) {{
          // At road start -> choose connected street from r.ns
          const nextConns = (road.ns || []).filter(c => !blockedRoads.has(c.idx) && (v.type!=='bus' || roads[c.idx].b));
          if(nextConns.length > 0) {{
            const chosen = nextConns[Math.floor(Math.random() * nextConns.length)];
            v.roadIdx = chosen.idx;
            const nextRoad = roads[chosen.idx];
            v.fwd = chosen.fwd;
            v.segIdx = v.fwd ? 0 : nextRoad.p.length - 2;
          }} else {{
            // Dead end or all next blocked -> U-turn
            v.fwd = true;
            v.segIdx = 0;
          }}
        }}
      }}
    }}

    // Current interpolated coordinate strictly on real street
    const curRoad = roads[v.roadIdx];
    const curA = curRoad.p[v.segIdx];
    const curB = curRoad.p[v.segIdx + 1];
    const curProg = v.fwd ? v.progress : (1.0 - v.progress);
    
    const lat = curA[0] + (curB[0] - curA[0]) * curProg;
    const lng = curA[1] + (curB[1] - curA[1]) * curProg;
    v.marker.setPosition({{ lat, lng }});

    // Heading orientation (forward or backward along segment)
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
// 4. RAIN CANVAS SYSTEM
// ==========================================
let rainCtx, rainDrops = [];
function initRainCanvas() {{
  const canvas = document.getElementById("rain-canvas");
  canvas.width = window.innerWidth - 420;
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

// ==========================================
// 5. ANIMATION LOOP
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

function updateWaterlogVisuals() {{
  waterlogSpots.forEach(s => {{
    const c = waterCircles[s.id];
    if(!c) return;
    const factor = waterAccumulationLevel / 100.0;
    const curDepth = Math.round(s.baseDepth * factor);
    const elem = document.getElementById(`wl-depth-${{s.id}}`);
    if(elem) {{
      elem.textContent = `${{curDepth}} cm`;
      elem.className = `depth-badge ${{curDepth > 45 ? 'badge-severe' : curDepth > 20 ? 'badge-moderate' : 'badge-low'}}`;
    }}
    c.setOptions({{
      fillOpacity: factor * 0.45,
      strokeOpacity: factor * 0.9,
      strokeColor: curDepth > 45 ? "#ef4444" : curDepth > 20 ? "#f59e0b" : "#0284c7"
    }});
  }});
  document.getElementById("bs-w").textContent = `${{Math.round(45 * (waterAccumulationLevel/100.0))}} cm`;
}}

// ==========================================
// 6. ROAD BLOCKING & REROUTING ENGINE
// ==========================================
function toggleRoadBlock(roadIdx) {{
  const r = roads[roadIdx];
  if(!r) return;

  const poly = roadPolylines[roadIdx];
  if(blockedRoads.has(roadIdx)) {{
    blockedRoads.delete(roadIdx);
    if(poly) {{
      const isMajor = r.t === 'primary' || r.t === 'trunk' || r.t === 'secondary';
      poly.setOptions({{ strokeColor: isMajor ? '#facc15' : '#38bdf8', strokeWeight: isMajor ? 4.5 : 2.5 }});
    }}
  }} else {{
    blockedRoads.add(roadIdx);
    if(poly) {{
      poly.setOptions({{ strokeColor: '#ef4444', strokeWeight: 6 }});
    }}
  }}
  updateReroutePanel(roadIdx);
  updateDashboard();
}}

function clearBlocks() {{
  blockedRoads.forEach(roadIdx => {{
    const r = roads[roadIdx];
    const poly = roadPolylines[roadIdx];
    if(poly && r) {{
      const isMajor = r.t === 'primary' || r.t === 'trunk' || r.t === 'secondary';
      poly.setOptions({{ strokeColor: isMajor ? '#facc15' : '#38bdf8', strokeWeight: isMajor ? 4.5 : 2.5 }});
    }}
  }});
  blockedRoads.clear();
  document.getElementById("reroute-box").innerHTML = '<p style="color:#94a3b8">Turn on <b style="color:#fcd34d">Road Block Mode</b> and click any road to analyze traffic displacement & alternate bypasses.</p>';
  updateDashboard();
}}

function updateReroutePanel(lastClickedIdx) {{
  const box = document.getElementById("reroute-box");
  if(blockedRoads.size === 0) {{
    box.innerHTML = '<p style="color:#94a3b8">No roads currently blocked. All 848 real street corridors flowing smoothly.</p>';
    return;
  }}
  const lastR = roads[lastClickedIdx];
  let bypassNames = [];
  if(lastR) {{
    const neighbors = [...(lastR.ns||[]), ...(lastR.ne||[])];
    neighbors.forEach(n => {{
      const nr = roads[n.idx];
      if(nr && nr.n && !bypassNames.includes(nr.n)) bypassNames.push(nr.n);
    }});
  }}
  const bypassText = bypassNames.length ? bypassNames.slice(0, 4).join(', ') : 'Parallel George Town grid alleys';

  box.innerHTML = `
    <h4>🚧 Incident Active: ${{blockedRoads.size}} Corridors Blocked</h4>
    <div style="margin:4px 0;color:#f87171"><b>Blocked:</b> ${{lastR ? lastR.n : 'Selected Street'}}</div>
    <div style="margin:4px 0;color:#38bdf8"><b>Live Rerouting:</b> Traffic displaced onto ${{bypassText}}</div>
    <div style="margin:4px 0;color:#fcd34d"><b>Network Congestion:</b> +${{blockedRoads.size * 14}}% elevated delay in Royapuram sector</div>
  `;
}}

// ==========================================
// 7. UI CONTROLS & DASHBOARD
// ==========================================
function initDestinationSliders() {{
  const container = document.getElementById("dest-sliders");
  container.innerHTML = "";
  pois.forEach(p => {{
    const item = document.createElement("div");
    item.className = "dest-item";
    item.innerHTML = `
      <div class="dest-header">
        <span>${{p.icon}} ${{p.name}}</span>
        <span class="dest-badge" id="badge-${{p.id}}">${{p.defaultVeh}} veh/h</span>
      </div>
      <input type="range" min="10" max="300" value="${{p.defaultVeh}}" 
        oninput="updateDestTraffic('${{p.id}}', this.value)">
    `;
    container.appendChild(item);
  }});
}}

function updateDestTraffic(id, val) {{
  destVehTargets[id] = parseInt(val, 10);
  const badge = document.getElementById(`badge-${{id}}`);
  if(badge) badge.textContent = `${{val}} veh/h`;
  rebalanceVehicles();
  updateDashboard();
}}

function initWaterList() {{
  const list = document.getElementById("water-list");
  list.innerHTML = "";
  waterlogSpots.forEach(s => {{
    const item = document.createElement("div");
    item.className = "water-item";
    item.innerHTML = `
      <div class="top-row">
        <span>${{s.name}}</span>
        <span class="depth-badge badge-low" id="wl-depth-${{s.id}}">0 cm</span>
      </div>
      <div class="desc">${{s.desc}}</div>
    `;
    list.appendChild(item);
  }});
}}

function toggleRain(enable) {{
  rainOn = enable;
  document.getElementById("rain-canvas").style.display = enable ? "block" : "none";
  document.getElementById("bs-r").textContent = enable ? (rainIntensity===1?'Light':rainIntensity===2?'Moderate':'Heavy') : 'Dry';
  if(!enable) {{
    if(rainCtx) {{
      const c = document.getElementById("rain-canvas");
      rainCtx.clearRect(0, 0, c.width, c.height);
    }}
  }}
  updateDashboard();
}}

function setRainInt(val) {{
  rainIntensity = parseInt(val, 10);
  const labels = ["", "Light Shower", "Moderate Monsoon", "Heavy Cloudburst"];
  document.getElementById("rain-lbl").textContent = labels[rainIntensity];
  if(rainOn) document.getElementById("bs-r").textContent = ["", "Light", "Moderate", "Heavy"][rainIntensity];
}}

function toggleSim(run) {{
  simRunning = run;
  document.getElementById("btn-play").className = `btn ${{run ? 'active' : ''}}`;
  document.getElementById("btn-pause").className = `btn ${{!run ? 'active' : ''}}`;
}}

function setSpd(s, btn) {{
  simSpeed = s;
  document.querySelectorAll(".speed-btns .btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
}}

function setTOD(h) {{
  timeOfDay = parseInt(h, 10);
  const hourStr = timeOfDay === 0 ? "12:00 AM" : timeOfDay < 12 ? `${{timeOfDay}}:00 AM` : timeOfDay === 12 ? "12:00 PM" : `${{timeOfDay-12}}:00 PM`;
  document.getElementById("time-disp").textContent = `🕐 ${{hourStr}}`;
  const lbl = timeOfDay >= 7 && timeOfDay <= 10 ? "Morning Rush" :
              timeOfDay >= 11 && timeOfDay <= 16 ? "Midday Commercial" :
              timeOfDay >= 17 && timeOfDay <= 21 ? "Evening Peak" : "Late Night Quiet";
  document.getElementById("tod-lbl").textContent = lbl;
  updateDashboard();
}}

function togVeh(type, enable) {{
  vehConfigs[type].enabled = enable;
  vehicles.forEach(v => {{
    if(v.type === type) v.marker.setMap(enable ? map : null);
  }});
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

function tiltCam(t) {{
  if(map) map.setTilt(t);
}}

function rotateCam() {{
  if(map) map.setHeading((map.getHeading() || 0) + 45);
}}

function updateDashboard() {{
  const activeFleet = vehicles.filter(v => vehConfigs[v.type].enabled).length;
  document.getElementById("bs-v").textContent = activeFleet;

  // Counts by type
  const counts = {{ car:0, bike:0, auto:0, bus:0 }};
  vehicles.forEach(v => {{ if(counts[v.type]!==undefined) counts[v.type]++; }});
  document.getElementById("c-car").textContent = counts.car;
  document.getElementById("c-bike").textContent = counts.bike;
  document.getElementById("c-auto").textContent = counts.auto;
  document.getElementById("c-bus").textContent = counts.bus;

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
  if(c) {{ c.width = window.innerWidth - 420; c.height = window.innerHeight; }}
}});
</script>

<!-- Google Maps JavaScript API with User Key -->
<script async defer src="https://maps.googleapis.com/maps/api/js?key={apiKey}&callback=initGoogleMap&v=weekly"></script>
</body>
</html>
'''

with open('c:/Users/SAAQIB/areatwin/google_maps_twin.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("google_maps_twin.html generated successfully with all 848 real OSM streets!")
