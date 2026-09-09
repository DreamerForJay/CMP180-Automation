let customPlanPayload = null;
let customPlanResult = null;
let customHardwareEnabled = false;

// frequencyToHz／formatFrequency 已移至 app.js 共用，避免與 gprf-power.js／hardware.js 重複定義。

function configureAxisFields() {
  const axisIsFrequency = $('#customPlanForm').elements.axis.value === 'frequency';
  const form = $('#customPlanForm').elements;
  [form.start, form.stop].forEach(input => {
    if (axisIsFrequency) {
      const unit = form[`${input.name}_unit`].value;
      input.min = unit === 'GHz' ? 0.4 : 400;
      input.max = unit === 'GHz' ? 8 : 8000;
    } else {
      // Power 軸 start/stop 是 dBm，不能沿用頻率欄位的 min/max。
      input.removeAttribute('min');
      input.removeAttribute('max');
    }
  });
  // Power 軸的 start/stop/step 是 dBm，隱藏對應的頻率單位切換鈕。
  ['start_unit', 'stop_unit', 'step_unit'].forEach(name => {
    const button = document.querySelector(`#customPlanForm [data-unit-for="${name}"]`);
    if (button) button.hidden = !axisIsFrequency;
  });
  // 固定值欄位只有「另一個軸」會用到：頻率掃描時 analyzer 逐點 retune，固定中心頻率
  // 不會被讀取；功率掃描時各點功率由 start/stop/step 決定，固定功率同樣不會被讀取。
  // 隱藏未使用的欄位，避免操作員誤以為它會影響掃描。
  const centerField = form.center_frequency_mhz.closest('label');
  const powerField = form.generator_power_dbm.closest('label');
  if (centerField) centerField.hidden = axisIsFrequency;
  if (powerField) powerField.hidden = !axisIsFrequency;
}

fetch('/api/status').then(response => response.json()).then(status => {
  customHardwareEnabled = status.custom_hardware_enabled === true;
}).catch(() => { customHardwareEnabled = false; });

function buildCustomPlanPayload() {
  const form = new FormData($('#customPlanForm'));
  const axis = form.get('axis');
  const payload = {
    axis,
    bandwidth_hz: Number(form.get('bandwidth_mhz')) * 1e6,
    dwell_ms: Number(form.get('dwell_ms')),
    generator_power_dbm: Number(form.get('generator_power_dbm')),
    center_frequency_hz: frequencyToHz(form.get('center_frequency_mhz'), form.get('center_unit'))
  };
  if (axis === 'frequency') {
    payload.start_hz = frequencyToHz(form.get('start'), form.get('start_unit'));
    payload.stop_hz = frequencyToHz(form.get('stop'), form.get('stop_unit'));
    payload.step_hz = frequencyToHz(form.get('step'), form.get('step_unit'));
  } else {
    payload.start_dbm = Number(form.get('start'));
    payload.stop_dbm = Number(form.get('stop'));
    payload.step_dbm = Number(form.get('step'));
  }
  return payload;
}

function renderCustomPlanPreview(data) {
  const preview = $('#customPlanPreview');
  preview.hidden = false;
  const first = data.points?.[0];
  const last = data.points?.[data.points.length - 1];
  const axisLabel = data.axis === 'frequency'
    ? (language === 'zh' ? 'WLAN EVM 頻率掃描' : 'WLAN EVM Frequency Sweep')
    : (language === 'zh' ? 'WLAN EVM 功率掃描' : 'WLAN EVM Power Sweep');
  const range = data.axis === 'frequency'
    ? `${formatFrequency(first)} → ${formatFrequency(last)}`
    : `${first} dBm → ${last} dBm`;
  const gateText = data.execution_allowed
    ? (language === 'zh' ? '可執行：目前計畫會照畫面參數送出，不會改跑固定三點。' : 'Executable: this plan will use the on-screen values, not a fixed three-point profile.')
    : window.formatPlanRejection(data, 'workflow rejected the plan', 'wlan');
  preview.textContent = language === 'zh' ? [
    axisLabel,
    `點數：${data.point_count}`,
    `範圍：${range}`,
    `頻寬：${formatFrequency(data.bandwidth_hz)}`,
    `停留時間：${data.dwell_ms} ms`,
    gateText
  ].join('\n') : [
    axisLabel,
    `Points: ${data.point_count}`,
    `Range: ${range}`,
    `Bandwidth: ${formatFrequency(data.bandwidth_hz)}`,
    `Dwell: ${data.dwell_ms} ms`,
    gateText
  ].join('\n');
}

window.addEventListener('cmp180-language-change', () => {
  // 使用既有 preview 資料換語言，不重新送出 Review 或 RF 請求。
  if (customPlanResult) renderCustomPlanPreview(customPlanResult);
});

