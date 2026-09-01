(function () {
  const byId = id => document.getElementById(id);
  let campaign = null;
  function notify(message, type = 'info') { const node = byId('toast'); if (!node) return; node.textContent = message; node.dataset.type = type; node.classList.add('show'); setTimeout(() => node.classList.remove('show'), 4800); }
  async function request(path, payload) { const response = await fetch(path, payload === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Campaign request failed'); return data; }
  function escapeHtml(value) { return String(value).replace(/[&<>"']/g,character=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character])); }
  function evidence(item) {
    const runDir = item.artifacts && item.artifacts.run_dir;
    const relative = runDir ? `output/${String(runDir).split(/[\\/]/).pop()}` : '';
    const reason = item.reason || '';
    if (!reason && !relative) return '—';
    const summary = escapeHtml(reason || relative);
    const detail = [reason,relative].filter(Boolean).map(value=>`<span>${escapeHtml(value)}</span>`).join('');
    return `<details class="campaign-detail"><summary title="${summary}">${summary}</summary>${detail}</details>`;
  }
  function render() {
    if (!campaign) return;
    const cases = campaign.cases || [], counts = cases.reduce((value,item)=>{value[item.state]=(value[item.state]||0)+1;return value;},{});
    byId('campaignSummary').textContent = `READY ${counts.ready||0} · DONE ${counts.complete||0} · BLOCKED ${counts.blocked||0}`;
    byId('campaignRows').innerHTML = cases.map(item => `<tr><td><span class="campaign-state ${item.state}">${item.state.toUpperCase()}</span></td><td>${escapeHtml(item.category)}</td><td><strong>${escapeHtml(item.label)}</strong></td><td>${escapeHtml(item.route)}</td><td>${item.preview?.point_count||'—'}</td><td class="campaign-evidence">${evidence(item)}</td><td class="campaign-actions">${item.state==='failed'||item.state==='interrupted'?`<button class="ghost" type="button" data-campaign-retry="${item.case_id}">Retry</button>`:`<button class="primary" type="button" data-campaign-start="${item.case_id}" ${item.state==='ready'?'':'disabled'}>Run</button>`}${item.state==='running'?` <button class="ghost" type="button" data-campaign-job="${item.job_id}" data-action="pause">Pause</button> <button class="danger-button" type="button" data-campaign-job="${item.job_id}" data-action="cancel">Stop</button>`:''}</td></tr>`).join('');
    document.querySelectorAll('[data-campaign-start]').forEach(button => { button.onclick = () => startCase(button.dataset.campaignStart); });
    document.querySelectorAll('[data-campaign-retry]').forEach(button => { button.onclick = async()=>{try{campaign=await request(`/api/hil-campaign/cases/${encodeURIComponent(button.dataset.campaignRetry)}/retry`,{});render();notify('案例已重新檢查；舊 artifacts 仍保留');}catch(error){notify(error.message,'error');}}; });
    document.querySelectorAll('[data-campaign-job]').forEach(button => { button.onclick = async()=>{try{await request(`/api/jobs/${button.dataset.campaignJob}/${button.dataset.action}`,{});notify(`${button.dataset.action} requested`);}catch(error){notify(error.message,'error');}}; });
  }
  async function load() { try { campaign = await request('/api/hil-campaign'); render(); } catch(error) { notify(error.message,'error'); } }
  async function prepare() { try { campaign = await request('/api/hil-campaign/prepare',{}); render(); } catch(error) { notify(error.message,'error'); } }
  async function startCase(caseId) {
    if (!byId('campaignOperator').checked || !byId('campaignRoute').checked) { notify('請先確認操作員在場與目前 route 接線','error'); return; }
    try { const job = await request(`/api/hil-campaign/cases/${encodeURIComponent(caseId)}/start`,{operator_present:true,route_connected:true}); notify(`Started ${caseId} · job ${job.job_id}`); await pollCase(job.job_id); }
    catch(error) { notify(error.message,'error'); await load(); }
  }
  async function pollCase(jobId) { const job = await request(`/api/jobs/${jobId}`); await load(); if (['queued','running','paused','stopping'].includes(job.state)) { setTimeout(()=>pollCase(jobId),300); return; } notify(job.state==='complete'?'Campaign case complete':(job.error||job.state),job.state==='complete'?'info':'error'); }
  byId('prepareCampaign').onclick=prepare; byId('refreshCampaign').onclick=load;
  byId('runNextCampaign').onclick=()=>{const next=campaign?.cases?.find(item=>item.state==='ready');if(next)startCase(next.case_id);else notify('沒有 READY 案例；請 Prepare 或檢查 blocked 原因');};
  byId('resetCampaign').onclick=async()=>{if(!confirm('重設 Campaign 狀態？量測 artifacts 不會刪除。'))return;try{campaign=await request('/api/hil-campaign/reset',{});render();}catch(error){notify(error.message,'error');}};
  load();
})();
