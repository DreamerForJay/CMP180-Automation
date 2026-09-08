# CMP180 專案交接 / Project Handoff

## 中文版本

### 狀態（2026-08-27）

- 2026-09-03 完成 11 個 approved Loopback 代表點的升級後回歸：每點 Repeat=10，共 110/110 valid；11/11 均為 approved lifecycle、Stability PASS、Reasonableness PASS、`LOOPBACK_READY`，逐份 metadata 為 final RF OFF、measurement RDY、cleanup error 空。正式 artifact 範圍為 `output/20260903T111307Z_loopback-validation_3d788aaab7` 至 `output/20260903T111527Z_loopback-validation_582aded41f`，完整 case 對照見 `docs/loopback-validation.md`。同批完成 Web 檢查計畫中英即時切換：SingleShot、WLAN Sweep、GPRF、Loopback、HIL Campaign 與 Calibration 的步驟、Preview、安全原因／修正方式與最後確認均跟隨語言；切換只重繪既有資料，不呼叫 RF。軟體驗證為 282 tests、兩份 YAML validation 與 `git diff --check` 通過。

- 2026-09-03 新增 Loopback「一鍵執行全部」：涵蓋 11 個 approved WLAN section 代表點、每點 Repeat=10，共 110 次獨立 SingleShot，逐 profile 保存 artifact，SCPI／cleanup error 即停止。實機批次已完成 110/110 valid；11 個案例均 Stability PASS、Reasonableness PASS/DRAFT_PASS，final RF OFF、measurement RDY、cleanup error 空。十個新代表點已使用各自 artifact 升級為 approved profile；既有 6 GHz／320 MHz 維持原核准證據。未涵蓋的 route／UD Box 仍 blocked。

- 2026-09-03 以正式 Loopback Web 頁完成第一份 Repeat=10 實機 HIL：RF1.1 → RF1.5、6105 MHz、320 MHz、−40 dBm。10/10 valid，Stability PASS，Reasonableness DRAFT_PASS；EVM／Power／Frequency Error sample std 為 0.03178 dB／0.000604 dB／9.3989 Hz。Repeat 1 frequency error 為 IQR outlier，但仍有效並保留。Artifact 為 `output/20260903T101748Z_loopback-validation_865ca580c5`；final RF OFF、measurement RDY、cleanup error 空。依此證據將完全相同條件與至少 10 repeats 升級為 approved profile；核准後回歸 artifact `output/20260903T102312Z_loopback-validation_76df94aae2` 為 10/10 valid、Stability/Reasonableness PASS、`LOOPBACK_READY`。其他輸入仍為 draft。

- 2026-09-03 新增獨立 Loopback Web 頁、非同步 hardware job、完成 cleanup 後的即時三指標趨勢與 INVALID／IQR outlier 標示。每個 repeat 真正呼叫完整 SingleShot；invalid 保留並繼續，SCPI／cleanup error 才停止。新增 sample statistics、Validity／Stability／Reasonableness／Overall 分層與可追溯 artifacts。本批只使用單元／Mock 測試，沒有執行新的 CMP180 RF measurement；Repeat=10 HIL 仍待現場執行。

- 2026-09-03 完成 Web 結果與首頁整合修正：新 SingleShot／Frequency Sweep／Power Sweep
  在保存 CSV 後自動以 Pandas DataFrame＋Matplotlib Agg 產生 PNG，結果頁改為用選單切換
  單張 Matplotlib 預覽與原圖連結，不再一次鋪出四張；功率掃描 PNG 會使用變動的
  Generator Power (dBm) 作為 X 軸。Web SVG 圖改為獨立 X/Y 軸標題、工程單位、六組刻度、
  安全邊界、hover 十字游標、A/B 游標與滑鼠拖曳水平平移，不再與端點文字重疊。實機
  SingleShot 新增 CMP180 400–8000 MHz envelope 內的中心頻率／WLAN 頻寬／Generator 功率
  輸入，預覽會顯示是否通過目前 WLAN approved/HIL profile；只有通過者才可送 RF，後端
  仍以 fingerprint 與二次 gate 驗證同一組值。首頁白名單嵌入兩份既有互動架構圖，改用
  `present=1` 互動／簡報模式，可切換、重新載入及全頁開啟，不自動播放。Browser Demo
  驗證 5955 MHz／20 MHz／-50 dBm 預覽與 Matplotlib 選單式預覽；本批沒有連線 CMP180 或
  送 RF，自訂單點仍待現場低功率 HIL。

- 2026-09-03 完成新一輪 query-only CMP180 preflight：TCP 5025 經乙太網路可達，
  firmware `6.0.50.23`，error queue 空；WLAN MEAS1 為 `RDY`、RF1.5、EHT／BW320／
  B6GH／6105 MHz、IF Power -45 dB、expected -20 dBm、SingleShot 10。序號不寫入文件。
  本次未查證 Generator RF state，沒有啟動量測或傳送 RF，因此是安全快照，不是新 HIL。
  Path Loss、DUT、UDBox 仍因校正設備／接線／功率上限／owner 核准缺失而 BLOCKED；
  詳見 `docs/path-loss-dut-udbox-hil-plan.md`。

- 2026-09-03 新增 Pandas／Matplotlib 離線 PNG 報告引擎；`plot_results.py` 支援
  `svg`、`pandas-matplotlib` 與 `both`，且只讀 stored CSV，不連線或控制 CMP180。
  同批新增 0–5 次 bounded retry，只接到 query-only connection diagnostic；只重試
  transient connection／timeout，每次 retry 前 disconnect，絕不自動重送 SCPI write、
  RF workflow、safety rejection 或 `INV`。完整驗證 261 tests、兩份 YAML validation
  與 `git diff --check` 通過；沒有連線儀器或傳送 RF。

- 2026-09-03 將獨立開發日誌擴充為 Week 1–12，逐日記錄進度、問題、決策理由與隔日
  目標，並明確區分可追溯日期與由 repository 重建的規劃單位。

