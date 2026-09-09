let loopbackJobId = null;
let loopbackBatchMode = false;
let loopbackPreviewState = null;

function loopbackPayload() {
  const form = new FormData(document.querySelector('#loopbackForm'));
  const numeric = name => form.get(name) === '' ? null : Number(form.get(name));
  return {
    center_frequency_hz: numeric('center_frequency_hz'),
    bandwidth_hz: numeric('bandwidth_hz'),
    generator_power_dbm: numeric('generator_power_dbm'),
    repeat_count: numeric('repeat_count'),
    minimum_repeats: Math.min(5, numeric('repeat_count')),
    max_evm_std_db: numeric('max_evm_std_db'),
    max_power_std_db: numeric('max_power_std_db'),
    max_freq_error_std_hz: numeric('max_freq_error_std_hz'),
    max_invalid_ratio: numeric('max_invalid_ratio'),
    expected_power_dbm: numeric('expected_power_dbm'),
    allowed_power_error_db: numeric('allowed_power_error_db'),
    cable_confirmation: String(form.get('cable_confirmation') || ''),
    direct_cable_no_attenuator: form.get('direct_cable_no_attenuator') === 'on',
    operator_present: form.get('operator_present') === 'on'
  };
}

// 圖表 metric key 與 analysis 統計欄位名稱不同，需明確對應才能標出正確的 outlier。
const LOOPBACK_METRIC_FIELDS = {
  evm_all_db: 'evm_all_carriers_db',
  burst_power_dbm: 'burst_power_dbm',
  frequency_error_hz: 'frequency_error_hz'
};

function loopbackSvg(points, field, label, outlierRepeats = new Set()) {
  const samples = points.map((point, index) => ({index, value: Number(point[field]), valid: point.valid !== false && Number.isFinite(Number(point[field]))}));
  const finite = samples.filter(sample => sample.valid);
  if (!finite.length) return `<div><strong>${label}</strong><svg viewBox="0 0 360 140"><text x="180" y="70" text-anchor="middle">No valid data</text></svg></div>`;
  const low = Math.min(...finite.map(sample => sample.value));
  const high = Math.max(...finite.map(sample => sample.value));
  const span = Math.max(high - low, Math.abs(high) * .001, .01);
  const x = index => 35 + index / Math.max(samples.length - 1, 1) * 305;
  const y = value => 115 - (value - (low - span * .15)) / (span * 1.3) * 85;
  let path = '', open = false;
  samples.forEach(sample => { if (!sample.valid) { open = false; return; } path += `${open ? 'L' : 'M'}${x(sample.index)},${y(sample.value)} `; open = true; });
  const repeatOf = index => Number(points[index].repeat_index || index + 1);
  const dots = samples.map(sample => {
    const repeat = repeatOf(sample.index);
    if (!sample.valid) return `<text x="${x(sample.index)}" y="70" class="loopback-invalid">×</text>`;
    // Outlier 只標色不刪除資料點，趨勢線仍保留原始量測值。
    const flagged = outlierRepeats.has(repeat);
    return `<circle cx="${x(sample.index)}" cy="${y(sample.value)}" r="${flagged ? 6 : 4}" class="${flagged ? 'loopback-outlier-dot' : ''}"><title>Repeat ${repeat}: ${sample.value}${flagged ? ' (IQR outlier)' : ''}</title></circle>`;
  }).join('');
  return `<div><strong>${label}</strong><svg viewBox="0 0 360 140"><line x1="35" y1="115" x2="340" y2="115" class="grid-line"/><path d="${path}" class="plot-line"/>${dots}</svg></div>`;
}

