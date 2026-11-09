import { loadData, buildNetwork } from './network.js';
import { Forecaster, vcColor, vcLabel } from './forecast.js';
import { Sim, VEHICLE_TYPES } from './sim.js';
import { Weather, WATER_SPOTS, INTENSITY, CLOSE_CM } from './weather.js';
import { MapView, BASEMAPS } from './mapview.js';
import { lineChart, donut, gauge } from './charts.js';
import { shortest, tracePath } from './router.js';

const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fmt = n => Math.round(n).toLocaleString('en-IN');
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const store = {
  get(k, d) { try { return localStorage.getItem('areatwin.' + k) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem('areatwin.' + k, v); } catch { /* private mode */ } },
};
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const CLOCK_MIN_PER_SEC = 1;
const HISTORY = 180;

const S = {
  mode: 'class', autoSwitched: false,
  manual: new Set(), pickClose: false,
  clock: 8 * 60, autoClock: true, speed: 1, running: true,
  visitors: 1200, focusShare: 0.55,
  selected: null, fc: null,
  poiCat: 'all', poiQuery: '',
  hist: { speed: [], cong: [] },
  hl: { oneway: false, narrow: false, dead: false, low: false },
  tab: 'overview',
};

let net, sim, forecaster, weather, view;

// ======================================================================
// boot
// ======================================================================
boot().catch(err => {
  console.error(err);
  const box = $('loading');
  box.classList.add('error');
  $('loading-msg').textContent = location.protocol === 'file:'
    ? 'Open this page through a local web server (for example: python -m http.server 8000) - browsers block data files on file:// URLs.'
    : 'Could not start: ' + err.message;
});

async function boot() {
  if (!window.L) throw new Error('The map library (Leaflet) failed to load. Check your internet connection.');
  document.documentElement.dataset.theme = store.get('theme', 'dark');
  syncThemeIcon();

  const data = await loadData();
  $('loading-msg').textContent = 'Building the street graph…';
  await new Promise(r => setTimeout(r, 20));
  net = buildNetwork(data.roads, data.pois);
  sim = new Sim(net);

  $('loading-msg').textContent = 'Calibrating the traffic forecast…';
  await new Promise(r => setTimeout(r, 20));
  forecaster = new Forecaster(net);
  weather = new Weather(net, sim, () => applyClosures());

  view = new MapView($('map'), net, {
    initialBase: store.get('base', 'satellite'),
    onPick, onPoi: selectPoi, onGateway: pickGateway, onHover: hoverRoad,
    onTileError: () => toast('Map tiles are not loading. Check your connection, or try another base map.', 'warn', 5000),
  });
  view.map.fitBounds(net.bounds, { padding: [30, 30] });
  view.map.setZoom(Math.max(16, view.map.getZoom()));

  sim.focusPoi = net.pois.find(p => p.id === 'kovil_angala') || net.pois[0];
  sim.targetFleet = fleetTarget();
  sim.prefill(sim.targetFleet);
  for (let i = 0; i < 300; i++) sim.step(0.1);        // warm start: roads are populated on first paint

  for (let i = 0; i < 24; i++) { S.hist.speed.push(sim.stats.avgKmh); S.hist.cong.push(sim.stats.congestion * 100); }   // so the charts are not empty on first paint
  buildUi();
  syncBaseButtons();
  refreshRoadStyles();
  runForecast();
  updateKpis(); drawCharts();
  window.areatwin = { S, net, sim, view, weather, forecaster };       // handy in the dev console
  requestAnimationFrame(frame);
  $('loading').classList.add('done');
  setTimeout(() => $('loading').remove(), 600);
  if (innerWidth <= 900) $('sidebar').classList.add('collapsed');
}

// ======================================================================
// main loop
// ======================================================================
let lastT = performance.now(), acc250 = 0, acc1000 = 0;
function frame(now) {
  const dt = clamp((now - lastT) / 1000, 0, 0.1);
  lastT = now;
  if (S.running) {
    let rem = dt * S.speed;
    while (rem > 1e-6) { const h = Math.min(0.1, rem); sim.step(h); rem -= h; }
    if (S.autoClock) { S.clock = (S.clock + dt * S.speed * CLOCK_MIN_PER_SEC) % 1440; }
    weather.update(dt * S.speed * 0.5);
  }
  view.tick(dt);
  view.waterLevel = weather.level;
  view.centerOnFollow();
  view.redraw(sim);
  view.drawRain(dt, reduceMotion);

  acc250 += dt; acc1000 += dt;
  if (acc250 >= 0.25) { acc250 = 0; updateKpis(); updateInspectorLive(); updateClock(); }
  if (acc1000 >= 1) {
    acc1000 = 0;
    sim.targetFleet = fleetTarget();
    if (S.running) pushHistory();
    drawCharts();
    updateLiveLists();
    if (S.mode === 'traffic') refreshRoadStyles();
    view.setNight(nightFactor(S.clock / 60));
  }
  requestAnimationFrame(frame);
}

// ======================================================================
// demand and clock
// ======================================================================
function demandFactor(h) {
  const g = (x, m, s) => Math.exp(-(((x - m) / s) ** 2));
  return 0.35 + 0.9 * g(h, 9, 1.8) + 0.8 * g(h, 18, 1.9);
}
function fleetTarget() { return clamp(Math.round(S.visitors / 10 * demandFactor(S.clock / 60)), 40, 400); }
function nightFactor(h) {
  if (h < 5) return 1; if (h < 7) return 1 - (h - 5) / 2;
  if (h < 18.5) return 0; if (h < 20.5) return (h - 18.5) / 2; return 1;
}
function phaseName(h) {
  if (h >= 7 && h < 11) return 'Morning peak';
  if (h >= 16.5 && h < 20.5) return 'Evening peak';
  if (h < 5 || h >= 22) return 'Night';
  if (h < 7) return 'Early morning';
  if (h >= 20.5) return 'Late evening';
  return 'Daytime';
}
const hhmm = m => { const t = Math.floor(m) % 1440; return String(Math.floor(t / 60)).padStart(2, '0') + ':' + String(t % 60).padStart(2, '0'); };
function updateClock() {
  $('clock-time').textContent = hhmm(S.clock);
  $('clock-phase').textContent = phaseName(S.clock / 60) + (weather.on ? ' · ' + weather.label.toLowerCase() : '');
  $('lbl-time').textContent = hhmm(S.clock);
  if (S.autoClock) $('sl-time').value = Math.floor(S.clock / 5) * 5;
}

// ======================================================================
// toasts
// ======================================================================
function toast(msg, kind = '', ms = 3200) {
  const t = document.createElement('div');
  t.className = 'toast ' + kind; t.textContent = msg;
  $('toasts').appendChild(t);
  setTimeout(() => t.remove(), ms);
  while ($('toasts').children.length > 3) $('toasts').firstChild.remove();
}

