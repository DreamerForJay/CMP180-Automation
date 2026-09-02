Object.assign(translations.zh, {
  hardwareTab: '實機量測',
  hardwareTitle: 'CMP180 實機量測',
  hardwareHelp: '設定量測條件、完成檢查、執行並即時查看進度。',
  rfWarning: 'RF 輸出',
  rfWarningText: '送出前請確認接線與輸入功率；任一異常會停止流程並關閉 RF。',
  cableText: '接線路徑',
  cablePlaceholder: '例如 RF1.1-RF1.5',
  cableVerifiedOption: '已驗證：RF1.1 → RF1.5',
  cableHelp: '目前自動化 RF workflow 使用 RF1.1 → RF1.5；其他路徑會先阻擋，避免打錯孔位。',
  operatorPresent: '我人在 CMP180 旁並能觀察儀器',
  runHardware: '執行實機量測',
  preflightTitle: '執行前檢查',
  routeCheck: '接線符合 RF1.1 → RF1.5',
  operatorCheck: '操作員在儀器旁',
  hardwareBadge: '實機模式',
  hardwareControlState: '已啟用實機控制',
  hardwareControlHint: '完成檢查後才會送 RF',
  serverLockedTitle: '目前未啟用實機控制',
  serverLockedText: '請用 python -m cmp180_evm.web --host 127.0.0.1 --port 8765 啟動本機服務。'
});

Object.assign(translations.en, {
  hardwareTab: 'Hardware Measurement',
  hardwareTitle: 'CMP180 Hardware Measurement',
  hardwareHelp: 'Set conditions, complete checks, execute, and watch live progress.',
  rfWarning: 'RF output',
  rfWarningText: 'Confirm cabling and input power before execution. Any anomaly stops the flow and turns RF off.',
  cableText: 'Cable route',
  cablePlaceholder: 'e.g. RF1.1-RF1.5',
  cableVerifiedOption: 'Verified: RF1.1 → RF1.5',
  cableHelp: 'The current automated RF workflow uses RF1.1 → RF1.5; other routes are blocked to prevent wrong-port output.',
  operatorPresent: 'I am beside the CMP180 and can observe it',
  runHardware: 'Run hardware measurement',
  preflightTitle: 'Preflight checks',
  routeCheck: 'Route matches RF1.1 → RF1.5',
  operatorCheck: 'Operator is beside the instrument',
  hardwareBadge: 'Hardware Mode',
  hardwareControlState: 'Hardware control enabled',
  hardwareControlHint: 'RF is sent only after preflight',
  serverLockedTitle: 'Hardware control is not enabled',
  serverLockedText: 'Start the local service with python -m cmp180_evm.web --host 127.0.0.1 --port 8765.'
});

let hardwareEnabled = false;
let hardwareRequestRunning = false;

function normalizeRoute(value) {
  return String(value || '').trim().toUpperCase().replaceAll('→', '-').replaceAll(' ', '');
}

function showHardwareAlert(message, notify = true) {
  const alert = $('#hardwareAlert');
  alert.textContent = message;
  alert.hidden = !message;
  if (message && notify) toast(message, 'error');
}