async function reviewCustomPlan(button = null) {
  const payload = buildCustomPlanPayload();
  if (button) button.disabled = true;
  try {
    const response = await fetch('/api/hardware/custom-plan-preview', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Plan validation failed');
    customPlanPayload = payload;
    customPlanResult = data;
    renderCustomPlanPreview(data);
    return data;
  } catch (error) {
    toast(error.message, 'error');
    throw error;
  } finally {
    if (button) button.disabled = false;
  }
}

$('#customPlanForm').onsubmit = async event => {
  event.preventDefault();
  try {
    await reviewCustomPlan(event.submitter);
  } catch {
    // 錯誤已由 reviewCustomPlan 顯示；這裡避免重複 toast。
  }
};

window.reviewAndExecuteCustomHardwarePlan = async function(button) {
  let data;
  try {
    data = await reviewCustomPlan(button);
  } catch {
    return;
  }
  if (!customHardwareEnabled) {
    toast(language === 'zh' ? '伺服器未啟用實機控制，未送出 RF。' : 'Hardware control is not enabled; no RF was transmitted.', 'error');
    return;
  }
  if (!data.execution_allowed) {
    toast(language === 'zh' ? '此掃描計畫未通過 workflow 檢查，未送出 RF。' : 'This sweep plan is blocked by workflow checks; no RF was transmitted.', 'error');
    return;
  }
  const hardwareForm = $('#hardwareForm').elements;
  if (normalizeRoute(hardwareForm.cable_confirmation.value) !== 'RF1.1-RF1.5' || !hardwareForm.operator_present.checked) {
    toast(language === 'zh' ? '請先完成接線與人在現場確認。' : 'Complete cabling and operator preflight first.', 'error');
    return;
  }
  // 最後確認保留在 Web 內；後端仍會用 fingerprint 重新確認參數未被竄改。
  const approved = confirm(language === 'zh'
    ? `即將送出真實 RF\n\n${data.axis} sweep · ${data.point_count} 點\n${$('#customPlanPreview').textContent}\n\n確認接線未變、人在儀器旁並開始？`
    : `Real RF will be transmitted\n\n${data.axis} sweep · ${data.point_count} points\n${$('#customPlanPreview').textContent}\n\nConfirm unchanged cabling, operator presence, and start?`);
  if (!approved) {
    toast(language === 'zh' ? '已取消，未送出 RF。' : 'Cancelled; no RF was transmitted.');
    return;
  }
  startJob('/api/jobs/hardware/custom-sweep', {
    ...customPlanPayload,
    cable_confirmation: hardwareForm.cable_confirmation.value,
    operator_present: hardwareForm.operator_present.checked,
    direct_cable_no_attenuator: hardwareForm.direct_cable_no_attenuator.checked,
    execution_confirmation: data.required_confirmation
  }, button, data.axis);
};

function setCustomPlanAxis(axis) {
  const form = $('#customPlanForm').elements;
  const powerAxis = axis === 'power';
  form.axis.value = axis;
  // 預設 frequency sweep 放在已核准 6 GHz/BW320 section，避免一切回掃描軸就踩到
  // 5 GHz 以下的非 WLAN 空隙而被 workflow gate 擋下。
  form.start.value = powerAxis ? -55 : 5925;
  form.stop.value = powerAxis ? -30 : 6125;
  form.step.value = powerAxis ? 5 : 20;
  // 切換掃描軸時單位一律回到 MHz，隱藏值與按鈕文字必須同步。
  ['start_unit', 'stop_unit', 'step_unit'].forEach(name => {
    form[name].value = 'MHz';
    const button = document.querySelector(`#customPlanForm [data-unit-for="${name}"]`);
    if (button) button.textContent = 'MHz';
  });
  configureAxisFields();
}

// 單位改為單鍵切換：點一下就在 MHz／GHz 之間互換，不需要展開選單。
document.querySelectorAll('#customPlanForm [data-unit-for]').forEach(button => {
  button.addEventListener('click', () => {
    const form = $('#customPlanForm').elements;
    const holder = form[button.dataset.unitFor];
    const inputName = button.dataset.unitFor === 'center_unit'
      ? 'center_frequency_mhz'
      : button.dataset.unitFor.replace('_unit', '');
    const input = form[inputName];
    const previousUnit = holder.value === 'GHz' ? 'GHz' : 'MHz';
    const nextUnit = previousUnit === 'GHz' ? 'MHz' : 'GHz';
    // 單位切換會等值換算現有數字，避免 6105 MHz 被誤解成 6105 GHz。
    const hz = frequencyToHz(input.value, previousUnit);
    input.value = Math.round((hz / (nextUnit === 'GHz' ? 1e9 : 1e6)) * 1e6) / 1e6;
    holder.value = nextUnit;
    button.textContent = nextUnit;
    configureAxisFields();
    updateHardwareSummary?.();
  });
});

configureAxisFields();
