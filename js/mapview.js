// Leaflet map, street layer and the canvas overlays (vehicles, flood, rain).

import { pointAt } from './network.js';
import { WATER_SPOTS } from './weather.js';

const L = window.L;

export const BASEMAPS = {
  satellite: {
    label: 'Satellite',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr: 'Imagery © Esri, Maxar, Earthstar Geographics', maxNativeZoom: 19, dark: true,
  },
  dark: {
    label: 'Dark',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
    attr: 'Tiles © Esri, DeLorme, NAVTEQ', maxNativeZoom: 16, dark: true,
  },
  light: {
    label: 'Light',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
    attr: 'Tiles © Esri, DeLorme, NAVTEQ', maxNativeZoom: 16, dark: false,
  },
  streets: {
    label: 'Streets',
    url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attr: '© OpenStreetMap contributors', maxNativeZoom: 19, dark: false,
  },
};

const CENTER = [13.1035, 80.2935];
const speedColor = ratio => `hsl(${Math.round(Math.max(0, Math.min(1, ratio)) * 125)} 85% 55%)`;

export class MapView {
  constructor(el, net, handlers) {
    this.net = net; this.h = handlers;
    this.followVeh = null;
    this.colorBySpeed = false;
    this.showVehicles = true;
    this.closedInfo = new Map();
    this.waterLevel = 0;
    this.rain = { on: false, intensity: 1 };
    this.drops = [];
    this.t = 0;
    this._last = null;

    const map = this.map = L.map(el, {
      center: CENTER, zoom: 16, minZoom: 14, maxZoom: 19, zoomControl: false,
      zoomAnimation: false, zoomSnap: 0.5, zoomDelta: 0.5, wheelPxPerZoomLevel: 90,
      maxBounds: L.latLngBounds(net.bounds).pad(1.2), attributionControl: true, preferCanvas: true,
    });
    L.control.zoom({ position: 'bottomleft' }).addTo(map);
    map.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet</a>');

    this.baseLayer = null;
    this._tileErrors = 0;
    this.setBase(handlers.initialBase || 'satellite');

    // panes
    const mk = (name, z) => { const p = map.createPane(name); p.style.zIndex = z; return p; };
    mk('casing', 410); mk('roads', 420); mk('route', 430);
    const vp = mk('vehicles', 450); vp.style.pointerEvents = 'none';

    this.casingRenderer = L.canvas({ pane: 'casing', padding: 0.4 });
    this.roadRenderer = L.canvas({ pane: 'roads', padding: 0.4, tolerance: 6 });
    this.routeRenderer = L.svg({ pane: 'route' });

    this._buildRoads();
    this._buildMarkers();
    this._buildVehicleCanvas(vp);
    this._buildRainCanvas(el);

    this.selLine = L.polyline([], { pane: 'route', renderer: this.routeRenderer, color: '#fff', weight: 9, opacity: 0.85, interactive: false, className: 'sel-line' }).addTo(map);
    this.routeLine = L.polyline([], { pane: 'route', renderer: this.routeRenderer, color: '#22d3ee', weight: 5, opacity: 0.95, dashArray: '2 10', lineCap: 'round', interactive: false, className: 'route-line' }).addTo(map);
    this.routeGlow = L.polyline([], { pane: 'route', renderer: this.routeRenderer, color: '#22d3ee', weight: 12, opacity: 0.25, interactive: false }).addTo(map);

    map.on('click', e => handlers.onPick(e.latlng, null));
    map.on('move zoom resize', () => this.redraw());
    map.on('zoomend', () => { el.dataset.zoom = Math.round(map.getZoom()); });
    el.dataset.zoom = Math.round(map.getZoom());
    new ResizeObserver(() => { this._sizeCanvases(); map.invalidateSize(); this.redraw(); }).observe(el);
  }

