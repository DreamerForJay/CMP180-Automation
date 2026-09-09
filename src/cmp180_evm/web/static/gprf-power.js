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
  sa_safe_limit_dbm: 0
};

function gprfHz(mhz) {
  // GPRF 表單固定用 MHz，後端與 SCPI 一律接收 Hz，避免單位誤送。
  return Number(mhz) * 1e6;
}

function gprfFormatFrequency(hz) {
  return hz >= 1e9 ? `${(hz / 1e9).toFixed(3)} GHz` : `${(hz / 1e6).toFixed(1)} MHz`;
}

function configureGprfFields() {
  const form = $('#gprfPowerForm').elements;
  const frequencyAxis = form.axis.value === 'frequency';
  $('#gprfFixedPowerField').hidden = !frequencyAxis;
  $('#gprfFixedFrequencyField').hidden = frequencyAxis;
  $('#gprfStartUnit').textContent = frequencyAxis ? 'MHz' : 'dBm';
  $('#gprfStopUnit').textContent = frequencyAxis ? 'MHz' : 'dBm';
  $('#gprfStepUnit').textContent = frequencyAxis ? 'MHz' : 'dB';
  form.start.value = frequencyAxis ? 400 : -80;
  form.stop.value = frequencyAxis ? 8000 : 20;
  form.step.value = frequencyAxis ? 100 : 5;
  $('#gprfModeTitle').textContent = frequencyAxis
    ? (language === 'zh' ? 'RF 功率讀值頻率掃描（GPRF）' : 'RF Power vs Frequency (GPRF)')
    : (language === 'zh' ? 'RF 功率讀值功率掃描（GPRF）' : 'RF Power vs Generator Power (GPRF)');
  // Axis 改變後同步頁首與執行摘要，避免仍顯示上一種掃描名稱。
  updateHardwareSummary();
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
  gprfPlanPayload = null;
  gprfPlanResult = null;
  $('#gprfPowerPreview').hidden = true;
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
  if (axis === 'frequency') {
    payload.start_hz = gprfHz(form.get('start'));
    payload.stop_hz = gprfHz(form.get('stop'));
    payload.step_hz = gprfHz(form.get('step'));
    payload.power_dbm = Number(form.get('power_dbm'));
  } else {
    payload.frequency_hz = gprfHz(form.get('frequency_mhz'));
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
    ? `${gprfFormatFrequency(first)} → ${gprfFormatFrequency(last)}`
    : `${first} dBm → ${last} dBm`;
  const fixed = data.axis === 'frequency'
    ? `${language === 'zh' ? '固定功率' : 'Fixed power'}: ${data.power_dbm} dBm`
    : `${language === 'zh' ? '固定頻率' : 'Fixed frequency'}: ${gprfFormatFrequency(data.frequency_hz)}`;
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
});

$('#loadPaProfileButton').onclick = loadApprovedPaProfile;

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
  if (normalizeRoute(hardwareForm.cable_confirmation.value) !== 'RF1.1-RF1.5' || !hardwareForm.operator_present.checked) {
    toast(language === 'zh' ? '請先完成接線與人在現場確認。' : 'Complete cabling and operator preflight first.', 'error');
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
window.configureGprfFields = configureGprfFields;
window.loadApprovedPaProfile = loadApprovedPaProfile;
