// Run with: node tests/logic.test.mjs
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { buildNetwork, pointAt } from '../js/network.js';
import { Forecaster } from '../js/forecast.js';
import { Sim } from '../js/sim.js';
import { shortest, tracePath } from '../js/router.js';

const roads = JSON.parse(readFileSync(new URL('../data/roads.json', import.meta.url)));
const pois = JSON.parse(readFileSync(new URL('../data/pois.json', import.meta.url)));
const net = buildNetwork(roads, pois);

let mainCount = 0; for (let e = 0; e < net.nE; e++) mainCount += net.main[e];
console.log('streets', net.nStreets, 'segments', net.nR, 'edges', net.exists.reduce((a, b) => a + b, 0), 'circulating edges', mainCount);
console.log('gateways', net.gateways.map(g => `${g.key}:${g.edge} (${net.roads[g.edge >> 1]?.n})`).join(' | '));
assert.ok(mainCount > net.nR * 1.5, 'a large circulating core exists');
assert.ok(net.gateways.length >= 4);
for (const p of pois) assert.ok(p.edges.length > 0, 'poi has edges: ' + p.name);

// no teleporting: every connection joins an end of one street to a touching end of the next
{
  const M = 111320, cos = Math.cos(13.1 * Math.PI / 180);
  let worst = 0;
  for (let u = 0; u < net.nE; u++) {
    if (!net.exists[u]) continue;
    const a = net.pts[u].at(-1);
    for (const v of net.out[u]) {
      if (v >> 1 === u >> 1) continue;               // U-turn at a dead end
      const b = net.pts[v][0];
      worst = Math.max(worst, Math.hypot((a[0] - b[0]) * M, (a[1] - b[1]) * M * cos));
    }
  }
  console.log('longest junction jump (m):', worst.toFixed(1));
  assert.ok(worst <= 30, 'junction connections are physically adjacent');
  assert.ok(net.nR > net.nStreets, 'T-junction splitting produced extra segments');
}

// pointAt endpoints
{ const R = net.roads, e = 2 * 5; const a = pointAt(net, e, 0).slice(); const b = pointAt(net, e, net.edgeLen[e]).slice();
  assert.ok(Math.abs(a[0] - R[5].p[0][0]) < 1e-6); assert.ok(Math.abs(b[0] - R[5].p.at(-1)[0]) < 1e-6);
  const r = pointAt(net, e + 1, 0); assert.ok(Math.abs(r[0] - R[5].p.at(-1)[0]) < 1e-6); }

// every gateway reaches every poi
for (const g of net.gateways) { if (g.edge == null) continue;
  const res = shortest(net, [g.edge], e => net.edgeLen[e] / net.limit[e]);
  for (const p of pois) assert.ok(p.edges.some(e => res.dist[e] < Infinity), `${g.key} -> ${p.name}`); }

// forecast
let t = performance.now();
const fc = new Forecaster(net);
console.log('forecast init ms', (performance.now() - t).toFixed(0), 'scale', fc.scale.toFixed(3));
const bvc = [...fc.baseline.vc].sort((a, b) => b - a);
console.log('baseline top vc', bvc.slice(0, 5).map(x => x.toFixed(2)).join(','), 'served', fc.baseline.served.toFixed(0), 'unserved', fc.baseline.unserved.toFixed(0));
// busiest road
let busiest = 0; fc.baseline.flowRoad.forEach((f, i) => { if (f > fc.baseline.flowRoad[busiest]) busiest = i; });
t = performance.now();
const scen = fc.run(new Set([busiest]));
const cmp = fc.compare(scen);
console.log('close', net.roads[busiest].n, 'flow', fc.baseline.flowRoad[busiest].toFixed(0), 'run ms', (performance.now() - t).toFixed(0));
console.log(JSON.stringify({ ...cmp, top: cmp.top.map(r => [r.name, r.vcBase.toFixed(2), r.vcScen.toFixed(2), r.surge.toFixed(0)]) }));
assert.ok(cmp.displaced > 0);
assert.ok(scen.vht >= fc.baseline.vht - 1e-6, 'closing a road cannot reduce total travel time');
assert.equal(scen.flowRoad[busiest], 0);

// simulation
const sim = new Sim(net);
sim.targetFleet = 80;
t = performance.now();
for (let i = 0; i < 3000; i++) sim.step(0.1);        // 300 s
console.log('sim 300s ms', (performance.now() - t).toFixed(0), JSON.stringify(sim.stats), 'arrived', sim.arrivedTotal, 'stranded', sim.strandedTotal, 'n', sim.vehicles.length);
assert.ok(sim.vehicles.length >= 60);
assert.ok(sim.arrivedTotal > 5, 'vehicles reach destinations');
// no overlaps on the same edge (rear-end collisions)
let overlaps = 0;
for (const e of sim.touched) { const l = sim.lists[e]; for (let i = 1; i < l.length; i++) if (l[i - 1].s - l[i - 1].len - l[i].s < -0.5) overlaps++; }
console.log('overlaps', overlaps, 'of', sim.vehicles.length);
assert.ok(overlaps <= 3, 'car-following keeps vehicles from overlapping');

// closure re-routes and nobody drives through
const busyEdges = sim.touched.slice().sort((a, b) => sim.lists[b].length - sim.lists[a].length)[0] >> 1;
sim.setClosed(new Set([busyEdges]));
for (let i = 0; i < 1200; i++) sim.step(0.1);
// (vehicles with no alternative route are legitimately held at the barrier and keep retrying)
const thru = sim.vehicles.filter(v => !v.failAt && v.route.slice(v.ri + 1).some(e => e >> 1 === busyEdges)).length;
console.log('closed', net.roads[busyEdges].n, 'vehicles still routed through:', thru, 'stats', JSON.stringify(sim.stats));
assert.equal(thru, 0);
console.log('OK');
process.exit(0);