  // ---------- base map ----------
  setBase(key) {
    const b = BASEMAPS[key]; if (!b) return;
    if (this.baseLayer) this.map.removeLayer(this.baseLayer);
    this.baseKey = key;
    this.lightBase = b.dark === false;
    this.baseLayer = L.tileLayer(b.url, {
      attribution: b.attr, subdomains: b.subdomains || 'abc', maxNativeZoom: b.maxNativeZoom, maxZoom: 19, crossOrigin: true,
    }).addTo(this.map);
    this.baseLayer.bringToBack();
    this.baseLayer.on('tileerror', () => {
      if (++this._tileErrors === 6) this.h.onTileError && this.h.onTileError(key);
    });
    this._tileErrors = 0;
    this.map.getContainer().dataset.base = key;
  }

  setNight(f) {   // 0 = day, 1 = deepest night
    this.map.getPane('tilePane').style.filter = `brightness(${(1 - 0.5 * f).toFixed(2)}) saturate(${(1 - 0.3 * f).toFixed(2)})`;
  }

  // ---------- roads ----------
  _buildRoads() {
    this.lines = []; this.casings = []; this._styleCache = [];
    const grp = this.roadGroup = L.layerGroup().addTo(this.map);
    for (const r of this.net.roads) {
      const ll = r.p;
      const casing = L.polyline(ll, { pane: 'casing', renderer: this.casingRenderer, color: '#020617', weight: 5, opacity: 0.5, interactive: false, lineCap: 'round' });
      const line = L.polyline(ll, { pane: 'roads', renderer: this.roadRenderer, color: '#94a3b8', weight: 2, opacity: 0.8, lineCap: 'round', lineJoin: 'round', bubblingMouseEvents: false });
      line.on('click', e => this.h.onPick(e.latlng, r.roadIdx));
      line.on('mouseover', e => this.h.onHover && this.h.onHover(r.roadIdx, e.originalEvent));
      line.on('mouseout', () => this.h.onHover && this.h.onHover(null));
      line.on('mousemove', e => this.h.onHover && this.h.onHover(r.roadIdx, e.originalEvent));
      grp.addLayer(casing); grp.addLayer(line);
      this.casings[r.roadIdx] = casing; this.lines[r.roadIdx] = line;
    }
  }

  /** styleFn(road) -> {color, weight, opacity, order?} */
  restyle(styleFn) {
    for (const r of this.net.roads) {
      const s = styleFn(r);
      const key = s.color + '|' + s.weight + '|' + s.opacity;
      if (this._styleCache[r.roadIdx] === key) continue;
      this._styleCache[r.roadIdx] = key;
      this.lines[r.roadIdx].setStyle({ color: s.color, weight: s.weight, opacity: s.opacity });
      this.casings[r.roadIdx].setStyle({ weight: s.weight + 2.6, opacity: Math.min(0.6, s.opacity * 0.65) });
    }
  }

  setRoadsVisible(v) {
    if (v) this.map.addLayer(this.roadGroup); else this.map.removeLayer(this.roadGroup);
  }

  select(roadIdx) {
    this.selLine.setLatLngs(roadIdx == null ? [] : this.net.roads[roadIdx].p);
    if (roadIdx != null) this.selLine.bringToFront();
  }

  // ---------- markers ----------
  _buildMarkers() {
    const { map, net } = this;
    this.poiMarkers = new Map();
    this.poiLayer = L.layerGroup().addTo(map);
    for (const p of net.pois) {
      const icon = L.divIcon({
        className: 'poi-wrap', iconSize: [30, 30], iconAnchor: [15, 15],
        html: `<div class="poi-pin cat-${p.category}" data-id="${p.id}"><span>${p.icon}</span></div><div class="poi-label">${p.name}</div>`,
      });
      const m = L.marker([p.lat, p.lng], { icon, keyboard: true, title: p.name, riseOnHover: true });
      m.on('click', ev => { L.DomEvent.stopPropagation(ev); this.h.onPoi(p); });
      m.addTo(this.poiLayer);
      this.poiMarkers.set(p.id, m);
    }
    this.gwLayer = L.layerGroup().addTo(map);
    for (const g of net.gateways) {
      if (g.edge == null) continue;
      L.marker([g.lat, g.lng], {
        interactive: true, icon: L.divIcon({ className: 'gw-wrap', iconSize: [0, 0], html: `<div class="gw-pin" data-key="${g.key}"><b>${g.icon}</b><span>${g.key === 'harbour' ? 'East' : g.key}</span></div>` }),
      }).on('click', ev => { L.DomEvent.stopPropagation(ev); this.h.onGateway(g); }).addTo(this.gwLayer);
    }
  }