function renderLoopbackLive(points, outlierMap = new Map()) {
  const repeatsFor = field => new Set(
    [...outlierMap].filter(([, metrics]) => metrics.includes(LOOPBACK_METRIC_FIELDS[field])).map(([repeat]) => repeat)
  );
  document.querySelector('#loopbackCharts').innerHTML =
    loopbackSvg(points, 'evm_all_db', 'EVM All (dB)', repeatsFor('evm_all_db')) +
    loopbackSvg(points, 'burst_power_dbm', 'Burst Power (dBm)', repeatsFor('burst_power_dbm')) +
    loopbackSvg(points, 'frequency_error_hz', 'Frequency Error (Hz)', repeatsFor('frequency_error_hz'));
  document.querySelector('#loopbackRows').innerHTML = points.map(point =>
    `<tr class="${point.valid === false ? 'loopback-abnormal' : ''}"><td>${point.repeat_index || point.point_index + 1}</td><td>${formatMeasured(point.evm_all_db)}</td><td>${formatMeasured(point.burst_power_dbm)}</td><td>${formatMeasured(point.frequency_error_hz)}</td><td>${point.valid === false ? `INVALID: ${escapeHtml((point.invalid_reasons || []).join(', '))}` : 'VALID'}</td><td>—</td></tr>`
  ).join('');
}

function renderLoopbackResult(result) {
  const analysis = result.loopback.analysis;
  const stats = analysis.statistics;
  const show = value => Number.isFinite(Number(value)) ? Number(value).toFixed(3) : '—';
  document.querySelector('#loopbackOverall').textContent = analysis.overall_status;
  document.querySelector('#loopbackMetrics').innerHTML =
    metric('Stability', analysis.stability_status) +
    metric('Reasonable', analysis.reasonableness_status) +
    metric('Valid', `${analysis.valid_count}/${analysis.repeat_count}`) +
    metric('Outliers', analysis.outlier_count) +
    metric('Avg EVM', `${show(stats.evm_all_carriers_db.mean)} dB`) +
    metric('EVM Std', `${show(stats.evm_all_carriers_db.std_dev)} dB`) +
    metric('Avg Power', `${show(stats.burst_power_dbm.mean)} dBm`) +
    metric('Power Std', `${show(stats.burst_power_dbm.std_dev)} dB`) +
    metric('Avg Freq Err', `${show(stats.frequency_error_hz.mean)} Hz`) +
    metric('Freq Err Std', `${show(stats.frequency_error_hz.std_dev)} Hz`);
  const outlierMap = new Map();
  const outlierMetrics = new Map();
  analysis.outliers.forEach(item => {
    const values = outlierMap.get(item.repeat_index) || [];
    values.push(`${item.metric}=${item.value}`);
    outlierMap.set(item.repeat_index, values);
    outlierMetrics.set(item.repeat_index, [...(outlierMetrics.get(item.repeat_index) || []), item.metric]);
  });
  const points = result.points || [];
  renderLoopbackLive(points, outlierMetrics);
  document.querySelector('#loopbackRows').innerHTML = points.map(point => {
    const repeat = point.repeat_index || point.point_index + 1;
    const outliers = outlierMap.get(repeat) || [];
    const abnormal = point.valid === false || outliers.length;
    return `<tr class="${abnormal ? 'loopback-abnormal' : ''}"><td>${repeat}</td><td>${formatMeasured(point.evm_all_db)}</td><td>${formatMeasured(point.burst_power_dbm)}</td><td>${formatMeasured(point.frequency_error_hz)}</td><td>${point.valid === false ? `INVALID: ${escapeHtml((point.invalid_reasons || []).join(', '))}` : 'VALID'}</td><td>${outliers.length ? escapeHtml(outliers.join('; ')) : '—'}</td></tr>`;
  }).join('');
  const urls = result.artifact_urls || {};
  document.querySelector('#loopbackArtifacts').innerHTML = Object.entries(urls).map(([key, url]) => `<a href="${url}" target="_blank" rel="noopener">${escapeHtml(key)}</a>`).join(' · ');
}

function renderLoopbackBatchResult(result) {
  const cases = result.cases || [];
  document.querySelector('#loopbackOverall').textContent = `${cases.length}/${result.requested_cases || 11} PROFILES COMPLETE`;
  document.querySelector('#loopbackMetrics').innerHTML = cases.map(item =>
    metric(item.case_id, item.overall_status)
  ).join('');
  document.querySelector('#loopbackArtifacts').innerHTML = cases.map(item => {
    const report = item.artifacts?.report;
    const url = report ? `/artifacts/${String(report).split(/[\\/]/).slice(-2).join('/')}` : '';
    return url ? `<a href="${url}" target="_blank" rel="noopener">${escapeHtml(item.case_id)} report</a>` : escapeHtml(item.case_id);
  }).join(' · ');
}

