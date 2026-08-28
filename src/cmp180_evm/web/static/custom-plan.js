let customPlanPayload = null;
let customPlanResult = null;
let customHardwareEnabled = false;
// 每個頻率欄位自行保存 MHz／GHz；送往 API 前一律正規化為 Hz，避免 UI 單位滲入 RF workflow。
function frequencyToHz(value, unit) {
  return Number(value) * (unit === 'GHz' ? 1e9 : 1e6);
}

function configureAxisFields() {
  const axisIsFrequency = $('#customPlanForm').elements.axis.value === 'frequency';
  const form = $('#customPlanForm').elements;
  [form.start, form.stop].forEach(input => {
    if (axisIsFrequency) {
      const unit = form[`${input.name}_unit`].value;
      input.min = unit === 'GHz' ? 0.4 : 400;
      input.max = unit === 'GHz' ? 8 : 8000;
    } else {
      // Power 軸時 start/stop 是 dBm，不受頻率單位換算與型錄範圍限制。
      input.removeAttribute('min');
      input.removeAttribute('max');
    }
  });
  [form.start_unit, form.stop_unit, form.step_unit].forEach(select => { select.hidden = !axisIsFrequency; });
}

const customExecutionPanel = document.createElement('section');
customExecutionPanel.className = 'custom-execution-panel';
customExecutionPanel.hidden = true;
customExecutionPanel.innerHTML = '<h4>實機執行確認 / Hardware Execution</h4><p data-role="gate"></p><label class="check-label"><input data-role="direct" type="checkbox"><span>確認 RF1.1 直接接 RF1.5，沒有衰減器</span></label><label><span>計畫確認字串</span><input data-role="confirmation" autocomplete="off"></label><button data-role="execute" class="danger-button" type="button" disabled>執行自訂實機掃描</button>';
$('#customPlanPreview').after(customExecutionPanel);

fetch('/api/status').then(response => response.json()).then(status => {
  customHardwareEnabled = status.custom_hardware_enabled === true;
}).catch(() => { customHardwareEnabled = false; });

function updateCustomExecuteState() {
  const confirmationMatches = customExecutionPanel.querySelector('[data-role="confirmation"]').value === customPlanResult?.required_confirmation;
  const directConfirmed = customExecutionPanel.querySelector('[data-role="direct"]').checked;
  const hardwareForm = $('#hardwareForm').elements;
  const preflightReady = normalizeRoute(hardwareForm.cable_confirmation.value) === 'RF1.1-RF1.5' && hardwareForm.operator_present.checked;
  customExecutionPanel.querySelector('[data-role="execute"]').disabled = !customHardwareEnabled || customPlanResult?.execution_allowed !== true || !confirmationMatches || !directConfirmed || !preflightReady;
}

$('#customPlanForm').onsubmit = async event => {
  event.preventDefault();
  const form = new FormData(event.target);
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
  const button = event.submitter;
  button.disabled = true;
  try {
    const response = await fetch('/api/hardware/custom-plan-preview', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Plan validation failed');
    const preview = $('#customPlanPreview');
    preview.hidden = false;
    preview.textContent = JSON.stringify(data, null, 2);
    customPlanPayload = payload;
    customPlanResult = data;
    customExecutionPanel.hidden = false;
    customExecutionPanel.querySelector('[data-role="confirmation"]').value = '';
    customExecutionPanel.querySelector('[data-role="direct"]').checked = false;
    customExecutionPanel.querySelector('[data-role="gate"]').textContent = !customHardwareEnabled
      ? '目前為 --demo-only；移除此旗標後即可進行受保護的實機執行。'
      : data.execution_allowed
        ? `此組合位於核准範圍。輸入 ${data.required_confirmation} 並確認接線後執行。`
        : '計畫已建立，但此組合尚未納入 Approved／HIL Profile，因此不會送出 RF。';
    updateCustomExecuteState();
  } catch (error) {
    toast(error.message, 'error');
  } finally {
    button.disabled = false;
  }
};

customExecutionPanel.addEventListener('input', updateCustomExecuteState);
$('#hardwareForm').addEventListener('input', updateCustomExecuteState);
customExecutionPanel.querySelector('[data-role="execute"]').onclick = event => {
  if (!customPlanPayload || !customPlanResult || !customHardwareEnabled) return;
  const hardwareForm = $('#hardwareForm').elements;
  startJob('/api/jobs/hardware/custom-sweep', {
    ...customPlanPayload,
    cable_confirmation: hardwareForm.cable_confirmation.value,
    operator_present: hardwareForm.operator_present.checked,
    direct_cable_no_attenuator: customExecutionPanel.querySelector('[data-role="direct"]').checked,
    execution_confirmation: customExecutionPanel.querySelector('[data-role="confirmation"]').value
  }, event.currentTarget, customPlanResult.axis);
};

function setCustomPlanAxis(axis) {
  const form = $('#customPlanForm').elements;
  const powerAxis = axis === 'power';
  form.axis.value = axis;
  form.start.value = powerAxis ? -55 : 6085;
  form.stop.value = powerAxis ? -40 : 6125;
  form.step.value = powerAxis ? 5 : 10;
  form.start_unit.value = 'MHz';
  form.stop_unit.value = 'MHz';
  form.step_unit.value = 'MHz';
  // 之前切到 Power 軸時 start/stop 仍殘留 min="400"，導致 -55 dBm 無法通過瀏覽器原生驗證送出；
  // 這裡同步依目前軸別與單位重設 min/max。
  configureAxisFields();
}

document.querySelectorAll('#customPlanForm .field-unit').forEach(select => {
  select.addEventListener('change', event => {
    const form = $('#customPlanForm').elements;
    const inputName = event.target.name === 'center_unit'
      ? 'center_frequency_mhz'
      : event.target.name.replace('_unit', '');
    const input = form[inputName];
    const previousUnit = event.target.dataset.previousUnit || (event.target.value === 'GHz' ? 'MHz' : 'GHz');
    // 單位切換會等值換算現有數字，避免 6105 MHz 被誤解成 6105 GHz。
    const hz = frequencyToHz(input.value, previousUnit);
    input.value = Math.round((hz / (event.target.value === 'GHz' ? 1e9 : 1e6)) * 1e6) / 1e6;
    event.target.dataset.previousUnit = event.target.value;
    configureAxisFields();
  });
});

document.querySelectorAll('#customPlanForm .field-unit').forEach(select => { select.dataset.previousUnit = select.value; });
configureAxisFields();
