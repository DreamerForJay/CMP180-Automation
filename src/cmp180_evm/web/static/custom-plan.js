let customPlanPayload = null;
let customPlanResult = null;
let customHardwareEnabled = false;

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
    center_frequency_hz: Number(form.get('center_frequency_mhz')) * 1e6
  };
  if (axis === 'frequency') {
    payload.start_hz = Number(form.get('start')) * 1e6;
    payload.stop_hz = Number(form.get('stop')) * 1e6;
    payload.step_hz = Number(form.get('step')) * 1e6;
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

$('#customPlanForm').elements.axis.onchange = event => {
  const powerAxis = event.target.value === 'power';
  const form = $('#customPlanForm').elements;
  form.start.value = powerAxis ? -55 : 6085;
  form.stop.value = powerAxis ? -40 : 6125;
  form.step.value = powerAxis ? 5 : 10;
};