// ======================================================================
// road styling
// ======================================================================
const CLASS_W = { primary: 4.6, trunk: 4.6, primary_link: 3.4, secondary: 4, tertiary: 3.2, residential: 2.2, living_street: 1.8 };
const MODES = [
  { id: 'class', name: 'Road class', sub: 'Hierarchy' },
  { id: 'traffic', name: 'Live traffic', sub: 'Simulated speed' },
  { id: 'forecast', name: 'Forecast load', sub: 'Volume / capacity' },
  { id: 'delta', name: 'Diversion', sub: 'Change vs normal' },
  { id: 'flood', name: 'Flooding', sub: 'Depth and risk' },
  { id: 'elevation', name: 'Elevation', sub: 'Terrain height' },
];
const isLightBase = () => BASEMAPS[view.baseKey].dark === false;
const dim = () => ({ color: isLightBase() ? '#94a3b8' : '#64748b', opacity: 0.45 });

function styleFor(r) {
  const i = r.roadIdx;
  const w = CLASS_W[r.t] || 2.2;
  const light = isLightBase();
  let s;
  switch (S.mode) {
    case 'traffic': {
      const ratio = sim.roadRatio(i), n = sim.roadCount(i);
      if (n === 0 && ratio > 0.97) s = { color: dim().color, weight: w * 0.85, opacity: dim().opacity };
      else s = { color: ratio > 0.8 ? '#22c55e' : ratio > 0.6 ? '#a3e635' : ratio > 0.4 ? '#facc15' : ratio > 0.2 ? '#f97316' : '#ef4444', weight: w + 0.8, opacity: 0.95 };
      break;
    }
    case 'forecast': {
      const res = S.fc ? S.fc.scen : forecaster.baseline;
      const vc = res.vc[i], flow = res.flowRoad[i];
      s = flow < 1 ? { color: dim().color, weight: w * 0.85, opacity: dim().opacity } : { color: vcColor(vc), weight: w + (vc >= 0.85 ? 1.6 : 0.6), opacity: 0.95 };
      break;
    }
    case 'delta': {
      const base = forecaster.baseline.flowRoad[i], scen = S.fc ? S.fc.scen.flowRoad[i] : base;
      const d = scen - base;
      if (Math.abs(d) < 4) s = { color: dim().color, weight: w * 0.85, opacity: dim().opacity };
      else if (d > 0) s = { color: d > 150 ? '#ef4444' : d > 60 ? '#f97316' : '#fbbf24', weight: w + 1.4, opacity: 0.95 };
      else s = { color: '#38bdf8', weight: w + 0.6, opacity: 0.85 };
      break;
    }
    case 'flood': {
      const depth = weather.level > 0.01 ? weather.roadDepth(r) : (r.low ? r.water_depth_cm : 0);
      s = depth <= 0 ? { color: dim().color, weight: w * 0.8, opacity: dim().opacity * 0.8 }
        : { color: `hsl(${Math.round(200 + clamp(depth / 60, 0, 1) * 30)} ${90}% ${Math.round(70 - clamp(depth / 60, 0, 1) * 30)}%)`, weight: w + 1 + depth / 30, opacity: weather.level > 0.01 ? 1 : 0.7 };
      break;
    }
    case 'elevation': {
      const t = clamp((r.el - 3.7) / (5.3 - 3.7), 0, 1);
      s = { color: `hsl(${Math.round(205 - t * 165)} 85% ${light ? 45 : 58}%)`, weight: w + 0.6, opacity: 0.92 };
      break;
    }
    default: {
      const major = r.t === 'primary' || r.t === 'trunk' || r.t === 'secondary' || r.t === 'primary_link';
      if (major) s = { color: light ? '#d97706' : '#fbbf24', weight: w, opacity: 0.95 };
      else if (r.t === 'tertiary') s = { color: light ? '#0284c7' : '#38bdf8', weight: w, opacity: 0.9 };
      else if (r.t === 'residential') s = { color: light ? '#475569' : '#e2e8f0', weight: w, opacity: light ? 0.7 : 0.6 };
      else s = { color: light ? '#64748b' : '#cbd5e1', weight: w, opacity: light ? 0.6 : 0.45 };
    }
  }
  // constraint highlights
  if (S.hl.oneway && r.ow) s = { color: '#fb923c', weight: Math.max(s.weight, 3.6), opacity: 1 };
  if (S.hl.narrow && r.sm) s = { color: '#c084fc', weight: Math.max(s.weight, 3), opacity: 1 };
  if (S.hl.dead && r.de) s = { color: '#f43f5e', weight: Math.max(s.weight, 3.4), opacity: 1 };
  if (S.hl.low && r.low) s = { color: '#0ea5e9', weight: Math.max(s.weight, 3.4), opacity: 1 };
  const kind = closedKind(i);
  if (kind) s = { color: kind === 'flood' ? '#0ea5e9' : '#ef4444', weight: Math.max(s.weight + 2, 5), opacity: 1 };
  return s;
}

function closedKind(i) { return S.manual.has(i) ? 'manual' : weather.floodClosed.has(i) ? 'flood' : null; }

function refreshRoadStyles() { view.restyle(styleFor); renderLegend(); }

function renderLegend() {
  const items = (arr) => `<div class="items">${arr.map(([c, l]) => `<span class="it"><i class="sw" style="background:${c}"></i>${l}</span>`).join('')}</div>`;
  const ramp = (grad, a, b) => `<div class="ramp" style="background:${grad}"></div><div class="ramp-l"><span>${a}</span><span>${b}</span></div>`;
  const light = isLightBase();
  let title = '', body = '';
  switch (S.mode) {
    case 'traffic': title = 'Live speed vs free flow'; body = items([['#22c55e', 'Flowing'], ['#a3e635', 'Slowing'], ['#facc15', 'Heavy'], ['#f97316', 'Crawling'], ['#ef4444', 'Stopped']]); break;
    case 'forecast': title = S.fc ? 'Forecast volume / capacity' : 'Normal-day volume / capacity'; body = items([['#22c55e', '&lt; 0.4'], ['#84cc16', '0.4 - 0.65'], ['#eab308', '0.65 - 0.85'], ['#f97316', '0.85 - 1.1'], ['#ef4444', '&ge; 1.1']]); break;
    case 'delta': title = 'Traffic change after closures'; body = items([['#ef4444', '+150 veh/h'], ['#f97316', '+60'], ['#fbbf24', '+4'], ['#38bdf8', 'Relieved']]); break;
    case 'flood': title = weather.level > 0.01 ? 'Flood depth now' : 'Flood risk (surveyed depth)'; body = ramp('linear-gradient(90deg,hsl(200 90% 70%),hsl(230 90% 40%))', '0 cm', '60+ cm'); break;
    case 'elevation': title = 'Street elevation'; body = ramp('linear-gradient(90deg,hsl(205 85% 58%),hsl(122 85% 58%),hsl(40 85% 58%))', '3.7 m', '5.3 m'); break;
    default: title = 'Road class'; body = items([[light ? '#d97706' : '#fbbf24', 'Arterial'], [light ? '#0284c7' : '#38bdf8', 'Collector'], [light ? '#475569' : '#e2e8f0', 'Local'], ['#ef4444', 'Closed']]);
  }
  $('legend').innerHTML = `<h4>${title}</h4>${body}`;
}

