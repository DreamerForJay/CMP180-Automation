(() => {
  const chart = document.querySelector('#constellationChart');
  const form = document.querySelector('#constellationForm');
  if (!chart || !form) return;

  let payload = null;
  const view = { cx: 0, cy: 0, span: 3, drag: null };
  const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const finite = value => Number.isFinite(Number(value)) ? Number(value) : null;
  const fmt = (value, digits = 4) => finite(value) === null ? '—' : Number(value).toFixed(digits);
  const metric = (label, value, source = 'SIMULATED · DERIVED') => `<div class="metric"><small>${escape(label)}</small><strong>${escape(value)}</strong><span>${escape(source)}</span></div>`;
  const coords = point => document.querySelector('#constellationCoordinateMode').value === 'raw'
    ? [finite(point.i), finite(point.q)] : [finite(point.normalized_i), finite(point.normalized_q)];
  const sx = value => 70 + (value - (view.cx - view.span)) / (view.span * 2) * 620;
  const sy = value => 690 - (value - (view.cy - view.span)) / (view.span * 2) * 620;
  const outlierThreshold = () => {
    const rms = finite(payload?.analysis?.rms_evm_percent?.value);
    return rms === null ? Infinity : (rms / 100) * 3;
  };

  function draw() {
    if (!payload) return;
    const ticks = 6, grid = [], labels = [];
    for (let index = 0; index <= ticks; index += 1) {
      const value = view.cx - view.span + index * view.span * 2 / ticks;
      const yValue = view.cy - view.span + index * view.span * 2 / ticks;
      const x = sx(value), y = sy(yValue);
      grid.push(`<line class="constellation-grid" x1="${x}" y1="70" x2="${x}" y2="690"/><line class="constellation-grid" x1="70" y1="${y}" x2="690" y2="${y}"/>`);
      labels.push(`<text class="constellation-label" x="${x}" y="716" text-anchor="middle">${value.toFixed(2)}</text><text class="constellation-label" x="58" y="${y + 4}" text-anchor="end">${yValue.toFixed(2)}</text>`);
    }
    const threshold = outlierThreshold();
    const points = payload.points.map(point => {
      const [i, q] = coords(point);
      if (!point.valid || i === null || q === null) return '';
      const outlier = finite(point.evm) !== null && Number(point.evm) > threshold;
      return `<circle class="constellation-point${outlier ? ' outlier' : ''}" data-symbol="${point.symbol_index}" data-i="${fmt(i)}" data-q="${fmt(q)}" data-evm="${fmt(point.evm)}" cx="${sx(i)}" cy="${sy(q)}" r="3.2"><title>Symbol ${point.symbol_index} · I ${fmt(i)} · Q ${fmt(q)} · EVM ${fmt(point.evm)}</title></circle>`;
    }).join('');
    const ideals = payload.ideal_points.map(point => `<path class="constellation-ideal" d="M ${sx(point.i)-4} ${sy(point.q)} h 8 M ${sx(point.i)} ${sy(point.q)-4} v 8"/>`).join('');
    // 圖例使用獨立色彩，避免深色主題或瀏覽器快取讓有效點誤看成黑色。
    const legend = `<circle class="constellation-point" cx="84" cy="42" r="4"/><text class="constellation-legend" x="94" y="46">Measured / simulated</text><path class="constellation-ideal" d="M 244 42 h 10 M 249 37 v 10"/><text class="constellation-legend" x="262" y="46">Ideal reference</text><circle class="constellation-point outlier" cx="402" cy="42" r="4"/><text class="constellation-legend" x="412" y="46">Outlier</text>`;
    chart.innerHTML = `${legend}<rect x="70" y="70" width="620" height="620" fill="transparent" stroke="#587089" opacity=".9"/>${grid.join('')}<line class="constellation-axis" x1="${sx(0)}" y1="70" x2="${sx(0)}" y2="690"/><line class="constellation-axis" x1="70" y1="${sy(0)}" x2="690" y2="${sy(0)}"/>${labels.join('')}${ideals}${points}<text class="constellation-label" x="380" y="748" text-anchor="middle">I</text><text class="constellation-label" x="16" y="380" text-anchor="middle" transform="rotate(-90 16 380)">Q</text>`;
  }

  function render(data) {
    payload = data;
    Object.assign(view, { cx: 0, cy: 0, span: 3, drag: null });
    const a = data.analysis, m = data.metadata;
    document.querySelector('#constellationChartTitle').textContent = `${m.modulation} · ${m.valid_count}/${m.sample_count} valid`;
    document.querySelector('#constellationMetrics').innerHTML = [
      metric('Modulation', m.modulation, 'SIMULATED'), metric('Point count', m.sample_count, 'SIMULATED'),
      metric('Valid / Invalid', `${a.valid_count} / ${a.invalid_count}`, 'SIMULATED'),
      metric('RMS EVM', `${fmt(a.rms_evm_percent?.value, 3)} %`, 'SIMULATED · DERIVED'),
      metric('Peak EVM', `${fmt(a.peak_evm_percent?.value, 3)} %`, 'SIMULATED · DERIVED'),
      metric('I mean', fmt(a.i_mean?.value), 'SIMULATED · DERIVED'), metric('Q mean', fmt(a.q_mean?.value), 'SIMULATED · DERIVED'),
      metric('I/Q imbalance', `${fmt(a.iq_gain_imbalance_db?.value, 3)} dB`, 'SIMULATED · DERIVED'),
      metric('Estimated phase', `${fmt(a.estimated_phase_error_deg?.value, 3)}°`, 'SIMULATED · DERIVED'),
    ].join('');
    const threshold = outlierThreshold();
    document.querySelector('#constellationRows').innerHTML = data.points.slice(0, 500).map(point => {
      const outlier = point.valid && finite(point.evm) !== null && Number(point.evm) > threshold;
      return `<tr class="${point.valid ? (outlier ? 'outlier' : '') : 'invalid'}"><td>${point.symbol_index}</td><td>${fmt(point.i)}</td><td>${fmt(point.q)}</td><td>${fmt(point.ideal_i)}</td><td>${fmt(point.ideal_q)}</td><td>${fmt(point.evm)}</td><td>${point.valid ? (outlier ? 'VALID · OUTLIER' : 'VALID') : 'INVALID'}</td></tr>`;
    }).join('');
    const urls = data.artifact_urls || {};
    document.querySelector('#constellationArtifacts').innerHTML = ['csv','json','svg','png','metadata'].filter(key => urls[key]).map(key => `<a href="${escape(urls[key])}" target="_blank" rel="noopener">${key.toUpperCase()}</a>`).join(' · ');
    [['#constellationSvg','svg'],['#constellationPng','png'],['#constellationCsv','csv'],['#constellationJson','json']].forEach(([selector,key]) => { const button = document.querySelector(selector); button.disabled = !urls[key]; button.dataset.url = urls[key] || ''; });
    draw();
  }

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const button = document.querySelector('#runConstellation');
    button.disabled = true;
    try {
      const values = new FormData(form), request = Object.fromEntries(values.entries());
      for (const key of ['point_count','noise_db','phase_deg','gain_imbalance_db','quadrature_error_deg','frequency_offset_hz','symbol_rate_hz','amplitude_scale','dc_i','dc_q','invalid_rate','seed']) request[key] = Number(request[key]);
      const response = await fetch('/api/mock/constellation', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(request) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Constellation generation failed');
      render(data);
    } catch (error) {
      window.toast ? window.toast(error.message, 'error') : alert(error.message);
    } finally { button.disabled = false; }
  });

  document.querySelector('#constellationCoordinateMode').addEventListener('change', draw);
  document.querySelector('#constellationReset').addEventListener('click', () => { Object.assign(view, {cx:0,cy:0,span:3,drag:null}); draw(); });
  chart.addEventListener('wheel', event => { if (!payload) return; event.preventDefault(); view.span = Math.max(.15, Math.min(8, view.span * (event.deltaY > 0 ? 1.15 : .85))); draw(); }, {passive:false});
  chart.addEventListener('pointerdown', event => { if (!payload) return; chart.setPointerCapture(event.pointerId); chart.classList.add('dragging'); view.drag = {x:event.clientX,y:event.clientY,cx:view.cx,cy:view.cy}; });
  chart.addEventListener('pointermove', event => {
    const hover = document.querySelector('#constellationHover');
    if (view.drag) {
      const box=chart.getBoundingClientRect(), scale=view.span*2/(box.width*620/760);
      view.cx=view.drag.cx-(event.clientX-view.drag.x)*scale; view.cy=view.drag.cy+(event.clientY-view.drag.y)*scale; draw();
      hover.hidden = true;
      return;
    }
    const point = event.target.closest?.('.constellation-point');
    if (!point) { hover.hidden = true; return; }
    const card = chart.parentElement.getBoundingClientRect();
    hover.textContent = `Symbol ${point.dataset.symbol} · I ${point.dataset.i} · Q ${point.dataset.q} · EVM ${point.dataset.evm}`;
    hover.style.left = `${event.clientX - card.left + 12}px`; hover.style.top = `${event.clientY - card.top + 12}px`; hover.hidden = false;
  });
  chart.addEventListener('pointerleave', () => { document.querySelector('#constellationHover').hidden = true; });
  chart.addEventListener('pointerup', () => { view.drag=null; chart.classList.remove('dragging'); });
  chart.addEventListener('pointercancel', () => { view.drag=null; chart.classList.remove('dragging'); });
  [['#constellationSvg','constellation.svg'],['#constellationCsv','constellation.csv'],['#constellationJson','constellation.json']].forEach(([selector,name]) => document.querySelector(selector).addEventListener('click', () => { const url=document.querySelector(selector).dataset.url; if (url) { const link=document.createElement('a'); link.href=url; link.download=name; link.click(); } }));
  document.querySelector('#constellationPng').addEventListener('click', () => {
    if (!payload) return;
    const svg = chart.cloneNode(true); svg.setAttribute('xmlns','http://www.w3.org/2000/svg');
    const blob = new Blob([new XMLSerializer().serializeToString(svg)], {type:'image/svg+xml'}), url=URL.createObjectURL(blob), image=new Image();
    image.onload=()=>{const canvas=document.createElement('canvas');canvas.width=1520;canvas.height=1520;const context=canvas.getContext('2d');context.fillStyle=getComputedStyle(document.documentElement).getPropertyValue('--console-surface')||'#071018';context.fillRect(0,0,1520,1520);context.drawImage(image,0,0,1520,1520);canvas.toBlob(png=>{if(png){const link=document.createElement('a');link.href=URL.createObjectURL(png);link.download='constellation.png';link.click();setTimeout(()=>URL.revokeObjectURL(link.href),0)}},'image/png');URL.revokeObjectURL(url)};image.src=url;
  });
})();
