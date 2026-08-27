Object.assign(translations.zh, {
  hardwareTab: '實機量測',
  hardwareTitle: '實機量測',
  hardwareHelp: '選擇量測、設定參數並完成執行前檢查。',
  rfWarning: 'RF 輸出',
  rfWarningText: '送出前確認接線與輸入功率；異常時系統會停止量測並關閉 RF。',
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
  ,hardwareControlHint: '待執行前安全確認'
  ,serverLockedTitle: '實機控制未啟用'
  ,serverLockedText: '請以 `python -m cmp180_evm.web --host 127.0.0.1 --port 8765 --enable-hardware` 重新啟動服務。'
});

Object.assign(translations.en, {
  hardwareTab: 'Hardware Measurement',
  hardwareTitle: 'Hardware Measurement',
  hardwareHelp: 'Select a measurement, configure parameters, and complete preflight.',
  rfWarning: 'RF output',
  rfWarningText: 'Confirm cabling and input power before execution. An anomaly stops measurement and turns RF off.',
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
  ,hardwareControlHint: 'Preflight required before execution'
  ,serverLockedTitle: 'Hardware control is disabled'
  ,serverLockedText: 'Restart with `python -m cmp180_evm.web --host 127.0.0.1 --port 8765 --enable-hardware`.'
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
  const blocked = !hardwareEnabled || !routeVerified || !operatorPresent || hardwareRequestRunning;
  $('#hardwareButton').disabled = blocked;
  $('#blockRunButton').disabled = blocked;
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

const hardwareProfiles = {
  single: {title: 'SingleShot', detail: '6105 MHz · 320 MHz · -40 dBm'},
  frequency: {title: 'Frequency Sweep', detail: '6085 / 6105 / 6125 MHz · 320 MHz · -40 dBm'},
  power: {title: 'Power Sweep', detail: '6105 MHz · 320 MHz · -55 / -50 / -45 / -40 dBm'}
};

function selectHardwareAction(action) {
  const form = $('#hardwareForm');
  if (!hardwareProfiles[action]) return;
  form.elements.hardware_action.value = action;
  document.querySelectorAll('[data-hardware-action]').forEach(button => {
    button.classList.toggle('active', button.dataset.hardwareAction === action);
  });
  const profile = hardwareProfiles[action];
  $('#hardwareProfileSummary').innerHTML = `<small>${language === 'zh' ? '目前設定' : 'Profile'}</small><strong>${profile.title}</strong><span>${profile.detail}</span>`;
  const setup = $('#hardwareSweepSetup');
  setup.hidden = action === 'single';
  setup.open = action !== 'single';
  // 實機分頁與自訂掃描共用同一個安全驗證模型，切換時同步掃描軸但不送出 RF。
  if (action !== 'single') $('#customPlanForm').elements.axis.value = action;
}

document.querySelectorAll('[data-hardware-action]').forEach(button => {
  button.addEventListener('click', () => selectHardwareAction(button.dataset.hardwareAction));
});
selectHardwareAction('single');

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
  const action = form.get('hardware_action');
  const profileSummary = action === 'frequency'
    ? 'Frequency Sweep · 6085 / 6105 / 6125 MHz · 320 MHz · -40 dBm'
    : action === 'power'
      ? 'Power Sweep · 6105 MHz · 320 MHz · -55 / -50 / -45 / -40 dBm'
      : 'SingleShot · 6105 MHz · 320 MHz · -40 dBm';
  // 最後一次確認留在 Web 內完成，摘要顯示真正將送出的固定 profile，避免誤按或選錯模式。
  const approved = confirm(language === 'zh'
    ? `即將送出真實 RF\n\n${profileSummary}\nRoute: ${route}\n\n確認接線未變、操作員在場並開始量測？`
    : `Real RF will be transmitted\n\n${profileSummary}\nRoute: ${route}\n\nConfirm unchanged cabling, operator presence, and start?`);
  if (!approved) {
    toast(language === 'zh' ? '已取消，未送出 RF。' : 'Cancelled; no RF was transmitted.');
    return;
  }
  showHardwareAlert('');
  hardwareRequestRunning = true;
  updateBlockJobState({state: 'running'});
  updatePreflight();
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
    updateBlockJobState(null);
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
