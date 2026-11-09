// Road network model: loads the OSM-derived street data and turns it into a
// directed graph with one node per (road, direction) pair.
//
//   edge id e = 2 * roadIndex + dir      dir 0 = along the stored polyline
//                                        dir 1 = against it (absent on one-way streets)

const DEG = Math.PI / 180;
const M_PER_DEG = 111320;
const LINK_MAX_M = 25;      // recorded links longer than this are not real junctions
const SNAP_M = 8;           // unrecorded street ends this close are treated as one junction
const JUMP_MAX_M = 30;      // longest allowed hop between two streets at a junction
const TEE_M = 6;            // a street end this close to the side of another street is a T-junction
const MIN_PIECE_M = 4;      // never split off a piece shorter than this

// Free-flow speed by OSM highway class (km/h)
const CLASS_KMH = {
  trunk: 40, primary: 40, primary_link: 30, secondary: 36, tertiary: 30,
  residential: 24, living_street: 15,
};

export async function loadData(base = 'data/') {
  const [roads, pois] = await Promise.all([
    fetch(base + 'roads.json').then(r => { if (!r.ok) throw new Error('roads.json ' + r.status); return r.json(); }),
    fetch(base + 'pois.json').then(r => { if (!r.ok) throw new Error('pois.json ' + r.status); return r.json(); }),
  ]);
  return { roads, pois };
}

function segLen(a, b) {
  const dy = (b[0] - a[0]) * M_PER_DEG;
  const dx = (b[1] - a[1]) * M_PER_DEG * Math.cos(a[0] * DEG);
  return Math.hypot(dx, dy);
}


// Many streets end on the side of another street (T-junctions) but the source data keeps
// the through street as a single way. Split it at those points so the junction exists in
// the graph. The first piece keeps the original index; extra pieces are appended.
function planarize(src) {
  const roads = src.map((r, i) => ({ ...r, src: i }));
  const n = roads.length;
  const cosL = Math.cos(13.1 * DEG);
  const toXY = p => [p[1] * M_PER_DEG * cosL, p[0] * M_PER_DEG];
  const xy = roads.map(r => r.p.map(toXY));
  const box = xy.map(a => {
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const [x, y] of a) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
    return [x0 - TEE_M, y0 - TEE_M, x1 + TEE_M, y1 + TEE_M];
  });
  const cumXY = xy.map(a => { const c = [0]; for (let k = 1; k < a.length; k++) c.push(c[k - 1] + Math.hypot(a[k][0] - a[k - 1][0], a[k][1] - a[k - 1][1])); return c; });

  const splits = Array.from({ length: n }, () => []);
  for (let i = 0; i < n; i++) {
    for (const end of [0, xy[i].length - 1]) {
      const [ex, ey] = xy[i][end];
      let best = null;
      for (let j = 0; j < n; j++) {
        if (j === i) continue;
        const b = box[j];
        if (ex < b[0] || ex > b[2] || ey < b[1] || ey > b[3]) continue;
        const a = xy[j];
        for (let k = 0; k < a.length - 1; k++) {
          const dx = a[k + 1][0] - a[k][0], dy = a[k + 1][1] - a[k][1];
          const l2 = dx * dx + dy * dy || 1e-9;
          const tt = Math.max(0, Math.min(1, ((ex - a[k][0]) * dx + (ey - a[k][1]) * dy) / l2));
          const px = a[k][0] + dx * tt, py = a[k][1] + dy * tt;
          const d = Math.hypot(ex - px, ey - py);
          if (d <= TEE_M && (!best || d < best.d)) {
            const s = cumXY[j][k] + tt * Math.sqrt(l2);
            best = { j, k, tt, d, s, pt: [roads[j].p[k][0] + (roads[j].p[k + 1][0] - roads[j].p[k][0]) * tt, roads[j].p[k][1] + (roads[j].p[k + 1][1] - roads[j].p[k][1]) * tt] };
          }
        }
      }
      if (!best) continue;
      const total = cumXY[best.j][cumXY[best.j].length - 1];
      if (best.s < MIN_PIECE_M || total - best.s < MIN_PIECE_M) continue;   // that is an end-to-end junction
      splits[best.j].push(best);
    }
  }

  const extra = [];
  for (let j = 0; j < n; j++) {
    if (!splits[j].length) continue;
    const r = roads[j], pts = r.p;
    const list = splits[j].sort((a, b) => a.s - b.s);
    const pieces = []; let cur = [pts[0]], next = 1, lastS = 0;
    for (const s of list) {
      if (s.s - lastS < MIN_PIECE_M) continue;
      for (let v = next; v <= s.k; v++) cur.push(pts[v]);
      next = s.k + 1;
      cur.push(s.pt); pieces.push(cur); cur = [s.pt]; lastS = s.s;
    }
    for (let v = next; v < pts.length; v++) cur.push(pts[v]);
    pieces.push(cur);
    r.p = pieces[0];
    for (let q = 1; q < pieces.length; q++) extra.push({ ...r, p: pieces[q], id: r.id + '#' + (q + 1) });
  }
  return roads.concat(extra);
}