  setPoiVisible(v) { if (v) this.map.addLayer(this.poiLayer); else this.map.removeLayer(this.poiLayer); }
  setGatewaysVisible(v) { if (v) this.map.addLayer(this.gwLayer); else this.map.removeLayer(this.gwLayer); }

  highlightPoi(id) {
    document.querySelectorAll('.poi-pin.active').forEach(n => n.classList.remove('active'));
    const n = document.querySelector(`.poi-pin[data-id="${id}"]`);
    if (n) n.classList.add('active');
  }

  // ---------- route overlay ----------
  showRoute(edges) {
    const ll = [];
    for (const e of edges) for (const p of this.net.pts[e]) ll.push(p);
    this.routeLine.setLatLngs(ll); this.routeGlow.setLatLngs(ll);
  }
  clearRoute() { this.routeLine.setLatLngs([]); this.routeGlow.setLatLngs([]); }

  // ---------- canvases ----------
  _buildVehicleCanvas(pane) {
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'veh-canvas';
    pane.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d');
    // one-way chevrons, precomputed
    this.arrows = [];
    for (const r of this.net.roads) {
      if (!r.ow) continue;
      const e = 2 * r.roadIdx, L = this.net.edgeLen[e];
      const n = Math.max(1, Math.floor(L / 70));
      for (let k = 0; k < n; k++) {
        const p = pointAt(this.net, e, L * (k + 0.5) / n);
        this.arrows.push([p[0], p[1], p[2]]);
      }
    }
    this._sizeCanvases();
  }

  _buildRainCanvas(el) {
    this.rainCanvas = document.createElement('canvas');
    this.rainCanvas.className = 'rain-canvas';
    el.appendChild(this.rainCanvas);
    this.rctx = this.rainCanvas.getContext('2d');
  }

  _sizeCanvases() {
    const el = this.map.getContainer();
    const w = el.clientWidth, h = el.clientHeight, dpr = Math.min(2, window.devicePixelRatio || 1);
    this.dpr = dpr; this.w = w; this.h_ = h;
    for (const c of [this.canvas, this.rainCanvas].filter(Boolean)) {
      c.width = Math.round(w * dpr); c.height = Math.round(h * dpr);
      c.style.width = w + 'px'; c.style.height = h + 'px';
    }
  }

  get pxPerM() {
    const z = this.map.getZoom();
    return Math.pow(2, z) / (156543.03 * Math.cos(CENTER[0] * Math.PI / 180));
  }

  /** Draw the dynamic layer. Called every animation frame and on map movement. */
  redraw(sim) {
    if (sim) this._sim = sim; else sim = this._sim;
    if (!sim || !this.ctx) return;
    const { map, ctx, dpr, net } = this;
    L.DomUtil.setPosition(this.canvas, map.containerPointToLayerPoint([0, 0]));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, this.w, this.h_);

    const z = map.getZoom();
    const ppm = this.pxPerM;
    const scale = Math.max(2.6, Math.min(4.5, ppm * 3));
    const view = map.getBounds().pad(0.05);

