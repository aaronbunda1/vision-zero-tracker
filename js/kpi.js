// KPI panel: monthly deaths & injuries from NYC Open Data (Socrata h9gi-nx95),
// rendered as trailing-12-month trend lines with a plan-announcement marker.

const DATASET = 'https://data.cityofnewyork.us/resource/h9gi-nx95.json';
const SNAPSHOT = 'data/kpi-snapshot.json';
const ANNOUNCED = '2026-09'; // plan announcement month (marker)
const PROVISIONAL_MONTHS = 3; // NYPD reporting lag

const SERIES = [
  { key: 'ped', label: 'Pedestrians', color: 'var(--series-1)' },
  { key: 'cyc', label: 'Cyclists', color: 'var(--series-2)' },
  { key: 'mot', label: 'Motorists', color: 'var(--series-3)' },
];

const soql =
  '$select=date_trunc_ym(crash_date) as month,' +
  'sum(number_of_persons_killed) as killed,' +
  'sum(number_of_pedestrians_killed) as ped_killed,' +
  'sum(number_of_cyclist_killed) as cyc_killed,' +
  'sum(number_of_motorist_killed) as mot_killed,' +
  'sum(number_of_persons_injured) as injured,' +
  'sum(number_of_pedestrians_injured) as ped_injured,' +
  'sum(number_of_cyclist_injured) as cyc_injured,' +
  'sum(number_of_motorist_injured) as mot_injured' +
  "&$where=crash_date >= '2016-01-01'" +
  '&$group=month&$order=month&$limit=200';

export async function initKpi() {
  const statusEl = document.querySelector('#kpi-status');
  let rows, live = true;
  try {
    const res = await fetch(`${DATASET}?${encodeURI(soql)}`);
    if (!res.ok) throw new Error(`API ${res.status}`);
    rows = await res.json();
  } catch (e) {
    live = false;
    try {
      rows = await fetch(SNAPSHOT).then((r) => r.json());
    } catch {
      statusEl.textContent = 'Could not load collision data (API unreachable and no local snapshot). Run scripts/fetch_kpi.sh to cache a snapshot.';
      return;
    }
  }
  const months = normalize(rows);
  statusEl.textContent = live
    ? `Live from NYC Open Data · data through ${months.at(-1).month}`
    : `Offline — showing cached snapshot through ${months.at(-1).month} (run scripts/fetch_kpi.sh to refresh)`;
  render(months);
}

function normalize(rows) {
  const n = (v) => Number(v || 0);
  const months = rows
    .map((r) => ({
      month: r.month.slice(0, 7),
      killed: n(r.killed), ped_killed: n(r.ped_killed), cyc_killed: n(r.cyc_killed), mot_killed: n(r.mot_killed),
      injured: n(r.injured), ped_injured: n(r.ped_injured), cyc_injured: n(r.cyc_injured), mot_injured: n(r.mot_injured),
    }))
    .sort((a, b) => a.month.localeCompare(b.month));
  months.pop(); // trailing month is always a partial
  return months;
}

function rolling12(months, field) {
  const out = [];
  for (let i = 11; i < months.length; i++) {
    let s = 0;
    for (let j = i - 11; j <= i; j++) s += months[j][field];
    out.push({ month: months[i].month, value: s });
  }
  return out;
}

function render(months) {
  renderTiles(months);
  const charts = document.querySelector('#kpi-charts');
  charts.innerHTML = '';
  charts.appendChild(chartCard('Traffic deaths', 'Trailing 12-month total by road user', months, 'killed'));
  charts.appendChild(chartCard('Traffic injuries (all severities)', 'Trailing 12-month total by road user', months, 'injured'));
}

function trailingSum(months, field, offset) {
  // offset 0 = latest 12 complete months; 1 = the 12 before those
  const end = months.length - offset * 12;
  return months.slice(end - 12, end).reduce((s, m) => s + m[field], 0);
}

function renderTiles(months) {
  const tiles = [
    ['Deaths, last 12 mo', 'killed'],
    ['Pedestrian deaths', 'ped_killed'],
    ['Cyclist deaths', 'cyc_killed'],
    ['Injuries, last 12 mo', 'injured'],
  ].map(([label, field]) => {
    const cur = trailingSum(months, field, 0);
    const prev = trailingSum(months, field, 1);
    const d = cur - prev;
    const cls = d <= 0 ? 'delta-good' : 'delta-bad';
    const arrow = d <= 0 ? '▼' : '▲';
    return `<div class="tile" role="listitem"><div class="label">${label}</div>
      <div class="value">${cur.toLocaleString()}</div>
      <div class="delta ${cls}">${arrow} ${Math.abs(d).toLocaleString()} vs prior 12 mo</div></div>`;
  });
  document.querySelector('#kpi-tiles').innerHTML = tiles.join('');
}

function chartCard(title, sub, months, suffix) {
  const series = SERIES.map((s) => ({ ...s, data: rolling12(months, `${s.key}_${suffix}`).slice(-60) }));
  const card = document.createElement('div');
  card.className = 'chart-card';
  card.innerHTML = `<h3>${title}</h3><p class="chart-sub">${sub} · shaded band = provisional (reporting lag)</p>`;
  card.appendChild(lineChart(series, title));
  card.insertAdjacentHTML(
    'beforeend',
    `<div class="legend">${series
      .map((s) => `<span><span class="swatch" style="background:${s.color}"></span>${s.label}</span>`)
      .join('')}</div>`
  );
  return card;
}

