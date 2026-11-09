import json

with open("c:/Users/SAAQIB/areatwin/accurate_roads.json", "r", encoding="utf-8") as f:
    roads_data = json.load(f)

roads_json_str = json.dumps(roads_data, ensure_ascii=False)

html_code = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Royapuram Google Maps Digital Twin - Clean Realistic Roads</title>
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
.stat-card.warn .val{{color:#ffb703}}
.stat-card.danger .val{{color:#ff3366}}
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
.road-tag{{font-size:10px;font-weight:600}}
::-webkit-scrollbar{{width:5px}}
::-webkit-scrollbar-track{{background:#030712}}
::-webkit-scrollbar-thumb{{background:#1e294b;border-radius:3px}}
</style>
</head>
<body>
<div id="app">
<div id="map-container">
  <div id="hud">
    <h1>🏙️ Royapuram Digital Twin <span class="tag">Google Maps Satellite 3D</span></h1>
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
    <div class="ctrl"><label>Show Road Track Lines</label>
      <label class="toggle"><input type="checkbox" id="road-lines-tog" checked onchange="toggleRoadLines(this.checked)"><span class="sl"></span></label>
    </div>
    <div class="ctrl"><label>Google Live Traffic Layer</label>
      <label class="toggle"><input type="checkbox" id="traffic-tog" onchange="toggleGoogleTraffic(this.checked)"><span class="sl"></span></label>
    </div>
    <div class="ctrl"><label>Simulation State</label>
      <div style="display:flex;gap:5px">
        <button class="btn active" id="btn-play" onclick="toggleSim()">▶ Play</button>
        <button class="btn" id="btn-pause" onclick="toggleSim()">⏸ Pause</button>
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
    <p style="font-size:10px;color:#94a3b8;margin-bottom:8px">Change vehicles sent to each landmark — watch live route pathfinding along real streets:</p>
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

  <!-- Vehicle Modalities -->
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

  <!-- Road Traffic & Congestion -->
  <div class="panel">
    <h3><span>🛣️</span> Real Streets Status</h3>
    <div class="list-box" id="road-list" style="max-height:160px"></div>
    <div class="cbar"><div class="cfill" id="cfill" style="width:30%;background:#10b981"></div></div>
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
// 1. DATA INITIALIZATION
// ==========================================
const apiKey = "YOUR_GOOGLE_MAPS_API_KEY";
const roads = {roads_json_str};

// Landmark coordinates verified against real Google Maps Satellite locations
const pois = [
  {{id:'poi_station', name:'Royapuram Railway Station', lat:13.1068, lng:80.2922, icon:'🚂', color:'#f59e0b', defaultVeh:90}},
  {{id:'poi_harbour', name:'Kasimedu Fishing Harbour', lat:13.1140, lng:80.2982, icon:'🐟', color:'#0284c7', defaultVeh:130}},
  {{id:'poi_metro', name:'Mannadi Metro Station', lat:13.0945, lng:80.2902, icon:'🚇', color:'#06b6d4', defaultVeh:150}},
  {{id:'poi_stanley', name:'Stanley Medical College & Hospital', lat:13.0990, lng:80.2875, icon:'🏥', color:'#10b981', defaultVeh:100}},
  {{id:'poi_amman', name:'Arulmigu Angalaparameshwari Temple', lat:13.1082, lng:80.2910, icon:'🛕', color:'#eab308', defaultVeh:65}},
  {{id:'poi_subramania', name:'Subramania Swamy Temple', lat:13.1042, lng:80.2928, icon:'🛕', color:'#facc15', defaultVeh:50}},
  {{id:'poi_stpeters', name:'St. Peter’s Church', lat:13.1030, lng:80.2942, icon:'⛪', color:'#818cf8', defaultVeh:40}},
  {{id:'poi_stanthony', name:'St. Anthony’s Church', lat:13.1028, lng:80.2938, icon:'⛪', color:'#a78bfa', defaultVeh:35}},
  {{id:'poi_theagaraya', name:'Sir Theagaraya College', lat:13.1010, lng:80.2878, icon:'🎓', color:'#14b8a6', defaultVeh:45}},
  {{id:'poi_fire_temple', name:'Parsi Fire Temple (Agiary)', lat:13.1035, lng:80.2936, icon:'🔥', color:'#f97316', defaultVeh:25}}
];

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
const roadPolylines = {{}};
const blockedRoads = new Set();
let blockMode = false;
let showRoadLines = true;
const reroutePolylines = [];
const destVehTargets = {{}};
const waterCircles = {{}};
let waterAccumulationLevel = 0;

let simRunning = true, simSpeed = 1, timeOfDay = 8, rainOn = false, rainIntensity = 1;

const vehConfigs = {{
  car: {{speed: 0.00035, color:'#38bdf8', enabled:true}},
  bike:{{speed: 0.00045, color:'#22c55e', enabled:true}},
  auto:{{speed: 0.00028, color:'#facc15', enabled:true}},
  bus: {{speed: 0.00022, color:'#ef4444', enabled:true}}
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

  // Render Clean Street Centerlines (subtle, aligned strictly with pavement)
  renderRoads();

  // Render Distinct Landmarks
  renderLandmarks();

  // Render Water Puddles
  renderWaterPuddles();

  // UI Setup
  initDestinationSliders();
  initRainCanvas();
  rebalanceVehicles();
  updateDashboard();

  requestAnimationFrame(animateSimulation);
}}

function renderRoads() {{
  roads.forEach(r => {{
    const path = r.pts.map(p => ({{ lat: p[0], lng: p[1] }}));
    const color = r.type === 'highway' ? '#facc15' : r.type === 'arterial' ? '#38bdf8' : '#e2e8f0';

    // Clean subtle road tracks strictly on real pavement
    const polyline = new google.maps.Polyline({{
      path,
      geodesic: true,
      strokeColor: color,
      strokeOpacity: 0.6,
      strokeWeight: r.width >= 6 ? 5 : 3.5,
      map: showRoadLines ? map : null
    }});

    polyline.roadData = r;
    polyline.addListener("click", () => {{
      if(blockMode) {{
        toggleRoadBlock(r.id);
      }}
    }});

    roadPolylines[r.id] = polyline;
  }});
}}

function toggleRoadLines(show) {{
  showRoadLines = show;
  Object.values(roadPolylines).forEach(p => {{
    p.setMap(show ? map : null);
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
        <div style="color:#000;font-family:sans-serif;padding:5px">
          <b style="font-size:13px">${{p.icon}} ${{p.name}}</b><br>
          <span style="font-size:11px;color:#0284c7;font-weight:700">Target Traffic: ${{p.defaultVeh}} veh/hr</span>
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
// 3. VEHICLE SIMULATION (ALIGNED TO REAL STREETS)
// ==========================================
function spawnVehicle(poiId) {{
  const poi = pois.find(p => p.id === poiId) || pois[0];
  const types = ['car','bike','bike','auto','auto','car'];
  if(poi.id==='poi_station' || poi.id==='poi_metro' || poi.id==='poi_stanley') types.push('bus');
  const type = types[Math.floor(Math.random()*types.length)];
  const cfg = vehConfigs[type];
  if(!cfg.enabled) return null;

  const avail = roads.filter(r => !blockedRoads.has(r.id) && (type!=='bus' || r.busRoute));
  if(!avail.length) return null;
  const road = avail[Math.floor(Math.random()*avail.length)];
  const forward = Math.random() > 0.5;
  const path = forward ? [...road.pts] : [...road.pts].reverse();

  // Create clean vehicle symbol (no cluttering dots!)
  const marker = new google.maps.Marker({{
    position: {{ lat: path[0][0], lng: path[0][1] }},
    map: map,
    icon: {{
      path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
      scale: type==='bus'?4.5:type==='car'?3.8:type==='auto'?3.2:2.6,
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
    roadId: road.id,
    path,
    segIdx: 0,
    prog: 0,
    speed: cfg.speed * (0.8 + Math.random()*0.4)
  }};
}}

function rebalanceVehicles() {{
  let totalDesired = 0;
  pois.forEach(p => {{ totalDesired += destVehTargets[p.id] || 0; }});
  const targetFleet = Math.max(16, Math.min(100, Math.round(totalDesired / 6.0)));

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

function updateVehicles(dt) {{
  const rainSlow = rainOn ? [1, 0.72, 0.50, 0.32][rainIntensity] : 1.0;

  vehicles.forEach(v => {{
    if(v.segIdx >= v.path.length - 1) {{
      // Reached street end, pick connected real street
      const lastPt = v.path[v.path.length - 1];
      const avail = roads.filter(r => !blockedRoads.has(r.id) && (v.type!=='bus' || r.busRoute));
      if(avail.length) {{
        // Find street starting near lastPt
        const candidates = [];
        avail.forEach(r => {{
          const d0 = Math.hypot(r.pts[0][0] - lastPt[0], r.pts[0][1] - lastPt[1]);
          const dEnd = Math.hypot(r.pts[r.pts.length-1][0] - lastPt[0], r.pts[r.pts.length-1][1] - lastPt[1]);
          if(d0 < 0.003) candidates.push({{ r, fwd: true }});
          else if(dEnd < 0.003) candidates.push({{ r, fwd: false }});
        }});

        if(candidates.length) {{
          const next = candidates[Math.floor(Math.random()*candidates.length)];
          v.roadId = next.r.id;
          v.path = next.fwd ? [...next.r.pts] : [...next.r.pts].reverse();
        }} else {{
          const nRoad = avail[Math.floor(Math.random()*avail.length)];
          v.roadId = nRoad.id;
          v.path = Math.random()>0.5 ? [...nRoad.pts] : [...nRoad.pts].reverse();
        }}
        v.segIdx = 0;
        v.prog = 0;
      }}
      return;
    }}

    const p1 = v.path[v.segIdx];
    const p2 = v.path[v.segIdx+1];
    const dLat = p2[0] - p1[0];
    const dLng = p2[1] - p1[1];
    const dist = Math.hypot(dLat, dLng);

    const step = (v.speed * rainSlow * simSpeed * dt) / Math.max(dist, 0.0001);
    v.prog += step;

    if(v.prog >= 1) {{
      v.segIdx++;
      v.prog = 0;
    }} else {{
      const curLat = p1[0] + dLat * v.prog;
      const curLng = p1[1] + dLng * v.prog;
      v.marker.setPosition({{ lat: curLat, lng: curLng }});

      // Heading orientation for arrow icon
      const heading = (Math.atan2(dLng, dLat) * 180 / Math.PI + 360) % 360;
      const icon = v.marker.getIcon();
      if(icon) {{
        icon.rotation = heading;
        v.marker.setIcon(icon);
      }}
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

  for(let i=0; i<300; i++) {{
    rainDrops.push({{
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      len: 12 + Math.random()*15,
      speed: 15 + Math.random()*15
    }});
  }}
}}

function updateRain() {{
  if(!rainOn) return;
  const canvas = document.getElementById("rain-canvas");
  rainCtx.clearRect(0, 0, canvas.width, canvas.height);
  rainCtx.strokeStyle = "rgba(147, 197, 253, 0.65)";
  rainCtx.lineWidth = 1.2;

  const dropCount = [0, 80, 180, 300][rainIntensity];
  for(let i=0; i<dropCount; i++) {{
    const d = rainDrops[i];
    rainCtx.beginPath();
    rainCtx.moveTo(d.x, d.y);
    rainCtx.lineTo(d.x - 3, d.y + d.len);
    rainCtx.stroke();

    d.y += d.speed * simSpeed * 0.4;
    d.x -= 1.2;
    if(d.y > canvas.height) {{
      d.y = -20;
      d.x = Math.random() * canvas.width;
    }}
  }}
}}

function updateWaterPuddles() {{
  const target = rainOn ? [0, 0.35, 0.70, 1.0][rainIntensity] : 0;
  waterAccumulationLevel += (target - waterAccumulationLevel) * 0.05;

  let peakDepth = 0;
  waterlogSpots.forEach(s => {{
    const curDepth = Math.round(s.baseDepth * waterAccumulationLevel);
    if(curDepth > peakDepth) peakDepth = curDepth;

    const circle = waterCircles[s.id];
    if(circle) {{
      circle.setOptions({{
        fillOpacity: Math.min(0.65, waterAccumulationLevel * 0.6),
        radius: s.radius * (0.6 + waterAccumulationLevel * 0.5)
      }});
    }}
  }});

  document.getElementById("bs-w").textContent = peakDepth > 0 ? `${{peakDepth}} cm` : "0 cm";
  updateWaterlogSidebar(peakDepth);
}}

function updateWaterlogSidebar(peakDepth) {{
  const div = document.getElementById('water-list');
  let html = '';
  waterlogSpots.forEach(s => {{
    const depth = Math.round(s.baseDepth * waterAccumulationLevel);
    let badgeClass = 'badge-low';
    let statusText = 'Normal Runoff';
    if(depth >= 45) {{ badgeClass = 'badge-severe'; statusText = '🚫 Submerged / Impassable'; }}
    else if(depth >= 25) {{ badgeClass = 'badge-moderate'; statusText = '⚠️ Water Stagnation / Slow'; }}

    html += `
    <div class="water-item ${{depth>=45?'severe':depth>=25?'moderate':''}}">
      <div class="top-row">
        <span>${{s.name}}</span>
        <span class="depth-badge ${{badgeClass}}">${{depth}} cm</span>
      </div>
      <div class="desc">${{s.desc}}</div>
      <div style="font-size:9.5px;color:${{depth>=45?'#f87171':depth>=25?'#fbbf24':'#38bdf8'}};margin-top:2px;font-weight:600">
        Status: ${{statusText}}
      </div>
    </div>`;
  }});
  div.innerHTML = html;
}}

// ==========================================
// 5. ROAD BLOCKING & REROUTING
// ==========================================
function toggleRoadBlock(roadId) {{
  if(blockedRoads.has(roadId)) {{
    unblockRoad(roadId);
  }} else {{
    blockRoad(roadId);
  }}
  updateDashboard();
  updateReroutingReport();
}}

function blockRoad(roadId) {{
  blockedRoads.add(roadId);
  const poly = roadPolylines[roadId];
  if(poly) {{
    poly.setOptions({{
      strokeColor: "#ef4444",
      strokeOpacity: 0.95,
      strokeWeight: 7,
      map: map
    }});
  }}

  // Redirect vehicles traversing this road
  vehicles.forEach(v => {{
    if(v.roadId === roadId) {{
      const avail = roads.filter(r => !blockedRoads.has(r.id) && (v.type!=='bus' || r.busRoute));
      if(avail.length) {{
        const alt = avail[Math.floor(Math.random()*avail.length)];
        v.roadId = alt.id;
        v.path = Math.random()>0.5 ? [...alt.pts] : [...alt.pts].reverse();
        v.segIdx = 0; v.prog = 0;
      }}
    }}
  }});
}}

function unblockRoad(roadId) {{
  blockedRoads.delete(roadId);
  const poly = roadPolylines[roadId];
  const r = roads.find(x => x.id === roadId);
  if(poly && r) {{
    const color = r.type === 'highway' ? '#facc15' : r.type === 'arterial' ? '#38bdf8' : '#e2e8f0';
    poly.setOptions({{
      strokeColor: color,
      strokeOpacity: 0.6,
      strokeWeight: r.width >= 6 ? 5 : 3.5,
      map: showRoadLines ? map : null
    }});
  }}
}}

function clearBlocks() {{
  [...blockedRoads].forEach(id => unblockRoad(id));
  reroutePolylines.forEach(p => p.setMap(null));
  reroutePolylines.length = 0;
  updateDashboard();
  updateReroutingReport();
}}

function updateReroutingReport() {{
  const div = document.getElementById("reroute-box");
  reroutePolylines.forEach(p => p.setMap(null));
  reroutePolylines.length = 0;

  if(!blockedRoads.size) {{
    div.innerHTML = '<p style="color:#94a3b8">Turn on <b style="color:#fcd34d">Road Block Mode</b> and click any road on Google Maps to analyze traffic displacement & alternate bypasses.</p>';
    return;
  }}

  let html = '<h4>🚧 Live Rerouting Assessment</h4>';
  const blockedArr = [...blockedRoads];
  const unblocked = roads.filter(r => !blockedRoads.has(r.id));
  let totalDisplaced = 0;

  blockedArr.forEach(bid => {{
    const br = roads.find(r => r.id === bid);
    if(!br) return;
    const displaced = Math.round(br.traffic * br.capacity / 100);
    totalDisplaced += displaced;

    html += `<div style="margin:5px 0;padding:6px;background:#241407;border-radius:5px;border-left:3px solid #f97316">`;
    html += `<b style="color:#fb923c">⛔ Blocked: ${{br.name}}</b><br>`;
    html += `<span style="color:#fcd34d">${{displaced}} veh/hr diverted</span><br>`;

    const alts = unblocked.filter(u => u.type===br.type || u.type==='arterial' || u.type==='highway' || u.type==='connector').slice(0, 3);
    if(alts.length) {{
      html += `<span style="color:#94a3b8">Recommended Reroutes:</span><br>`;
      alts.forEach(a => {{
        const addedLoad = Math.round(displaced / alts.length);
        const newLoadPct = Math.min(100, a.traffic + Math.round(addedLoad * 100 / a.capacity));
        html += `<span style="color:#2dd4bf">⤷ ${{a.name}}</span> <span style="color:#fcd34d">(+${{addedLoad}} veh/hr, ${{newLoadPct}}% load)</span><br>`;

        const rPath = a.pts.map(p => ({{ lat: p[0], lng: p[1] }}));
        const glowPoly = new google.maps.Polyline({{
          path: rPath,
          strokeColor: "#f97316",
          strokeOpacity: 0.85,
          strokeWeight: 6,
          map: map
        }});
        reroutePolylines.push(glowPoly);
      }});
    }}
    html += `</div>`;
  }});

  div.innerHTML = html;
}}

// ==========================================
// 6. UI CONTROLS & DESTINATION SLIDERS
// ==========================================
function initDestinationSliders() {{
  const container = document.getElementById('dest-sliders');
  let html = '';
  pois.forEach(p => {{
    const currentVal = destVehTargets[p.id];
    html += `
      <div class="dest-item">
        <div class="dest-header">
          <span>${{p.icon}} ${{p.name}}</span>
          <span class="dest-badge" id="badge-${{p.id}}">${{currentVal}} veh/hr</span>
        </div>
        <input type="range" min="0" max="450" value="${{currentVal}}" id="slider-${{p.id}}" 
          oninput="setDestinationTraffic('${{p.id}}', this.value)">
      </div>`;
  }});
  container.innerHTML = html;
}}

function setDestinationTraffic(poiId, val) {{
  const intVal = parseInt(val);
  destVehTargets[poiId] = intVal;
  const badge = document.getElementById(`badge-${{poiId}}`);
  if(badge) badge.textContent = `${{intVal}} veh/hr`;
  rebalanceVehicles();
  updateDashboard();
}}

function toggleSim() {{
  simRunning = !simRunning;
  document.getElementById('btn-play').classList.toggle('active', simRunning);
  document.getElementById('btn-pause').classList.toggle('active', !simRunning);
}}

function setSpd(s, btn) {{
  simSpeed = s;
  document.querySelectorAll('.speed-btns .btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}}

function setTOD(val) {{
  timeOfDay = parseInt(val);
  const labels = ['Late Night','Late Night','Late Night','Late Night','Early Hours','Dawn Commute','Morning Kickoff','Morning Rush (Peak)','Morning Rush','Morning Commercial','Midday Lull','Afternoon Flow','Afternoon Peak','School Rush','Late Afternoon','Evening Commute','Evening Rush (Peak)','Evening Rush','Night Bazaar','Night Market','Night Commercial','Late Night','Midnight Shift','Dead Hours'];
  document.getElementById('tod-lbl').textContent = labels[timeOfDay];
  rebalanceVehicles();
  updateDashboard();
}}

function togVeh(type, on) {{
  vehConfigs[type].enabled = on;
  rebalanceVehicles();
  updateDashboard();
}}

function toggleRain(on) {{
  rainOn = on;
  document.getElementById("rain-canvas").style.display = on ? "block" : "none";
  updateDashboard();
}}

function setRainInt(v) {{
  rainIntensity = parseInt(v);
  document.getElementById('rain-lbl').textContent = ['','Light Shower','Moderate Downpour','Severe Cloudburst (Monsoon)'][rainIntensity];
  updateDashboard();
}}

function setMapType(type) {{
  map.setMapTypeId(type);
  document.getElementById('btn-sat').classList.toggle('active', type==='hybrid');
  document.getElementById('btn-road').classList.toggle('active', type==='roadmap');
}}

function toggleGoogleTraffic(on) {{
  trafficLayer.setMap(on ? map : null);
}}

function tiltCam(tilt) {{
  map.setTilt(tilt);
}}

let currentHeading = 0;
function rotateCam() {{
  currentHeading = (currentHeading + 45) % 360;
  map.setHeading(currentHeading);
}}

// ==========================================
// 7. DASHBOARD & RENDER LOOP
// ==========================================
function updateDashboard() {{
  const counts = {{car:0, bike:0, auto:0, bus:0}};
  vehicles.forEach(v => {{ counts[v.type]++; }});
  document.getElementById('c-car').textContent = counts.car;
  document.getElementById('c-bike').textContent = counts.bike;
  document.getElementById('c-auto').textContent = counts.auto;
  document.getElementById('c-bus').textContent = counts.bus;

  const total = counts.car + counts.bike + counts.auto + counts.bus;
  document.getElementById('bs-v').textContent = total;

  const rainSlow = rainOn ? [1, 0.72, 0.50, 0.32][rainIntensity] : 1.0;
  const avgSpeed = Math.round(28 * rainSlow);
  document.getElementById('bs-s').textContent = `${{avgSpeed}} km/h`;

  let totalTarget = 0;
  pois.forEach(p => {{ totalTarget += destVehTargets[p.id] || 0; }});
  const cong = Math.min(100, Math.round((totalTarget / 700)*55 + (rainOn ? rainIntensity*10 : 0) + blockedRoads.size*14));
  document.getElementById('bs-c').textContent = `${{cong}}%`;
  const cf = document.getElementById('cfill');
  cf.style.width = `${{cong}}%`;
  cf.style.background = cong<45 ? '#10b981' : cong<75 ? '#f59e0b' : '#ef4444';

  document.getElementById('bs-r').textContent = rainOn ? ['','Light','Moderate','Monsoon'][rainIntensity] : 'Dry';
  document.getElementById('bs-b').textContent = blockedRoads.size;

  const hr12 = timeOfDay%12 || 12;
  document.getElementById('time-disp').textContent = `🕐 ${{String(hr12).padStart(2,'0')}}:00 ${{timeOfDay>=12?'PM':'AM'}}`;

  let rhtml = '';
  roads.slice(0, 10).forEach(r => {{
    const blk = blockedRoads.has(r.id);
    rhtml += `
      <div style="display:flex;justify-content:space-between;padding:4px 8px;background:#0e172e;border-radius:4px;margin-bottom:3px;font-size:10.5px;${{blk?'opacity:0.4;text-decoration:line-through':''}}">
        <span style="color:#cbd5e1">${{r.name}}</span>
        <span class="road-tag" style="color:${{blk?'#ef4444':r.traffic>75?'#f59e0b':'#10b981'}}">${{blk ? 'BLOCKED' : r.traffic + '%'}}</span>
      </div>`;
  }});
  document.getElementById('road-list').innerHTML = rhtml;
}}

let lastFrame = performance.now();
function animateSimulation(now) {{
  requestAnimationFrame(animateSimulation);
  const dt = Math.min((now - lastFrame) / 1000, 0.1);
  lastFrame = now;

  if(simRunning) {{
    updateVehicles(dt);
    if(rainOn) updateRain();
  }}
  updateWaterPuddles();
}}

window.addEventListener('resize', () => {{
  if(rainOn) initRainCanvas();
}});
</script>
<script async defer src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&v=beta&callback=initGoogleMap"></script>
</body>
</html>
'''

with open("c:/Users/SAAQIB/areatwin/google_maps_twin.html", "w", encoding="utf-8") as f:
    f.write(html_code)

print("Generated clean google_maps_twin.html successfully!")