// ======================================================================
// closures and forecast
// ======================================================================
function effectiveClosed() { return new Set([...S.manual, ...weather.floodClosed]); }

function applyClosures() {
  const eff = effectiveClosed();
  sim.setClosed(eff);
  const info = new Map();
  for (const i of weather.floodClosed) info.set(i, 'flood');
  for (const i of S.manual) info.set(i, 'manual');
  view.closedInfo = info;
  refreshRoadStyles();
  renderClosedList();
  clearTimeout(applyClosures.t);
  applyClosures.t = setTimeout(runForecast, 140);
}

function runForecast() {
  const eff = effectiveClosed();
  if (eff.size) {
    const t0 = performance.now();
    const scen = forecaster.run(eff);
    S.fc = { scen, cmp: forecaster.compare(scen), ms: performance.now() - t0 };
    if (S.mode === 'class' && !S.autoSwitched) { setMode('forecast'); S.autoSwitched = true; }
  } else {
    S.fc = null;
    if (S.autoSwitched && S.mode === 'forecast') setMode('class');
    S.autoSwitched = false;
  }
  renderForecast();
  const b = $('badge-forecast');
  b.textContent = streetCount(eff); b.classList.toggle('hidden', !eff.size);
  refreshRoadStyles();
}

const piecesOf = i => net.bySrc.get(net.roads[i].src);
const streetCount = set => new Set([...set].map(i => net.roads[i].src)).size;

// closing acts on the whole street (every junction-split piece of it)
function toggleClose(i) {
  const pieces = piecesOf(i);
  const closing = !pieces.every(p => S.manual.has(p));
  for (const p of pieces) closing ? S.manual.add(p) : S.manual.delete(p);
  toast(closing ? `Closed ${net.roads[i].n || 'street'}. Traffic is re-routing.` : `Reopened ${net.roads[i].n || 'street'}`, closing ? 'warn' : 'good');
  applyClosures();
  if (S.selected && S.selected.type === 'road') renderInspector();
}

function renderClosedList() {
  const el = $('closed-list');
  const rows = [], seen = new Set();
  for (const i of S.manual) { const s = net.roads[i].src; if (!seen.has(s)) { seen.add(s); rows.push(closedRow(i, 'manual')); } }
  for (const i of weather.floodClosed) { const s = net.roads[i].src; if (!S.manual.has(i) && !seen.has(s)) { seen.add(s); rows.push(closedRow(i, 'flood')); } }
  el.innerHTML = rows.slice(0, 12).join('') + (rows.length > 12 ? `<p class="hint">+ ${rows.length - 12} more flooded streets</p>` : '');
}
function closedRow(i, kind) {
  const r = net.roads[i];
  return `<div class="closed-item"><span class="tag ${kind === 'flood' ? 't-lo' : 't-cl'}">${kind === 'flood' ? 'Flooded' : 'Closed'}</span><b data-zoom-road="${i}" title="Zoom to street">${esc(r.n || 'Unnamed street')}</b>${kind === 'manual' ? `<button class="btn small" data-reopen="${i}">Reopen</button>` : ''}</div>`;
}

function renderForecast() {
  const out = $('forecast-out');
  if (!S.fc) {
    out.innerHTML = `<div class="card"><div class="empty"><svg class="ic"><use href="#i-forecast"/></svg><p><b>No closures yet.</b><br>Close a corridor above, or click any street on the map and choose <em>Close street</em>. The forecast appears here.</p></div></div>`;
    return;
  }
  const { cmp, scen } = S.fc;
  const sev = cmp.counts.severe + cmp.counts.heavy, sevB = cmp.bcounts.severe + cmp.bcounts.heavy;
  const rowsHtml = cmp.top.length ? cmp.top.map(t => `
    <div class="choke" data-zoom-road="${t.i}" tabindex="0" role="button" style="border-left-color:${vcColor(t.vcScen)}">
      <div class="nm">${esc(t.name)}<small>${vcLabel(t.vcScen)} · capacity ${fmt(t.cap)} veh/h · ${t.surge >= 100 && t.vcBase < 0.05 ? 'newly used' : '+' + Math.round(t.surge) + '% traffic'}</small></div>
      <div class="vc" style="color:${vcColor(t.vcScen)}">${t.vcScen.toFixed(2)}<small>from ${t.vcBase.toFixed(2)}</small></div>
    </div>`).join('') : '<p class="hint">No street is pushed past 0.65 V/C. The network absorbs this closure.</p>';

  const band = (label, color, b, s) => {
    const max = Math.max(1, b, s, 8);
    return `<div class="bar-row"><div class="bl"><span>${label}</span><span class="muted">${b} → <b style="color:var(--text)">${s}</b> streets</span></div>
      <div class="bar" style="margin-bottom:3px"><i style="width:${b / max * 100}%;background:var(--muted);opacity:.55"></i></div>
      <div class="bar"><i style="width:${s / max * 100}%;background:${color}"></i></div></div>`;
  };

  out.innerHTML = `
    <div class="grid2">
      <div class="stat"><b style="color:var(--warn)">${fmt(cmp.displaced)}<small class="muted"> veh/h</small></b><span>Traffic displaced</span></div>
      <div class="stat"><b style="color:${sev > sevB ? 'var(--bad)' : 'var(--good)'}">${sev}<small class="muted"> / ${sevB} normal</small></b><span>Streets ≥ 0.85 V/C</span></div>
      <div class="stat"><b>+${cmp.detourSec < 10 ? cmp.detourSec.toFixed(1) : fmt(cmp.detourSec)}<small class="muted"> s</small></b><span>Delay per diverted vehicle</span></div>
      <div class="stat"><b>${fmt(cmp.queue10)}<small class="muted"> m</small></b><span>Tailback after 10 min</span></div>
    </div>
    ${cmp.unservedPct > 0.05 ? `<div class="card" style="border-color:var(--bad)"><h2 style="color:var(--bad)">Trips cut off</h2><p style="font-size:12px">${cmp.unservedPct.toFixed(1)}% of visitor trips have no drivable route under the current closures.</p></div>` : ''}
    <div class="card">
      <h2>Streets under pressure</h2>
      ${rowsHtml}
    </div>
    <div class="card">
      <h2>Load distribution</h2>
      <div class="compare"><span><i style="background:var(--muted);opacity:.55"></i>Normal day</span><span><i style="background:var(--accent)"></i>With closures</span></div>
      ${band('Severe · ≥ 1.10', '#ef4444', cmp.bcounts.severe, cmp.counts.severe)}
      ${band('Heavy · ≥ 0.85', '#f97316', cmp.bcounts.heavy, cmp.counts.heavy)}
      ${band('Moderate · ≥ 0.65', '#eab308', cmp.bcounts.moderate, cmp.counts.moderate)}
    </div>
    <div class="card">
      <h2>Suggested response</h2>
      <ul class="tips">${mitigation(cmp, scen).map(t => `<li>${t}</li>`).join('')}</ul>
      <p class="hint">Computed in ${Math.round(S.fc.ms)} ms. V/C = modelled volume ÷ capacity per direction.</p>
    </div>`;
}

