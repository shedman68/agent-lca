"""Build a self-contained HTML page: hourly CO2 heatmaps (CH consumption mix, DE) + job-shift table.

Usage: python build_chart.py <profile_csv> <shift_csv> <out_html>
"""
import json
import sys

import pandas as pd

prof = pd.read_csv(sys.argv[1])
shift = pd.read_csv(sys.argv[2])
MONTHS = [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8]
MNAME = {1: "Jan 2026", 2: "Feb 2026", 3: "Mar 2026", 4: "Apr 2026", 5: "May 2026", 6: "Jun 2026", 7: "Jul 2026",
         8: "Aug 2026", 9: "Sep 2025", 10: "Oct 2025", 11: "Nov 2025", 12: "Dec 2025"}


def grid(col):
    p = prof.pivot(index="month", columns="hour", values=col).reindex(MONTHS)
    return [[None if pd.isna(v) else round(float(v), 1) for v in row] for row in p.values]


data = {
    "months": [MNAME[m] for m in MONTHS],
    "ch": grid("CH"), "de": grid("DE"),
    "ch_mean": round(float(prof["CH"].mean()), 1), "de_mean": round(float(prof["DE"].mean()), 1),
    "jobs": shift.dropna(subset=["g_per_kwh_now"]).sort_values("reduction_pct", ascending=False).to_dict("records"),
    "excluded": shift[shift["g_per_kwh_now"].isna()][["job", "resource", "note"]].to_dict("records"),
}

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hourly CO2 of electricity – Switzerland and Germany (Sep 2025 – Aug 2026)</title>
<style>
.viz-root {
  color-scheme: light;
  --page: #f9f9f7; --surface-1: #fcfcfb; --text-primary: #0b0b0b; --text-secondary: #52514e; --muted: #898781;
  --grid: #e1e0d9; --border: rgba(11,11,11,0.10); --good-text: #006300;
  --ramp: "#cde2fb,#b7d3f6,#9ec5f4,#86b6ef,#6da7ec,#5598e7,#3987e5,#2a78d6,#256abf,#1c5cab,#184f95,#104281,#0d366b";
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) .viz-root {
    color-scheme: dark;
    --page: #0d0d0d; --surface-1: #1a1a19; --text-primary: #f0efec; --text-secondary: #c3c2b7; --muted: #898781;
    --grid: #2c2c2a; --border: rgba(255,255,255,0.10); --good-text: #0ca30c;
    --ramp: "#0d366b,#104281,#184f95,#1c5cab,#256abf,#2a78d6,#3987e5,#5598e7,#6da7ec,#86b6ef,#9ec5f4,#b7d3f6,#cde2fb";
  }
}
:root[data-theme="dark"] .viz-root {
  color-scheme: dark;
  --page: #0d0d0d; --surface-1: #1a1a19; --text-primary: #f0efec; --text-secondary: #c3c2b7; --muted: #898781;
  --grid: #2c2c2a; --border: rgba(255,255,255,0.10); --good-text: #0ca30c;
  --ramp: "#0d366b,#104281,#184f95,#1c5cab,#256abf,#2a78d6,#3987e5,#5598e7,#6da7ec,#86b6ef,#9ec5f4,#b7d3f6,#cde2fb";
}
body { margin: 0; }
.viz-root { background: var(--page); color: var(--text-primary); font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  padding: 24px; min-height: 100vh; box-sizing: border-box; }
h1 { font-size: 20px; margin: 0 0 4px; }
.sub { color: var(--text-secondary); font-size: 14px; margin: 0 0 20px; max-width: 880px; line-height: 1.45; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(520px, 1fr)); gap: 16px; }
.card { background: var(--surface-1); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
.card h2 { font-size: 15px; margin: 0 0 2px; }
.card .note { color: var(--text-secondary); font-size: 13px; margin: 0 0 12px; }
svg text { font-size: 11px; fill: var(--muted); font-variant-numeric: tabular-nums; }
.cell:focus { outline: 2px solid var(--text-primary); outline-offset: -1px; }
.legend { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--text-secondary); margin-top: 8px; }
.legend .bar { height: 10px; width: 180px; border-radius: 4px; }
.tip { position: fixed; pointer-events: none; background: var(--surface-1); border: 1px solid var(--border); border-radius: 6px;
  padding: 6px 10px; font-size: 12px; color: var(--text-secondary); box-shadow: 0 2px 8px rgba(0,0,0,0.15); display: none; }