export function buildNetwork(srcRoads, pois) {
  const roads = planarize(srcRoads);
  const nR = roads.length;
  const nE = nR * 2;

  const exists = new Uint8Array(nE);
  const edgeLen = new Float64Array(nE);
  const limit = new Float32Array(nE);        // speed limit, m/s
  const pts = new Array(nE);                 // polyline in travel direction
  const cum = new Array(nE);                 // cumulative metres along pts
  const capDir = new Float32Array(nE);       // vehicles / hour for this direction

  roads.forEach((r, i) => {
    const fwdPts = r.p;
    const fwdCum = [0];
    for (let k = 1; k < fwdPts.length; k++) fwdCum.push(fwdCum[k - 1] + segLen(fwdPts[k - 1], fwdPts[k]));
    const total = fwdCum[fwdCum.length - 1];
    r.L = Math.max(total, 1);                 // true geometric length (m)
    r.roadIdx = i;

    let kmh = CLASS_KMH[r.t] || 24;
    if (r.sm) kmh = Math.min(kmh, 20);        // narrow streets crawl
    const lim = kmh / 3.6;

    for (let d = 0; d < 2; d++) {
      const e = 2 * i + d;
      if (d === 1 && r.ow) continue;
      exists[e] = 1;
      edgeLen[e] = r.L;
      limit[e] = lim;
      capDir[e] = r.ow ? r.cap : r.cap / 2;
      if (d === 0) { pts[e] = fwdPts; cum[e] = fwdCum; }
      else {
        const rp = fwdPts.slice().reverse();
        pts[e] = rp;
        cum[e] = fwdCum.map(c => total - c).reverse();
      }
    }
  });

  // Junctions. The source adjacency lists are not trustworthy: a link recorded on one
  // street is often missing on the other, and many links join street ends hundreds of
  // metres apart (T-junctions recorded against the far endpoint). Street ends are merged
  // into junction clusters only when they physically touch, and every street can leave
  // through every other end of its cluster.
  //   end id = 2 * roadIndex + (0: first point, 1: last point)
  const parent = Int32Array.from({ length: nR * 2 }, (_, k) => k);
  const find = k => { while (parent[k] !== k) { parent[k] = parent[parent[k]]; k = parent[k]; } return k; };
  const union = (a, b) => { a = find(a); b = find(b); if (a !== b) parent[a] = b; };
  const endPt = k => { const p = roads[k >> 1].p; return k & 1 ? p[p.length - 1] : p[0]; };
  const gap = (a, b) => Math.hypot((a[0] - b[0]) * M_PER_DEG, (a[1] - b[1]) * M_PER_DEG * Math.cos(a[0] * DEG));
  roads.forEach((r, i) => {
    for (const c of r.ne || []) { const a = 2 * i + 1, b = 2 * c.idx + (c.fwd ? 0 : 1); if (gap(endPt(a), endPt(b)) <= LINK_MAX_M) union(a, b); }
    for (const c of r.ns || []) { const a = 2 * i, b = 2 * c.idx + (c.fwd ? 0 : 1); if (gap(endPt(a), endPt(b)) <= LINK_MAX_M) union(a, b); }
  });
  // ends that touch but were never linked in the source data
  const grid = new Map();
  for (let k = 0; k < nR * 2; k++) {
    const p = endPt(k);
    const cx = Math.floor(p[0] * M_PER_DEG / SNAP_M), cy = Math.floor(p[1] * M_PER_DEG * Math.cos(p[0] * DEG) / SNAP_M);
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) {
      for (const o of grid.get((cx + dx) + ',' + (cy + dy)) || []) if (gap(p, endPt(o)) <= SNAP_M) union(k, o);
    }
    const key = cx + ',' + cy;
    if (!grid.has(key)) grid.set(key, []);
    grid.get(key).push(k);
  }
  const cluster = new Map();
  for (let k = 0; k < nR * 2; k++) {
    const root = find(k);
    if (!cluster.has(root)) cluster.set(root, []);
    cluster.get(root).push(k);
  }

  // successors of each directed edge
  const out = Array.from({ length: nE }, () => []);
  for (let i = 0; i < nR; i++) {
    for (let d = 0; d < 2; d++) {
      const e = 2 * i + d;
      if (!exists[e]) continue;
      const arrivalEnd = d === 0 ? 2 * i + 1 : 2 * i;
      for (const y of cluster.get(find(arrivalEnd))) {
        const j = y >> 1;
        if (j === i || gap(endPt(arrivalEnd), endPt(y)) > JUMP_MAX_M) continue;   // clusters can chain; never jump far
        const e2 = 2 * j + (y & 1 ? 1 : 0);      // leave j from end y: from its start -> dir 0
        if (exists[e2] && !out[e].includes(e2)) out[e].push(e2);
      }
      if (!out[e].length) {                  // dead end: U-turn at the end of the street
        const u = 2 * i + (1 - d);
        if (exists[u]) out[e].push(u);
      }
    }
  }

  // largest strongly connected component (Kosaraju, iterative) - the part of the
  // network that vehicles can actually circulate in
  const main = largestScc(nE, exists, out);

  const net = {
    roads, pois, nR, nE, nStreets: srcRoads.length, exists, edgeLen, limit, pts, cum, capDir, out, main,
    roadOf: e => e >> 1,
    bounds: null,
  };

  // map bounds
  let s = 90, n = -90, w = 180, ea = -180;
  for (const r of roads) for (const p of r.p) {
    if (p[0] < s) s = p[0]; if (p[0] > n) n = p[0];
    if (p[1] < w) w = p[1]; if (p[1] > ea) ea = p[1];
  }
  net.bounds = [[s, w], [n, ea]];

  net.bySrc = new Map();
  roads.forEach((r, i) => { if (!net.bySrc.has(r.src)) net.bySrc.set(r.src, []); net.bySrc.get(r.src).push(i); });
  net.gateways = pickGateways(net);
  attachPoiEdges(net);
  return net;
}