function renderLoopbackPreview() {
  if (!loopbackPreviewState) return;
  const target = document.querySelector('#loopbackPreview');
  target.hidden = false;
  const {mode, preview, payload} = loopbackPreviewState;
  if (mode === 'batch') {
    target.textContent = language === 'zh'
      ? `${preview.case_count} 個 approved profiles × Repeat ${preview.repeat_count_per_case}\n共 ${preview.total_measurements} 次獨立 SingleShot\nRF1.1 → RF1.5 · 逐一 cleanup\n可執行：相同代表點會直接產生正式 LOOPBACK_READY artifact`
      : `${preview.case_count} approved profiles × Repeat ${preview.repeat_count_per_case}\n${preview.total_measurements} independent SingleShots\nRF1.1 → RF1.5 · sequential cleanup\nExecutable: matching representative points produce formal LOOPBACK_READY artifacts`;
    return;
  }
  const approved = preview.profile_lifecycle === 'approved';
  const profileLabel = language === 'zh'
    ? (approved ? 'APPROVED 正式 profile' : 'DRAFT 草稿 profile')
    : (approved ? 'APPROVED profile' : 'DRAFT profile');
  const gate = preview.execution_allowed
    ? (language === 'zh'
      ? (approved ? 'RF 計畫允許；成功時產生正式 LOOPBACK_READY artifact' : 'RF 計畫允許；結果維持 draft，不宣稱正式 READY')
      : (approved ? 'RF plan allowed; a successful run produces a formal LOOPBACK_READY artifact' : 'RF plan allowed; results remain draft and do not claim formal READY'))
    : (window.localizePlanDetail(preview.rejection_reason) || (language === 'zh' ? 'RF 計畫遭阻擋' : 'RF plan blocked'));
  target.textContent = `${profileLabel}\n${payload.center_frequency_hz / 1e6} MHz · ${payload.bandwidth_hz / 1e6} MHz · ${payload.generator_power_dbm} dBm\n${payload.repeat_count} ${language === 'zh' ? '次獨立 SingleShot' : 'independent SingleShots'}\n${gate}`;
}

window.addEventListener('cmp180-language-change', () => {
  // 只重繪已取得的檢查計畫，不重新送出 preview，也不觸發 RF。
  renderLoopbackPreview();
});

async function pollLoopback() {
  const response = await fetch(`/api/jobs/${loopbackJobId}`);
  const job = await response.json();
  renderLoopbackLive(job.live_points || []);
  document.querySelector('#loopbackOverall').textContent = `${job.state.toUpperCase()} ${job.completed_points}/${job.total_points}`;
  if (job.state === 'complete' || job.state === 'cancelled') {
    if (loopbackBatchMode) renderLoopbackBatchResult(job.result);
    else renderLoopbackResult(job.result);
    loopbackJobId = null;
    loopbackBatchMode = false;
    document.querySelector('#loopbackForm button[type="submit"]').disabled = false;
    document.querySelector('#runAllLoopbacks').disabled = false;
    loadRunHistory();
    return;
  }
  if (job.state === 'failed') {
    toast(job.error || 'Loopback validation failed', 'error');
    loopbackJobId = null;
    loopbackBatchMode = false;
    document.querySelector('#loopbackForm button[type="submit"]').disabled = false;
    document.querySelector('#runAllLoopbacks').disabled = false;
    return;
  }
  setTimeout(pollLoopback, 200);
}