function updateHardwareSummary() {
  const action = $('#hardwareForm').elements.hardware_action.value;
  const form = $('#customPlanForm')?.elements;
  let detail = '6105 MHz · 320 MHz · -40 dBm';
  let planCheck = 'SingleShot：RF1.1 → RF1.5 · 6105 MHz · 320 MHz · -40 dBm';
  let title = 'SingleShot';
  if (form && action === 'frequency') {
    title = 'Frequency Sweep';
    detail = `${form.start.value} ${form.start_unit.value} → ${form.stop.value} ${form.stop_unit.value} · Step ${form.step.value} ${form.step_unit.value} · ${form.bandwidth_mhz.value} MHz · ${form.generator_power_dbm.value} dBm`;
    planCheck = 'WLAN Frequency Sweep：先 Review；只允許通過 approved section 的中心頻率';
  }
  if (form && action === 'power') {
    title = 'Power Sweep';
    detail = `${form.start.value} → ${form.stop.value} dBm · Step ${form.step.value} dB · ${form.center_frequency_mhz.value} ${form.center_unit.value} · ${form.bandwidth_mhz.value} MHz`;
    planCheck = 'WLAN Power Sweep：先 Review；使用已核准 WLAN section 與安全功率';
  }
  if (action === 'gprf') {
    const gprf = $('#gprfPowerForm')?.elements;
    title = 'GPRF Power Sweep';
    detail = gprf
      ? `${gprf.axis.value} · ${gprf.start.value} → ${gprf.stop.value} · Dwell ${gprf.dwell_ms.value} ms`
      : 'GPRF power only · not WLAN EVM';
    planCheck = 'GPRF Power：可掃儀器調諧能力；不宣稱 WLAN EVM';
  }
  $('#hardwareProfileSummary').innerHTML = `<small>${language === 'zh' ? '目前設定' : 'Current plan'}</small><strong>${title}</strong><span>${detail}</span>`;
  // Review 文案跟著量測模式更新，避免操作員誤把 GPRF 掃描當成 WLAN EVM。
  $('#planCheckText').textContent = planCheck;
}

function updatePreflight() {
  const form = $('#hardwareForm');
  const routeVerified = normalizeRoute(form.elements.cable_confirmation.value) === 'RF1.1-RF1.5';
  const operatorPresent = form.elements.operator_present.checked;
  $('#routeCheck').classList.toggle('ok', routeVerified);
  $('#operatorCheck').classList.toggle('ok', operatorPresent);
  const blocked = !hardwareEnabled || !routeVerified || !operatorPresent || hardwareRequestRunning;
  $('#hardwareButton').disabled = blocked;
  updateHardwareSummary();
}

async function loadHardwareStatus() {
  try {
    const response = await fetch('/api/status');
    const status = await response.json();
    hardwareEnabled = status.hardware_enabled === true;
    $('#hardwareBadge').textContent = hardwareEnabled ? 'ARMED' : 'LOCKED';
    $('#serverLockedNotice').hidden = hardwareEnabled;
    if (hardwareEnabled) {
      // 狀態只反映本機 Web 服務是否允許實機 endpoint，不代表已送出 RF。
      const badge = $('#modeStatus');
      $('#modeStatusLabel').dataset.i18n = 'hardwareBadge';
      badge.classList.add('hardware');
      $('#controlStateText').dataset.i18n = 'hardwareControlState';
      $('#controlStateHint').dataset.i18n = 'hardwareControlHint';
      $('.workspace-state').classList.add('hardware');
      applyLanguage();
    }
    updatePreflight();
  } catch (error) {
    toast(`Status error: ${error.message}`, 'error');
  }
}

function selectHardwareAction(action) {
  const form = $('#hardwareForm');
  if (!['single', 'frequency', 'power', 'gprf'].includes(action)) return;
  form.elements.hardware_action.value = action;
  document.querySelectorAll('[data-hardware-action]').forEach(button => {
    button.classList.toggle('active', button.dataset.hardwareAction === action);
  });
  $('#hardwareSweepSetup').hidden = action === 'single' || action === 'gprf';
  $('#gprfPowerSetup').hidden = action !== 'gprf';
  if (action === 'frequency' || action === 'power') setCustomPlanAxis(action);
  updatePreflight();
}

document.querySelectorAll('[data-hardware-action]').forEach(button => {
  button.addEventListener('click', () => selectHardwareAction(button.dataset.hardwareAction));
});
selectHardwareAction('single');