function largestScc(nE, exists, out) {
  const inn = Array.from({ length: nE }, () => []);
  for (let u = 0; u < nE; u++) if (exists[u]) for (const v of out[u]) inn[v].push(u);

  const visited = new Uint8Array(nE);
  const order = [];
  for (let s = 0; s < nE; s++) {
    if (!exists[s] || visited[s]) continue;
    const stack = [[s, 0]];
    visited[s] = 1;
    while (stack.length) {
      const top = stack[stack.length - 1];
      const [u, k] = top;
      if (k < out[u].length) {
        top[1]++;
        const v = out[u][k];
        if (!visited[v]) { visited[v] = 1; stack.push([v, 0]); }
      } else { order.push(u); stack.pop(); }
    }
  }

  const comp = new Int32Array(nE).fill(-1);
  let nc = 0;
  const sizes = [];
  for (let i = order.length - 1; i >= 0; i--) {
    const s = order[i];
    if (comp[s] !== -1) continue;
    let size = 0;
    const stack = [s];
    comp[s] = nc;
    while (stack.length) {
      const u = stack.pop(); size++;
      for (const v of inn[u]) if (comp[v] === -1) { comp[v] = nc; stack.push(v); }
    }
    sizes.push(size); nc++;
  }
  let best = 0;
  sizes.forEach((sz, c) => { if (sz > sizes[best]) best = c; });
  const main = new Uint8Array(nE);
  for (let e = 0; e < nE; e++) if (exists[e] && comp[e] === best) main[e] = 1;
  return main;
}

