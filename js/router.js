// Shortest-path search over the directed edge graph (binary-heap Dijkstra).

class Heap {
  constructor() { this.k = []; this.v = []; }
  get size() { return this.k.length; }
  push(key, val) {
    const k = this.k, v = this.v;
    let i = k.length;
    k.push(key); v.push(val);
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (k[p] <= key) break;
      k[i] = k[p]; v[i] = v[p]; i = p;
    }
    k[i] = key; v[i] = val;
  }
  pop() {
    const k = this.k, v = this.v;
    const topV = v[0];
    const lastK = k.pop(), lastV = v.pop();
    const n = k.length;
    if (n) {
      let i = 0;
      for (;;) {
        let c = 2 * i + 1;
        if (c >= n) break;
        if (c + 1 < n && k[c + 1] < k[c]) c++;
        if (k[c] >= lastK) break;
        k[i] = k[c]; v[i] = v[c]; i = c;
      }
      k[i] = lastK; v[i] = lastV;
    }
    return topV;
  }
}

/**
 * @param net      network from buildNetwork
 * @param sources  edge ids to start from
 * @param cost     (edge) => seconds to traverse it, or Infinity if not allowed
 * @param stopAt   optional Set of edge ids; search ends at the first one settled
 * @returns {dist, prev, hit}
 */
export function shortest(net, sources, cost, stopAt) {
  const dist = new Float64Array(net.nE).fill(Infinity);
  const prev = new Int32Array(net.nE).fill(-1);
  const done = new Uint8Array(net.nE);
  const heap = new Heap();
  for (const s of sources) {
    const c = cost(s);
    if (c === Infinity) continue;
    dist[s] = c;
    heap.push(c, s);
  }
  let hit = -1;
  const out = net.out;
  while (heap.size) {
    const u = heap.pop();
    if (done[u]) continue;
    done[u] = 1;
    if (stopAt && stopAt.has(u)) { hit = u; break; }
    const du = dist[u];
    const nb = out[u];
    for (let i = 0; i < nb.length; i++) {
      const v = nb[i];
      if (done[v]) continue;
      const c = cost(v);
      if (c === Infinity) continue;
      const nd = du + c;
      if (nd < dist[v]) { dist[v] = nd; prev[v] = u; heap.push(nd, v); }
    }
  }
  return { dist, prev, hit };
}

export function tracePath(prev, e) {
  const path = [];
  for (let u = e; u !== -1; u = prev[u]) path.push(u);
  return path.reverse();
}
