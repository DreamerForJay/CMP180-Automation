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
let singlePlanPayload = null;
let singlePlanResult = null;

function normalizeRoute(value) {
  return String(value || '').trim().toUpperCase().replaceAll('→', '-').replaceAll(' ', '');
}

function showHardwareAlert(message, notify = true) {
  const alert = $('#hardwareAlert');
  alert.textContent = message;
  alert.hidden = !message;
  if (message && notify) toast(message, 'error');
}

function localizePlanDetail(value) {
  if (language !== 'zh' || !value) return value;
  const exact = {
    'Move the center/sweep frequencies into an approved WLAN section for the selected bandwidth.': '把中心／掃描頻率移到所選頻寬已核准的 WLAN 區段內。',
    'Choose one of the HIL-approved WLAN bandwidths and review the plan again.': '選擇已通過 HIL 的 WLAN 頻寬，再重新檢查計畫。',
    'Keep generator power inside the approved HIL envelope; for DUT/UDBox, obtain path-loss data first.': 'Generator 功率需保持在已核准 HIL 範圍內；DUT／UDBox 應先取得 Path Loss 資料。',
    'Set dwell to the approved range so each point has enough settling time without overextending RF exposure.': '把停留時間設在核准範圍內，讓每點充分穩定且不延長 RF 暴露。',
    'Reduce sweep span, increase step size, or split the run into smaller approved campaigns.': '縮小掃描範圍、增加步進，或拆成較小的核准批次。',
    'Adjust the rejected field and run Review again; no RF is transmitted until the gate passes.': '修正遭拒欄位並重新檢查；安全閘門通過前不會送出 RF。',
    'Set every RF point inside the CMP180 GPRF planning range, then review again.': '把每個 RF 點設在 CMP180 GPRF 規劃範圍內，再重新檢查。',
    'Reduce the generator level or sweep endpoints to the accepted GPRF power range.': '降低 Generator level 或掃描端點，使其落在 GPRF 接受功率範圍內。',
    'Use a dwell time that is long enough for settling but inside the approved UI guard.': '使用足以穩定且仍在 UI 核准防護範圍內的停留時間。',
    'Adjust the highlighted plan field and review again before enabling RF.': '修正標示的計畫欄位，在啟用 RF 前重新檢查。'
  };
  if (exact[value]) return exact[value];
  if (value.startsWith('CMP180 UI planning range is ')) return 'CMP180 UI 規劃範圍為 400 MHz..8 GHz；WLAN EVM RF 執行仍限 RF1.1-RF1.5、已核准 WLAN 區段、20/40/80/160/320 MHz 頻寬、Generator 功率 -55..-30 dBm、停留時間 100..2000 ms，以及核准的點數／跨度。';
  if (value.startsWith('Frequency 400 MHz..8 GHz; generator power ')) return '頻率 400 MHz..8 GHz；Generator 功率 -80..20 dBm；停留時間 50..5000 ms；最多 401 點。';
  // 後端安全閘門以英文保存稽核原因；畫面只翻譯顯示文字，不改動原始回應或判定。
  return value
    .replace(/^(\d+) MHz is outside every supported WLAN band; the instrument tunes 400–8 GHz but WLAN measurement needs a band$/, '$1 MHz 不在任何支援的 WLAN 頻段內；儀器可調諧 400 MHz–8 GHz，但 WLAN 量測必須落在有效頻段內')
    .replace(/^Frequency\/bandwidth combination is outside the approved WLAN sections for (.+)$/, '頻率／頻寬組合不在 $1 的已核准 WLAN 區段內')
    .replace(/^Route (.+) is not included in approved profile (.+)$/, 'Route $1 不在核准 profile $2 內')
    .replace(/^Sweep span exceeds approved (.+)$/, '掃描跨度超過核准值 $1')
    .replace(/^Bandwidth (.+) is not HIL-approved$/, '頻寬 $1 尚未通過 HIL 核准')
    .replace(/^Bandwidth (.+) is not installed$/, '本機未安裝頻寬 $1')
    .replace(/^Generator power is outside approved (.+)$/, 'Generator 功率超出核准範圍 $1')
    .replace(/^Dwell must stay within approved (.+)$/, '停留時間必須位於核准範圍 $1')
    .replace(/^Plan exceeds the approved (.+)$/, '計畫超出核准的 $1')
    .replace(/^SingleShot frequency must stay within the CMP180 (.+)$/, 'SingleShot 頻率必須位於 CMP180 $1')
    .replace(/^Frequency exceeds CMP180 GPRF planning range (.+)$/, '頻率超出 CMP180 GPRF 規劃範圍 $1')
    .replace(/^Generator power must stay within (.+)$/, 'Generator 功率必須位於 $1')
    .replace(/^Power sweep exceeds (.+) planning range$/, '功率掃描超出 $1 規劃範圍');
}
window.localizePlanDetail = localizePlanDetail;