function mitigation(cmp, scen) {
  const tips = [];
  const top = cmp.top[0];
  const closedNames = [...new Set([...scen.closed].map(i => net.roads[i].n))];
  if (top) tips.push(`Post traffic wardens at <b>${esc(top.name)}</b>, the first street to choke (V/C ${top.vcScen.toFixed(2)}).`);
  let best = null;
  for (const r of net.roads) {
    if (r.cap < 950 || scen.closed.has(r.roadIdx) || r.ow && false) continue;
    const spare = (1 - scen.vc[r.roadIdx]) * (r.ow ? r.cap : r.cap / 2);
    if (scen.flowRoad[r.roadIdx] < 20) continue;
    if (!best || spare > best.spare) best = { r, spare };
  }
  if (best && best.spare > 100) tips.push(`Signpost <b>${esc(best.r.n)}</b> as the bypass: it still has about ${fmt(best.spare)} veh/h of spare capacity.`);
  const narrow = cmp.top.find(t => net.roads[t.i].sm);
  if (narrow) tips.push(`<b>${esc(narrow.name)}</b> is a narrow street absorbing diverted traffic. Consider a turn ban or barrier at its entry.`);
  if (streetCount(scen.closed) > 1) tips.push(`${streetCount(scen.closed)} streets are closed together. Phasing the work (one corridor at a time) would cut the peak load.`);
  else if (cmp.displaced > 500) tips.push(`Schedule work on <b>${esc(closedNames[0])}</b> outside the 08-10 and 17-19 peaks to avoid the worst of the ${fmt(cmp.displaced)} veh/h diversion.`);
  if (!tips.length) tips.push('The network has enough alternative routes. No intervention needed.');
  return tips;
}

// ======================================================================
// selection and inspector
// ======================================================================
function onPick(latlng, roadIdx) {
  if (S.pickClose) { if (roadIdx != null) toggleClose(roadIdx); return; }
  const v = view.nearestVehicle(sim, latlng, 14);
  if (v) return selectVehicle(v);
  if (roadIdx != null) return selectRoad(roadIdx);
  clearSelection();
}

function clearSelection() {
  S.selected = null; view.select(null); view.selectedVeh = null; view.follow(null); view.highlightPoi(null);
  $('inspector').classList.add('hidden');
}

function selectRoad(i) {
  S.selected = { type: 'road', idx: i };
  view.selectedVeh = null; view.follow(null); view.highlightPoi(null);
  view.select(i);
  renderInspector();
}

function selectVehicle(v) {
  S.selected = { type: 'vehicle', v };
  view.select(null); view.selectedVeh = v; view.highlightPoi(null);
  renderInspector();
}

function selectPoi(p) {
  S.selected = { type: 'poi', p };
  view.select(null); view.selectedVeh = null; view.follow(null);
  view.highlightPoi(p.id);
  view.map.panTo([p.lat, p.lng]);
  renderInspector();
}

function pickGateway(g) {
  $('sel-gw').value = g.key; setGateway(g.key);
  toast(`Entry gateway: ${g.name}`);
}

function bar(label, valueText, frac, color) {
  return `<div class="bar-row"><div class="bl"><span>${label}</span><b>${valueText}</b></div><div class="bar"><i style="width:${clamp(frac, 0, 1) * 100}%;background:${color}"></i></div></div>`;
}

function renderInspector() {
  const el = $('inspector');
  const sel = S.selected;
  if (!sel) return el.classList.add('hidden');
  el.classList.remove('hidden');
  const close = `<button class="icon-btn" data-action="clear" aria-label="Close panel"><svg class="ic"><use href="#i-x"/></svg></button>`;

  if (sel.type === 'road') {
    const r = net.roads[sel.idx], i = sel.idx;
    const kind = closedKind(i);
    const base = forecaster.baseline.vc[i];
    const fcvc = S.fc ? S.fc.scen.vc[i] : null;
    const tags = [r.ow ? '<span class="tag t-ow">One-way</span>' : '', r.sm ? '<span class="tag t-nr">Narrow</span>' : '', r.de ? '<span class="tag t-de">Dead end</span>' : '',
      r.low ? '<span class="tag t-lo">Low-lying</span>' : '', r.b ? '<span class="tag">Bus route</span>' : '', kind ? `<span class="tag t-cl">${kind === 'flood' ? 'Flooded' : 'Closed'}</span>` : ''].join('');
    el.innerHTML = `
      <div class="ihead"><div><h3>${esc(r.n || 'Unnamed street')}</h3><div class="isub">${esc(r.t.replace('_', ' '))} · street #${i}</div></div>${close}</div>
      <div class="facts">
        <div class="fact"><b>${r.w} m</b><span>Width</span></div>
        <div class="fact"><b>${fmt(r.L)} m</b><span>Length</span></div>
        <div class="fact"><b>${fmt(r.cap)}</b><span>Veh / h</span></div>
      </div>
      <div class="tags">${tags}</div>
      <div id="ins-live"></div>
      ${bar('Normal-day load (V/C)', base.toFixed(2), base / 1.3, vcColor(base))}
      ${fcvc != null ? bar('Forecast with closures', fcvc.toFixed(2), fcvc / 1.3, vcColor(fcvc)) : ''}
      ${r.low ? `<p class="desc" style="margin-top:8px">Elevation ${r.el} m · ${esc(r.basin || 'low basin')} · ${r.water_depth_cm} cm surveyed stagnation depth.</p>` : `<p class="desc" style="margin-top:8px">Elevation ${r.el} m.</p>`}
      <div class="actions">
        <button class="btn ${S.manual.has(i) ? 'good' : 'danger'}" data-action="toggle-close">${S.manual.has(i) ? 'Reopen street' : 'Close street'}</button>
        <button class="btn" data-action="zoom-road">Zoom to</button>
      </div>`;
    updateInspectorLive();
  } else if (sel.type === 'vehicle') {
    const v = sel.v, P = v.P;
    el.innerHTML = `
      <div class="ihead"><div><h3>${P.icon} ${P.label} · ${v.id}</h3><div class="isub">Heading to ${esc(v.poi.name)}</div></div>${close}</div>
      <canvas id="iv-gauge"></canvas>
      <div class="facts" style="margin-top:6px">
        <div class="fact"><b id="iv-gap">-</b><span>Gap ahead</span></div>
        <div class="fact"><b id="iv-state">-</b><span>State</span></div>
        <div class="fact"><b id="iv-left">-</b><span>To go</span></div>
      </div>
      <p class="desc" id="iv-road"></p>
      <div class="actions">
        <button class="btn ${view.followVeh === v ? 'primary' : ''}" data-action="follow">${view.followVeh === v ? 'Following' : 'Follow'}</button>
        <button class="btn" data-action="show-route">Show route</button>
      </div>`;
    updateInspectorLive();
  } else if (sel.type === 'poi') {
    const p = sel.p;
    el.innerHTML = `
      <div class="ihead"><div><h3>${p.icon} ${esc(p.name)}</h3><div class="isub">${esc(p.category)} · near ${esc(p.road ? p.road.n : '')}</div></div>${close}</div>
      <p class="desc">${esc(p.desc)}</p>
      <div class="facts" style="grid-template-columns:repeat(2,1fr)">
        <div class="fact"><b>${fmt(p.defaultVisitors)}</b><span>Typical visitors / h</span></div>
        <div class="fact"><b>${p.edges.length}</b><span>Access edges</span></div>
      </div>
      <div class="actions"><button class="btn primary" data-action="send-visitors">Send visitors here</button><button class="btn" data-action="zoom-poi">Zoom to</button></div>`;
  }
}

