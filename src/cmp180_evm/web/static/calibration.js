let calibrationDraft = null;

const calibrationHelp = {
  profile_id: ['Profile ID', '這份路徑校正資料的唯一名稱。換線材、轉接頭或路徑時應建立新的 ID。'],
  revision: ['Revision', '同一 Profile 的版本。重新量測或修改器材後應提升版本，不要覆寫已使用的版本。'],
  route: ['Route／路徑', '訊號由哪個輸出端經過哪些線材到哪個輸入端。目前只接受已驗證的 RF1.1-RF1.5。'],
  equipment_reference: ['器材識別', '記錄線材、轉接頭、衰減器與參考儀器的資產編號或序號。不要填密碼或授權碼。'],
  calibrated_at: ['校正日期', '實際取得這批參考讀值的日期，不是建立檔案的日期。'],
  expires_at: ['到期日', '依公司校正週期填寫。到期 Profile 會被禁止套用正式量測。'],
  readings: ['CSV 欄位', 'frequency_hz 是頻率；source_reference_dbm 是 Source 參考面功率；receiver_reading_dbm 是 Receiver 參考面讀值。Path Loss = Source - Receiver。']
};

function showCalibrationHelp(title, text) {
  let dialog = $('#calibrationHelpDialog');
  if (!dialog) {
    dialog = document.createElement('dialog');
    dialog.id = 'calibrationHelpDialog';
    dialog.className = 'help-dialog';
    dialog.innerHTML = '<div class="panel-head"><h3></h3><button class="ghost" type="button" aria-label="關閉說明">×</button></div><p></p>';
    document.body.append(dialog);
    dialog.querySelector('button').onclick = () => dialog.close();
  }
  dialog.querySelector('h3').textContent = title;
  dialog.querySelector('p').textContent = text;
  dialog.showModal();
}

const calibrationForm = $('#calibrationForm');
const calibrationToday = new Date();
const calibrationExpiry = new Date(calibrationToday);
calibrationExpiry.setDate(calibrationExpiry.getDate() + 90);
calibrationForm.elements.calibrated_at.value ||= calibrationToday.toISOString().slice(0, 10);
calibrationForm.elements.expires_at.value ||= calibrationExpiry.toISOString().slice(0, 10);
Object.entries(calibrationHelp).forEach(([name, help]) => {
  const field = calibrationForm.elements[name];
  const labelText = field.closest('label').querySelector('span');
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'help-button';
  button.textContent = '?';
  button.setAttribute('aria-label', `說明 ${help[0]}`);
  button.onclick = () => showCalibrationHelp(help[0], help[1]);
  labelText.append(button);
});

const calibrationToolbar = document.createElement('div');
calibrationToolbar.className = 'calibration-toolbar';
calibrationToolbar.innerHTML = '<button class="ghost" type="button" data-action="import">匯入 CSV</button><input type="file" accept=".csv,text/csv" hidden><button class="ghost" type="button" data-action="example">載入範例</button><button class="ghost" type="button" data-action="capture">從儀器擷取</button><button class="help-button" type="button" data-action="help" aria-label="說明校正資料來源">?</button>';
calibrationForm.before(calibrationToolbar);

const calibrationFile = calibrationToolbar.querySelector('input[type="file"]');
calibrationToolbar.querySelector('[data-action="import"]').onclick = () => calibrationFile.click();
calibrationFile.onchange = async () => {
  if (!calibrationFile.files.length) return;
  calibrationForm.elements.readings.value = await calibrationFile.files[0].text();
  toast(language === 'zh' ? 'CSV 已匯入，請確認器材與日期後計算 Draft。' : 'CSV imported. Review equipment and dates before calculating the draft.');
};
calibrationToolbar.querySelector('[data-action="example"]').onclick = () => {
  calibrationForm.elements.readings.value = 'frequency_hz,source_reference_dbm,receiver_reading_dbm\n6085000000,-40.000,-40.850\n6105000000,-40.000,-40.870\n6125000000,-40.000,-40.890';
  toast(language === 'zh' ? '已載入示範資料；不可作為正式校正。' : 'Example data loaded; it is not a formal calibration.');
};
calibrationToolbar.querySelector('[data-action="capture"]').onclick = () => {
  showCalibrationHelp('從儀器擷取尚未啟用', '尚未設定外部校正儀器型號、連線位址與 SCPI adapter。目前請匯入儀器輸出的 CSV；此按鍵不會控制 CMP180 或產生 RF。');
};
calibrationToolbar.querySelector('[data-action="help"]').onclick = () => {
  showCalibrationHelp('校正資料來源', '正式校正應由已校正的 Source 與 Receiver／Power Meter 提供讀值。CMP180 自打自收只能作相對路徑驗證。');
};

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
    $('#calibrationGate').textContent = language === 'zh'
      ? '目前為 Draft：只能審查與下載，尚未核准套用正式量測。'
      : 'Draft only: available for review and download, not approved for formal measurement.';
    let summary = $('#calibrationLossSummary');
    if (!summary) {
      summary = document.createElement('div');
      summary.id = 'calibrationLossSummary';
      $('#calibrationProfilePreview').before(summary);
    }
    summary.innerHTML = `<div class="table-wrap"><table><thead><tr><th>Frequency (MHz)</th><th>Path Loss (dB)</th></tr></thead><tbody>${data.profile.points.map(point => `<tr><td>${(point.frequency_hz / 1e6).toFixed(3)}</td><td>${point.loss_db.toFixed(3)}</td></tr>`).join('')}</tbody></table></div>`;
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
