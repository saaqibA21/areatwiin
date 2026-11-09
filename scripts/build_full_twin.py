import json

with open("c:/Users/SAAQIB/areatwin/royapuram_roads.json", "r", encoding="utf-8") as f:
    roads_data = json.load(f)

roads_json_str = json.dumps(roads_data)

html_code = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Royapuram 3D Digital Twin - Ultra-Realistic Simulation</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:#030712;color:#f3f4f6;overflow:hidden;height:100vh}}
#app{{display:flex;height:100vh;width:100vw}}
#canvas-container{{flex:1;position:relative;background:#030712}}
canvas{{display:block;width:100%;height:100%}}
#sidebar{{width:420px;background:linear-gradient(180deg,#0a1124 0%,#0c152c 100%);border-left:1px solid #1f2d52;overflow-y:auto;z-index:20;flex-shrink:0;box-shadow:-8px 0 35px rgba(0,0,0,0.7)}}
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
.list-box{{max-height:230px;overflow-y:auto;padding-right:3px}}
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
#bottom-bar{{position:absolute;bottom:0;left:0;right:420px;z-index:10;background:linear-gradient(transparent,rgba(4,8,18,0.96) 30%);padding:10px 20px;display:flex;gap:12px;justify-content:center}}
.bs{{text-align:center;background:#0f172acc;backdrop-filter:blur(6px);border:1px solid #1e293b;border-radius:8px;padding:8px 15px;min-width:105px}}
.bs .v{{font-size:16px;font-weight:700;color:#2dd4bf}}
.bs .l{{font-size:8.5px;color:#94a3b8;text-transform:uppercase;margin-top:2px;letter-spacing:0.5px}}
#cam-hint{{position:absolute;bottom:65px;left:50%;transform:translateX(-50%);z-index:10;color:#94a3b8;font-size:11px;background:#080c1ad6;padding:5px 18px;border-radius:20px;border:1px solid #1e294b;pointer-events:none;letter-spacing:0.3px}}
.cbar{{width:100%;height:6px;background:#1e293b;border-radius:3px;margin-top:6px;overflow:hidden}}
.cfill{{height:100%;border-radius:3px;transition:width .5s,background .5s}}
.road-tag{{font-size:10px;font-weight:600}}
#follow-badge{{position:absolute;top:70px;left:22px;z-index:12;background:#0f172ae6;border:1px solid #38bdf8;border-radius:16px;padding:5px 14px;font-size:11px;color:#38bdf8;display:none;align-items:center;gap:8px}}
::-webkit-scrollbar{{width:5px}}
::-webkit-scrollbar-track{{background:#030712}}
::-webkit-scrollbar-thumb{{background:#1e294b;border-radius:3px}}
</style>
</head>
<body>
<div id="app">
<div id="canvas-container">
  <div id="hud">
    <h1>🏙️ Royapuram Digital Twin <span class="tag">Fully Detailed 3D Model</span></h1>
    <div id="time-disp">🕐 08:00 AM</div>
  </div>
  <div id="follow-badge">
    <span>🎥 Following Vehicle: <b id="follow-name">Car</b></span>
    <button class="btn" style="padding:2px 7px;font-size:10px" onclick="stopFollow()">Exit Cam</button>
  </div>
  <div id="bottom-bar">
    <div class="bs"><div class="v" id="bs-v">0</div><div class="l">Live Fleet</div></div>
    <div class="bs"><div class="v" id="bs-s">0 km/h</div><div class="l">Avg Speed</div></div>
    <div class="bs"><div class="v" id="bs-c">0%</div><div class="l">Congestion</div></div>
    <div class="bs"><div class="v" id="bs-r">Dry</div><div class="l">Monsoon Rain</div></div>
    <div class="bs"><div class="v" id="bs-w">0 cm</div><div class="l">Water Stagnant</div></div>
    <div class="bs"><div class="v" id="bs-b">0</div><div class="l">Blocked Roads</div></div>
  </div>
  <div id="cam-hint">🖱️ Left-drag: Orbit | Right-drag: Pan | Scroll: Zoom | Click any vehicle to Chase Cam | Block Mode: Click road</div>
</div>
<div id="sidebar">
  <!-- Simulation Controls -->
  <div class="panel">
    <h3><span>⚙️</span> Simulation Controls</h3>
    <div class="ctrl"><label>Map Visual Style</label>
      <div style="display:flex;gap:4px">
        <button class="btn active" id="btn-style-sat" onclick="setMapStyle('satellite')">🛰️ Satellite</button>
        <button class="btn" id="btn-style-dark" onclick="setMapStyle('dark')">🏙️ Dark 3D</button>
      </div>
    </div>
    <div class="ctrl"><label>3D Architectural Landmarks</label>
      <label class="toggle"><input type="checkbox" id="bld-tog" checked onchange="toggleBuildings(this.checked)"><span class="sl"></span></label>
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
    <div class="ctrl" style="margin-top:8px"><label>🎥 Cinematic Camera Presets</label>
      <div style="display:flex;gap:3px;flex-wrap:wrap">
        <button class="btn" onclick="camPreset('overview')">Aerial</button>
        <button class="btn" onclick="camPreset('station')">Station</button>
        <button class="btn" onclick="camPreset('harbour')">Harbour</button>
        <button class="btn" onclick="camPreset('temple')">Temple</button>
        <button class="btn" onclick="camPreset('waterlog')">Floods</button>
      </div>
    </div>
  </div>

  <!-- Target Destination Traffic Allocator -->
  <div class="panel">
    <h3><span>🎯</span> Destination Traffic Allocator</h3>
    <p style="font-size:10px;color:#94a3b8;margin-bottom:8px">Change vehicles sent to each landmark — watch live route pathfinding on all 30 roads:</p>
    <div class="list-box" id="dest-sliders"></div>
  </div>

  <!-- Rain & Water Stagnation Simulation -->
  <div class="panel">
    <h3><span>🌧️</span> Rain & Water Stoppage (Flooding)</h3>
    <div class="ctrl"><label>Monsoon Rainfall</label><label class="toggle"><input type="checkbox" id="rain-tog" onchange="toggleRain(this.checked)"><span class="sl"></span></label></div>
    <div class="ctrl"><label>Rainfall Intensity</label><span id="rain-lbl" style="font-size:11px;color:#38bdf8;font-weight:600">Light Shower</span></div>
    <input type="range" id="rain-sl" min="1" max="3" value="1" oninput="setRainInt(this.value)">
    <div class="ctrl" style="margin-top:6px"><label>Water Depth Gauges & Ripples</label>
      <label class="toggle"><input type="checkbox" id="water-vis-tog" checked onchange="toggleWaterVis(this.checked)"><span class="sl"></span></label>
    </div>
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
    <h3><span>🛣️</span> 30-Road Network Status</h3>
    <div class="list-box" id="road-list" style="max-height:160px"></div>
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
// 1. GEO COORDINATES & SYSTEM
// ==========================================
const CENTER = {{lat:13.1040, lng:80.2937}};
const SCALE = 85000;
function geo(lat, lng){{
  return {{x:(lng-CENTER.lng)*SCALE, z:-(lat-CENTER.lat)*SCALE}};
}}

// ==========================================
// 2. THREE.JS SCENE SETUP
// ==========================================
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x040814);
scene.fog = new THREE.FogExp2(0x040814, 0.002);

const camera = new THREE.PerspectiveCamera(48, container.clientWidth/container.clientHeight, 0.5, 4000);
camera.position.set(0, 120, 150);

const renderer = new THREE.WebGLRenderer({{antialias:true, powerPreference:"high-performance"}});
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.35;
container.appendChild(renderer.domElement);

// Lighting
const ambientLight = new THREE.AmbientLight(0x475569, 0.9);
scene.add(ambientLight);

const sunLight = new THREE.DirectionalLight(0xfffbeb, 1.35);
sunLight.position.set(90, 170, 70);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(2048, 2048);
sunLight.shadow.camera.left = -240;
sunLight.shadow.camera.right = 240;
sunLight.shadow.camera.top = 240;
sunLight.shadow.camera.bottom = -240;
scene.add(sunLight);

const skyLight = new THREE.HemisphereLight(0x38bdf8, 0x0f172a, 0.65);
scene.add(skyLight);

// ==========================================
// 3. ORBIT CONTROLS & CHASE CAM
// ==========================================
let camTheta = Math.PI/4, camPhi = Math.PI/3.6, camDist = 180, camTarget = new THREE.Vector3(0,0,0);
let isDragging = false, isPanning = false, lastMX = 0, lastMY = 0;
let followedVehicle = null;

renderer.domElement.addEventListener('mousedown', e => {{
  if(e.button===0) isDragging=true;
  else if(e.button===2) isPanning=true;
  lastMX=e.clientX; lastMY=e.clientY;
}});
window.addEventListener('mouseup', () => {{isDragging=false; isPanning=false;}});
renderer.domElement.addEventListener('mousemove', e => {{
  const dx=e.clientX-lastMX, dy=e.clientY-lastMY;
  lastMX=e.clientX; lastMY=e.clientY;
  if(isDragging && !followedVehicle){{
    camTheta -= dx*0.0055;
    camPhi = Math.max(0.08, Math.min(Math.PI/2-0.03, camPhi-dy*0.0055));
  }}
  if(isPanning && !followedVehicle){{
    const right = new THREE.Vector3(-Math.cos(camTheta), 0, Math.sin(camTheta));
    const fwd = new THREE.Vector3(-Math.sin(camTheta), 0, -Math.cos(camTheta));
    camTarget.addScaledVector(right, dx*0.18);
    camTarget.addScaledVector(fwd, -dy*0.18);
  }}
}});
renderer.domElement.addEventListener('wheel', e => {{
  if(!followedVehicle){{
    camDist = Math.max(12, Math.min(650, camDist + e.deltaY*0.12));
  }}
  e.preventDefault();
}},{{passive:false}});
renderer.domElement.addEventListener('contextmenu', e=>e.preventDefault());

function updateCamera(){{
  if(followedVehicle && followedVehicle.mesh){{
    const vPos = followedVehicle.mesh.position;
    const vRot = followedVehicle.mesh.rotation.y;
    // Bumper / chase camera 6 units behind and 3 units above
    const behindX = vPos.x - Math.sin(vRot)*10;
    const behindZ = vPos.z - Math.cos(vRot)*10;
    camera.position.set(behindX, vPos.y + 4.5, behindZ);
    camera.lookAt(vPos.x + Math.sin(vRot)*15, vPos.y + 1.2, vPos.z + Math.cos(vRot)*15);
  }} else {{
    camera.position.set(
      camTarget.x + camDist*Math.sin(camPhi)*Math.sin(camTheta),
      camTarget.y + camDist*Math.cos(camPhi),
      camTarget.z + camDist*Math.sin(camPhi)*Math.cos(camTheta)
    );
    camera.lookAt(camTarget);
  }}
}}

function followVehicle(v){{
  followedVehicle = v;
  document.getElementById('follow-badge').style.display = 'flex';
  document.getElementById('follow-name').textContent = `${{v.type.toUpperCase()}} -> ${{v.targetPOI.name}}`;
}}
function stopFollow(){{
  followedVehicle = null;
  document.getElementById('follow-badge').style.display = 'none';
  camTarget.set(0,0,0);
  camDist = 140;
}}

// ==========================================
// 4. REAL SATELLITE TERRAIN & OCEAN
// ==========================================
const terrainGeo = new THREE.PlaneGeometry(800, 800, 20, 20);
const terrainMat = new THREE.MeshStandardMaterial({{color:0x0a1122, roughness:0.92, metalness:0.05}});
const terrain = new THREE.Mesh(terrainGeo, terrainMat);
terrain.rotation.x = -Math.PI/2;
terrain.receiveShadow = true;
scene.add(terrain);

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

// Bay of Bengal animated ocean surface
const seaGeo = new THREE.PlaneGeometry(240, 800, 20, 20);
const seaMat = new THREE.MeshStandardMaterial({{
  color:0x0284c7, roughness:0.1, metalness:0.8,
  transparent:true, opacity:0.65, emissive:0x0369a1, emissiveIntensity:0.25
}});
const sea = new THREE.Mesh(seaGeo, seaMat);
sea.rotation.x = -Math.PI/2;
sea.position.set(165, 0.14, 0);
scene.add(sea);

// Coastal Breakwater Tetrapods along Beach Road
const tetrapodGroup = new THREE.Group();
const tetraMat = new THREE.MeshStandardMaterial({{color:0x64748b, roughness:0.9}});
for(let z = -180; z <= 180; z += 9){{
  const tGeo = new THREE.CylinderGeometry(0.5, 0.8, 2.2, 5);
  const tMesh = new THREE.Mesh(tGeo, tetraMat);
  tMesh.position.set(48 + Math.sin(z)*1.5, 1.0, z);
  tMesh.rotation.z = 0.4;
  tetrapodGroup.add(tMesh);
}}
scene.add(tetrapodGroup);

makeLabel("🌊 Bay of Bengal (Chennai Port Breakwater)", {{x:165,z:0}}, 14, '#38bdf8');

function setMapStyle(style){{
  const btnSat = document.getElementById('btn-style-sat');
  const btnDark = document.getElementById('btn-style-dark');
  if(style === 'satellite'){{
    satMesh.visible = true;
    seaMat.opacity = 0.65;
    btnSat.classList.add('active');
    btnDark.classList.remove('active');
  }} else {{
    satMesh.visible = false;
    seaMat.opacity = 0.88;
    btnDark.classList.add('active');
    btnSat.classList.remove('active');
  }}
}}

// ==========================================
// 5. 30 DETAILED ROADS & JUNCTIONS
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

    // Asphalt Bed
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

    // Concrete Curbs
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

    // White Edge Lines
    const edgeLineGeo = new THREE.BoxGeometry(0.12, 0.05, len);
    const edgeLineMat = new THREE.MeshBasicMaterial({{color: 0xffffff}});
    const edgeL = new THREE.Mesh(edgeLineGeo, edgeLineMat);
    edgeL.position.set(midX - Math.cos(angle)*(r.width*0.44), 0.36, midZ + Math.sin(angle)*(r.width*0.44));
    edgeL.rotation.y = angle;
    roadGroup.add(edgeL);

    const edgeR = edgeL.clone();
    edgeR.position.set(midX + Math.cos(angle)*(r.width*0.44), 0.36, midZ - Math.sin(angle)*(r.width*0.44));
    roadGroup.add(edgeR);

    // Center Line
    const dashGeo = new THREE.BoxGeometry(0.18, 0.05, len);
    const dashMat = new THREE.MeshBasicMaterial({{color: r.lineColor || 0xffffff}});
    const centerLine = new THREE.Mesh(dashGeo, dashMat);
    centerLine.position.set(midX, 0.36, midZ);
    centerLine.rotation.y = angle;
    roadGroup.add(centerLine);

    // Junction Connection
    const capGeo = new THREE.CylinderGeometry(r.width/2 + curbWidth, r.width/2 + curbWidth, 0.25, 16);
    const cap = new THREE.Mesh(capGeo, roadMat);
    cap.position.set(p1.x, 0.22, p1.z);
    roadGroup.add(cap);

    // Zebra Crossings at Major Intersections
    if(i === 0 && (r.type === 'arterial' || r.type === 'highway')){{
      for(let zOff = -r.width*0.35; zOff <= r.width*0.35; zOff += 1.1){{
        const zebraGeo = new THREE.BoxGeometry(0.5, 0.06, 2.5);
        const zebraMat = new THREE.MeshBasicMaterial({{color: 0xffffff}});
        const zebra = new THREE.Mesh(zebraGeo, zebraMat);
        zebra.position.set(p1.x + Math.sin(angle)*1.5 + Math.cos(angle)*zOff, 0.37, p1.z + Math.cos(angle)*1.5 - Math.sin(angle)*zOff);
        zebra.rotation.y = angle;
        roadGroup.add(zebra);
      }}
    }}
  }}

  scene.add(roadGroup);
  roadMeshes[r.id] = roadGroup;

  const midPoint = wpts[Math.floor(wpts.length/2)];
  makeLabel(r.name, midPoint, 4.0, r.type==='highway'?'#facc15':r.type==='arterial'?'#38bdf8':'#cbd5e1');
}});

// ==========================================
// 6. DETAILED ARCHITECTURAL LANDMARKS
// ==========================================
const bldGroup = new THREE.Group();

// 1. Royapuram Railway Station (Heritage 1856 - Red & White Colonial)
function createRailwayStation(pos){{
  const stGroup = new THREE.Group();
  stGroup.position.set(pos.x, 0, pos.z);

  // Main Portico Wing
  const mainGeo = new THREE.BoxGeometry(22, 9, 12);
  const redMat = new THREE.MeshStandardMaterial({{color:0xb91c1c, roughness:0.65}});
  const whiteMat = new THREE.MeshStandardMaterial({{color:0xf8fafc, roughness:0.5}});
  const mainBld = new THREE.Mesh(mainGeo, redMat);
  mainBld.position.y = 4.5;
  stGroup.add(mainBld);

  // White Victorian Portico Columns & Arches
  for(let x = -8; x <= 8; x += 4){{
    const colGeo = new THREE.CylinderGeometry(0.4, 0.4, 6, 8);
    const col = new THREE.Mesh(colGeo, whiteMat);
    col.position.set(x, 3, 7.5);
    stGroup.add(col);
  }}

  // Central Clock Tower
  const towerGeo = new THREE.BoxGeometry(7, 18, 7);
  const tower = new THREE.Mesh(towerGeo, redMat);
  tower.position.set(0, 9, 0);
  stGroup.add(tower);

  // Clock face
  const clockGeo = new THREE.CylinderGeometry(1.6, 1.6, 0.4, 16);
  const clockMesh = new THREE.Mesh(clockGeo, whiteMat);
  clockMesh.rotation.x = Math.PI/2;
  clockMesh.position.set(0, 14, 3.6);
  stGroup.add(clockMesh);

  // Pitched Heritage Roof
  const roofGeo = new THREE.ConeGeometry(5.2, 5, 4);
  const roofMat = new THREE.MeshStandardMaterial({{color:0x7f1d1d, roughness:0.4}});
  const roof = new THREE.Mesh(roofGeo, roofMat);
  roof.rotation.y = Math.PI/4;
  roof.position.set(0, 20.5, 0);
  stGroup.add(roof);

  // Southern Railway Tracks & Platforms behind the station
  const trackMat = new THREE.MeshStandardMaterial({{color:0x334155, roughness:0.8}});
  for(let t = -6; t <= 6; t += 3){{
    const railGeo = new THREE.BoxGeometry(45, 0.2, 0.4);
    const rail = new THREE.Mesh(railGeo, trackMat);
    rail.position.set(0, 0.25, -9 + t);
    stGroup.add(rail);
  }}

  bldGroup.add(stGroup);
}}

// 2. Kasimedu Fishing Harbour & Wharf
function createFishingHarbour(pos){{
  const hGroup = new THREE.Group();
  hGroup.position.set(pos.x, 0, pos.z);

  // Concrete Wharf Quayside
  const pierGeo = new THREE.BoxGeometry(38, 1.8, 26);
  const pierMat = new THREE.MeshStandardMaterial({{color:0x475569, roughness:0.8}});
  const pier = new THREE.Mesh(pierGeo, pierMat);
  pier.position.y = 0.9;
  hGroup.add(pier);

  // Blue Tin Auction Shed
  const shedGeo = new THREE.BoxGeometry(26, 6, 12);
  const shedMat = new THREE.MeshStandardMaterial({{color:0x0284c7, roughness:0.4, metalness:0.3}});
  const shed = new THREE.Mesh(shedGeo, shedMat);
  shed.position.set(-2, 4.0, 0);
  hGroup.add(shed);

  // Docked Fishing Trawlers / Boats
  const boatColors = [0xef4444, 0xf59e0b, 0x10b981, 0x3b82f6];
  for(let i = 0; i < 6; i++){{
    const bGeo = new THREE.BoxGeometry(3.5, 1.4, 7);
    const bMat = new THREE.MeshStandardMaterial({{color:boatColors[i%4], roughness:0.5}});
    const boat = new THREE.Mesh(bGeo, bMat);
    boat.position.set(13, 0.6, -9 + i*3.6);
    hGroup.add(boat);

    // Mast
    const mastGeo = new THREE.CylinderGeometry(0.1, 0.1, 4, 6);
    const mastMat = new THREE.MeshBasicMaterial({{color:0xfacc15}});
    const mast = new THREE.Mesh(mastGeo, mastMat);
    mast.position.set(13, 2.5, -9 + i*3.6);
    hGroup.add(mast);
  }}

  bldGroup.add(hGroup);
}}

// 3. Dravidian Hindu Temple Gopuram
function createTempleGopuram(pos, templeName, primaryColor=0xeab308){{
  const tGroup = new THREE.Group();
  tGroup.position.set(pos.x, 0, pos.z);

  // Stepped Tier Pyramidal Gopuram
  const tiers = 5;
  for(let i=0; i<tiers; i++){{
    const width = 12 - i*1.8;
    const depth = 8 - i*1.1;
    const gGeo = new THREE.BoxGeometry(width, 3.2, depth);
    const gMat = new THREE.MeshStandardMaterial({{
      color: primaryColor, roughness:0.5, metalness:0.2, emissive:primaryColor, emissiveIntensity:0.15
    }});
    const tier = new THREE.Mesh(gGeo, gMat);
    tier.position.y = 1.6 + i*3.2;
    tGroup.add(tier);
  }}

  // Gold Kalasam Finials on top
  const finialGeo = new THREE.ConeGeometry(0.4, 1.8, 8);
  const finialMat = new THREE.MeshStandardMaterial({{color:0xfacc15, metalness:0.9, roughness:0.2}});
  for(let k = -2; k <= 2; k += 1.2){{
    const finial = new THREE.Mesh(finialGeo, finialMat);
    finial.position.set(k, 18.5, 0);
    tGroup.add(finial);
  }}

  // Red & White Striped Temple Compound Wall
  const wallGeo = new THREE.BoxGeometry(22, 2.8, 16);
  const wallMat = new THREE.MeshStandardMaterial({{color:0xb91c1c, roughness:0.8}});
  const wall = new THREE.Mesh(wallGeo, wallMat);
  wall.position.y = 1.4;
  tGroup.add(wall);

  bldGroup.add(tGroup);
}}

// 4. Historic Gothic Church (St. Peter's / St. Anthony's)
function createColonialChurch(pos){{
  const cGroup = new THREE.Group();
  cGroup.position.set(pos.x, 0, pos.z);

  // White Stone Nave
  const naveGeo = new THREE.BoxGeometry(16, 10, 24);
  const stoneMat = new THREE.MeshStandardMaterial({{color:0xf1f5f9, roughness:0.6}});
  const nave = new THREE.Mesh(naveGeo, stoneMat);
  nave.position.y = 5.0;
  cGroup.add(nave);

  // Twin Bell Spires
  [-6, 6].forEach(xOff => {{
    const spGeo = new THREE.BoxGeometry(4, 18, 4);
    const spire = new THREE.Mesh(spGeo, stoneMat);
    spire.position.set(xOff, 9, 10);
    cGroup.add(spire);

    const roofGeo = new THREE.ConeGeometry(2.5, 6, 4);
    const roofMat = new THREE.MeshStandardMaterial({{color:0x334155, roughness:0.3}});
    const roof = new THREE.Mesh(roofGeo, roofMat);
    roof.rotation.y = Math.PI/4;
    roof.position.set(xOff, 21, 10);
    cGroup.add(roof);

    // Cross
    const crossMat = new THREE.MeshBasicMaterial({{color:0xfacc15}});
    const c1 = new THREE.Mesh(new THREE.BoxGeometry(0.3, 2.2, 0.3), crossMat);
    c1.position.set(xOff, 25, 10);
    cGroup.add(c1);
    const c2 = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.3, 0.3), crossMat);
    c2.position.set(xOff, 25.5, 10);
    cGroup.add(c2);
  }});

  bldGroup.add(cGroup);
}}

// 5. Stanley Medical College & Hospital
function createHospitalCampus(pos){{
  const hGroup = new THREE.Group();
  hGroup.position.set(pos.x, 0, pos.z);

  // Multi-wing Hospital Complex
  const wingMat = new THREE.MeshStandardMaterial({{color:0xe2e8f0, roughness:0.6}});
  const mainWing = new THREE.Mesh(new THREE.BoxGeometry(26, 14, 14), wingMat);
  mainWing.position.y = 7;
  hGroup.add(mainWing);

  const eastWing = new THREE.Mesh(new THREE.BoxGeometry(12, 10, 20), wingMat);
  eastWing.position.set(15, 5, 2);
  hGroup.add(eastWing);

  // Red Cross Emergency Emblem
  const crossMat = new THREE.MeshBasicMaterial({{color:0xef4444}});
  const rc1 = new THREE.Mesh(new THREE.BoxGeometry(1.0, 3.6, 0.2), crossMat);
  rc1.position.set(0, 11, 7.2);
  hGroup.add(rc1);
  const rc2 = new THREE.Mesh(new THREE.BoxGeometry(3.6, 1.0, 0.2), crossMat);
  rc2.position.set(0, 11, 7.2);
  hGroup.add(rc2);

  bldGroup.add(hGroup);
}}

// 6. Generic Residential / Commercial Blocks
for(let i=0; i<160; i++){{
  const lat = 13.0945 + Math.random()*0.021;
  const lng = 80.2840 + Math.random()*0.015;
  const p = geo(lat, lng);
  const w = 2.5 + Math.random()*3.5;
  const d = 2.5 + Math.random()*3.5;
  const h = 3.0 + Math.random()*10.0;
  const geoBox = new THREE.BoxGeometry(w, h, d);
  const mat = new THREE.MeshStandardMaterial({{color: i%2===0?0x1e293b:0x0f172a, roughness:0.8}});
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
// 7. 10 FAMOUS SPOTS & BEACONS
// ==========================================
const pois = [
  {{id:'poi_station', name:'Royapuram Railway Station', lat:13.1065, lng:80.2920, icon:'🚂', color:0xf59e0b, h:18, defaultVeh:90, builder: createRailwayStation}},
  {{id:'poi_harbour', name:'Kasimedu Fishing Harbour', lat:13.1115, lng:80.2965, icon:'🐟', color:0x0284c7, h:14, defaultVeh:130, builder: createFishingHarbour}},
  {{id:'poi_metro', name:'Mannadi Metro Station', lat:13.0960, lng:80.2850, icon:'🚇', color:0x06b6d4, h:10, defaultVeh:150, builder: null}},
  {{id:'poi_stanley', name:'Stanley Medical College & Hospital', lat:13.0995, lng:80.2870, icon:'🏥', color:0x10b981, h:20, defaultVeh:100, builder: createHospitalCampus}},
  {{id:'poi_amman', name:'Arulmigu Angalaparameshwari Temple', lat:13.1055, lng:80.2910, icon:'🛕', color:0xeab308, h:17, defaultVeh:65, builder: p => createTempleGopuram(p, "Angalaparameshwari", 0xeab308)}},
  {{id:'poi_subramania', name:'Subramania Swamy Temple', lat:13.1038, lng:80.2925, icon:'🛕', color:0xfacc15, h:15, defaultVeh:50, builder: p => createTempleGopuram(p, "Subramania Swamy", 0xf59e0b)}},
  {{id:'poi_stpeters', name:'St. Peter’s Church', lat:13.1030, lng:80.2945, icon:'⛪', color:0x818cf8, h:19, defaultVeh:40, builder: createColonialChurch}},
  {{id:'poi_stanthony', name:'St. Anthony’s Church', lat:13.1028, lng:80.2940, icon:'⛪', color:0xa78bfa, h:16, defaultVeh:35, builder: createColonialChurch}},
  {{id:'poi_theagaraya', name:'Sir Theagaraya College', lat:13.1010, lng:80.2880, icon:'🎓', color:0x14b8a6, h:16, defaultVeh:45, builder: null}},
  {{id:'poi_fire_temple', name:'Parsi Fire Temple (Agiary)', lat:13.1045, lng:80.2935, icon:'🔥', color:0xf97316, h:14, defaultVeh:25, builder: null}}
];

const poiMeshes = [];
const destVehTargets = {{}};

pois.forEach(p => {{
  destVehTargets[p.id] = p.defaultVeh;
  const pos = geo(p.lat, p.lng);

  if(p.builder){{
    p.builder(pos);
  }}

  // Landmark Beacon Tower
  const towerGeo = new THREE.CylinderGeometry(0.6, 1.4, p.h, 16);
  const towerMat = new THREE.MeshStandardMaterial({{color:p.color, metalness:0.3, roughness:0.4, emissive:p.color, emissiveIntensity:0.35}});
  const tower = new THREE.Mesh(towerGeo, towerMat);
  tower.position.set(pos.x, p.h/2 + 2, pos.z);
  scene.add(tower);

  const crownGeo = new THREE.SphereGeometry(1.6, 16, 16);
  const crownMat = new THREE.MeshBasicMaterial({{color:p.color}});
  const crown = new THREE.Mesh(crownGeo, crownMat);
  crown.position.set(pos.x, p.h + 3, pos.z);
  scene.add(crown);

  const ringGeo = new THREE.RingGeometry(3, 4.5, 32);
  const ringMat = new THREE.MeshBasicMaterial({{color:p.color, transparent:true, opacity:0.35, side:THREE.DoubleSide}});
  const ring = new THREE.Mesh(ringGeo, ringMat);
  ring.rotation.x = -Math.PI/2;
  ring.position.set(pos.x, 0.38, pos.z);
  scene.add(ring);

  const labelSprite = makeLabel(`${{p.icon}} ${{p.name}}`, pos, p.h + 6, '#f8fafc');
  poiMeshes.push({{data:p, pos, ring, crown, labelSprite}});
}});

// Animated Southern Railway EMU Local Train on tracks behind Royapuram Station
const trainGroup = new THREE.Group();
const trainBodyMat = new THREE.MeshStandardMaterial({{color:0x1e3a8a, roughness:0.4}});
const trainStripeMat = new THREE.MeshBasicMaterial({{color:0x38bdf8}});
for(let c=0; c<3; c++){{
  const coach = new THREE.Mesh(new THREE.BoxGeometry(11, 2.8, 2.6), trainBodyMat);
  coach.position.set(c*12 - 12, 1.7, -9);
  trainGroup.add(coach);
  const stripe = new THREE.Mesh(new THREE.BoxGeometry(11, 0.4, 2.65), trainStripeMat);
  stripe.position.set(c*12 - 12, 2.1, -9);
  trainGroup.add(stripe);
}}
trainGroup.position.set(geo(13.1065, 80.2920).x, 0, geo(13.1065, 80.2920).z);
scene.add(trainGroup);

// ==========================================
// 8. WATERLOGGING WITH REAL MEASURING DEPTH GAUGES
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

  // Scaled Water Depth Gauge Pole (Real physical ruler pole with stripes)
  const poleGeo = new THREE.CylinderGeometry(0.2, 0.2, 7, 8);
  const poleMat = new THREE.MeshStandardMaterial({{color:0xfacc15, roughness:0.5}});
  const pole = new THREE.Mesh(poleGeo, poleMat);
  pole.position.set(pos.x, 3.5, pos.z);
  pole.visible = false;
  scene.add(pole);

  const labelSprite = makeLabel(`🌊 ${{s.name}}: DRY`, pos, 7, '#38bdf8');
  labelSprite.visible = false;

  waterlogMeshes.push({{ data: s, pos, puddle, ripple, pole, labelSprite }});
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
      wm.pole.visible = true;
      wm.labelSprite.visible = true;

      const severity = curDepth >= 45 ? '#ef4444' : curDepth >= 28 ? '#f59e0b' : '#38bdf8';
      updateLabelText(wm.labelSprite, `🌊 ${{wm.data.name}}: ${{curDepth}} cm Stagnant`, severity);
    }} else {{
      wm.puddle.material.opacity = 0.0;
      wm.ripple.material.opacity = 0.0;
      wm.pole.visible = false;
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
// 9. CHENNAI MULTI-MODAL 3D VEHICLES
// ==========================================
const vehConfigs = {{
  car: {{speed:32, enabled:true}},
  bike:{{speed:42, enabled:true}},
  auto:{{speed:24, enabled:true}},
  bus: {{speed:18, enabled:true}}
}};

let vehicles = [];
let simRunning = true, simSpeed = 1, timeOfDay = 8, rainOn = false, rainIntensity = 1;

// Detailed 3D Vehicle Builders
function buildDetailedVehicle(type){{
  const g = new THREE.Group();

  if(type === 'auto'){{
    // Iconic Chennai Auto (Yellow body, black canvas top, windscreen)
    const yMat = new THREE.MeshStandardMaterial({{color:0xfacc15, metalness:0.4, roughness:0.4}});
    const bMat = new THREE.MeshStandardMaterial({{color:0x0f172a, roughness:0.8}});
    const wMat = new THREE.MeshBasicMaterial({{color:0x38bdf8, transparent:true, opacity:0.6}});

    const base = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.6, 2.0), yMat);
    base.position.y = 0.45;
    g.add(base);

    const roof = new THREE.Mesh(new THREE.BoxGeometry(1.15, 0.7, 1.4), bMat);
    roof.position.set(0, 1.0, -0.2);
    g.add(roof);

    const windshield = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.6, 0.1), wMat);
    windshield.position.set(0, 0.9, 0.6);
    windshield.rotation.x = -0.3;
    g.add(windshield);
  }}
  else if(type === 'bus'){{
    // Chennai MTC Low-Floor City Bus (Red & Cream Livery)
    const redMat = new THREE.MeshStandardMaterial({{color:0xdc2626, metalness:0.3, roughness:0.4}});
    const creamMat = new THREE.MeshStandardMaterial({{color:0xfef3c7, roughness:0.5}});
    const glassMat = new THREE.MeshBasicMaterial({{color:0x38bdf8, transparent:true, opacity:0.5}});

    const lower = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.8, 5.2), redMat);
    lower.position.y = 0.6;
    g.add(lower);

    const upper = new THREE.Mesh(new THREE.BoxGeometry(1.95, 0.9, 5.1), creamMat);
    upper.position.y = 1.45;
    g.add(upper);

    // Glass Window Strips
    const glassL = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.6, 4.4), glassMat);
    glassL.position.set(-1.0, 1.3, 0);
    g.add(glassL);
    const glassR = glassL.clone();
    glassR.position.x = 1.0;
    g.add(glassR);

    // Destination LED Board (Yellow)
    const led = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.3, 0.1), new THREE.MeshBasicMaterial({{color:0xfacc15}}));
    led.position.set(0, 1.7, 2.6);
    g.add(led);
  }}
  else if(type === 'bike'){{
    // Two-Wheeler / Scooter with Rider
    const bikeMat = new THREE.MeshStandardMaterial({{color:0x22c55e, roughness:0.4}});
    const frame = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.6, 1.4), bikeMat);
    frame.position.y = 0.45;
    g.add(frame);

    // Rider Torso & Helmet
    const rider = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.6, 0.4), new THREE.MeshStandardMaterial({{color:0x1e293b}}));
    rider.position.set(0, 0.9, -0.1);
    g.add(rider);
    const helmet = new THREE.Mesh(new THREE.SphereGeometry(0.22, 8, 8), new THREE.MeshStandardMaterial({{color:0xef4444}}));
    helmet.position.set(0, 1.35, -0.1);
    g.add(helmet);
  }}
  else {{
    // Car / Sedan
    const carMat = new THREE.MeshStandardMaterial({{color:0x38bdf8, metalness:0.6, roughness:0.35}});
    const glassMat = new THREE.MeshBasicMaterial({{color:0x0f172a}});

    const base = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.6, 2.8), carMat);
    base.position.y = 0.45;
    g.add(base);

    const cabin = new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.55, 1.6), glassMat);
    cabin.position.set(0, 0.95, -0.1);
    g.add(cabin);
  }}

  // Headlights
  const hlMat = new THREE.MeshBasicMaterial({{color:0xfef08a}});
  const hl = new THREE.Mesh(new THREE.SphereGeometry(0.12, 6, 6), hlMat);
  hl.position.set(0.4, 0.45, 1.2);
  g.add(hl);
  const hl2 = hl.clone();
  hl2.position.x = -0.4;
  g.add(hl2);

  return g;
}}