function updateInspectorLive() {
  const sel = S.selected;
  if (!sel) return;
  if (sel.type === 'road') {
    const live = $('ins-live'); if (!live) return;
    const i = sel.idx, n = sim.roadCount(i), ratio = sim.roadRatio(i);
    const depth = weather.roadDepth(net.roads[i]);
    live.innerHTML = bar(`Live speed · ${n} vehicle${n === 1 ? '' : 's'} now`, n || ratio < 0.97 ? Math.round(ratio * 100) + '% of free flow' : 'empty', n || ratio < 0.97 ? ratio : 1, ratio > 0.7 ? '#22c55e' : ratio > 0.4 ? '#facc15' : '#ef4444')
      + (depth > 0 ? bar('Water depth now', depth + ' cm', depth / 60, '#38bdf8') : '');
  } else if (sel.type === 'vehicle') {
    const v = sel.v;
    if (v.dead || !sim.vehicles.includes(v)) {
      toast(`${v.id} reached its destination`, 'good', 1800); clearSelection(); return;
    }
    const kmh = v.v * 3.6;
    const col = kmh > 30 ? '#34d399' : kmh > 12 ? '#fbbf24' : '#f87171';
    const cv = $('iv-gauge'); if (cv) gauge(cv, kmh, 60, col, 'km/h');
    $('iv-gap').textContent = v.gap < 400 ? v.gap.toFixed(1) + ' m' : 'clear';
    $('iv-state').textContent = kmh < 1 ? 'Stopped' : v.braking ? 'Braking' : 'Cruising';
    let left = -v.s; for (let k = v.ri; k < v.route.length; k++) left += net.edgeLen[v.route[k]];
    $('iv-left').textContent = left > 950 ? (left / 1000).toFixed(1) + ' km' : Math.max(0, Math.round(left)) + ' m';
    $('iv-road').innerHTML = `On <b>${esc(net.roads[v.e >> 1].n || 'unnamed street')}</b> · limit ${Math.round(Math.min(v.p.v0, sim.edgeV0(v.e)) * 3.6)} km/h`;
  }
}

$('inspector').addEventListener('click', e => {
  const b = e.target.closest('[data-action]'); if (!b) return;
  const sel = S.selected; if (!sel) return;
  switch (b.dataset.action) {
    case 'clear': clearSelection(); break;
    case 'toggle-close': toggleClose(sel.idx); break;
    case 'zoom-road': zoomRoad(sel.idx); break;
    case 'follow': view.follow(view.followVeh === sel.v ? null : sel.v); view.map.setZoom(Math.max(view.map.getZoom(), 17.5)); renderInspector(); break;
    case 'show-route': view.showRoute(sel.v.route.slice(sel.v.ri)); toast('Route shown for ' + sel.v.id); break;
    case 'send-visitors': $('sel-poi').value = sel.p.id; setTab('flow'); dispatch(); break;
    case 'zoom-poi': view.map.setView([sel.p.lat, sel.p.lng], 18); break;
  }
});

function zoomStreet(i) {
  const b = L.latLngBounds(piecesOf(i).flatMap(p => net.roads[p].p));
  view.map.fitBounds(b, { maxZoom: 18, padding: [120, 120] });
}
function zoomRoad(i) {
  const b = L.latLngBounds(net.roads[i].p);
  view.map.fitBounds(b, { maxZoom: 18, padding: [120, 120] });
}

// hover tooltip
const tip = document.createElement('div');
tip.className = 'leaflet-tooltip road-tip'; tip.style.cssText = 'position:absolute;z-index:900;pointer-events:none;display:none';
$('stage').appendChild(tip);
function hoverRoad(i, ev) {
  if (i == null || !ev) { tip.style.display = 'none'; return; }
  const r = net.roads[i];
  const rect = $('stage').getBoundingClientRect();
  tip.innerHTML = `<b>${esc(r.n || 'Unnamed street')}</b> <span class="muted">${r.t.replace('_', ' ')}${r.ow ? ' · one-way' : ''}</span>`;
  tip.style.display = 'block';
  tip.style.left = ev.clientX - rect.left + 14 + 'px'; tip.style.top = ev.clientY - rect.top + 12 + 'px';
}

// ======================================================================
// KPIs and charts
// ======================================================================
function updateKpis() {
  const st = sim.stats;
  $('k-veh').textContent = sim.vehicles.length;
  $('k-veh-sub').textContent = `target ${sim.targetFleet}`;
  $('k-speed').innerHTML = `${Math.round(st.avgKmh)}<small> km/h</small>`;
  $('k-speed-sub').textContent = `top ${Math.round(st.topKmh)} km/h`;
  $('k-queue').textContent = st.queued;
  const cong = Math.round(st.congestion * 100);
  $('k-cong').innerHTML = `${cong}<small>%</small>`;
  const cb = $('k-cong-bar'); cb.style.width = clamp(cong * 2, 2, 100) + '%';
  cb.style.background = cong > 40 ? 'var(--bad)' : cong > 20 ? 'var(--warn)' : 'var(--good)';
  $('k-thru').innerHTML = `${fmt(st.throughput)}<small> /h</small>`;
  $('k-thru-sub').textContent = `${fmt(sim.arrivedTotal)} arrived`;
  const nClosed = streetCount(effectiveClosed());
  $('k-closed').textContent = nClosed;
  $('k-closed-sub').textContent = nClosed ? `${streetCount(S.manual)} manual · ${streetCount(weather.floodClosed)} flood` : 'all streets open';
  $('kpi-closed').classList.toggle('alert', nClosed > 0);
  $('k-water').innerHTML = `${weather.maxDepth}<small> cm</small>`;
  $('k-water-sub').textContent = weather.on ? weather.label : weather.level > 0.02 ? 'Draining' : 'Dry';
  $('kpi-water').classList.toggle('alert', weather.maxDepth >= CLOSE_CM);
}