- 2026-09-02 修正 GPRF power sweep 的量測端設定缺口。唯讀探索確認 GPRF measurement 的
  routing／ENPower／EATTenuation／catalog 命令（韌體 `6.0.50.23`，error queue 全空），
  setter 以 RF Off 同值寫回驗證通過。修正前量測端停在**未接線的 `"RF1.6"`**，讀到的
  -80.87 dBm 其實是雜訊底；workflow 現在依 `cable_confirmation` 明確寫入並 read-back
  `"RF1.5"`、ENPower 與 EATT，不符即中止，且每點量測後與收尾都讀 `SYST:ERR?`，
  error queue 非空一律標為 `INVALID`。修正後 run `d3c259178c` 讀到 -56.25 dBm
  （改善約 24.6 dB），但 reliability 為 `3`，故仍標記 `INVALID`。剩餘約 15.8 dB 落差
  定位為**產生器播放突發 WLAN ARB 波形而非 CW**，已於同日以 CW 切換解決（見下一則）。
  最終 RF `OFF`、error queue 空。這是新實機 RF 量測。

- 2026-09-02 GPRF power sweep 改為自動切換 CW，量值落差全數解決。
  `scripts/cmp180_gprf_bbmode_discovery.py` 在韌體 `6.0.50.23` 確認
  `SOURce:GPRF:GEN:BBMode` 接受 `CW` 與 `ARB`（readback 一致、error queue 空），
  其餘 baseband 候選 header 皆為 `-113`。**實機確認切到 CW 再切回 ARB 不會清除已選
  waveform**；workflow 仍在收尾比對並於不符時重新指定。CW 下 run `67ccd62048` 讀到
  **-39.7106 dBm**（Generator -40 dBm，差 **0.29 dB**）、**reliability `0`**、
  `valid=true`，error queue 與 cleanup 皆空。收尾還原確認 baseband `ARB`、waveform
  路徑相同、RF `OFF`、WLAN measurement `RDY`。WLAN 回歸驗證 run `7ccdb50ca1` 的
  EVM data carriers `-36.86 dB`、burst power -39.80 dBm，與先前一致，WLAN 能力未受影響。
  GPRF power 現可用於 400 MHz–8 GHz 掃頻、線損與 port 響應特性；線損若要成為正式數據，
  仍須完成 Calibration Profile 核准流程。這是新實機 RF 量測。

- 2026-09-02 RF owner 核准將 11 個已完成 HIL 的 WLAN section 納入 Web approved
  profile。執行閘門改為逐 section 比對 band／bandwidth／frequency envelope，避免整體
  min/max 放行非 WLAN 空隙；SingleMeasurement backend 會在 RF OFF／measurement idle
  後依頻寬自動選取匹配 waveform，並完成 OPC、error queue 與 ABSPath readback。

- 2026-09-01 使用 Chrome 唯讀檢查 CMsquares 確認長時間 `RUN` 的根因是
  Measurement Repetition 漂移為 `Continuous`、Stop Condition 為 `None`。CMP180
  內建 WebHelp 確認 `CONFigure:WLAN:MEAS:MEValuation:REPetition SINGleshot`
  與 `...:SCOunt:MODulation 10`。backend 現在於 RF Off 設定並 read-back 這兩項，
  且未操作 ARB Sequencer state tree。單一 campaign tool 重驗通過：黃金點
  run `49441e526a`、49 點 5925–7125 MHz 頻掃 run `956dbedc4a`、26 點
  -55 至 -30 dBm 功掃 run `2c85d90e4d`。獨立收尾為 RF `OFF`、measurement
  `RDY`、error queue empty。這是新實機 RF 量測，不是 Mock 或 stored-only `FETCh`。

- 2026-09-01 重新載入後以 RF1.1 → RF1.5 直連、0 dB 衰減、320 MHz、6105 MHz、
  Generator -40 dBm 進行黃金點重驗。修正後的 cleanup 只操作 GPRF Baseband ARB
  的通用 Generator state，沒有再送 ARB Sequencer state-tree command。兩次 INIT
  都只觀察到 `RUN`，分別在 60 與 120 秒後逾時；STOP 後的獨立唯讀
  `FETCh` 有有限數值，但不得當成完整自動 SingleShot PASS。兩次最終皆為
  RF `OFF`、measurement `RDY`、error queue empty。因黃金點 workflow 未通過，
  未執行 320 MHz 頻率或功率批次。

- 2026-09-01 新增可恢復的 Web `HIL Campaign Runner`，將 2.4／5／6 GHz 頻寬、代表功率、其他 RF routes、500 MHz analysis bandwidth、雙 VSA／VSG 與 LEN≥32768 waveform 分類為 READY／BLOCKED，並以 `output/hil-campaign/state.json` 保存跨瀏覽器／server session 進度。只有現行 backend 與 Approved Profile 可執行的案例能按 Run；blocked 案例不會偷換成既有 RF1.1→RF1.5 profile。Pause／Stop 沿用點位 cleanup／RF-Off 邊界。驗證為 183 tests、兩份 YAML validation、JavaScript syntax 與 `git diff --check` 通過；本批只使用 Unit／Mock，未連線儀器、未送 RF。

- 2026-08-28 修正實機掃描控制的正確性問題：頻率／功率掃描按鈕現在使用畫面上的自訂 Sweep Plan，不再呼叫固定三點／四點 profile endpoint，因此不會出現輸入 400 MHz 卻實際跑 6085／6105／6125 MHz 的隱性覆蓋。Preview 會回傳 `rejection_reason`，未通過目前 RF workflow 的組合會顯示原因且不送 RF。EVM limit 方向已加測：EVM dB 越負越好，量測值必須 `<= maximum_evm_db`；沒有 approved limit profile 時實機結果顯示 `MEASURED` 而非 PASS。Power Reference Plane 尚未套用正式 +5 dB compensation，metadata 仍標示 `calibration_applied=false`。本批只使用 unit／Mock 驗證，未連線儀器、未送 RF。

- 2026-08-28 掃描設定改為永久展開，移除 Axis 下拉選單；實機單點／頻率／功率分頁直接決定 workflow。Start／Stop／Step／Center 各自提供 MHz／GHz 選單並等值換算。Job API 公開已完成點的唯讀快照，Web 執行中顯示進度、最新 EVM 與即時趨勢；資料只在單點 cleanup／RF Off 後發布。本批使用 Mock／unit 驗證，未連線儀器、未送 RF。

- 2026-08-27 建立 `feature/hardware-console-productization`：一般本機啟動直接提供受保護的實機控制，`--demo-only` 才停用儀器；移除實機頁裝飾性積木與模式下拉選單，改由單點／頻率／功率分頁直接設定。規劃層接受 CMP180 型錄 400 MHz–8 GHz 與 WLAN 20／40／80／160／320 MHz，但 RF 執行仍只允許 Approved Profile／HIL 組合。本批未連線儀器、未送 RF。

