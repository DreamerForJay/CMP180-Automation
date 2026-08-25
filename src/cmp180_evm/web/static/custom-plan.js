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
  } catch (error) {
    toast(error.message, 'error');
  } finally {
    button.disabled = false;
  }
};

$('#customPlanForm').elements.axis.onchange = event => {
  const powerAxis = event.target.value === 'power';
  const form = $('#customPlanForm').elements;
  form.start.value = powerAxis ? -55 : 6085;
  form.stop.value = powerAxis ? -40 : 6125;
  form.step.value = powerAxis ? 5 : 10;
};