function pushHistory() {
  const st = sim.stats;
  S.hist.speed.push(st.avgKmh); S.hist.cong.push(st.congestion * 100);
  if (S.hist.speed.length > HISTORY) { S.hist.speed.shift(); S.hist.cong.shift(); }
}

function drawCharts() {
  if (S.tab === 'overview') {
    lineChart($('ch-speed'), [{ data: S.hist.speed, color: '#38bdf8', fill: true }], { min: 0, max: 60, points: HISTORY, xLabel: ['−3 min', 'now'] });
    lineChart($('ch-cong'), [{ data: S.hist.cong, color: '#f97316', fill: true }], { min: 0, max: 100, points: HISTORY, xLabel: ['−3 min', 'now'] });
    const st = sim.stats;
    $('ch-speed-now').textContent = `${Math.round(st.avgKmh)} km/h`;
    $('ch-cong-now').textContent = `${Math.round(st.congestion * 100)} %`;
    const counts = {}; for (const k in VEHICLE_TYPES) counts[k] = 0;
    for (const v of sim.vehicles) counts[v.type]++;
    donut($('ch-mix'), Object.keys(VEHICLE_TYPES).map(k => ({ value: counts[k], color: VEHICLE_TYPES[k].color })), { center: sim.vehicles.length, sub: 'vehicles' });
  } else if (S.tab === 'flow') {
    const pts = [];
    for (let m = 0; m <= 1440; m += 15) pts.push(clamp(Math.round(S.visitors / 10 * demandFactor(m / 60)), 40, 400));
    lineChart($('ch-demand'), [{ data: pts, color: '#a78bfa', fill: true }], { min: 0, points: pts.length, xLabel: ['00:00', '24:00'], marker: S.clock / 1440 });
  } else if (S.tab === 'weather') {
    gauge($('ch-water'), weather.maxDepth, 80, weather.maxDepth >= CLOSE_CM ? '#f87171' : weather.maxDepth >= 25 ? '#fbbf24' : '#38bdf8', 'cm deepest');
  }
}

function updateLiveLists() {
  const counts = {}; for (const k in VEHICLE_TYPES) counts[k] = 0;
  for (const v of sim.vehicles) counts[v.type]++;
  for (const k in counts) { const n = document.querySelector(`[data-count="${k}"]`); if (n) n.textContent = counts[k]; }
  if (S.tab === 'weather') {
    for (const s of WATER_SPOTS) {
      const d = weather.spotDepth(s);
      const el = document.querySelector(`[data-spot="${s.id}"]`); if (!el) continue;
      el.querySelector('.depth').textContent = d + ' cm';
      el.querySelector('.bar i').style.width = clamp(d / 80, 0, 1) * 100 + '%';
    }
    $('lbl-rain').textContent = INTENSITY[+$('sl-rain').value].label;
  }
}

// ======================================================================
// UI construction and events
// ======================================================================
function setTab(id) {
  S.tab = id;
  document.querySelectorAll('.tabs [role=tab]').forEach(t => t.setAttribute('aria-selected', String(t.dataset.tab === id)));
  document.querySelectorAll('.panel').forEach(p => { p.hidden = p.id !== 'p-' + id; });
  $('sidebar').classList.remove('collapsed');
  drawCharts(); updateLiveLists();
}

function setMode(id) {
  S.mode = id;
  document.querySelectorAll('.mode').forEach(b => b.setAttribute('aria-checked', String(b.dataset.mode === id)));
  refreshRoadStyles();
}

function setGateway(key) {
  sim.focusGateway = key;
  document.querySelectorAll('.gw-pin').forEach(n => n.classList.toggle('active', n.dataset.key === key));
}

function setSpeed(n) {
  S.speed = n;
  document.querySelectorAll('#speed-seg button').forEach(b => { const on = +b.dataset.speed === n; b.classList.toggle('on', on); b.setAttribute('aria-pressed', String(on)); });
}

function setRunning(r) {
  S.running = r;
  $('btn-play').innerHTML = `<svg class="ic"><use href="#i-${r ? 'pause' : 'play'}"/></svg>`;
  $('btn-play').setAttribute('aria-label', r ? 'Pause simulation' : 'Resume simulation');
}

function setPick(on) {
  S.pickClose = on;
  $('map').classList.toggle('picking', on);
  $('btn-pick').classList.toggle('on', on);
  if (on) toast('Click streets to close or reopen them. Press Esc when finished.', '', 4200);
}

function syncThemeIcon() {
  const dark = document.documentElement.dataset.theme !== 'light';
  const b = $('btn-theme'); if (b) b.innerHTML = `<svg class="ic"><use href="#i-${dark ? 'sun' : 'moon'}"/></svg>`;
}
function syncBaseButtons() {
  document.querySelectorAll('#base-seg button').forEach(b => { const on = b.dataset.base === view.baseKey; b.classList.toggle('on', on); b.setAttribute('aria-pressed', String(on)); });
}