document.querySelector('#loopbackForm').addEventListener('submit', async event => {
  event.preventDefault();
  const button = event.submitter;
  const payload = loopbackPayload();
  if (!payload.operator_present || !payload.direct_cable_no_attenuator) {
    toast(language === 'zh' ? '請先確認接線條件與操作員在場。' : 'Confirm cabling conditions and operator presence first.', 'error');
    return;
  }
  button.disabled = true;
  try {
    const previewResponse = await fetch('/api/hardware/loopback-preview', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
    const preview = await previewResponse.json();
    if (!previewResponse.ok) throw new Error(preview.error || 'Loopback preview failed');
    loopbackPreviewState = {mode: 'single', preview, payload};
    renderLoopbackPreview();
    if (!preview.execution_allowed) throw new Error(preview.rejection_reason || 'RF plan is blocked');
    // 最後確認列出真正 RF 條件；取消時不建立 job、不送 SCPI。
    if (!confirm(language === 'zh'
      ? `即將執行真實 Loopback RF\n${payload.repeat_count} 次獨立 SingleShot\n${payload.center_frequency_hz / 1e6} MHz · ${payload.bandwidth_hz / 1e6} MHz · ${payload.generator_power_dbm} dBm\nRoute: ${payload.cable_confirmation}\n\n確認開始？`
      : `Real Loopback RF will be transmitted\n${payload.repeat_count} independent SingleShots\n${payload.center_frequency_hz / 1e6} MHz · ${payload.bandwidth_hz / 1e6} MHz · ${payload.generator_power_dbm} dBm\nRoute: ${payload.cable_confirmation}\n\nConfirm and start?`)) return;
    payload.execution_confirmation = preview.required_confirmation;
    const response = await fetch('/api/jobs/hardware/loopback', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
    const job = await response.json();
    if (!response.ok) throw new Error(job.error || 'Unable to start loopback validation');
    loopbackJobId = job.job_id;
    loopbackBatchMode = false;
    pollLoopback();
  } catch (error) {
    toast(error.message, 'error');
    button.disabled = false;
  } finally {
    if (!loopbackJobId) button.disabled = false;
  }
});

document.querySelector('#runAllLoopbacks').addEventListener('click', async event => {
  const button = event.currentTarget;
  const payload = loopbackPayload();
  if (!payload.operator_present || !payload.direct_cable_no_attenuator) {
    toast(language === 'zh' ? '請先確認接線條件與操作員在場。' : 'Confirm cabling conditions and operator presence first.', 'error');
    return;
  }
  button.disabled = true;
  document.querySelector('#loopbackForm button[type="submit"]').disabled = true;
  try {
    const previewResponse = await fetch('/api/hardware/loopback-batch-preview', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: '{}'
    });
    const preview = await previewResponse.json();
    if (!previewResponse.ok || !preview.execution_allowed) throw new Error(preview.error || 'Batch preview is blocked');
    loopbackPreviewState = {mode: 'batch', preview, payload};
    renderLoopbackPreview();
    // 最後確認明列總 RF 次數；取消時不建立 job，也不送任何 SCPI。
    if (!confirm(language === 'zh'
      ? `即將執行全部 LOOPBACK profiles\n${preview.case_count} profiles × Repeat ${preview.repeat_count_per_case}\n共 ${preview.total_measurements} 次獨立 SingleShot\nRoute: RF1.1-RF1.5\n\n確認開始？`
      : `All LOOPBACK profiles will transmit real RF\n${preview.case_count} profiles × Repeat ${preview.repeat_count_per_case}\n${preview.total_measurements} independent SingleShots total\nRoute: RF1.1-RF1.5\n\nConfirm and start?`)) return;
    const response = await fetch('/api/jobs/hardware/loopback-batch', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        cable_confirmation: 'RF1.1-RF1.5',
        direct_cable_no_attenuator: true,
        operator_present: true,
        execution_confirmation: preview.required_confirmation
      })
    });
    const job = await response.json();
    if (!response.ok) throw new Error(job.error || 'Unable to start all loopback profiles');
    loopbackJobId = job.job_id;
    loopbackBatchMode = true;
    pollLoopback();
  } catch (error) {
    toast(error.message, 'error');
  } finally {
    if (!loopbackJobId) {
      button.disabled = false;
      document.querySelector('#loopbackForm button[type="submit"]').disabled = false;
    }
  }
});
