const translations={zh:{subtitle:'WLAN TX EVM 自動化量測',mockBadge:'DEMO',workspaceTitle:'量測工作區',controlState:'控制狀態',demoControlState:'僅使用示範資料',demoControlHint:'CMP180 RF 控制未啟用',singleTab:'單點量測',sweepTab:'頻率掃描',resultsTab:'結果與圖表',historyTab:'量測紀錄',historyTitle:'量測紀錄',historyHelp:'瀏覽本機保存的實機與示範結果；不會啟動量測或 RF。',refreshHistory:'重新整理',historyEmpty:'尚無可用紀錄。',historyTime:'時間',historyName:'名稱',historySource:'來源',historyStatus:'狀態',historyPoints:'點數',historyFiles:'檔案',singleTitle:'示範單點量測',singleHelp:'輸入一個測試點，驗證資料保存與圖表流程。',frequency:'中心頻率',bandwidth:'頻寬',power:'Generator 功率',testName:'測試名稱',runSingle:'執行示範單點',sweepTitle:'示範頻率掃描',sweepHelp:'依起點、終點與步進建立頻點，示範資料不送 RF。',start:'起始頻率',stop:'結束頻率',step:'步進',dwell:'停留時間',runSweep:'執行示範掃描',resultTitle:'量測結果',empty:'尚未執行量測。',resultChart:'結果趨勢圖',dwellHelp:'每個頻點之間的等待時間，範圍 100–2000 ms。',sweepPowerHelp:'示範資料不套用實機功率安全限制。',powerSweepTab:'功率掃描',powerSweepTitle:'示範功率掃描',powerSweepHelp:'固定頻率，建立可示範 Gain compression 與 P1dB 的功率點。',startPower:'起始功率',stopPower:'結束功率',stepPower:'步進',runPowerSweep:'執行示範功率掃描',singlePowerHelp:'示範資料不送 RF，可自由輸入功率觀察圖表。'},en:{subtitle:'WLAN TX EVM Automation',mockBadge:'DEMO',workspaceTitle:'Measurement Workspace',controlState:'Control state',demoControlState:'Demo data only',demoControlHint:'CMP180 RF control disabled',singleTab:'Single',sweepTab:'Frequency Sweep',resultsTab:'Results & Plots',historyTab:'Run History',historyTitle:'Run History',historyHelp:'Browse saved hardware and demo results without starting a measurement or RF.',refreshHistory:'Refresh',historyEmpty:'No saved runs found.',historyTime:'Time',historyName:'Name',historySource:'Source',historyStatus:'Status',historyPoints:'Points',historyFiles:'Files',singleTitle:'Demo single measurement',singleHelp:'Enter one point to validate artifact and plotting workflows.',frequency:'Center frequency',bandwidth:'Bandwidth',power:'Generator power',testName:'Test name',runSingle:'Run demo single',sweepTitle:'Demo frequency sweep',sweepHelp:'Build points from start, stop, and step; demo data transmits no RF.',start:'Start frequency',stop:'Stop frequency',step:'Step',dwell:'Dwell time',runSweep:'Run demo sweep',resultTitle:'Measurement results',empty:'No measurement has been run.',resultChart:'Result trends',dwellHelp:'Wait time between frequency points, 100–2000 ms.',sweepPowerHelp:'Demo data does not apply hardware power safety limits.',powerSweepTab:'Power Sweep',powerSweepTitle:'Demo power sweep',powerSweepHelp:'Fixed frequency; build points that demonstrate gain compression and P1dB.',startPower:'Start power',stopPower:'Stop power',stepPower:'Step',runPowerSweep:'Run demo power sweep',singlePowerHelp:'Demo data transmits no RF; enter any power to explore charts.'}};
// 導覽名稱明確區分 Demo 與實機，避免相同量測類型看起來像重複功能。
translations.zh.singleTab='示範單點';translations.zh.sweepTab='示範頻掃';translations.zh.powerSweepTab='示範功掃';
translations.en.singleTab='Demo Single';translations.en.sweepTab='Demo Freq Sweep';translations.en.powerSweepTab='Demo Power Sweep';
Object.assign(translations.zh,{demoAdvancedMode:'進階 PA 指標',advancedPaTitle:'進階 PA 指標示範',advancedPaHelp:'以固定教學模型示範 OIP3、Harmonics、ACP 與 ACLR；不連線儀器或送出 RF。',advancedInputPower:'PA 輸入功率 Pin',advancedPowerHelp:'Demo 不套用實機功率安全限制。',toneSpacing:'雙音間距',channelBandwidth:'通道頻寬',runAdvancedPa:'產生進階 PA Demo'});
Object.assign(translations.en,{demoAdvancedMode:'Advanced PA',advancedPaTitle:'Advanced PA Metrics Demo',advancedPaHelp:'Use a deterministic training model to demonstrate OIP3, harmonics, ACP, and ACLR without instrument control or RF.',advancedInputPower:'PA input power Pin',advancedPowerHelp:'Demo data does not apply hardware power safety limits.',toneSpacing:'Tone spacing',channelBandwidth:'Channel bandwidth',runAdvancedPa:'Generate Advanced PA Demo'});
translations.zh.campaignTab='HIL 批次';translations.en.campaignTab='HIL Campaign';
Object.assign(translations.zh,{homeTab:'首頁',measurementTab:'量測',calibrationTab:'校正',guideTab:'說明',guideTitle:'快速操作',guideIntro:'啟動服務、執行量測、查看結果。',guideSafeTitle:'Demo 模式',guideSafeText:'不發送 RF',guideStep1:'啟動',guideStep2:'量測',guideStep3:'結果',guideStep4:'報告',demoCommandTitle:'啟動 Demo',demoCommandHelp:'不連線 CMP180、不送 SCPI。',copyCommand:'複製',openBrowser:'網址',configCommandTitle:'檢查設定',configCommandHelp:'驗證 YAML 與安全設定。',expectedOutput:'預期結果',connectionCommandTitle:'連線檢查',connectionCommandHelp:'讀取 IDN、Options 與 Error Queue。',powerWarning:'注意',queryOnlyAdvice:'此動作不啟動量測或 RF。',hardwareCommandTitle:'啟動實機服務',hardwareCommandHelp:'啟動後仍需在量測頁完成安全確認。',hardwareHold:'未通過安全確認時不會送出 RF。',whereResultsTitle:'輸出位置',whereResultsText:'output\\<timestamp>_<run>\\',whenStopTitle:'停止條件',whenStopText:'INV、逾時、SCPI Error、接線異動或 RF 狀態不明。'});
Object.assign(translations.zh,{guideInstallTitle:'第一次安裝',guideCliTitle:'CLI：檢查連線與設定',guideDataTitle:'取得與分析資料',guideDataHelp:'也可在「量測紀錄」開啟詳情，再到「結果與圖表」比較 2–8 筆 Run。'});
Object.assign(translations.en,{guideInstallTitle:'First-time installation',guideCliTitle:'CLI: connection and configuration',guideDataTitle:'Get and analyze data',guideDataHelp:'You can also open details in Runs, then compare 2–8 runs in Results & Analysis.'});
Object.assign(translations.zh,{
  hardwareSource:'實機量測',demoSource:'示範與訓練',hardwareSop1:'設定數值',hardwareSop2:'檢查接線與人在場',hardwareSop3:'檢查計畫',hardwareSop4:'執行並保存 artifacts',
  measurementSettings:'設定數值',measurementSettingsHelp:'先選擇量測類型並填好頻率、功率、頻寬與點數。',singleSetup:'單點設定',singleSetupHelp:'輸入中心頻率、WLAN 頻寬與 Generator 功率。Web 會先檢查 approved profile，通過且完成最後確認後才控制 CMP180。',reviewSingle:'檢查單點計畫',sweepSetup:'掃描設定',sweepSetupHelp:'設定 WLAN EVM 掃描軸、範圍、步進與停留時間；送出前會顯示點位、預估時間與安全檢查結果。',reviewPlan:'檢查量測計畫',reviewGprf:'檢查 GPRF 計畫',safetyCheck:'檢查接線與現場狀態',safetyCheckHelp:'目前只核准 RF1.1 → RF1.5。確認直接線路沒有額外衰減器，且操作員在機台旁。',safetyCheckHelpGprf:'目前只核准 RF1.1 → RF1.5。確認線材、衰減器與轉接件都已登錄於計畫，且操作員在機台旁。',directCableConfirm:'我已確認目前為核准的直接線路，沒有未登錄的衰減器或轉接件',directCableCheck:'直接線路／無未登錄衰減器',executeHardware:'執行實機量測',executeHardwareHelp:'按下後仍會顯示最後確認；取消不會送 RF，完成後保存 artifacts。',
  loopbackTitle:'Loopback RF 效能驗證',loopbackHelp:'固定條件下執行獨立 SingleShot repeats；先驗證 Tester／Cable／UD Box／RF path，不代表 DUT PASS。',loopbackWarning:'穩定不等於合理',loopbackWarningHelp:'Stability 評估重複性；Reasonableness 比較 Analyzer input reference plane 的 Expected RX Power。相同代表點、門檻且至少 Repeat 10 使用 approved baseline；其他條件仍為 draft。',loopbackCableConfirm:'接線、Cable／UD Box path 與衰減條件已確認且本次不變',loopbackOperatorConfirm:'操作員在 CMP180 旁，可處理 RF 異常',runLoopback:'檢查並執行 Loopback',runAllLoopbacks:'一鍵執行全部 11 Profiles × Repeat 10',runAllLoopbacksHelp:'依序執行 110 次 SingleShot；每個 profile 獨立保存 artifact，SCPI／cleanup error 會停止整批。',loopbackTrends:'即時 Repeat 趨勢',loopbackTrendsHelp:'紅色點代表 INVALID 或 IQR outlier；資料不會被刪除',
  campaignTitle:'HIL 批次執行器',campaignHelp:'分類矩陣保存到 output/hil-campaign/state.json；關閉瀏覽器或對話後仍可繼續。',campaignRules:'執行規則',campaignRulesHelp:'Prepare 只檢查目前 profile；只有 READY 案例可送 RF。BLOCKED 不會改跑其他 profile。Pause／Stop 只會在單點 cleanup 與 RF Off 邊界生效。',campaignSop1:'準備矩陣',campaignSop2:'依 Priority 接線',campaignSop3:'只執行 READY',campaignSop4:'保存證據',prepareCampaign:'STEP 1：準備／重新檢查矩陣',runNextCampaign:'STEP 3：執行下一個 READY',refreshCampaign:'重新載入',resetCampaign:'重設進度',campaignOperatorConfirm:'操作員在機台旁',campaignRouteConfirm:'RF1.1 Generator output 已接到 RF1.5 Analyzer input',campaignPriority:'重要度',campaignState:'狀態',campaignCategory:'類別',campaignCase:'案例',campaignRoute:'接線',campaignPoints:'點數',campaignEvidence:'下一步／證據',campaignAction:'操作',
  calibrationTitle:'Path Loss 校正 SOP',calibrationHelp:'輸入校正設備的參考面讀值，建立待審查 Draft Profile；此頁不會控制儀器或開啟 RF。',calibrationSop1:'登錄器材',calibrationSop2:'取得讀值',calibrationSop3:'檢查線損',calibrationSop4:'送交核准',calculateDraft:'計算 Draft Profile',draftPreview:'Draft 預覽',downloadDraft:'下載 Draft YAML'
});
Object.assign(translations.en,{
  hardwareSource:'Hardware Measurement',demoSource:'Demo & Training',hardwareSop1:'Set values',hardwareSop2:'Check cabling and operator',hardwareSop3:'Review plan',hardwareSop4:'Execute and save artifacts',
  measurementSettings:'Measurement settings',measurementSettingsHelp:'Select the measurement type and enter the frequency, power, bandwidth, and point count.',singleSetup:'SingleShot setup',singleSetupHelp:'Enter center frequency, WLAN bandwidth, and generator power. The Web checks the approved profile before CMP180 control and requires final confirmation.',reviewSingle:'Review SingleShot plan',sweepSetup:'Sweep setup',sweepSetupHelp:'Set the WLAN EVM sweep axis, range, step, and dwell. Points, estimated time, and safety checks are shown before execution.',reviewPlan:'Review measurement plan',reviewGprf:'Review GPRF plan',safetyCheck:'Cabling and operator safety check',safetyCheckHelp:'Only RF1.1 → RF1.5 is approved. Confirm the direct path has no extra attenuator and an operator is beside the instrument.',safetyCheckHelpGprf:'Only RF1.1 → RF1.5 is approved. Confirm that every cable, attenuator, and adapter is recorded in the plan and an operator is beside the instrument.',directCableConfirm:'I confirm the approved direct path has no unrecorded attenuator or adapter',directCableCheck:'Direct path / no unrecorded attenuator',executeHardware:'Execute hardware measurement',executeHardwareHelp:'A final confirmation is still shown. Cancelling transmits no RF; artifacts are saved after completion.',
  loopbackTitle:'Loopback RF Performance Validation',loopbackHelp:'Run independent SingleShot repeats under fixed conditions to validate the tester, cable, UD Box, and RF path; this is not a DUT PASS.',loopbackWarning:'Stable is not necessarily reasonable',loopbackWarningHelp:'Stability evaluates repeatability; Reasonableness compares Expected RX Power at the analyzer input reference plane. Matching representative points and thresholds with at least Repeat 10 use approved baselines; other conditions remain draft.',loopbackCableConfirm:'Cabling, Cable/UD Box path, and attenuation conditions are confirmed and will remain unchanged',loopbackOperatorConfirm:'An operator is beside the CMP180 and can respond to RF anomalies',runLoopback:'Review and run Loopback',runAllLoopbacks:'Run all 11 profiles × Repeat 10',runAllLoopbacksHelp:'Runs 110 SingleShots sequentially. Each profile saves an independent artifact; any SCPI or cleanup error stops the batch.',loopbackTrends:'Live repeat trends',loopbackTrendsHelp:'Red dots indicate INVALID or IQR outliers; data is never deleted',
  campaignTitle:'HIL Campaign Runner',campaignHelp:'The categorized matrix is saved to output/hil-campaign/state.json and can continue after closing the browser or conversation.',campaignRules:'Execution rules',campaignRulesHelp:'Prepare only checks the current profile; only READY cases may transmit RF. BLOCKED never substitutes another profile. Pause/Stop takes effect only at a SingleShot cleanup and RF Off boundary.',campaignSop1:'Prepare matrix',campaignSop2:'Cable by priority',campaignSop3:'Run READY only',campaignSop4:'Save evidence',prepareCampaign:'STEP 1: Prepare / recheck matrix',runNextCampaign:'STEP 3: Run next READY',refreshCampaign:'Reload',resetCampaign:'Reset progress',campaignOperatorConfirm:'Operator is beside the instrument',campaignRouteConfirm:'RF1.1 Generator output is connected to RF1.5 Analyzer input',campaignPriority:'Priority',campaignState:'State',campaignCategory:'Category',campaignCase:'Case',campaignRoute:'Route',campaignPoints:'Points',campaignEvidence:'Next step / Evidence',campaignAction:'Action',
  calibrationTitle:'Path Loss Calibration SOP',calibrationHelp:'Enter reference-plane readings from calibration equipment to create a draft profile for review. This page does not control the instrument or enable RF.',calibrationSop1:'Register equipment',calibrationSop2:'Acquire readings',calibrationSop3:'Check path loss',calibrationSop4:'Submit for approval',calculateDraft:'Calculate Draft Profile',draftPreview:'Draft Preview',downloadDraft:'Download Draft YAML'
});
Object.assign(translations.zh,{demoSingleMode:'示範單點',demoFrequencyMode:'示範頻率掃描',demoPowerMode:'示範功率掃描',hardwareSingleMode:'WLAN EVM 單點',hardwareFrequencyMode:'WLAN EVM 頻率掃描',hardwarePowerMode:'WLAN EVM 功率掃描',hardwareGprfMode:'RF 功率讀值（GPRF）',gprfModeHelp:'GPRF 是 General Purpose RF：此模式只用 CMP180 Gen/Meas 讀 RF power，可看 tune／power flatness；不是 WLAN EVM、不是 compliance。'});
Object.assign(translations.en,{demoSingleMode:'Demo Single',demoFrequencyMode:'Demo Frequency Sweep',demoPowerMode:'Demo Power Sweep',hardwareSingleMode:'WLAN EVM SingleShot',hardwareFrequencyMode:'WLAN EVM Frequency Sweep',hardwarePowerMode:'WLAN EVM Power Sweep',hardwareGprfMode:'RF Power Reading (GPRF)',gprfModeHelp:'GPRF means General Purpose RF: this mode reads RF power with CMP180 Gen/Meas for tune/power-flatness checks; it is not WLAN EVM or compliance.'});
Object.assign(translations.en,{homeTab:'Home',measurementTab:'Measure',calibrationTab:'Calibration',guideTab:'Operator Guide',guideTitle:'From startup to report',guideIntro:'Each card is a directly usable standard procedure. First choose demo data, a query-only check, or an explicitly authorized hardware mode.',guideSafeTitle:'Recommended now: Demo mode',guideSafeText:'Do not enable RF while power is unstable',guideStep1:'Start service',guideStep2:'Select measurement',guideStep3:'Review results',guideStep4:'Open report',demoCommandTitle:'Start the Demo console',demoCommandHelp:'No CMP180 connection, SCPI, or RF. Use it to review and practice the workflow.',copyCommand:'Copy',openBrowser:'Open browser',configCommandTitle:'Validate configuration',configCommandHelp:'Validates YAML fields and safety settings without contacting the instrument.',expectedOutput:'Expected output',connectionCommandTitle:'Query-only connection check',connectionCommandHelp:'Reads IDN, options, and the error queue without starting measurement or RF.',powerWarning:'During unstable power',queryOnlyAdvice:'Run query-only checks only; do not enable hardware Web mode.',hardwareCommandTitle:'Hardware mode (on hold)',hardwareCommandHelp:'Use only with stable power, confirmed cabling, an on-site operator, and explicit authorization.',hardwareHold:'Instrument power is currently unstable; execution is prohibited.',whereResultsTitle:'Where are results stored?',whereResultsText:'Each run creates an independent output folder. Use Open folder in Run History or open HTML, CSV, and JSON from Results.',whenStopTitle:'When must I stop?',whenStopText:'Stop immediately and verify RF OFF on INV, unknown RF state, timeout, SCPI error, cabling change, or power abnormality.'});
let language='zh';let latest=[];let runHistory=[];let analysisTraces=[];const selectedCompareKeys=new Set();
let resultViewState={mode:'empty'};
let lastSummaryContext={context:{},rawPoints:null};
let expandedRunKey=null;
const $=selector=>document.querySelector(selector);
// 紀錄狀態與篩選文案同步語系，保留後端狀態碼原義。
Object.assign(translations.zh,{"historyUi0": "搜尋", "historyUi1": "日期", "historyUi2": "來源", "historyUi3": "狀態", "historyUi4": "排序", "historyUi5": "全部日期", "historyUi6": "今天", "historyUi7": "最近 7 天", "historyUi8": "最近 30 天", "historyUi9": "全部來源", "historyUi10": "Hardware", "historyUi11": "Demo", "historyUi12": "全部狀態", "historyUi13": "Complete", "historyUi14": "Partial", "historyUi15": "Failed", "historyUi16": "時間：新到舊", "historyUi17": "時間：舊到新", "historyUi18": "點數：多到少", "historyUi19": "頻率：低到高", "historyUi20": "功率：低到高", "historyUi21": "Worst EVM：較差優先", "historyUi22": "比較", "historyUi23": "Actions", "historyRunNote": "執行完成不代表量測有效或規格通過；請查看結果有效性與判定門檻。", "historySearchHint": "測試名稱、Run ID、DUT、操作員、註記"});
Object.assign(translations.en,{"historyUi0": "Search", "historyUi1": "Date", "historyUi2": "Source", "historyUi3": "Status", "historyUi4": "Sort", "historyUi5": "All dates", "historyUi6": "Today", "historyUi7": "Last 7 days", "historyUi8": "Last 30 days", "historyUi9": "All sources", "historyUi10": "Hardware", "historyUi11": "Demo", "historyUi12": "All statuses", "historyUi13": "Complete", "historyUi14": "Partial", "historyUi15": "Failed", "historyUi16": "Time: newest first", "historyUi17": "Time: oldest first", "historyUi18": "Points: most first", "historyUi19": "Frequency: ascending", "historyUi20": "Power: ascending", "historyUi21": "Worst EVM: worst first", "historyUi22": "Compare", "historyUi23": "Actions", "historyRunNote": "Completion does not imply valid results or a specification pass. Review validity and applicable limits.", "historySearchHint": "Test name, Run ID, DUT, operator, notes"});
Object.assign(translations.zh,{homeControl:'本機 Web 控制',homeControlDetail:'可執行接線依後端設定',homeMeasurement:'SingleShot 與掃描',homeMeasurementDetail:'依設定檢查量測條件',homeResult:'28 欄 OFDM SISO',homeResultDetail:'EVM、功率與頻率誤差',capabilityTitle:'CMP180 能力與目前執行範圍',capabilityIntro:'本表區分型錄規格、目前設定與既有 HIL 紀錄。列出的範圍不代表每個條件均已驗證；實際執行仍依所選流程檢查。',capItem:'項目',capCatalog:'CMP180 型錄',capInstalled:'本機／選件',capApproved:'核准 Profile',capHil:'HIL 證據'});
Object.assign(translations.en,{homeControl:'Local Web control',homeControlDetail:'Available routes depend on server configuration',homeMeasurement:'SingleShot and sweeps',homeMeasurementDetail:'Measurement conditions are checked against configuration',homeResult:'28-field OFDM SISO',homeResultDetail:'EVM, power, and frequency error',capabilityTitle:'CMP180 capability and current execution scope',capabilityIntro:'This table separates catalog specifications, local configuration, and existing HIL evidence. A listed range does not mean every condition has been verified; each workflow still checks the requested plan.',capItem:'Item',capCatalog:'CMP180 catalog',capInstalled:'Local installation / options',capApproved:'Approved profile',capHil:'HIL evidence'});
Object.assign(translations.zh,{loopbackTab:'Loopback 驗證',diagramControlsLabel:'架構圖選擇與播放控制',diagramFrameTitle:'CMP180 互動系統架構動畫'});
Object.assign(translations.en,{loopbackTab:'Loopback Validation',diagramControlsLabel:'Architecture diagram selection and playback controls',diagramFrameTitle:'Interactive CMP180 system architecture diagram'});
const homeCopy={
  "zh": {
    "heroTitle": "CMP180 WLAN<br><span>自動化量測與分析</span>",
    "heroIntro": "設定單點量測與頻率／功率掃描，檢視 WLAN EVM、功率及頻率誤差，並保存量測結果。實機可執行範圍依目前設定與後端檢查決定；驗證狀態請見下方能力表。",
    "enterConsole": "進入量測控制台",
    "openManual": "查看操作指南",
    "capabilityTitle": "量測與資料分析功能",
    "capabilityIntro": "整合量測設定、執行狀態、結果檢視與檔案管理。CMsquares 保留作為儀器設定探索與除錯工具。",
    "f1t": "實機量測控制",
    "f1p": "依所選流程檢查頻率、頻寬、功率與接線確認；操作員完成最後確認後執行量測。",
    "f2t": "頻率與功率掃描",
    "f2p": "顯示逐點進度並支援取消。WLAN 掃描遇關鍵結果無效、儀器或收尾錯誤時停止後續點位，保留已取得的結果。",
    "f3t": "WLAN EVM 分析",
    "f3p": "檢視 EVM、功率與頻率誤差，支援互動圖表及圖檔匯出；無效結果以 INVALID 標示。",
    "f4t": "歷史量測比較",
    "f4p": "搜尋與篩選量測紀錄，選取 2–8 筆進行疊圖比較，調整曲線樣式並匯出圖表。",
    "f5t": "路徑損耗資料管理",
    "f5p": "匯入參考讀值並建立校正草稿。正式套用須確認器材、參考面、有效範圍與核准狀態。",
    "f6t": "量測檔案與執行紀錄",
    "f6p": "依量測流程保存結果、設定與執行資訊；實機結果另記錄原始回應及 RF 收尾狀態。可用檔案以該筆紀錄為準。",
    "workflowTitle": "量測操作流程",
    "manualTitle": "操作入口",
    "manualIntro": "首頁提供功能導覽。實機量測、Loopback 與 HIL 批次須在各自頁面完成檢查與執行確認；示範模式不送出 RF。",
    "homeDetail0": "系統資料流程",
    "homeDetail1": "選取節點查看量測計畫、執行檢查、儀器控制與結果保存的處理方式。",
    "homeDetail2": "執行條件檢查",
    "homeDetail3": "接線確認、操作員與設定限制",
    "homeDetail4": "SCPI 控制與 RF 關閉處理",
    "homeDetail5": "結果解析",
    "homeDetail6": "EVM、功率、誤差與有效性",
    "homeDetail7": "量測檔案與歷史曲線",
    "homeDetail8": "系統架構與單點量測流程",
    "homeDetail9": "圖表說明系統組成與單點量測的狀態轉換。可選取節點或播放章節導覽；圖表操作不控制儀器。",
    "homeDetail10": "重新載入圖表",
    "homeDetail11": "另開圖表",
    "homeDetail12": "使用圖內 Play story 播放或暫停章節。「重新載入圖表」會重設目前圖表，不會自動播放。",
    "homeDetail13": "確認接線、輸入限制與操作員在場",
    "homeDetail14": "確認後執行，查看進度或取消",
    "homeDetail15": "檢查結果有效性及量測數值",
    "homeDetail16": "查看結果檔案並匯出圖表",
    "homeDetail17": "選擇量測類型與測試條件",
    "homeDetail18": "校正資料",
    "homeDetail19": "參考讀值匯入與校正草稿",
    "homeDetail20": "量測紀錄",
    "homeDetail21": "結果比較",
    "homeDetail22": "曲線比較、條件差異與圖表匯出",
    "homeDetail23": "操作指南",
    "homeDetail24": "啟動方式、執行檢查與結果說明",
    "homeDetail25": "本機 Web 控制",
    "homeDetail26": "可執行接線依後端設定",
    "homeDetail27": "依設定檢查量測條件",
    "homeDetail28": "結果檔案",
    "homeDetail29": "檔案種類依量測流程",
    "homeLabel0": "量測計畫",
    "homeLabel1": "頻率、功率、頻寬與掃描軸",
    "homeLabel2": "報告與比較",
    "homeLabel3": "系統架構",
    "homeLabel4": "單點量測生命週期",
    "homeLabel5": "建立計畫",
    "homeLabel6": "安全預檢",
    "homeLabel7": "執行量測",
    "homeLabel8": "分析結果",
    "homeLabel9": "保存報告",
    "homeLabel10": "實機、示範、SingleShot 與 Sweep",
    "homeLabel11": "搜尋、篩選、詳情與輸出檔案",
    "homeLabel12": "中英雙語"
  },
  "en": {
    "heroTitle": "CMP180 WLAN<br><span>Measurement and Analysis</span>",
    "heroIntro": "Configure single measurements and frequency or power sweeps, review WLAN EVM, power and frequency error, and save results. Execution depends on the current configuration and server checks; see the capability table for validation status.",
    "enterConsole": "Open measurement console",
    "openManual": "Open operator guide",
    "capabilityTitle": "Measurement and analysis",
    "capabilityIntro": "Measurement setup, execution status, result review and file management. CMsquares remains available for instrument discovery and troubleshooting.",
    "f1t": "Hardware measurement control",
    "f1p": "The selected workflow checks frequency, bandwidth, power and wiring confirmations. Measurement starts after final operator confirmation.",
    "f2t": "Frequency and power sweeps",
    "f2p": "View point progress and request cancellation. WLAN sweeps stop subsequent points on invalid critical results, instrument errors or cleanup errors, retaining available results.",
    "f3t": "WLAN EVM analysis",
    "f3p": "Review EVM, power and frequency error with interactive plots and image export. Invalid results are marked INVALID.",
    "f4t": "Historical measurement comparison",
    "f4p": "Search and filter records; overlay 2–8 runs, adjust trace styles and export plots.",
    "f5t": "Path loss data management",
    "f5p": "Import reference readings and create calibration drafts. Application requires verified equipment, reference planes, valid ranges and approval status.",
    "f6t": "Measurement files and execution records",
    "f6p": "Save results, settings and execution details according to the workflow. Hardware results also record raw responses and RF cleanup status. Available files depend on the run.",
    "workflowTitle": "Measurement workflow",
    "manualTitle": "Workspace shortcuts",
    "manualIntro": "Use the relevant Measurement, Loopback or HIL page for hardware checks and execution confirmation. Demo mode transmits no RF.",
    "homeDetail0": "System data flow",
    "homeDetail1": "Select a node to review planning, execution checks, instrument control and result storage.",
    "homeDetail2": "Execution checks",
    "homeDetail3": "Wiring confirmation, operator and limits",
    "homeDetail4": "SCPI control and RF cleanup",
    "homeDetail5": "Result parsing",
    "homeDetail6": "EVM, power, error and validity",
    "homeDetail7": "Measurement files and historical traces",
    "homeDetail8": "System architecture and single measurement sequence",
    "homeDetail9": "Explore system components and single measurement state transitions. Select nodes or play chapter navigation; diagram controls do not operate the instrument.",
    "homeDetail10": "Reload diagram",
    "homeDetail11": "Open diagram",
    "homeDetail12": "Use Play story inside the diagram to play or pause chapters. Reload diagram resets the view without starting playback.",
    "homeDetail13": "Confirm wiring, input limits and operator presence",
    "homeDetail14": "Confirm execution, monitor progress or cancel",
    "homeDetail15": "Check validity and measured values",
    "homeDetail16": "Review result files and export plots",
    "homeDetail17": "Select measurement type and test conditions",
    "homeDetail18": "Calibration data",
    "homeDetail19": "Reference reading import and calibration drafts",
    "homeDetail20": "Measurement records",
    "homeDetail21": "Result comparison",
    "homeDetail22": "Trace comparison, condition differences and plot export",
    "homeDetail23": "Operator guide",
    "homeDetail24": "Startup, execution checks and result interpretation",
    "homeDetail25": "Local Web control",
    "homeDetail26": "Routes depend on server configuration",
    "homeDetail27": "Measurement conditions checked against configuration",
    "homeDetail28": "Result files",
    "homeDetail29": "File types depend on workflow",
    "homeLabel0": "Measurement plan",
    "homeLabel1": "Frequency, power, bandwidth and sweep axis",
    "homeLabel2": "Reports and comparison",
    "homeLabel3": "System architecture",
    "homeLabel4": "Single measurement sequence",
    "homeLabel5": "Create plan",
    "homeLabel6": "Preflight checks",
    "homeLabel7": "Run measurement",
    "homeLabel8": "Review results",
    "homeLabel9": "Save reports",
    "homeLabel10": "Hardware and demo single measurements and sweeps",
    "homeLabel11": "Search, filters, details and result files",
    "homeLabel12": "Chinese / English"
  }
};
const pageCopy={zh:{home:['RF AUTOMATION PLATFORM','CMP180 自動化量測','安全、可重現、可分析的 WLAN TX EVM 工程工作站'],measurement:['WLAN TX MEASUREMENT','量測控制台','RF1.1 → RF1.5 · 6105 MHz · 320 MHz · -40 dBm'],constellation:['OFFLINE I/Q ANALYSIS','Constellation 星座分析','Software / Mock Verified · HIL Pending · 不連接 CMP180'],'mcs-sweep':['OFFLINE EHT ANALYSIS','MCS Sweep','Software / Mock Verified · HIL Pending · 無 compliance claim'],campaign:['HIL CAMPAIGN','分類實機驗收','持久化頻段、頻寬、功率、Route 與能力驗收進度'],calibration:['PATH LOSS & CALIBRATION','路徑損耗校正','建立可追溯的線材、轉接頭與參考面補償資料'],results:['RESULT ANALYSIS','結果分析台','檢視 EVM、功率與頻率誤差，或比較多筆歷史量測'],history:['RUN ARCHIVE','量測紀錄庫','搜尋、開啟、比較與管理本機保存的量測成果'],guide:['OPERATOR PLAYBOOK','操作指南','從啟動服務、安全檢查到取得報告的標準流程']},en:{home:['RF AUTOMATION PLATFORM','CMP180 Automation','A safe, reproducible, and analyzable WLAN TX EVM engineering workstation'],measurement:['WLAN TX MEASUREMENT','Measurement Console','RF1.1 → RF1.5 · 6105 MHz · 320 MHz · -40 dBm'],constellation:['OFFLINE I/Q ANALYSIS','Constellation Analysis','Software / Mock Verified · HIL Pending · no CMP180 connection'],'mcs-sweep':['OFFLINE EHT ANALYSIS','MCS Sweep','Software / Mock Verified · HIL Pending · no compliance claim'],campaign:['HIL CAMPAIGN','Categorized Hardware Acceptance','Persistent band, bandwidth, power, route, and capability acceptance progress'],calibration:['PATH LOSS & CALIBRATION','Path Loss Calibration','Build traceable compensation data for cables, adapters, and reference planes'],results:['RESULT ANALYSIS','Results & Analysis','Review EVM, power, and frequency error or compare historical runs'],history:['RUN ARCHIVE','Run Archive','Search, open, compare, and manage locally stored measurement results'],guide:['OPERATOR PLAYBOOK','Operator Guide','Standard workflow from service startup and safety checks to reports']}};
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
  if(demo==='advancedPa')return language==='zh'?['ADVANCED PA DEMO','OIP3、Harmonics 與 ACP／ACLR','固定教學模型；不連線儀器或送 RF']:['ADVANCED PA DEMO','OIP3, Harmonics, and ACP/ACLR','Deterministic training model; no instrument or RF'];
  return language==='zh'?['DEMO SINGLE','示範單點量測','僅產生示範資料，不送出 RF']:['DEMO SINGLE','Demo Single Measurement','Demo data only; no RF transmitted'];
}
function updatePageHeading(){const loopbackCopy=language==='zh'?['LOOPBACK BASELINE','Loopback 驗證','Tester／Cable／UD Box／RF Path 的重複性與合理性']:['LOOPBACK BASELINE','Loopback Validation','Repeatability and reasonableness of the tester, cable, UD Box, and RF path'];const copy=activeTopTab==='measurement'?measurementPageCopy():activeTopTab==='loopback'?loopbackCopy:pageCopy[language][activeTopTab];$('#pageKicker').textContent=copy[0];$('#pageTitle').textContent=copy[1];$('#pageContext').textContent=copy[2]}
const heroTypewriterStates=new WeakMap();
function renderHeroTypewriter(element, markup){
  const previous=heroTypewriterStates.get(element);
  // 狀態更新會重套語系；內容相同時不可重啟動畫。
  if(previous?.markup===markup)return;
  if(previous)clearTimeout(previous.timer);
  const state={markup,timer:null};
  heroTypewriterStates.set(element,state);
  element.innerHTML=markup;
  element.classList.add('typewriter-title');
  // 保留完整標題供輔助工具一次朗讀；逐字動畫不使用 live region。
  element.setAttribute('aria-label',element.innerText.replace(/\n/g,' '));
  const walker=document.createTreeWalker(element,NodeFilter.SHOW_TEXT);
  const nodes=[];
  while(walker.nextNode())nodes.push(walker.currentNode);
  const glyphs=[];
  const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
  for(const node of nodes){
    const fragment=document.createDocumentFragment();
    // 以 Unicode 字元切分，保留原有換行與漸層容器，避免逐字出現造成版面跳動。
    const characters=Array.from(node.textContent);
    for(const [position,character] of characters.entries()){
      const glyph=document.createElement('i');
      glyph.className='typewriter-glyph';
      glyph.setAttribute('aria-hidden','true');
      glyphs.push(glyph);
      // 每字直接著色，避免透明子元素使父層 background-clip 漸層文字消失。
      glyph.style.setProperty('--type-progress',`${position/Math.max(1,characters.length-1)*100}%`);
      glyph.textContent=character;
      fragment.append(glyph);
    }
    node.replaceWith(fragment);
  }
  // CSS 預設可見；只在啟動動畫時隱藏，結束後移除暫時狀態，不依賴 CSS 動畫保留畫面。
  if(reducedMotion.matches)return;
  glyphs.forEach(glyph=>{glyph.style.visibility='hidden'});
  let shown=0;
  const started=Date.now();
  const tick=()=>{
    if(heroTypewriterStates.get(element)!==state)return;
    element.querySelector('.typewriter-current')?.classList.remove('typewriter-current');
    // 背景分頁計時器延後時按實際經過時間補齊，避免返回頁面仍卡在半句。
    const count=reducedMotion.matches?glyphs.length:Math.min(glyphs.length,Math.max(0,Math.floor((Date.now()-started-350)/160)+1));
    while(shown<count)glyphs[shown++].style.removeProperty('visibility');
    if(shown===glyphs.length){state.timer=null;return;}
    if(shown)glyphs[shown-1].classList.add('typewriter-current');
    state.timer=setTimeout(tick,40);
  };
  state.timer=setTimeout(tick,350);
}
function applyLanguage(){document.documentElement.lang=language==='zh'?'zh-Hant':'en';document.querySelectorAll('[data-i18n]').forEach(el=>{const value=translations[language][el.dataset.i18n];if(value)el.textContent=value});document.querySelectorAll('[data-home]').forEach(el=>{const value=homeCopy[language][el.dataset.home];if(value){if(el.dataset.home==='heroTitle')renderHeroTypewriter(el,value);else el.textContent=value}});document.querySelectorAll('[data-i18n-placeholder]').forEach(el=>{const value=translations[language][el.dataset.i18nPlaceholder];if(value)el.placeholder=value});document.querySelectorAll('[data-i18n-aria-label]').forEach(el=>{const value=translations[language][el.dataset.i18nAriaLabel];if(value)el.setAttribute('aria-label',value)});document.querySelectorAll('[data-i18n-title]').forEach(el=>{const value=translations[language][el.dataset.i18nTitle];if(value)el.title=value});$('#languageButton').textContent=language==='zh'?'EN':'中文';updatePageHeading();if(window.updateHardwareSummary)window.updateHardwareSummary();if(window.configureGprfFields)window.configureGprfFields();renderRunHistory(false);renderCapabilityProfile();updateThemeLabel();renderToast();renderResultViewState();if(latest.length)renderResultSummary(latest,latestAxis,lastSummaryContext.context,lastSummaryContext.rawPoints);if(analysisTraces.length)renderComparisonControls();if(latest.length||analysisTraces.length)redrawActiveChart();
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
const historyFeedback={phase:'idle',detail:''};
const runDetailCache=new Map();
function uiText(zh,en){return language==='zh'?zh:en}
function renderHistoryFeedback(){
  const busy=historyFeedback.phase==='loading',failed=historyFeedback.phase==='error';
  const button=$('#refreshHistoryButton'),notice=$('#historyNotice');
  button.disabled=busy;
  button.textContent=busy?uiText('載入中…','Loading…'):translations[language].refreshHistory;
  $('#history').setAttribute('aria-busy',String(busy));
  notice.hidden=!busy&&!failed;
  notice.dataset.state=historyFeedback.phase;
  notice.textContent=busy?uiText('正在讀取量測紀錄…','Loading measurement records…'):failed?uiText('無法更新紀錄。可按「重新整理」重試；下方如有資料，為上次載入內容。','Unable to refresh records. Use Refresh to retry; any rows below are from the previous load.')+' '+historyFeedback.detail:'';
  const empty=$('#historyEmpty');
  empty.hidden=busy||failed||filteredRuns().length>0;
  empty.textContent=runHistory.length?uiText('沒有符合篩選條件的紀錄，請調整搜尋或篩選。','No records match. Adjust the search or filters.'):uiText('尚無量測紀錄。完成量測後，可在此查看結果。','No measurement records yet. Completed measurements will appear here.');
}
function renderRunHistory(loadDetail=true){const labels=language==='zh'?{load:'查看詳情',close:'收合詳情',open:'開啟輸出',trash:'刪除'}:{load:'View details',close:'Close details',open:'Open output',trash:'Delete'};const rows=filteredRuns();$('#historyEmpty').hidden=rows.length>0;$('#historyEmpty').textContent=language==='zh'?'沒有符合條件的量測紀錄。':'No runs match the current filters.';$('#historyRows').innerHTML=rows.map(run=>{const files=run.artifact_urls||{};const links=[historyLink(files.report,'HTML'),historyLink(files.csv,'CSV'),historyLink(files.json,'JSON'),historyLink(files.metadata,'Metadata')].filter(Boolean).join(' · ');const source=run.simulated?uiText('示範','DEMO'):uiText('實機','HARDWARE'),checked=selectedCompareKeys.has(run.run_key)?'checked':'',expanded=expandedRunKey===run.run_key,openUrl=files.report||files.json||files.csv||files.metadata||'';return `<tr class="run-main-row"><td class="select-column"><input class="run-select" type="checkbox" data-compare-run="${escapeHtml(run.run_key)}" ${checked} aria-label="Select ${escapeHtml(run.test_name)} for comparison"></td><td>${run.created_at?new Date(run.created_at).toLocaleString(language==='zh'?'zh-TW':'en-US'):'—'}</td><td>${escapeHtml(run.test_name)}</td><td><code>${escapeHtml(run.run_id)}</code></td><td><span class="pill ${run.simulated?'neutral':'hardware-source'}">${source}</span></td><td>${escapeHtml(uiText(({complete:'執行完成',partial:'部分完成',failed:'執行失敗',cancelled:'已取消'})[String(run.status).toLowerCase()]||String(run.status).toUpperCase(),String(run.status).toUpperCase()))}</td><td>${run.completed_points}</td><td class="history-links">${links||'—'}</td><td class="record-actions"><button type="button" data-record-action="load" data-run-key="${escapeHtml(run.run_key)}">${expanded?labels.close:labels.load}</button><button type="button" data-record-action="open" data-open-url="${escapeHtml(openUrl)}" ${openUrl?'':'disabled'}>${labels.open}</button><button type="button" class="danger-mini" data-record-action="trash" data-run-key="${escapeHtml(run.run_key)}" data-run-id="${escapeHtml(run.run_id)}">${labels.trash}</button></td></tr><tr class="run-detail-row" data-detail-row="${escapeHtml(run.run_key)}" ${expanded?'':'hidden'}><td colspan="9"><div class="inline-run-detail">${expanded?'<div class="detail-loading">'+uiText('載入詳情中…','Loading details…')+'</div>':''}</div></td></tr>`}).join('');updateCompareSelection();renderHistoryFeedback();if(expandedRunKey&&(loadDetail||runDetailCache.has(expandedRunKey)))loadRunRecord(expandedRunKey,true)}
const renderRunHistoryBase=renderRunHistory;
renderRunHistory=function(...args){
  renderRunHistoryBase(...args);
  document.querySelectorAll('.record-actions').forEach(actions=>{
    if(actions.querySelector('[data-record-action="rename"]'))return;
    const button=document.createElement('button');
    button.type='button';button.dataset.recordAction='rename';button.dataset.runKey=actions.querySelector('[data-record-action="load"]')?.dataset.runKey||'';
    button.textContent=language==='zh'?'改名':'Rename';actions.insertBefore(button,actions.querySelector('[data-record-action="open"]'));
  });
}
$('#historyRows').addEventListener('click',async event=>{
  const button=event.target.closest('[data-record-action="rename"]');if(!button)return;
  const run=runHistory.find(item=>item.run_key===button.dataset.runKey),current=run?.test_name||'';
  const next=prompt(language==='zh'?'輸入量測紀錄顯示名稱：':'Enter a display name for this measurement:',current);
  if(next===null)return;
  button.disabled=true;
  try{await postRecordAction(button.dataset.runKey,'rename',{display_name:next});runDetailCache.delete(button.dataset.runKey);await loadRunHistory();toast(language==='zh'?'量測紀錄名稱已更新':'Measurement record name updated')}catch(error){toast(error.message,'error')}finally{button.disabled=false}
});
async function loadRunHistory(){
  // 僅手動或導覽讀取紀錄；阻擋重複請求，不對 RF 操作套用重試。
  if(historyFeedback.phase==='loading')return;
  historyFeedback.phase='loading';historyFeedback.detail='';renderHistoryFeedback();
  try{
    const response=await fetch('/api/runs',{cache:'no-store',signal:AbortSignal.timeout(15000)});
    const data=await response.json();
    if(!response.ok)throw new Error(data.error||`HTTP ${response.status}`);
    runHistory=Array.isArray(data.runs)?data.runs:[];
    const validKeys=new Set(runHistory.map(run=>run.run_key));
    [...selectedCompareKeys].forEach(key=>{if(!validKeys.has(key))selectedCompareKeys.delete(key)});
    historyFeedback.phase='ready';renderRunHistory();
  }catch(error){
    // 失敗保留上次資料並標示過期狀態，不能當作空清單或成功載入。
    historyFeedback.phase='error';historyFeedback.detail=String(error.message||error);
  }finally{renderHistoryFeedback();}
}
function escapeHtml(value){const node=document.createElement('span');node.textContent=String(value);return node.innerHTML}
// 全頁共用的頻率單位轉換／顯示格式；原本在 custom-plan.js／gprf-power.js／hardware.js 各自重複一份，統一成單一來源。
function frequencyToHz(value,unit){return Number(value)*(unit==='GHz'?1e9:1e6)}
function formatFrequency(hz){return hz>=1e9?`${(hz/1e9).toFixed(3)} GHz`:`${(hz/1e6).toFixed(1)} MHz`}
function updateCompareSelection(){const count=selectedCompareKeys.size;$('#compareCount').textContent=language==='zh'?`已選 ${count} 筆`:`${count} selected`;$('#compareSelectedButton').textContent=count===1?(language==='zh'?'查看所選圖表':'Plot selected run'):(language==='zh'?'比較所選資料':'Compare selected runs');$('#compareSelectedButton').disabled=count<1||count>8}
// 儀器缺值與空字串不代表 0；先排除，避免污染圖表及摘要統計。
function finiteNumber(value){if(value===null||value===undefined||typeof value==='boolean'||(typeof value==='string'&&!value.trim()))return null;const number=Number(value);return Number.isFinite(number)?number:null}
function normalizeHistoricalPoints(record){const source=Array.isArray(record.results)?record.results:(record.results?.points||[]);const metadata=record.metadata||{};return source.map((raw,index)=>{const frequency=finiteNumber(raw.frequency_hz??metadata.frequency_hz??metadata.center_frequency_hz),power=finiteNumber(raw.generator_power_dbm??metadata.generator_power_dbm),evmAll=finiteNumber(raw.evm_all_db??raw.evm_all_carriers_db),evmData=finiteNumber(raw.evm_data_db??raw.evm_data_carriers_db),evmPilot=finiteNumber(raw.evm_pilot_db??raw.evm_pilot_carriers_db),burstPower=finiteNumber(raw.burst_power_dbm),expectedPower=finiteNumber(raw.expected_power_dbm??raw.generator_power_dbm??metadata.generator_power_dbm),powerError=burstPower!==null&&expectedPower!==null?burstPower-expectedPower:null,peakPower=finiteNumber(raw.peak_power_dbm),frequencyError=finiteNumber(raw.frequency_error_hz),clockError=finiteNumber(raw.clock_error_ppm??raw.clock_error),pin=finiteNumber(raw.pin_dbm),pout=finiteNumber(raw.pout_dbm),gain=finiteNumber(raw.gain_db);return {point_index:Number(raw.point_index??index),frequency_hz:frequency,generator_power_dbm:power,expected_power_dbm:expectedPower,power_error_db:powerError,pin_dbm:pin,pout_dbm:pout,gain_db:gain,evm_all_db:evmAll,evm_data_db:evmData,evm_pilot_db:evmPilot,burst_power_dbm:burstPower,peak_power_dbm:peakPower,frequency_error_hz:frequencyError,clock_error_ppm:clockError,margin_db:finiteNumber(raw.margin_db),measurement_state:String(raw.measurement_state||''),valid:typeof raw.valid==='boolean'?raw.valid:([evmAll,burstPower,frequencyError,pout,gain].some(value=>value!==null)&&String(raw.measurement_state||'').toUpperCase()!=='INV'),limit_status:String(raw.limit_status||raw.status||'RECORDED')}})}
function inferTraceAxis(points){const frequencies=new Set(points.map(point=>point.frequency_hz).filter(value=>value!==null));const powers=new Set(points.map(point=>point.generator_power_dbm).filter(value=>value!==null));return powers.size>frequencies.size?'power':'frequency'}
const traceColors=['#18d7e5','#f59e0b','#a78bfa','#43c47a','#f05261','#60a5fa','#f472b6','#eab308'];
// 歷史回放時，主紀錄（第一筆）沿用量測完成時的摘要、明細表與已保存 artifacts；比較模式再於前方補上跨 Run 統計。
function renderHistoryDetail(records,traces){
  const primary=records.find(record=>traces.some(trace=>trace.id===record.run_key))||records[0];
  const trace=traces.find(item=>item.id===primary.run_key)||traces[0];
  const metadata=primary.metadata||{};
  // 規格、量測家族與 P1dB 都保存在 metadata；沒有的欄位維持 null，不猜測當時的判定條件。
  const context={
    measurement_family:String(metadata.measurement_family||''),
    p1db:metadata.p1db||null,
    limit_profile:metadata.limit_profile||null,
    compliance_claim:Boolean(metadata.compliance_claim)
  };
  const rawPoints=Array.isArray(primary.results)?primary.results:(primary.results?.points||[]);
  renderResultSummary(trace.points,trace.axis,context,rawPoints);
  if(traces.length>1)$('#metrics').innerHTML=metric('Runs',traces.length)+metric('Visible',traces.filter(item=>item.visible).length)+metric('Points',traces.reduce((sum,item)=>sum+item.points.length,0))+metric('Mode','READ ONLY')+$('#metrics').innerHTML;
  const summary=runHistory.find(run=>run.run_key===primary.run_key)||{};
  const urls=summary.artifact_urls||{};
  $('#artifacts').innerHTML=['csv','json','report'].filter(key=>urls[key]).map(key=>`<a href="${urls[key]}" target="_blank" rel="noopener">${key==='report'?'HTML':key.toUpperCase()}</a>`).join(' · ');
  renderMatplotlibGallery(urls);
  return trace;
}
async function compareSelectedRuns(){const button=$('#compareSelectedButton');button.disabled=true;try{const keys=[...selectedCompareKeys];const records=await Promise.all(keys.map(async key=>{const response=await fetch(`/api/runs/${encodeURIComponent(key)}`);const record=await response.json();if(!response.ok)throw new Error(record.error||`Unable to load ${key}`);return record}));analysisTraces=records.map((record,index)=>{const summary=runHistory.find(run=>run.run_key===record.run_key)||{};const points=normalizeHistoricalPoints(record);return {id:record.run_key,name:summary.test_name||record.metadata?.test_name||record.metadata?.run_id||record.run_key,color:traceColors[index],visible:true,colorLocked:false,lineStyle:'solid',pointShape:'circle',axis:inferTraceAxis(points),compatibility:{bandwidth:summary.bandwidth_hz,route:summary.route,calibration:summary.calibration_profile,waveform:record.metadata?.waveform_file||record.metadata?.arb_waveform_file||'',mcs:record.metadata?.mcs||''},points}}).filter(trace=>trace.points.length);if(analysisTraces.length<1)throw new Error(language==='zh'?'所選紀錄沒有可用結果':'The selected run has no usable results');latestAxis=analysisTraces[0].axis;latest=analysisTraces[0].points;selectBestChartMetric(latest,{measurement_family:String(records[0].metadata?.measurement_family||'')});renderComparisonControls();const primaryTrace=renderHistoryDetail(records,analysisTraces);resultViewState={mode:'history',traceCount:analysisTraces.length,primaryName:primaryTrace.name};renderResultViewState();activateTopTab('results');drawAnalysisChart()}catch(error){toast(error.message,'error')}finally{updateCompareSelection()}}
function compatibilityWarnings(){const fields=['bandwidth','waveform','mcs','route','calibration'];return fields.filter(field=>new Set(analysisTraces.map(trace=>trace.compatibility[field]).filter(Boolean)).size>1)}
function renderComparisonControls(){$('#comparisonPanel').hidden=false;const axes=new Set(analysisTraces.map(trace=>trace.axis)),warnings=compatibilityWarnings();$('#comparisonHint').textContent=warnings.length?(language==='zh'?`相容性警告：${warnings.join('、')} 不一致，禁止直接做合規結論。`:`Compatibility warning: ${warnings.join(', ')} differ; do not infer compliance.`):axes.size>1?(language==='zh'?'資料包含不同掃描軸；請確認比較目的。':'Runs use different sweep axes; verify comparison intent.'):(language==='zh'?'EVM 越負通常越好；INVALID 點會中斷，不與正常資料連線。':'More-negative EVM is generally better; INVALID points break traces.');$('#traceList').innerHTML=analysisTraces.map((trace,index)=>`<div class="trace-control" draggable="true" data-trace-index="${index}"><button class="trace-drag" type="button" title="Drag to reorder">⋮⋮</button><input type="checkbox" data-trace-visible="${index}" ${trace.visible?'checked':''} title="Hide / Show"><input type="color" data-trace-color="${index}" value="${trace.color}" ${trace.colorLocked?'disabled':''}><input type="text" data-trace-name="${index}" value="${escapeHtml(trace.name)}"><select data-trace-line="${index}" title="Line style"><option value="solid" ${trace.lineStyle==='solid'?'selected':''}>Solid</option><option value="dash" ${trace.lineStyle==='dash'?'selected':''}>Dash</option><option value="dot" ${trace.lineStyle==='dot'?'selected':''}>Dot</option></select><select data-trace-point="${index}" title="Point shape"><option value="circle" ${trace.pointShape==='circle'?'selected':''}>●</option><option value="square" ${trace.pointShape==='square'?'selected':''}>■</option><option value="diamond" ${trace.pointShape==='diamond'?'selected':''}>◆</option></select><button type="button" data-trace-solo="${index}">Solo</button><button type="button" data-trace-lock="${index}" title="Color lock">${trace.colorLocked?'🔒':'🔓'}</button><button type="button" class="trace-remove" data-trace-remove="${index}" title="Remove">×</button><small>${trace.points.length} pts</small></div>`).join('')}
$('#compareSelectedButton').onclick=compareSelectedRuns;
$('#traceList').oninput=event=>{const index=Number(event.target.dataset.traceVisible??event.target.dataset.traceColor??event.target.dataset.traceName??event.target.dataset.traceLine??event.target.dataset.tracePoint);if(!Number.isInteger(index)||!analysisTraces[index])return;if(event.target.dataset.traceVisible!==undefined)analysisTraces[index].visible=event.target.checked;if(event.target.dataset.traceColor!==undefined&&!analysisTraces[index].colorLocked)analysisTraces[index].color=event.target.value;if(event.target.dataset.traceName!==undefined)analysisTraces[index].name=event.target.value;if(event.target.dataset.traceLine!==undefined)analysisTraces[index].lineStyle=event.target.value;if(event.target.dataset.tracePoint!==undefined)analysisTraces[index].pointShape=event.target.value;drawAnalysisChart()};
$('#traceList').onclick=event=>{const solo=event.target.closest('[data-trace-solo]'),lock=event.target.closest('[data-trace-lock]'),remove=event.target.closest('[data-trace-remove]');if(solo){const index=Number(solo.dataset.traceSolo);analysisTraces.forEach((trace,i)=>trace.visible=i===index)}if(lock){const index=Number(lock.dataset.traceLock);analysisTraces[index].colorLocked=!analysisTraces[index].colorLocked}if(remove){analysisTraces.splice(Number(remove.dataset.traceRemove),1)}if(solo||lock||remove){renderComparisonControls();drawAnalysisChart()}};
let draggedTraceIndex=null;$('#traceList').ondragstart=event=>{const item=event.target.closest('[data-trace-index]');if(item)draggedTraceIndex=Number(item.dataset.traceIndex)};$('#traceList').ondragover=event=>event.preventDefault();$('#traceList').ondrop=event=>{event.preventDefault();const target=event.target.closest('[data-trace-index]');if(target&&draggedTraceIndex!==null){const [trace]=analysisTraces.splice(draggedTraceIndex,1);analysisTraces.splice(Number(target.dataset.traceIndex),0,trace);renderComparisonControls();drawAnalysisChart()}draggedTraceIndex=null};
$('#refreshHistoryButton').onclick=loadRunHistory;
function metadataTable(metadata){return `<dl class="settings-list">${Object.entries(metadata).map(([key,value])=>`<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(typeof value==='object'?JSON.stringify(value):value)}</dd>`).join('')}</dl>`}
async function loadRunRecord(runKey,alreadyExpanded=false){if(!alreadyExpanded&&expandedRunKey===runKey){expandedRunKey=null;renderRunHistory();return}expandedRunKey=runKey;if(!alreadyExpanded)renderRunHistory();const row=document.querySelector(`[data-detail-row="${CSS.escape(runKey)}"]`),container=row?.querySelector('.inline-run-detail');if(!container)return;try{let record=runDetailCache.get(runKey);if(!record){const response=await fetch(`/api/runs/${encodeURIComponent(runKey)}`,{signal:AbortSignal.timeout(15000)});record=await response.json();if(!response.ok)throw new Error(record.error||`HTTP ${response.status}`);runDetailCache.set(runKey,record);}const waveform=record.waveform_recorded?escapeHtml(record.waveform_reference):(language==='zh'?'未保存 Waveform reference':'Waveform reference not saved');container.innerHTML=`<div class="inline-detail-head"><div><strong>Run ${escapeHtml(record.metadata.run_id||runKey)}</strong><code>${escapeHtml(record.output_location)}</code></div><span>${language==='zh'?'詳情顯示於原紀錄下方':'Details shown under the selected run'}</span></div><div class="history-detail-grid"><div><h4>${uiText('設定','Settings')}</h4>${metadataTable(record.metadata)}</div><div><h4>${uiText('波形','Waveform')}</h4><p>${waveform}</p><h4>${uiText('原始回應檔案','Raw response files')}</h4><p>${record.raw_files.length?escapeHtml(record.raw_files.join(', ')):(language==='zh'?'無 raw 檔案':'No raw files')}</p></div></div><details><summary>${uiText('量測結果 JSON','Results JSON')}</summary><pre>${escapeHtml(JSON.stringify(record.results,null,2))}</pre></details>`}catch(error){container.textContent=uiText('無法載入詳情，請收合後重新開啟：','Unable to load details. Close and reopen to retry: ')+String(error.message||error);}}
async function postRecordAction(runKey,action,payload={}){const response=await fetch(`/api/runs/${encodeURIComponent(runKey)}/${action}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const data=await response.json();if(!response.ok)throw new Error(data.error||'Record action failed');return data}
$('#historyRows').onclick=async event=>{const checkbox=event.target.closest('[data-compare-run]');if(checkbox){checkbox.checked?selectedCompareKeys.add(checkbox.dataset.compareRun):selectedCompareKeys.delete(checkbox.dataset.compareRun);updateCompareSelection();return}const button=event.target.closest('[data-record-action]');if(!button)return;const action=button.dataset.recordAction,runKey=button.dataset.runKey;button.disabled=true;try{if(action==='load')await loadRunRecord(runKey);if(action==='open'){const url=button.dataset.openUrl;if(!url)throw new Error(language==='zh'?'此紀錄沒有可開啟的輸出檔案':'This run has no browser-readable output');window.open(url,'_blank','noopener');toast(language==='zh'?'已在新分頁開啟輸出':'Output opened in a new tab')}if(action==='trash'){const runId=button.dataset.runId;const typed=prompt(language==='zh'?`刪除防呆：輸入 Run ID ${runId}，紀錄將移至可復原 Trash。`:`Safety check: type Run ID ${runId}; the run will move to recoverable Trash.`);if(typed!==runId){toast(language==='zh'?'Run ID 不符，已取消刪除':'Run ID mismatch; deletion cancelled','error');return}if(!confirm(language==='zh'?'確定將此完整 Run 與 artifacts 移至 Trash？':'Move this complete run and its artifacts to Trash?'))return;await postRecordAction(runKey,'trash',{confirm_run_id:typed});expandedRunKey=null;await loadRunHistory();toast(language==='zh'?'紀錄已移至可復原 Trash':'Run moved to recoverable Trash')}}catch(error){toast(error.message,'error')}finally{button.disabled=false}};
$('#closeHistoryDetail').onclick=()=>{$('#historyDetail').hidden=true};
['runSearch','runDateFilter','runSourceFilter','runStatusFilter','runSort'].forEach(id=>{$('#'+id).addEventListener(id==='runSearch'?'input':'change',renderRunHistory)});
let toastTimer=null,toastState=null;
function renderToast(){
  if(!toastState)return;
  $('#toastTitle').textContent=toastState.type==='error'?uiText('操作未完成','Action not completed'):uiText('操作提示','Notification');
  $('#toastMessage').textContent=typeof toastState.message==='object'?toastState.message[language]:toastState.message;
  $('#dismissToast').textContent=uiText('關閉','Dismiss');
}
function toast(message,type='info'){
  // 新提示取代舊計時器；錯誤保留到手動關閉，避免重要診斷資訊消失。
  clearTimeout(toastTimer);toastState={message,type};renderToast();
  const node=$('#toast');node.dataset.type=type;node.classList.add('show');
  if(type!=='error')toastTimer=setTimeout(()=>{node.classList.remove('show');toastState=null},4800);
}
$('#dismissToast').onclick=()=>{clearTimeout(toastTimer);$('#toast').classList.remove('show');toastState=null};
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
function drawAdvancedBarChart(selector,samples){
  const svg=$(selector),width=560,height=300,left=64,right=18,top=25,bottom=58;
  const values=samples.map(sample=>Number(sample.value)).filter(Number.isFinite);
  if(!values.length){svg.innerHTML='<text x="280" y="150" text-anchor="middle" class="axis-label">No simulated data</text>';return}
  const low=Math.floor(Math.min(...values,-60)/10)*10-5,high=Math.ceil(Math.max(...values,0)/10)*10+5,span=Math.max(high-low,10);
  const y=value=>top+(high-value)/span*(height-top-bottom),slot=(width-left-right)/samples.length,barWidth=Math.min(56,slot*.52),base=y(low);
  // 小圖只呈現後端固定模型；輸入的 MHz 已在送出前轉為 Hz，功率一律為 dBm。
  let html=`<line x1="${left}" y1="${height-bottom}" x2="${width-right}" y2="${height-bottom}" class="grid-line"/><line x1="${left}" y1="${top}" x2="${left}" y2="${height-bottom}" class="grid-line"/>`;
  for(let tick=0;tick<=4;tick++){const value=low+span*tick/4,py=y(value);html+=`<line x1="${left}" y1="${py}" x2="${width-right}" y2="${py}" class="grid-line"/><text x="${left-8}" y="${py+5}" text-anchor="end" class="axis-label">${value.toFixed(0)}</text>`}
  samples.forEach((sample,index)=>{const value=Number(sample.value),x=left+slot*(index+.5),py=y(value);html+=`<rect x="${x-barWidth/2}" y="${Math.min(py,base)}" width="${barWidth}" height="${Math.max(2,Math.abs(base-py))}" rx="3" class="advanced-bar"><title>${escapeHtml(sample.label)}: ${value.toFixed(2)} dBm</title></rect><text x="${x}" y="${height-bottom+22}" text-anchor="middle" class="axis-label">${escapeHtml(sample.label)}</text><text x="${x}" y="${Math.max(top+13,py-7)}" text-anchor="middle" class="bar-value">${value.toFixed(1)}</text>`});
  html+=`<text x="19" y="150" text-anchor="middle" transform="rotate(-90 19 150)" class="axis-title mini-axis">Power (dBm)</text>`;
  svg.innerHTML=html;
}
function renderAdvancedPa(data){
  const metrics=data.metrics||{},format=(key,unit)=>Number.isFinite(Number(metrics[key]))?Number(metrics[key]).toFixed(2)+' '+unit:'—';
  $('#advancedPaMetrics').innerHTML=metric('OIP3',format('oip3_dbm','dBm'))+metric('IM3',format('im3_dbc','dBc'))+metric('H2',format('h2_dbc','dBc'))+metric('H3',format('h3_dbc','dBc'))+metric('Lower ACLR',format('aclr_lower_db','dB'))+metric('Upper ACLR',format('aclr_upper_db','dB'));
  drawAdvancedBarChart('#oip3Chart',(data.two_tone||[]).map(point=>({label:point.label,value:point.power_dbm})));
  drawAdvancedBarChart('#harmonicChart',(data.harmonics||[]).map(point=>({label:`H${point.order}`,value:point.power_dbm})));
  drawAdvancedBarChart('#acpChart',(data.acp_channels||[]).map(point=>({label:point.channel==='Lower adjacent'?'Lower':point.channel==='Upper adjacent'?'Upper':'Main',value:point.power_dbm})));
  const urls=data.artifact_urls||{};
  $('#advancedPaArtifacts').innerHTML=`<strong>SIMULATED artifacts</strong><br>${['csv','json','report'].filter(key=>urls[key]).map(key=>`<a href="${urls[key]}" target="_blank" rel="noopener">${key==='report'?'HTML':key.toUpperCase()}</a>`).join(' · ')}<br><code>${escapeHtml(data.output_location||'')}</code>`;
  $('#advancedPaResult').hidden=false;
}
$('#advancedPaForm').onsubmit=async event=>{event.preventDefault();const form=new FormData(event.target),button=event.submitter;button.disabled=true;try{
  // Demo 不建立儀器 session；前端只送模擬參數到本機 API 並顯示計算結果。
  const response=await fetch('/api/mock/pa-advanced',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({frequency_hz:+form.get('frequency_mhz')*1e6,input_power_dbm:+form.get('input_power_dbm'),tone_spacing_hz:+form.get('tone_spacing_mhz')*1e6,channel_bandwidth_hz:+form.get('channel_bandwidth_mhz')*1e6,test_name:form.get('test_name')})});
  const data=await response.json();if(!response.ok)throw new Error(data.error||'Unable to generate advanced PA demo');renderAdvancedPa(data);
}catch(error){toast(error.message,'error')}finally{button.disabled=false}};
let latestAxis='frequency';
// 目前結果套用的 EVM spec limit（dB）；null 代表本次沒有套用 limit profile。
let latestSpecLimitDb=null;
// P1dB 是由相鄰實測點內插而來；保留 metadata 才能在 PA 圖上標出非整數功率的位置。
let latestP1db=null;
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
  const result=p1db||{},status=result.status||'insufficient_points';
  // null 不可經 Number(null) 變成零；未找到與資料不足必須保留不同狀態。
  const value=(name,unit)=>{const number=finiteNumber(result[name]);return number===null?'—':number.toFixed(2)+unit};
  return metric(uiText('小訊號增益','Small-signal gain'),value('small_signal_gain_db',' dB'))
    +metric(uiText('最大壓縮量','Max compression'),value('max_compression_db',' dB'))
    +metric('IP1dB',status==='found'?value('ip1db_dbm',' dBm'):status)
    +metric('OP1dB',status==='found'?value('op1db_dbm',' dBm'):status);
}
function paSummaryMetrics(points,axis,p1db){
  // PA 統計只使用同時具備有效 Pin／Pout／Gain 的點；INVALID 的數值僅供診斷。
  const valid=points.filter(point=>point.valid===true&&['pin_dbm','pout_dbm','gain_db'].every(key=>finiteNumber(point[key])!==null));
  const gains=valid.map(point=>Number(point.gain_db));
  const mean=gains.length?gains.reduce((sum,value)=>sum+value,0)/gains.length:null;
  const format=value=>value===null?'—':value.toFixed(3)+' dB';
  const gainMetrics=axis==='power'?p1dbMetrics(p1db)
    :metric(uiText('平均增益','Mean gain'),format(mean))
      +metric(uiText('增益峰對峰漣波','Gain peak-to-peak ripple'),format(gains.length?Math.max(...gains)-Math.min(...gains):null))
      +metric(uiText('增益標準差','Gain standard deviation'),format(gains.length?Math.sqrt(gains.reduce((sum,value)=>sum+(value-mean)**2,0)/gains.length):null));
  // Max Pout 取所有有效輸出中的最大值，不假設最高 Pin 的輸出必定最大。
  return gainMetrics+metric(uiText('最大 Pout','Max Pout'),valid.length?Math.max(...valid.map(point=>Number(point.pout_dbm))).toFixed(2)+' dBm':'—')
    +metric(uiText('有效點','Valid points'),`${valid.length}/${points.length}`);
}
function renderResultViewState(){
  const notice=$('#resultNotice'),badge=$('#resultBadge'),meta=$('#runMeta'),state=resultViewState;
  badge.className='pill neutral';
  if(state.mode==='empty'){
    badge.textContent='NO DATA';meta.textContent=uiText('尚未執行量測。','No measurement has been run.');notice.dataset.state='empty';
    notice.textContent=uiText('尚無結果。請先執行示範量測，或從量測紀錄開啟既有資料。','No results yet. Run a demo measurement or open saved data from Run History.');
    if(!latest.length&&!analysisTraces.length)$('#chart').innerHTML=`<text class="axis-label" x="450" y="150" text-anchor="middle">${uiText('尚無可顯示的量測資料','No measurement data to display')}</text>`;
    return;
  }
  if(state.mode==='history'){
    const compared=state.traceCount>1;
    badge.textContent=compared?'COMPARE':'HISTORY';meta.textContent=compared
      ?uiText(`比較 ${state.traceCount} 筆歷史量測（唯讀）`,`Comparing ${state.traceCount} historical runs (read-only)`)
      :uiText('查看 1 筆歷史量測（唯讀）','Viewing 1 historical run (read-only)');
    if(compared&&state.primaryName)meta.textContent+=uiText(` · 明細與檔案顯示第 1 筆：${state.primaryName}`,` · Details and files show run 1: ${state.primaryName}`);
    notice.dataset.state='ready';notice.textContent=uiText('歷史資料為唯讀。比較前請確認頻寬、波形、MCS、接線與校正條件相容。','Historical data is read-only. Before comparison, verify bandwidth, waveform, MCS, route, and calibration compatibility.');
    return;
  }
  const source=state.simulated?uiText('示範資料','DEMO DATA'):uiText('實機資料','HARDWARE');
  const pointLabel=language==='zh'?'點':state.pointCount===1?'point':'points';
  meta.textContent=`Run ${state.runId} · ${state.pointCount} ${pointLabel} · ${source}`;
  if(state.validCount===0){badge.textContent='INVALID';badge.classList.add('danger');notice.dataset.state='error';notice.textContent=uiText('沒有有效量測點。請查看各點狀態、原始回應與收尾紀錄；此結果不可用於規格判定。','No valid measurement points. Review point status, raw responses, and cleanup records; do not use this result for specification decisions.');return;}
  if(state.status!=='complete'||state.invalidCount>0){badge.textContent=state.status==='cancelled'?'CANCELLED':'PARTIAL';badge.classList.add('draft-limit');notice.dataset.state='warning';notice.textContent=uiText(`已保留 ${state.validCount} 個有效點，另有 ${state.invalidCount} 個無效或未完成點。請先查明原因再比較或判定。`,`Retained ${state.validCount} valid points; ${state.invalidCount} points are invalid or incomplete. Investigate before comparison or assessment.`);return;}
  badge.textContent='COMPLETE';badge.classList.add('hardware-source');notice.dataset.state='ready';notice.textContent=uiText(`執行完成，共 ${state.validCount} 個有效點。完成狀態不等於規格通過，仍須查看有效性與適用限值。`,`Execution completed with ${state.validCount} valid ${state.validCount===1?'point':'points'}. Completion does not imply a specification pass; review validity and applicable limits.`);
}
// 量測完成與歷史回放共用同一套摘要／明細渲染；歷史紀錄丟回圖表時必須看到與當時相同的數值。
function renderResultSummary(points,axis,context={},rawPoints=null){
  lastSummaryContext={context,rawPoints};
  const source=Array.isArray(rawPoints)?rawPoints:points;
  const xField=xFieldFor(axis);
  $('#xAxisHeader').textContent=xUnitFor(axis);
  // INVALID 即使留有診斷數值也不列入 EVM 摘要。
  const validEvm=points.filter(point=>point.valid).map(point=>point.evm_all_db).filter(Number.isFinite);
  const avg=validEvm.length?validEvm.reduce((sum,value)=>sum+value,0)/validEvm.length:null;
  const worst=validEvm.length?Math.max(...validEvm):null;
  const pass=points.filter(point=>['PASS','DRAFT_PASS'].includes(point.limit_status)).length;
  const measured=points.filter(point=>point.valid&&point.limit_status==='MEASURED').length;
  const fixedLabel=axis==='power'?uiText('固定頻率','Fixed frequency'):uiText('固定功率','Fixed power');
  // 歷史紀錄可能缺少固定軸欄位；取第一個有效值，缺值顯示破折號而不是補 0。
  const firstFrequency=points.map(point=>finiteNumber(point.frequency_hz)).find(value=>value!==null);
  const firstPower=points.map(point=>finiteNumber(point.generator_power_dbm)).find(value=>value!==null);
  const fixedValue=axis==='power'
    ?(firstFrequency===undefined?'—':(firstFrequency/1e6).toFixed(1)+' MHz')
    :(firstPower===undefined?'—':firstPower+' dBm');
  const statusLabel=context.limit_profile?.lifecycle==='draft'?'DRAFT PASS':context.limit_profile?'PASS':uiText('已量測','Measured');
  // PASS 分母是「有效點數」而非全部點數：無效點沒有做過規格判定，不該被算進去。
  const validCount=points.filter(point=>point.valid).length;
  const invalidCount=points.length-validCount;
  const statusCount=context.limit_profile?pass:measured;
  const statusTotal=context.limit_profile?validCount:points.length;
  latestSpecLimitDb=context.limit_profile?context.limit_profile.maximum_evm_db:null;
  latestP1db=context.p1db||null;
  // margin = limit - measured，正值代表優於限值；此符號約定與 backend 的 margin_db 相同。
  const margins=points.filter(point=>point.valid&&Number.isFinite(point.margin_db)).map(point=>point.margin_db);
  const avgMargin=margins.length?margins.reduce((sum,value)=>sum+value,0)/margins.length:null;
  const worstMargin=margins.length?Math.min(...margins):null;
  const signed=value=>(value>0?'+':'')+value.toFixed(2)+' dB';
  const powerStats=powerFlatnessStats(points),isGprf=context.measurement_family==='GPRF_POWER';
  // Demo 與實機共用 PA 欄位契約；只要結果含 Gain，就顯示 PA 摘要，不以量測來源阻擋 P1dB。
  const hasPa=source.some(point=>point&&Object.hasOwn(point,'gain_db'));
  $('#metrics').innerHTML=hasPa?paSummaryMetrics(points,axis,context.p1db)+metric(fixedLabel,fixedValue):isGprf&&powerStats
    ? metric(uiText('Analyzer 平均功率（dBm 算術平均）','Mean analyzer power (dBm arithmetic mean)'),powerStats.avgMeasured.toFixed(3)+' dBm')
    +metric(uiText('Analyzer 平均期望功率','Mean expected analyzer power'),powerStats.avgExpected.toFixed(3)+' dBm')
    +metric(uiText('平均誤差','Mean error'),(powerStats.meanError>=0?'+':'')+powerStats.meanError.toFixed(3)+' dB')
    +metric(uiText('最大絕對誤差','Max |Error|'),powerStats.maxAbsError.toFixed(3)+' dB')
    +metric(uiText('Analyzer 誤差峰對峰漣波','Analyzer error peak-to-peak ripple'),powerStats.ripple.toFixed(3)+' dB')
    +metric(uiText('Analyzer 誤差標準差','Analyzer error standard deviation'),powerStats.stdDev.toFixed(3)+' dB')
    +metric(uiText('有效點','Valid'),`${powerStats.valid}/${powerStats.total}`)
    +metric(fixedLabel,fixedValue)
    : metric(uiText('平均 EVM','Avg EVM'),avg===null?'—':avg.toFixed(2)+' dB')
    +metric(uiText('最差 EVM','Worst EVM'),worst===null?'—':worst.toFixed(2)+' dB')
    +metric(uiText('規格限值','Spec Limit'),latestSpecLimitDb===null?'—':latestSpecLimitDb.toFixed(2)+' dB')
    +metric(uiText('平均餘裕','Avg Margin'),avgMargin===null?'—':signed(avgMargin))
    +metric(uiText('最差餘裕','Worst Margin'),worstMargin===null?'—':signed(worstMargin))
    +metric(statusLabel,`${statusCount}/${statusTotal}`)
    +metric(uiText('無效點','Invalid'),`${invalidCount}`)
    +metric(fixedLabel,fixedValue);
  // 只有真的存在 INVALID 點才提示，避免讓操作員誤以為本次量測含無效資料。
  const hint=$('#chartHint');
  if(hint&&hasPa)hint.textContent=language==='zh'?'PA Gain = Pout − Pin；摘要排除 INVALID。not_found 表示有效範圍內未觀察到 1 dB 壓縮；insufficient_points 表示資料不足。':'PA Gain = Pout − Pin; summary excludes INVALID. not_found: no observed 1 dB compression; insufficient_points: insufficient data.';
  else if(hint&&isGprf)hint.textContent=language==='zh'
    ?'GPRF power：藍線是量測功率，橘色虛線是 Expected power；Power Error = measured - expected'
    :'GPRF power: blue is measured power, orange dashed line is expected power; Power Error = measured - expected';
  else if(hint)hint.textContent=invalidCount
    ?(language==='zh'?'EVM dB 越負通常越好；PASS 區在 limit line 下方；INVALID 不與有效點連線':'Lower (more negative) EVM is better; PASS zone is below the limit line; INVALID points are not connected')
    :(language==='zh'?'EVM dB 越負通常越好；PASS 區在 limit line 下方':'Lower (more negative) EVM is better; PASS zone is below the limit line');
  renderLimitProfile(context.limit_profile,context.compliance_claim);
  // PA 使用明確參考面欄位；避免把 Analyzer 功率當作 DUT 輸出或空白 EVM 誤當量測失敗。
  const header=$('#resultRows').closest('table').querySelector('thead tr');
  header.innerHTML=`<th>#</th><th id="xAxisHeader">${xUnitFor(axis)}</th>`+(hasPa
    ?`<th>PA Pin (dBm)</th><th>PA Pout (dBm)</th><th>PA Gain (dB)</th><th>Analyzer (dBm)</th><th>${uiText('狀態','Status')}</th>`
    :`<th>EVM (dB)</th><th>Power (dBm)</th><th>Power Error (dB)</th><th>Freq Error (Hz)</th><th>${uiText('狀態','Status')}</th>`);
  if(hasPa){
    $('#resultRows').innerHTML=points.map(point=>`<tr><td>${point.point_index+1}</td><td>${Number.isFinite(point[xField])?xDisplayFor(axis,point[xField]):'—'}</td><td>${formatMeasured(point.pin_dbm)}</td><td>${formatMeasured(point.pout_dbm)}</td><td>${formatMeasured(point.gain_db,3)}</td><td>${formatMeasured(point.burst_power_dbm)}</td><td class="${String(point.limit_status||'').toLowerCase()}">${escapeHtml(point.limit_status||'—')}</td></tr>`).join('');
    return;
  }
  // INV／null 是量測無效訊號，表格以破折號呈現，不得補零或讓前端拋出例外。
  $('#resultRows').innerHTML=points.map(point=>`<tr><td>${point.point_index+1}</td><td>${Number.isFinite(point[xField])?xDisplayFor(axis,point[xField]):'—'}</td><td>${formatMeasured(point.evm_all_db)}</td><td>${formatMeasured(point.burst_power_dbm)}</td><td>${formatMeasured(point.power_error_db,3)}</td><td>${formatMeasured(point.frequency_error_hz)}</td><td class="${String(point.limit_status||'').toLowerCase()}">${escapeHtml(point.limit_status||'—')}</td></tr>`).join('');
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
  const validCount=latest.filter(point=>point.valid===true).length;
  resultViewState={mode:'current',runId:data.artifacts.run_id,pointCount:latest.length,simulated:Boolean(data.simulated),status:String(data.status||'complete').toLowerCase(),validCount,invalidCount:latest.length-validCount};
  renderResultViewState();
  renderResultSummary(latest,latestAxis,data,data.points);
  const urls=data.artifact_urls||{};
  $('#artifacts').innerHTML=['csv','json','report'].filter(key=>urls[key]).map(key=>`<a href="${urls[key]}" target="_blank" rel="noopener">${key==='report'?'HTML':key.toUpperCase()}</a>`).join(' · ');
  renderMatplotlibGallery(urls);
  drawChart(latest,latestAxis);
}
function renderLimitProfile(profile,complianceClaim){const card=$('#limitProfileCard');if(!profile){card.hidden=true;return}card.hidden=false;const warning=complianceClaim?'APPROVED':'DRAFT · NOT A DUT COMPLIANCE CLAIM';card.innerHTML=`<strong>${escapeHtml(profile.profile_id)} · ${escapeHtml(profile.revision)}</strong><span class="pill ${complianceClaim?'hardware-source':'draft-limit'}">${warning}</span><p>EVM ≤ ${profile.maximum_evm_db} dB · |Frequency Error| ≤ ${profile.maximum_absolute_frequency_error_hz} Hz · |Power Error| ≤ ${profile.maximum_absolute_power_error_db} dB</p>`}
function metric(label,value){return `<div class="metric"><small>${label}</small><strong>${value}</strong></div>`}
function metricAxisLabel(metricName){return {evm_all_db:'EVM All (dB)',evm_data_db:'EVM Data (dB)',evm_pilot_db:'EVM Pilot (dB)',burst_power_dbm:'Burst Power (dBm)',pin_dbm:'PA Pin (dBm)',pout_dbm:'PA Pout (dBm)',gain_db:'PA Gain (dB)',power_error_db:'Power Error (dB)',peak_power_dbm:'Peak Power (dBm)',frequency_error_hz:'Frequency Error (Hz)',clock_error_ppm:'Clock Error (ppm)'}[metricName]||metricName}
const metricOrder=['evm_all_db','evm_data_db','evm_pilot_db','burst_power_dbm','pin_dbm','pout_dbm','gain_db','power_error_db','peak_power_dbm','frequency_error_hz','clock_error_ppm'];
function updateChartMetricAvailability(points){
  const select=$('#chartMetric');
  [...select.options].forEach(option=>{const available=points.some(point=>Number.isFinite(point[option.value]));option.disabled=!available;option.hidden=!available});
  if(select.selectedOptions[0]?.disabled)select.value=[...select.options].find(option=>!option.disabled)?.value||'';
}
function selectBestChartMetric(points,data={}){
  // 新結果進來時只自動選一次最有趨勢意義的指標；使用者之後手動切換不會重算資料。
  updateChartMetricAvailability(points);
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
  const preferred='matplotlib_'+$('#chartMetric').value;
  const current=plots.some(([key])=>key===preferred)?preferred:select.value&&plots.some(([key])=>key===select.value)?select.value:plots[0][0];
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
const chartFrame={width:900,height:410,left:104,right:52,top:28,bottom:82};
const chartZoomLimits={minWidth:18,minHeight:18};
const chartManualRange={xmin:null,xmax:null,ymin:null,ymax:null};
function clampChartX(x,width=chartView.width){
  // 縮小最多回到完整圖，避免 viewBox 大於圖面後把曲線縮到像消失。
  if(width>=chartFrame.width)return 0;
  return Math.max(0,Math.min(chartFrame.width-width,x));
}
function clampChartY(y,height=chartView.height){
  // Y 軸也限制在資料全域範圍內，讓拖曳不會把所有測點帶離畫布。
  if(height>=chartFrame.height)return 0;
  return Math.max(0,Math.min(chartFrame.height-height,y));
}
function syncChartViewportSize(){
  const svg=$('#chart');
  chartView.x=clampChartX(chartView.x,chartView.width);chartView.y=clampChartY(chartView.y,chartView.height);
  // 畫布與座標軸固定；縮放只改變資料範圍，避免瀏覽器等比縮放造成左右裁切。
  svg.setAttribute('viewBox',`0 0 ${chartFrame.width} ${chartFrame.height}`);
  svg.style.aspectRatio=`${chartFrame.width} / ${chartFrame.height}`;
}
function setChartNaturalView(points=[]){
  // 圖表尺寸集中由 chartFrame 管理，避免 SVG viewBox 與互動縮放範圍不同步。
  Object.assign(chartView,{x:0,y:0,width:chartFrame.width,height:chartFrame.height});
  syncChartViewportSize();
}
function chartDataWindow(xmin,xmax,samples){
  const span=xmax-xmin||1;
  const low=xmin+chartView.x/chartFrame.width*span,high=low+chartView.width/chartFrame.width*span;
  // 最小視窗涵蓋最大相鄰有效點距離，拖到邊界仍保留有效測點。
  const positions=[xmin,...samples.map(point=>point.x),xmax].filter(Number.isFinite).sort((a,b)=>a-b);
  const gap=Math.max(0,...positions.slice(1).map((value,index)=>value-positions[index]));
  chartZoomLimits.minWidth=Math.max(18,Math.min(chartFrame.width,gap/span*chartFrame.width*1.05));
  const visible=samples.filter(point=>point.x>=low&&point.x<=high);
  return {xmin:low,xmax:high,ys:(visible.length?visible:samples).map(point=>point.y)};
}
function chartClipMarkup(){
  // 只裁切資料層；軸標題與刻度永遠留在圖框外的固定位置。
  const f=chartFrame;
  return `<defs><clipPath id="chartDataClip"><rect x="${f.left-6}" y="${f.top-6}" width="${f.width-f.left-f.right+12}" height="${f.height-f.top-f.bottom+12}"/></clipPath></defs><g clip-path="url(#chartDataClip)">`;
}
function axisTickLabel(axis,value){return axis==='frequency'?(value/1e6).toLocaleString(undefined,{maximumFractionDigits:3}):Number(value).toFixed(1)}
function chartExtent(values,{minimumSpan=1,paddingRatio=.08}={}){
  const finite=values.filter(Number.isFinite),low=Math.min(...finite),high=Math.max(...finite);
  const midpoint=(low+high)/2,rawSpan=high-low,span=Math.max(rawSpan,minimumSpan);
  // Y 軸只加必要留白，讓小幅變化不會被壓扁；零跨度資料仍保留最小可讀範圍。
  return {min:midpoint-span/2-span*paddingRatio,max:midpoint+span/2+span*paddingRatio};
}
function chartYWindow(extent){
  const span=extent.max-extent.min||1,high=extent.max-chartView.y/chartFrame.height*span;
  return {min:high-chartView.height/chartFrame.height*span,max:high};
}
function p1dbChartMarker(axis,metric){
  const result=latestP1db||{};
  if(axis!=='power'||result.status!=='found')return null;
  const ip1db=finiteNumber(result.ip1db_dbm);
  if(ip1db===null)return null;
  if(metric==='pin_dbm')return {x:ip1db,y:ip1db,label:`IP1dB ${ip1db.toFixed(2)} dBm`};
  if(metric==='pout_dbm'){
    const op1db=finiteNumber(result.op1db_dbm);
    return op1db===null?null:{x:ip1db,y:op1db,label:`OP1dB ${op1db.toFixed(2)} dBm`};
  }
  if(metric==='gain_db'){
    const target=finiteNumber(result.target_gain_db);
    return target===null?null:{x:ip1db,y:target,label:`IP1dB ${ip1db.toFixed(2)} dBm`};
  }
  return null;
}
function p1dbMarkerMarkup(marker,x,y){
  if(!marker)return '';
  const cx=x(marker.x),cy=y(marker.y),labelY=cy<chartFrame.top+24?cy+24:cy-12,atRight=cx>chartFrame.width-chartFrame.right-150;
  return `<line class="p1db-guide" x1="${cx}" y1="${chartFrame.top}" x2="${cx}" y2="${chartFrame.height-chartFrame.bottom}"/><line class="p1db-guide" x1="${chartFrame.left}" y1="${cy}" x2="${cx}" y2="${cy}"/><circle class="p1db-marker" cx="${cx}" cy="${cy}" r="8"><title>${marker.label}</title></circle><text class="p1db-label" x="${cx+(atRight?-10:10)}" y="${labelY}" text-anchor="${atRight?'end':'start'}">${marker.label}</text>`;
}
function chartUserMarksMarkup(x,y){return chartView.marks.map(mark=>`<circle class="chart-user-mark" cx="${x(mark.x)}" cy="${y(mark.y)}" r="7"/><text class="chart-user-mark-label" x="${x(mark.x)+10}" y="${y(mark.y)-10}">${mark.label}</text>`).join('')}
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
function drawChart(points,axis='frequency',preserveView=false){
  if(!preserveView)setChartNaturalView();
  updateChartRangeLabels();
  const svg=$('#chart'),metric=$('#chartMetric').value,w=chartFrame.width,h=chartFrame.height,xField=xFieldFor(axis),xUnit=xUnitFor(axis),left=chartFrame.left,right=chartFrame.right,top=chartFrame.top,bottom=chartFrame.bottom;
  const xs=points.map(point=>point[xField]).filter(Number.isFinite);
  const validPoints=points.filter(point=>point.valid&&Number.isFinite(point[metric]));
  const ys=validPoints.map(point=>point[metric]);
  if(!xs.length||!ys.length){svg.innerHTML=`<text class="axis-label" x="450" y="150" text-anchor="middle">${uiText('此指標沒有有效數值；請查看結果表與執行狀態','No valid values for this metric; review the results and run status')}</text>`;return}
  // EVM 圖需要把 spec limit 一起納入 Y 範圍，否則 limit line 會被裁切在圖外。
  const specLimit=metric==='evm_all_db'&&Number.isFinite(latestSpecLimitDb)?latestSpecLimitDb:null;
  const expectedReference=expectedReferenceForPowerMetric(validPoints,axis,metric);
  const expectedSpread=expectedReference?.kind==='diagonal'?expectedReference.points.map(point=>point.y):expectedReference?[expectedReference.value]:[];
  const p1Marker=p1dbChartMarker(axis,metric);
  const spread=[...ys,...(specLimit===null?[]:[specLimit]),...expectedSpread,...(p1Marker?[p1Marker.y]:[])];
  const baseXMin=chartManualRange.xmin??Math.min(...xs),baseXMax=chartManualRange.xmax??Math.max(...xs),window=chartDataWindow(baseXMin,baseXMax,validPoints.map(point=>({x:point[xField],y:point[metric]})));
  const {xmin,xmax}=window,metricSpan=Math.max(...spread)-Math.min(...spread);
  const minimumSpan=metric==='burst_power_dbm'||metric==='power_error_db'?0.18:metric==='frequency_error_hz'?Math.max(metricSpan,.5):0.5;
  const autoYExtent=chartExtent(chartView.width<chartFrame.width?window.ys:spread,{minimumSpan:chartView.width<chartFrame.width?.02:minimumSpan,paddingRatio:.1}),baseYExtent={min:chartManualRange.ymin??autoYExtent.min,max:chartManualRange.ymax??autoYExtent.max},yExtent=chartYWindow(baseYExtent),ymin=yExtent.min,ymax=yExtent.max;
  const x=value=>left+(value-xmin)/(xmax-xmin||1)*(w-left-right),y=value=>h-bottom-(value-ymin)/(ymax-ymin||1)*(h-top-bottom);
  let html=chartAxisMarkup(axis,metric,xmin,xmax,ymin,ymax,x,y)+chartClipMarkup();
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
  html+=validPoints.map(point=>{const tip=`x=${xDisplayFor(axis,point[xField])} ${xUnit} | ${metric}=${point[metric].toFixed(3)} | Pin=${formatMeasured(point.pin_dbm)} dBm | Pout=${formatMeasured(point.pout_dbm)} dBm | Gain=${formatMeasured(point.gain_db)} dB | EVM=${formatMeasured(point.evm_all_db)} dB | Power=${formatMeasured(point.burst_power_dbm)} dBm | Error=${formatMeasured(point.power_error_db,3)} dB | FreqErr=${formatMeasured(point.frequency_error_hz)} Hz | ${point.limit_status}`;return `<circle class="plot-dot" data-chart-point="true" data-chart-x="${point[xField]}" data-chart-y="${point[metric]}" data-tooltip="${escapeHtml(tip)}" cx="${x(point[xField])}" cy="${y(point[metric])}" r="4"><title>${escapeHtml(tip)}</title></circle>`}).join('');
  html+=p1dbMarkerMarkup(p1Marker,x,y)+chartUserMarksMarkup(x,y);
  // 無效點固定畫在圖底並標示叉號，保留其頻率／功率位置且不偽造 Y 值。
  html+=points.filter(point=>!point.valid||!Number.isFinite(point[metric])).map(point=>`<g class="plot-invalid" transform="translate(${x(point[xField])},${h-bottom})"><path d="M-5-5L5 5M5-5L-5 5"/><title>${xDisplayFor(axis,point[xField])} ${xUnit} · INVALID</title></g>`).join('');
  svg.innerHTML=html+'</g>';
  syncChartViewportSize();
  updateExportAvailability();
}
function drawAnalysisChart(preserveView=false){
  if(!preserveView)setChartNaturalView();
  updateChartRangeLabels();
  const visible=analysisTraces.filter(trace=>trace.visible);
  if(!visible.length){$('#chart').innerHTML='';return}
  const metricName=$('#chartMetric').value,w=chartFrame.width,h=chartFrame.height,left=chartFrame.left,right=chartFrame.right,top=chartFrame.top,bottom=chartFrame.bottom,samples=[];
  visible.forEach(trace=>trace.points.forEach(point=>{const xValue=point[xFieldFor(trace.axis)],yValue=point[metricName];if(point.valid&&Number.isFinite(xValue)&&Number.isFinite(yValue))samples.push({x:xValue,y:yValue})}));
  if(!samples.length){$('#chart').innerHTML=`<text class="axis-label" x="45" y="70">${language==='zh'?'此指標沒有可比較的有效數值':'No comparable values for this metric'}</text>`;return}
  const referenceLines=visible.map(trace=>({trace,reference:expectedReferenceForPowerMetric(trace.points.filter(point=>point.valid),trace.axis,metricName)})).filter(item=>item.reference);
  const referenceSpread=referenceLines.flatMap(item=>item.reference.kind==='diagonal'?item.reference.points.map(point=>point.y):[item.reference.value]);
  // X 軸仍含 INVALID 的位置，Y 軸只用有效值；失敗點不應消失或擴大增益範圍。
  const allXs=visible.flatMap(trace=>trace.points.map(point=>point[xFieldFor(trace.axis)])).filter(Number.isFinite);
  const baseXMin=chartManualRange.xmin??Math.min(...allXs),baseXMax=chartManualRange.xmax??Math.max(...allXs),window=chartDataWindow(baseXMin,baseXMax,samples);
  const comparisonMarker=visible.length===1?p1dbChartMarker(visible[0].axis,metricName):null;
  const {xmin,xmax}=window,spread=[...samples.map(sample=>sample.y),...referenceSpread,...(comparisonMarker?[comparisonMarker.y]:[])],metricSpan=Math.max(...spread)-Math.min(...spread);
  const minimumSpan=metricName==='burst_power_dbm'||metricName==='power_error_db'?0.18:metricName==='frequency_error_hz'?Math.max(metricSpan,.5):0.5;
  const autoYExtent=chartExtent(chartView.width<chartFrame.width?window.ys:spread,{minimumSpan:chartView.width<chartFrame.width?.02:minimumSpan,paddingRatio:.1}),baseYExtent={min:chartManualRange.ymin??autoYExtent.min,max:chartManualRange.ymax??autoYExtent.max},yExtent=chartYWindow(baseYExtent),ymin=yExtent.min,ymax=yExtent.max,x=value=>left+(value-xmin)/(xmax-xmin||1)*(w-left-right),y=value=>h-bottom-(value-ymin)/(ymax-ymin||1)*(h-top-bottom);
  const axes=new Set(visible.map(trace=>trace.axis)),comparisonAxis=axes.size===1?visible[0].axis:'frequency';
  let html=chartAxisMarkup(comparisonAxis,metricName,xmin,xmax,ymin,ymax,x,y)+chartClipMarkup();
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
  visible.forEach(trace=>{const xField=xFieldFor(trace.axis),dash=trace.lineStyle==='dash'?'10 7':trace.lineStyle==='dot'?'2 6':'none';let segment=[];const flush=()=>{if(segment.length){html+=`<polyline fill="none" stroke="${trace.color}" stroke-width="3" stroke-dasharray="${dash}" stroke-linecap="round" points="${segment.map(point=>`${x(point[xField])},${y(point[metricName])}`).join(' ')}"/>`;segment=[]}};trace.points.forEach(point=>{const valid=point.valid&&point[xField]!==null&&Number.isFinite(point[metricName]);if(valid)segment.push(point);else flush()});flush();trace.points.forEach(point=>{if(!Number.isFinite(point[xField]))return;if(!point.valid||!Number.isFinite(point[metricName])){html+=`<g class="plot-invalid" transform="translate(${x(point[xField])},${h-bottom})"><path d="M-5-5L5 5M5-5L-5 5"/><title>${escapeHtml(trace.name)} · INVALID</title></g>`;return}const cx=x(point[xField]),cy=y(point[metricName]),fill=point.valid?trace.color:'#f05261',title=`${trace.name} | x=${point[xField]} | ${metricName}=${point[metricName]} | EVM=${point.evm_all_db} dB | Power=${point.burst_power_dbm} dBm | FreqErr=${point.frequency_error_hz} Hz | ${point.valid?'VALID':'INVALID'}`,shape=trace.pointShape==='square'?`<rect x="${cx-4}" y="${cy-4}" width="8" height="8" rx="1"`:trace.pointShape==='diamond'?`<polygon points="${cx},${cy-5} ${cx+5},${cy} ${cx},${cy+5} ${cx-5},${cy}"`:`<circle cx="${cx}" cy="${cy}" r="4"`;html+=`${shape} data-chart-point="true" data-chart-x="${point[xField]}" data-chart-y="${point[metricName]}" data-tooltip="${escapeHtml(title)}" fill="${fill}" stroke="${trace.color}"><title>${escapeHtml(title)}</title></${trace.pointShape==='square'?'rect':trace.pointShape==='diamond'?'polygon':'circle'}>`})});
  html+=p1dbMarkerMarkup(comparisonMarker,x,y)+chartUserMarksMarkup(x,y);
  $('#chart').innerHTML=html+'</g>';
  syncChartViewportSize();
  updateExportAvailability();
}
$('#chartMetric').onchange=()=>{chartView.marks=[];analysisTraces.length?drawAnalysisChart():(latest.length&&drawChart(latest,latestAxis))};
function downloadBlob(filename,blob){const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=filename;link.click();setTimeout(()=>URL.revokeObjectURL(url),0)}
// A08：圖表沒有任何測點時不得匯出，避免產生空白但看似正式的報告檔。
function chartHasExportableData(){return analysisTraces.length?analysisTraces.some(trace=>trace.points.length):latest.length>0}
function updateExportAvailability(){const ready=chartHasExportableData();['#exportSvg','#exportPng','#exportCompareCsv'].forEach(selector=>{const button=$(selector);if(!button)return;if(button.dataset.exportTitle===undefined)button.dataset.exportTitle=button.title;button.disabled=!ready;button.title=ready?button.dataset.exportTitle:(language==='zh'?'目前沒有可匯出的測點':'No measured points to export')})}
$('#exportSvg').onclick=()=>{if(!chartHasExportableData())return;const svg=$('#chart').cloneNode(true);svg.setAttribute('xmlns','http://www.w3.org/2000/svg');downloadBlob('cmp180-comparison.svg',new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml'}))};
$('#exportPng').onclick=()=>{if(!chartHasExportableData())return;const svg=$('#chart').cloneNode(true);svg.setAttribute('xmlns','http://www.w3.org/2000/svg');const blob=new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml'}),url=URL.createObjectURL(blob),image=new Image();image.onload=()=>{const canvas=document.createElement('canvas');canvas.width=1800;canvas.height=780;const context=canvas.getContext('2d');context.fillStyle=getComputedStyle(document.documentElement).getPropertyValue('--console-surface')||'#fff';context.fillRect(0,0,canvas.width,canvas.height);context.drawImage(image,0,0,canvas.width,canvas.height);canvas.toBlob(png=>{if(png)downloadBlob('cmp180-comparison.png',png)},'image/png');URL.revokeObjectURL(url)};image.src=url};
$('#exportCompareCsv').onclick=()=>{if(!chartHasExportableData())return;const metricName=$('#chartMetric').value,rows=[['trace','valid','frequency_hz','generator_power_dbm',metricName,'measurement_state']];(analysisTraces.length?analysisTraces:[{name:'current',points:latest}]).forEach(trace=>trace.points.forEach(point=>rows.push([trace.name,point.valid,point.frequency_hz,point.generator_power_dbm,point[metricName],point.measurement_state])));const csv=rows.map(row=>row.map(value=>`"${String(value??'').replaceAll('"','""')}"`).join(',')).join('\r\n');downloadBlob('cmp180-comparison.csv',new Blob([csv],{type:'text/csv;charset=utf-8'}))};
updateExportAvailability();
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
$('#chart').addEventListener('pointermove',event=>{const svg=$('#chart'),points=[...svg.querySelectorAll('[data-chart-point]')];if(!points.length||chartView.drag)return;let nearest=null,distance=Infinity;points.forEach(point=>{const box=point.getBoundingClientRect(),dx=event.clientX-(box.left+box.width/2),dy=event.clientY-(box.top+box.height/2),candidate=Math.hypot(dx,dy);if(candidate<distance){distance=candidate;nearest=point}});svg.querySelectorAll('.chart-crosshair,.chart-focus-ring').forEach(item=>item.remove());if(!nearest||distance>64){clearHoverPoint();return}const ns='http://www.w3.org/2000/svg',center=chartPointCenter(nearest),vertical=document.createElementNS(ns,'line'),horizontal=document.createElementNS(ns,'line'),ring=document.createElementNS(ns,'circle');vertical.setAttribute('class','chart-crosshair');vertical.setAttribute('x1',center.x);vertical.setAttribute('x2',center.x);vertical.setAttribute('y1',chartFrame.top);vertical.setAttribute('y2',chartFrame.height-chartFrame.bottom);horizontal.setAttribute('class','chart-crosshair');horizontal.setAttribute('x1',chartFrame.left);horizontal.setAttribute('x2',chartFrame.width-chartFrame.right);horizontal.setAttribute('y1',center.y);horizontal.setAttribute('y2',center.y);ring.setAttribute('class','chart-focus-ring');ring.setAttribute('cx',center.x);ring.setAttribute('cy',center.y);ring.setAttribute('r','9');svg.append(vertical,horizontal,ring);const readout=$('#chartCursorReadout'),pointText=nearest.dataset.tooltip||'';readout.hidden=false;readout.textContent=pointText;chartTooltip.innerHTML=`<strong>${language==='zh'?'量測點數值':'Measurement values'}</strong>${escapeHtml(pointText).replaceAll(' | ','<br>')}`;const cardElement=document.querySelector('.chart-card'),card=cardElement.getBoundingClientRect(),readoutBox=readout.getBoundingClientRect(),tooltipWidth=Math.min(460,card.width-24),fixedTop=Math.max(8,readoutBox.bottom-card.top+10);chartTooltip.style.maxWidth=`${tooltipWidth}px`;chartTooltip.style.left=`${Math.max(8,Math.min(event.clientX-card.left,card.width-tooltipWidth-24))}px`;chartTooltip.style.top=`${fixedTop}px`;chartTooltip.hidden=false});
$('#chart').addEventListener('pointerleave',clearHoverPoint);

// 架構節點只切換說明，不呼叫任何儀器 API，也不會改變 RF 狀態。
const architectureCopy={
  zh:{plan:'設定量測類型、頻率、頻寬與功率，建立待檢查的計畫。',safety:'後端檢查參數與操作員提交的接線確認；軟體無法判斷實際線材是否接妥。',instrument:'量測流程在結束或例外時嘗試停止量測並關閉 RF，並記錄收尾錯誤；異常時仍須由現場操作員確認儀器狀態。',result:'解析原始回應並標示有效性；圖表不連接 INVALID 點，未核准判定門檻時不宣稱 PASS。',artifact:'依執行結果提供可用檔案。中止或失敗時可能只有部分結果；啟動前被拒絕的計畫不代表已完成量測。'},
  en:{plan:'Set measurement type, frequency, bandwidth and power to build a plan for review.',safety:'The server checks parameters and submitted wiring confirmations; software cannot verify physical cable connections.',instrument:'On completion or exceptions, the workflow attempts measurement stop and RF off and records cleanup errors. An on-site operator must confirm instrument state after a failure.',result:'Parse raw responses and mark validity. Plots do not connect INVALID points; no PASS claim is made without approved limits.',artifact:'Available files depend on the execution outcome. Cancelled or failed runs may contain partial results; a plan rejected before execution is not a completed measurement.'}
};
function renderArchitectureDetail(){const key=document.querySelector('[data-architecture].active')?.dataset.architecture||'plan';$('#architectureDetail').textContent=architectureCopy[language][key]}
// 語言切換只更新節點說明，不重載圖表或送出量測請求。
window.addEventListener('cmp180-language-change',renderArchitectureDetail);
document.querySelectorAll('[data-architecture]').forEach(node=>node.addEventListener('click',()=>{document.querySelectorAll('[data-architecture]').forEach(item=>item.classList.toggle('active',item===node));renderArchitectureDetail()}));

// 首頁 iframe 僅載入 server 白名單內的兩份文件；播放與切換不會呼叫任何量測 API。
let activeDiagramPath='/diagrams/system-architecture.html';
function diagramPlaybackUrl(path){return `${path}?present=1&theme=${document.documentElement.dataset.theme==='light'?'light':'dark'}`}
document.querySelectorAll('[data-diagram-path]').forEach(button=>button.addEventListener('click',()=>{activeDiagramPath=button.dataset.diagramPath;document.querySelectorAll('[data-diagram-path]').forEach(item=>item.classList.toggle('active',item===button));$('#diagramShowcaseFrame').src=diagramPlaybackUrl(activeDiagramPath)}));
$('#restartDiagram').addEventListener('click',()=>{$('#diagramShowcaseFrame').src=diagramPlaybackUrl(activeDiagramPath)});
$('#openDiagram').addEventListener('click',()=>window.open(diagramPlaybackUrl(activeDiagramPath),'_blank','noopener'));

// 圖表檢視狀態只影響瀏覽器顯示；不重新量測，也不修改原始結果。
const chartView={x:0,y:0,width:chartFrame.width,height:chartFrame.height,drag:null,cursors:[],marks:[]};
function redrawActiveChart(){
  // 重繪時保留拖曳狀態，但移除舊像素座標游標，避免 A/B 標記指向錯誤測點。
  chartView.cursors=[];clearHoverPoint();
  analysisTraces.length?drawAnalysisChart(true):drawChart(latest,latestAxis,true);
  updateExportAvailability();
}
function resetChartView(){Object.assign(chartView,{x:0,y:0,width:chartFrame.width,height:chartFrame.height,drag:null,cursors:[],marks:[]});redrawActiveChart();$('#chartCursorReadout').hidden=true;$('#chart').querySelectorAll('.chart-ab-line,.chart-ab-label').forEach(item=>item.remove())}
function renderChartCursors(){const svg=$('#chart');svg.querySelectorAll('.chart-ab-line,.chart-ab-label').forEach(item=>item.remove());chartView.cursors.forEach((cursor,index)=>{const ns='http://www.w3.org/2000/svg',line=document.createElementNS(ns,'line'),label=document.createElementNS(ns,'text');line.setAttribute('class','chart-ab-line');line.setAttribute('x1',cursor.x);line.setAttribute('x2',cursor.x);line.setAttribute('y1',chartFrame.top);line.setAttribute('y2',chartFrame.height-chartFrame.bottom);label.setAttribute('class','chart-ab-label');label.setAttribute('x',cursor.x+5);label.setAttribute('y',chartFrame.top-5);label.textContent=index?'B':'A';svg.append(line,label)});const readout=$('#chartCursorReadout');if(chartView.cursors.length){readout.hidden=false;readout.textContent=chartView.cursors.map((cursor,index)=>`${index?'B':'A'}: ${cursor.label}`).join('  |  ')+(chartView.cursors.length===2?`  |  ΔX(view): ${Math.abs(chartView.cursors[1].x-chartView.cursors[0].x).toFixed(1)}`:'')}else readout.hidden=true}
function activeChartAxis(){return analysisTraces.filter(trace=>trace.visible)[0]?.axis||latestAxis}
function updateChartRangeLabels(){const axis=activeChartAxis();$('#chartXRangeLabel').textContent=`X (${xUnitFor(axis)})`;$('#chartYRangeLabel').textContent=`Y (${metricAxisLabel($('#chartMetric').value)})`}
function applyChartRange(){
  const values=['chartXMin','chartXMax','chartYMin','chartYMax'].map(id=>{const raw=$('#'+id).value.trim();return raw===''?null:Number(raw)});
  if(values.some(value=>value!==null&&!Number.isFinite(value))||((values[0]===null)!==(values[1]===null))||((values[2]===null)!==(values[3]===null)))throw new Error('Enter both minimum and maximum for each axis, or leave both empty for auto range.');
  if((values[0]!==null&&values[0]>=values[1])||(values[2]!==null&&values[2]>=values[3]))throw new Error('Range minimum must be smaller than maximum.');
  const axis=activeChartAxis();chartManualRange.xmin=values[0]===null?null:(axis==='frequency'?values[0]*1e6:values[0]);chartManualRange.xmax=values[1]===null?null:(axis==='frequency'?values[1]*1e6:values[1]);chartManualRange.ymin=values[2];chartManualRange.ymax=values[3];setChartNaturalView();redrawActiveChart();
}
$('#chartApplyRange').onclick=()=>{try{applyChartRange()}catch(error){toast(error.message,'error')}};
$('#chartAutoRange').onclick=()=>{Object.assign(chartManualRange,{xmin:null,xmax:null,ymin:null,ymax:null});['chartXMin','chartXMax','chartYMin','chartYMax'].forEach(id=>{$('#'+id).value=''});setChartNaturalView();redrawActiveChart()};
$('#chartReset').onclick=resetChartView;
$('#chartYExpand').onclick=()=>{zoomChartAt(.5,.5,1.5);redrawActiveChart()};
$('#chartYShrink').onclick=()=>{zoomChartAt(.5,.5,1/1.5);redrawActiveChart()};
$('#chartCursorMode').onclick=event=>{event.currentTarget.classList.toggle('active');toast(event.currentTarget.classList.contains('active')?{zh:'A/B 游標已啟用：點選圖上測點',en:'A/B cursors enabled: select measured points'}:{zh:'A/B 游標已關閉',en:'A/B cursors disabled'})};
$('#chartMarkMode').onclick=event=>{event.currentTarget.classList.toggle('active');toast(event.currentTarget.classList.contains('active')?{zh:'標記模式：點選測點加入 M 標記',en:'Mark mode: select measured points to add M marks'}:{zh:'標記模式已關閉',en:'Mark mode disabled'})};
function chartPointer(event){
  // 用 SVG 螢幕矩陣處理響應式尺寸與瀏覽器縮放，不以 DOM 寬度猜測圖內座標。
  const matrix=event.currentTarget.getScreenCTM();
  return matrix?new DOMPoint(event.clientX,event.clientY).matrixTransform(matrix.inverse()):null;
}
function zoomChartAt(xFraction,yFraction,factor){
  const nextWidth=Math.min(chartFrame.width,Math.max(chartZoomLimits.minWidth,chartView.width*factor));
  const nextHeight=Math.min(chartFrame.height,Math.max(chartZoomLimits.minHeight,chartView.height*factor));
  chartView.x=clampChartX(chartView.x+xFraction*(chartView.width-nextWidth),nextWidth);
  chartView.y=clampChartY(chartView.y+yFraction*(chartView.height-nextHeight),nextHeight);
  chartView.width=nextWidth;chartView.height=nextHeight;
}
$('#chart').addEventListener('wheel',event=>{
  const point=chartPointer(event),f=chartFrame;
  if(!point||point.x<f.left||point.x>f.width-f.right||point.y<f.top||point.y>f.height-f.bottom||!event.deltaY)return;
  event.preventDefault();
  zoomChartAt((point.x-f.left)/(f.width-f.left-f.right),(point.y-f.top)/(f.height-f.top-f.bottom),event.deltaY<0?1/1.2:1.2);redrawActiveChart();
},{passive:false});
$('#chart').addEventListener('pointerdown',event=>{
  if(event.button!==0)return;
  const position=chartPointer(event);if(!position)return;
  if($('#chartCursorMode').classList.contains('active')){
    const point=event.target.closest('[data-chart-point]');
    if(point){chartView.cursors.push({x:chartPointCenter(point).x,label:point.dataset.tooltip});if(chartView.cursors.length>2)chartView.cursors.shift();renderChartCursors()}return;
  }
  if($('#chartMarkMode').classList.contains('active')){
    const point=event.target.closest('[data-chart-point]');
    if(point){const x=Number(point.dataset.chartX),y=Number(point.dataset.chartY);if(Number.isFinite(x)&&Number.isFinite(y)){chartView.marks.push({x,y,label:`M${chartView.marks.length+1}`});if(chartView.marks.length>8)chartView.marks.shift();redrawActiveChart()}return}
  }
  const f=chartFrame;if(position.x<f.left||position.x>f.width-f.right||position.y<f.top||position.y>f.height-f.bottom)return;
  chartView.drag={pointerId:event.pointerId,startX:position.x,startY:position.y,x:chartView.x,y:chartView.y,width:chartView.width,height:chartView.height};
  event.currentTarget.setPointerCapture(event.pointerId);document.querySelector('.chart-card').classList.add('is-panning');
});
$('#chart').addEventListener('pointermove',event=>{
  const drag=chartView.drag;if(!drag||drag.pointerId!==event.pointerId)return;
  const position=chartPointer(event);if(!position)return;
  chartView.x=clampChartX(drag.x-(position.x-drag.startX)/(chartFrame.width-chartFrame.left-chartFrame.right)*drag.width);
  chartView.y=clampChartY(drag.y-(position.y-drag.startY)/(chartFrame.height-chartFrame.top-chartFrame.bottom)*drag.height);redrawActiveChart();
});
function finishChartDrag(event){
  // 放開、系統取消與失去捕捉都結束拖曳，避免滑鼠離開後圖仍黏著游標。
  if(chartView.drag&&event.pointerId!==chartView.drag.pointerId)return;
  chartView.drag=null;document.querySelector('.chart-card').classList.remove('is-panning');
  if(event.currentTarget.hasPointerCapture(event.pointerId))event.currentTarget.releasePointerCapture(event.pointerId);
}
['pointerup','pointercancel','lostpointercapture'].forEach(name=>$('#chart').addEventListener(name,finishChartDrag));
$('#chart').addEventListener('dblclick',resetChartView);
const sunIcon='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>';
const moonIcon='<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.7 15.3A8.7 8.7 0 0 1 9.7 4.3a.6.6 0 0 0-.75-.8A10 10 0 1 0 21.5 16a.6.6 0 0 0-.8-.7z"/></svg>';
let theme=localStorage.getItem('cmp180-theme')||'dark';
let capabilityProfile=null,capabilityError='';
function updateThemeLabel(){const label=document.documentElement.dataset.theme==='dark'?uiText('切換至亮色模式','Switch to light theme'):uiText('切換至暗色模式','Switch to dark theme');$('#themeButton').title=label;$('#themeButton').setAttribute('aria-label',label)}
function applyTheme(){document.documentElement.dataset.theme=theme;$('#themeButton').innerHTML=theme==='dark'?sunIcon:moonIcon;updateThemeLabel();const frame=$('#diagramShowcaseFrame');if(frame)frame.src=diagramPlaybackUrl(activeDiagramPath);}
$('#themeButton').onclick=()=>{theme=theme==='dark'?'light':'dark';localStorage.setItem('cmp180-theme',theme);applyTheme()};
applyTheme();
applyLanguage();
// 預先讀取紀錄，切換到紀錄頁時可立即顯示；這是唯讀 API，不會啟動量測或 RF。
function formatMHz(value){return Number.isFinite(Number(value))?`${Number(value)/1e6} MHz`:'—'}
function formatGHzRange(layer){return layer?`${Number(layer.frequency_min_hz)/1e9}–${Number(layer.frequency_max_hz)/1e9} GHz`:'—'}
function renderCapabilityProfile(){
  const body=$('#capabilityRows');
  if(capabilityError){body.innerHTML=`<tr><td colspan="5">${escapeHtml(uiText('無法載入能力資料：','Unable to load capability data: ')+capabilityError)}</td></tr>`;return;}
  if(!capabilityProfile){body.innerHTML=`<tr><td colspan="5">${uiText('正在載入能力資料…','Loading capability data…')}</td></tr>`;return;}
  const {catalog,installed,approved_profile:approved,verified_hil:hil}=capabilityProfile,approvedSections=approved.sections.map(section=>section.key);
  const rows=[
    [uiText('RF 頻率','RF frequency'),formatGHzRange(catalog),formatGHzRange(installed),formatGHzRange(approved),hil.frequencies_hz.map(formatMHz).join(', ')],
    [uiText('分析頻寬','Analysis bandwidth'),`≤ ${formatMHz(catalog.maximum_analysis_bandwidth_hz)}`,installed.analysis_bandwidths_hz.map(formatMHz).join(', '),approved.bandwidths_hz.map(formatMHz).join(', '),hil.bandwidths_hz.map(formatMHz).join(', ')],
    [uiText('WLAN 區段','WLAN sections'),'2.4 / 5 / 6 GHz',uiText('2.4 / 5 / 6 GHz 波形集','2.4 / 5 / 6 GHz waveform pool'),approvedSections.join(', '),hil.sections.join(', ')],
    [uiText('RF 資源','RF resources'),`${catalog.generator_count} VSG / ${catalog.analyzer_count} VSA / ${catalog.rf_port_count} ${uiText('埠','ports')}`,`${installed.generator_count} VSG / ${installed.analyzer_count} VSA / ${installed.rf_ports.length} ${uiText('埠','ports')}`,approved.routes.join(', '),hil.routes.join(', ')],
    [uiText('Generator 功率','Generator power'),uiText('依 RF 埠、選件與路徑而定','Depends on RF port, options, and path'),uiText('須依已安裝選件與 RF 埠確認','Confirm from installed options and RF port'),`${approved.generator_power_min_dbm}–${approved.generator_power_max_dbm} dBm`,hil.generator_powers_dbm.join(', ')+' dBm'],
    [uiText('掃描控制','Sweep control'),catalog.supports_list_mode?uiText('型錄列有 List mode','List mode listed in catalog'):'—',uiText('本機能力待探索確認','Local capability pending discovery'),`≤ ${approved.maximum_points} ${uiText('點','points')}; ${approved.dwell_min_ms}–${approved.dwell_max_ms} ms`,`${hil.dwell_ms.join(', ')} ms`]
  ];
  body.innerHTML=rows.map(row=>`<tr>${row.map(value=>`<td>${escapeHtml(value)}</td>`).join('')}</tr>`).join('');
  $('#capabilityGate').textContent=language==='zh'?`RF 執行設定：${approved.profile_id}；其中 ${approvedSections.length} 個 WLAN 區段已有 HIL 紀錄。`:`RF execution profile: ${approved.profile_id}. ${approvedSections.length} WLAN sections have HIL records.`;
}
renderCapabilityProfile();
fetch('/api/capabilities').then(async response=>{const data=await response.json();if(!response.ok)throw new Error(data.error||`HTTP ${response.status}`);capabilityProfile=data;renderCapabilityProfile()}).catch(error=>{capabilityError=String(error.message||error);renderCapabilityProfile()});
loadRunHistory();
document.querySelectorAll('[data-copy-target]').forEach(button=>button.addEventListener('click',async()=>{const target=document.getElementById(button.dataset.copyTarget);try{await navigator.clipboard.writeText(target.innerText.replaceAll('PS ','').trim());toast(language==='zh'?'指令已複製':'Command copied')}catch(error){toast(language==='zh'?'無法複製，請手動選取指令':'Copy failed; select the command manually','error')}}));
