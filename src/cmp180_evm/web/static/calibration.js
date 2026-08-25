let calibrationDraft = null;

function parseCalibrationCsv(text) {
  const lines = text.trim().split(/\r?\n/).filter(Boolean);
  const header = lines.shift().split(',').map(value => value.trim());
  const required = ['frequency_hz', 'source_reference_dbm', 'receiver_reading_dbm'];
  if (!required.every(name => header.includes(name))) throw new Error('CSV header is invalid');
  return lines.map(line => {
    const values = line.split(',').map(value => value.trim());
    return Object.fromEntries(header.map((name, index) => [name, Number(values[index])]));
  });
}

$('#calibrationForm').onsubmit = async event => {
  event.preventDefault();
  const form = new FormData(event.target);
  const button = event.submitter;
  button.disabled = true;
  try {
    const payload = Object.fromEntries(form.entries());
    payload.readings = parseCalibrationCsv(payload.readings);
    const response = await fetch('/api/calibration/draft-preview', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Calibration preview failed');
    calibrationDraft = data.profile;
    $('#calibrationResult').hidden = false;
    $('#calibrationGate').textContent = data.measurement_use;
    $('#calibrationProfilePreview').textContent = JSON.stringify(data.profile, null, 2);
  } catch (error) {
    toast(error.message, 'error');
  } finally {
    button.disabled = false;
  }
};

$('#downloadCalibration').onclick = () => {
  if (!calibrationDraft) return;
  // JSON 是 YAML 1.2 的有效子集合；保持 draft 狀態，避免下載後被誤當 Approved。
  const blob = new Blob([JSON.stringify(calibrationDraft, null, 2)], {type: 'application/yaml'});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${calibrationDraft.profile_id}-${calibrationDraft.revision}.yaml`;
  link.click();
  URL.revokeObjectURL(link.href);
};
