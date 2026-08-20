Object.assign(translations.zh, {
  hardwareTab: '實機量測',
  hardwareTitle: 'CMP180 實機量測',
  hardwareHelp: '提供已驗證的 SingleShot、頻率掃描與功率掃描固定 profile。',
  rfWarning: '此動作會產生真實 RF',
  rfWarningText: '只有在線材已確認且操作員位於儀器旁時才能執行。錯誤時會 STOP/ABORT 並 RF Off。',
  cableText: '接線路徑（可選擇或輸入）',
  cablePlaceholder: '例如 RF1.1-RF1.5',
  cableVerifiedOption: '已驗證：RF1.1 → RF1.5',
  cableHelp: '可輸入自訂路徑；未驗證路徑會顯示警示且禁止 RF 輸出。',
  operatorPresent: '我人在 CMP180 旁並能觀察儀器',
  runHardware: '執行實機量測',
  preflightTitle: '執行前安全檢查',
  routeCheck: '接線符合已驗證路徑',
  operatorCheck: '操作員在儀器旁'
  ,hardwareBadge: '實機模式'
  ,hardwareControlState: '已啟用實機控制'
  ,hardwareControlHint: '僅允許已驗證的固定 profile'
  ,serverLockedTitle: '此頁面目前無法使用'
  ,serverLockedText: '伺服器未以 --enable-hardware 啟動，目前是唯讀 Mock 模式。要開放這個頁面，需要在本機用 `python -m cmp180_evm.web --enable-hardware` 重新啟動伺服器，且只能綁定 loopback 位址。'
});

Object.assign(translations.en, {
  hardwareTab: 'Hardware Measurement',
  hardwareTitle: 'CMP180 Hardware Measurement',
  hardwareHelp: 'Provides fixed HIL-verified SingleShot, frequency-sweep, and power-sweep profiles.',
  rfWarning: 'This action produces real RF',
  rfWarningText: 'Run only with confirmed cabling and an operator beside the instrument. Errors trigger STOP/ABORT and RF Off.',
  cableText: 'Cable route (select or type)',
  cablePlaceholder: 'e.g. RF1.1-RF1.5',
  cableVerifiedOption: 'Verified: RF1.1 → RF1.5',
  cableHelp: 'Custom routes are accepted as input, but unverified routes trigger a warning and cannot enable RF.',
  operatorPresent: 'I am beside the CMP180 and can observe it',
  runHardware: 'Run hardware measurement',
  preflightTitle: 'Preflight safety checks',
  routeCheck: 'Route matches a verified cable path',
  operatorCheck: 'Operator is beside the instrument'
  ,hardwareBadge: 'Hardware Mode'
  ,hardwareControlState: 'Hardware control enabled'
  ,hardwareControlHint: 'Verified fixed profile only'
  ,serverLockedTitle: 'This page is currently unavailable'
  ,serverLockedText: 'The server was not started with --enable-hardware and is running in read-only mock mode. To use this page, restart the server locally with `python -m cmp180_evm.web --enable-hardware`; it may only bind to a loopback address.'
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

function updatePreflight() {
  const form = $('#hardwareForm');
  const routeVerified = normalizeRoute(form.elements.cable_confirmation.value) === 'RF1.1-RF1.5';
  const operatorPresent = form.elements.operator_present.checked;
  $('#routeCheck').classList.toggle('ok', routeVerified);
  $('#operatorCheck').classList.toggle('ok', operatorPresent);
  $('#hardwareButton').disabled = !hardwareEnabled || !routeVerified || !operatorPresent || hardwareRequestRunning;
}

async function loadHardwareStatus() {
  try {
    const response = await fetch('/api/status');
    const status = await response.json();
    hardwareEnabled = status.hardware_enabled === true;
    $('#hardwareBadge').textContent = hardwareEnabled ? 'ARMED' : 'LOCKED';
    $('#serverLockedNotice').hidden = hardwareEnabled;
    if (hardwareEnabled) {
      // 啟用實機 server 時改用紅色狀態，避免操作員誤認為 Mock。
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
    toast(`Status error: ${error.message}`);
  }
}

$('#hardwareForm').onsubmit = event => {
  event.preventDefault();
  const form = new FormData(event.target);
  if (!hardwareEnabled) {
    showHardwareAlert(language === 'zh' ? '實機模式未在伺服器啟動，禁止執行 RF。' : 'Hardware mode is locked at server startup.');
    return;
  }
  const route = normalizeRoute(form.get('cable_confirmation'));
  if (!route) {
    showHardwareAlert(language === 'zh' ? '請選擇或輸入接線路徑。' : 'Select or enter a cable route.');
    return;
  }
  if (route !== 'RF1.1-RF1.5') {
    showHardwareAlert(language === 'zh' ? `「${route}」尚未完成實機驗證，為保護儀器，本次禁止 RF 輸出。` : `Route "${route}" is not hardware-verified; RF output is blocked.`);
    return;
  }
  if (form.get('operator_present') !== 'on') {
    showHardwareAlert(language === 'zh' ? '請確認操作員在 CMP180 旁再執行。' : 'Confirm that an operator is beside the CMP180.');
    return;
  }
  if (hardwareRequestRunning) {
    showHardwareAlert(language === 'zh' ? '量測正在執行，請勿重複送出。' : 'A measurement is already running.');
    return;
  }
  showHardwareAlert('');
  hardwareRequestRunning = true;
  updatePreflight();
  const action = form.get('hardware_action');
  if (action === 'frequency' || action === 'power') {
    const profile = action === 'frequency' ? '6085-6125MHz' : '-55--40dBm';
    startJob(`/api/jobs/hardware/${action}-sweep`, {
      cable_confirmation: route,
      operator_present: true,
      sweep_confirmation: profile
    }, event.submitter, action).finally(() => {
      hardwareRequestRunning = false;
      updatePreflight();
    });
    return;
  }
  send('/api/hardware/single', {
    cable_confirmation: route,
    operator_present: form.get('operator_present') === 'on'
  }, event.submitter).finally(() => {
    hardwareRequestRunning = false;
    updatePreflight();
  });
};

$('#hardwareForm').addEventListener('input', () => {
  const route = normalizeRoute($('#hardwareForm').elements.cable_confirmation.value);
  const warning = route && route !== 'RF1.1-RF1.5'
    ? (language === 'zh' ? `「${route}」尚未完成實機驗證，為保護儀器，本次禁止 RF 輸出。` : `Route "${route}" is not hardware-verified; RF output is blocked.`)
    : '';
  showHardwareAlert(warning, false);
  updatePreflight();
});

$('#hardwareForm').elements.cable_confirmation.addEventListener('change', event => {
  const route = normalizeRoute(event.target.value);
  if (route && route !== 'RF1.1-RF1.5') {
    showHardwareAlert(language === 'zh' ? `「${route}」尚未完成實機驗證，為保護儀器，本次禁止 RF 輸出。` : `Route "${route}" is not hardware-verified; RF output is blocked.`);
  }
});

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