function findNextRoad(currentRoadId, currentCoord, targetPos, isBus){{
  const candidates = [];
  roads.forEach(r => {{
    if(blockedRoads.has(r.id)) return;
    if(isBus && !r.busRoute) return;

    const wpts = roadWorldPts[r.id];
    for(let i=0; i<wpts.length; i++){{
      const pt = wpts[i];
      const dist = Math.hypot(pt.x - currentCoord.x, pt.z - currentCoord.z);
      if(dist < 18){{
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
  candidates.sort((a,b) => a.distToTarget - b.distToTarget);
  const choice = Math.random() < 0.75 ? candidates[0] : candidates[Math.floor(Math.random()*candidates.length)];
  return choice;
}}

function spawnVehicleForDestination(poiId){{
  const poi = pois.find(p => p.id === poiId);
  if(!poi) return null;
  const targetPos = geo(poi.lat, poi.lng);

  const types = ['car','bike','bike','auto','auto','car'];
  if(poi.id==='poi_station' || poi.id==='poi_metro' || poi.id==='poi_stanley') types.push('bus');
  const type = types[Math.floor(Math.random()*types.length)];
  const cfg = vehConfigs[type];
  if(!cfg.enabled) return null;

  const availableRoads = roads.filter(r => !blockedRoads.has(r.id) && (type!=='bus' || r.busRoute));
  if(!availableRoads.length) return null;
  const startRoad = availableRoads[Math.floor(Math.random()*availableRoads.length)];
  const wpts = roadWorldPts[startRoad.id];
  const fwd = Math.random() > 0.5;
  const coords = fwd ? [...wpts] : [...wpts].reverse();

  const mesh = buildDetailedVehicle(type);
  mesh.vehicleData = {{type, targetPOI: poi}};
  scene.add(mesh);

  return {{
    type,
    mesh,
    targetPOI: poi,
    targetPos,
    roadId: startRoad.id,
    coords,
    segIdx: 0,
    segProg: 0,
    speed: cfg.speed * (0.85 + Math.random()*0.35)
  }};
}}

// Vehicle Raycasting for Chase Cam
const vRaycaster = new THREE.Raycaster();
const vMouse = new THREE.Vector2();

renderer.domElement.addEventListener('click', e => {{
  if(blockMode) return;
  const rect = renderer.domElement.getBoundingClientRect();
  vMouse.x = ((e.clientX - rect.left)/rect.width)*2 - 1;
  vMouse.y = -((e.clientY - rect.top)/rect.height)*2 + 1;
  vRaycaster.setFromCamera(vMouse, camera);

  const vehicleMeshes = vehicles.map(v => v.mesh);
  const hits = vRaycaster.intersectObjects(vehicleMeshes, true);
  if(hits.length > 0){{
    let topGroup = hits[0].object;
    while(topGroup.parent && topGroup.parent !== scene){{
      topGroup = topGroup.parent;
    }}
    const match = vehicles.find(v => v.mesh === topGroup);
    if(match){{
      followVehicle(match);
    }}
  }}
}});

function rebalanceVehicles(){{
  let totalDesired = 0;
  pois.forEach(p => {{ totalDesired += destVehTargets[p.id] || 0; }});
  const targetFleet = Math.max(25, Math.min(180, Math.round(totalDesired / 4.0)));

  while(vehicles.length > targetFleet){{
    const v = vehicles.pop();
    if(v && v.mesh) scene.remove(v.mesh);
  }}

  while(vehicles.length < targetFleet){{
    let r = Math.random() * totalDesired;
    let chosenPOI = pois[0];
    for(const p of pois){{
      r -= (destVehTargets[p.id] || 0);
      if(r <= 0){{ chosenPOI = p; break; }}
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
      const lastCoord = v.coords[v.coords.length-1];
      const nextChoice = findNextRoad(v.roadId, lastCoord, v.targetPos, v.type==='bus');

      if(nextChoice){{
        v.roadId = nextChoice.road.id;
        const wpts = roadWorldPts[nextChoice.road.id];
        v.coords = nextChoice.forward ? [...wpts] : [...wpts].reverse();
        v.segIdx = 0;
        v.segProg = 0;
      }} else {{
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
  const particleCount = [0, 1500, 3800, 8500][rainIntensity];
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
        <input type="range" min="0" max="450" value="${{currentVal}}" id="slider-${{p.id}}" 
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
  stopFollow();
  if(p==='overview'){{ camTheta=Math.PI/4; camPhi=Math.PI/3.6; camDist=180; camTarget.set(0,0,0); }}
  else if(p==='station'){{
    const pos = geo(13.1065, 80.2920);
    camTheta=Math.PI/3; camPhi=Math.PI/2.7; camDist=45; camTarget.set(pos.x, 0, pos.z);
  }}
  else if(p==='harbour'){{
    const pos = geo(13.1115, 80.2965);
    camTheta=Math.PI/1.2; camPhi=Math.PI/2.8; camDist=55; camTarget.set(pos.x, 0, pos.z);
  }}
  else if(p==='temple'){{
    const pos = geo(13.1055, 80.2910);
    camTheta=Math.PI/2.2; camPhi=Math.PI/2.6; camDist=38; camTarget.set(pos.x, 0, pos.z);
  }}
  else if(p==='waterlog'){{
    const pos = geo(13.0995, 80.2872); // Stanley Subway
    camTheta=Math.PI/3.5; camPhi=Math.PI/2.6; camDist=45; camTarget.set(pos.x, 0, pos.z);
  }}
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

  let rhtml = '';
  roads.slice(0, 12).forEach(r => {{
    const extra = blockedRoads.size && !blockedRoads.has(r.id) ? Math.round(blockedRoads.size*7) : 0;
    const t = Math.min(100, r.traffic + extra + (rainOn ? rainIntensity*6 : 0));
    const cls = t<50 ? 'color:#10b981' : t<75 ? 'color:#f59e0b' : 'color:#ef4444';
    const blk = blockedRoads.has(r.id);
    rhtml += `
      <div style="display:flex;justify-content:space-between;padding:4px 8px;background:#0e172e;border-radius:4px;margin-bottom:3px;font-size:10.5px;${{blk?'opacity:0.4;text-decoration:line-through':''}}">
        <span style="color:#cbd5e1">${{r.name}}</span>
        <span class="road-tag" style="${{cls}}">${{blk ? 'BLOCKED' : t + '%'}}</span>
      </div>`;
  }});
  document.getElementById('road-list').innerHTML = rhtml;

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

    // Animate EMU train moving on tracks
    trainGroup.position.x = geo(13.1065, 80.2920).x + Math.sin(elapsedTime*0.4)*35;
  }}

  updateWaterlogVisuals(rainIntensity, rainOn);

  sea.position.y = 0.14 + Math.sin(elapsedTime*1.5)*0.08;

  poiMeshes.forEach((p, idx) => {{
    p.ring.scale.setScalar(1.0 + Math.sin(elapsedTime*2.5 + idx)*0.22);
    p.crown.position.y = p.data.h + 3 + Math.sin(elapsedTime*3.0 + idx)*0.35;
  }});

  renderer.render(scene, camera);
}}

window.addEventListener('resize', () => {{
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}});

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
    f.write(html_code)

print("Created ultra-realistic index.html! Bytes:", len(html_code))