    this._drawWater(ctx, ppm);
    if (z >= 16.5) this._drawArrows(ctx, view, z);
    this._drawClosures(ctx, scale);
    if (this.showVehicles) this._drawVehicles(ctx, sim, view, scale);
  }

  _drawWater(ctx, ppm) {
    if (this.waterLevel <= 0.01) return;
    const lvl = Math.min(1.2, this.waterLevel);
    for (const s of WATER_SPOTS) {
      const c = this.map.latLngToContainerPoint([s.lat, s.lng]);
      const r = Math.max(10, s.radius * ppm * (0.45 + 0.55 * Math.min(1, lvl)) * 1.4);
      const g = ctx.createRadialGradient(c.x, c.y, 0, c.x, c.y, r);
      const a = Math.min(0.62, 0.18 + 0.4 * lvl);
      g.addColorStop(0, `rgba(56,189,248,${a})`); g.addColorStop(0.7, `rgba(14,116,144,${a * 0.7})`); g.addColorStop(1, 'rgba(14,116,144,0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(c.x, c.y, r, 0, Math.PI * 2); ctx.fill();
      const ph = (this.t * 0.6 + s.radius) % 1;
      ctx.strokeStyle = `rgba(186,230,253,${0.45 * (1 - ph)})`; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(c.x, c.y, r * (0.25 + 0.7 * ph), 0, Math.PI * 2); ctx.stroke();
      if (this.map.getZoom() >= 16) {
        ctx.fillStyle = 'rgba(224,242,254,.95)'; ctx.font = '600 11px system-ui, sans-serif'; ctx.textAlign = 'center';
        ctx.fillText(`${Math.round(s.baseDepth * lvl)} cm`, c.x, c.y + 4);
      }
    }
  }

  _drawArrows(ctx, view, z) {
    ctx.fillStyle = 'rgba(255,255,255,.85)';
    const sz = z >= 18 ? 4.5 : 3.2;
    for (const a of this.arrows) {
      if (!view.contains([a[0], a[1]])) continue;
      const p = this.map.latLngToContainerPoint([a[0], a[1]]);
      ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(-a[2]);
      ctx.beginPath(); ctx.moveTo(sz, 0); ctx.lineTo(-sz, sz * 0.9); ctx.lineTo(-sz * 0.4, 0); ctx.lineTo(-sz, -sz * 0.9); ctx.closePath(); ctx.fill();
      ctx.restore();
    }
  }

  _drawClosures(ctx, scale) {
    if (!this.closedInfo.size) return;
    const pulse = 0.5 + 0.5 * Math.sin(this.t * 4);
    const r0 = 7 + scale * 1.4;
    const seen = new Set();
    for (const [i, kind] of this.closedInfo) {
      const rd = this.net.roads[i];
      if (seen.has(rd.src)) continue;            // one marker per street, not per junction piece
      seen.add(rd.src);
      const mid = rd.p[Math.floor(rd.p.length / 2)];
      const c = this.map.latLngToContainerPoint(mid);
      const col = kind === 'flood' ? '#0ea5e9' : '#ef4444';
      ctx.fillStyle = col + '33'; ctx.beginPath(); ctx.arc(c.x, c.y, r0 + 6 * pulse, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = col; ctx.beginPath(); ctx.arc(c.x, c.y, r0, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 2;
      if (kind === 'flood') {
        ctx.beginPath(); ctx.moveTo(c.x - r0 * .5, c.y - 1); ctx.quadraticCurveTo(c.x - r0 * .25, c.y - r0 * .45, c.x, c.y - 1); ctx.quadraticCurveTo(c.x + r0 * .25, c.y + r0 * .4, c.x + r0 * .5, c.y - 1); ctx.stroke();
      } else {
        ctx.beginPath(); ctx.moveTo(c.x - r0 * .55, c.y); ctx.lineTo(c.x + r0 * .55, c.y); ctx.stroke();
      }
    }
  }

  _drawVehicles(ctx, sim, view, scale) {
    const sel = this.selectedVeh;
    const rr = typeof ctx.roundRect === 'function';
    for (const v of sim.vehicles) {
      const p = pointAt(this.net, v.e, v.s);
      if (!view.contains([p[0], p[1]])) continue;
      const c = this.map.latLngToContainerPoint([p[0], p[1]]);
      const len = v.P.len * scale, wid = Math.max(3, v.P.wid * scale * 1.15);
      ctx.save(); ctx.translate(c.x, c.y); ctx.rotate(-p[2]);
      if (v === sel) {
        ctx.strokeStyle = '#fff'; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(0, 0, Math.max(len, 12) * 0.9, 0, Math.PI * 2); ctx.stroke();
        ctx.fillStyle = 'rgba(255,255,255,.18)'; ctx.fill();
      }
      ctx.fillStyle = this.colorBySpeed ? speedColor(v.v / Math.max(1, Math.min(v.p.v0, sim.edgeV0(v.e)))) : v.P.color;
      ctx.strokeStyle = this.lightBase ? 'rgba(2,6,23,.8)' : 'rgba(255,255,255,.9)'; ctx.lineWidth = 1;
      ctx.beginPath();
      if (rr) ctx.roundRect(-len / 2, -wid / 2, len, wid, Math.min(2.2, wid / 2)); else ctx.rect(-len / 2, -wid / 2, len, wid);
      ctx.fill(); ctx.stroke();
      if (v.braking || v.v < 0.5) {            // brake lights
        ctx.fillStyle = '#ff2d2d';
        ctx.fillRect(-len / 2 - 0.6, -wid / 2 + 0.4, 1.8, wid - 0.8);
      }
      ctx.restore();
    }
  }

  nearestVehicle(sim, latlng, maxPx = 16) {
    const c0 = this.map.latLngToContainerPoint(latlng);
    let best = null, bd = maxPx * maxPx;
    for (const v of sim.vehicles) {
      const p = pointAt(this.net, v.e, v.s);
      const c = this.map.latLngToContainerPoint([p[0], p[1]]);
      const d = (c.x - c0.x) ** 2 + (c.y - c0.y) ** 2;
      if (d < bd) { bd = d; best = v; }
    }
    return best;
  }

  vehicleLatLng(v) { const p = pointAt(this.net, v.e, v.s); return [p[0], p[1]]; }

  follow(v) { this.followVeh = v; }
  centerOnFollow() {
    if (!this.followVeh) return;
    const ll = this.vehicleLatLng(this.followVeh);
    const c = this.map.latLngToContainerPoint(ll), mid = this.map.getSize().divideBy(2);
    if (Math.hypot(c.x - mid.x, c.y - mid.y) > 6) this.map.panBy([c.x - mid.x, c.y - mid.y], { animate: false });
  }

  // ---------- rain ----------
  drawRain(dt, reducedMotion) {
    const { rctx: ctx, w, h_: h, dpr } = this;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    if (!this.rain.on) { this.drops.length = 0; return; }
    const I = this.rain.intensity;
    const target = reducedMotion ? 0 : [0, 90, 220, 420][I];
    while (this.drops.length < target) this.drops.push({ x: Math.random() * (w + 80), y: Math.random() * h, l: 8 + Math.random() * 12, s: 520 + Math.random() * 380 });
    if (this.drops.length > target) this.drops.length = target;
    ctx.fillStyle = `rgba(15,40,80,${0.07 + I * 0.06})`; ctx.fillRect(0, 0, w, h);
    ctx.strokeStyle = 'rgba(190,225,255,.55)'; ctx.lineWidth = 1;
    ctx.beginPath();
    for (const d of this.drops) {
      d.y += d.s * dt; d.x -= d.s * dt * 0.22;
      if (d.y > h) { d.y = -d.l; d.x = Math.random() * (w + 80); }
      ctx.moveTo(d.x, d.y); ctx.lineTo(d.x + d.l * 0.22, d.y - d.l);
    }
    ctx.stroke();
  }

  tick(dt) { this.t += dt; }
}
