// Traffic assignment forecast.
//
// Visitor demand from each entry gateway to each place is loaded onto the street
// graph with a capacity-restrained user-equilibrium heuristic (BPR volume-delay
// function + method of successive averages). Running it twice - once with the
// network as normal, once with the current closures - shows where displaced
// traffic ends up and which streets choke.

import { shortest, tracePath } from './router.js';

const VEH_PER_VISITOR = 0.5;
const MSA_ITERATIONS = 6;
const CALIBRATION_VC = 0.85;      // calibration: on a normal day the busiest arterial runs at 0.85 V/C
const LOCAL_ORIGINS = 10;

export const VC_BANDS = [
  { min: 1.10, color: '#ef4444', label: 'Severe gridlock' },
  { min: 0.85, color: '#f97316', label: 'Heavy congestion' },
  { min: 0.65, color: '#eab308', label: 'Moderate load' },
  { min: 0.40, color: '#84cc16', label: 'Busy' },
  { min: 0.00, color: '#22c55e', label: 'Free flowing' },
];
export const vcColor = vc => (VC_BANDS.find(b => vc >= b.min) || VC_BANDS[VC_BANDS.length - 1]).color;
export const vcLabel = vc => (VC_BANDS.find(b => vc >= b.min) || VC_BANDS[VC_BANDS.length - 1]).label;

export class Forecaster {
  constructor(net) {
    this.net = net;
    this.t0 = new Float64Array(net.nE);
    for (let e = 0; e < net.nE; e++) if (net.exists[e]) this.t0[e] = net.edgeLen[e] / net.limit[e];

    this.origins = this._buildOrigins();
    this.scale = 1;
    this.scale = this._calibrate();
    this.baseline = this.run(new Set());
  }

  _buildOrigins() {
    const { net } = this;
    const origins = [];
    for (const g of net.gateways) for (const e of g.edges) origins.push({ edge: e, share: g.share / g.edges.length, key: g.key });
    const localShare = (net.gateways.find(g => g.key === 'local') || { share: 0 }).share;
    const cand = [];
    for (let e = 0; e < net.nE; e++) {
      if (!net.main[e]) continue;
      const r = net.roads[e >> 1];
      if (r.t === 'residential' || r.t === 'tertiary') cand.push(e);
    }
    const step = Math.max(1, Math.floor(cand.length / LOCAL_ORIGINS));
    for (let i = 0, c = 0; i < cand.length && c < LOCAL_ORIGINS; i += step, c++) {
      origins.push({ edge: cand[i], share: localShare / LOCAL_ORIGINS, key: 'local' });
    }
    return origins;
  }

  _demandFor(origin) {
    return this.net.pois.map(p => [p, origin.share * p.defaultVisitors * VEH_PER_VISITOR * this.scale]);
  }

  _calibrate() {
    const { net } = this;
    const flow = new Float64Array(net.nE);
    this._loadAon(flow, e => this.t0[e]);
    let peak = 0;
    for (let e = 0; e < net.nE; e++) {
      if (net.exists[e] && net.roads[e >> 1].cap >= 950) peak = Math.max(peak, flow[e] / net.capDir[e]);
    }
    return peak > 0 ? CALIBRATION_VC / peak : 1;
  }

  // Entries closed at a gateway hand their demand to the gateway's open entries; a gateway
  // with every entry closed loses its demand.
  _activeOrigins(closedEdge) {
    const groups = new Map();
    for (const o of this.origins) { if (!groups.has(o.key)) groups.set(o.key, []); groups.get(o.key).push(o); }
    const active = []; let lostShare = 0;
    for (const list of groups.values()) {
      const total = list.reduce((a, o) => a + o.share, 0);
      const open = list.filter(o => !closedEdge[o.edge]);
      if (!open.length) { lostShare += total; continue; }
      for (const o of open) active.push({ edge: o.edge, key: o.key, share: total / open.length });
    }
    return { active, lostShare };
  }

  // all-or-nothing assignment; adds into `flow`, returns unserved veh/h
  _loadAon(flow, cost, origins = this.origins) {
    const { net } = this;
    let unserved = 0;
    for (const o of origins) {
      const { dist, prev } = shortest(net, [o.edge], cost);
      for (const [p, q] of this._demandFor(o)) {
        let best = -1, bd = Infinity;
        for (const e of p.edges) if (dist[e] < bd) { bd = dist[e]; best = e; }
        if (best < 0) { unserved += q; continue; }
        for (const e of tracePath(prev, best)) flow[e] += q;
      }
    }
    return unserved;
  }

