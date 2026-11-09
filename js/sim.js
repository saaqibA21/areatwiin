// Microscopic traffic simulation.
//
// Every vehicle follows a route over the directed street graph and is driven by
// the Intelligent Driver Model (IDM), so spacing, queues and shock waves emerge
// from car-following rather than being scripted. Closed streets act as a stop
// line and trigger re-routing; flooded streets slow traffic down.

import { shortest, tracePath } from './router.js';

export const VEHICLE_TYPES = {
  car:  { label: 'Car',           icon: '🚗', color: '#38bdf8', len: 4.2,  wid: 1.8, v0: 52 / 3.6, a: 1.5, b: 2.5, T: 1.3, s0: 2.0, share: 0.34 },
  bike: { label: 'Two-wheeler',   icon: '🏍️', color: '#34d399', len: 1.9,  wid: 0.8, v0: 48 / 3.6, a: 2.2, b: 3.0, T: 0.9, s0: 1.0, share: 0.34 },
  auto: { label: 'Auto-rickshaw', icon: '🛺', color: '#fbbf24', len: 2.8,  wid: 1.4, v0: 38 / 3.6, a: 1.4, b: 2.5, T: 1.1, s0: 1.6, share: 0.22 },
  bus:  { label: 'MTC bus',       icon: '🚌', color: '#f87171', len: 10.5, wid: 2.5, v0: 32 / 3.6, a: 1.0, b: 2.0, T: 1.5, s0: 2.5, share: 0.10 },
};

const QUEUED_MS = 5 / 3.6;           // slower than 5 km/h counts as queued
const STATS_EVERY = 0.5;             // s of sim time

function idm(v, v0, gap, dv, p) {
  const sStar = p.s0 + Math.max(0, v * p.T + (v * dv) / (2 * Math.sqrt(p.a * p.b)));
  const g = Math.max(gap, 0.1);
  const a = p.a * (1 - Math.pow(v / v0, 4) - (sStar * sStar) / (g * g));
  return a < -9 ? -9 : a;
}

export class Sim {
  constructor(net) {
    this.net = net;
    this.vehicles = [];
    this.lists = new Array(net.nE);
    this.touched = [];
    this.closedRoad = new Uint8Array(net.nR);
    this.slow = new Float32Array(net.nR).fill(1);      // flood speed factor per road
    this.rainFactor = 1;
    this.enabled = { car: true, bike: true, auto: true, bus: true };
    this.targetFleet = 60;
    this.focusPoi = net.pois[0];
    this.focusGateway = 'south';
    this.focusShare = 0.55;
    this.antiCollision = true;
    this.nextId = 101;
    this.time = 0;
    this.statsClock = 0;
    this.ratio = new Float32Array(net.nE).fill(1);     // live speed / free-flow per edge
    this.count = new Uint16Array(net.nE);
    this.arrivals = [];
    this.arrivedTotal = 0;
    this.strandedTotal = 0;
    this.tripTimeSum = 0;
    this.rq = [];
    this.stats = { avgKmh: 0, queued: 0, topKmh: 0, congestion: 0, throughput: 0, meanTrip: 0, n: 0 };

    this.localEdges = [];
    this.busEdges = [];
    for (let e = 0; e < net.nE; e++) {
      if (!net.main[e]) continue;
      const r = net.roads[e >> 1];
      if (r.t === 'residential' || r.t === 'tertiary') this.localEdges.push(e);
      if (r.b && !r.sm) this.busEdges.push(e);
    }
    this.totalVisitors = net.pois.reduce((s, p) => s + p.defaultVisitors, 0);
  }

  // ---------- configuration ----------
  setClosed(roadSet) {
    this.closedRoad.fill(0);
    for (const r of roadSet) this.closedRoad[r] = 1;
    for (const v of this.vehicles) {
      for (let k = v.ri + 1; k < v.route.length; k++) {
        if (this.closedRoad[v.route[k] >> 1]) { this._queueReroute(v); break; }
      }
    }
  }

  flush() { this.vehicles.length = 0; this.rq.length = 0; }

  /** Fill the network straight away with vehicles scattered along their first street. */
  prefill(n) {
    for (let tries = 0; this.vehicles.length < n && tries < n * 8; tries++) this._trySpawn(true);
  }

  _queueReroute(v) { if (!v.rq) { v.rq = true; this.rq.push(v); } }

  edgeV0(e) { return this.net.limit[e] * this.rainFactor * this.slow[e >> 1]; }

  // ---------- routing ----------
  _cost(type) {
    const { net } = this;
    const bus = type === 'bus';
    return e => {
      const r = e >> 1;
      if (this.closedRoad[r]) return Infinity;
      if (bus) { const rd = net.roads[r]; if (!rd.b || rd.sm) return Infinity; }
      const t = net.edgeLen[e] / Math.max(0.8, net.limit[e] * this.slow[r]);
      return t * (1 + 1.5 * (1 - this.ratio[e]));      // drivers avoid jammed streets
    };
  }

