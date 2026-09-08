(function () {
  const byId = id => document.getElementById(id);
  let campaign = null;
  function notify(message, type = 'info') { const node = byId('toast'); if (!node) return; node.textContent = message; node.dataset.type = type; node.classList.add('show'); setTimeout(() => node.classList.remove('show'), 4800); }
  async function request(path, payload) { const response = await fetch(path, payload === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Campaign request failed'); return data; }
  function escapeHtml(value) { return String(value).replace(/[&<>"']/g,character=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character])); }
  function campaignText(zh, en) { return language === 'zh' ? zh : en; }
  function priorityForCase(item) {
    if (item.case_id === 'b6-bw320') return {rank:0,label:'P0',text:campaignText('黃金點','Golden point')};
    if (item.category === 'bandwidth') return {rank:1,label:'P1',text:'11ax EVM'};
    if (item.category === 'power') return {rank:2,label:'P2',text:campaignText('功率邊界','Power boundary')};
    if (item.category === 'route') return {rank:3,label:'P3',text:campaignText('Route 待核准','Route pending approval')};
    return {rank:4,label:'HOLD',text:campaignText('能力待核准','Capability pending approval')};
  }
  function campaignCaseOrder(item) {
    const order = {
      'b6-bw320': 0,
      'b24-bw20': 10,
      'b24-bw40': 11,
      'b5-bw20': 20,
      'b5-bw40': 21,
      'b5-bw80': 22,
      'b5-bw160': 23,
      'b6-bw20': 30,
      'b6-bw40': 31,
      'b6-bw80': 32,
      'b6-bw160': 33,
      'b6-power': 40
    };
    // 同一 Priority 內採現場常用順序：2.4G→5G→6G、頻寬由小到大、功率最後。
    return order[item.case_id] ?? 900;
  }
  function sortedCampaignCases() {
    const order = {ready:0,running:1,failed:2,interrupted:3,blocked:4,complete:5};
    // HIL 操作依安全重要度排序；未核准能力留在後面，避免現場誤先改接或誤啟用 RF。
    return [...(campaign?.cases || [])].sort((left,right) => {
      const leftPriority = priorityForCase(left).rank;
      const rightPriority = priorityForCase(right).rank;
      return leftPriority - rightPriority
        || (order[left.state] ?? 9) - (order[right.state] ?? 9)
        || campaignCaseOrder(left) - campaignCaseOrder(right)
        || String(left.case_id).localeCompare(String(right.case_id));
    });
  }
  function connectionInstruction(item) {
    // 目前唯一核准接線是 RF1.1→RF1.5；其他 route 僅保留成待驗證案例。
    if (item.route === 'RF1.1-RF1.5') return campaignText('接 RF1.1 Generator output → RF1.5 Analyzer input；先不要切換其他 RF ports。','Connect RF1.1 Generator output → RF1.5 Analyzer input; do not switch to other RF ports.');
    return campaignText(`${item.route || '未指定 route'} 尚未核准；不要改接線，保留 BLOCKED 等待新 SOP。`,`${item.route || 'Unspecified route'} is not approved; do not change cabling. Keep it BLOCKED pending a new SOP.`);
  }
  function nextAction(item) {
    const instruction = connectionInstruction(item);
    const evidenceHtml = evidence(item);
    if (item.state === 'ready') return `<strong>${campaignText('下一步：','Next step:')}</strong>${escapeHtml(instruction)}<br><span>${campaignText('確認兩個 checkbox 後按執行。','Confirm both checkboxes, then click Run.')}</span>`;
    if (item.state === 'running') return `<strong>${campaignText('執行中：','Running:')}</strong>${escapeHtml(instruction)}<br><span>${campaignText('等待 job 完成；取消會在 cleanup/RF Off 邊界生效。','Wait for the job to complete; cancellation takes effect at a cleanup/RF Off boundary.')}</span>`;
    if (item.state === 'complete') return evidenceHtml;
    if (item.state === 'blocked') return `<strong>${campaignText('暫停：','Blocked:')}</strong>${escapeHtml(instruction)}${item.reason ? `<br><span>${escapeHtml(item.reason)}</span>` : ''}`;
    return evidenceHtml;
  }
  function evidence(item) {
    const runDir = item.artifacts && item.artifacts.run_dir;
    const relative = runDir ? `output/${String(runDir).split(/[\\/]/).pop()}` : '';
    const reason = window.localizePlanDetail(item.reason) || '';
    if (!reason && !relative) return '—';
    const summary = escapeHtml(reason || relative);
    const detail = [reason,relative].filter(Boolean).map(value=>`<span>${escapeHtml(value)}</span>`).join('');
    return `<details class="campaign-detail"><summary title="${summary}">${summary}</summary>${detail}</details>`;
  }
  function render() {
    if (!campaign) return;
    const cases = sortedCampaignCases(), counts = (campaign.cases || []).reduce((value,item)=>{value[item.state]=(value[item.state]||0)+1;return value;},{});
    const next = cases.find(item=>item.state==='ready');
    byId('campaignSummary').textContent = language === 'zh'
      ? `待執行 ${counts.ready||0} · 已完成 ${counts.complete||0} · 已阻擋 ${counts.blocked||0}`
      : `READY ${counts.ready||0} · DONE ${counts.complete||0} · BLOCKED ${counts.blocked||0}`;
    byId('campaignOperatorHint').innerHTML = next
      ? `<strong>${campaignText('目前接線指示','Current cabling instruction')}</strong><span>${escapeHtml(priorityForCase(next).label)} ${escapeHtml(next.label)}：${escapeHtml(connectionInstruction(next))}</span>`
      : `<strong>${campaignText('目前接線指示','Current cabling instruction')}</strong><span>${campaignText('沒有 READY 案例；請準備矩陣或查看 BLOCKED 原因，不要任意改接 RF ports。','No READY case. Prepare the matrix or inspect BLOCKED reasons; do not change RF ports arbitrarily.')}</span>`;
    const categoryLabel = value => ({bandwidth:campaignText('頻寬','Bandwidth'),power:campaignText('功率','Power'),route:campaignText('接線','Route'),capability:campaignText('能力','Capability')}[value] || value);
    byId('campaignRows').innerHTML = cases.map(item => { const priority = priorityForCase(item); return `<tr><td><span class="campaign-priority p${priority.rank}">${escapeHtml(priority.label)}</span><small>${escapeHtml(priority.text)}</small></td><td><span class="campaign-state ${item.state}">${item.state.toUpperCase()}</span></td><td>${escapeHtml(categoryLabel(item.category))}</td><td><strong>${escapeHtml(item.label)}</strong></td><td>${escapeHtml(item.route)}</td><td>${item.preview?.point_count||'—'}</td><td class="campaign-evidence">${nextAction(item)}</td><td class="campaign-actions">${item.state==='failed'||item.state==='interrupted'?`<button class="ghost" type="button" data-campaign-retry="${item.case_id}">${campaignText('重試','Retry')}</button>`:`<button class="primary" type="button" data-campaign-start="${item.case_id}" ${item.state==='ready'?'':'disabled'}>${campaignText('執行','Run')}</button>`}${item.state==='running'?` <button class="ghost" type="button" data-campaign-job="${item.job_id}" data-action="pause">${campaignText('暫停','Pause')}</button> <button class="danger-button" type="button" data-campaign-job="${item.job_id}" data-action="cancel">${campaignText('停止','Stop')}</button>`:''}</td></tr>`; }).join('');
    document.querySelectorAll('[data-campaign-start]').forEach(button => { button.onclick = () => startCase(button.dataset.campaignStart); });
    document.querySelectorAll('[data-campaign-retry]').forEach(button => { button.onclick = async()=>{try{campaign=await request(`/api/hil-campaign/cases/${encodeURIComponent(button.dataset.campaignRetry)}/retry`,{});render();notify('案例已重新檢查；舊 artifacts 仍保留');}catch(error){notify(error.message,'error');}}; });
    document.querySelectorAll('[data-campaign-job]').forEach(button => { button.onclick = async()=>{try{await request(`/api/jobs/${button.dataset.campaignJob}/${button.dataset.action}`,{});notify(`${button.dataset.action} requested`);}catch(error){notify(error.message,'error');}}; });
  }
  async function load() { try { campaign = await request('/api/hil-campaign'); render(); } catch(error) { notify(error.message,'error'); } }
  async function prepare() { try { campaign = await request('/api/hil-campaign/prepare',{}); render(); } catch(error) { notify(error.message,'error'); } }
  async function startCase(caseId) {
    if (!byId('campaignOperator').checked || !byId('campaignRoute').checked) { notify(campaignText('請先確認操作員在場與目前 route 接線','Confirm operator presence and the current route first'),'error'); return; }
    try { const job = await request(`/api/hil-campaign/cases/${encodeURIComponent(caseId)}/start`,{operator_present:true,route_connected:true}); notify(`Started ${caseId} · job ${job.job_id}`); await pollCase(job.job_id); }
    catch(error) { notify(error.message,'error'); await load(); }
  }
  async function pollCase(jobId) { const job = await request(`/api/jobs/${jobId}`); await load(); if (['queued','running','paused','stopping'].includes(job.state)) { setTimeout(()=>pollCase(jobId),300); return; } notify(job.state==='complete'?'Campaign case complete':(job.error||job.state),job.state==='complete'?'info':'error'); }
  byId('prepareCampaign').onclick=prepare; byId('refreshCampaign').onclick=load;
  byId('runNextCampaign').onclick=()=>{const next=sortedCampaignCases().find(item=>item.state==='ready');if(next)startCase(next.case_id);else notify(campaignText('沒有 READY 案例；請準備矩陣或檢查 BLOCKED 原因','No READY case; prepare the matrix or inspect BLOCKED reasons'));};
  byId('resetCampaign').onclick=async()=>{if(!confirm(campaignText('重設 Campaign 狀態？量測 artifacts 不會刪除。','Reset Campaign state? Measurement artifacts will not be deleted.')))return;try{campaign=await request('/api/hil-campaign/reset',{});render();}catch(error){notify(error.message,'error');}};
  window.addEventListener('cmp180-language-change',()=>{if(campaign)render();});
  load();
})();
