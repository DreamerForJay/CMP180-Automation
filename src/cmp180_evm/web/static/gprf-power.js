let gprfPlanPayload = null;
let gprfPlanResult = null;

const approvedPaProfile = {
  axis: 'power',
  start: -55,
  stopWithoutAttenuator: -25,
  approvedStop: -20,
  step: 1,
  frequency_mhz: 6105,
  dwell_ms: 200,
  expected_dut_gain_db: 25,
  output_attenuator_db: 0,
  sa_safe_limit_dbm: 0,
  dut_max_input_dbm: -20
};

// UDBox 0630 規劃範例；數值與 configs/udbox_sweep.example.yaml 對齊，改一邊要同時改另一邊。
const udboxPlan = {
  axis: 'power',
  start: -20,
  stop: 8,
  step: 1,
  frequency_mhz: 1000,
  dwell_ms: 200,
  expected_dut_gain_db: -10,
  output_attenuator_db: 10,
  sa_safe_limit_dbm: 0,
  dut_max_input_dbm: 13,
  conversion_direction: 'up',
  conversion_sideband: 'high',
  conversion_lo_mhz: 6000
};

// GPRF 表單固定用 MHz；改呼叫 app.js 共用的 frequencyToHz(value,'MHz')／formatFrequency。

function configureGprfFields() {
  const form = $('#gprfPowerForm').elements;
  const frequencyAxis = form.axis.value === 'frequency';
  $('#gprfFixedPowerField').hidden = !frequencyAxis;
  $('#gprfFixedFrequencyField').hidden = frequencyAxis;
  $('#gprfStartUnit').textContent = frequencyAxis ? 'MHz' : 'dBm';
  $('#gprfStopUnit').textContent = frequencyAxis ? 'MHz' : 'dBm';
  $('#gprfStepUnit').textContent = frequencyAxis ? 'MHz' : 'dB';
  form.start.value = frequencyAxis ? 400 : -80;
  // CMP180 generator 上限 +8 dBm，預設 stop 不可再用 +20；改用安全的 -25 dBm。
  form.stop.value = frequencyAxis ? 8000 : -25;
  form.step.value = frequencyAxis ? 100 : 5;
  $('#gprfModeTitle').textContent = frequencyAxis
    ? (language === 'zh' ? 'RF 功率讀值頻率掃描（GPRF）' : 'RF Power vs Frequency (GPRF)')
    : (language === 'zh' ? 'RF 功率讀值功率掃描（GPRF）' : 'RF Power vs Generator Power (GPRF)');
  // Axis 改變後同步頁首與執行摘要，避免仍顯示上一種掃描名稱。
  updateHardwareSummary();
}

function configureConversionFields() {
  const form = $('#gprfPowerForm').elements;
  const enabled = form.conversion_enabled.checked;
  // 未勾選時隱藏並不送出 conversion；後端沒有 conversion 就維持兩端同頻。
  $('#gprfConversionDirectionField').hidden = !enabled;
  $('#gprfConversionSidebandField').hidden = !enabled;
  $('#gprfConversionLoField').hidden = !enabled;
}