- 2026-08-27 實機量測改為與示範訓練一致的單點／頻率掃描／功率掃描分頁；切換會同步後端 action，單點隱藏掃描欄位。圖表改為固定座標，滾輪只縮放 X 軸、拖曳只水平平移且有邊界，hover 顯示十字游標與完整工程值。說明頁新增 Git clone、Python 3.11 安裝、Demo、YAML validation、唯讀連線、離線 SVG 與 HTML report 指令。完整基準為 `155 passed`；本批未連線儀器、未送 RF。

- 2026-08-27 收斂 Web 操作層級：隱藏重複的頁面 Hero／控制狀態卡，將「自訂量測計畫」改名為「掃描設定」，並以三步快速操作取代重複的 Operator Playbook 卡片。PowerShell 指南現在先切到專案目錄，且複製內容不再包含錯誤的 `PS` 提示符。新增 `docs/next-hil-campaign.md`，把下一次機台時段整理成 90 分鐘能力快照、RF-Off 回讀、參考點、邊界點、短掃描與稽核批次。完整基準為 `153 passed`；本批未連線儀器、未送 RF。

- 2026-08-27 已解決新實機阻點：原 lib8/GI32 waveform 仍存在；根因是儀器 profile
  漂移與 Baseband ARB／ARB Sequencer state tree 混用。Python SingleShot run
  `5cabdc74de`、三點頻率 sweep `e0a40c3bab`、四點功率 sweep `5cbb6c37a7` 全部通過，
  最終 RF OFF／measurement RDY／error queue empty。

- 2026-08-27 依 CMsquares Workspace 操作模型新增 Generator／Analyzer／Measurement Flow 積木。Run 仍走既有安全表單；掃描 Pause 只在點位 STOP／RF Off 邊界進入 `PAUSED`，Resume 從下一點繼續，Stop 可解除暫停並保存 partial artifacts。新增兩項 Job pause/cancel 測試，完整基準為 `150 passed`。本批只使用 Mock／unit，不是新的實機 HIL。
- 2026-08-27 新增實機 artifact 診斷快照：量測狀態轉換、WLAN standard／band、ARB waveform、trigger source／threshold、expected nominal power、external attenuation 與 ranging strategy。既有 2026-08-27 結果顯示有效 GI3.2/MCS11 結果與最終 `RDY`；`RDY,ADJ,INV` 是可用狀態集合，不可單獨視為本次 INV。此修改尚未執行新的 RF HIL。
- 2026-08-27 新增 CMP180 四層能力模型與 `/api/capabilities`：Catalog、Installed、Approved Profile、Verified HIL 必須分開。首頁顯示能力矩陣，型錄的 400 MHz–8 GHz／最高 500 MHz 只供規劃，RF 執行仍由 approved profile 授權。新增交付與能力擴充文件；完整基準為 `152 passed`，本批未送 RF。
- 2026-08-27 完成 repository hygiene：移除 37 個可重建的 pytest／mypy／ruff cache 目錄，保留 `output/` 量測成果；README 新增 GitHub 中英文跳轉、能力狀態、實機／自訂啟動方式與專案結構，並新增 `docs/README.md` 文件中心，明確標示權威規格及封存資料。本批只整理檔案與文件，未連線儀器、未送 RF。

- 2026-08-25 固定 profile 現場重驗未通過：目前可用 lib1/GI08 waveform 在 -40 dBm
  下，IF Power 與 Generator Restart Marker 觸發皆得到 `RUN → RDY`，但完整狀態為
  `RDY,ADJ,INV`，五組 28 欄結果皆無效。程式已改為檢查完整 substate 與關鍵欄位，
  不再把主狀態 `RDY` 誤報為 PASS。既有 2026-08-20 HIL 保留，但目前 profile 需先
  排除 waveform／同步／解調差異，才能重新執行 sweep。

- 2026-08-25 自訂兩點頻率 HIL（6085／6105 MHz、-45 dBm）在第 2 點回傳 `INV`，
  已依規則停止；最終 Generator `OFF`、Analyzer `RDY`、error queue empty。此結果是
  finding，不是通過證據。已修正 `INV` 正規化與 partial artifact 保留；重新 HIL 前需先
  確認 trigger／ranging 設定並取得新的現場授權。
- 2026-08-25 操作員評估後已恢復 `static/` 原版橫向量測工作區；`static_v2/` 保留為封存設計參考但不再由伺服器提供。正式介面新增從量測紀錄勾選 2–8 筆 Run 的唯讀疊圖比較，可調整 Trace 名稱、顏色與顯示，並在 `INV`／缺值處中斷曲線；不會因此啟動量測或 RF。
- 2026-08-25 修正量測紀錄前端反覆 mutation 導致的空白／卡住風險，改為一次性列渲染並在啟動時預先讀取；同時修正校正步驟雙重編號、操作指南分頁切換、各工作區情境標題與完整亮／暗主題覆寫。該批只使用 API、既有資料與自動測試，未送 RF。
- 2026-08-25 實機／示範量測子頁已真正互斥顯示；Runs 新增全文搜尋、日期／來源／狀態篩選、RF 排序、列內詳情與瀏覽器輸出。Trace 新增線型、點型、色彩鎖、Solo、移除、拖曳與 SVG／PNG／CSV 匯出。Explorer 權限失敗路徑不再由 UI 呼叫；刪除維持 Run ID 防呆與可復原 Trash。
- Web 實機授權改為頁內完成：Route、操作員在場與後端安全 profile 通過後，最後確認框顯示實際頻率／功率／頻寬摘要；取消不送 RF。另新增曲線鄰近點 hover 完整讀值與亮色按鈕反光互動。
- 新增公司內部產品首頁：雙語 Hero、系統能力、RF 自動化流程、Artifacts、校正、歷史比較與操作手冊入口。首頁使用本機 CSS 動畫且只做導覽，不會呼叫 RF API；HeyGen／HyperFrames 教學影片保留為後續可選內容。
- 2026-08-25 曾建立隔離的 V2 並完成 Demo 瀏覽器驗收；操作員評估後已停止提供
  `static_v2/`，目前只保留為封存設計參考。正式伺服器提供 `static/` 原版橫向量測
  工作區，並已回用 V2 的歷史多 Run 比較概念。
