(() => {
  const form = document.querySelector('#mcsSweepForm');
  const chart = document.querySelector('#mcsChart');
  if (!form || !chart) return;

  let payload = null;
  const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const finite = value => Number.isFinite(Number(value)) ? Number(value) : null;
  const fmt = (value, digits = 3) => finite(value) === null ? '—' : Number(value).toFixed(digits);
  const metricCard = (label, value) => `<div class="metric"><small>${escape(label)}</small><strong>${escape(value)}</strong><span>SIMULATED · DERIVED</span></div>`;

  function draw() {
    if (!payload) return;
    const metric = document.querySelector('#mcsMetric').value;
    const label = metric === 'evm_db' ? 'EVM (dB)' : 'Power (dBm)';
    const valid = payload.points.filter(point => point.valid && finite(point[metric]) !== null);
    const values = valid.map(point => Number(point[metric]));
    const mcsValues = payload.metadata.selected_mcs;
    const xMin = Math.min(...mcsValues), xMax = Math.max(...mcsValues);
    let yMin = values.length ? Math.min(...values) : -1, yMax = values.length ? Math.max(...values) : 1;
    const padding = Math.max((yMax - yMin) * .18, .5); yMin -= padding; yMax += padding;
    const sx = value => 70 + (value - xMin) / Math.max(xMax - xMin, 1) * 760;
    const sy = value => 390 - (value - yMin) / Math.max(yMax - yMin, 1) * 320;
    const grid = [], labels = [];
    for (let index = 0; index <= 5; index += 1) {
      const yValue = yMin + (yMax - yMin) * index / 5, y = sy(yValue);
      grid.push(`<line class="mcs-grid" x1="70" y1="${y}" x2="830" y2="${y}"/>`);
      labels.push(`<text class="mcs-label" x="58" y="${y + 4}" text-anchor="end">${yValue.toFixed(2)}</text>`);
    }
    const path = valid.map((point, index) => `${index ? 'L' : 'M'} ${sx(point.mcs_index)} ${sy(point[metric])}`).join(' ');
    const points = valid.map(point => `<circle class="mcs-point" cx="${sx(point.mcs_index)}" cy="${sy(point[metric])}" r="5"><title>MCS ${point.mcs_index} · ${point.modulation} · ${label} ${fmt(point[metric])}</title></circle>`).join('');
    const xLabels = mcsValues.map(value => `<text class="mcs-label" x="${sx(value)}" y="415" text-anchor="middle">${value}</text>`).join('');
    chart.innerHTML = `${grid.join('')}<line class="mcs-axis" x1="70" y1="390" x2="830" y2="390"/><line class="mcs-axis" x1="70" y1="70" x2="70" y2="390"/>${labels.join('')}${path ? `<path class="mcs-line" d="${path}"/>` : ''}${points}${xLabels}<text class="mcs-label" x="450" y="455" text-anchor="middle">MCS index</text><text class="mcs-label" x="18" y="230" text-anchor="middle" transform="rotate(-90 18 230)">${label}</text>`;
    document.querySelector('#mcsChartTitle').textContent = `${label} vs MCS`;
  }

  function render(data) {
    payload = data;
    const valid = data.points.filter(point => point.valid);
    const evm = valid.map(point => finite(point.evm_db)).filter(value => value !== null);
    document.querySelector('#mcsMetrics').innerHTML = [
      metricCard('Standard', data.metadata.standard),
      metricCard('Selected MCS', data.metadata.selected_mcs.join(', ')),
      metricCard('Valid / Total', `${data.metadata.valid_count} / ${data.metadata.point_count}`),
      metricCard('EVM range', evm.length ? `${fmt(Math.min(...evm))}…${fmt(Math.max(...evm))} dB` : 'insufficient_data'),
    ].join('');
    document.querySelector('#mcsRows').innerHTML = data.points.map(point => `<tr class="${point.valid ? '' : 'invalid'}"><td>${point.mcs_index}</td><td>${escape(point.modulation)}</td><td>${escape(point.coding_rate)}</td><td>${fmt(point.evm_db)} dB</td><td>${fmt(point.power_dbm)} dBm</td><td>${fmt(point.frequency_error_hz)} Hz</td><td>${point.reliability ?? '—'}</td><td>${point.valid ? 'VALID' : 'INVALID'}</td></tr>`).join('');
    const urls = data.artifact_urls || {};
    document.querySelector('#mcsArtifacts').innerHTML = ['csv','json','svg','png','metadata'].filter(key => urls[key]).map(key => `<a href="${escape(urls[key])}" target="_blank" rel="noopener">${key.toUpperCase()}</a>`).join(' · ');
    [['#mcsSvg','svg'],['#mcsPng','png'],['#mcsCsv','csv'],['#mcsJson','json']].forEach(([selector,key]) => { const button=document.querySelector(selector); button.disabled=!urls[key]; button.dataset.url=urls[key]||''; });
    draw();
  }

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const button = document.querySelector('#runMcsSweep'); button.disabled = true;
    try {
      const request = Object.fromEntries(new FormData(form).entries());
      for (const key of ['bandwidth_mhz','frequency_hz','nominal_power_dbm','evm_jitter_db','power_jitter_db','frequency_error_std_hz','invalid_rate','seed']) request[key] = Number(request[key]);
      const response = await fetch('/api/mock/mcs-sweep', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request)});
      const data = await response.json(); if (!response.ok) throw new Error(data.error || 'MCS sweep generation failed'); render(data);
    } catch (error) { window.toast ? window.toast(error.message, 'error') : alert(error.message); }
    finally { button.disabled = false; }
  });
  document.querySelector('#mcsMetric').addEventListener('change', draw);
  [['#mcsSvg','mcs_sweep.svg'],['#mcsPng','mcs_sweep.png'],['#mcsCsv','mcs_sweep.csv'],['#mcsJson','mcs_sweep.json']].forEach(([selector,name]) => document.querySelector(selector).addEventListener('click', () => { const url=document.querySelector(selector).dataset.url;if(url){const link=document.createElement('a');link.href=url;link.download=name;link.click();} }));
})();
