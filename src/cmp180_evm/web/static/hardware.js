Object.assign(translations.zh, {
  hardwareTab: '實機單點',
  hardwareTitle: 'CMP180 實機 SingleShot',
  hardwareHelp: '固定使用已驗證的 RF1.1→RF1.5、6105 MHz、320 MHz、-40 dBm profile。',
  rfWarning: '此動作會產生真實 RF',
  rfWarningText: '只有在線材已確認且操作員位於儀器旁時才能執行。錯誤時會 STOP/ABORT 並 RF Off。',
  cableText: '接線路徑（可選擇或輸入）',
  cableHelp: '可輸入自訂路徑；未驗證路徑會顯示警示且禁止 RF 輸出。',
  operatorPresent: '我人在 CMP180 旁並能觀察儀器',
  runHardware: '執行實機 SingleShot',
  preflightTitle: '執行前安全檢查',
  routeCheck: '接線符合已驗證路徑',
  operatorCheck: '操作員在儀器旁'
  ,hardwareSafeTitle: '實機控制已解鎖'
  ,hardwareSafeText: '只有完成執行前檢查後才會向 CMP180 發送 RF 指令'
  ,hardwareIntro: 'Mock 流程、實機 SingleShot、結果輸出與圖表皆可使用；實機操作受安全檢查保護。'
  ,hardwareBadge: '實機模式'
});

Object.assign(translations.en, {
  hardwareTab: 'Hardware Single',
  hardwareTitle: 'CMP180 Hardware SingleShot',
  hardwareHelp: 'Uses only the verified RF1.1→RF1.5, 6105 MHz, 320 MHz, -40 dBm profile.',
  rfWarning: 'This action produces real RF',
  rfWarningText: 'Run only with confirmed cabling and an operator beside the instrument. Errors trigger STOP/ABORT and RF Off.',
  cableText: 'Cable route (select or type)',
  cableHelp: 'Custom routes are accepted as input, but unverified routes trigger a warning and cannot enable RF.',
  operatorPresent: 'I am beside the CMP180 and can observe it',
  runHardware: 'Run hardware SingleShot',
  preflightTitle: 'Preflight safety checks',
  routeCheck: 'Route matches a verified cable path',
  operatorCheck: 'Operator is beside the instrument'
  ,hardwareSafeTitle: 'Hardware controls armed'
  ,hardwareSafeText: 'RF commands are sent only after all preflight checks pass'
  ,hardwareIntro: 'Mock workflows, hardware SingleShot, artifacts, and plots are available with guarded RF controls.'
  ,hardwareBadge: 'Hardware Mode'
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
    if (hardwareEnabled) {
      // 啟用實機 server 時改用紅色狀態，避免操作員誤認為 Mock。
      const badge = document.querySelector('.status.mock');
      badge.dataset.i18n = 'hardwareBadge';
      badge.style.background = '#421a20';
      badge.style.color = '#ffb7bd';
      $('[data-i18n="safeTitle"]').dataset.i18n = 'hardwareSafeTitle';
      $('[data-i18n="safeText"]').dataset.i18n = 'hardwareSafeText';
      $('[data-i18n="intro"]').dataset.i18n = 'hardwareIntro';
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
  $('#artifacts').innerHTML = links
    ? `<div><strong>${data.simulated ? 'SIMULATED' : 'HARDWARE'} artifacts</strong></div><div class="artifact-links">${links}</div>`
    : '';
};

applyLanguage();
loadHardwareStatus();