function loadUdboxPlan() {
  const form = $('#gprfPowerForm').elements;
  form.axis.value = udboxPlan.axis;
  configureGprfFields();
  form.start.value = udboxPlan.start;
  form.stop.value = udboxPlan.stop;
  form.step.value = udboxPlan.step;
  form.frequency_mhz.value = udboxPlan.frequency_mhz;
  form.dwell_ms.value = udboxPlan.dwell_ms;
  form.input_cable_loss_db.value = 0;
  form.output_cable_loss_db.value = 0;
  form.external_gain_db.value = 0;
  form.expected_dut_gain_db.value = udboxPlan.expected_dut_gain_db;
  form.output_attenuator_db.value = udboxPlan.output_attenuator_db;
  form.sa_safe_limit_dbm.value = udboxPlan.sa_safe_limit_dbm;
  form.dut_max_input_dbm.value = udboxPlan.dut_max_input_dbm;
  form.conversion_enabled.checked = true;
  form.conversion_direction.value = udboxPlan.conversion_direction;
  form.conversion_sideband.value = udboxPlan.conversion_sideband;
  form.conversion_lo_mhz.value = udboxPlan.conversion_lo_mhz;
  configureConversionFields();
  gprfPlanPayload = null;
  gprfPlanResult = null;
  $('#gprfPowerPreview').hidden = true;
  // 程式化填值不會觸發 input；最後統一刷新摘要，避免顯示載入前的掃描範圍。
  updateHardwareSummary();
  toast(language === 'zh'
    ? ' 已載入 UDBox 0630 規劃範例：IF 1000 MHz + LO 6000 MHz → RF 7000 MHz。此範例量得到 conversion gain 與平坦度，但 generator 上限 +8 dBm 不足以推到 P1dB。'
    : 'UD Box 0630 planning example loaded: IF 1000 MHz + LO 6000 MHz to RF 7000 MHz. It measures conversion gain and flatness; the +8 dBm generator ceiling cannot reach P1dB.');
}

function loadApprovedPaProfile() {
  const form = $('#gprfPowerForm').elements;
  // Web 快速鍵採用 profile 的安全預設：未填實體輸出衰減器時，依 25 dB DUT gain 將 stop 裁切到 RF1.5 0 dBm safe limit。
  form.axis.value = approvedPaProfile.axis;
  configureGprfFields();
  form.start.value = approvedPaProfile.start;
  form.stop.value = approvedPaProfile.stopWithoutAttenuator;
  form.step.value = approvedPaProfile.step;
  form.frequency_mhz.value = approvedPaProfile.frequency_mhz;
  form.dwell_ms.value = approvedPaProfile.dwell_ms;
  form.input_cable_loss_db.value = 0;
  form.output_cable_loss_db.value = 0;
  form.external_gain_db.value = 0;
  form.expected_dut_gain_db.value = approvedPaProfile.expected_dut_gain_db;
  form.output_attenuator_db.value = approvedPaProfile.output_attenuator_db;
  form.sa_safe_limit_dbm.value = approvedPaProfile.sa_safe_limit_dbm;
  form.dut_max_input_dbm.value = approvedPaProfile.dut_max_input_dbm;
  // PA 是同頻 DUT；載入 PA profile 必須清掉 converter 設定，避免殘留上一次的 LO。
  form.conversion_enabled.checked = false;
  configureConversionFields();
  gprfPlanPayload = null;
  gprfPlanResult = null;
  $('#gprfPowerPreview').hidden = true;
  // 程式化填值不會觸發 input；最後統一刷新摘要，避免顯示載入前的掃描範圍。
  updateHardwareSummary();
  toast(language === 'zh'
    ? `已載入 approved PA profile：未接衰減器先掃 ${approvedPaProfile.start} → ${approvedPaProfile.stopWithoutAttenuator} dBm；若現場有受控衰減器，可調整 Output attenuator 後再檢查計畫。`
    : `Approved PA profile loaded: without an output attenuator, sweep ${approvedPaProfile.start} to ${approvedPaProfile.stopWithoutAttenuator} dBm first. Adjust Output attenuator for a controlled fixture before reviewing the plan.`);
}