// Entry points on the edge of the study area for through traffic.
function pickGateways(net) {
  const { roads } = net;
  const arterial = roads.filter(r => r.cap >= 950 &&
    (net.main[2 * r.roadIdx] || net.main[2 * r.roadIdx + 1]));
  const defs = [
    { key: 'south', name: 'South · Parrys / High Court', score: p => -p[0], share: 0.30, icon: '↑' },
    { key: 'north', name: 'North · Tondiarpet / Ennore', score: p => p[0], share: 0.22, icon: '↓' },
    { key: 'west', name: 'West · Mint / Basin Bridge', score: p => -p[1], share: 0.24, icon: '→' },
    { key: 'harbour', name: 'East · Kasimedu Harbour', score: p => p[1] + 0.35 * p[0], share: 0.09, icon: '←' },
  ];
  const used = new Set();
  const gws = [];
  for (const g of defs) {
    // candidate street ends, best-scoring first; keep up to 3 entries at least 120 m apart
    const cands = [];
    for (const r of arterial) for (const end of [0, r.p.length - 1]) cands.push({ r, end, sc: g.score(r.p[end]) });
    cands.sort((a, b) => b.sc - a.sc);
    const entries = [];
    for (const c of cands) {
      if (entries.length >= 3) break;
      if (used.has(c.r.roadIdx)) continue;
      const pt = c.r.p[c.end];
      if (entries.some(q => Math.hypot((q.pt[0] - pt[0]) * M_PER_DEG, (q.pt[1] - pt[1]) * M_PER_DEG * Math.cos(pt[0] * DEG)) < 120)) continue;
      // enter at that end, travelling inward
      let e = 2 * c.r.roadIdx + (c.end === 0 ? 0 : 1);
      if (!net.exists[e] || !net.main[e]) e ^= 1;
      if (!net.exists[e] || !net.main[e]) continue;
      used.add(c.r.roadIdx);
      entries.push({ e, pt });
    }
    if (!entries.length) continue;
    const p = net.pts[entries[0].e][0];
    gws.push({ key: g.key, name: g.name, share: g.share, edge: entries[0].e, edges: entries.map(q => q.e), lat: p[0], lng: p[1], icon: g.icon });
  }
  gws.push({ key: 'local', name: 'Local · all Royapuram wards', share: 0.15, edge: null, edges: [], icon: '◎' });
  return gws;
}

function attachPoiEdges(net) {
  const { roads, pois } = net;
  const bySrc = new Map();
  roads.forEach((r, i) => { if (!bySrc.has(r.src)) bySrc.set(r.src, []); bySrc.get(r.src).push(i); });
  // midpoints of every circulating road for nearest-road fallback
  const mids = [];
  roads.forEach((r, i) => {
    if (!(net.main[2 * i] || net.main[2 * i + 1])) return;
    const m = r.p[Math.floor(r.p.length / 2)];
    mids.push([i, m[0], m[1]]);
  });
  for (const p of pois) {
    const edges = [];
    for (const s of p.nearest_roads || []) {
      for (const ri of bySrc.get(s) || []) {
        for (let d = 0; d < 2; d++) {
          const e = 2 * ri + d;
          if (net.exists[e] && net.main[e]) edges.push(e);
        }
      }
    }
    if (!edges.length) {
      let best = null, bd = Infinity;
      for (const [i, la, ln] of mids) {
        const d = Math.hypot(la - p.lat, (ln - p.lng) * Math.cos(p.lat * DEG));
        if (d < bd) { bd = d; best = i; }
      }
      for (let d = 0; d < 2; d++) { const e = 2 * best + d; if (net.exists[e] && net.main[e]) edges.push(e); }
    }
    p.edges = edges;
    p.road = roads[edges.length ? edges[0] >> 1 : 0];
  }
}

// Position and compass heading at distance s (m) along directed edge e.
const _out = [0, 0, 0];
export function pointAt(net, e, s) {
  const pts = net.pts[e], cum = net.cum[e];
  const L = cum[cum.length - 1];
  if (s < 0) s = 0; else if (s > L) s = L;
  let k = 1;
  while (k < cum.length - 1 && cum[k] < s) k++;
  const a = pts[k - 1], b = pts[k];
  const seg = cum[k] - cum[k - 1] || 1;
  const t = (s - cum[k - 1]) / seg;
  _out[0] = a[0] + (b[0] - a[0]) * t;
  _out[1] = a[1] + (b[1] - a[1]) * t;
  const dy = b[0] - a[0], dx = (b[1] - a[1]) * Math.cos(a[0] * DEG);
  _out[2] = Math.atan2(dy, dx);              // radians, 0 = east, CCW (math convention)
  return _out;
}

export function freeFlowTime(net, e) { return net.edgeLen[e] / net.limit[e]; }