function lineChart(series, name) {
  const W = 900, H = 280, M = { t: 14, r: 136, b: 26, l: 46 };
  const pw = W - M.l - M.r, ph = H - M.t - M.b;
  const xs = series[0].data.map((d) => d.month);
  const maxY = Math.max(...series.flatMap((s) => s.data.map((d) => d.value))) * 1.08 || 1;
  const x = (i) => M.l + (pw * i) / (xs.length - 1);
  const y = (v) => M.t + ph - (ph * v) / maxY;

  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  svg.setAttribute('role', 'img');
  svg.setAttribute('aria-label', `${name}, trailing 12-month totals by road user`);
  const add = (parent, tag, attrs, text) => {
    const el = document.createElementNS(ns, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    if (text != null) el.textContent = text;
    parent.appendChild(el);
    return el;
  };

  // provisional band (last PROVISIONAL_MONTHS points)
  const provStart = Math.max(0, xs.length - 1 - PROVISIONAL_MONTHS);
  add(svg, 'rect', {
    x: x(provStart), y: M.t, width: x(xs.length - 1) - x(provStart), height: ph,
    fill: 'var(--grid)', opacity: 0.45,
  });

  // gridlines + y labels (4 ticks)
  for (let i = 0; i <= 4; i++) {
    const v = (maxY / 4) * i, yy = y(v);
    add(svg, 'line', { x1: M.l, x2: W - M.r, y1: yy, y2: yy, stroke: 'var(--grid)', 'stroke-width': 1 });
    add(svg, 'text', { x: M.l - 6, y: yy + 4, 'text-anchor': 'end', fill: 'var(--text-muted)', 'font-size': 11 },
      Math.round(v).toLocaleString());
  }
  // x labels: Januaries
  xs.forEach((m, i) => {
    if (m.endsWith('-01')) {
      add(svg, 'text', { x: x(i), y: H - 8, 'text-anchor': 'middle', fill: 'var(--text-muted)', 'font-size': 11 }, m.slice(0, 4));
      add(svg, 'line', { x1: x(i), x2: x(i), y1: M.t + ph, y2: M.t + ph + 4, stroke: 'var(--baseline)' });
    }
  });
  add(svg, 'line', { x1: M.l, x2: W - M.r, y1: M.t + ph, y2: M.t + ph, stroke: 'var(--baseline)', 'stroke-width': 1 });

  // announcement marker
  const ai = xs.indexOf(ANNOUNCED);
  if (ai >= 0) {
    add(svg, 'line', { x1: x(ai), x2: x(ai), y1: M.t, y2: M.t + ph, stroke: 'var(--text-muted)', 'stroke-dasharray': '3 4' });
    add(svg, 'text', { x: x(ai) - 5, y: M.t + 12, 'text-anchor': 'end', fill: 'var(--text-secondary)', 'font-size': 11 }, 'Plan announced');
  }

  // series lines + direct labels at line end
  for (const s of series) {
    const d = s.data.map((p, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(p.value).toFixed(1)}`).join('');
    add(svg, 'path', { d, fill: 'none', stroke: s.color, 'stroke-width': 2, 'stroke-linejoin': 'round' });
    const last = s.data.at(-1);
    add(svg, 'text', { x: W - M.r + 8, y: y(last.value) + 4, fill: s.color, 'font-size': 12, 'font-weight': 600 },
      `${s.label} ${last.value.toLocaleString()}`);
  }

  attachHover(svg, series, xs, x, y, { M, ph, W });
  return svg;
}

let tooltipEl;
function tooltip() {
  if (!tooltipEl) {
    tooltipEl = document.createElement('div');
    tooltipEl.className = 'viz-tooltip';
    document.body.appendChild(tooltipEl);
  }
  return tooltipEl;
}

function attachHover(svg, series, xs, x, y, { M, ph, W }) {
  const ns = 'http://www.w3.org/2000/svg';
  const cross = document.createElementNS(ns, 'line');
  cross.setAttribute('stroke', 'var(--baseline)');
  cross.setAttribute('stroke-width', 1);
  cross.setAttribute('y1', M.t);
  cross.setAttribute('y2', M.t + ph);
  cross.style.display = 'none';
  svg.appendChild(cross);
  const dots = series.map((s) => {
    const c = document.createElementNS(ns, 'circle');
    c.setAttribute('r', 4);
    c.setAttribute('fill', s.color);
    c.setAttribute('stroke', 'var(--surface-1)');
    c.setAttribute('stroke-width', 2);
    c.style.display = 'none';
    svg.appendChild(c);
    return c;
  });

  svg.addEventListener('pointermove', (ev) => {
    const rect = svg.getBoundingClientRect();
    const px = ((ev.clientX - rect.left) / rect.width) * W;
    const i = Math.max(0, Math.min(xs.length - 1, Math.round(((px - M.l) / (x(xs.length - 1) - M.l)) * (xs.length - 1))));
    cross.setAttribute('x1', x(i));
    cross.setAttribute('x2', x(i));
    cross.style.display = '';
    series.forEach((s, k) => {
      dots[k].setAttribute('cx', x(i));
      dots[k].setAttribute('cy', y(s.data[i].value));
      dots[k].style.display = '';
    });
    const tt = tooltip();
    tt.innerHTML =
      `<div class="tt-date">12 months ending ${xs[i]}</div>` +
      series
        .map((s) => `<div class="row"><span><span class="swatch" style="background:${s.color};display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:5px"></span>${s.label}</span><span class="val">${s.data[i].value.toLocaleString()}</span></div>`)
        .join('');
    tt.style.display = 'block';
    tt.style.left = `${Math.min(ev.clientX + 14, window.innerWidth - 190)}px`;
    tt.style.top = `${ev.clientY + 14}px`;
  });
  svg.addEventListener('pointerleave', () => {
    cross.style.display = 'none';
    dots.forEach((d) => (d.style.display = 'none'));
    tooltip().style.display = 'none';
  });
}