- Web V2 已進一步重構為 RF 工作站：移除所有頁面重複的固定量測 Hero，加入每頁情境標題、
  Dark／Light／System、Runs Table 搜尋／篩選／排序、2–8 Run 比較、Trace 名稱／顏色／拖曳、
  metric、逐點 Table、Zoom／Pan／A-B Cursor 與 Draft 校正 SOP。歷史 Demo 時間戳相容層
  只讀 `results.json`，不改寫舊 artifacts。本批 Chrome 與自動測試僅使用 Demo／既有資料。

- 分支：`feature/web-v2-clean-rebuild`。
- Python 實機 SingleShot 已通過：RF1.1 → RF1.5、6105 MHz、320 MHz、-40 dBm。
- Web GUI 已有雙語響應式版面（亮／暗主題切換，預設暗色）、Mock 單點／頻率掃描／功率掃描、受保護實機 SingleShot、artifacts 與圖表。
- 實機 Web 只允許 loopback bind；尚無 authentication／RBAC，不得對內網公開 RF endpoint。
- 安全短掃描核心（頻率與功率）與 Mock tests 已完成；固定三點頻率 HIL 已通過，功率 HIL 未完成，Web 實機 sweep 仍鎖定。
- Run `bb3e8db580` 完成 6085／6105／6125 MHz 三點實機掃頻；三點 errors 均空，最終 RF `OFF`、measurement `RDY`、error queue empty，完整 artifacts 已保存。
- 功率掃描 run `56ab9c982e` 在 -60 dBm 回傳 `INV`，舊核心錯標 complete；安全收尾正常。已補有限關鍵指標閘門，需重新 HIL，原 artifacts 保持不變作為 finding 證據。
- 修正版 run `b8db34c0f4` 在 -60 dBm 正確立即停止、標示 partial，未執行較高功率；最終 RF OFF／RDY／error queue empty。下一個候選有效批次為 -55 至 -40 dBm。
- Run `e6e86fe3d7` 完成 -55／-50／-45／-40 dBm 四點有效功率掃描；四點 errors 均空，最終 RF OFF／RDY／error queue empty，20 份 raw 與完整 artifacts 已保存。
- Web Mock Sweep 已改為非同步 Job API，支援進度、單一 active job、取消與 partial artifacts；瀏覽器驗收通過取消 3/11、完成 4/4、檔案連結與窄版無溢出；該批驗收未控制實機。
- 實機 Web Frequency／Power Sweep 已接固定 HIL profile；run `afb64617df` 完成頻率 3/3，run `7463d55002` 的功率取消於安全邊界停止為 2/4 並保存 partial artifacts。最終 RF OFF／measurement RDY／error queue empty，現場 Web HIL 已通過。
- Web GUI 新增唯讀「量測紀錄」，由新到舊顯示 `output/` runs，提供 HTML／CSV／JSON／Metadata 受控連結；不暴露本機絕對路徑或 raw SCPI，也不接觸 RF。
- 新增 Draft Limit Profile 架構；Mock 結果只標示 `DRAFT_PASS`／`DRAFT_FAIL`，metadata 保存 profile snapshot 與 `compliance_claim=false`。正式數值仍待 RF／測試負責人核准。
- UX 將三個 Mock 頁明確改為示範模式，實機 SingleShot／Frequency／Power 集中於「實機量測」；badge、檢查燈與模式有 hover 說明，結果顯示不含敏感資訊的相對輸出位置。
- Web server 改用 exclusive port bind，防止多個新舊 process 同時佔用相同 port 而造成新版頁面呼叫舊 API 的 `Not found`。
- Run History 已擴充為可載入過去設定／結果／波形參考、開啟本機輸出資料夾，並以 Run ID 二次確認後移至可復原的 `output/.trash/`；本機檔案副作用 API 僅允許 loopback client。
- 新增 Path Loss／Calibration Profile 核心：Draft／Approved、有效期限、0–30 dB、範圍內線性內插、禁止外插及 CLI 驗證。範例仍是 Draft 佔位值，尚未套入實機量測。
- 新增器材更換校正 SOP：CSV 讀值轉 Draft Profile 腳本、Web 校正精靈，以及自訂掃描安全點位預覽。這些新路徑目前不會送 RF；自訂實機執行仍待 HIL。
- Web 校正頁新增 CSV 匯入、示範資料、外部儀器擷取入口與各欄位可鍵盤操作的 `?` 說明；一般操作員不必手動輸入 CLI。外部 adapter 未設定時會說明原因且不控制 RF。
- 新增 Calibration Adapter registry、共用 capture controller 與 Mock Reference Adapter；Web 會查詢可用能力並顯示 DEMO／unavailable。所有 capture 路徑在例外時仍執行 output off／close。
- 自訂 CMP180 頻率／功率掃描已完成軟體執行接線：雙重 startup gate、後端 fingerprint 確認、Job／取消、partial artifacts、失敗狀態保留與 emergency RF Off。尚未執行新的自訂實機 HIL。
- Tkinter 桌面 GUI 已移除（功能已被 Web GUI 完全取代），改用 CLI／Web GUI。
- Result artifacts 現在保存全部 5 組已驗證統計（average／current／min／max／std_dev），不只 average。
- 2026-08-20 已完成五統計同一實機 SingleShot HIL：五組各 28 欄、`simulated=false`、
  instrument／cleanup errors 空，最終 RF `OFF`、measurement `RDY`、error queue empty。
- 新增 ruff／mypy（CI 中非阻斷）與 `scripts/precommit_check.ps1`。
- PR #7 接手審查已將 Frequency／Power Sweep 的頻率、頻寬、功率、span 與點數改為
  不可由呼叫端放寬的硬性安全包絡，並補上繞過測試；尚未執行新的實機 RF。
- UI-1 已移除底部模式列與宣傳式 Hero，改成緊湊量測工作區、單一模式狀態與較
  清楚的深色控制台層級；Demo 掃描同步限制為最多 11 點，單點功率上限 -40 dBm。
- PR #7 程式驗證：87 tests、兩份 YAML validation、JavaScript syntax 與
  `git diff --check` 通過；該批自動檢查只使用 unit／Mock。其後已另行完成上述
  2026-08-20 五統計實機 RF HIL，兩者不可混稱為同一次驗證。

### 安全基線與完成項目