function buildUi() {
  // ----- map style modes
  $('mode-grid').innerHTML = MODES.map(m => `<button class="mode" role="radio" aria-checked="${m.id === S.mode}" data-mode="${m.id}">${m.name}<small>${m.sub}</small></button>`).join('');
  $('mode-grid').addEventListener('click', e => { const b = e.target.closest('.mode'); if (b) { S.autoSwitched = false; setMode(b.dataset.mode); } });

  // ----- fleet
  $('fleet-list').innerHTML = Object.entries(VEHICLE_TYPES).map(([k, t]) =>
    `<label class="fl"><input type="checkbox" data-veh="${k}" checked><i class="sw" style="background:${t.color}"></i>${t.icon} ${t.label}<span class="n" data-count="${k}">0</span></label>`).join('');
  $('fleet-list').addEventListener('change', e => { const k = e.target.dataset.veh; if (k) { sim.enabled[k] = e.target.checked; if (!e.target.checked) { sim.vehicles = sim.vehicles.filter(v => v.type !== k); } } });

  // ----- toggles
  $('tg-speedcolor').onchange = e => { view.colorBySpeed = e.target.checked; };
  $('tg-roads').onchange = e => view.setRoadsVisible(e.target.checked);
  $('tg-vehicles').onchange = e => { view.showVehicles = e.target.checked; };
  $('tg-places').onchange = e => view.setPoiVisible(e.target.checked);
  $('tg-gateways').onchange = e => view.setGatewaysVisible(e.target.checked);
  $('tg-anticol').onchange = e => { sim.antiCollision = e.target.checked; toast(e.target.checked ? 'Car-following on' : 'Car-following off: vehicles will overlap', e.target.checked ? 'good' : 'warn'); };

  // ----- closure forecast
  const flows = forecaster.baseline.flowRoad;
  const cands = [...net.bySrc.values()].map(ps => ({
    roadIdx: ps[0], r: net.roads[ps[0]], L: ps.reduce((a, p) => a + net.roads[p].L, 0),
    flow: Math.max(...ps.map(p => flows[p])), circ: ps.some(p => net.main[2 * p] || net.main[2 * p + 1]),
  })).filter(g => g.r.cap >= 950 && g.circ).sort((a, b) => b.flow - a.flow).slice(0, 60);
  $('sel-close').innerHTML = `<option value="">Choose a street…</option>` + cands.map(g => `<option value="${g.roadIdx}">${esc(g.r.n || 'Unnamed')} · ${fmt(g.L)} m · ${fmt(g.flow)} veh/h</option>`).join('');
  $('btn-close-sel').onclick = () => { const v = $('sel-close').value; if (!v) return toast('Choose a street first.'); const i = +v; if (!S.manual.has(i)) toggleClose(i); zoomStreet(i); };
  $('btn-busiest').onclick = () => { const i = cands.find(r => !S.manual.has(r.roadIdx)).roadIdx; toggleClose(i); zoomStreet(i); };
  $('btn-pick').onclick = () => setPick(!S.pickClose);
  $('btn-reopen-all').onclick = () => { if (S.manual.size) { S.manual.clear(); applyClosures(); toast('All manual closures lifted', 'good'); } };
  $('closed-list').addEventListener('click', e => {
    const re = e.target.closest('[data-reopen]'); if (re) return toggleClose(+re.dataset.reopen);
    const z = e.target.closest('[data-zoom-road]'); if (z) { zoomRoad(+z.dataset.zoomRoad); selectRoad(+z.dataset.zoomRoad); }
  });
  $('forecast-out').addEventListener('click', e => { const z = e.target.closest('[data-zoom-road]'); if (z) { zoomRoad(+z.dataset.zoomRoad); selectRoad(+z.dataset.zoomRoad); } });
  $('forecast-out').addEventListener('keydown', e => { if (e.key === 'Enter') { const z = e.target.closest('[data-zoom-road]'); if (z) z.click(); } });

  // ----- visitors
  const cats = { kovil: 'Temples', hotel: 'Food & stay', metro: 'Metro', station: 'Rail', place: 'Landmarks' };
  $('sel-poi').innerHTML = Object.entries(cats).map(([c, label]) => `<optgroup label="${label}">${net.pois.filter(p => p.category === c).map(p => `<option value="${p.id}">${p.icon} ${esc(p.name)}</option>`).join('')}</optgroup>`).join('');
  $('sel-poi').value = sim.focusPoi.id;
  $('sel-poi').onchange = e => { sim.focusPoi = net.pois.find(p => p.id === e.target.value); S.visitors = sim.focusPoi.defaultVisitors; $('sl-visitors').value = S.visitors; $('lbl-visitors').textContent = fmt(S.visitors); };
  $('sel-gw').innerHTML = net.gateways.map(g => `<option value="${g.key}">${esc(g.name)}</option>`).join('');
  $('sel-gw').onchange = e => setGateway(e.target.value);
  setGateway('south'); $('sel-gw').value = 'south';
  $('sl-visitors').oninput = e => { S.visitors = +e.target.value; $('lbl-visitors').textContent = fmt(S.visitors); };
  $('sl-focus').oninput = e => { sim.focusShare = e.target.value / 100; $('lbl-focus').textContent = e.target.value + '%'; };
  $('btn-dispatch').onclick = dispatch;

  // ----- weather
  $('tg-rain').onchange = e => setRain(e.target.checked);
  $('sl-rain').oninput = e => { weather.intensity = +e.target.value; view.rain.intensity = weather.intensity; weather.poke(); $('lbl-rain').textContent = INTENSITY[weather.intensity].label; };
  $('tg-autoclose').onchange = e => { weather.autoClose = e.target.checked; weather.poke(); weather.update(0); };
  $('tg-autoclock').onchange = e => { S.autoClock = e.target.checked; };
  $('sl-time').oninput = e => { S.clock = +e.target.value; S.autoClock = false; $('tg-autoclock').checked = false; updateClock(); };
  $('hotspot-list').innerHTML = WATER_SPOTS.map(s => `<div class="hs" data-spot="${s.id}" tabindex="0" role="button"><div class="t"><span>${esc(s.name)}</span><span class="depth accent">0 cm</span></div><div class="d">${s.elev} · up to ${s.baseDepth} cm · ${esc(s.desc)}</div><div class="bar"><i style="width:0"></i></div></div>`).join('');
  $('hotspot-list').addEventListener('click', e => { const h = e.target.closest('.hs'); if (!h) return; const s = WATER_SPOTS.find(x => x.id === h.dataset.spot); view.map.setView([s.lat, s.lng], 17.5); });

  // ----- streets
  const km = net.roads.reduce((a, r) => a + r.L, 0) / 1000;
  const cnt = f => new Set(net.roads.filter(f).map(r => r.src)).size;
  $('net-stats').innerHTML = [[fmt(net.nStreets), 'Streets'], [km.toFixed(0) + ' km', 'Total length'], [fmt(net.nR), 'Junction segments']].map(([b, l]) => `<div class="stat"><b>${b}</b><span>${l}</span></div>`).join('');
  const lab = (id, n) => $(id).closest('.row').firstElementChild.append(` (${fmt(n)})`);
  lab('tg-oneway', cnt(r => r.ow)); lab('tg-narrow', cnt(r => r.sm)); lab('tg-dead', cnt(r => r.de)); lab('tg-low', cnt(r => r.low));
  for (const [id, key] of [['tg-oneway', 'oneway'], ['tg-narrow', 'narrow'], ['tg-dead', 'dead'], ['tg-low', 'low']]) $(id).onchange = e => { S.hl[key] = e.target.checked; refreshRoadStyles(); };
  $('road-search').placeholder = `Search ${fmt(net.nStreets)} streets…`; $('poi-search').placeholder = `Search ${net.pois.length} places…`;
  $('road-search').oninput = e => renderRoadResults(e.target.value);
  renderRoadResults('');
  $('road-results').addEventListener('click', e => { const b = e.target.closest('[data-road]'); if (b) { zoomRoad(+b.dataset.road); selectRoad(+b.dataset.road); } });

  // ----- places
  $('poi-chips').innerHTML = [['all', 'All'], ...Object.entries(cats)].map(([k, l]) => `<button class="chip ${k === 'all' ? 'on' : ''}" data-cat="${k}">${l}</button>`).join('');
  $('poi-chips').addEventListener('click', e => { const c = e.target.closest('.chip'); if (!c) return; S.poiCat = c.dataset.cat; document.querySelectorAll('#poi-chips .chip').forEach(x => x.classList.toggle('on', x === c)); renderPoiList(); });
  $('poi-search').oninput = e => { S.poiQuery = e.target.value.toLowerCase(); renderPoiList(); };
  $('poi-list').addEventListener('click', e => { const b = e.target.closest('[data-poi]'); if (b) { const p = net.pois.find(x => x.id === b.dataset.poi); view.map.setView([p.lat, p.lng], 17.5); selectPoi(p); } });
  renderPoiList();

  // ----- chrome
  document.querySelector('.tabs').addEventListener('click', e => { const t = e.target.closest('[role=tab]'); if (t) setTab(t.dataset.tab); });
  document.querySelector('.tabs').addEventListener('keydown', e => {
    const tabs = [...document.querySelectorAll('.tabs [role=tab]')]; const i = tabs.findIndex(t => t.getAttribute('aria-selected') === 'true');
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { const n = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length]; n.focus(); setTab(n.dataset.tab); }
  });
  $('sheet-handle').onclick = () => $('sidebar').classList.toggle('collapsed');
  $('btn-play').onclick = () => setRunning(!S.running);
  $('speed-seg').addEventListener('click', e => { const b = e.target.closest('button'); if (b) setSpeed(+b.dataset.speed); });
  $('base-seg').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; view.setBase(b.dataset.base); store.set('base', b.dataset.base); syncBaseButtons(); refreshRoadStyles(); });
  $('btn-theme').onclick = () => { const t = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light'; document.documentElement.dataset.theme = t; store.set('theme', t); syncThemeIcon(); drawCharts(); };
  $('btn-help').onclick = () => $('help').showModal();

  document.addEventListener('keydown', onKey);
  addEventListener('resize', drawCharts);
  renderClosedList(); setGateway('south'); updateClock();
}