function formatPlanRejection(data, fallback, family = 'wlan') {
  const reason = localizePlanDetail(data.rejection_reason || fallback);
  const help = localizePlanDetail(data.rejection_help || (family === 'gprf'
    ? '把頻率、功率、停留時間或點數改回 CMP180 GPRF 規劃範圍後重新 Review。'
    : '把頻率、頻寬、功率、接線或點數改回目前 approved/HIL profile 後重新 Review。'));
  const range = localizePlanDetail(data.correct_range || (family === 'gprf'
    ? 'Frequency 400 MHz..8 GHz；Power -80..20 dBm；Dwell 50..5000 ms；最多 401 點。'
    : 'UI 可規劃 400 MHz..8 GHz；WLAN EVM 送 RF 仍限 approved WLAN sections、RF1.1-RF1.5、-55..-30 dBm。'));
  // 異常訊息要同時給原因、修正方式與正確範圍，避免操作員靠猜測調參數。
  return language === 'zh'
    ? `不可執行\n原因：${reason}\n如何解決：${help}\n正確範圍：${range}`
    : `Blocked\nReason: ${reason}\nHow to fix: ${help}\nValid range: ${range}`;
}
window.formatPlanRejection = formatPlanRejection;

function updateHardwareSummary() {
  const action = $('#hardwareForm').elements.hardware_action.value;
  const form = $('#customPlanForm')?.elements;
  const single = $('#singlePlanForm')?.elements;
  let detail = single ? `${single.center_frequency.value} ${single.center_unit.value} · ${single.bandwidth_mhz.value} MHz · ${single.generator_power_dbm.value} dBm` : '6105 MHz · 320 MHz · -40 dBm';
  let planCheck = language === 'zh'
    ? 'WLAN EVM 單點：先 Review；執行時採用畫面輸入並由後端重新驗證'
    : 'WLAN EVM SingleShot: review first; execution revalidates the entered values';
  let title = language === 'zh' ? 'WLAN EVM 單點量測' : 'WLAN EVM SingleShot';
  if (form && action === 'frequency') {
    title = language === 'zh' ? 'WLAN EVM 頻率掃描' : 'WLAN EVM Frequency Sweep';
    detail = `${form.start.value} ${form.start_unit.value} → ${form.stop.value} ${form.stop_unit.value} · Step ${form.step.value} ${form.step_unit.value} · ${form.bandwidth_mhz.value} MHz · ${form.generator_power_dbm.value} dBm`;
    planCheck = language === 'zh'
      ? 'WLAN EVM 頻率掃描：先 Review；只允許通過 approved section 的中心頻率'
      : 'WLAN EVM Frequency Sweep: review first; only approved WLAN sections can transmit RF';
  }
  if (form && action === 'power') {
    title = language === 'zh' ? 'WLAN EVM 功率掃描－線性度' : 'WLAN EVM Power Sweep – Linearity';
    detail = `${form.start.value} → ${form.stop.value} dBm · Step ${form.step.value} dB · ${form.center_frequency_mhz.value} ${form.center_unit.value} · ${form.bandwidth_mhz.value} MHz`;
    planCheck = language === 'zh'
      ? 'WLAN EVM 功率掃描：先 Review；使用已核准 WLAN section 與安全功率'
      : 'WLAN EVM Power Sweep: review first; use approved WLAN section and safe power';
  }
  if (action === 'gprf') {
    const gprf = $('#gprfPowerForm')?.elements;
    title = gprf?.axis.value === 'frequency'
      ? (language === 'zh' ? 'RF 功率讀值頻率掃描（GPRF）' : 'RF Power vs Frequency (GPRF)')
      : (language === 'zh' ? 'RF 功率讀值功率掃描（GPRF）' : 'RF Power vs Generator Power (GPRF)');
    detail = gprf
      ? `${gprf.axis.value} · ${gprf.start.value} → ${gprf.stop.value} · Dwell ${gprf.dwell_ms.value} ms`
      : 'GPRF power only · not WLAN EVM';
    planCheck = language === 'zh'
      ? 'GPRF：只量 RF power，不是 WLAN EVM、不做 compliance 宣稱'
      : 'GPRF: RF power only, not WLAN EVM and not a compliance claim';
  }
  $('#hardwareProfileSummary').innerHTML = `<small>${language === 'zh' ? '目前設定' : 'Current plan'}</small><strong>${title}</strong><span>${detail}</span>`;
  // Review 文案跟著量測模式更新，避免操作員誤把 GPRF 掃描當成 WLAN EVM。
  $('#planCheckText').textContent = planCheck;
  updatePageHeading();
}
window.updateHardwareSummary = updateHardwareSummary;