- 核准測試 endpoint：`192.168.200.50:5025`；RF1.1 → RF1.5 單 cable loopback。
- 基線：6105 MHz、320 MHz、Generator -40 dBm、expected power -20 dBm。
- 最近收尾確認 RF `OFF`、measurement `RDY`、error queue empty；每次新 session 仍須重新查詢。
- 已完成設定／連線、discovery、setter、INIT／STOP／ABORT、RF On／Off、SingleShot backend、28 欄 parser、CSV／JSON／metadata／raw／HTML 與 Web GUI。
- GitHub Actions 只跑 unit／Mock／config validation，不連公司 CMP180。

### 下一步

1. 取得 RF1.1→RF1.5 真實線損與設備參考編號，核准 Calibration Profile，再將 snapshot 與修正值接入實機 artifacts。
2. 完成內網 deployment 所需 authentication、RBAC 與 audit log；完成前不得綁定非 loopback。
3. 增加 run history、取消／cleanup 細節與獨立 CSV／JSON redraw CLI。

實機前先跑連線與 query-only Generator discovery，確認 RF OFF、measurement RDY、error queue empty，再依 [hardware SOP](docs/hardware-test-sop.md) 操作。

## English Version

- On 2026-09-03, the post-promotion regression completed for all 11 approved Loopback representative points with Repeat=10 each. All 110 measurements were valid; all 11 profiles recorded approved lifecycle, Stability PASS, Reasonableness PASS, and `LOOPBACK_READY`, with final RF OFF, measurement RDY, and no cleanup errors in every metadata record. Formal artifacts span `output/20260903T111307Z_loopback-validation_3d788aaab7` through `output/20260903T111527Z_loopback-validation_582aded41f`; the complete case mapping is in `docs/loopback-validation.md`. The same batch made all Web check plans immediately bilingual: SingleShot, WLAN Sweep, GPRF, Loopback, HIL Campaign, and Calibration steps, previews, safety reasons/corrections, and final confirmations follow the language selector. Language changes redraw existing data without calling RF. Software validation passed 282 tests, both YAML validations, and `git diff --check`.

- On 2026-09-03, Loopback gained Run All for representative points across all 11 approved WLAN sections, Repeat=10 each, for 110 independent SingleShots. Each profile saves separate artifacts and any SCPI or cleanup error stops the batch. The live batch completed 110/110 valid; every case passed Stability and Reasonableness or draft Reasonableness, with final RF OFF, measurement RDY, and no cleanup errors. The ten new representative points were promoted using their own artifacts, while the existing 6 GHz/320 MHz profile retains its original approval evidence. Other routes and UD Box paths remain blocked.


- On 2026-09-03, the first live Repeat=10 HIL completed through the production Loopback Web page at RF1.1 to RF1.5, 6105 MHz, 320 MHz, and −40 dBm. All 10 repeats were valid, Stability passed, and Reasonableness produced DRAFT_PASS. EVM/power/frequency-error sample standard deviations were 0.03178 dB/0.000604 dB/9.3989 Hz. Repeat 1 was an IQR frequency-error outlier but remained valid and preserved. Evidence is `output/20260903T101748Z_loopback-validation_865ca580c5`; final RF was OFF, measurement was RDY, and cleanup errors were empty. The exact condition with at least 10 repeats is now an approved profile; the post-approval regression artifact `output/20260903T102312Z_loopback-validation_76df94aae2` completed 10/10 valid with Stability/Reasonableness PASS and `LOOPBACK_READY`. All other inputs remain draft.


- 2026-09-03: Added a dedicated Loopback Web page, asynchronous hardware job, post-cleanup live trends for three core metrics, and INVALID/IQR-outlier highlighting. Every repeat invokes a complete SingleShot; invalid results are retained while SCPI or cleanup errors stop execution. Added sample statistics, layered Validity/Stability/Reasonableness/Overall decisions, and traceable artifacts. This batch used unit/Mock tests only and did not run a new CMP180 RF measurement; Repeat=10 HIL remains pending.

- On 2026-09-02, the GPRF power sweep's measurement-side configuration gap was fixed.
  Read-only discovery confirmed the GPRF measurement routing/ENPower/EATTenuation/catalog
  commands on firmware `6.0.50.23` with an empty error queue, and the setters passed
  same-value write-back validation with RF off. Before the fix the measurement side was
  parked on the **uncabled `"RF1.6"`** port, so the -80.87 dBm reading was a noise floor.
  The workflow now writes and reads back `"RF1.5"`, ENPower, and EATT from
  `cable_confirmation`, aborts on mismatch, and reads `SYST:ERR?` after every point and
  after cleanup, forcing `INVALID` on a non-empty queue. Post-fix run `d3c259178c` measured
  -56.25 dBm (about 24.6 dB better) but returned reliability `3`, so it is still recorded as
  `INVALID`. The remaining ~15.8 dB gap was attributed to the generator playing a **bursted
  WLAN ARB waveform rather than CW**, which was resolved the same day by the CW switch below.
  Final RF was `OFF` with an empty error queue. This was a new live RF measurement.

- On 2026-09-02, the GPRF power sweep began selecting CW automatically, resolving every
  measured-value discrepancy. `scripts/cmp180_gprf_bbmode_discovery.py` confirmed on firmware
  `6.0.50.23` that `SOURce:GPRF:GEN:BBMode` accepts `CW` and `ARB` with matching read-backs
  and an empty error queue, while every other baseband candidate header returned `-113`.
  Switching to CW and back was confirmed **not** to clear the selected waveform; the workflow
  still compares it during cleanup and reselects it on a mismatch. In CW, run `67ccd62048`
  measured **-39.7106 dBm** against a -40 dBm generator level (**0.29 dB** difference) with
  **reliability `0`** and `valid=true`, and empty error and cleanup queues. Restore checks
  confirmed baseband `ARB`, an identical waveform path, RF `OFF`, and WLAN measurement `RDY`.
  WLAN regression run `7ccdb50ca1` measured EVM data carriers `-36.86 dB` and burst power
  -39.80 dBm, consistent with earlier results, so WLAN capability is unaffected. GPRF power is
  now usable for 400 MHz-8 GHz sweeps, cable loss, and port response; cable-loss figures still
  need the Calibration Profile approval flow before they count as formal data. This was a new
  live RF measurement.

- On 2026-09-02, the RF owner approved all 11 HIL-complete WLAN sections for the Web
  approved profile. The execution gate now matches each band/bandwidth/frequency envelope
  independently so the overall min/max cannot authorize non-WLAN gaps. While RF is OFF and
  measurement is idle, the SingleMeasurement backend auto-selects the matching waveform
  and verifies OPC, the error queue, and its absolute-path readback.