.tip strong { display: block; color: var(--text-primary); font-size: 14px; }
table { border-collapse: collapse; font-size: 13px; width: 100%; }
th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--grid); }
th { color: var(--text-secondary); font-weight: 600; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
.good { color: var(--good-text); font-weight: 600; }
details { margin-top: 16px; }
summary { cursor: pointer; color: var(--text-secondary); font-size: 13px; }
.wide { grid-column: 1 / -1; }
.caveat { font-size: 13px; color: var(--text-secondary); line-height: 1.45; }
</style>
</head>
<body>
<div class="viz-root">
  <h1>When is electricity cleanest? Hourly CO2, baseline year Sep 2025 – Aug 2026</h1>
  <p class="sub">Average g CO2-eq per kWh for each month and hour of the day (local time).
    Switzerland is the <b>consumption mix including imports</b>, the same basis as our grid factor. Germany is the generation mix.
    Source: Energy-Charts API (Fraunhofer ISE), our calculation. Values are indicative and are not used in the baseline CO2, which uses annual factors.</p>
  <div class="cards">
    <div class="card"><h2>Switzerland (Zurich) – dp-prod, logs, archive</h2>
      <p class="note" id="ch-note"></p><div id="ch"></div></div>
    <div class="card"><h2>Germany (Frankfurt) – dp-dev</h2>
      <p class="note" id="de-note"></p><div id="de"></div></div>
    <div class="card wide"><h2>Flexible jobs: same work, lower CO2 by moving the start within the allowed window</h2>
      <p class="note">Average CO2 per kWh during the job, now vs the best start hour inside the job's own window. Fixed and protected jobs are not moved.</p>
      <table id="jobs"><thead><tr><th>Job</th><th>Resource</th><th>Allowed window</th><th class="num">Now starts</th>
        <th class="num">Best start</th><th class="num">g/kWh now</th><th class="num">g/kWh best</th><th class="num">Change</th></tr></thead><tbody></tbody></table>
      <p class="caveat" id="excluded"></p>
      <p class="caveat"><b>Caveat:</b> moving a job only saves CO2 if the cluster actually uses less power when the job is not running
        (auto-scaling or pause). dp-prod and dp-dev currently run around the clock, so the saving only becomes real together with a schedule or auto-pause measure.</p>
      <p class="caveat"><b>Protection windows:</b> on dp-prod, jobs keep their current start on the last 3 working days of each month and at year-end close
        (finance closing, T-1029), so nothing runs alongside the month-end close. dp-dev keeps quarterly training free on days 1–3 of Jan, Apr, Jul and Oct (T-1053).
        "Best start" is the most frequent best hour across months; the CO2 change uses the best hour of each month.</p>
    </div>
  </div>
  <details><summary>Table view: all hourly values (g CO2-eq/kWh)</summary><div id="table"></div></details>
  <div class="tip" id="tip" role="status" aria-live="polite"></div>
</div>
<script>
const D = __DATA__;
const root = document.querySelector('.viz-root');
function ramp() { return getComputedStyle(root).getPropertyValue('--ramp').replace(/["\s]/g, '').split(','); }
function hex2rgb(h) { return [1,3,5].map(i => parseInt(h.slice(i, i + 2), 16)); }
function colorAt(t, r) {
  const x = Math.max(0, Math.min(1, t)) * (r.length - 1), i = Math.floor(x), f = x - i;
  const a = hex2rgb(r[i]), b = hex2rgb(r[Math.min(i + 1, r.length - 1)]);
  return 'rgb(' + a.map((v, k) => Math.round(v + (b[k] - v) * f)).join(',') + ')';
}
const tip = document.getElementById('tip');
function showTip(ev, value, label) {
  tip.textContent = '';
  const s = document.createElement('strong'); s.textContent = value + ' g/kWh'; tip.appendChild(s);
  tip.appendChild(document.createTextNode(label));
  tip.style.display = 'block';
  const r = ev.target.getBoundingClientRect();
  const x = ev.clientX || (r.left + r.width / 2), y = ev.clientY || r.top;
  tip.style.left = Math.min(x + 12, window.innerWidth - 200) + 'px'; tip.style.top = (y + 12) + 'px';
}
function hideTip() { tip.style.display = 'none'; }
const NS = 'http://www.w3.org/2000/svg';
function heat(id, g, country) {
  const el = document.getElementById(id); el.textContent = '';
  const vals = g.flat().filter(v => v !== null), lo = Math.min(...vals), hi = Math.max(...vals), r = ramp();
  const cw = 18, ch = 18, gap = 2, left = 64, top = 4, W = left + 24 * (cw + gap) + 16, H = top + 12 * (ch + gap) + 20;
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H); svg.setAttribute('width', '100%');
  svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', country + ' hourly CO2 heatmap, ' + lo + ' to ' + hi + ' g per kWh');
  g.forEach((row, mi) => {
    const t = document.createElementNS(NS, 'text'); t.setAttribute('x', left - 8); t.setAttribute('y', top + mi * (ch + gap) + 13);
    t.setAttribute('text-anchor', 'end'); t.textContent = D.months[mi]; svg.appendChild(t);
    row.forEach((v, h) => {
      const c = document.createElementNS(NS, 'rect');
      c.setAttribute('x', left + h * (cw + gap)); c.setAttribute('y', top + mi * (ch + gap));
      c.setAttribute('width', cw); c.setAttribute('height', ch); c.setAttribute('rx', 2);
      c.setAttribute('fill', v === null ? 'none' : colorAt((v - lo) / (hi - lo), r));
      c.setAttribute('class', 'cell'); c.setAttribute('tabindex', '0');
      const label = country + ' · ' + D.months[mi] + ' · ' + String(h).padStart(2, '0') + ':00–' + String(h + 1).padStart(2, '0') + ':00';
      c.setAttribute('aria-label', label + ': ' + v + ' g per kWh');
      c.addEventListener('pointermove', e => showTip(e, v, label)); c.addEventListener('pointerleave', hideTip);
      c.addEventListener('focus', e => showTip(e, v, label)); c.addEventListener('blur', hideTip);
      svg.appendChild(c);
    });
  });
  [0, 6, 12, 18, 23].forEach(h => {
    const t = document.createElementNS(NS, 'text'); t.setAttribute('x', left + h * (cw + gap) + cw / 2);
    t.setAttribute('y', H - 4); t.setAttribute('text-anchor', 'middle'); t.textContent = String(h).padStart(2, '0') + ':00'; svg.appendChild(t);
  });
  el.appendChild(svg);
  const lg = document.createElement('div'); lg.className = 'legend';
  const a = document.createElement('span'); a.textContent = Math.round(lo) + ' g/kWh';
  const bar = document.createElement('span'); bar.className = 'bar';
  bar.style.background = 'linear-gradient(90deg,' + r.join(',') + ')';
  const b = document.createElement('span'); b.textContent = Math.round(hi) + ' g/kWh';
  lg.append(a, bar, b); el.appendChild(lg);
  return [lo, hi];
}
function render() {
  const [cl, chh] = heat('ch', D.ch, 'Switzerland'); const [dl, dh] = heat('de', D.de, 'Germany');
  document.getElementById('ch-note').textContent = 'Range ' + Math.round(cl) + '–' + Math.round(chh) + ' g/kWh, mean ' + Math.round(D.ch_mean) + '. Colour scale below the chart.';
  document.getElementById('de-note').textContent = 'Range ' + Math.round(dl) + '–' + Math.round(dh) + ' g/kWh, mean ' + Math.round(D.de_mean) + '. Own scale; Germany is about 4x Switzerland.';
}
render();
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', render);
const tb = document.querySelector('#jobs tbody');
D.jobs.forEach(j => {
  const tr = document.createElement('tr');
  const cells = [j.job, j.resource + ' (' + j.grid + ')', j.window.replace('flexible: ', ''), j.current_start, j.best_start_typical,
    j.g_per_kwh_now, j.g_per_kwh_best, '−' + j.reduction_pct + ' %'];
  cells.forEach((v, i) => { const td = document.createElement('td'); td.textContent = v; if (i >= 3) td.className = 'num'; if (i === 7) td.classList.add('good'); tr.appendChild(td); });
  tb.appendChild(tr);
});
document.getElementById('excluded').textContent = D.excluded.length ? 'Not moved: ' + D.excluded.map(e => e.job + ' on ' + e.resource + ' – ' + e.note).join('; ') + '.' : '';
const tw = document.getElementById('table');
[['Switzerland (consumption mix)', D.ch], ['Germany', D.de]].forEach(([name, g]) => {
  const h = document.createElement('h3'); h.textContent = name; h.style.fontSize = '14px'; tw.appendChild(h);
  const t = document.createElement('table'); const hr = document.createElement('tr');
  ['Month'].concat([...Array(24).keys()].map(x => String(x).padStart(2, '0'))).forEach((x, i) => { const th = document.createElement('th'); th.textContent = x; if (i) th.className = 'num'; hr.appendChild(th); });
  t.appendChild(hr);
  g.forEach((row, mi) => { const tr = document.createElement('tr'); const td0 = document.createElement('td'); td0.textContent = D.months[mi]; tr.appendChild(td0);
    row.forEach(v => { const td = document.createElement('td'); td.className = 'num'; td.textContent = v === null ? '–' : Math.round(v); tr.appendChild(td); }); t.appendChild(tr); });
  tw.appendChild(t);
});
</script>
</body>
</html>
"""
open(sys.argv[3], "w", encoding="utf-8").write(HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False)))
print("written", sys.argv[3])