  /** @param closedRoads Set of road indices that are closed */
  run(closedRoads) {
    const { net } = this;
    const closedEdge = new Uint8Array(net.nE);
    for (const r of closedRoads) { closedEdge[2 * r] = 1; closedEdge[2 * r + 1] = 1; }

    const flow = new Float64Array(net.nE);
    const aon = new Float64Array(net.nE);
    const { active, lostShare } = this._activeOrigins(closedEdge);
    const perShare = net.pois.reduce((a, p) => a + p.defaultVisitors, 0) * VEH_PER_VISITOR * this.scale;
    let unserved = 0;
    const cost = e => {
      if (closedEdge[e]) return Infinity;
      const x = flow[e] / Math.max(net.capDir[e], 1);
      return this.t0[e] * (1 + 0.15 * x * x * x * x);
    };
    for (let k = 1; k <= MSA_ITERATIONS; k++) {
      aon.fill(0);
      unserved = this._loadAon(aon, cost, active);
      const w = 1 / k;
      for (let e = 0; e < net.nE; e++) flow[e] = flow[e] * (1 - w) + aon[e] * w;
    }

    const vc = new Float32Array(net.nR);
    const flowRoad = new Float64Array(net.nR);
    let vht = 0, served = 0;
    for (let e = 0; e < net.nE; e++) {
      if (!net.exists[e]) continue;
      const x = flow[e] / Math.max(net.capDir[e], 1);
      const i = e >> 1;
      if (x > vc[i]) vc[i] = x;
      flowRoad[i] += flow[e];
      vht += flow[e] * this.t0[e] * (1 + 0.15 * x * x * x * x) / 3600;
    }
    const total = this.origins.reduce((a, o) => a + o.share, 0) * perShare;
    unserved += lostShare * perShare;
    served = total - unserved;
    return { vc, flowRoad, vht, served, unserved, total, closed: new Set(closedRoads) };
  }

  /** Compare a scenario run against the normal-day baseline. */
  compare(scen) {
    const base = this.baseline, { net } = this;
    // traffic that normally uses a closed street: a trip crosses several junction pieces of the
    // same street, so take the busiest piece of each street instead of summing the pieces
    const perStreet = new Map();
    for (const r of scen.closed) {
      const s = net.roads[r].src;
      perStreet.set(s, Math.max(perStreet.get(s) || 0, base.flowRoad[r]));
    }
    let displaced = 0;
    for (const f of perStreet.values()) displaced += f;

    const counts = { severe: 0, heavy: 0, moderate: 0 };
    const bcounts = { severe: 0, heavy: 0, moderate: 0 };
    const tally = (c, vc) => { if (vc >= 1.1) c.severe++; else if (vc >= 0.85) c.heavy++; else if (vc >= 0.65) c.moderate++; };

    const rows = [];
    let sumVc = 0, nVc = 0;
    for (let i = 0; i < net.nR; i++) {
      tally(bcounts, base.vc[i]);
      if (scen.closed.has(i)) continue;
      tally(counts, scen.vc[i]);
      if (scen.flowRoad[i] > 0) { sumVc += scen.vc[i]; nVc++; }
      const surge = base.flowRoad[i] > 1 ? (scen.flowRoad[i] / base.flowRoad[i] - 1) * 100 : (scen.flowRoad[i] > 1 ? 100 : 0);
      if (scen.vc[i] >= 0.65 && scen.flowRoad[i] > base.flowRoad[i] * 1.05) {
        rows.push({ i, name: net.roads[i].n, vcBase: base.vc[i], vcScen: scen.vc[i], surge, cap: net.roads[i].cap });
      }
    }
    rows.sort((a, b) => b.vcScen - a.vcScen);

    const lanes = r => (net.roads[r].w >= 5.5 ? 2 : 1);
    let queue10 = 0;
    for (const r of scen.closed) queue10 = Math.max(queue10, base.flowRoad[r] * (10 / 60) * 7.5 / lanes(r) / (net.roads[r].ow ? 1 : 2));

    const dVht = Math.max(0, scen.vht - base.vht);
    return {
      displaced,
      queue10: Math.min(queue10, 1800),
      extraVehHours: dVht,
      detourSec: displaced > 1 ? dVht * 3600 / displaced : 0,
      delayMin: scen.served > 0 ? dVht * 60 / scen.served : 0,
      avgVc: nVc ? sumVc / nVc : 0,
      unservedPct: scen.total ? scen.unserved / scen.total * 100 : 0,
      counts, bcounts,
      top: rows.slice(0, 6),
    };
  }
}