- On 2026-09-01, read-only Chrome inspection of CMsquares identified the persistent `RUN`
  root cause: Measurement Repetition had drifted to `Continuous` with Stop Condition
  `None`. CMP180 built-in WebHelp confirmed
  `CONFigure:WLAN:MEAS:MEValuation:REPetition SINGleshot` and
  `...:SCOunt:MODulation 10`. The backend now sets and reads back both values while RF is
  off and does not operate the ARB Sequencer state tree. One full campaign tool passed the
  golden point (run `49441e526a`), the 49-point 5925–7125 MHz frequency sweep (run
  `956dbedc4a`), and the 26-point -55 to -30 dBm power sweep (run `2c85d90e4d`). Independent
  final checks showed RF `OFF`, measurement `RDY`, and an empty error queue. This was a new
  live RF measurement, not Mock data or a stored-only `FETCh`.

- On 2026-09-01, the golden point was retried after reload with the direct RF1.1-to-RF1.5
  path, 0 dB attenuation, 320 MHz, 6105 MHz, and -40 dBm Generator power. The corrected
  cleanup only used the common GPRF Baseband ARB Generator state and did not issue an ARB
  Sequencer state-tree command. Both INIT attempts remained in `RUN` and timed out after
  60 and 120 seconds respectively. A separate query-only `FETCh` after STOP returned finite
  values, but it does not qualify as a complete automated SingleShot pass. Both attempts
  ended with RF `OFF`, measurement `RDY`, and an empty error queue. Because the golden-point
  workflow did not pass, no 320 MHz frequency or power batch was executed.

- On 2026-09-01, a resumable Web `HIL Campaign Runner` was added. It classifies 2.4/5/6 GHz bandwidths, representative power, alternate RF routes, 500 MHz analysis bandwidth, dual VSA/VSG, and LEN≥32768 waveform cases as READY or BLOCKED and persists progress across browser/server sessions in `output/hil-campaign/state.json`. Run is enabled only when the current backend and Approved Profile support the case; blocked cases are never substituted with the existing RF1.1-to-RF1.5 profile. Pause and Stop retain point-cleanup/RF-Off boundaries. Validation passed 183 tests, both YAML validations, JavaScript syntax, and `git diff --check`; this batch used Unit/Mock only and did not connect to the instrument or transmit RF.

- On 2026-08-27, Hardware Measurement adopted the same Single/Frequency Sweep/Power Sweep tabs as Demo Training. Tab changes synchronize the backend action and Single hides sweep-only fields. Charts now use fixed coordinates: the wheel zooms only X, drag pans horizontally within bounds, and hover shows a crosshair plus complete engineering values. Help now covers Git clone, Python 3.11 installation, Demo startup, YAML validation, query-only connection checks, offline SVG generation, and HTML report rebuilding. The complete baseline is `155 passed`; this batch did not connect to the instrument or transmit RF.

- On 2026-08-27, the Web hierarchy was reduced: duplicate page heroes/control-state cards are hidden, "Custom Measurement Plan" is renamed "Sweep Setup," and a three-step quick-start replaces the repeated Operator Playbook cards. PowerShell guidance now changes to the project directory first and copied commands no longer include the invalid `PS` prompt. `docs/next-hil-campaign.md` defines a ninety-minute capability snapshot, RF-Off readback, reference-point, boundary-point, short-sweep, and audit campaign for the next instrument slot. The complete baseline is `153 passed`; this batch did not connect to the instrument or transmit RF.

### Status (2026-08-27)

- On 2026-09-03, Web Results and home-page integration was completed. Newly saved
  SingleShot/sweep CSV files automatically produce four 160 DPI Pandas DataFrame plus
  Matplotlib Agg PNGs, shown as Results thumbnails and artifacts. The Web SVG now has
  separately laid-out X/Y titles, engineering units, six tick groups, and safe margins.
  Hardware SingleShot accepts center frequency, WLAN bandwidth, and generator power;
  preview, fingerprint, final confirmation, and server-side gate use the same values.
  Execution remains limited to the approved profile, RF1.1-to-RF1.5, -55 to -30 dBm, and
  emergency cleanup. The home page allowlists and embeds both interactive diagrams with
  autoplay, switching, replay, and full-page controls. A Browser Demo verified a
  5955 MHz/20 MHz/-50 dBm preview and four synchronized PNGs. The full regression passed
  263 tests, both YAML validations, and `git diff --check`. No CMP180 connection or RF
  transmission occurred; custom-value SingleShot still requires low-power on-site HIL.

- On 2026-09-03, a fresh query-only preflight confirmed Ethernet TCP 5025, firmware
  6.0.50.23, an empty error queue, and WLAN MEAS1 in `RDY` with RF1.5,
  EHT/BW320/B6GH/6105 MHz, IF Power at -45 dB, -20 dBm expected power, and SingleShot 10.
  The serial is omitted. Generator RF state was not verified, no measurement was started,
  and no RF was transmitted; this is a safety snapshot, not new HIL. Path Loss, DUT, and
  UDBox remain blocked on calibrated equipment, cabling, power limits, and owner approval;
  see `docs/path-loss-dut-udbox-hil-plan.md`.

- On 2026-09-03, the offline reporting path gained Pandas/Matplotlib PNG output. The
  plotting script supports `svg`, `pandas-matplotlib`, and `both` and reads stored CSV
  without connecting to or controlling the CMP180. The same batch added a 0–5 bounded
  retry used only by query-only connection diagnostics. It retries transient connection/
  timeout failures, disconnects before retrying, and never automatically repeats SCPI
  writes, RF workflows, safety rejections, or `INV`. Validation passed 261 tests, both
  YAML validations, and `git diff --check`; no instrument connection or RF transmission
  was performed.

- On 2026-09-03, the standalone development journal was expanded to Weeks 1–12 with
  daily progress, problems, decision rationale, and next-workday targets, while clearly
  distinguishing dated evidence from repository-reconstructed planning units.

- On 2026-08-28, hardware sweep correctness was fixed: Frequency/Power Sweep now executes the custom Sweep Plan shown on screen instead of calling the fixed three-point/four-point profile endpoints, so a 400 MHz input cannot be silently replaced by 6085/6105/6125 MHz. Preview now returns `rejection_reason`; plans rejected by the current RF workflow display the reason and transmit no RF. EVM limit direction is covered by tests: more-negative EVM dB is better, and the measured value must be `<= maximum_evm_db`. Hardware results without an approved limit profile display `MEASURED`, not PASS. Power Reference Plane does not yet apply formal +5 dB compensation; metadata still reports `calibration_applied=false`. This batch used unit/mock validation only and did not connect to the instrument or transmit RF.