  _route(type, from, destEdges) {
    const res = shortest(this.net, [from], this._cost(type), destEdges);
    return res.hit >= 0 ? tracePath(res.prev, res.hit) : null;
  }

  _reroute(v) {
    const base = this._cost(v.type);
    const res = shortest(this.net, [v.e], e => (e === v.e ? 0.01 : base(e)), v.destEdges);
    if (res.hit < 0) return false;
    v.route = tracePath(res.prev, res.hit);
    v.ri = 0;
    return true;
  }

  // ---------- spawning ----------
  _pickType() {
    let total = 0;
    for (const k in VEHICLE_TYPES) if (this.enabled[k]) total += VEHICLE_TYPES[k].share;
    if (!total) return null;
    let x = Math.random() * total;
    for (const k in VEHICLE_TYPES) {
      if (!this.enabled[k]) continue;
      x -= VEHICLE_TYPES[k].share;
      if (x <= 0) return k;
    }
    return 'car';
  }

  _pickPoi() {
    let x = Math.random() * this.totalVisitors;
    for (const p of this.net.pois) { x -= p.defaultVisitors; if (x <= 0) return p; }
    return this.net.pois[0];
  }

  _pickGatewayKey() {
    let x = Math.random();
    for (const g of this.net.gateways) { x -= g.share; if (x <= 0) return g.key; }
    return 'local';
  }

  _originEdge(key, type) {
    if (type === 'bus') return this.busEdges.length ? this.busEdges[(Math.random() * this.busEdges.length) | 0] : null;
    const g = this.net.gateways.find(x => x.key === key);
    if (g && g.edges.length) {
      const open = g.edges.filter(e => !this.closedRoad[e >> 1]);
      return open.length ? open[(Math.random() * open.length) | 0] : null;   // every entry closed: cut off
    }
    return this.localEdges[(Math.random() * this.localEdges.length) | 0];
  }

  _trySpawn(scatter = false) {
    const type0 = this._pickType();
    if (!type0) return false;
    const focus = Math.random() < this.focusShare;
    const poi = focus ? this.focusPoi : this._pickPoi();
    const key = focus ? this.focusGateway : this._pickGatewayKey();
    let type = type0;
    let from = this._originEdge(key, type);
    if (from == null || this.closedRoad[from >> 1]) return false;

    const destEdges = new Set(poi.edges.filter(e => !this.closedRoad[e >> 1]));
    if (!destEdges.size || destEdges.has(from)) return false;

    // either enter at the start of the street, or (scatter) drop in somewhere along it
    const s = scatter ? Math.random() * this.net.edgeLen[from] * 0.8 : 0;
    const clear = e => { for (const o of this.vehicles) if (o.e === e && Math.abs(o.s - s) < o.len + 12) return false; return true; };
    if (!clear(from)) return false;

    let route = this._route(type, from, destEdges);
    if (!route && type === 'bus') { type = 'car'; from = this._originEdge(key, type); route = from != null && clear(from) ? this._route(type, from, destEdges) : null; }
    if (!route) return false;

    const P = VEHICLE_TYPES[type];
    const jitter = 0.88 + Math.random() * 0.22;
    this.vehicles.push({
      id: 'V-' + this.nextId++, type, P,
      p: { v0: P.v0 * jitter, a: P.a, b: P.b, T: P.T * (0.9 + Math.random() * 0.25), s0: P.s0 },
      len: P.len, e: route[0], s, v: scatter ? P.v0 * 0.6 : Math.min(4, P.v0 * 0.3), a: 0, gap: 1e9,
      route, ri: 0, poi, destEdges, born: this.time, wait: 0, braking: false, rq: false, failAt: 0,
    });
    return true;
  }