function buildGprfPayload() {
  const form = new FormData($('#gprfPowerForm'));
  const axis = form.get('axis');
  const payload = {
    axis,
    dwell_ms: Number(form.get('dwell_ms')),
    input_cable_loss_db: Number(form.get('input_cable_loss_db')),
    output_cable_loss_db: Number(form.get('output_cable_loss_db')),
    external_gain_db: Number(form.get('external_gain_db')),
    expected_dut_gain_db: Number(form.get('expected_dut_gain_db')),
    output_attenuator_db: Number(form.get('output_attenuator_db')),
    external_attenuation_db: 0,
    sa_safe_limit_dbm: Number(form.get('sa_safe_limit_dbm'))
  };
  // 空字串代表「路徑上沒有 DUT」；不可送成 0，那會被當成一個真實的 0 dBm 上限。
  const dutMaxInput = form.get('dut_max_input_dbm');
  if (dutMaxInput !== null && String(dutMaxInput).trim() !== '') {
    payload.dut_max_input_dbm = Number(dutMaxInput);
  }
  if (form.get('conversion_enabled')) {
    payload.conversion = {
      direction: form.get('conversion_direction'),
      sideband: form.get('conversion_sideband'),
      lo_frequency_hz: frequencyToHz(form.get('conversion_lo_mhz'), 'MHz')
    };
  }
  if (axis === 'frequency') {
    payload.start_hz = frequencyToHz(form.get('start'), 'MHz');
    payload.stop_hz = frequencyToHz(form.get('stop'), 'MHz');
    payload.step_hz = frequencyToHz(form.get('step'), 'MHz');
    payload.power_dbm = Number(form.get('power_dbm'));
  } else {
    payload.frequency_hz = frequencyToHz(form.get('frequency_mhz'), 'MHz');
    payload.start_dbm = Number(form.get('start'));
    payload.stop_dbm = Number(form.get('stop'));
    payload.step_dbm = Number(form.get('step'));
  }
  return payload;
}

function renderGprfPreview(data) {
  const preview = $('#gprfPowerPreview');
  const first = data.points?.[0];
  const last = data.points?.[data.points.length - 1];
  const range = data.axis === 'frequency'
    ? `${formatFrequency(first)} → ${formatFrequency(last)}`
    : `${first} dBm → ${last} dBm`;
  const fixed = data.axis === 'frequency'
    ? `${language === 'zh' ? '固定功率' : 'Fixed power'}: ${data.power_dbm} dBm`
    : `${language === 'zh' ? '固定頻率' : 'Fixed frequency'}: ${formatFrequency(data.frequency_hz)}`;
  const pinRange = data.pin_start_dbm === null
    ? ''
    : `${language === 'zh' ? 'DUT Pin 範圍' : 'DUT Pin range'}: ${data.pin_start_dbm.toFixed(2)} → ${data.pin_stop_dbm.toFixed(2)} dBm`;
  const compensation = language === 'zh'
    ? `補償：Input loss ${data.input_cable_loss_db} dB，Output loss ${data.output_cable_loss_db} dB，External gain ${data.external_gain_db} dB，Expected DUT gain ${data.expected_dut_gain_db} dB，Output attenuator ${data.output_attenuator_db} dB，Measurement EATT ${data.external_attenuation_db} dB，SA limit ${data.sa_safe_limit_dbm} dBm`
    : `Compensation: input loss ${data.input_cable_loss_db} dB, output loss ${data.output_cable_loss_db} dB, external gain ${data.external_gain_db} dB, expected DUT gain ${data.expected_dut_gain_db} dB, output attenuator ${data.output_attenuator_db} dB, measurement EATT ${data.external_attenuation_db} dB, SA limit ${data.sa_safe_limit_dbm} dBm`;
  preview.hidden = false;
  const title = data.axis === 'frequency'
    ? (language === 'zh' ? 'RF 功率讀值頻率掃描（GPRF）' : 'RF Power vs Frequency (GPRF)')
    : (language === 'zh' ? 'RF 功率讀值功率掃描（GPRF）' : 'RF Power vs Generator Power (GPRF)');
  preview.textContent = language === 'zh' ? [
    title,
    `點數：${data.point_count}`,
    `範圍：${range}`,
    fixed,
    pinRange,
    compensation,
    `停留時間：${data.dwell_ms} ms`,
    data.execution_allowed
      ? '可執行：僅讀取 RF 功率，不是 WLAN EVM。'
      : window.formatPlanRejection(data, 'GPRF workflow 拒絕此計畫', 'gprf')
  ].join('\n') : [
    title,
    `Points: ${data.point_count}`,
    `Range: ${range}`,
    fixed,
    pinRange,
    compensation,
    `Dwell: ${data.dwell_ms} ms`,
    data.execution_allowed
      ? (language === 'zh' ? '可執行：RF 功率讀值，不是 WLAN EVM。' : 'Executable: RF power reading only, not WLAN EVM.')
      : window.formatPlanRejection(data, 'GPRF workflow rejected the plan', 'gprf')
  ].join('\n');
}