- On 2026-08-28, Sweep Setup became permanently expanded and the Axis dropdown was removed; direct Single/Frequency/Power tabs select the workflow. Start/Stop/Step/Center fields each have an adjacent MHz/GHz selector with value-preserving conversion. The Job API exposes read-only snapshots of completed points so the Web page can show progress, latest EVM, and a live trend only after point cleanup/RF Off. This batch used Mock/unit validation and did not connect to the instrument or transmit RF.

- On 2026-08-27, `feature/hardware-console-productization` changed normal local startup to expose guarded hardware control; `--demo-only` disables instrument access. Decorative blocks and the measurement-mode dropdown were removed in favor of direct Single/Frequency/Power tabs. Planning accepts the 400 MHz–8 GHz catalog range and WLAN 20/40/80/160/320 MHz bandwidths, while RF execution remains limited to Approved Profile/HIL combinations. This batch did not connect to the instrument or transmit RF.

- The new hardware blocker was resolved on 2026-08-27. The original lib8/GI32 waveform
  is still present; the root cause was profile drift plus mixing the Baseband ARB and ARB
  Sequencer state trees. Python SingleShot `5cabdc74de`, three-point frequency sweep
  `e0a40c3bab`, and four-point power sweep `5cbb6c37a7` all passed, ending with RF off,
  measurement ready, and an empty error queue.

- On 2026-08-27, CMsquares-inspired Generator, Analyzer, and Measurement Flow blocks were added. Run still delegates to the guarded form. Sweep Pause enters `PAUSED` only at a STOP/RF-Off point boundary, Resume continues at the next point, and Stop releases a paused job while preserving partial artifacts. Two job pause/cancel tests were added, bringing the complete baseline to `150 passed`. This batch used mock/unit testing only and is not new hardware HIL evidence.
- On 2026-08-27, hardware artifacts gained diagnostic snapshots for measurement-state transitions, WLAN standard/band, ARB waveform, trigger source/threshold, expected nominal power, external attenuation, and ranging strategy. Existing 2026-08-27 artifacts contain valid GI3.2/MCS11 results and end in `RDY`; `RDY,ADJ,INV` is a state catalog and must not be treated as proof that the run entered INV. No new RF HIL was executed for this change.
- On 2026-08-27, a four-layer CMP180 capability model and `/api/capabilities` were added. Catalog, Installed, Approved Profile, and Verified HIL are now separate, and the home page renders the matrix. The catalog 400 MHz–8 GHz/up-to-500 MHz figures are planning-only; RF execution remains authorized by an approved profile. Partner-delivery documentation was added. The full baseline is `152 passed`; no RF was transmitted in this batch.
- On 2026-08-27, repository hygiene removed 37 reproducible pytest/mypy/ruff cache directories while preserving measurement artifacts under `output/`. The README gained GitHub language navigation, a capability matrix, guarded hardware/custom startup commands, and a repository map. A new `docs/README.md` documentation centre now identifies authoritative and archived material. This batch only organized files and documentation; it did not connect to the instrument or transmit RF.

- The fixed-profile on-site revalidation on 2026-08-25 did not pass. With the currently
  available lib1/GI08 waveform at -40 dBm, both IF Power and Generator Restart Marker
  triggering produced `RUN → RDY`, but the full state was `RDY,ADJ,INV` and all five
  28-field statistics were invalid. The workflow now checks the full substate and critical
  fields instead of reporting PASS from the main `RDY` state alone. Existing 2026-08-20
  HIL evidence remains, but waveform/synchronization/demodulation differences must be
  resolved before rerunning sweeps.

- The 2026-08-25 custom two-point frequency HIL (6085/6105 MHz at -45 dBm) returned
  `INV` at point 2 and stopped as required. Final state was Generator `OFF`, Analyzer `RDY`,
  and an empty error queue. This is a finding, not passing evidence. `INV` normalization and
  partial-artifact retention are corrected; a rerun requires trigger/ranging review and fresh
  on-site authorization.
- After operator review on 2026-08-25, the original horizontal workspace in `static/` was restored as the served UI. `static_v2/` remains an archived design reference. The production UI now compares 2–8 saved runs read-only, with editable trace names, colours, visibility, and breaks at `INV` or missing values; comparison never starts RF.
- On 2026-08-25, the run-history DOM mutation loop that could leave the table blank or stalled was replaced with deterministic row rendering and eager startup loading. The same change fixed duplicated calibration-step numbers, Operator Guide navigation, contextual workspace headings, and complete light/dark overrides. Validation used APIs, saved data, and automated tests only; no RF was transmitted.
- On 2026-08-25, hardware/demo measurement subviews became truly mutually exclusive. Runs gained full-text search, date/source/status filters, RF-aware sorting, inline details, and browser-native output opening. Traces gained line/point styles, colour lock, Solo, removal, drag ordering, and SVG/PNG/CSV export. The UI no longer calls the Explorer path that failed under workstation permissions; deletion retains exact Run-ID confirmation and recoverable Trash.
- Hardware authorization is now completed in-page: after route, operator-presence, and backend safe-profile checks, a final dialog shows the exact frequency/power/bandwidth summary. Cancelling transmits no RF. The chart also gained nearest-point hover readouts and light-theme reflective button interaction.
- Added a bilingual internal-product home with a capability overview, RF automation workflow, artifacts, calibration, run comparison, and operator-manual entry points. The home uses local CSS motion and navigation-only CTAs that call no RF API; a HeyGen/HyperFrames tutorial remains an optional follow-up.
- On 2026-08-25 an isolated V2 was created and validated with Demo data. After operator
  review, `static_v2/` stopped being served and remains only as an archived design reference.
  The server now serves the original horizontal workspace from `static/`, with the useful
  V2 historical multi-run comparison concept ported into production.
- Web V2 is now an RF workstation rather than a repeated measurement hero: contextual headings,
  Dark/Light/System, searchable/filterable/sortable Runs, 2–8 run comparison, trace naming/color/
  drag order, metric and point tables, zoom/pan/A-B cursors, and a Draft calibration SOP. Legacy
  Demo timestamps are recovered read-only from `results.json`; old artifacts are not rewritten.
  This browser and automated-test batch used Demo/saved data only.