  // ---------- main step ----------
  step(dt) {
    const { net, lists, touched } = this;
    this.time += dt;

    // bucket vehicles by edge, leader first
    for (const e of touched) lists[e].length = 0;
    touched.length = 0;
    for (const v of this.vehicles) {
      let l = lists[v.e];
      if (!l) l = lists[v.e] = [];
      if (!l.length) touched.push(v.e);
      l.push(v);
    }
    for (const e of touched) if (lists[e].length > 1) lists[e].sort((a, b) => b.s - a.s);

    // accelerations
    for (const e of touched) {
      const l = lists[e];
      const L = net.edgeLen[e];
      const v0e = Math.max(0.8, this.edgeV0(e));
      for (let i = 0; i < l.length; i++) {
        const v = l[i];
        let gap = 1e9, dv = 0;
        if (this.antiCollision) {
          if (i > 0) {
            const lead = l[i - 1];
            gap = lead.s - lead.len - v.s; dv = v.v - lead.v;
          } else {
            const next = v.route[v.ri + 1];
            if (next !== undefined) {
              if (this.closedRoad[next >> 1]) { gap = L - v.s - 1; dv = v.v; }
              else {
                const nl = lists[next];
                const tail = nl && nl.length ? nl[nl.length - 1] : null;
                if (tail && v.wait < 45) { gap = (L - v.s) + tail.s - tail.len; dv = v.v - tail.v; }
              }
            }
          }
        } else if (i === 0) {
          const next = v.route[v.ri + 1];
          if (next !== undefined && this.closedRoad[next >> 1]) { gap = L - v.s - 1; dv = v.v; }
        }
        v.gap = gap;
        v.a = idm(v.v, Math.min(v.p.v0, v0e), gap, dv, v.p);
      }
    }

    // integrate + advance along routes
    let removed = false;
    for (const v of this.vehicles) {
      const nv = Math.max(0, v.v + v.a * dt);
      v.s += Math.max(0, (v.v + nv) * 0.5 * dt);
      v.v = nv;
      v.wait = nv < 0.3 ? v.wait + dt : 0;
      v.braking = v.a < -1.2;

      let L = net.edgeLen[v.e];
      if (v.destEdges.has(v.e) && v.s >= Math.min(L - 0.5, Math.max(10, L * 0.5))) { this._arrive(v); removed = true; continue; }
      while (v.s >= L) {
        const next = v.route[v.ri + 1];
        if (next === undefined) { this._arrive(v); removed = true; break; }
        if (this.closedRoad[next >> 1]) { v.s = L - 0.3; v.v = 0; this._queueReroute(v); break; }
        v.e = next; v.ri++; v.s -= L; L = net.edgeLen[v.e];
      }
      if (v.wait > 180 && !v.dead) { v.dead = true; this.strandedTotal++; removed = true; }
    }
    if (removed) this.vehicles = this.vehicles.filter(v => !v.dead);

    // re-routing queue (bounded work per step)
    for (let n = 0; n < 20 && this.rq.length; n++) {
      const v = this.rq.shift();
      v.rq = false;
      if (v.dead) continue;
      if (!this._reroute(v)) { v.failAt++; if (v.failAt < 24) setTimeout(() => this._queueReroute(v), 5000); }
    }

    // keep fleet near target
    let attempts = 3;
    while (this.vehicles.length < this.targetFleet && attempts-- > 0) this._trySpawn();
    if (this.vehicles.length > this.targetFleet * 1.15 + 2) this.vehicles.shift();

    this.statsClock += dt;
    if (this.statsClock >= STATS_EVERY) { this.statsClock = 0; this._stats(); }
  }

  _arrive(v) {
    v.dead = true;
    this.arrivedTotal++;
    this.tripTimeSum += this.time - v.born;
    this.arrivals.push(this.time);
  }

  _stats() {
    const { net, lists, touched } = this;
    const seen = new Set();
    let sum = 0, n = 0, queued = 0, top = 0, rsum = 0;
    for (const e of touched) {
      const l = lists[e];
      if (!l.length) continue;
      const v0e = Math.max(0.8, this.edgeV0(e));
      let es = 0;
      for (const v of l) {
        es += v.v; sum += v.v; n++;
        if (v.v < QUEUED_MS) queued++;
        if (v.v > top) top = v.v;
        rsum += Math.min(1, v.v / Math.min(v.p.v0, v0e));
      }
      const target = Math.min(1, es / l.length / v0e);
      this.ratio[e] += (target - this.ratio[e]) * 0.35;
      this.count[e] = l.length;
      seen.add(e);
    }
    for (let e = 0; e < net.nE; e++) {
      if (seen.has(e)) continue;
      this.count[e] = 0;
      if (this.ratio[e] < 1) this.ratio[e] = Math.min(1, this.ratio[e] + 0.06);
    }
    while (this.arrivals.length && this.arrivals[0] < this.time - 300) this.arrivals.shift();
    const win = Math.max(30, Math.min(300, this.time));
    this.stats = {
      n,
      avgKmh: n ? (sum / n) * 3.6 : 0,
      topKmh: top * 3.6,
      queued,
      congestion: n ? 1 - rsum / n : 0,
      throughput: this.arrivals.length / win * 3600,
      meanTrip: this.arrivedTotal ? this.tripTimeSum / this.arrivedTotal : 0,
    };
  }

  /** Live speed ratio of a road (lower of its two directions that carry traffic), 1 = free flow */
  roadRatio(i) {
    const a = this.ratio[2 * i], b = this.ratio[2 * i + 1];
    return Math.min(a, b);
  }
  roadCount(i) { return this.count[2 * i] + this.count[2 * i + 1]; }
}