window.addEventListener('cmp180-language-change', () => {
  // 語言切換只重繪已驗證計畫；不控制儀器、不重新執行 preview。
  if (gprfPlanResult) renderGprfPreview(gprfPlanResult);
});

async function reviewGprfPlan(button = null) {
  const payload = buildGprfPayload();
  if (button) button.disabled = true;
  try {
    const response = await fetch('/api/hardware/gprf-power-preview', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'GPRF plan validation failed');
    gprfPlanPayload = payload;
    gprfPlanResult = data;
    renderGprfPreview(data);
    return data;
  } finally {
    if (button) button.disabled = false;
  }
}

$('#gprfPowerForm').addEventListener('change', event => {
  if (event.target.name === 'axis') configureGprfFields();
  if (event.target.name === 'conversion_enabled') configureConversionFields();
});

$('#loadPaProfileButton').onclick = loadApprovedPaProfile;
$('#loadUdboxPlanButton').onclick = loadUdboxPlan;

$('#gprfPowerForm').onsubmit = async event => {
  event.preventDefault();
  try {
    await reviewGprfPlan(event.submitter);
  } catch (error) {
    toast(error.message, 'error');
  }
};

window.reviewAndExecuteGprfPowerPlan = async function(button) {
  let data;
  try {
    data = await reviewGprfPlan(button);
  } catch (error) {
    toast(error.message, 'error');
    return;
  }
  if (!data.execution_allowed) {
    toast(language === 'zh' ? 'GPRF 計畫未通過檢查，未送出 RF。' : 'GPRF plan is blocked; no RF transmitted.', 'error');
    return;
  }
  const hardwareForm = $('#hardwareForm').elements;
  // 與 hardware.js 同一份能力判定：只擋軟體驅動不了的接線，不再比對單一路徑。
  const routeCheck = checkRoute(hardwareForm.cable_confirmation.value);
  if (!routeCheck.ok || !hardwareForm.operator_present.checked) {
    toast(routeCheck.ok
      ? (language === 'zh' ? '請先確認操作員在現場。' : 'Confirm operator presence first.')
      : routeCheck.reason, 'error');
    return;
  }
  // GPRF 會開真實 RF，但不使用 WLAN measurement；確認文字必須把能力邊界講清楚。
  const runTitle = data.axis === 'frequency'
    ? (language === 'zh' ? 'RF 功率讀值頻率掃描（GPRF）' : 'RF Power vs Frequency (GPRF)')
    : (language === 'zh' ? 'RF 功率讀值功率掃描（GPRF）' : 'RF Power vs Generator Power (GPRF)');
  const approved = confirm(language === 'zh'
    ? `即將送出真實 RF 進行 ${runTitle}\n\n${$('#gprfPowerPreview').textContent}\n\n確認這不是 WLAN EVM，接線未變、人在儀器旁並開始？`
    : `Real RF will be transmitted for ${runTitle}\n\n${$('#gprfPowerPreview').textContent}\n\nConfirm this is not WLAN EVM, cabling is unchanged, and an operator is present?`);
  if (!approved) {
    toast(language === 'zh' ? '已取消，未送出 RF。' : 'Cancelled; no RF was transmitted.');
    return;
  }
  startJob('/api/jobs/hardware/gprf-power-sweep', {
    ...gprfPlanPayload,
    cable_confirmation: hardwareForm.cable_confirmation.value,
    operator_present: hardwareForm.operator_present.checked,
    gprf_confirmation: 'GPRF-POWER-NOT-WLAN-EVM'
  }, button, data.axis);
};

configureGprfFields();
configureConversionFields();
window.configureGprfFields = configureGprfFields;
window.configureConversionFields = configureConversionFields;
window.loadApprovedPaProfile = loadApprovedPaProfile;
window.loadUdboxPlan = loadUdboxPlan;
