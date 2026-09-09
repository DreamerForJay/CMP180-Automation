const translations={zh:{subtitle:'WLAN TX EVM 自動化量測',mockBadge:'DEMO',workspaceTitle:'量測工作區',controlState:'控制狀態',demoControlState:'僅使用示範資料',demoControlHint:'CMP180 RF 控制未啟用',singleTab:'單點量測',sweepTab:'頻率掃描',resultsTab:'結果與圖表',historyTab:'量測紀錄',historyTitle:'量測紀錄',historyHelp:'瀏覽本機保存的實機與示範結果；不會啟動量測或 RF。',refreshHistory:'重新整理',historyEmpty:'尚無可用紀錄。',historyTime:'時間',historyName:'名稱',historySource:'來源',historyStatus:'狀態',historyPoints:'點數',historyFiles:'檔案',singleTitle:'示範單點量測',singleHelp:'輸入一個測試點，驗證資料保存與圖表流程。',frequency:'中心頻率',bandwidth:'頻寬',power:'Generator 功率',testName:'測試名稱',runSingle:'執行示範單點',sweepTitle:'示範頻率掃描',sweepHelp:'依起點、終點與步進建立頻點，最多 11 點。',start:'起始頻率',stop:'結束頻率',step:'步進',dwell:'停留時間',runSweep:'執行示範掃描',resultTitle:'量測結果',empty:'尚未執行量測。',resultChart:'結果趨勢圖',dwellHelp:'每個頻點之間的等待時間，範圍 100–2000 ms。',sweepPowerHelp:'安全短掃描上限為 -40 dBm。',powerSweepTab:'功率掃描',powerSweepTitle:'示範功率掃描',powerSweepHelp:'固定頻率，依起點、終點與步進建立功率點，最多 11 點。',startPower:'起始功率',stopPower:'結束功率',stepPower:'步進',runPowerSweep:'執行示範功率掃描',singlePowerHelp:'與實機安全 profile 一致，上限 -40 dBm。'},en:{subtitle:'WLAN TX EVM Automation',mockBadge:'DEMO',workspaceTitle:'Measurement Workspace',controlState:'Control state',demoControlState:'Demo data only',demoControlHint:'CMP180 RF control disabled',singleTab:'Single',sweepTab:'Frequency Sweep',resultsTab:'Results & Plots',historyTab:'Run History',historyTitle:'Run History',historyHelp:'Browse saved hardware and demo results without starting a measurement or RF.',refreshHistory:'Refresh',historyEmpty:'No saved runs found.',historyTime:'Time',historyName:'Name',historySource:'Source',historyStatus:'Status',historyPoints:'Points',historyFiles:'Files',singleTitle:'Demo single measurement',singleHelp:'Enter one point to validate artifact and plotting workflows.',frequency:'Center frequency',bandwidth:'Bandwidth',power:'Generator power',testName:'Test name',runSingle:'Run demo single',sweepTitle:'Demo frequency sweep',sweepHelp:'Build points from start, stop, and step; maximum 11 points.',start:'Start frequency',stop:'Stop frequency',step:'Step',dwell:'Dwell time',runSweep:'Run demo sweep',resultTitle:'Measurement results',empty:'No measurement has been run.',resultChart:'Result trends',dwellHelp:'Wait time between frequency points, 100–2000 ms.',sweepPowerHelp:'The safe short-sweep ceiling is -40 dBm.',powerSweepTab:'Power Sweep',powerSweepTitle:'Demo power sweep',powerSweepHelp:'Fixed frequency; build power points from start, stop, and step; maximum 11 points.',startPower:'Start power',stopPower:'Stop power',stepPower:'Step',runPowerSweep:'Run demo power sweep',singlePowerHelp:'Aligned with the hardware safety profile; ceiling -40 dBm.'}};
// 導覽名稱明確區分 Demo 與實機，避免相同量測類型看起來像重複功能。
translations.zh.singleTab='示範單點';translations.zh.sweepTab='示範頻掃';translations.zh.powerSweepTab='示範功掃';
translations.en.singleTab='Demo Single';translations.en.sweepTab='Demo Freq Sweep';translations.en.powerSweepTab='Demo Power Sweep';
translations.zh.campaignTab='HIL 批次';translations.en.campaignTab='HIL Campaign';
Object.assign(translations.zh,{homeTab:'首頁',measurementTab:'量測',calibrationTab:'校正',guideTab:'說明',guideTitle:'快速操作',guideIntro:'啟動服務、執行量測、查看結果。',guideSafeTitle:'Demo 模式',guideSafeText:'不發送 RF',guideStep1:'啟動',guideStep2:'量測',guideStep3:'結果',guideStep4:'報告',demoCommandTitle:'啟動 Demo',demoCommandHelp:'不連線 CMP180、不送 SCPI。',copyCommand:'複製',openBrowser:'網址',configCommandTitle:'檢查設定',configCommandHelp:'驗證 YAML 與安全設定。',expectedOutput:'預期結果',connectionCommandTitle:'連線檢查',connectionCommandHelp:'讀取 IDN、Options 與 Error Queue。',powerWarning:'注意',queryOnlyAdvice:'此動作不啟動量測或 RF。',hardwareCommandTitle:'啟動實機服務',hardwareCommandHelp:'啟動後仍需在量測頁完成安全確認。',hardwareHold:'未通過安全確認時不會送出 RF。',whereResultsTitle:'輸出位置',whereResultsText:'output\\<timestamp>_<run>\\',whenStopTitle:'停止條件',whenStopText:'INV、逾時、SCPI Error、接線異動或 RF 狀態不明。'});
Object.assign(translations.zh,{guideInstallTitle:'第一次安裝',guideCliTitle:'CLI：檢查連線與設定',guideDataTitle:'取得與分析資料',guideDataHelp:'也可在「量測紀錄」開啟詳情，再到「結果與圖表」比較 2–8 筆 Run。'});
Object.assign(translations.en,{guideInstallTitle:'First-time installation',guideCliTitle:'CLI: connection and configuration',guideDataTitle:'Get and analyze data',guideDataHelp:'You can also open details in Runs, then compare 2–8 runs in Results & Analysis.'});
Object.assign(translations.zh,{
  hardwareSource:'實機量測',demoSource:'示範與訓練',hardwareSop1:'設定數值',hardwareSop2:'檢查接線與人在場',hardwareSop3:'檢查計畫',hardwareSop4:'執行並保存 artifacts',
  measurementSettings:'設定數值',measurementSettingsHelp:'先選擇量測類型並填好頻率、功率、頻寬與點數。',singleSetup:'單點設定',singleSetupHelp:'輸入中心頻率、WLAN 頻寬與 Generator 功率。Web 會先檢查 approved profile，通過且完成最後確認後才控制 CMP180。',reviewSingle:'檢查單點計畫',sweepSetup:'掃描設定',sweepSetupHelp:'設定 WLAN EVM 掃描軸、範圍、步進與停留時間；送出前會顯示點位、預估時間與安全檢查結果。',reviewPlan:'檢查量測計畫',reviewGprf:'檢查 GPRF 計畫',safetyCheck:'檢查接線與現場狀態',safetyCheckHelp:'目前只核准 RF1.1 → RF1.5。確認直接線路沒有額外衰減器，且操作員在機台旁。',directCableConfirm:'我已確認目前為核准的直接線路，沒有未登錄的衰減器或轉接件',directCableCheck:'直接線路／無未登錄衰減器',executeHardware:'執行實機量測',executeHardwareHelp:'按下後仍會顯示最後確認；取消不會送 RF，完成後保存 artifacts。',
  loopbackTitle:'Loopback RF 效能驗證',loopbackHelp:'固定條件下執行獨立 SingleShot repeats；先驗證 Tester／Cable／UD Box／RF path，不代表 DUT PASS。',loopbackWarning:'穩定不等於合理',loopbackWarningHelp:'Stability 評估重複性；Reasonableness 比較 Analyzer input reference plane 的 Expected RX Power。相同代表點、門檻且至少 Repeat 10 使用 approved baseline；其他條件仍為 draft。',loopbackCableConfirm:'接線、Cable／UD Box path 與衰減條件已確認且本次不變',loopbackOperatorConfirm:'操作員在 CMP180 旁，可處理 RF 異常',runLoopback:'檢查並執行 Loopback',runAllLoopbacks:'一鍵執行全部 11 Profiles × Repeat 10',runAllLoopbacksHelp:'依序執行 110 次 SingleShot；每個 profile 獨立保存 artifact，SCPI／cleanup error 會停止整批。',loopbackTrends:'即時 Repeat 趨勢',loopbackTrendsHelp:'紅色點代表 INVALID 或 IQR outlier；資料不會被刪除',
  campaignTitle:'HIL 批次執行器',campaignHelp:'分類矩陣保存到 output/hil-campaign/state.json；關閉瀏覽器或對話後仍可繼續。',campaignRules:'執行規則',campaignRulesHelp:'Prepare 只檢查目前 profile；只有 READY 案例可送 RF。BLOCKED 不會改跑其他 profile。Pause／Stop 只會在單點 cleanup 與 RF Off 邊界生效。',campaignSop1:'準備矩陣',campaignSop2:'依 Priority 接線',campaignSop3:'只執行 READY',campaignSop4:'保存證據',prepareCampaign:'STEP 1：準備／重新檢查矩陣',runNextCampaign:'STEP 3：執行下一個 READY',refreshCampaign:'重新載入',resetCampaign:'重設進度',campaignOperatorConfirm:'操作員在機台旁',campaignRouteConfirm:'RF1.1 Generator output 已接到 RF1.5 Analyzer input',campaignPriority:'重要度',campaignState:'狀態',campaignCategory:'類別',campaignCase:'案例',campaignRoute:'接線',campaignPoints:'點數',campaignEvidence:'下一步／證據',campaignAction:'操作',
  calibrationTitle:'Path Loss 校正 SOP',calibrationHelp:'輸入校正設備的參考面讀值，建立待審查 Draft Profile；此頁不會控制儀器或開啟 RF。',calibrationSop1:'登錄器材',calibrationSop2:'取得讀值',calibrationSop3:'檢查線損',calibrationSop4:'送交核准',calculateDraft:'計算 Draft Profile',draftPreview:'Draft 預覽',downloadDraft:'下載 Draft YAML'
});
Object.assign(translations.en,{
  hardwareSource:'Hardware Measurement',demoSource:'Demo & Training',hardwareSop1:'Set values',hardwareSop2:'Check cabling and operator',hardwareSop3:'Review plan',hardwareSop4:'Execute and save artifacts',
  measurementSettings:'Measurement settings',measurementSettingsHelp:'Select the measurement type and enter the frequency, power, bandwidth, and point count.',singleSetup:'SingleShot setup',singleSetupHelp:'Enter center frequency, WLAN bandwidth, and generator power. The Web checks the approved profile before CMP180 control and requires final confirmation.',reviewSingle:'Review SingleShot plan',sweepSetup:'Sweep setup',sweepSetupHelp:'Set the WLAN EVM sweep axis, range, step, and dwell. Points, estimated time, and safety checks are shown before execution.',reviewPlan:'Review measurement plan',reviewGprf:'Review GPRF plan',safetyCheck:'Cabling and operator safety check',safetyCheckHelp:'Only RF1.1 → RF1.5 is approved. Confirm the direct path has no extra attenuator and an operator is beside the instrument.',directCableConfirm:'I confirm the approved direct path has no unrecorded attenuator or adapter',directCableCheck:'Direct path / no unrecorded attenuator',executeHardware:'Execute hardware measurement',executeHardwareHelp:'A final confirmation is still shown. Cancelling transmits no RF; artifacts are saved after completion.',
  loopbackTitle:'Loopback RF Performance Validation',loopbackHelp:'Run independent SingleShot repeats under fixed conditions to validate the tester, cable, UD Box, and RF path; this is not a DUT PASS.',loopbackWarning:'Stable is not necessarily reasonable',loopbackWarningHelp:'Stability evaluates repeatability; Reasonableness compares Expected RX Power at the analyzer input reference plane. Matching representative points and thresholds with at least Repeat 10 use approved baselines; other conditions remain draft.',loopbackCableConfirm:'Cabling, Cable/UD Box path, and attenuation conditions are confirmed and will remain unchanged',loopbackOperatorConfirm:'An operator is beside the CMP180 and can respond to RF anomalies',runLoopback:'Review and run Loopback',runAllLoopbacks:'Run all 11 profiles × Repeat 10',runAllLoopbacksHelp:'Runs 110 SingleShots sequentially. Each profile saves an independent artifact; any SCPI or cleanup error stops the batch.',loopbackTrends:'Live repeat trends',loopbackTrendsHelp:'Red dots indicate INVALID or IQR outliers; data is never deleted',
  campaignTitle:'HIL Campaign Runner',campaignHelp:'The categorized matrix is saved to output/hil-campaign/state.json and can continue after closing the browser or conversation.',campaignRules:'Execution rules',campaignRulesHelp:'Prepare only checks the current profile; only READY cases may transmit RF. BLOCKED never substitutes another profile. Pause/Stop takes effect only at a SingleShot cleanup and RF Off boundary.',campaignSop1:'Prepare matrix',campaignSop2:'Cable by priority',campaignSop3:'Run READY only',campaignSop4:'Save evidence',prepareCampaign:'STEP 1: Prepare / recheck matrix',runNextCampaign:'STEP 3: Run next READY',refreshCampaign:'Reload',resetCampaign:'Reset progress',campaignOperatorConfirm:'Operator is beside the instrument',campaignRouteConfirm:'RF1.1 Generator output is connected to RF1.5 Analyzer input',campaignPriority:'Priority',campaignState:'State',campaignCategory:'Category',campaignCase:'Case',campaignRoute:'Route',campaignPoints:'Points',campaignEvidence:'Next step / Evidence',campaignAction:'Action',
  calibrationTitle:'Path Loss Calibration SOP',calibrationHelp:'Enter reference-plane readings from calibration equipment to create a draft profile for review. This page does not control the instrument or enable RF.',calibrationSop1:'Register equipment',calibrationSop2:'Acquire readings',calibrationSop3:'Check path loss',calibrationSop4:'Submit for approval',calculateDraft:'Calculate Draft Profile',draftPreview:'Draft Preview',downloadDraft:'Download Draft YAML'
});
Object.assign(translations.zh,{demoSingleMode:'示範單點',demoFrequencyMode:'示範頻率掃描',demoPowerMode:'示範功率掃描',hardwareSingleMode:'WLAN EVM 單點',hardwareFrequencyMode:'WLAN EVM 頻率掃描',hardwarePowerMode:'WLAN EVM 功率掃描',hardwareGprfMode:'RF 功率讀值（GPRF）',gprfModeHelp:'GPRF 是 General Purpose RF：此模式只用 CMP180 Gen/Meas 讀 RF power，可看 tune／power flatness；不是 WLAN EVM、不是 compliance。'});
Object.assign(translations.en,{demoSingleMode:'Demo Single',demoFrequencyMode:'Demo Frequency Sweep',demoPowerMode:'Demo Power Sweep',hardwareSingleMode:'WLAN EVM SingleShot',hardwareFrequencyMode:'WLAN EVM Frequency Sweep',hardwarePowerMode:'WLAN EVM Power Sweep',hardwareGprfMode:'RF Power Reading (GPRF)',gprfModeHelp:'GPRF means General Purpose RF: this mode reads RF power with CMP180 Gen/Meas for tune/power-flatness checks; it is not WLAN EVM or compliance.'});
Object.assign(translations.en,{homeTab:'Home',measurementTab:'Measure',calibrationTab:'Calibration',guideTab:'Operator Guide',guideTitle:'From startup to report',guideIntro:'Each card is a directly usable standard procedure. First choose demo data, a query-only check, or an explicitly authorized hardware mode.',guideSafeTitle:'Recommended now: Demo mode',guideSafeText:'Do not enable RF while power is unstable',guideStep1:'Start service',guideStep2:'Select measurement',guideStep3:'Review results',guideStep4:'Open report',demoCommandTitle:'Start the Demo console',demoCommandHelp:'No CMP180 connection, SCPI, or RF. Use it to review and practice the workflow.',copyCommand:'Copy',openBrowser:'Open browser',configCommandTitle:'Validate configuration',configCommandHelp:'Validates YAML fields and safety settings without contacting the instrument.',expectedOutput:'Expected output',connectionCommandTitle:'Query-only connection check',connectionCommandHelp:'Reads IDN, options, and the error queue without starting measurement or RF.',powerWarning:'During unstable power',queryOnlyAdvice:'Run query-only checks only; do not enable hardware Web mode.',hardwareCommandTitle:'Hardware mode (on hold)',hardwareCommandHelp:'Use only with stable power, confirmed cabling, an on-site operator, and explicit authorization.',hardwareHold:'Instrument power is currently unstable; execution is prohibited.',whereResultsTitle:'Where are results stored?',whereResultsText:'Each run creates an independent output folder. Use Open folder in Run History or open HTML, CSV, and JSON from Results.',whenStopTitle:'When must I stop?',whenStopText:'Stop immediately and verify RF OFF on INV, unknown RF state, timeout, SCPI error, cabling change, or power abnormality.'});
let language='zh';let latest=[];let runHistory=[];let analysisTraces=[];const selectedCompareKeys=new Set();
let expandedRunKey=null;
const $=selector=>document.querySelector(selector);
const homeCopy={
  zh:{heroTitle:'讓 RF 量測成為<br><span>可重現的工程流程</span>',heroIntro:'Web 現已支援自訂 SingleShot、頻率／功率掃描、完整座標圖表、Pandas／Matplotlib PNG 與可稽核 artifacts；正式 Path Loss、DUT／UDBox 仍須現場核准後 HIL。',enterConsole:'進入量測控制台',openManual:'查看操作手冊',capabilityTitle:'工程師真正需要的功能',capabilityIntro:'保留 CMsquares 作為探索與除錯參考，把重複操作轉成可驗證、可比較、可交接的自動化流程。',f1t:'安全實機量測',f1p:'Route、操作員、頻率、頻寬與功率通過檢查後，Web 直接設定並控制 CMP180 workflow。',f2t:'頻率與功率掃描',f2p:'逐點進度、取消、partial artifacts，以及任何異常立即停止整批。',f3t:'EVM 結果分析',f3p:'完整軸標題與刻度、EVM／Power／Error，以及由 DataFrame 產生的 Matplotlib PNG。',f4t:'歷史 Run 比較',f4p:'搜尋、篩選、排序並比較 2–8 筆量測，調整 Trace 樣式與匯出圖表。',f5t:'Path Loss 校正',f5p:'軟體管理流程已備妥；正式 Profile 仍需器材、參考面資料與 RF owner 核准。',f6t:'可稽核與可交接',f6p:'原始回應、設定快照、cleanup 狀態、報告與中英操作文件一起保存。',workflowTitle:'五步完成一次可靠量測',manualTitle:'從這裡開始操作',manualIntro:'首頁只說明與導覽；只有進入量測頁並完成最後確認才可能送出 RF。'},
  en:{heroTitle:'Turn RF measurement into<br><span>a reproducible engineering workflow</span>',heroIntro:'The Web now supports custom SingleShot, frequency/power sweeps, fully labelled charts, Pandas/Matplotlib PNG reports, and auditable artifacts. Formal Path Loss and DUT/UDBox HIL still require on-site approval.',enterConsole:'Open measurement console',openManual:'Open operator manual',capabilityTitle:'The capabilities RF engineers need',capabilityIntro:'Keep CMsquares for discovery and troubleshooting while turning repetitive actions into verifiable, comparable, and transferable automation.',f1t:'Safe hardware measurement',f1p:'After route, operator, frequency, bandwidth, and power checks, the Web directly configures the guarded CMP180 workflow.',f2t:'Frequency and power sweeps',f2p:'Per-point progress, cancellation, partial artifacts, and immediate batch stop on abnormal results.',f3t:'EVM result analysis',f3p:'Fully labelled axes and ticks, EVM/Power/Error views, plus DataFrame-generated Matplotlib PNG reports.',f4t:'Historical run comparison',f4p:'Search, filter, sort, and compare 2–8 runs with editable trace styles and chart export.',f5t:'Path Loss calibration',f5p:'The software workflow is ready; formal profiles still require equipment, reference-plane data, and RF-owner approval.',f6t:'Auditable and transferable',f6p:'Preserve raw responses, setting snapshots, cleanup state, reports, and bilingual operator documentation.',workflowTitle:'Five steps to a reliable measurement',manualTitle:'Start here',manualIntro:'The home page only explains and navigates. RF is possible only after entering Measurement and completing final confirmation.'}
};
const pageCopy={zh:{home:['RF AUTOMATION PLATFORM','CMP180 自動化量測','安全、可重現、可分析的 WLAN TX EVM 工程工作站'],measurement:['WLAN TX MEASUREMENT','量測控制台','RF1.1 → RF1.5 · 6105 MHz · 320 MHz · -40 dBm'],campaign:['HIL CAMPAIGN','分類實機驗收','持久化頻段、頻寬、功率、Route 與能力驗收進度'],calibration:['PATH LOSS & CALIBRATION','路徑損耗校正','建立可追溯的線材、轉接頭與參考面補償資料'],results:['RESULT ANALYSIS','結果分析台','檢視 EVM、功率與頻率誤差，或比較多筆歷史量測'],history:['RUN ARCHIVE','量測紀錄庫','搜尋、開啟、比較與管理本機保存的量測成果'],guide:['OPERATOR PLAYBOOK','操作指南','從啟動服務、安全檢查到取得報告的標準流程']},en:{home:['RF AUTOMATION PLATFORM','CMP180 Automation','A safe, reproducible, and analyzable WLAN TX EVM engineering workstation'],measurement:['WLAN TX MEASUREMENT','Measurement Console','RF1.1 → RF1.5 · 6105 MHz · 320 MHz · -40 dBm'],campaign:['HIL CAMPAIGN','Categorized Hardware Acceptance','Persistent band, bandwidth, power, route, and capability acceptance progress'],calibration:['PATH LOSS & CALIBRATION','Path Loss Calibration','Build traceable compensation data for cables, adapters, and reference planes'],results:['RESULT ANALYSIS','Results & Analysis','Review EVM, power, and frequency error or compare historical runs'],history:['RUN ARCHIVE','Run Archive','Search, open, compare, and manage locally stored measurement results'],guide:['OPERATOR PLAYBOOK','Operator Guide','Standard workflow from service startup and safety checks to reports']}};
let activeTopTab='home';
function measurementPageCopy(){
  const hardwareVisible=$('#hardware')?.classList.contains('active');
  if(hardwareVisible){
    const action=$('#hardwareForm')?.elements.hardware_action.value||'single';
    if(action==='frequency')return language==='zh'?['WLAN TX FREQUENCY SWEEP','WLAN 頻率掃描','固定 Generator 功率，量測 EVM 對頻率的變化']:['WLAN TX FREQUENCY SWEEP','WLAN Frequency Sweep','Fixed generator power; measure EVM versus frequency'];
    if(action==='power')return language==='zh'?['WLAN TX POWER SWEEP','WLAN 功率掃描－線性度','固定中心頻率，量測 EVM 對輸入功率的變化']:['WLAN TX POWER SWEEP','WLAN Power Sweep – Linearity','Fixed center frequency; measure EVM versus input power'];
    if(action==='gprf'){
      const frequencyAxis=$('#gprfPowerForm')?.elements.axis.value==='frequency';
      if(frequencyAxis)return language==='zh'?['GPRF FREQUENCY SWEEP','GPRF 頻率掃描－功率平坦度','固定功率；X 軸為 Frequency，分析 Power Flatness']:['GPRF FREQUENCY SWEEP','GPRF Frequency Sweep – Power Flatness','Fixed power; Frequency X axis for power-flatness analysis'];
      return language==='zh'?['GPRF POWER SWEEP','GPRF 功率掃描－線性度','固定頻率；X 軸為 Power，分析輸入／量測功率線性度']:['GPRF POWER SWEEP','GPRF Power Sweep – Linearity','Fixed frequency; Power X axis for input/measured-power linearity'];
    }
    return language==='zh'?['WLAN TX SINGLESHOT','WLAN 單點量測','RF1.1 → RF1.5 · 6105 MHz · 320 MHz · -40 dBm']:['WLAN TX SINGLESHOT','WLAN SingleShot','RF1.1 → RF1.5 · 6105 MHz · 320 MHz · -40 dBm'];
  }
  const demo=document.querySelector('[data-demo-tab].active')?.dataset.demoTab||'single';
  if(demo==='sweep')return language==='zh'?['DEMO FREQUENCY SWEEP','示範頻率掃描','固定功率，X 軸為 Frequency']:['DEMO FREQUENCY SWEEP','Demo Frequency Sweep','Fixed power; Frequency X axis'];
  if(demo==='powerSweep')return language==='zh'?['DEMO POWER SWEEP','示範功率掃描－線性度','固定頻率，X 軸為 Power']:['DEMO POWER SWEEP','Demo Power Sweep – Linearity','Fixed frequency; Power X axis'];
  return language==='zh'?['DEMO SINGLE','示範單點量測','僅產生示範資料，不送出 RF']:['DEMO SINGLE','Demo Single Measurement','Demo data only; no RF transmitted'];
}
function updatePageHeading(){const loopbackCopy=language==='zh'?['LOOPBACK BASELINE','Loopback 驗證','Tester／Cable／UD Box／RF Path 的重複性與合理性']:['LOOPBACK BASELINE','Loopback Validation','Repeatability and reasonableness of the tester, cable, UD Box, and RF path'];const copy=activeTopTab==='measurement'?measurementPageCopy():activeTopTab==='loopback'?loopbackCopy:pageCopy[language][activeTopTab];$('#pageKicker').textContent=copy[0];$('#pageTitle').textContent=copy[1];$('#pageContext').textContent=copy[2]}
function applyLanguage(){document.documentElement.lang=language==='zh'?'zh-Hant':'en';document.querySelectorAll('[data-i18n]').forEach(el=>{const value=translations[language][el.dataset.i18n];if(value)el.textContent=value});document.querySelectorAll('[data-home]').forEach(el=>{const value=homeCopy[language][el.dataset.home];if(value){if(el.dataset.home==='heroTitle')el.innerHTML=value;else el.textContent=value}});document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>{const value=translations[language][el.dataset.i18nPlaceholder];if(value)el.placeholder=value});$('#languageButton').textContent=language==='zh'?'EN':'中文';updatePageHeading();if(window.updateHardwareSummary)window.updateHardwareSummary();if(window.configureGprfFields)window.configureGprfFields();if(runHistory.length)renderRunHistory();
  // 已顯示的 Review／Preview 也要即時換語言，避免操作員讀到上一個語言的安全計畫。
  window.dispatchEvent(new CustomEvent('cmp180-language-change',{detail:{language}}));
}
$('#languageButton').onclick=()=>{language=language==='zh'?'en':'zh';applyLanguage()};
// 只切換 main 的第一層工作區，避免誤清除量測區內的子分頁 active 狀態。
function activateTopTab(tabName){activeTopTab=tabName;document.querySelectorAll('.tabs .tab').forEach(el=>el.classList.toggle('active',el.dataset.tab===tabName));document.querySelectorAll('main > .panel').forEach(el=>el.classList.toggle('active',el.id===tabName));updatePageHeading();if(tabName==='history')loadRunHistory()}
document.querySelectorAll('.tabs .tab').forEach(button=>button.onclick=()=>activateTopTab(button.dataset.tab));
document.querySelectorAll('[data-go-tab]').forEach(button=>button.onclick=()=>{activateTopTab(button.dataset.goTab);window.scrollTo({top:0,behavior:'smooth'})});
document.querySelectorAll('[data-measure-view]').forEach(button=>button.onclick=()=>{document.querySelectorAll('[data-measure-view],.measurement-view').forEach(el=>el.classList.remove('active'));button.classList.add('active');$('#'+button.dataset.measureView).classList.add('active');updatePageHeading()});
document.querySelectorAll('[data-demo-tab]').forEach(button=>button.onclick=()=>{document.querySelectorAll('[data-demo-tab],.demo-panel').forEach(el=>el.classList.remove('active'));button.classList.add('active');$('#'+button.dataset.demoTab).classList.add('active');updatePageHeading()});
function historyLink(url,label){return url?`<a href="${url}" target="_blank" rel="noopener">${label}</a>`:''}
function filteredRuns(){const query=$('#runSearch').value.trim().toLowerCase(),dateFilter=$('#runDateFilter').value,sourceFilter=$('#runSourceFilter').value,statusFilter=$('#runStatusFilter').value,now=Date.now();const filtered=runHistory.filter(run=>{const haystack=[run.test_name,run.run_id,run.dut,run.operator,run.notes,run.route,run.calibration_profile].join(' ').toLowerCase();if(query&&!haystack.includes(query))return false;if(sourceFilter!=='all'&&(sourceFilter==='demo')!==Boolean(run.simulated))return false;if(statusFilter!=='all'&&String(run.status).toLowerCase()!==statusFilter)return false;if(dateFilter!=='all'){const created=Date.parse(run.created_at);if(!Number.isFinite(created))return false;const days=dateFilter==='today'?1:Number(dateFilter);if(now-created>days*86400000)return false}return true});const sort=$('#runSort').value,number=(value,fallback=0)=>Number.isFinite(Number(value))?Number(value):fallback;return filtered.sort((a,b)=>sort==='time-asc'?Date.parse(a.created_at)-Date.parse(b.created_at):sort==='points-desc'?number(b.completed_points)-number(a.completed_points):sort==='frequency-asc'?number(a.frequency_hz,Infinity)-number(b.frequency_hz,Infinity):sort==='power-asc'?number(a.generator_power_dbm,Infinity)-number(b.generator_power_dbm,Infinity):sort==='evm-desc'?number(b.worst_evm_db,-Infinity)-number(a.worst_evm_db,-Infinity):Date.parse(b.created_at)-Date.parse(a.created_at))}
function renderRunHistory(){const labels=language==='zh'?{load:'查看詳情',close:'收合詳情',open:'開啟輸出',trash:'刪除'}:{load:'View details',close:'Close details',open:'Open output',trash:'Delete'};const rows=filteredRuns();$('#historyEmpty').hidden=rows.length>0;$('#historyEmpty').textContent=language==='zh'?'沒有符合條件的量測紀錄。':'No runs match the current filters.';$('#historyRows').innerHTML=rows.map(run=>{const files=run.artifact_urls||{};const links=[historyLink(files.report,'HTML'),historyLink(files.csv,'CSV'),historyLink(files.json,'JSON'),historyLink(files.metadata,'Metadata')].filter(Boolean).join(' · ');const source=run.simulated?'DEMO':'HARDWARE',checked=selectedCompareKeys.has(run.run_key)?'checked':'',expanded=expandedRunKey===run.run_key,openUrl=files.report||files.json||files.csv||files.metadata||'';return `<tr class="run-main-row"><td class="select-column"><input class="run-select" type="checkbox" data-compare-run="${escapeHtml(run.run_key)}" ${checked} aria-label="Select ${escapeHtml(run.test_name)} for comparison"></td><td>${run.created_at?new Date(run.created_at).toLocaleString():'—'}</td><td>${escapeHtml(run.test_name)}</td><td><code>${escapeHtml(run.run_id)}</code></td><td><span class="pill ${run.simulated?'neutral':'hardware-source'}">${source}</span></td><td>${escapeHtml(String(run.status).toUpperCase())}</td><td>${run.completed_points}</td><td class="history-links">${links||'—'}</td><td class="record-actions"><button type="button" data-record-action="load" data-run-key="${escapeHtml(run.run_key)}">${expanded?labels.close:labels.load}</button><button type="button" data-record-action="open" data-open-url="${escapeHtml(openUrl)}" ${openUrl?'':'disabled'}>${labels.open}</button><button type="button" class="danger-mini" data-record-action="trash" data-run-key="${escapeHtml(run.run_key)}" data-run-id="${escapeHtml(run.run_id)}">${labels.trash}</button></td></tr><tr class="run-detail-row" data-detail-row="${escapeHtml(run.run_key)}" ${expanded?'':'hidden'}><td colspan="9"><div class="inline-run-detail">${expanded?'<div class="detail-loading">Loading…</div>':''}</div></td></tr>`}).join('');updateCompareSelection();if(expandedRunKey)loadRunRecord(expandedRunKey,true)}
async function loadRunHistory(){const button=$('#refreshHistoryButton');button.disabled=true;try{const response=await fetch('/api/runs',{cache:'no-store'});const data=await response.json();if(!response.ok)throw new Error(data.error||'Unable to load run history');runHistory=Array.isArray(data.runs)?data.runs:[];const validKeys=new Set(runHistory.map(run=>run.run_key));[...selectedCompareKeys].forEach(key=>{if(!validKeys.has(key))selectedCompareKeys.delete(key)});renderRunHistory()}catch(error){$('#historyEmpty').hidden=false;$('#historyEmpty').textContent=language==='zh'?`無法載入紀錄：${error.message}`:`Unable to load runs: ${error.message}`;toast(error.message,'error')}finally{button.disabled=false}}
function escapeHtml(value){const node=document.createElement('span');node.textContent=String(value);return node.innerHTML}
function updateCompareSelection(){const count=selectedCompareKeys.size;$('#compareCount').textContent=language==='zh'?`已選 ${count} 筆`:`${count} selected`;$('#compareSelectedButton').textContent=count===1?(language==='zh'?'查看所選圖表':'Plot selected run'):(language==='zh'?'比較所選資料':'Compare selected runs');$('#compareSelectedButton').disabled=count<1||count>8}
function finiteNumber(value){const number=Number(value);return Number.isFinite(number)?number:null}
function normalizeHistoricalPoints(record){const source=Array.isArray(record.results)?record.results:(record.results?.points||[]);const metadata=record.metadata||{};return source.map((raw,index)=>{const frequency=finiteNumber(raw.frequency_hz??metadata.frequency_hz??metadata.center_frequency_hz),power=finiteNumber(raw.generator_power_dbm??metadata.generator_power_dbm),evmAll=finiteNumber(raw.evm_all_db??raw.evm_all_carriers_db),evmData=finiteNumber(raw.evm_data_db??raw.evm_data_carriers_db),evmPilot=finiteNumber(raw.evm_pilot_db??raw.evm_pilot_carriers_db),burstPower=finiteNumber(raw.burst_power_dbm),expectedPower=finiteNumber(raw.expected_power_dbm??raw.generator_power_dbm??metadata.generator_power_dbm),powerError=burstPower!==null&&expectedPower!==null?burstPower-expectedPower:null,peakPower=finiteNumber(raw.peak_power_dbm),frequencyError=finiteNumber(raw.frequency_error_hz),clockError=finiteNumber(raw.clock_error_ppm??raw.clock_error),pin=finiteNumber(raw.pin_dbm),pout=finiteNumber(raw.pout_dbm),gain=finiteNumber(raw.gain_db);return {point_index:Number(raw.point_index??index),frequency_hz:frequency,generator_power_dbm:power,expected_power_dbm:expectedPower,power_error_db:powerError,pin_dbm:pin,pout_dbm:pout,gain_db:gain,evm_all_db:evmAll,evm_data_db:evmData,evm_pilot_db:evmPilot,burst_power_dbm:burstPower,peak_power_dbm:peakPower,frequency_error_hz:frequencyError,clock_error_ppm:clockError,measurement_state:String(raw.measurement_state||''),valid:[evmAll,burstPower,frequencyError,pout,gain].some(value=>value!==null)&&String(raw.measurement_state||'').toUpperCase()!=='INV',limit_status:String(raw.limit_status||raw.status||'RECORDED')}})}
function inferTraceAxis(points){const frequencies=new Set(points.map(point=>point.frequency_hz).filter(value=>value!==null));const powers=new Set(points.map(point=>point.generator_power_dbm).filter(value=>value!==null));return powers.size>frequencies.size?'power':'frequency'}
const traceColors=['#18d7e5','#f59e0b','#a78bfa','#43c47a','#f05261','#60a5fa','#f472b6','#eab308'];
async function compareSelectedRuns(){const button=$('#compareSelectedButton');button.disabled=true;try{const keys=[...selectedCompareKeys];const records=await Promise.all(keys.map(async key=>{const response=await fetch(`/api/runs/${encodeURIComponent(key)}`);const record=await response.json();if(!response.ok)throw new Error(record.error||`Unable to load ${key}`);return record}));analysisTraces=records.map((record,index)=>{const summary=runHistory.find(run=>run.run_key===record.run_key)||{};const points=normalizeHistoricalPoints(record);return {id:record.run_key,name:summary.test_name||record.metadata?.test_name||record.metadata?.run_id||record.run_key,color:traceColors[index],visible:true,colorLocked:false,lineStyle:'solid',pointShape:'circle',axis:inferTraceAxis(points),compatibility:{bandwidth:summary.bandwidth_hz,route:summary.route,calibration:summary.calibration_profile,waveform:record.metadata?.waveform_file||record.metadata?.arb_waveform_file||'',mcs:record.metadata?.mcs||''},points}}).filter(trace=>trace.points.length);if(analysisTraces.length<1)throw new Error(language==='zh'?'所選紀錄沒有可用結果':'The selected run has no usable results');latestAxis=analysisTraces[0].axis;latest=analysisTraces[0].points;selectBestChartMetric(latest,records[0]);renderComparisonControls();const isSingle=analysisTraces.length===1;$('#runMeta').textContent=language==='zh'?(isSingle?'查看 1 筆歷史量測（唯讀）':`比較 ${analysisTraces.length} 筆歷史量測（唯讀）`):(isSingle?'Viewing 1 historical run (read-only)':`Comparing ${analysisTraces.length} historical runs (read-only)`);$('#resultBadge').textContent=isSingle?'HISTORY':'COMPARE';$('#metrics').innerHTML=metric('Runs',analysisTraces.length)+metric('Visible',analysisTraces.filter(trace=>trace.visible).length)+metric('Points',analysisTraces.reduce((sum,trace)=>sum+trace.points.length,0))+metric('Mode','READ ONLY');$('#limitProfileCard').hidden=true;$('#resultRows').innerHTML='';$('#artifacts').innerHTML='';renderMatplotlibGallery({});activateTopTab('results');drawAnalysisChart()}catch(error){toast(error.message,'error')}finally{updateCompareSelection()}}
function compatibilityWarnings(){const fields=['bandwidth','waveform','mcs','route','calibration'];return fields.filter(field=>new Set(analysisTraces.map(trace=>trace.compatibility[field]).filter(Boolean)).size>1)}
function renderComparisonControls(){$('#comparisonPanel').hidden=false;const axes=new Set(analysisTraces.map(trace=>trace.axis)),warnings=compatibilityWarnings();$('#comparisonHint').textContent=warnings.length?(language==='zh'?`相容性警告：${warnings.join('、')} 不一致，禁止直接做合規結論。`:`Compatibility warning: ${warnings.join(', ')} differ; do not infer compliance.`):axes.size>1?(language==='zh'?'資料包含不同掃描軸；請確認比較目的。':'Runs use different sweep axes; verify comparison intent.'):(language==='zh'?'EVM 越負通常越好；INVALID 點會中斷，不與正常資料連線。':'More-negative EVM is generally better; INVALID points break traces.');$('#traceList').innerHTML=analysisTraces.map((trace,index)=>`<div class="trace-control" draggable="true" data-trace-index="${index}"><button class="trace-drag" type="button" title="Drag to reorder">⋮⋮</button><input type="checkbox" data-trace-visible="${index}" ${trace.visible?'checked':''} title="Hide / Show"><input type="color" data-trace-color="${index}" value="${trace.color}" ${trace.colorLocked?'disabled':''}><input type="text" data-trace-name="${index}" value="${escapeHtml(trace.name)}"><select data-trace-line="${index}" title="Line style"><option value="solid" ${trace.lineStyle==='solid'?'selected':''}>Solid</option><option value="dash" ${trace.lineStyle==='dash'?'selected':''}>Dash</option><option value="dot" ${trace.lineStyle==='dot'?'selected':''}>Dot</option></select><select data-trace-point="${index}" title="Point shape"><option value="circle" ${trace.pointShape==='circle'?'selected':''}>●</option><option value="square" ${trace.pointShape==='square'?'selected':''}>■</option><option value="diamond" ${trace.pointShape==='diamond'?'selected':''}>◆</option></select><button type="button" data-trace-solo="${index}">Solo</button><button type="button" data-trace-lock="${index}" title="Color lock">${trace.colorLocked?'🔒':'🔓'}</button><button type="button" class="trace-remove" data-trace-remove="${index}" title="Remove">×</button><small>${trace.points.length} pts</small></div>`).join('')}
$('#compareSelectedButton').onclick=compareSelectedRuns;
$('#traceList').oninput=event=>{const index=Number(event.target.dataset.traceVisible??event.target.dataset.traceColor??event.target.dataset.traceName??event.target.dataset.traceLine??event.target.dataset.tracePoint);if(!Number.isInteger(index)||!analysisTraces[index])return;if(event.target.dataset.traceVisible!==undefined)analysisTraces[index].visible=event.target.checked;if(event.target.dataset.traceColor!==undefined&&!analysisTraces[index].colorLocked)analysisTraces[index].color=event.target.value;if(event.target.dataset.traceName!==undefined)analysisTraces[index].name=event.target.value;if(event.target.dataset.traceLine!==undefined)analysisTraces[index].lineStyle=event.target.value;if(event.target.dataset.tracePoint!==undefined)analysisTraces[index].pointShape=event.target.value;drawAnalysisChart()};
$('#traceList').onclick=event=>{const solo=event.target.closest('[data-trace-solo]'),lock=event.target.closest('[data-trace-lock]'),remove=event.target.closest('[data-trace-remove]');if(solo){const index=Number(solo.dataset.traceSolo);analysisTraces.forEach((trace,i)=>trace.visible=i===index)}if(lock){const index=Number(lock.dataset.traceLock);analysisTraces[index].colorLocked=!analysisTraces[index].colorLocked}if(remove){analysisTraces.splice(Number(remove.dataset.traceRemove),1)}if(solo||lock||remove){renderComparisonControls();drawAnalysisChart()}};
let draggedTraceIndex=null;$('#traceList').ondragstart=event=>{const item=event.target.closest('[data-trace-index]');if(item)draggedTraceIndex=Number(item.dataset.traceIndex)};$('#traceList').ondragover=event=>event.preventDefault();$('#traceList').ondrop=event=>{event.preventDefault();const target=event.target.closest('[data-trace-index]');if(target&&draggedTraceIndex!==null){const [trace]=analysisTraces.splice(draggedTraceIndex,1);analysisTraces.splice(Number(target.dataset.traceIndex),0,trace);renderComparisonControls();drawAnalysisChart()}draggedTraceIndex=null};
$('#refreshHistoryButton').onclick=loadRunHistory;
function metadataTable(metadata){return `<dl class="settings-list">${Object.entries(metadata).map(([key,value])=>`<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(typeof value==='object'?JSON.stringify(value):value)}</dd>`).join('')}</dl>`}
async function loadRunRecord(runKey,alreadyExpanded=false){if(!alreadyExpanded&&expandedRunKey===runKey){expandedRunKey=null;renderRunHistory();return}expandedRunKey=runKey;if(!alreadyExpanded)renderRunHistory();const row=document.querySelector(`[data-detail-row="${CSS.escape(runKey)}"]`),container=row?.querySelector('.inline-run-detail');if(!container)return;const response=await fetch(`/api/runs/${encodeURIComponent(runKey)}`);const record=await response.json();if(!response.ok)throw new Error(record.error||'Unable to load record');const waveform=record.waveform_recorded?escapeHtml(record.waveform_reference):(language==='zh'?'未保存 Waveform reference':'Waveform reference not saved');container.innerHTML=`<div class="inline-detail-head"><div><strong>Run ${escapeHtml(record.metadata.run_id||runKey)}</strong><code>${escapeHtml(record.output_location)}</code></div><span>${language==='zh'?'詳情顯示於原紀錄下方':'Details shown under the selected run'}</span></div><div class="history-detail-grid"><div><h4>Settings / 設定</h4>${metadataTable(record.metadata)}</div><div><h4>Waveform / 波形</h4><p>${waveform}</p><h4>Raw files</h4><p>${record.raw_files.length?escapeHtml(record.raw_files.join(', ')):(language==='zh'?'無 raw 檔案':'No raw files')}</p></div></div><details><summary>Results JSON / 過去量測值</summary><pre>${escapeHtml(JSON.stringify(record.results,null,2))}</pre></details>`}
async function postRecordAction(runKey,action,payload={}){const response=await fetch(`/api/runs/${encodeURIComponent(runKey)}/${action}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const data=await response.json();if(!response.ok)throw new Error(data.error||'Record action failed');return data}
$('#historyRows').onclick=async event=>{const checkbox=event.target.closest('[data-compare-run]');if(checkbox){checkbox.checked?selectedCompareKeys.add(checkbox.dataset.compareRun):selectedCompareKeys.delete(checkbox.dataset.compareRun);updateCompareSelection();return}const button=event.target.closest('[data-record-action]');if(!button)return;const action=button.dataset.recordAction,runKey=button.dataset.runKey;button.disabled=true;try{if(action==='load')await loadRunRecord(runKey);if(action==='open'){const url=button.dataset.openUrl;if(!url)throw new Error(language==='zh'?'此紀錄沒有可開啟的輸出檔案':'This run has no browser-readable output');window.open(url,'_blank','noopener');toast(language==='zh'?'已在新分頁開啟輸出':'Output opened in a new tab')}if(action==='trash'){const runId=button.dataset.runId;const typed=prompt(language==='zh'?`刪除防呆：輸入 Run ID ${runId}，紀錄將移至可復原 Trash。`:`Safety check: type Run ID ${runId}; the run will move to recoverable Trash.`);if(typed!==runId){toast(language==='zh'?'Run ID 不符，已取消刪除':'Run ID mismatch; deletion cancelled','error');return}if(!confirm(language==='zh'?'確定將此完整 Run 與 artifacts 移至 Trash？':'Move this complete run and its artifacts to Trash?'))return;await postRecordAction(runKey,'trash',{confirm_run_id:typed});expandedRunKey=null;await loadRunHistory();toast(language==='zh'?'紀錄已移至可復原 Trash':'Run moved to recoverable Trash')}}catch(error){toast(error.message,'error')}finally{button.disabled=false}};
$('#closeHistoryDetail').onclick=()=>{$('#historyDetail').hidden=true};
['runSearch','runDateFilter','runSourceFilter','runStatusFilter','runSort'].forEach(id=>{$('#'+id).addEventListener(id==='runSearch'?'input':'change',renderRunHistory)});
function toast(message,type='info'){const node=$('#toast');node.textContent=message;node.dataset.type=type;node.classList.add('show');setTimeout(()=>node.classList.remove('show'),4800)}
async function send(path,payload,button){button.disabled=true;try{const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const data=await response.json();if(!response.ok)throw new Error(data.error||'Request failed');render(data);document.querySelector('[data-tab="results"]').click();return data}catch(error){toast(error.message,'error');return null}finally{button.disabled=false}}
let activeJobId=null,latestJobState='ready';
function renderLiveMeasurement(job){const panel=$('#liveMeasurementPanel');if(!panel)return;const points=job.live_points||[];panel.hidden=false;$('#liveMeasurementCount').textContent=`${job.completed_points} / ${job.total_points}`;const last=points.at(-1),value=last?.evm_all_db;$('#liveMeasurementValue').textContent=last?`EVM All ${Number.isFinite(Number(value))?Number(value).toFixed(3)+' dB':'INVALID'} · ${job.message}`:'等待第一個量測點';const svg=$('#liveMeasurementChart');if(!points.length){svg.innerHTML='<text x="450" y="110" text-anchor="middle" class="axis-label">Waiting for first completed point</text>';return}const valid=points.map((point,index)=>({index,value:Number(point.evm_all_db),valid:point.valid!==false&&Number.isFinite(Number(point.evm_all_db))})).filter(point=>point.valid);if(!valid.length){svg.innerHTML='<text x="450" y="110" text-anchor="middle" class="axis-label">INVALID — batch will stop safely</text>';return}const min=Math.min(...valid.map(point=>point.value)),max=Math.max(...valid.map(point=>point.value)),span=Math.max(max-min,.5),x=index=>70+(index/Math.max(points.length-1,1))*790,y=value=>180-((value-(min-span*.15))/(span*1.3))*140;let path='',open=false;points.forEach((point,index)=>{const value=Number(point.evm_all_db),ok=point.valid!==false&&Number.isFinite(value);if(!ok){open=false;return}path+=`${open?'L':'M'}${x(index).toFixed(1)},${y(value).toFixed(1)} `;open=true});svg.innerHTML=`<line x1="70" y1="180" x2="860" y2="180" class="grid-line"/><path d="${path}" class="plot-line"/>${points.map((point,index)=>{const value=Number(point.evm_all_db),ok=point.valid!==false&&Number.isFinite(value);return ok?`<circle cx="${x(index)}" cy="${y(value)}" r="5" class="plot-dot"><title>Point ${index+1} · EVM ${value.toFixed(3)} dB</title></circle>`:''}).join('')}`}
function updateBlockJobState(job){const state=job?.state||'ready',active=['queued','running','paused','stopping'].includes(state),paused=state==='paused',controllable=Boolean(activeJobId)&&active;/* 積木介面已移除；工作狀態只更新單一進度列與 Pause/Resume，避免兩套控制互相矛盾。 */$('#pauseJobButton').hidden=paused;$('#resumeJobButton').hidden=!paused;$('#pauseJobButton').disabled=!controllable||state==='stopping';$('#resumeJobButton').disabled=!paused||!activeJobId}
async function startJob(path,payload,button,axis){button.disabled=true;try{const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const job=await response.json();if(!response.ok)throw new Error(job.error||'Unable to start job');activeJobId=job.job_id;$('#jobPanel').hidden=false;$('#liveMeasurementPanel').hidden=false;$('#jobTitle').textContent=axis==='power'?'Power sweep':'Frequency sweep';updateBlockJobState(job);renderLiveMeasurement(job);await pollJob(axis)}catch(error){toast(error.message,'error');button.disabled=false;updateBlockJobState(null)}}
async function pollJob(axis){if(!activeJobId)return;const response=await fetch(`/api/jobs/${activeJobId}`);const job=await response.json();latestJobState=job.state;$('#jobState').textContent=job.state.toUpperCase();$('#jobMessage').textContent=job.message||job.error||'Preparing';$('#jobProgress').value=job.progress_percent;$('#jobCount').textContent=`${job.completed_points} / ${job.total_points}`;$('#cancelJobButton').disabled=!['queued','running','paused','stopping'].includes(job.state);updateBlockJobState(job);renderLiveMeasurement(job);if(['complete','cancelled'].includes(job.state)){job.result.sweep_axis=axis;render(job.result);document.querySelector('[data-tab="results"]').click();document.querySelectorAll('form .submit').forEach(button=>button.disabled=false);activeJobId=null;latestJobState=job.state;updateBlockJobState(null);return}if(job.state==='failed'){toast(job.error,'error');document.querySelectorAll('form .submit').forEach(button=>button.disabled=false);activeJobId=null;latestJobState='failed';updateBlockJobState(null);return}setTimeout(()=>pollJob(axis),150)}
$('#cancelJobButton').onclick=async()=>{if(!activeJobId)return;$('#cancelJobButton').disabled=true;await fetch(`/api/jobs/${activeJobId}/cancel`,{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})};
async function toggleJobPause(){if(!activeJobId)return;const action=latestJobState==='paused'?'resume':'pause';await fetch(`/api/jobs/${activeJobId}/${action}`,{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'})}
$('#pauseJobButton').onclick=()=>toggleJobPause();$('#resumeJobButton').onclick=()=>toggleJobPause();updateBlockJobState(null);
$('#singleForm').onsubmit=event=>{event.preventDefault();const form=new FormData(event.target);send('/api/mock/single',{frequency_hz:+form.get('frequency_mhz')*1e6,bandwidth_hz:+form.get('bandwidth_mhz')*1e6,generator_power_dbm:+form.get('power_dbm'),test_name:form.get('test_name')},event.submitter)};
$('#sweepForm').onsubmit=event=>{event.preventDefault();const form=new FormData(event.target);startJob('/api/jobs/mock/frequency-sweep',{start_hz:+form.get('start_mhz')*1e6,stop_hz:+form.get('stop_mhz')*1e6,step_hz:+form.get('step_mhz')*1e6,bandwidth_hz:+form.get('bandwidth_mhz')*1e6,generator_power_dbm:+form.get('power_dbm'),dwell_ms:+form.get('dwell_ms'),test_name:form.get('test_name')},event.submitter,'frequency')};
// 表單顯示 MHz，但 API 與 workflow 一律使用 Hz；此處集中做 1e6 單位轉換。
$('#powerSweepForm').onsubmit=event=>{event.preventDefault();const form=new FormData(event.target);startJob('/api/jobs/mock/power-sweep',{frequency_hz:+form.get('frequency_mhz')*1e6,bandwidth_hz:+form.get('bandwidth_mhz')*1e6,start_dbm:+form.get('start_dbm'),stop_dbm:+form.get('stop_dbm'),step_dbm:+form.get('step_dbm'),dwell_ms:+form.get('dwell_ms'),test_name:form.get('test_name')},event.submitter,'power')};
let latestAxis='frequency';
// 目前結果套用的 EVM spec limit（dB）；null 代表本次沒有套用 limit profile。
let latestSpecLimitDb=null;
function xFieldFor(axis){return axis==='power'?'generator_power_dbm':'frequency_hz'}
function xUnitFor(axis){return axis==='power'?'dBm':'MHz'}
function xDisplayFor(axis,value){return axis==='power'?value.toFixed(1):(value/1e6).toFixed(1)}
function formatMeasured(value,digits=2){return Number.isFinite(value)?value.toFixed(digits):'—'}
function powerFlatnessStats(points){
  const rows=points.map(point=>{
    const measured=finiteNumber(point.burst_power_dbm),expected=finiteNumber(point.expected_power_dbm??point.generator_power_dbm);
    if(measured===null||expected===null)return null;
    return {measured,expected,error:measured-expected,valid:point.valid!==false};
  }).filter(Boolean);
  const valid=rows.filter(row=>row.valid);
  if(!valid.length)return null;
  const avgMeasured=valid.reduce((sum,row)=>sum+row.measured,0)/valid.length;
  const avgExpected=valid.reduce((sum,row)=>sum+row.expected,0)/valid.length;
  const errors=valid.map(row=>row.error),meanError=errors.reduce((sum,value)=>sum+value,0)/errors.length;
  const maxAbsError=Math.max(...errors.map(Math.abs)),minError=Math.min(...errors),maxError=Math.max(...errors);
  const variance=errors.reduce((sum,value)=>sum+(value-meanError)**2,0)/errors.length;
  return {avgMeasured,avgExpected,meanError,maxAbsError,ripple:maxError-minError,stdDev:Math.sqrt(variance),valid:valid.length,total:points.length};
}
function p1dbMetrics(p1db){
  if(!p1db||p1db.status==='frequency_sweep')return '';
  const value=(name,unit)=>Number.isFinite(Number(p1db[name]))?Number(p1db[name]).toFixed(2)+unit:'—';
  if(p1db.status==='found')return metric('IP1dB',value('ip1db_dbm',' dBm'))+metric('OP1dB',value('op1db_dbm',' dBm'))+metric('Small-signal Gain',value('small_signal_gain_db',' dB'));
  // 尚未掃到 1 dB 壓縮時仍顯示已觀察到的最大壓縮與最大 Pin/Pout，避免誤填假 P1dB。
  return metric('P1dB','not_found')+metric('Max Compression',value('max_compression_db',' dB'))+metric('Max Pin',value('max_measured_pin_dbm',' dBm'))+metric('Max Pout',value('max_measured_pout_dbm',' dBm'));
}
function render(data){
  // 新量測結果取代歷史比較狀態，避免圖例與單次結果互相混淆。
  analysisTraces=[];
  $('#comparisonPanel').hidden=true;
  latest=data.points.map(point=>{
    const measured=finiteNumber(point.burst_power_dbm),expected=finiteNumber(point.expected_power_dbm??point.generator_power_dbm);
    const pin=finiteNumber(point.pin_dbm),pout=finiteNumber(point.pout_dbm),gain=finiteNumber(point.gain_db);
    // Power Error 是 GPRF flatness 的工程量：量到的功率減去該點期望功率。
    return {...point,power_error_db:measured!==null&&expected!==null?measured-expected:null,expected_power_dbm:expected,pin_dbm:pin,pout_dbm:pout,gain_db:gain};
  });
  latestAxis=data.sweep_axis||'frequency';
  selectBestChartMetric(latest,data);
  const xField=xFieldFor(latestAxis);
  const validEvm=latest.map(point=>point.evm_all_db).filter(Number.isFinite);
  const avg=validEvm.length?validEvm.reduce((sum,value)=>sum+value,0)/validEvm.length:null;
  const worst=validEvm.length?Math.max(...validEvm):null;
  const pass=latest.filter(point=>['PASS','DRAFT_PASS'].includes(point.limit_status)).length;
  const measured=latest.filter(point=>point.valid&&point.limit_status==='MEASURED').length;
  const fixedLabel=latestAxis==='power'?'Frequency':'Power';
  const fixedValue=latestAxis==='power'?(latest[0].frequency_hz/1e6).toFixed(1)+' MHz':latest[0].generator_power_dbm+' dBm';
  const sourceLabel=data.simulated?(language==='zh'?'示範資料':'DEMO DATA'):'HARDWARE';
  $('#runMeta').textContent=`Run ${data.artifacts.run_id} · ${latest.length} points · ${sourceLabel}`;
  $('#resultBadge').textContent=sourceLabel;
  $('#xAxisHeader').textContent=xUnitFor(latestAxis);
  const statusLabel=data.limit_profile?.lifecycle==='draft'?'DRAFT PASS':data.limit_profile?'PASS':'Measured';
  // PASS 分母是「有效點數」而非全部點數：無效點沒有做過規格判定，不該被算進去。
  const validCount=latest.filter(point=>point.valid).length;
  const invalidCount=latest.length-validCount;
  const statusCount=data.limit_profile?pass:measured;
  const statusTotal=data.limit_profile?validCount:latest.length;
  latestSpecLimitDb=data.limit_profile?data.limit_profile.maximum_evm_db:null;
  // margin = limit - measured，正值代表優於限值；此符號約定與 backend 的 margin_db 相同。
  const margins=latest.filter(point=>point.valid&&Number.isFinite(point.margin_db)).map(point=>point.margin_db);
  const avgMargin=margins.length?margins.reduce((sum,value)=>sum+value,0)/margins.length:null;
  const worstMargin=margins.length?Math.min(...margins):null;
  const signed=value=>(value>0?'+':'')+value.toFixed(2)+' dB';
  const powerStats=powerFlatnessStats(latest),isGprf=data.measurement_family==='GPRF_POWER';
  $('#metrics').innerHTML=isGprf&&powerStats
    ? metric('Average Power',powerStats.avgMeasured.toFixed(3)+' dBm')
    +p1dbMetrics(data.p1db)
    +metric('Expected Power',powerStats.avgExpected.toFixed(3)+' dBm')
    +metric('Mean Error',(powerStats.meanError>=0?'+':'')+powerStats.meanError.toFixed(3)+' dB')
    +metric('Max |Error|',powerStats.maxAbsError.toFixed(3)+' dB')
    +metric('Peak-to-Peak Ripple',powerStats.ripple.toFixed(3)+' dB')
    +metric('Std Dev',powerStats.stdDev.toFixed(3)+' dB')
    +metric('Valid',`${powerStats.valid}/${powerStats.total}`)
    +metric(fixedLabel,fixedValue)
    : metric('Avg EVM',avg===null?'—':avg.toFixed(2)+' dB')
    +metric('Worst EVM',worst===null?'—':worst.toFixed(2)+' dB')
    +metric('Spec Limit',latestSpecLimitDb===null?'—':latestSpecLimitDb.toFixed(2)+' dB')
    +metric('Avg Margin',avgMargin===null?'—':signed(avgMargin))
    +metric('Worst Margin',worstMargin===null?'—':signed(worstMargin))
    +metric(statusLabel,`${statusCount}/${statusTotal}`)
    +metric('Invalid',`${invalidCount}`)
    +metric(fixedLabel,fixedValue);
  // 只有真的存在 INVALID 點才提示，避免讓操作員誤以為本次量測含無效資料。
  const hint=$('#chartHint');
  if(hint&&isGprf)hint.textContent=language==='zh'
    ?'GPRF power：藍線是量測功率，橘色虛線是 Expected power；Power Error = measured - expected'
    :'GPRF power: blue is measured power, orange dashed line is expected power; Power Error = measured - expected';
  else if(hint)hint.textContent=invalidCount
    ?(language==='zh'?'EVM dB 越負通常越好；PASS 區在 limit line 下方；INVALID 不與有效點連線':'Lower (more negative) EVM is better; PASS zone is below the limit line; INVALID points are not connected')
    :(language==='zh'?'EVM dB 越負通常越好；PASS 區在 limit line 下方':'Lower (more negative) EVM is better; PASS zone is below the limit line');
  renderLimitProfile(data.limit_profile,data.compliance_claim);
  // INV／null 是量測無效訊號，表格以破折號呈現，不得補零或讓前端拋出例外。
  $('#resultRows').innerHTML=latest.map(point=>`<tr><td>${point.point_index+1}</td><td>${xDisplayFor(latestAxis,point[xField])}</td><td>${formatMeasured(point.evm_all_db)}</td><td>${formatMeasured(point.burst_power_dbm)}</td><td>${formatMeasured(point.power_error_db,3)}</td><td>${formatMeasured(point.frequency_error_hz)}</td><td class="${point.limit_status.toLowerCase()}">${point.limit_status}</td></tr>`).join('');
  const urls=data.artifact_urls||{};
  $('#artifacts').innerHTML=['csv','json','report'].filter(key=>urls[key]).map(key=>`<a href="${urls[key]}" target="_blank" rel="noopener">${key==='report'?'HTML':key.toUpperCase()}</a>`).join(' · ');
  renderMatplotlibGallery(urls);
  drawChart(latest,latestAxis);
}
function renderLimitProfile(profile,complianceClaim){const card=$('#limitProfileCard');if(!profile){card.hidden=true;return}card.hidden=false;const warning=complianceClaim?'APPROVED':'DRAFT · NOT A DUT COMPLIANCE CLAIM';card.innerHTML=`<strong>${escapeHtml(profile.profile_id)} · ${escapeHtml(profile.revision)}</strong><span class="pill ${complianceClaim?'hardware-source':'draft-limit'}">${warning}</span><p>EVM ≤ ${profile.maximum_evm_db} dB · |Frequency Error| ≤ ${profile.maximum_absolute_frequency_error_hz} Hz · |Power Error| ≤ ${profile.maximum_absolute_power_error_db} dB</p>`}
function metric(label,value){return `<div class="metric"><small>${label}</small><strong>${value}</strong></div>`}
function metricAxisLabel(metricName){return {evm_all_db:'EVM All (dB)',evm_data_db:'EVM Data (dB)',evm_pilot_db:'EVM Pilot (dB)',burst_power_dbm:'Burst Power (dBm)',pin_dbm:'PA Pin (dBm)',pout_dbm:'PA Pout (dBm)',gain_db:'PA Gain (dB)',power_error_db:'Power Error (dB)',peak_power_dbm:'Peak Power (dBm)',frequency_error_hz:'Frequency Error (Hz)',clock_error_ppm:'Clock Error (ppm)'}[metricName]||metricName}
const metricOrder=['evm_all_db','evm_data_db','evm_pilot_db','burst_power_dbm','pin_dbm','pout_dbm','gain_db','power_error_db','peak_power_dbm','frequency_error_hz','clock_error_ppm'];
function selectBestChartMetric(points,data={}){
  // 新結果進來時只自動選一次最有趨勢意義的指標；使用者之後手動切換不會重算資料。
  const preferred=data.measurement_family==='GPRF_POWER'?['gain_db','pout_dbm','burst_power_dbm','power_error_db','frequency_error_hz']:metricOrder;
  const selected=[...preferred,...metricOrder].find(metricName=>points.some(point=>Number.isFinite(point[metricName])));
  if(selected)$('#chartMetric').value=selected;
}
const matplotlibLabels={
  matplotlib_evm_all_carriers_db:{label:'EVM All (dB)',unit:'Y: EVM All (dB)'},
  matplotlib_burst_power_dbm:{label:'Burst Power (dBm)',unit:'Y: Burst Power (dBm)'},
  matplotlib_pin_dbm:{label:'PA Pin (dBm)',unit:'Y: PA Pin (dBm)'},
  matplotlib_pout_dbm:{label:'PA Pout (dBm)',unit:'Y: PA Pout (dBm)'},
  matplotlib_gain_db:{label:'PA Gain (dB)',unit:'Y: PA Gain (dB)'},
  matplotlib_frequency_error_hz:{label:'Frequency Error (Hz)',unit:'Y: Frequency Error (Hz)'},
  matplotlib_clock_error_ppm:{label:'Clock Error (ppm)',unit:'Y: Clock Error (ppm)'}
};
function renderMatplotlibGallery(urls){
  const plots=Object.entries(urls||{}).filter(([key])=>key.startsWith('matplotlib_'));
  const section=$('#matplotlibGallery'),select=$('#matplotlibMetric'),preview=$('#matplotlibPlots'),open=$('#matplotlibOpen');
  section.hidden=!plots.length;
  if(!plots.length){
    select.innerHTML='';
    preview.innerHTML='';
    open.removeAttribute('href');
    return;
  }
  const current=select.value&&plots.some(([key])=>key===select.value)?select.value:plots[0][0];
  select.innerHTML=plots.map(([key])=>`<option value="${escapeHtml(key)}">${escapeHtml(matplotlibLabels[key]?.label||key)}</option>`).join('');
  select.value=current;
  const update=()=>{
    const [key,url]=plots.find(([candidate])=>candidate===select.value)||plots[0];
    const label=matplotlibLabels[key]?.label||key,unit=matplotlibLabels[key]?.unit||'Y axis follows selected metric';
    // Matplotlib PNG 是已保存 CSV 的離線報告預覽；切換圖片不會重新量測或呼叫 RF endpoint。
    preview.innerHTML=`<a class="matplotlib-active-plot" href="${url}" target="_blank" rel="noopener"><img src="${url}" alt="${escapeHtml(label)} Matplotlib chart"><span>${escapeHtml(label)} · ${escapeHtml(unit)}</span></a>`;
    open.href=url;
  };
  select.onchange=update;
  update();
}
function expectedReferenceForPowerMetric(points,axis,metricName){
  if(metricName==='power_error_db')return {kind:'horizontal',value:0,label:'Expected error 0 dB'};
  if(metricName!=='burst_power_dbm')return null;
  if(axis==='power'){
    const linePoints=points.filter(point=>point.valid&&Number.isFinite(point.generator_power_dbm)).map(point=>({x:point.generator_power_dbm,y:point.generator_power_dbm}));
    // Power sweep 的線性比較基準是 Pexpected = Pgenerator；不能用 Analyzer ENPower 畫成水平線。
    return linePoints.length?{kind:'diagonal',points:linePoints,label:'Expected = Generator Power'}:null;
  }
  const expectedValues=points.map(point=>point.expected_power_dbm).filter(Number.isFinite);
  const reference=expectedValues.length?expectedValues.reduce((sum,value)=>sum+value,0)/expectedValues.length:null;
  return reference===null?null:{kind:'horizontal',value:reference,label:`Expected ${reference.toFixed(2)} dBm`};
}
const chartFrame={width:900,height:390,left:104,right:42,top:38,bottom:82};
const chartZoomLimits={minWidth:18};
function clampChartX(x,width=chartView.width){
  // 縮小最多回到完整圖，避免 viewBox 大於圖面後把曲線縮到像消失。
  if(width>=chartFrame.width)return 0;
  return Math.max(0,Math.min(chartFrame.width-width,x));
}
function syncChartViewportSize(){
  const svg=$('#chart');
  chartView.x=clampChartX(chartView.x,chartView.width);
  svg.setAttribute('viewBox',`${chartView.x} ${chartView.y} ${chartView.width} ${chartView.height}`);
  svg.style.aspectRatio=`${chartFrame.width} / ${chartFrame.height}`;
}
function setChartNaturalView(points=[]){
  // 圖表尺寸集中由 chartFrame 管理，避免 SVG viewBox 與互動縮放範圍不同步。
  Object.assign(chartView,{x:0,y:0,width:chartFrame.width,height:chartFrame.height});
  syncChartViewportSize();
}
function axisTickLabel(axis,value){return axis==='frequency'?(value/1e6).toLocaleString(undefined,{maximumFractionDigits:3}):Number(value).toFixed(1)}
function chartExtent(values,{minimumSpan=1,paddingRatio=.08}={}){
  const finite=values.filter(Number.isFinite),low=Math.min(...finite),high=Math.max(...finite);
  const midpoint=(low+high)/2,rawSpan=high-low,span=Math.max(rawSpan,minimumSpan);
  // Y 軸只加必要留白，讓小幅變化不會被壓扁；零跨度資料仍保留最小可讀範圍。
  return {min:midpoint-span/2-span*paddingRatio,max:midpoint+span/2+span*paddingRatio};
}
function chartAxisMarkup(axis,metric,xmin,xmax,ymin,ymax,x,y){
  const frame=chartFrame,xTicks=xmin===xmax?1:6,yTicks=6;
  let html='';
  for(let index=0;index<yTicks;index++){
    const value=ymax-index*(ymax-ymin)/(yTicks-1),yy=y(value);
    html+=`<line class="grid-line" x1="${frame.left}" y1="${yy}" x2="${frame.width-frame.right}" y2="${yy}"/><text class="axis-label" x="${frame.left-12}" y="${yy+4}" text-anchor="end">${value.toLocaleString(undefined,{maximumFractionDigits:3})}</text>`;
  }
  for(let index=0;index<xTicks;index++){
    const value=xTicks===1?xmin:xmin+index*(xmax-xmin)/(xTicks-1),xx=x(value);
    const anchor=index===0?'start':index===xTicks-1?'end':'middle';
    html+=`<line class="grid-line x-grid" x1="${xx}" y1="${frame.top}" x2="${xx}" y2="${frame.height-frame.bottom}"/><text class="axis-label" x="${xx}" y="${frame.height-frame.bottom+26}" text-anchor="${anchor}">${axisTickLabel(axis,value)}</text>`;
  }
  // 軸標題與刻度保留獨立邊界，避免先前標題和端點數字疊在同一列。
  const xTitle=axis==='power'?'Generator Power':'Frequency',xUnit=xUnitFor(axis);
  html+=`<text class="axis-title" x="${frame.left+(frame.width-frame.left-frame.right)/2}" y="${frame.height-12}" text-anchor="middle">${xTitle} (${xUnit})</text>`;
  html+=`<text class="axis-title" x="24" y="${frame.top+(frame.height-frame.top-frame.bottom)/2}" text-anchor="middle" transform="rotate(-90 24 ${frame.top+(frame.height-frame.top-frame.bottom)/2})">${metricAxisLabel(metric)}</text>`;
  return html;
}
function drawChart(points,axis='frequency'){
  const svg=$('#chart'),metric=$('#chartMetric').value,w=chartFrame.width,h=chartFrame.height,xField=xFieldFor(axis),xUnit=xUnitFor(axis),left=chartFrame.left,right=chartFrame.right,top=chartFrame.top,bottom=chartFrame.bottom;
  const xs=points.map(point=>point[xField]).filter(Number.isFinite);
  const validPoints=points.filter(point=>point.valid&&Number.isFinite(point[metric]));
  const ys=validPoints.map(point=>point[metric]);
  if(!xs.length||!ys.length){svg.innerHTML='<text class="axis-label" x="450" y="150" text-anchor="middle">No valid numeric data</text>';return}
  // EVM 圖需要把 spec limit 一起納入 Y 範圍，否則 limit line 會被裁切在圖外。
  const specLimit=metric==='evm_all_db'&&Number.isFinite(latestSpecLimitDb)?latestSpecLimitDb:null;
  const expectedReference=expectedReferenceForPowerMetric(validPoints,axis,metric);
  const expectedSpread=expectedReference?.kind==='diagonal'?expectedReference.points.map(point=>point.y):expectedReference?[expectedReference.value]:[];
  const spread=[...ys,...(specLimit===null?[]:[specLimit]),...expectedSpread];
  const xmin=Math.min(...xs),xmax=Math.max(...xs),metricSpan=Math.max(...spread)-Math.min(...spread);
  const minimumSpan=metric==='burst_power_dbm'||metric==='power_error_db'?0.18:metric==='frequency_error_hz'?Math.max(metricSpan,.5):0.5;
  const yExtent=chartExtent(spread,{minimumSpan,paddingRatio:.1}),ymin=yExtent.min,ymax=yExtent.max;
  const x=value=>left+(value-xmin)/(xmax-xmin||1)*(w-left-right),y=value=>h-bottom-(value-ymin)/(ymax-ymin||1)*(h-top-bottom);
  let html=chartAxisMarkup(axis,metric,xmin,xmax,ymin,ymax,x,y);
  if(specLimit!==null){
    // EVM dB 越負越好，因此 PASS 區在 limit line 下方；以陰影標示避免誤讀。
    const yLimit=y(specLimit);
    html+=`<rect class="spec-pass-zone" x="${left}" y="${yLimit}" width="${w-left-right}" height="${Math.max(0,h-bottom-yLimit)}"/>`;
    html+=`<line class="spec-limit-line" x1="${left}" y1="${yLimit}" x2="${w-right}" y2="${yLimit}"/>`;
    html+=`<text class="spec-limit-label" x="${w-right-4}" y="${yLimit-6}" text-anchor="end">Limit ${specLimit.toFixed(2)} dB</text>`;
  }
  if(expectedReference){
    if(expectedReference.kind==='diagonal'){
      html+=`<polyline class="expected-power-line" fill="none" points="${expectedReference.points.map(point=>`${x(point.x)},${y(point.y)}`).join(' ')}"/>`;
      const last=expectedReference.points.at(-1);
      html+=`<text class="expected-power-label" x="${x(last.x)-4}" y="${y(last.y)-7}" text-anchor="end">${expectedReference.label}</text>`;
    }else{
      // Power Error 圖以 0 dB 為基準；頻率掃描的 Burst Power 則使用固定 Expected power。
      const yExpected=y(expectedReference.value);
      html+=`<line class="expected-power-line" x1="${left}" y1="${yExpected}" x2="${w-right}" y2="${yExpected}"/>`;
      html+=`<text class="expected-power-label" x="${w-right-4}" y="${yExpected-7}" text-anchor="end">${expectedReference.label}</text>`;
    }
  }
  // 無效點不得跨越連線：先依 valid 與數值完整性切成獨立線段。
  const segments=[];let segment=[];
  points.forEach(point=>{if(point.valid&&Number.isFinite(point[metric])){segment.push(point)}else{if(segment.length)segments.push(segment);segment=[]}});
  if(segment.length)segments.push(segment);
  html+=segments.map(values=>`<polyline class="plot-line" points="${values.map(point=>`${x(point[xField])},${y(point[metric])}`).join(' ')}"/>`).join('');
  html+=validPoints.map(point=>{const tip=`x=${xDisplayFor(axis,point[xField])} ${xUnit} | ${metric}=${point[metric].toFixed(3)} | Pin=${formatMeasured(point.pin_dbm)} dBm | Pout=${formatMeasured(point.pout_dbm)} dBm | Gain=${formatMeasured(point.gain_db)} dB | EVM=${formatMeasured(point.evm_all_db)} dB | Power=${formatMeasured(point.burst_power_dbm)} dBm | Error=${formatMeasured(point.power_error_db,3)} dB | FreqErr=${formatMeasured(point.frequency_error_hz)} Hz | ${point.limit_status}`;return `<circle class="plot-dot" data-chart-point="true" data-tooltip="${escapeHtml(tip)}" cx="${x(point[xField])}" cy="${y(point[metric])}" r="4"><title>${escapeHtml(tip)}</title></circle>`}).join('');
  // 無效點固定畫在圖底並標示叉號，保留其頻率／功率位置且不偽造 Y 值。
  html+=points.filter(point=>!point.valid||!Number.isFinite(point[metric])).map(point=>`<g class="plot-invalid" transform="translate(${x(point[xField])},${h-bottom})"><path d="M-5-5L5 5M5-5L-5 5"/><title>${xDisplayFor(axis,point[xField])} ${xUnit} · INVALID</title></g>`).join('');
  svg.innerHTML=html;
  setChartNaturalView(validPoints);
}
function drawAnalysisChart(){
  const visible=analysisTraces.filter(trace=>trace.visible);
  if(!visible.length){$('#chart').innerHTML='';return}
  const metricName=$('#chartMetric').value,w=chartFrame.width,h=chartFrame.height,left=chartFrame.left,right=chartFrame.right,top=chartFrame.top,bottom=chartFrame.bottom,samples=[];
  visible.forEach(trace=>trace.points.forEach(point=>{const xValue=point[xFieldFor(trace.axis)],yValue=point[metricName];if(xValue!==null&&Number.isFinite(yValue))samples.push({x:xValue,y:yValue})}));
  if(!samples.length){$('#chart').innerHTML=`<text class="axis-label" x="45" y="70">${language==='zh'?'此指標沒有可比較的有效數值':'No comparable values for this metric'}</text>`;return}
  const referenceLines=visible.map(trace=>({trace,reference:expectedReferenceForPowerMetric(trace.points.filter(point=>point.valid),trace.axis,metricName)})).filter(item=>item.reference);
  const referenceSpread=referenceLines.flatMap(item=>item.reference.kind==='diagonal'?item.reference.points.map(point=>point.y):[item.reference.value]);
  const xmin=Math.min(...samples.map(sample=>sample.x)),xmax=Math.max(...samples.map(sample=>sample.x)),spread=[...samples.map(sample=>sample.y),...referenceSpread],metricSpan=Math.max(...spread)-Math.min(...spread);
  const minimumSpan=metricName==='burst_power_dbm'||metricName==='power_error_db'?0.18:metricName==='frequency_error_hz'?Math.max(metricSpan,.5):0.5;
  const yExtent=chartExtent(spread,{minimumSpan,paddingRatio:.1}),ymin=yExtent.min,ymax=yExtent.max,x=value=>left+(value-xmin)/(xmax-xmin||1)*(w-left-right),y=value=>h-bottom-(value-ymin)/(ymax-ymin||1)*(h-top-bottom);
  const axes=new Set(visible.map(trace=>trace.axis)),comparisonAxis=axes.size===1?visible[0].axis:'frequency';
  let html=chartAxisMarkup(comparisonAxis,metricName,xmin,xmax,ymin,ymax,x,y);
  referenceLines.forEach(({reference})=>{
    if(reference.kind==='diagonal'){
      html+=`<polyline class="expected-power-line" fill="none" points="${reference.points.map(point=>`${x(point.x)},${y(point.y)}`).join(' ')}"/>`;
      const last=reference.points.at(-1);
      html+=`<text class="expected-power-label" x="${x(last.x)-4}" y="${y(last.y)-7}" text-anchor="end">${reference.label}</text>`;
    }else{
      const yReference=y(reference.value);
      html+=`<line class="expected-power-line" x1="${left}" y1="${yReference}" x2="${w-right}" y2="${yReference}"/>`;
      html+=`<text class="expected-power-label" x="${w-right-4}" y="${yReference-7}" text-anchor="end">${reference.label}</text>`;
    }
  });
  visible.forEach(trace=>{const xField=xFieldFor(trace.axis),dash=trace.lineStyle==='dash'?'10 7':trace.lineStyle==='dot'?'2 6':'none';let segment=[];const flush=()=>{if(segment.length){html+=`<polyline fill="none" stroke="${trace.color}" stroke-width="3" stroke-dasharray="${dash}" stroke-linecap="round" points="${segment.map(point=>`${x(point[xField])},${y(point[metricName])}`).join(' ')}"/>`;segment=[]}};trace.points.forEach(point=>{const valid=point.valid&&point[xField]!==null&&Number.isFinite(point[metricName]);if(valid)segment.push(point);else flush()});flush();trace.points.forEach(point=>{if(point[xField]===null||!Number.isFinite(point[metricName]))return;const cx=x(point[xField]),cy=y(point[metricName]),fill=point.valid?trace.color:'#f05261',title=`${trace.name} | x=${point[xField]} | ${metricName}=${point[metricName]} | EVM=${point.evm_all_db} dB | Power=${point.burst_power_dbm} dBm | FreqErr=${point.frequency_error_hz} Hz | ${point.valid?'VALID':'INVALID'}`,shape=trace.pointShape==='square'?`<rect x="${cx-4}" y="${cy-4}" width="8" height="8" rx="1"`:trace.pointShape==='diamond'?`<polygon points="${cx},${cy-5} ${cx+5},${cy} ${cx},${cy+5} ${cx-5},${cy}"`:`<circle cx="${cx}" cy="${cy}" r="4"`;html+=`${shape} data-chart-point="true" data-tooltip="${escapeHtml(title)}" fill="${fill}" stroke="${trace.color}"><title>${escapeHtml(title)}</title></${trace.pointShape==='square'?'rect':trace.pointShape==='diamond'?'polygon':'circle'}>`})});
  $('#chart').innerHTML=html;
  setChartNaturalView(samples);
}
$('#chartMetric').onchange=()=>{analysisTraces.length?drawAnalysisChart():(latest.length&&drawChart(latest,latestAxis))};
function downloadBlob(filename,blob){const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=filename;link.click();setTimeout(()=>URL.revokeObjectURL(url),0)}
$('#exportSvg').onclick=()=>{const svg=$('#chart').cloneNode(true);svg.setAttribute('xmlns','http://www.w3.org/2000/svg');downloadBlob('cmp180-comparison.svg',new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml'}))};
$('#exportPng').onclick=()=>{const svg=$('#chart').cloneNode(true);svg.setAttribute('xmlns','http://www.w3.org/2000/svg');const blob=new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml'}),url=URL.createObjectURL(blob),image=new Image();image.onload=()=>{const canvas=document.createElement('canvas');canvas.width=1800;canvas.height=600;const context=canvas.getContext('2d');context.fillStyle=getComputedStyle(document.documentElement).getPropertyValue('--console-surface')||'#fff';context.fillRect(0,0,canvas.width,canvas.height);context.drawImage(image,0,0,canvas.width,canvas.height);canvas.toBlob(png=>{if(png)downloadBlob('cmp180-comparison.png',png)},'image/png');URL.revokeObjectURL(url)};image.src=url};
$('#exportCompareCsv').onclick=()=>{const metricName=$('#chartMetric').value,rows=[['trace','valid','frequency_hz','generator_power_dbm',metricName,'measurement_state']];analysisTraces.forEach(trace=>trace.points.forEach(point=>rows.push([trace.name,point.valid,point.frequency_hz,point.generator_power_dbm,point[metricName],point.measurement_state])));const csv=rows.map(row=>row.map(value=>`"${String(value??'').replaceAll('"','""')}"`).join(',')).join('\r\n');downloadBlob('cmp180-comparison.csv',new Blob([csv],{type:'text/csv;charset=utf-8'}))};
const chartTooltip=document.createElement('div');chartTooltip.className='chart-hover-tooltip';chartTooltip.hidden=true;document.querySelector('.chart-card').append(chartTooltip);
function chartPointCenter(point){
  if(point.tagName.toLowerCase()==='circle')return {x:Number(point.getAttribute('cx')),y:Number(point.getAttribute('cy'))};
  const box=point.getBBox();
  return {x:box.x+box.width/2,y:box.y+box.height/2};
}
function clearHoverPoint(){
  chartTooltip.hidden=true;
  if(chartView.cursors.length)renderChartCursors();else $('#chartCursorReadout').hidden=true;
  $('#chart').querySelectorAll('.chart-crosshair,.chart-focus-ring').forEach(item=>item.remove());
}
$('#chart').addEventListener('pointermove',event=>{const svg=$('#chart'),points=[...svg.querySelectorAll('[data-chart-point]')];if(!points.length||chartView.drag)return;let nearest=null,distance=Infinity;points.forEach(point=>{const box=point.getBoundingClientRect(),dx=event.clientX-(box.left+box.width/2),dy=event.clientY-(box.top+box.height/2),candidate=Math.hypot(dx,dy);if(candidate<distance){distance=candidate;nearest=point}});svg.querySelectorAll('.chart-crosshair,.chart-focus-ring').forEach(item=>item.remove());if(!nearest||distance>64){clearHoverPoint();return}const ns='http://www.w3.org/2000/svg',center=chartPointCenter(nearest),vertical=document.createElementNS(ns,'line'),horizontal=document.createElementNS(ns,'line'),ring=document.createElementNS(ns,'circle');vertical.setAttribute('class','chart-crosshair');vertical.setAttribute('x1',center.x);vertical.setAttribute('x2',center.x);vertical.setAttribute('y1',chartFrame.top);vertical.setAttribute('y2',chartFrame.height-chartFrame.bottom);horizontal.setAttribute('class','chart-crosshair');horizontal.setAttribute('x1',chartFrame.left);horizontal.setAttribute('x2',chartFrame.width-chartFrame.right);horizontal.setAttribute('y1',center.y);horizontal.setAttribute('y2',center.y);ring.setAttribute('class','chart-focus-ring');ring.setAttribute('cx',center.x);ring.setAttribute('cy',center.y);ring.setAttribute('r','9');svg.append(vertical,horizontal,ring);const readout=$('#chartCursorReadout'),pointText=nearest.dataset.tooltip||'';readout.hidden=false;readout.textContent=pointText;chartTooltip.innerHTML=`<strong>${language==='zh'?'量測點數值':'Measurement values'}</strong>${escapeHtml(pointText).replaceAll(' | ','<br>')}`;const card=document.querySelector('.chart-card').getBoundingClientRect(),tooltipWidth=Math.min(460,card.width-24);chartTooltip.style.maxWidth=`${tooltipWidth}px`;chartTooltip.style.left=`${Math.max(8,Math.min(event.clientX-card.left,card.width-tooltipWidth-24))}px`;chartTooltip.style.top='104px';chartTooltip.hidden=false});
$('#chart').addEventListener('pointerleave',clearHoverPoint);

// 架構節點只切換說明，不呼叫任何儀器 API，也不會改變 RF 狀態。
const architectureCopy={
  plan:'先建立量測條件；此步驟只定義計畫，不會送出 RF。',
  safety:'伺服器會再次檢查接線、操作員在場、安全 Profile、頻率、功率與頻寬。',
  instrument:'通過最後確認後才建立 SCPI session；任何錯誤、取消或逾時都會執行 STOP／ABORT 與 RF Off。',
  result:'保存 raw response，再正規化 EVM、功率與誤差；INVALID 點不與有效資料連線。',
  artifact:'每次 Run 保留 CSV、JSON、HTML 與 Metadata，供搜尋、追溯及跨 Run 比較。'
};
document.querySelectorAll('[data-architecture]').forEach(node=>node.addEventListener('click',()=>{document.querySelectorAll('[data-architecture]').forEach(item=>item.classList.toggle('active',item===node));$('#architectureDetail').textContent=architectureCopy[node.dataset.architecture]}));

// 首頁 iframe 僅載入 server 白名單內的兩份文件；播放與切換不會呼叫任何量測 API。
let activeDiagramPath='/diagrams/system-architecture.html';
function diagramPlaybackUrl(path){return `${path}?present=1&theme=${document.documentElement.dataset.theme==='light'?'light':'dark'}`}
document.querySelectorAll('[data-diagram-path]').forEach(button=>button.addEventListener('click',()=>{activeDiagramPath=button.dataset.diagramPath;document.querySelectorAll('[data-diagram-path]').forEach(item=>item.classList.toggle('active',item===button));$('#diagramShowcaseFrame').src=diagramPlaybackUrl(activeDiagramPath)}));
$('#restartDiagram').addEventListener('click',()=>{$('#diagramShowcaseFrame').src=diagramPlaybackUrl(activeDiagramPath)});
$('#openDiagram').addEventListener('click',()=>window.open(diagramPlaybackUrl(activeDiagramPath),'_blank','noopener'));

// 圖表檢視狀態只影響瀏覽器顯示；不重新量測，也不修改原始結果。
const chartView={x:0,y:0,width:chartFrame.width,height:chartFrame.height,drag:null,cursors:[]};
function applyChartView(){syncChartViewportSize()}
function resetChartView(){Object.assign(chartView,{x:0,y:0,width:chartFrame.width,height:chartFrame.height,drag:null,cursors:[]});applyChartView();$('#chartCursorReadout').hidden=true;$('#chart').querySelectorAll('.chart-ab-line,.chart-ab-label').forEach(item=>item.remove())}
function renderChartCursors(){const svg=$('#chart');svg.querySelectorAll('.chart-ab-line,.chart-ab-label').forEach(item=>item.remove());chartView.cursors.forEach((cursor,index)=>{const ns='http://www.w3.org/2000/svg',line=document.createElementNS(ns,'line'),label=document.createElementNS(ns,'text');line.setAttribute('class','chart-ab-line');line.setAttribute('x1',cursor.x);line.setAttribute('x2',cursor.x);line.setAttribute('y1',chartFrame.top);line.setAttribute('y2',chartFrame.height-chartFrame.bottom);label.setAttribute('class','chart-ab-label');label.setAttribute('x',cursor.x+5);label.setAttribute('y',chartFrame.top-5);label.textContent=index?'B':'A';svg.append(line,label)});const readout=$('#chartCursorReadout');if(chartView.cursors.length){readout.hidden=false;readout.textContent=chartView.cursors.map((cursor,index)=>`${index?'B':'A'}: ${cursor.label}`).join('  |  ')+(chartView.cursors.length===2?`  |  ΔX(view): ${Math.abs(chartView.cursors[1].x-chartView.cursors[0].x).toFixed(1)}`:'')}else readout.hidden=true}
$('#chartReset').onclick=resetChartView;
$('#chartCursorMode').onclick=event=>{event.currentTarget.classList.toggle('active');toast(event.currentTarget.classList.contains('active')?'A/B 游標已啟用：點選圖上測點':'A/B 游標已關閉')};
$('#chart').addEventListener('wheel',event=>{event.preventDefault();const factor=event.deltaY<0?.72:1.38,rect=event.currentTarget.getBoundingClientRect(),px=chartView.x+(event.clientX-rect.left)/rect.width*chartView.width,nextWidth=Math.min(chartFrame.width,Math.max(chartZoomLimits.minWidth,chartView.width*factor));chartView.x=clampChartX(px-(px-chartView.x)*nextWidth/chartView.width,nextWidth);chartView.y=0;chartView.width=nextWidth;chartView.height=chartFrame.height;applyChartView()},{passive:false});
$('#chart').addEventListener('pointerdown',event=>{if($('#chartCursorMode').classList.contains('active')){const point=event.target.closest('[data-chart-point]');if(point){const rect=$('#chart').getBoundingClientRect(),box=point.getBoundingClientRect(),x=chartView.x+((box.left+box.width/2)-rect.left)/rect.width*chartView.width;chartView.cursors.push({x,label:point.dataset.tooltip});if(chartView.cursors.length>2)chartView.cursors.shift();renderChartCursors()}return}chartView.drag={clientX:event.clientX,clientY:event.clientY,x:chartView.x,y:chartView.y};event.currentTarget.setPointerCapture(event.pointerId);document.querySelector('.chart-card').classList.add('is-panning')});
$('#chart').addEventListener('pointermove',event=>{if(!chartView.drag)return;const rect=event.currentTarget.getBoundingClientRect(),nextX=chartView.drag.x-(event.clientX-chartView.drag.clientX)/rect.width*chartView.width;chartView.x=clampChartX(nextX);chartView.y=0;applyChartView()});
$('#chart').addEventListener('pointerup',()=>{chartView.drag=null;document.querySelector('.chart-card').classList.remove('is-panning')});
const sunIcon='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>';
const moonIcon='<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.7 15.3A8.7 8.7 0 0 1 9.7 4.3a.6.6 0 0 0-.75-.8A10 10 0 1 0 21.5 16a.6.6 0 0 0-.8-.7z"/></svg>';
let theme=localStorage.getItem('cmp180-theme')||'dark';
function applyTheme(){document.documentElement.dataset.theme=theme;const button=$('#themeButton');button.innerHTML=theme==='dark'?sunIcon:moonIcon;const label=theme==='dark'?'Switch to light theme':'Switch to dark theme';button.title=label;button.setAttribute('aria-label',label)}
$('#themeButton').onclick=()=>{theme=theme==='dark'?'light':'dark';localStorage.setItem('cmp180-theme',theme);applyTheme()};
applyTheme();
applyLanguage();
// 預先讀取紀錄，切換到紀錄頁時可立即顯示；這是唯讀 API，不會啟動量測或 RF。
function formatMHz(value){return Number.isFinite(Number(value))?`${Number(value)/1e6} MHz`:'—'}
function formatGHzRange(layer){return layer?`${Number(layer.frequency_min_hz)/1e9}–${Number(layer.frequency_max_hz)/1e9} GHz`:'—'}
fetch('/api/capabilities').then(response=>response.json()).then(profile=>{const catalog=profile.catalog,installed=profile.installed,approved=profile.approved_profile,hil=profile.verified_hil,approvedSections=approved.sections.map(section=>section.key),rows=[['RF frequency',formatGHzRange(catalog),formatGHzRange(installed),formatGHzRange(approved),hil.frequencies_hz.map(formatMHz).join(', ')],['Analysis bandwidth',`≤ ${formatMHz(catalog.maximum_analysis_bandwidth_hz)}`,installed.analysis_bandwidths_hz.map(formatMHz).join(', '),approved.bandwidths_hz.map(formatMHz).join(', '),hil.bandwidths_hz.map(formatMHz).join(', ')],['WLAN sections','2.4 / 5 / 6 GHz','2.4 / 5 / 6 GHz waveform pool',approvedSections.join(', '),hil.sections.join(', ')],['RF resources',`${catalog.generator_count} VSG / ${catalog.analyzer_count} VSA / ${catalog.rf_port_count} ports`,`${installed.generator_count} VSG / ${installed.analyzer_count} VSA / ${installed.rf_ports.length} ports`,approved.routes.join(', '),hil.routes.join(', ')],['Generator power','Depends on port/options/path','Confirm from installed option and port',`${approved.generator_power_min_dbm}–${approved.generator_power_max_dbm} dBm`,hil.generator_powers_dbm.join(', ')+' dBm'],['Sweep control',catalog.supports_list_mode?'List mode supported':'—','Installed capability pending discovery',`≤ ${approved.maximum_points} points; ${approved.dwell_min_ms}–${approved.dwell_max_ms} ms`,`${hil.dwell_ms.join(', ')} ms`]];$('#capabilityRows').innerHTML=rows.map(row=>`<tr>${row.map(value=>`<td>${escapeHtml(value)}</td>`).join('')}</tr>`).join('');$('#capabilityGate').textContent=language==='zh'?`RF 執行來源：${approved.profile_id}；已核准 ${approvedSections.length} 個完成 HIL 的 WLAN 區段。`:`RF execution source: ${approved.profile_id}. ${approvedSections.length} HIL-complete WLAN sections are approved.`}).catch(error=>{$('#capabilityRows').innerHTML=`<tr><td colspan="5">${escapeHtml(error.message)}</td></tr>`});
loadRunHistory();
document.querySelectorAll('[data-copy-target]').forEach(button=>button.addEventListener('click',async()=>{const target=document.getElementById(button.dataset.copyTarget);try{await navigator.clipboard.writeText(target.innerText.replaceAll('PS ','').trim());toast(language==='zh'?'指令已複製':'Command copied')}catch(error){toast(language==='zh'?'無法複製，請手動選取指令':'Copy failed; select the command manually','error')}}));
