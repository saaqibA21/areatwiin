// Monsoon rain and street flooding.
//
// Rain raises a water level (0..~1.2) that scales each low-lying street's surveyed
// stagnation depth. Deep water slows traffic and, past a threshold, closes the street.

export const WATER_SPOTS = [
  { id: 'stanley',  name: 'Stanley Subway Underpass',     lat: 13.0992, lng: 80.2872, elev: '-3.8 m', baseDepth: 75, radius: 65, desc: 'Depressed rail subway. Impassable in heavy rain; runoff cannot escape.' },
  { id: 'bridge',   name: 'Royapuram ROB Descent Dip',    lat: 13.1034, lng: 80.2936, elev: '-2.2 m', baseDepth: 45, radius: 55, desc: 'Foot of the bridge curve before Kamarajar Salai. Water pools from the approach slope.' },
  { id: 'madha',    name: 'S. Madha Church St Basin',     lat: 13.1068, lng: 80.2946, elev: '-2.5 m', baseDepth: 50, radius: 50, desc: 'Residential low-lying bowl near the cemetery with tide-locked drains.' },
  { id: 'harbour',  name: 'Kasimedu Wharf Gate Slipway',  lat: 13.1128, lng: 80.2982, elev: '-2.8 m', baseDepth: 40, radius: 60, desc: 'Coastal depression where fish-auction runoff stagnates.' },
  { id: 'kalman',   name: 'Kalmandapam Market Basin',     lat: 13.1045, lng: 80.2915, elev: '-2.0 m', baseDepth: 42, radius: 45, desc: 'Low market-street intersection prone to overflow.' },
  { id: 'walltax',  name: 'Wall Tax / Basin Bridge Line', lat: 13.0980, lng: 80.2830, elev: '-3.0 m', baseDepth: 60, radius: 70, desc: 'Low rail-boundary corridor with heavy waterlogging.' },
];

export const INTENSITY = [
  { label: 'Dry',        mm: 0,  slow: 1.00 },
  { label: 'Light shower', mm: 8,  slow: 0.90 },
  { label: 'Moderate rain', mm: 25, slow: 0.78 },
  { label: 'Cyclonic downpour', mm: 60, slow: 0.62 },
];

export const CLOSE_CM = 45;     // street is impassable at this depth
const SLOW_BANDS = [[35, 0.22], [25, 0.38], [12, 0.7]];

export class Weather {
  constructor(net, sim, onClosuresChanged) {
    this.net = net; this.sim = sim; this.onClosures = onClosuresChanged;
    this.on = false;
    this.intensity = 1;
    this.level = 0;
    this.autoClose = true;
    this.floodClosed = new Set();
    this.maxDepth = 0;
    this.floodedRoads = 0;
    this.lowRoads = net.roads.filter(r => r.low && r.water_depth_cm > 0);
  }

  get label() { return this.on ? INTENSITY[this.intensity].label : 'Dry'; }
  get levelCap() { return 0.6 + 0.2 * this.intensity; }
  spotDepth(spot) { return Math.round(spot.baseDepth * this.level); }
  roadDepth(r) { return r.low ? Math.round(r.water_depth_cm * this.level) : 0; }

  /** advance by dt simulated minutes */
  update(dtMin) {
    const before = this.level;
    if (this.on) this.level = Math.min(this.levelCap, this.level + 0.08 * this.intensity * dtMin);
    else this.level = Math.max(0, this.level - 0.05 * dtMin);
    if (this.level === before && !this._dirty) return;
    this._dirty = false;

    this.sim.rainFactor = this.on ? INTENSITY[this.intensity].slow : 1;
    const closed = new Set();
    let maxD = 0, flooded = 0;
    for (const r of this.lowRoads) {
      const d = this.roadDepth(r);
      if (d > maxD) maxD = d;
      if (d >= 12) flooded++;
      let f = 1;
      for (const [cm, k] of SLOW_BANDS) if (d >= cm) { f = k; break; }
      this.sim.slow[r.roadIdx] = f;
      if (this.autoClose && d >= CLOSE_CM) closed.add(r.roadIdx);
    }
    for (const s of WATER_SPOTS) maxD = Math.max(maxD, this.spotDepth(s));
    this.maxDepth = maxD;
    this.floodedRoads = flooded;

    const same = closed.size === this.floodClosed.size && [...closed].every(x => this.floodClosed.has(x));
    if (!same) { this.floodClosed = closed; this.onClosures(); }
  }

  poke() { this._dirty = true; }
}
