// Tiny dependency-free canvas charts (line/area, bars, donut) with HiDPI support.

function setup(canvas) {
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (!w || !h) return null;
  if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
    canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr);
  }
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, w, h);
  return { ctx, w, h };
}

const css = (name, fb) => getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fb;

/** series: [{data:number[], color, fill?:bool}], opts: {min,max,unit,label,format} */
export function lineChart(canvas, series, opts = {}) {
  const s = setup(canvas); if (!s) return;
  const { ctx, w, h } = s;
  const padL = 30, padR = 6, padT = 6, padB = 14;
  const iw = w - padL - padR, ih = h - padT - padB;
  let min = opts.min ?? 0, max = opts.max;
  if (max == null) { max = 0; for (const se of series) for (const v of se.data) if (v > max) max = v; max = Math.max(max * 1.15, 1); }
  const grid = css('--line', 'rgba(255,255,255,.1)'), muted = css('--muted', '#94a3b8');

  ctx.font = '10px system-ui, sans-serif';
  ctx.fillStyle = muted; ctx.strokeStyle = grid; ctx.lineWidth = 1;
  ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
  for (let i = 0; i <= 2; i++) {
    const v = min + (max - min) * (i / 2);
    const y = padT + ih - (ih * i) / 2;
    ctx.beginPath(); ctx.moveTo(padL, y + .5); ctx.lineTo(w - padR, y + .5); ctx.stroke();
    ctx.fillText((opts.format ? opts.format(v) : Math.round(v)) + '', padL - 5, y);
  }
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  if (opts.xLabel) { ctx.fillText(opts.xLabel[0], padL, h - 2); ctx.textAlign = 'right'; ctx.fillText(opts.xLabel[1], w - padR, h - 2); }

  for (const se of series) {
    const d = se.data; if (d.length < 2) continue;
    const n = opts.points || d.length;
    const x = i => padL + (iw * (i + (n - d.length))) / (n - 1);
    const y = v => padT + ih - ih * Math.min(1, Math.max(0, (v - min) / (max - min || 1)));
    ctx.beginPath();
    d.forEach((v, i) => (i ? ctx.lineTo(x(i), y(v)) : ctx.moveTo(x(i), y(v))));
    if (se.fill) {
      ctx.save();
      ctx.lineTo(x(d.length - 1), padT + ih); ctx.lineTo(x(0), padT + ih); ctx.closePath();
      const g = ctx.createLinearGradient(0, padT, 0, padT + ih);
      g.addColorStop(0, se.color + '55'); g.addColorStop(1, se.color + '00');
      ctx.fillStyle = g; ctx.fill(); ctx.restore();
      ctx.beginPath();
      d.forEach((v, i) => (i ? ctx.lineTo(x(i), y(v)) : ctx.moveTo(x(i), y(v))));
    }
    ctx.strokeStyle = se.color; ctx.lineWidth = 1.8; ctx.lineJoin = 'round'; ctx.stroke();
  }

  if (opts.marker != null && series[0] && series[0].data.length > 1) {   // vertical "now" marker
    const d = series[0].data, f = Math.min(1, Math.max(0, opts.marker));
    const mx = padL + iw * f;
    const idx = f * (d.length - 1), i0 = Math.floor(idx), i1 = Math.min(d.length - 1, i0 + 1);
    const val = d[i0] + (d[i1] - d[i0]) * (idx - i0);
    const my = padT + ih - ih * Math.min(1, Math.max(0, (val - min) / (max - min || 1)));
    ctx.save(); ctx.setLineDash([3, 3]); ctx.strokeStyle = muted; ctx.beginPath(); ctx.moveTo(mx, padT); ctx.lineTo(mx, padT + ih); ctx.stroke(); ctx.restore();
    ctx.fillStyle = series[0].color; ctx.beginPath(); ctx.arc(mx, my, 4, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = css('--solid', '#fff'); ctx.lineWidth = 2; ctx.stroke();
  }
}

/** bars: [{label, value, color}] vertical, opts: {max, format} */
export function barChart(canvas, bars, opts = {}) {
  const s = setup(canvas); if (!s) return;
  const { ctx, w, h } = s;
  const padB = 16, padT = 14;
  const max = opts.max ?? Math.max(1, ...bars.map(b => b.value)) * 1.1;
  const bw = w / bars.length;
  const muted = css('--muted', '#94a3b8'), text = css('--text', '#e2e8f0');
  ctx.font = '10px system-ui, sans-serif'; ctx.textAlign = 'center';
  bars.forEach((b, i) => {
    const bh = (h - padB - padT) * (b.value / max);
    const x = i * bw + bw * 0.18, ww = bw * 0.64, y = h - padB - bh;
    ctx.fillStyle = b.color;
    const r = Math.min(4, ww / 2, bh / 2);
    ctx.beginPath();
    ctx.moveTo(x, h - padB); ctx.lineTo(x, y + r); ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.lineTo(x + ww - r, y); ctx.quadraticCurveTo(x + ww, y, x + ww, y + r); ctx.lineTo(x + ww, h - padB);
    ctx.closePath(); ctx.fill();
    ctx.fillStyle = text; ctx.fillText(opts.format ? opts.format(b.value) : b.value, x + ww / 2, y - 3);
    ctx.fillStyle = muted; ctx.fillText(b.label, x + ww / 2, h - 3);
  });
}

/** donut: [{label, value, color}] */
export function donut(canvas, parts, opts = {}) {
  const s = setup(canvas); if (!s) return;
  const { ctx, w, h } = s;
  const total = parts.reduce((a, p) => a + p.value, 0) || 1;
  const r = Math.min(w, h) / 2 - 3, cx = w / 2, cy = h / 2, inner = r * 0.64;
  let a0 = -Math.PI / 2;
  for (const p of parts) {
    const a1 = a0 + (p.value / total) * Math.PI * 2;
    if (p.value > 0) {
      ctx.beginPath(); ctx.arc(cx, cy, r, a0, a1); ctx.arc(cx, cy, inner, a1, a0, true); ctx.closePath();
      ctx.fillStyle = p.color; ctx.fill();
    }
    a0 = a1;
  }
  ctx.fillStyle = css('--text', '#e2e8f0'); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = '700 17px system-ui, sans-serif'; ctx.fillText(opts.center ?? total, cx, cy - 4);
  ctx.fillStyle = css('--muted', '#94a3b8'); ctx.font = '9px system-ui, sans-serif'; ctx.fillText(opts.sub ?? '', cx, cy + 10);
}

/** Half-circle gauge 0..max */
export function gauge(canvas, value, max, color, label) {
  const s = setup(canvas); if (!s) return;
  const { ctx, w, h } = s;
  const r = Math.min(w / 2, h) - 8, cx = w / 2, cy = h - 6;
  ctx.lineWidth = 9; ctx.lineCap = 'round';
  ctx.strokeStyle = css('--line', 'rgba(255,255,255,.12)');
  ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI, 0); ctx.stroke();
  ctx.strokeStyle = color;
  ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI, Math.PI + Math.PI * Math.min(1, value / max)); ctx.stroke();
  ctx.fillStyle = css('--text', '#e2e8f0'); ctx.textAlign = 'center';
  ctx.font = '700 22px system-ui, sans-serif'; ctx.fillText(Math.round(value), cx, cy - 14);
  ctx.fillStyle = css('--muted', '#94a3b8'); ctx.font = '10px system-ui, sans-serif'; ctx.fillText(label, cx, cy - 1);
}
