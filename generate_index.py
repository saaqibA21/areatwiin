import json

with open("c:/Users/SAAQIB/areatwin/royapuram_roads.json", "r", encoding="utf-8") as f:
    roads_data = json.load(f)

roads_json_str = json.dumps(roads_data)

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Royapuram 3D Digital Twin - All Roads & Destination Traffic</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#050914;color:#e2e8f0;overflow:hidden;height:100vh}}
#app{{display:flex;height:100vh;width:100vw}}
#canvas-container{{flex:1;position:relative;background:#050914}}
canvas{{display:block;width:100%;height:100%}}
#sidebar{{width:410px;background:linear-gradient(180deg,#0a1022 0%,#0c152d 100%);border-left:1px solid #1e294b;overflow-y:auto;z-index:20;flex-shrink:0;box-shadow:-6px 0 30px rgba(0,0,0,0.6)}}
.panel{{padding:13px 16px;border-bottom:1px solid #1a274c}}
.panel h3{{font-size:12px;text-transform:uppercase;letter-spacing:1.5px;color:#00d4ff;margin-bottom:10px;display:flex;align-items:center;gap:7px}}
.panel h3 span{{font-size:16px}}
.stat-grid{{display:grid;grid-template-columns:1fr 1fr;gap:7px}}
.stat-card{{background:#111933;border:1px solid #1c2b54;border-radius:8px;padding:9px;text-align:center}}
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
.dest-item{{background:#101a33;border:1px solid #1a274c;border-radius:7px;padding:8px 10px;margin-bottom:6px}}
.dest-header{{display:flex;justify-content:space-between;align-items:center;font-size:11px;font-weight:600}}
.dest-badge{{font-size:9.5px;padding:2px 7px;border-radius:10px;background:#0369a133;color:#38bdf8;border:1px solid #0284c755;font-weight:700}}
.water-item{{padding:7px 9px;background:#0d1c33;border-radius:6px;margin-bottom:5px;font-size:11px;border-left:4px solid #0284c7}}
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
#hud{{position:absolute;top:0;left:0;right:0;z-index:10;background:linear-gradient(180deg,rgba(5,9,20,0.95) 0%,rgba(5,9,20,0.4) 70%,transparent 100%);padding:12px 22px;display:flex;align-items:center;justify-content:space-between;pointer-events:none}}
#hud>*{{pointer-events:auto}}
#hud h1{{font-size:18px;color:#f8fafc;font-weight:700;display:flex;align-items:center;gap:8px}}
#hud h1 span.tag{{font-size:11px;color:#38bdf8;font-weight:500;background:#0369a133;border:1px solid #0284c766;padding:2px 8px;border-radius:12px}}
#time-disp{{font-size:13px;color:#fcd34d;background:#0f172a;padding:5px 14px;border-radius:20px;border:1px solid #334155;font-weight:600;box-shadow:0 0 15px rgba(0,0,0,0.5)}}
#bottom-bar{{position:absolute;bottom:0;left:0;right:410px;z-index:10;background:linear-gradient(transparent,rgba(5,9,20,0.95) 30%);padding:10px 20px;display:flex;gap:13px;justify-content:center}}
.bs{{text-align:center;background:#0f172acc;backdrop-filter:blur(6px);border:1px solid #1e293b;border-radius:8px;padding:8px 16px;min-width:110px}}
.bs .v{{font-size:17px;font-weight:700;color:#2dd4bf}}
.bs .l{{font-size:8.5px;color:#94a3b8;text-transform:uppercase;margin-top:2px;letter-spacing:0.5px}}
#cam-hint{{position:absolute;bottom:65px;left:50%;transform:translateX(-50%);z-index:10;color:#94a3b8;font-size:11px;background:#090d1adb;padding:5px 16px;border-radius:20px;border:1px solid #1e294b;pointer-events:none;letter-spacing:0.3px}}
.cbar{{width:100%;height:6px;background:#1e293b;border-radius:3px;margin-top:6px;overflow:hidden}}
.cfill{{height:100%;border-radius:3px;transition:width .5s,background .5s}}
.road-tag{{font-size:10px;font-weight:600}}
::-webkit-scrollbar{{width:5px}}
::-webkit-scrollbar-track{{background:#050914}}
::-webkit-scrollbar-thumb{{background:#1e294b;border-radius:3px}}
</style>
</head>
<body>
<div id="app">
<div id="canvas-container">
  <div id="hud">
    <h1>🏙️ Royapuram 3D Twin <span class="tag">All 30 Connected Roads & Destinations</span></h1>
    <div id="time-disp">🕐 08:00 AM</div>
  </div>
  <div id="bottom-bar">
    <div class="bs"><div class="v" id="bs-v">0</div><div class="l">Live Vehicles</div></div>
    <div class="bs"><div class="v" id="bs-s">0 km/h</div><div class="l">Average Speed</div></div>
    <div class="bs"><div class="v" id="bs-c">0%</div><div class="l">Congestion Index</div></div>
    <div class="bs"><div class="v" id="bs-r">Dry</div><div class="l">Monsoon Rain</div></div>
    <div class="bs"><div class="v" id="bs-w">0 cm</div><div class="l">Peak Waterlog</div></div>
    <div class="bs"><div class="v" id="bs-b">0</div><div class="l">Blocked Roads</div></div>
  </div>
  <div id="cam-hint">🖱️ Left-drag: Orbit | Right-drag: Pan | Scroll: Zoom | Block Mode: Click any road to reroute</div>
</div>
<div id="sidebar">
  <!-- Simulation Controls -->
  <div class="panel">
    <h3><span>⚙️</span> Simulation Controls</h3>
    <div class="ctrl"><label>Map Layer (Free Open Source)</label>
      <div style="display:flex;gap:4px">
        <button class="btn active" id="btn-style-sat" onclick="setMapStyle('satellite')">🛰️ Satellite</button>
        <button class="btn" id="btn-style-dark" onclick="setMapStyle('dark')">🏙️ Dark 3D</button>
      </div>
    </div>
    <div class="ctrl"><label>3D Buildings</label>
      <label class="toggle"><input type="checkbox" id="bld-tog" checked onchange="toggleBuildings(this.checked)"><span class="sl"></span></label>
    </div>
    <div class="ctrl"><label>State</label>
      <div style="display:flex;gap:5px">
        <button class="btn active" id="btn-play" onclick="toggleSim()">▶ Play</button>
        <button class="btn" id="btn-pause" onclick="toggleSim()">⏸ Pause</button>
      </div>
    </div>
    <div class="ctrl"><label>Simulation Speed</label>
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
    <div class="ctrl" style="margin-top:8px"><label>🎥 Camera Angles</label>
      <div style="display:flex;gap:3px">
        <button class="btn" onclick="camPreset('overview')">Aerial</button>
        <button class="btn" onclick="camPreset('street')">Street</button>
        <button class="btn" onclick="camPreset('coastal')">Coast</button>
        <button class="btn" onclick="camPreset('waterlog')">Floods</button>
      </div>
    </div>
  </div>

  <!-- Target Destination Traffic Allocator -->
  <div class="panel">
    <h3><span>🎯</span> Destination Traffic (Change Vehicle Inflow)</h3>
    <p style="font-size:10px;color:#94a3b8;margin-bottom:8px">Adjust sliders to dynamically send more/fewer vehicles to each specific location across all 30 roads:</p>
    <div class="list-box" id="dest-sliders"></div>
  </div>

  <!-- Rain & Water Accumulation / Stoppage -->
  <div class="panel">
    <h3><span>🌧️</span> Rain & Water Stagnation (Flooding)</h3>
    <div class="ctrl"><label>Monsoon Rainfall</label><label class="toggle"><input type="checkbox" id="rain-tog" onchange="toggleRain(this.checked)"><span class="sl"></span></label></div>
    <div class="ctrl"><label>Rainfall Intensity</label><span id="rain-lbl" style="font-size:11px;color:#38bdf8;font-weight:600">Light Shower</span></div>
    <input type="range" id="rain-sl" min="1" max="3" value="1" oninput="setRainInt(this.value)">
    <div class="ctrl" style="margin-top:6px"><label>Show Water Stoppage Depths</label>
      <label class="toggle"><input type="checkbox" id="water-vis-tog" checked onchange="toggleWaterVis(this.checked)"><span class="sl"></span></label>
    </div>
    <div style="margin-top:8px;font-size:11px;color:#94a3b8;font-weight:600">🌊 Known Water Stoppage Points:</div>
    <div id="water-list" style="margin-top:6px"></div>
  </div>

  <!-- Vehicle Modalities -->
  <div class="panel">
    <h3><span>🚗</span> Vehicle Fleet</h3>
    <div class="ctrl"><label>🚗 Cars</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('car',this.checked)"><span class="sl"></span></label></div>
    <div class="ctrl"><label>🏍️ Bikes / Two-Wheelers</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('bike',this.checked)"><span class="sl"></span></label></div>
    <div class="ctrl"><label>🛺 Auto-Rickshaws</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('auto',this.checked)"><span class="sl"></span></label></div>
    <div class="ctrl"><label>🚌 MTC City Buses</label><label class="toggle"><input type="checkbox" checked onchange="togVeh('bus',this.checked)"><span class="sl"></span></label></div>
    <div class="stat-grid" style="margin-top:8px">
      <div class="stat-card"><div class="val" id="c-car">0</div><div class="lbl">Cars</div></div>
      <div class="stat-card"><div class="val" id="c-bike">0</div><div class="lbl">Bikes</div></div>
      <div class="stat-card"><div class="val" id="c-auto">0</div><div class="lbl">Autos</div></div>
      <div class="stat-card"><div class="val" id="c-bus">0</div><div class="lbl">Buses</div></div>
    </div>
  </div>

  <!-- Road Traffic & Congestion -->
  <div class="panel">
    <h3><span>🛣️</span> 30-Road Network Status</h3>
    <div class="list-box" id="road-list" style="max-height:170px"></div>
    <div class="cbar"><div class="cfill" id="cfill" style="width:30%;background:#10b981"></div></div>
  </div>

  <!-- Rerouting Analysis -->
  <div class="panel">
    <h3><span>🔀</span> Dynamic Rerouting Engine</h3>
    <div id="reroute-box" class="reroute-box">
      <p style="color:#94a3b8">Turn on <b style="color:#fcd34d">Road Block Mode</b> and click any road in the 3D scene to analyze traffic displacement & alternate bypasses.</p>
    </div>
  </div>
</div>
</div>

<script>
// ==========================================
// 1. GEO CONVERSION & MATH
// ==========================================
const CENTER = {{lat:13.1040, lng:80.2937}};
const SCALE = 85000;
function geo(lat, lng){{
  return {{x:(lng-CENTER.lng)*SCALE, z:-(lat-CENTER.lat)*SCALE}};
}}

// ==========================================
// 2. THREE.JS INITIALIZATION
// ==========================================
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x060a14);
scene.fog = new THREE.FogExp2(0x060a14, 0.0022);

const camera = new THREE.PerspectiveCamera(50, container.clientWidth/container.clientHeight, 0.5, 3500);
camera.position.set(0, 115, 140);

const renderer = new THREE.WebGLRenderer({{antialias:true, powerPreference:"high-performance"}});
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.35;
container.appendChild(renderer.domElement);

// Lighting
const ambientLight = new THREE.AmbientLight(0x475569, 0.85);
scene.add(ambientLight);

const sunLight = new THREE.DirectionalLight(0xfff7ed, 1.3);
sunLight.position.set(80, 160, 60);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -220;
sunLight.shadow.camera.right = 220;
sunLight.shadow.camera.top = 220;
sunLight.shadow.camera.bottom = -220;
scene.add(sunLight);

const skyLight = new THREE.HemisphereLight(0x38bdf8, 0x0f172a, 0.6);
scene.add(skyLight);

// ==========================================
// 3. SMOOTH ORBIT CONTROLS
// ==========================================
let camTheta = Math.PI/4, camPhi = Math.PI/3.6, camDist = 180, camTarget = new THREE.Vector3(0,0,0);
let isDragging = false, isPanning = false, lastMX = 0, lastMY = 0;

renderer.domElement.addEventListener('mousedown', e => {{
  if(e.button===0) isDragging=true;
  else if(e.button===2) isPanning=true;
  lastMX=e.clientX; lastMY=e.clientY;
}});
window.addEventListener('mouseup', () => {{isDragging=false; isPanning=false;}});
renderer.domElement.addEventListener('mousemove', e => {{
  const dx=e.clientX-lastMX, dy=e.clientY-lastMY;
  lastMX=e.clientX; lastMY=e.clientY;
  if(isDragging){{
    camTheta -= dx*0.0055;
    camPhi = Math.max(0.08, Math.min(Math.PI/2-0.03, camPhi-dy*0.0055));
  }}
  if(isPanning){{
    const right = new THREE.Vector3(-Math.cos(camTheta), 0, Math.sin(camTheta));
    const fwd = new THREE.Vector3(-Math.sin(camTheta), 0, -Math.cos(camTheta));
    camTarget.addScaledVector(right, dx*0.18);
    camTarget.addScaledVector(fwd, -dy*0.18);
  }}
}});
renderer.domElement.addEventListener('wheel', e => {{
  camDist = Math.max(15, Math.min(600, camDist + e.deltaY*0.12));
  e.preventDefault();
}},{{passive:false}});
renderer.domElement.addEventListener('contextmenu', e=>e.preventDefault());

function updateCamera(){{
  camera.position.set(
    camTarget.x + camDist*Math.sin(camPhi)*Math.sin(camTheta),
    camTarget.y + camDist*Math.cos(camPhi),
    camTarget.z + camDist*Math.sin(camPhi)*Math.cos(camTheta)
  );
  camera.lookAt(camTarget);
}}

// ==========================================
// 4. BASE GROUND & REAL OPEN-SOURCE SATELLITE
// ==========================================
const terrainGeo = new THREE.PlaneGeometry(800, 800, 20, 20);
const terrainMat = new THREE.MeshStandardMaterial({{color:0x0b1329, roughness:0.92, metalness:0.05}});
const terrain = new THREE.Mesh(terrainGeo, terrainMat);
terrain.rotation.x = -Math.PI/2;
terrain.receiveShadow = true;
scene.add(terrain);

const grid = new THREE.GridHelper(800, 100, 0x1e293b, 0x0f172a);
grid.position.y = 0.05;
scene.add(grid);

const satTexLoader = new THREE.TextureLoader();
const satTexture = satTexLoader.load('satellite_royapuram.jpg', () => {{
  renderer.render(scene, camera);
}});
satTexture.generateMipmaps = true;
satTexture.minFilter = THREE.LinearMipmapLinearFilter;

const satGeo = new THREE.PlaneGeometry(2801.51, 3183.33);
const satMat = new THREE.MeshStandardMaterial({{
  map: satTexture,
  roughness: 0.85,
  metalness: 0.05
}});
const satMesh = new THREE.Mesh(satGeo, satMat);
satMesh.rotation.x = -Math.PI/2;
satMesh.position.set(-10.28, 0.08, 37.88);
satMesh.receiveShadow = true;
scene.add(satMesh);

const seaGeo = new THREE.PlaneGeometry(240, 800, 20, 20);
const seaMat = new THREE.MeshStandardMaterial({{
  color:0x0284c7, roughness:0.1, metalness:0.8,
  transparent:true, opacity:0.65, emissive:0x0369a1, emissiveIntensity:0.25
}});
const sea = new THREE.Mesh(seaGeo, seaMat);
sea.rotation.x = -Math.PI/2;
sea.position.set(165, 0.14, 0);
scene.add(sea);

makeLabel("🌊 Bay of Bengal (Chennai Port / Coast)", {{x:165,z:0}}, 14, '#38bdf8');

function setMapStyle(style){{
  const btnSat = document.getElementById('btn-style-sat');
  const btnDark = document.getElementById('btn-style-dark');
  if(style === 'satellite'){{
    satMesh.visible = true;
    seaMat.opacity = 0.65;
    grid.visible = false;
    btnSat.classList.add('active');
    btnDark.classList.remove('active');
  }} else {{
    satMesh.visible = false;
    seaMat.opacity = 0.88;
    grid.visible = true;
    btnDark.classList.add('active');
    btnSat.classList.remove('active');
  }}
}}

// ==========================================
// 5. COMPREHENSIVE 30-ROAD NETWORK
// ==========================================
const roads = {roads_json_str};

const roadMeshes = {{}};
const roadWorldPts = {{}};
const blockedRoads = new Set();
let blockMode = false;

roads.forEach(r => {{
  const wpts = r.pts.map(p => geo(p[0], p[1]));
  roadWorldPts[r.id] = wpts;

  const roadGroup = new THREE.Group();
  roadGroup.roadId = r.id;

  for(let i=0; i<wpts.length-1; i++){{
    const p1 = wpts[i];
    const p2 = wpts[i+1];
    const dx = p2.x - p1.x;
    const dz = p2.z - p1.z;
    const len = Math.sqrt(dx*dx + dz*dz);
    const angle = Math.atan2(dx, dz);
    const midX = (p1.x + p2.x) / 2;
    const midZ = (p1.z + p2.z) / 2;

    // 1. Asphalt Road Surface
    const roadGeo = new THREE.BoxGeometry(r.width, 0.25, len);
    const roadMat = new THREE.MeshStandardMaterial({{
      color: 0x1f2430, roughness: 0.75, metalness: 0.15
    }});
    const roadSegment = new THREE.Mesh(roadGeo, roadMat);
    roadSegment.position.set(midX, 0.22, midZ);
    roadSegment.rotation.y = angle;
    roadSegment.receiveShadow = true;
    roadSegment.roadId = r.id;
    roadGroup.add(roadSegment);

    // 2. Concrete Curbs
    const curbWidth = 0.6;
    const curbGeo = new THREE.BoxGeometry(curbWidth, 0.32, len);
    const curbMat = new THREE.MeshStandardMaterial({{color: 0x475569, roughness: 0.9}});
    
    const curbL = new THREE.Mesh(curbGeo, curbMat);
    curbL.position.set(midX - Math.cos(angle)*(r.width/2 + curbWidth/2), 0.25, midZ + Math.sin(angle)*(r.width/2 + curbWidth/2));
    curbL.rotation.y = angle;
    roadGroup.add(curbL);

    const curbR = new THREE.Mesh(curbGeo, curbMat);
    curbR.position.set(midX + Math.cos(angle)*(r.width/2 + curbWidth/2), 0.25, midZ - Math.sin(angle)*(r.width/2 + curbWidth/2));
    curbR.rotation.y = angle;
    roadGroup.add(curbR);

    // 3. Crisp Road Markings (Solid White Border Lines)
    const edgeLineGeo = new THREE.BoxGeometry(0.12, 0.05, len);
    const edgeLineMat = new THREE.MeshBasicMaterial({{color: 0xffffff}});
    const edgeL = new THREE.Mesh(edgeLineGeo, edgeLineMat);
    edgeL.position.set(midX - Math.cos(angle)*(r.width*0.44), 0.36, midZ + Math.sin(angle)*(r.width*0.44));
    edgeL.rotation.y = angle;
    roadGroup.add(edgeL);

    const edgeR = edgeL.clone();
    edgeR.position.set(midX + Math.cos(angle)*(r.width*0.44), 0.36, midZ - Math.sin(angle)*(r.width*0.44));
    roadGroup.add(edgeR);

    // 4. Center Line
    const dashGeo = new THREE.BoxGeometry(0.18, 0.05, len);
    const dashMat = new THREE.MeshBasicMaterial({{color: r.lineColor || 0xffffff}});
    const centerLine = new THREE.Mesh(dashGeo, dashMat);
    centerLine.position.set(midX, 0.36, midZ);
    centerLine.rotation.y = angle;
    roadGroup.add(centerLine);

    // 5. Junction Node Cap
    const capGeo = new THREE.CylinderGeometry(r.width/2 + curbWidth, r.width/2 + curbWidth, 0.25, 16);
    const cap = new THREE.Mesh(capGeo, roadMat);
    cap.position.set(p1.x, 0.22, p1.z);
    roadGroup.add(cap);
  }}

  scene.add(roadGroup);
  roadMeshes[r.id] = roadGroup;

  // Add floating 3D Road Name Tag
  const midPoint = wpts[Math.floor(wpts.length/2)];
  makeLabel(r.name, midPoint, 4.0, r.type==='highway'?'#facc15':r.type==='arterial'?'#38bdf8':'#cbd5e1');
}});

// ==========================================
// 6. 10 FAMOUS SPOTS & DESTINATIONS
// ==========================================
const pois = [
  {{id:'poi_station', name:'Royapuram Railway Station', lat:13.1065, lng:80.2920, icon:'🚂', color:0xf59e0b, h:18, defaultVeh:80,
   desc:'Oldest surviving railway station in South India (1856); key commuter terminus.'}},
  {{id:'poi_harbour', name:'Kasimedu Fishing Harbour', lat:13.1115, lng:80.2965, icon:'🐟', color:0x0284c7, h:14, defaultVeh:120,
   desc:'Major commercial fishing port; massive morning auction crowd.'}},
  {{id:'poi_metro', name:'Mannadi Metro Station', lat:13.0960, lng:80.2850, icon:'🚇', color:0x06b6d4, h:10, defaultVeh:140,
   desc:'Primary rapid metro gateway connecting Royapuram to Central & Airport.'}},
  {{id:'poi_stanley', name:'Stanley Medical College & Hospital', lat:13.0995, lng:80.2870, icon:'🏥', color:0x10b981, h:22, defaultVeh:90,
   desc:'Historic medical college; heavy 24/7 ambulance & patient transit.'}},
  {{id:'poi_amman', name:'Arulmigu Angalaparameshwari Temple', lat:13.1055, lng:80.2910, icon:'🛕', color:0xeab308, h:17, defaultVeh:60,
   desc:'Centuries-old temple in Pudumanaikuppam with high festive gatherings.'}},
  {{id:'poi_subramania', name:'Subramania Swamy Temple', lat:13.1038, lng:80.2925, icon:'🛕', color:0xfacc15, h:15, defaultVeh:45,
   desc:'Revered Murugan temple drawing daily morning and evening devotees.'}},
  {{id:'poi_stpeters', name:'St. Peter’s Church', lat:13.1030, lng:80.2945, icon:'⛪', color:0x818cf8, h:19, defaultVeh:35,
   desc:'Vibrant Anglo-Indian community church established during early port days (1829).'}},
  {{id:'poi_stanthony', name:'St. Anthony’s Church', lat:13.1028, lng:80.2940, icon:'⛪', color:0xa78bfa, h:16, defaultVeh:30,
   desc:'Prominent North Chennai shrine opposite St. Peter’s.'}},
  {{id:'poi_theagaraya', name:'Sir Theagaraya College', lat:13.1010, lng:80.2880, icon:'🎓', color:0x14b8a6, h:17, defaultVeh:40,
   desc:'Pioneering educational institution serving North Chennai youth.'}},
  {{id:'poi_fire_temple', name:'Parsi Fire Temple (Agiary)', lat:13.1045, lng:80.2935, icon:'🔥', color:0xf97316, h:14, defaultVeh:20,
   desc:'Only functioning Parsi place of worship in Chennai, dating to colonial era.'}}
];

const poiMeshes = [];
const destVehTargets = {{}}; // destination ID -> user slider value

pois.forEach(p => {{
  destVehTargets[p.id] = p.defaultVeh;
  const pos = geo(p.lat, p.lng);
  
  const baseGeo = new THREE.BoxGeometry(6, 4, 6);
  const baseMat = new THREE.MeshStandardMaterial({{color:0x1e293b, roughness:0.5}});
  const base = new THREE.Mesh(baseGeo, baseMat);
  base.position.set(pos.x, 2, pos.z);
  scene.add(base);

  const towerGeo = new THREE.CylinderGeometry(0.8, 1.8, p.h, 16);
  const towerMat = new THREE.MeshStandardMaterial({{color:p.color, metalness:0.3, roughness:0.4, emissive:p.color, emissiveIntensity:0.35}});
  const tower = new THREE.Mesh(towerGeo, towerMat);
  tower.position.set(pos.x, p.h/2 + 4, pos.z);
  scene.add(tower);

  const crownGeo = new THREE.SphereGeometry(1.6, 16, 16);
  const crownMat = new THREE.MeshBasicMaterial({{color:p.color}});
  const crown = new THREE.Mesh(crownGeo, crownMat);
  crown.position.set(pos.x, p.h + 5, pos.z);
  scene.add(crown);

  const ringGeo = new THREE.RingGeometry(3, 4.5, 32);
  const ringMat = new THREE.MeshBasicMaterial({{color:p.color, transparent:true, opacity:0.35, side:THREE.DoubleSide}});
  const ring = new THREE.Mesh(ringGeo, ringMat);
  ring.rotation.x = -Math.PI/2;
  ring.position.set(pos.x, 0.38, pos.z);
  scene.add(ring);

  const labelSprite = makeLabel(`${{p.icon}} ${{p.name}}`, pos, p.h + 8, '#f8fafc');

  poiMeshes.push({{data:p, pos, ring, crown, labelSprite}});
}});

// ==========================================
// 7. BUILDINGS
// ==========================================
const bldGroup = new THREE.Group();
const bldMat1 = new THREE.MeshStandardMaterial({{color:0x1e293b, roughness:0.8, metalness:0.2}});
const bldMat2 = new THREE.MeshStandardMaterial({{color:0x0f172a, roughness:0.7, metalness:0.3}});
const bldMat3 = new THREE.MeshStandardMaterial({{color:0x334155, roughness:0.85, metalness:0.1}});

for(let i=0; i<180; i++){{
  const lat = 13.0945 + Math.random()*0.021;
  const lng = 80.2840 + Math.random()*0.015;
  const p = geo(lat, lng);
  const w = 2.5 + Math.random()*3.5;
  const d = 2.5 + Math.random()*3.5;
  const h = 3.0 + Math.random()*11.0;
  const geoBox = new THREE.BoxGeometry(w, h, d);
  const mat = i%3===0 ? bldMat1 : i%3===1 ? bldMat2 : bldMat3;
  const bMesh = new THREE.Mesh(geoBox, mat);
  bMesh.position.set(p.x, h/2, p.z);
  bMesh.castShadow = true;
  bMesh.receiveShadow = true;
  bldGroup.add(bMesh);
}}
scene.add(bldGroup);

function toggleBuildings(visible){{
  bldGroup.visible = visible;
}}

// ==========================================
// 8. WATERLOGGING & DRAINAGE STAGNATION
// ==========================================
const waterlogSpots = [
  {{id:'wl_stanley',name:'Stanley Subway Underpass',lat:13.0995,lng:80.2872,baseDepth:65,radius:16,
   desc:'Low-elevation rail underpass; chronic drainage blockage. Impassable in heavy rain.'}},
  {{id:'wl_kalmandapam',name:'Kalmandapam Market Junction',lat:13.1060,lng:80.2952,baseDepth:45,radius:13,
   desc:'Low basin pocket near residential bazaar; runoff accumulates from Surya Narayana Rd.'}},
  {{id:'wl_pvkovil',name:'P.V. Kovil St Low Basin',lat:13.1044,lng:80.2878,baseDepth:40,radius:12,
   desc:'Depression between residential blocks; stormwater drains overflow.'}},
  {{id:'wl_madha',name:'West Madha Church / MS Koil Corner',lat:13.1052,lng:80.2922,baseDepth:32,radius:11,
   desc:'High footfall commercial intersection; stormwater stalls due to tight road slope.'}},
  {{id:'wl_harbour',name:'Kasimedu Harbour Gate Basin',lat:13.1110,lng:80.2965,baseDepth:28,radius:14,
   desc:'Coastal backwater seepage and surface runoff from fish market sheds.'}},
  {{id:'wl_rob',name:'Royapuram ROB Bridge Slope',lat:13.1065,lng:80.2905,baseDepth:25,radius:10,
   desc:'Water collects at foot of Rail Overbridge ramp before reaching main line drain.'}}
];

const waterlogMeshes = [];
let waterAccumulationLevel = 0;

waterlogSpots.forEach(s => {{
  const pos = geo(s.lat, s.lng);
  
  const puddleGeo = new THREE.CircleGeometry(s.radius, 32);
  const puddleMat = new THREE.MeshStandardMaterial({{
    color: 0x0284c7, roughness: 0.05, metalness: 0.9,
    transparent: true, opacity: 0.0, emissive: 0x0369a1, emissiveIntensity: 0.35, depthWrite: false
  }});
  const puddle = new THREE.Mesh(puddleGeo, puddleMat);
  puddle.rotation.x = -Math.PI/2;
  puddle.position.set(pos.x, 0.42, pos.z);
  scene.add(puddle);

  const rippleGeo = new THREE.RingGeometry(s.radius*0.7, s.radius, 32);
  const rippleMat = new THREE.MeshBasicMaterial({{color: 0x38bdf8, transparent: true, opacity: 0.0, side: THREE.DoubleSide}});
  const ripple = new THREE.Mesh(rippleGeo, rippleMat);
  ripple.rotation.x = -Math.PI/2;
  ripple.position.set(pos.x, 0.44, pos.z);
  scene.add(ripple);

  const beaconGeo = new THREE.CylinderGeometry(0.2, 0.2, 6, 8);
  const beaconMat = new THREE.MeshBasicMaterial({{color: 0xef4444, transparent:true, opacity:0.0}});
  const beacon = new THREE.Mesh(beaconGeo, beaconMat);
  beacon.position.set(pos.x, 3, pos.z);
  scene.add(beacon);

  const labelSprite = makeLabel(`🌊 ${{s.name}}: DRY`, pos, 7, '#38bdf8');
  labelSprite.visible = false;

  waterlogMeshes.push({{ data: s, pos, puddle, ripple, beacon, labelSprite }});
}});

function updateWaterlogVisuals(intensity, isRaining){{
  const target = isRaining ? [0, 0.35, 0.70, 1.0][intensity] : 0;
  waterAccumulationLevel += (target - waterAccumulationLevel) * 0.08;

  let peakDepth = 0;
  waterlogMeshes.forEach(wm => {{
    const curDepth = Math.round(wm.data.baseDepth * waterAccumulationLevel);
    if(curDepth > peakDepth) peakDepth = curDepth;

    if(waterAccumulationLevel > 0.04){{
      wm.puddle.material.opacity = Math.min(0.88, 0.25 + waterAccumulationLevel * 0.65);
      wm.puddle.scale.setScalar(0.5 + waterAccumulationLevel * 0.55);
      wm.ripple.material.opacity = 0.35 * waterAccumulationLevel;
      wm.beacon.material.opacity = waterAccumulationLevel > 0.5 ? 0.8 : 0.0;
      wm.labelSprite.visible = true;

      const severity = curDepth >= 45 ? '#ef4444' : curDepth >= 30 ? '#f59e0b' : '#38bdf8';
      updateLabelText(wm.labelSprite, `🌊 ${{wm.data.name}}: ${{curDepth}} cm Stagnant`, severity);
    }} else {{
      wm.puddle.material.opacity = 0.0;
      wm.ripple.material.opacity = 0.0;
      wm.beacon.material.opacity = 0.0;
      wm.labelSprite.visible = false;
    }}
  }});

  document.getElementById('bs-w').textContent = peakDepth > 0 ? `${{peakDepth}} cm` : '0 cm';
  updateWaterlogSidebar(peakDepth);
}}

function updateWaterlogSidebar(peakDepth){{
  const div = document.getElementById('water-list');
  let html = '';
  waterlogSpots.forEach(s => {{
    const depth = Math.round(s.baseDepth * waterAccumulationLevel);
    let badgeClass = 'badge-low';
    let statusText = 'Normal Runoff';
    if(depth >= 45){{ badgeClass = 'badge-severe'; statusText = '🚫 Submerged / Impassable'; }}
    else if(depth >= 25){{ badgeClass = 'badge-moderate'; statusText = '⚠️ Water Stagnation / Slow'; }}

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
// 9. DYNAMIC VEHICLE FLEET & ALL-ROAD ROUTING
// ==========================================
const vehConfigs = {{
  car: {{color:0x38bdf8, w:1.4, h:0.75, d:2.4, speed:32, enabled:true}},
  bike:{{color:0x4ade80, w:0.5, h:0.65, d:1.2, speed:42, enabled:true}},
  auto:{{color:0xfacc15, w:1.0, h:0.95, d:1.7, speed:24, enabled:true}},
  bus: {{color:0xf43f5e, w:1.8, h:1.40, d:4.4, speed:18, enabled:true}}
}};

let vehicles = [];
let simRunning = true, simSpeed = 1, timeOfDay = 8, rainOn = false, rainIntensity = 1;

// Find connected / nearby roads at a waypoint
function findNextRoad(currentRoadId, currentCoord, targetPos, isBus){{
  const candidates = [];
  roads.forEach(r => {{
    if(blockedRoads.has(r.id)) return;
    if(isBus && !r.busRoute) return;

    const wpts = roadWorldPts[r.id];
    for(let i=0; i<wpts.length; i++){{
      const pt = wpts[i];
      const dist = Math.hypot(pt.x - currentCoord.x, pt.z - currentCoord.z);
      if(dist < 18){{ // Connected or junction proximity
        // Compute distance from road endpoint toward target destination
        const otherEnd = i===0 ? wpts[wpts.length-1] : wpts[0];
        const distToTarget = Math.hypot(otherEnd.x - targetPos.x, otherEnd.z - targetPos.z);
        candidates.push({{
          road: r,
          startIdx: i,
          forward: i < wpts.length-1,
          distToTarget: distToTarget
        }});
        break;
      }}
    }}
  }});

  if(!candidates.length) return null;
  // Sort candidates by proximity to destination (intelligent pathfinding)
  candidates.sort((a,b) => a.distToTarget - b.distToTarget);
  // Introduce small randomness (70% best road, 30% explore side lane)
  const choice = Math.random() < 0.7 ? candidates[0] : candidates[Math.floor(Math.random()*candidates.length)];
  return choice;
}}

function spawnVehicleForDestination(poiId){{
  const poi = pois.find(p => p.id === poiId);
  if(!poi) return null;
  const targetPos = geo(poi.lat, poi.lng);

  // Pick modal type based on destination profile
  const types = ['car','bike','bike','auto','auto','car'];
  if(poi.id==='poi_station' || poi.id==='poi_metro' || poi.id==='poi_stanley') types.push('bus');
  const type = types[Math.floor(Math.random()*types.length)];
  const cfg = vehConfigs[type];
  if(!cfg.enabled) return null;

  // Pick random entry road
  const availableRoads = roads.filter(r => !blockedRoads.has(r.id) && (type!=='bus' || r.busRoute));
  if(!availableRoads.length) return null;
  const startRoad = availableRoads[Math.floor(Math.random()*availableRoads.length)];
  const wpts = roadWorldPts[startRoad.id];
  const fwd = Math.random() > 0.5;
  const coords = fwd ? [...wpts] : [...wpts].reverse();

  // Create 3D Mesh
  const vehGroup = new THREE.Group();
  const bodyGeo = new THREE.BoxGeometry(cfg.w, cfg.h, cfg.d);
  const bodyMat = new THREE.MeshStandardMaterial({{
    color:cfg.color, metalness:0.6, roughness:0.35, emissive:cfg.color, emissiveIntensity:0.25
  }});
  const body = new THREE.Mesh(bodyGeo, bodyMat);
  body.castShadow = true;
  body.position.y = cfg.h/2 + 0.15;
  vehGroup.add(body);

  if(type==='car' || type==='bus'){{
    const roofGeo = new THREE.BoxGeometry(cfg.w*0.85, cfg.h*0.65, cfg.d*0.6);
    const roofMat = new THREE.MeshStandardMaterial({{color:0x0f172a, roughness:0.2}});
    const roof = new THREE.Mesh(roofGeo, roofMat);
    roof.position.set(0, cfg.h + 0.1, 0);
    vehGroup.add(roof);
  }} else if(type==='auto'){{
    const hoodGeo = new THREE.BoxGeometry(cfg.w*0.9, cfg.h*0.5, cfg.d*0.8);
    const hoodMat = new THREE.MeshStandardMaterial({{color:0x1e293b}});
    const hood = new THREE.Mesh(hoodGeo, hoodMat);
    hood.position.set(0, cfg.h*0.9, 0);
    vehGroup.add(hood);
  }}

  // Headlights
  const hlMat = new THREE.MeshBasicMaterial({{color:0xfef08a}});
  const hlL = new THREE.Mesh(new THREE.SphereGeometry(0.12, 6, 6), hlMat);
  hlL.position.set(cfg.w/2 - 0.2, cfg.h/2 + 0.1, cfg.d/2);
  vehGroup.add(hlL);
  const hlR = hlL.clone();
  hlR.position.x = -cfg.w/2 + 0.2;
  vehGroup.add(hlR);

  scene.add(vehGroup);

  return {{
    type,
    mesh: vehGroup,
    targetPOI: poi,
    targetPos: targetPos,
    roadId: startRoad.id,
    coords: coords,
    segIdx: 0,
    segProg: 0,
    speed: cfg.speed * (0.85 + Math.random()*0.35)
  }};
}}

function rebalanceVehicles(){{
  // Calculate total vehicles desired based on user sliders
  let totalDesired = 0;
  pois.forEach(p => {{
    totalDesired += destVehTargets[p.id] || 0;
  }});
  // Scale down into active on-screen entities (e.g. 1 entity = ~6 veh/hr)
  const targetFleet = Math.max(20, Math.min(160, Math.round(totalDesired / 4.5)));

  // Trim or spawn
  while(vehicles.length > targetFleet){{
    const v = vehicles.pop();
    if(v && v.mesh) scene.remove(v.mesh);
  }}

  while(vehicles.length < targetFleet){{
    // Pick destination proportionally to slider values
    let r = Math.random() * totalDesired;
    let chosenPOI = pois[0];
    for(const p of pois){{
      r -= (destVehTargets[p.id] || 0);
      if(r <= 0){{
        chosenPOI = p;
        break;
      }}
    }}
    const v = spawnVehicleForDestination(chosenPOI.id);
    if(v) vehicles.push(v);
    else break;
  }}
}}

function updateVehicles(dt){{
  const rainSlowdown = rainOn ? [1, 0.72, 0.50, 0.32][rainIntensity] : 1.0;
  
  vehicles.forEach(v => {{
    if(v.segIdx >= v.coords.length-1){{
      // Reached end of current road, find next road leading toward targetPOI
      const lastCoord = v.coords[v.coords.length-1];
      const nextChoice = findNextRoad(v.roadId, lastCoord, v.targetPos, v.type==='bus');

      if(nextChoice){{
        v.roadId = nextChoice.road.id;
        const wpts = roadWorldPts[nextChoice.road.id];
        v.coords = nextChoice.forward ? [...wpts] : [...wpts].reverse();
        v.segIdx = 0;
        v.segProg = 0;
      }} else {{
        // Reached destination or cul-de-sac: pick new route or return trip
        const avail = roads.filter(r => !blockedRoads.has(r.id) && (v.type!=='bus' || r.busRoute));
        if(avail.length){{
          const rRoad = avail[Math.floor(Math.random()*avail.length)];
          v.roadId = rRoad.id;
          v.coords = Math.random()>0.5 ? [...roadWorldPts[rRoad.id]] : [...roadWorldPts[rRoad.id]].reverse();
          v.segIdx = 0; v.segProg = 0;
        }}
      }}
      return;
    }}

    const p1 = v.coords[v.segIdx];
    const p2 = v.coords[v.segIdx+1];
    const dx = p2.x - p1.x;
    const dz = p2.z - p1.z;
    const len = Math.sqrt(dx*dx + dz*dz);

    // Deep water resistance
    let waterDrag = 1.0;
    if(waterAccumulationLevel > 0.3){{
      for(const s of waterlogSpots){{
        const pos = geo(s.lat, s.lng);
        const distToWater = Math.hypot(v.mesh.position.x - pos.x, v.mesh.position.z - pos.z);
        if(distToWater < s.radius){{
          waterDrag = s.baseDepth >= 40 ? 0.30 : 0.60;
          break;
        }}
      }}
    }}

    const effectiveSpeed = v.speed * rainSlowdown * waterDrag * simSpeed * 0.16;
    v.segProg += (effectiveSpeed * dt) / Math.max(len, 0.1);

    if(v.segProg >= 1){{
      v.segIdx++;
      v.segProg = 0;
    }} else {{
      const curX = p1.x + dx * v.segProg;
      const curZ = p1.z + dz * v.segProg;
      v.mesh.position.set(curX, 0.25, curZ);
      v.mesh.rotation.y = Math.atan2(dx, dz);
    }}
  }});
}}

// ==========================================
// 10. REAL-TIME RAIN DROP PARTICLES
// ==========================================
let rainSystem = null;
let rainGeo = null;

function setupRainParticles(){{
  cleanupRainParticles();
  const particleCount = [0, 1200, 3200, 7500][rainIntensity];
  if(!particleCount) return;

  rainGeo = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  const speeds = new Float32Array(particleCount);

  for(let i=0; i<particleCount; i++){{
    positions[i*3] = (Math.random() - 0.5) * 450;
    positions[i*3+1] = Math.random() * 110 + 10;
    positions[i*3+2] = (Math.random() - 0.5) * 450;
    speeds[i] = 45 + Math.random() * 45;
  }}
  rainGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  rainGeo.speeds = speeds;

  const rainMat = new THREE.PointsMaterial({{
    color: 0x93c5fd, size: 0.45, transparent: true, opacity: 0.65
  }});
  rainSystem = new THREE.Points(rainGeo, rainMat);
  scene.add(rainSystem);
}}

function cleanupRainParticles(){{
  if(rainSystem){{
    scene.remove(rainSystem);
    rainSystem = null;
    rainGeo = null;
  }}
}}

function updateRainSimulation(dt){{
  if(!rainSystem || !rainGeo) return;
  const pos = rainGeo.attributes.position.array;
  const speeds = rainGeo.speeds;
  for(let i=0; i<speeds.length; i++){{
    pos[i*3+1] -= speeds[i] * dt * simSpeed;
    if(pos[i*3+1] <= 0){{
      pos[i*3+1] = 110 + Math.random()*15;
    }}
  }}
  rainGeo.attributes.position.needsUpdate = true;
}}

// ==========================================
// 11. ROAD BLOCKING & REROUTING
// ==========================================
const blockBarriers = {{}};
const rerouteTubes = [];
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('click', e => {{
  if(!blockMode) return;
  const rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((e.clientX - rect.left)/rect.width)*2 - 1;
  mouse.y = -((e.clientY - rect.top)/rect.height)*2 + 1;
  raycaster.setFromCamera(mouse, camera);

  const targets = [];
  Object.values(roadMeshes).forEach(rg => {{
    rg.children.forEach(c => {{ if(c.roadId) targets.push(c); }});
  }});

  const hits = raycaster.intersectObjects(targets);
  if(hits.length > 0){{
    const rid = hits[0].object.roadId;
    if(rid) toggleRoadBlock(rid);
  }}
}});

function toggleRoadBlock(rid){{
  if(blockedRoads.has(rid)) unblockRoad(rid);
  else blockRoad(rid);
  updateDashboard();
  updateReroutingReport();
}}

function blockRoad(rid){{
  blockedRoads.add(rid);
  const roadGroup = roadMeshes[rid];
  if(roadGroup){{
    roadGroup.children.forEach(c => {{
      if(c.material) {{
        c.material.transparent = true;
        c.material.opacity = 0.22;
      }}
    }});
  }}

  const wpts = roadWorldPts[rid] || [];
  const barriers = [];
  wpts.forEach(p => {{
    const postGeo = new THREE.CylinderGeometry(0.35, 0.35, 3.5, 8);
    const postMat = new THREE.MeshStandardMaterial({{color:0xef4444, emissive:0xef4444, emissiveIntensity:0.6}});
    const post = new THREE.Mesh(postGeo, postMat);
    post.position.set(p.x, 1.75, p.z);
    scene.add(post);
    barriers.push(post);

    const barGeo = new THREE.BoxGeometry(2.4, 0.45, 0.2);
    const barMat = new THREE.MeshBasicMaterial({{color:0xffffff}});
    const sign = new THREE.Mesh(barGeo, barMat);
    sign.position.set(p.x, 3.2, p.z);
    scene.add(sign);
    barriers.push(sign);
  }});
  blockBarriers[rid] = barriers;

  // Immediately redirect vehicles currently traversing this road
  vehicles.forEach(v => {{
    if(v.roadId === rid){{
      const avail = roads.filter(r => !blockedRoads.has(r.id) && (v.type!=='bus' || r.busRoute));
      if(avail.length){{
        const alt = avail[Math.floor(Math.random()*avail.length)];
        v.roadId = alt.id;
        v.coords = [...roadWorldPts[alt.id]];
        v.segIdx = 0; v.segProg = 0;
      }}
    }}
  }});
}}

function unblockRoad(rid){{
  blockedRoads.delete(rid);
  const roadGroup = roadMeshes[rid];
  if(roadGroup){{
    roadGroup.children.forEach(c => {{
      if(c.material) {{
        c.material.transparent = false;
        c.material.opacity = 1.0;
      }}
    }});
  }}
  if(blockBarriers[rid]){{
    blockBarriers[rid].forEach(m => scene.remove(m));
    delete blockBarriers[rid];
  }}
}}

function clearBlocks(){{
  [...blockedRoads].forEach(id => unblockRoad(id));
  rerouteTubes.forEach(t => scene.remove(t));
  rerouteTubes.length = 0;
  updateDashboard();
  updateReroutingReport();
}}

function updateReroutingReport(){{
  const div = document.getElementById('reroute-box');
  rerouteTubes.forEach(t => scene.remove(t));
  rerouteTubes.length = 0;

  if(!blockedRoads.size){{
    div.innerHTML = '<p style="color:#94a3b8">Turn on <b style="color:#fcd34d">Road Block Mode</b> and click any road in the 3D scene to analyze traffic displacement & alternate bypasses.</p>';
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
    if(alts.length){{
      html += `<span style="color:#94a3b8">Recommended Reroutes:</span><br>`;
      alts.forEach(a => {{
        const addedLoad = Math.round(displaced / alts.length);
        const newLoadPct = Math.min(100, a.traffic + Math.round(addedLoad * 100 / a.capacity));
        html += `<span style="color:#2dd4bf">⤷ ${{a.name}}</span> <span style="color:#fcd34d">(+${{addedLoad}} veh/hr, ${{newLoadPct}}% load)</span><br>`;

        const wpts = roadWorldPts[a.id];
        if(wpts && wpts.length >= 2){{
          const curvePts = wpts.map(p => new THREE.Vector3(p.x, 2.2, p.z));
          const curve = new THREE.CatmullRomCurve3(curvePts);
          const tubeGeo = new THREE.TubeGeometry(curve, 24, 0.6, 8, false);
          const tubeMat = new THREE.MeshBasicMaterial({{color:0xf97316, transparent:true, opacity:0.45}});
          const tubeMesh = new THREE.Mesh(tubeGeo, tubeMat);
          scene.add(tubeMesh);
          rerouteTubes.push(tubeMesh);
        }}
      }});
    }}
    html += `</div>`;
  }});

  // Impact on POIs
  html += `<div style="margin-top:6px;padding:6px;background:#09192b;border-radius:5px">`;
  html += `<b style="color:#38bdf8">📍 Destination Access Impact:</b><br>`;
  pois.forEach(p => {{
    const near = blockedArr.some(bid => {{
      const br = roads.find(r => r.id === bid);
      if(!br) return false;
      const pp = geo(p.lat, p.lng);
      return br.pts.some(pt => {{
        const g = geo(pt[0], pt[1]);
        return Math.hypot(g.x-pp.x, g.z-pp.z) < 32;
      }});
    }});
    if(near){{
      const affectedVisitors = Math.round((destVehTargets[p.id] || 50) * 1.5);
      html += `<span style="color:#f87171">${{p.icon}} ${{p.name}}: ~${{affectedVisitors}} commuters delayed</span><br>`;
    }}
  }});
  html += `</div>`;
  html += `<div style="margin-top:5px;color:#fcd34d;font-weight:700">Total Traffic Displaced: ${{totalDisplaced.toLocaleString()}} veh/hr</div>`;
  div.innerHTML = html;
}}

// ==========================================
// 12. CANVAS LABEL GENERATOR
// ==========================================
function makeLabel(text, pos, y, color='#38bdf8'){{
  const canvas = document.createElement('canvas');
  canvas.width = 512; canvas.height = 72;
  const ctx = canvas.getContext('2d');
  ctx.font = 'bold 26px "Segoe UI", sans-serif';
  ctx.fillStyle = color;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.shadowColor = 'rgba(0,0,0,0.9)';
  ctx.shadowBlur = 6;
  ctx.fillText(text, 256, 36);

  const texture = new THREE.CanvasTexture(canvas);
  texture.minFilter = THREE.LinearFilter;
  const mat = new THREE.SpriteMaterial({{map:texture, depthTest:false, transparent:true}});
  const sprite = new THREE.Sprite(mat);
  sprite.position.set(pos.x, y, pos.z);
  sprite.scale.set(22, 3.1, 1);
  scene.add(sprite);
  sprite.canvas = canvas;
  sprite.ctx = ctx;
  sprite.texture = texture;
  return sprite;
}}

function updateLabelText(sprite, newText, color='#38bdf8'){{
  if(!sprite || !sprite.ctx) return;
  const ctx = sprite.ctx;
  ctx.clearRect(0, 0, 512, 72);
  ctx.font = 'bold 26px "Segoe UI", sans-serif';
  ctx.fillStyle = color;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.shadowColor = 'rgba(0,0,0,0.9)';
  ctx.shadowBlur = 6;
  ctx.fillText(newText, 256, 36);
  sprite.texture.needsUpdate = true;
}}

// ==========================================
// 13. UI CONTROLS & DESTINATION SLIDERS
// ==========================================
function initDestinationSliders(){{
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
        <input type="range" min="0" max="400" value="${{currentVal}}" id="slider-${{p.id}}" 
          oninput="setDestinationTraffic('${{p.id}}', this.value)">
      </div>`;
  }});
  container.innerHTML = html;
}}

function setDestinationTraffic(poiId, val){{
  const intVal = parseInt(val);
  destVehTargets[poiId] = intVal;
  const badge = document.getElementById(`badge-${{poiId}}`);
  if(badge) badge.textContent = `${{intVal}} veh/hr`;
  rebalanceVehicles();
  updateDashboard();
}}

function toggleSim(){{
  simRunning = !simRunning;
  document.getElementById('btn-play').classList.toggle('active', simRunning);
  document.getElementById('btn-pause').classList.toggle('active', !simRunning);
}}

function setSpd(s, btn){{
  simSpeed = s;
  document.querySelectorAll('.speed-btns .btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}}

function setTOD(val){{
  timeOfDay = parseInt(val);
  const labels = ['Late Night','Late Night','Late Night','Late Night','Early Hours','Dawn Commute','Morning Kickoff','Morning Rush (Peak)','Morning Rush','Morning Commercial','Midday Lull','Afternoon Flow','Afternoon Peak','School Rush','Late Afternoon','Evening Commute','Evening Rush (Peak)','Evening Rush','Night Bazaar','Night Market','Night Commercial','Late Night','Midnight Shift','Dead Hours'];
  document.getElementById('tod-lbl').textContent = labels[timeOfDay];
  
  if(timeOfDay>=6 && timeOfDay<=17){{
    sunLight.intensity = 1.35; ambientLight.intensity = 0.85;
    scene.background.set(0x0a1224); scene.fog.color.set(0x0a1224);
  }} else {{
    sunLight.intensity = 0.25; ambientLight.intensity = 0.40;
    scene.background.set(0x040812); scene.fog.color.set(0x040812);
  }}
  rebalanceVehicles();
  updateDashboard();
}}

function togVeh(type, on){{
  vehConfigs[type].enabled = on;
  rebalanceVehicles();
  updateDashboard();
}}

function toggleRain(on){{
  rainOn = on;
  if(on) setupRainParticles();
  else cleanupRainParticles();
  updateDashboard();
}}

function setRainInt(v){{
  rainIntensity = parseInt(v);
  document.getElementById('rain-lbl').textContent = ['','Light Shower','Moderate Downpour','Severe Cloudburst (Monsoon)'][rainIntensity];
  if(rainOn) setupRainParticles();
  updateDashboard();
}}

function toggleWaterVis(on){{
  waterlogMeshes.forEach(wm => {{
    wm.puddle.visible = on;
    wm.ripple.visible = on;
  }});
}}

function camPreset(p){{
  if(p==='overview'){{ camTheta=Math.PI/4; camPhi=Math.PI/3.6; camDist=180; camTarget.set(0,0,0); }}
  else if(p==='street'){{ camTheta=Math.PI/2.8; camPhi=Math.PI/2.3; camDist=42; camTarget.set(0,0,0); }}
  else if(p==='coastal'){{ camTheta=Math.PI/1.2; camPhi=Math.PI/3.2; camDist=130; camTarget.set(40,0,0); }}
  else if(p==='waterlog'){{ camTheta=Math.PI/3.5; camPhi=Math.PI/2.6; camDist=55; camTarget.set(-25,0,0); }}
}}

// ==========================================
// 14. DASHBOARD & STATS UPDATE
// ==========================================
function updateDashboard(){{
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

  // Road list (sample top 12 roads)
  let rhtml = '';
  roads.slice(0, 12).forEach(r => {{
    const extra = blockedRoads.size && !blockedRoads.has(r.id) ? Math.round(blockedRoads.size*7) : 0;
    const t = Math.min(100, r.traffic + extra + (rainOn ? rainIntensity*6 : 0));
    const cls = t<50 ? 'color:#10b981' : t<75 ? 'color:#f59e0b' : 'color:#ef4444';
    const blk = blockedRoads.has(r.id);
    rhtml += `
      <div style="display:flex;justify-content:space-between;padding:4px 8px;background:#101a33;border-radius:4px;margin-bottom:3px;font-size:10.5px;${{blk?'opacity:0.4;text-decoration:line-through':''}}">
        <span style="color:#cbd5e1">${{r.name}}</span>
        <span class="road-tag" style="${{cls}}">${{blk ? 'BLOCKED' : t + '%'}}</span>
      </div>`;
  }});
  document.getElementById('road-list').innerHTML = rhtml;

  // Update floating labels on 3D landmarks with incoming vehicle count
  poiMeshes.forEach(pm => {{
    const incoming = vehicles.filter(v => v.targetPOI && v.targetPOI.id === pm.data.id).length;
    updateLabelText(pm.labelSprite, `${{pm.data.icon}} ${{pm.data.name}} (${{incoming}} on route)`, '#f8fafc');
  }});
}}

// ==========================================
// 15. RENDER LOOP
// ==========================================
const clock = new THREE.Clock();

function animate(){{
  requestAnimationFrame(animate);
  const dt = clock.getDelta();
  const elapsedTime = clock.getElapsedTime();

  updateCamera();

  if(simRunning){{
    updateVehicles(dt);
    if(rainOn) updateRainSimulation(dt);
  }}

  updateWaterlogVisuals(rainIntensity, rainOn);

  sea.position.y = 0.14 + Math.sin(elapsedTime*1.5)*0.08;

  poiMeshes.forEach((p, idx) => {{
    p.ring.scale.setScalar(1.0 + Math.sin(elapsedTime*2.5 + idx)*0.22);
    p.crown.position.y = p.data.h + 5 + Math.sin(elapsedTime*3.0 + idx)*0.35;
  }});

  renderer.render(scene, camera);
}}

// Resize
window.addEventListener('resize', () => {{
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}});

// Boot
initDestinationSliders();
rebalanceVehicles();
updateDashboard();
setInterval(() => {{ if(simRunning) updateDashboard(); }}, 2000);
animate();
</script>
</body>
</html>
'''

with open("c:/Users/SAAQIB/areatwin/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated index.html successfully! Length: {len(html_content)} bytes")