- Branch: `feature/web-v2-clean-rebuild`.
- Python hardware SingleShot passed at RF1.1 to RF1.5, 6105 MHz, 320 MHz, and -40 dBm.
- The Web GUI provides a bilingual responsive layout (light/dark theme toggle, dark by default), mock single/frequency-sweep/power-sweep, guarded hardware SingleShot, artifacts, and plots.
- Hardware Web mode is loopback-only. Authentication/RBAC are absent, so never expose the RF endpoint to the network.
- The safe short-sweep cores (frequency and power) and mock tests are complete. Fixed three-point frequency HIL passed, power HIL is pending, and the Web hardware sweep buttons remain locked.
- Run `bb3e8db580` completed the 6085/6105/6125 MHz hardware sweep with empty per-point errors, final RF `OFF`, measurement `RDY`, an empty error queue, and complete artifacts.
- Power-sweep run `56ab9c982e` returned `INV` at -60 dBm and the old core mislabeled it complete; cleanup was safe. A finite critical-metric gate is now implemented and requires new HIL. Original artifacts remain unchanged as finding evidence.
- Corrected run `b8db34c0f4` stopped immediately at -60 dBm, recorded partial status, and did not run higher powers; final RF OFF/RDY/error queue empty. The next candidate numeric batch is -55 through -40 dBm.
- Run `e6e86fe3d7` completed the -55/-50/-45/-40 dBm numeric power sweep with empty per-point errors, final RF OFF/RDY/error queue empty, 20 raw responses, and complete artifacts.
- Web Mock Sweep now uses an asynchronous Job API with progress, one active job, cancellation, and partial artifacts. Browser acceptance passed cancel at 3/11, complete at 4/4, clickable artifact links, and narrow-layout overflow checks; that batch did not control hardware.
- Web hardware Frequency/Power Sweep uses fixed HIL profiles. Run `afb64617df` completed frequency 3/3; power run `7463d55002` cancelled safely at a point boundary with 2/4 partial artifacts. Final RF was OFF, measurement RDY, and the error queue empty; on-site Web HIL passed.
- The Web GUI now has read-only Run History, newest first, with controlled HTML/CSV/JSON/Metadata links. It exposes neither absolute local paths nor raw SCPI and never touches RF.
- Added the Draft Limit Profile framework. Mock results use only `DRAFT_PASS`/`DRAFT_FAIL`; metadata saves the profile snapshot and `compliance_claim=false`. Formal values still require RF/test-owner approval.
- UX now labels all three Mock pages as demos and groups real SingleShot/Frequency/Power under Hardware Measurement. Badges, preflight lights, and mode selectors have hover help; results show a non-sensitive relative output location.
- The Web server now uses an exclusive port bind, preventing stale and current processes from sharing a port and causing new pages to call old APIs with `Not found`.
- Run History can now load prior settings/results/waveform references, open the local output folder, and move a run to recoverable `output/.trash/` after exact Run ID confirmation. Local filesystem side effects are restricted to loopback clients.
- Added the Path Loss/Calibration Profile core: Draft/Approved lifecycle, expiry, a 0–30 dB bound, in-range linear interpolation, blocked extrapolation, and CLI validation. The example remains a draft placeholder and is not applied to live measurements.
- Added the equipment-change calibration SOP: a CSV-to-draft-profile script, a Web calibration wizard, and safety-bounded custom sweep point preview. These new paths do not transmit RF; custom live execution remains HIL-gated.
- The Web calibration page now has CSV import, example data, an external-instrument capture entry point, and keyboard-accessible per-field `?` help. Normal operators do not need the CLI. Missing adapters are explained without controlling RF.
- Added the Calibration Adapter registry, shared capture controller, and Mock Reference Adapter. The Web UI queries capabilities and labels DEMO/unavailable states. Every capture path still runs output-off/close cleanup on exceptions.
- Custom CMP180 frequency/power sweep execution is software-wired with a dual startup gate, backend fingerprint confirmation, jobs/cancellation, partial artifacts, retained failure state, and emergency RF Off. No new custom live HIL has been run yet.
- The Tkinter desktop GUI has been removed (fully superseded by the Web GUI); use the CLI/Web GUI instead.
- Result artifacts now save all 5 verified statistics (average/current/min/max/std_dev), not just average.
- On 2026-08-20, one real SingleShot completed five-statistic HIL: all five responses had
  28 fields, `simulated=false`, no instrument/cleanup errors, final RF `OFF`, measurement
  `RDY`, and an empty error queue.
- Added ruff/mypy (non-blocking in CI) and `scripts/precommit_check.ps1`.
- The PR #7 takeover review changed Frequency/Power Sweep frequency, bandwidth, power,
  span, and point limits into hard safety ceilings that callers cannot relax, with
  bypass tests added. No new live RF run was performed.
- UI-1 removed the persistent bottom mode bar and marketing-style hero, replacing them
  with a compact measurement workspace, one mode status, and a cleaner dark-console
  hierarchy. Demo sweeps now share the 11-point ceiling and demo single uses -40 dBm.
- PR #7 software validation: 87 tests, both YAML validations, JavaScript syntax, and
  `git diff --check` passed; that automated batch used unit/mock paths only. The separate
  five-statistic live-RF HIL described above was performed afterward on 2026-08-20 and
  must not be represented as part of the automated validation batch.

### Safety baseline and completed work

- Approved test endpoint: `192.168.200.50:5025`; one RF1.1-to-RF1.5 loopback cable.
- Baseline: 6105 MHz, 320 MHz, -40 dBm Generator, and -20 dBm expected power.
- Latest cleanup confirmed RF `OFF`, measurement `RDY`, and an empty error queue. Re-query every new session.
- Configuration/connection, discovery, setters, INIT/STOP/ABORT, RF On/Off, SingleShot backend, 28-field parser, artifacts, and Web GUI are complete.
- GitHub Actions runs only unit/mock/config checks and cannot access the company CMP180.

### Next steps

1. Measure the RF1.1-to-RF1.5 path loss and record equipment references, approve the Calibration Profile, then integrate its snapshot and corrected values into live artifacts.
2. Complete authentication, RBAC, and audit logging for intranet deployment; do not bind beyond loopback before then.
3. Add run history, richer cancellation/cleanup detail, and a standalone CSV/JSON redraw CLI.

Before live work, run connection and query-only Generator discovery, confirm RF OFF, measurement RDY, and an empty error queue, then follow the [hardware SOP](docs/hardware-test-sop.md).