function updatePreflight() {
  const form = $('#hardwareForm');
  const action = form.elements.hardware_action.value;
  const routeVerified = normalizeRoute(form.elements.cable_confirmation.value) === 'RF1.1-RF1.5';
  const directCableConfirmed = form.elements.direct_cable_no_attenuator.checked;
  const directPathReady = action === 'gprf' || directCableConfirmed;
  const operatorPresent = form.elements.operator_present.checked;
  $('#routeCheck').classList.toggle('ok', routeVerified);
  $('#directCableCheck').classList.toggle('ok', directCableConfirmed);
  $('#operatorCheck').classList.toggle('ok', operatorPresent);
  const blocked = !hardwareEnabled || !routeVerified || !directPathReady || !operatorPresent || hardwareRequestRunning;
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
  $('#hardwareSingleSetup').hidden = action !== 'single';
  $('#hardwareSweepSetup').hidden = action === 'single' || action === 'gprf';
  $('#gprfPowerSetup').hidden = action !== 'gprf';
  if (action === 'frequency' || action === 'power') setCustomPlanAxis(action);
  updatePreflight();
}

document.querySelectorAll('[data-hardware-action]').forEach(button => {
  button.addEventListener('click', () => selectHardwareAction(button.dataset.hardwareAction));
});
selectHardwareAction('single');

// 單點 UI 可切 MHz/GHz；改呼叫 app.js 共用的 frequencyToHz，API 永遠接收 Hz。

function buildSinglePlanPayload() {
  const form = new FormData($('#singlePlanForm'));
  return {
    center_frequency_hz: frequencyToHz(form.get('center_frequency'), form.get('center_unit')),
    bandwidth_hz: Number(form.get('bandwidth_mhz')) * 1e6,
    generator_power_dbm: Number(form.get('generator_power_dbm'))
  };
}

async function reviewSinglePlan(button = null) {
  const payload = buildSinglePlanPayload();
  if (button) button.disabled = true;
  try {
    const response = await fetch('/api/hardware/single-plan-preview', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'SingleShot plan validation failed');
    singlePlanPayload = payload;
    singlePlanResult = data;
    renderSinglePlanPreview(data);
    return data;
  } finally {
    if (button) button.disabled = false;
  }
}

function renderSinglePlanPreview(data) {
  const frequency = `${(data.points[0] / 1e6).toLocaleString(undefined,{maximumFractionDigits:3})} MHz`;
  $('#singlePlanPreview').hidden = false;
  $('#singlePlanPreview').textContent = language === 'zh' ? [
      'SingleShot 檢查計畫',
      `中心頻率：${frequency}`,
      `頻寬：${data.bandwidth_hz / 1e6} MHz`,
      `Generator 功率：${data.generator_power_dbm} dBm`,
      data.execution_allowed
        ? `可執行：${data.band_supported === false ? '此組合不在標準 WLAN channel plan 內，可執行但結果可能為 INV。' : '在標準 WLAN channel plan 內。'}`
        : formatPlanRejection(data, 'workflow 拒絕此計畫', 'wlan')
    ].join('\n') : [
      'SingleShot',
      `Center frequency: ${frequency}`,
      `Bandwidth: ${data.bandwidth_hz / 1e6} MHz`,
      `Generator power: ${data.generator_power_dbm} dBm`,
      data.execution_allowed
        ? `Executable: ${data.band_supported === false ? 'outside the standard WLAN channel plan; the run is allowed but may return INV.' : 'inside the standard WLAN channel plan.'}`
        : formatPlanRejection(data, 'workflow rejected the plan', 'wlan')
    ].join('\n');
}

