let gprfPlanPayload = null;
let gprfPlanResult = null;

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
    ? 'GPRF Frequency Sweep – Power Flatness / 頻率掃描－功率平坦度'
    : 'GPRF Power Sweep – Linearity / 功率掃描－線性度';
  // Axis 改變後同步頁首與執行摘要，避免仍顯示上一種掃描名稱。
  updateHardwareSummary();
}

function buildGprfPayload() {
  const form = new FormData($('#gprfPowerForm'));
  const axis = form.get('axis');
  const payload = {axis, dwell_ms: Number(form.get('dwell_ms'))};
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
    ? `Power: ${data.power_dbm} dBm`
    : `Frequency: ${gprfFormatFrequency(data.frequency_hz)}`;
  preview.hidden = false;
  preview.textContent = [
    data.axis === 'frequency' ? 'GPRF Frequency Sweep – Power Flatness' : 'GPRF Power Sweep – Linearity',
    `Points: ${data.point_count}`,
    `Range: ${range}`,
    fixed,
    `Dwell: ${data.dwell_ms} ms`,
    data.execution_allowed
      ? '可執行：GPRF power measurement，不是 WLAN EVM。'
      : `不可執行：${data.rejection_reason || 'GPRF workflow rejected the plan'}`
  ].join('\n');
}

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
  const approved = confirm(language === 'zh'
    ? `即將送出真實 RF 進行 ${data.axis === 'frequency' ? 'GPRF Frequency Sweep – Power Flatness' : 'GPRF Power Sweep – Linearity'}\n\n${$('#gprfPowerPreview').textContent}\n\n確認這不是 WLAN EVM，接線未變、人在儀器旁並開始？`
    : `Real RF will be transmitted for ${data.axis === 'frequency' ? 'GPRF Frequency Sweep – Power Flatness' : 'GPRF Power Sweep – Linearity'}\n\n${$('#gprfPowerPreview').textContent}\n\nConfirm this is not WLAN EVM, cabling is unchanged, and an operator is present?`);
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
