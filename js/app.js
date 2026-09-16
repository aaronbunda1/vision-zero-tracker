import { initKpi } from './kpi.js';

const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

let META, COMMITMENTS;

async function main() {
  [META, COMMITMENTS] = await Promise.all([
    fetch('data/meta.json').then((r) => r.json()),
    fetch('data/commitments.json').then((r) => r.json()),
  ]);
  renderLastUpdated();
  renderSummaryTiles();
  renderGoalBars();
  renderAgencyTable();
  buildFilters();
  renderList();
  initKpi();
}

function statusLabel(s) { return META.statuses[s] || s; }

function renderLastUpdated() {
  const latest = COMMITMENTS.flatMap((c) => c.updates.map((u) => u.date)).sort().at(-1);
  $('#last-updated').textContent = `tracker last updated ${latest}`;
}

function counts(list) {
  const by = { not_started: 0, in_progress: 0, completed: 0, stalled: 0 };
  for (const c of list) by[c.status] = (by[c.status] || 0) + 1;
  return by;
}

function renderSummaryTiles() {
  const by = counts(COMMITMENTS);
  const total = COMMITMENTS.length;
  const pct = Math.round((100 * (by.completed + 0.5 * by.in_progress)) / total);
  const tiles = [
    { label: 'Overall progress', value: `${pct}%`, sub: 'completed + half-credit for in progress' },
    { label: 'Commitments', value: total, sub: '8 goals · 14 agencies' },
    { label: 'Completed', value: by.completed, sub: statusBadge('completed') },
    { label: 'In progress', value: by.in_progress, sub: statusBadge('in_progress') },
    { label: 'Not started', value: by.not_started, sub: statusBadge('not_started') },
  ];
  $('#summary-tiles').innerHTML = tiles
    .map((t) => `<div class="tile" role="listitem"><div class="label">${esc(t.label)}</div>
      <div class="value">${esc(t.value)}</div><div class="delta">${t.sub}</div></div>`)
    .join('');
}

function statusBadge(s) {
  return `<span class="badge badge-${s}">${esc(statusLabel(s).toUpperCase())}</span>`;
}

function renderGoalBars() {
  const html = Object.entries(META.goals)
    .map(([g, name]) => {
      const list = COMMITMENTS.filter((c) => c.goal === Number(g));
      const by = counts(list);
      const seg = (k) =>
        by[k] ? `<span class="gb-${k}" style="width:${(100 * by[k]) / list.length}%" title="${esc(statusLabel(k))}: ${by[k]}"></span>` : '';
      return `<div class="goal-bar">
        <div class="gb-label"><span class="gb-name"><strong>Goal ${g}</strong> · ${esc(name)}</span>
          <span class="gb-count">${by.completed + by.in_progress}/${list.length} active or done</span></div>
        <div class="gb-track">${seg('completed')}${seg('in_progress')}${seg('stalled')}</div>
      </div>`;
    })
    .join('');
  $('#goal-bars').innerHTML = html;
}

function renderAgencyTable() {
  const rows = Object.keys(META.agencies)
    .map((a) => {
      const list = COMMITMENTS.filter((c) => c.agencies.includes(a));
      const by = counts(list);
      return { a, n: list.length, ip: by.in_progress, done: by.completed };
    })
    .filter((r) => r.n > 0)
    .sort((x, y) => y.n - x.n);
  $('#agency-table tbody').innerHTML = rows
    .map((r) => `<tr><td title="${esc(META.agencies[r.a])}">${esc(r.a)}</td>
      <td class="num">${r.n}</td><td class="num">${r.ip}</td><td class="num">${r.done}</td></tr>`)
    .join('');
}

function buildFilters() {
  $('#f-goal').innerHTML += Object.entries(META.goals)
    .map(([g, name]) => `<option value="${g}">Goal ${g} · ${esc(name.length > 48 ? name.slice(0, 45) + '…' : name)}</option>`)
    .join('');
  $('#f-agency').innerHTML += Object.entries(META.agencies)
    .map(([a, name]) => `<option value="${esc(a)}">${esc(a)} · ${esc(name)}</option>`)
    .join('');
  $('#f-status').innerHTML += Object.entries(META.statuses)
    .map(([s, name]) => `<option value="${esc(s)}">${esc(name)}</option>`)
    .join('');
  for (const id of ['#f-search', '#f-goal', '#f-agency', '#f-status', '#f-marquee'])
    $(id).addEventListener('input', renderList);
}

function filtered() {
  const q = $('#f-search').value.trim().toLowerCase();
  const goal = $('#f-goal').value;
  const agency = $('#f-agency').value;
  const status = $('#f-status').value;
  const marquee = $('#f-marquee').checked;
  return COMMITMENTS.filter((c) => {
    if (goal && c.goal !== Number(goal)) return false;
    if (agency && !c.agencies.includes(agency)) return false;
    if (status && c.status !== status) return false;
    if (marquee && !c.marquee) return false;
    if (q && !`${c.title} ${c.group || ''} ${c.id}`.toLowerCase().includes(q)) return false;
    return true;
  });
}

function renderList() {
  const list = filtered();
  $('#f-count').textContent = `${list.length} of ${COMMITMENTS.length}`;
  const byGoal = new Map();
  for (const c of list) {
    if (!byGoal.has(c.goal)) byGoal.set(c.goal, []);
    byGoal.get(c.goal).push(c);
  }
  $('#commitment-list').innerHTML = [...byGoal.entries()]
    .map(
      ([g, items]) => `<h4 class="goal-section-h">Goal ${g} · ${esc(META.goals[g])}</h4>` +
        items.map(renderCommitment).join('')
    )
    .join('');
}

function renderCommitment(c) {
  const star = c.marquee ? '<span class="marquee-star" title="Marquee action item">★</span> ' : '';
  const group = c.group ? `<span class="c-group">${esc(c.group)}</span>` : '';
  const history = c.updates
    .map(
      (u) => `<li><strong>${esc(u.date)}</strong> — ${statusBadge(u.status)} ${esc(u.note)}
        ${u.source ? ` · <a href="${esc(u.source)}" rel="noopener">source</a>` : ''}</li>`
    )
    .join('');
  return `<details class="commitment" id="${esc(c.id)}">
    <summary>
      <span class="c-id">${esc(c.id.replace('vz-', ''))}</span>
      <span class="c-title">${star}${esc(c.title)}${group}</span>
      <span class="c-agencies">${c.agencies.map(esc).join(', ')}</span>
      ${statusBadge(c.status)}
    </summary>
    <div class="c-body"><dl>
      ${c.target ? `<dt>Stated target</dt><dd>${esc(c.target)}</dd>` : ''}
      <dt>Responsible</dt><dd>${c.agencies.map((a) => esc(META.agencies[a] || a)).join('; ')}</dd>
      <dt>Plan reference</dt><dd>p. ${c.page} of the <a href="source/Vision-Zero-Reimagined-2026.pdf">plan PDF</a></dd>
      <dt>History</dt><dd><ul class="c-history">${history}</ul></dd>
    </dl></div>
  </details>`;
}

main().catch((e) => {
  document.body.insertAdjacentHTML('beforeend', `<p class="wrap">Failed to load data: ${esc(e.message)}</p>`);
});