window.addEventListener('cmp180-language-change', () => {
  // Preview 使用已驗證的回應重繪，不重新呼叫 API，也不產生任何 SCPI 副作用。
  if (singlePlanResult) renderSinglePlanPreview(singlePlanResult);
});

$('#singlePlanForm').onsubmit = async event => {
  event.preventDefault();
  try {
    await reviewSinglePlan(event.submitter);
  } catch (error) {
    toast(error.message, 'error');
  }
};

document.querySelector('[data-single-unit]').addEventListener('click', event => {
  const form = $('#singlePlanForm').elements;
  const previous = form.center_unit.value;
  const next = previous === 'GHz' ? 'MHz' : 'GHz';
  const hz = frequencyToHz(form.center_frequency.value, previous);
  form.center_frequency.value = Math.round((hz / (next === 'GHz' ? 1e9 : 1e6)) * 1e6) / 1e6;
  form.center_unit.value = next;
  event.currentTarget.textContent = next;
  form.center_frequency.min = next === 'GHz' ? 0.4 : 400;
  form.center_frequency.max = next === 'GHz' ? 8 : 8000;
  updateHardwareSummary();
});

$('#hardwareForm').onsubmit = async event => {
  event.preventDefault();
  const form = new FormData(event.target);
  if (!hardwareEnabled) {
    showHardwareAlert(language === 'zh' ? '實機控制未啟用，未送出 RF。' : 'Hardware mode is locked; no RF was transmitted.');
    return;
  }
  const route = normalizeRoute(form.get('cable_confirmation'));
  const action = form.get('hardware_action');
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
  if (action !== 'gprf' && form.get('direct_cable_no_attenuator') !== 'on') {
    showHardwareAlert(language === 'zh' ? '請確認直接線路沒有未登錄的衰減器或轉接件。' : 'Confirm that the direct path has no unrecorded attenuator or adapter.');
    return;
  }
  if (hardwareRequestRunning) {
    showHardwareAlert(language === 'zh' ? '已有量測正在執行。' : 'A measurement is already running.');
    return;
  }
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
  let reviewed;
  try {
    // 送出前重新 Review；即使使用者在預覽後改欄位，fingerprint 也會跟著更新。
    reviewed = await reviewSinglePlan(event.submitter);
  } catch (error) {
    hardwareRequestRunning = false;
    updatePreflight();
    toast(error.message, 'error');
    return;
  }
  if (!reviewed.execution_allowed) {
    hardwareRequestRunning = false;
    updatePreflight();
    toast(language === 'zh' ? '單點計畫未通過 approved profile，未送出 RF。' : 'The SingleShot plan is outside the approved profile; no RF was transmitted.', 'error');
    return;
  }
  const summary = $('#singlePlanPreview').textContent;
  const approved = confirm(language === 'zh'
    ? `即將送出真實 RF\n\n${summary}\nRoute: ${route}\n\n確認接線未變、操作員在場並開始？`
    : `Real RF will be transmitted\n\n${summary}\nRoute: ${route}\n\nConfirm unchanged cabling, operator presence, and start?`);
  if (!approved) {
    hardwareRequestRunning = false;
    updatePreflight();
    toast(language === 'zh' ? '已取消，未送出 RF。' : 'Cancelled; no RF was transmitted.');
    return;
  }
  updateBlockJobState({state: 'running'});
  send('/api/hardware/single', {
    ...singlePlanPayload,
    cable_confirmation: route,
    operator_present: form.get('operator_present') === 'on',
    direct_cable_no_attenuator: form.get('direct_cable_no_attenuator') === 'on',
    execution_confirmation: reviewed.required_confirmation
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
$('#singlePlanForm').addEventListener('input', updateHardwareSummary);
$('#gprfPowerForm').addEventListener('input', updateHardwareSummary);

const baseRender = render;
render = function(data) {
  baseRender(data);
  const urls = data.artifact_urls || {};
  const labels = {csv: 'CSV', json: 'JSON', metadata: 'Metadata', raw: 'Raw SCPI', report: 'HTML Report', matplotlib_evm_all_carriers_db: 'Matplotlib EVM PNG', matplotlib_burst_power_dbm: 'Matplotlib Power PNG', matplotlib_frequency_error_hz: 'Matplotlib Frequency Error PNG', matplotlib_clock_error_ppm: 'Matplotlib Clock Error PNG'};
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