$('#hardwareForm').onsubmit = event => {
  event.preventDefault();
  const form = new FormData(event.target);
  if (!hardwareEnabled) {
    showHardwareAlert(language === 'zh' ? '實機控制未啟用，未送出 RF。' : 'Hardware mode is locked; no RF was transmitted.');
    return;
  }
  const route = normalizeRoute(form.get('cable_confirmation'));
  if (!route) {
    showHardwareAlert(language === 'zh' ? '請輸入或選擇接線路徑。' : 'Select or enter a cable route.');
    return;
  }
  if (route !== 'RF1.1-RF1.5') {
    showHardwareAlert(language === 'zh' ? `${route} 尚未由本 workflow 驗證，未送出 RF。` : `Route "${route}" is not workflow-verified; no RF was transmitted.`);
    return;
  }
  if (form.get('operator_present') !== 'on') {
    showHardwareAlert(language === 'zh' ? '請確認操作員在 CMP180 旁。' : 'Confirm that an operator is beside the CMP180.');
    return;
  }
  if (hardwareRequestRunning) {
    showHardwareAlert(language === 'zh' ? '已有量測正在執行。' : 'A measurement is already running.');
    return;
  }
  const action = form.get('hardware_action');
  showHardwareAlert('');
  hardwareRequestRunning = true;
  updatePreflight();
  if (action === 'frequency' || action === 'power') {
    // 掃描一律使用畫面上的 custom plan，避免再退回 6085/6105/6125 固定 profile。
    window.reviewAndExecuteCustomHardwarePlan(event.submitter).finally(() => {
      hardwareRequestRunning = false;
      updatePreflight();
    });
    return;
  }
  if (action === 'gprf') {
    // GPRF 是另一條 RF power workflow，不可送進 WLAN custom-plan gate。
    window.reviewAndExecuteGprfPowerPlan(event.submitter).finally(() => {
      hardwareRequestRunning = false;
      updatePreflight();
    });
    return;
  }
  const approved = confirm(language === 'zh'
    ? `即將送出真實 RF\n\nSingleShot · 6105 MHz · 320 MHz · -40 dBm\nRoute: ${route}\n\n確認接線未變、操作員在場並開始？`
    : `Real RF will be transmitted\n\nSingleShot · 6105 MHz · 320 MHz · -40 dBm\nRoute: ${route}\n\nConfirm unchanged cabling, operator presence, and start?`);
  if (!approved) {
    hardwareRequestRunning = false;
    updatePreflight();
    toast(language === 'zh' ? '已取消，未送出 RF。' : 'Cancelled; no RF was transmitted.');
    return;
  }
  updateBlockJobState({state: 'running'});
  send('/api/hardware/single', {
    cable_confirmation: route,
    operator_present: form.get('operator_present') === 'on'
  }, event.submitter).finally(() => {
    hardwareRequestRunning = false;
    updateBlockJobState(null);
    updatePreflight();
  });
};

$('#hardwareForm').addEventListener('input', () => {
  const route = normalizeRoute($('#hardwareForm').elements.cable_confirmation.value);
  const warning = route && route !== 'RF1.1-RF1.5'
    ? (language === 'zh' ? `${route} 尚未由本 workflow 驗證，未送出 RF。` : `Route "${route}" is not workflow-verified; no RF was transmitted.`)
    : '';
  showHardwareAlert(warning, false);
  updatePreflight();
});

$('#customPlanForm').addEventListener('input', updateHardwareSummary);
$('#gprfPowerForm').addEventListener('input', updateHardwareSummary);

const baseRender = render;
render = function(data) {
  baseRender(data);
  const urls = data.artifact_urls || {};
  const labels = {csv: 'CSV', json: 'JSON', metadata: 'Metadata', raw: 'Raw SCPI', report: 'HTML Report'};
  const links = Object.entries(urls).map(([key, url]) =>
    `<a href="${url}" target="_blank" rel="noopener">${labels[key] || key}</a>`
  ).join('');
  const sourceLabel = data.simulated ? (language === 'zh' ? '示範資料' : 'DEMO DATA') : 'HARDWARE';
  const outputLabel = language === 'zh' ? '輸出位置' : 'Output location';
  const outputLocation = data.output_location ? escapeHtml(data.output_location) : '';
  $('#artifacts').innerHTML = links
    ? `<div><strong>${sourceLabel} artifacts</strong></div><div class="output-location"><span>${outputLabel}</span><code>${outputLocation}</code></div><div class="artifact-links">${links}</div>`
    : '';
};

applyLanguage();
loadHardwareStatus();