function onKey(e) {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const typing = /^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement.tagName);
  if (e.key === 'Escape') { if (S.pickClose) setPick(false); else clearSelection(); view.clearRoute(); return; }
  if (typing || $('help').open) return;
  switch (e.key) {
    case ' ': e.preventDefault(); setRunning(!S.running); break;
    case '1': setSpeed(1); break; case '2': setSpeed(2); break; case '4': setSpeed(4); break;
    case 'r': case 'R': { const on = !weather.on; $('tg-rain').checked = on; setRain(on); break; }
    case 'c': case 'C': setTab('forecast'); setPick(!S.pickClose); break;
    case 't': case 'T': setMode(MODES[(MODES.findIndex(m => m.id === S.mode) + 1) % MODES.length].id); S.autoSwitched = false; toast('Colouring: ' + MODES.find(m => m.id === S.mode).name); break;
    case '/': e.preventDefault(); setTab('places'); $('poi-search').focus(); break;
    case '?': $('help').showModal(); break;
  }
}

function setRain(on) {
  weather.on = on; view.rain.on = on; view.rain.intensity = weather.intensity; weather.poke();
  toast(on ? `${INTENSITY[weather.intensity].label} begins. Low basins will start to flood.` : 'Rain has stopped. Water is draining.', on ? 'warn' : 'good');
  if (on && S.mode === 'class') { /* keep user's mode; flood mode is one click away */ }
}

function renderRoadResults(q) {
  q = q.trim().toLowerCase();
  const list = net.roads.filter(r => r.n && (!q || r.n.toLowerCase().includes(q))).sort((a, b) => b.cap - a.cap || b.L - a.L).slice(0, 40);
  $('road-results').innerHTML = list.length ? list.map(r => `<button class="item" data-road="${r.roadIdx}"><span class="em">${r.ow ? '➜' : '═'}</span><span class="tx"><span>${esc(r.n)}</span><small>${r.t.replace('_', ' ')} · ${fmt(r.L)} m · ${r.w} m wide</small></span><span class="rt">${fmt(r.cap)}<br>veh/h</span></button>`).join('') : '<div class="empty">No street matches.</div>';
}

function renderPoiList() {
  const list = net.pois.filter(p => (S.poiCat === 'all' || p.category === S.poiCat) && (!S.poiQuery || p.name.toLowerCase().includes(S.poiQuery)));
  $('poi-list').innerHTML = list.length ? list.map(p => `<button class="item" data-poi="${p.id}"><span class="em">${p.icon}</span><span class="tx"><span>${esc(p.name)}</span><small>${esc(p.desc)}</small></span><span class="rt">${fmt(p.defaultVisitors)}<br>visitors/h</span></button>`).join('') : '<div class="empty">No place matches.</div>';
}

// ======================================================================
// visitor dispatch
// ======================================================================
function dispatch() {
  const poi = sim.focusPoi, gw = net.gateways.find(g => g.key === sim.focusGateway);
  sim.flush();
  sim.focusShare = $('sl-focus').value / 100;
  sim.targetFleet = fleetTarget();
  sim.prefill(sim.targetFleet);
  view.clearRoute();

  const open = gw ? gw.edges.filter(e => !sim.closedRoad[e >> 1]) : [];
  const from = open.length ? open[0] : (gw && gw.edges.length ? null : sim.localEdges[0]);
  const dest = new Set(poi.edges.filter(e => !sim.closedRoad[e >> 1]));
  const info = $('route-info');
  const res = from == null ? { hit: -1 } : shortest(net, [from], e => sim.closedRoad[e >> 1] ? Infinity : net.edgeLen[e] / net.limit[e], dest);
  if (res.hit >= 0) {
    const path = tracePath(res.prev, res.hit);
    view.showRoute(path);
    const dist = path.reduce((a, e) => a + net.edgeLen[e], 0);
    const names = []; const byName = new Map();
    for (const e of path) { const n = net.roads[e >> 1].n || ''; if (n) byName.set(n, (byName.get(n) || 0) + net.edgeLen[e]); }
    [...byName.entries()].sort((a, b) => b[1] - a[1]).slice(0, 3).forEach(([n]) => names.push(esc(n)));
    info.classList.remove('hidden');
    info.innerHTML = `<b>${(dist / 1000).toFixed(2)} km</b> · about <b>${Math.max(1, Math.round(res.dist[res.hit] / 60))} min</b> free-flow<br><span class="muted">via ${names.join(', ') || 'local streets'} · ${path.length} street segments</span>`;
    view.map.fitBounds(L.latLngBounds(path.flatMap(e => net.pts[e])), { padding: [90, 90], maxZoom: 17.5 });
    toast(`${fmt(S.visitors)} visitors/h heading to ${poi.name}`, 'good');
  } else {
    info.classList.remove('hidden');
    info.innerHTML = `<b style="color:var(--bad)">No drivable route</b> from this gateway to ${esc(poi.name)} with the current closures.`;
    toast('No route available. Reopen a closed street.', 'bad');
  }
  view.highlightPoi(poi.id);
}
