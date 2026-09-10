# CMP180 響應式 Web GUI 使用指南 / Responsive Web GUI Guide

## 中文版本

### 目前介面層級

主導覽只負責切換首頁、量測、校正、結果、紀錄與說明；每頁只顯示一個主要功能標題。量測頁以「實機量測／示範訓練」切換資料來源，實機表單中的進階範圍統一稱為「掃描設定」。說明頁提供可直接複製的 PowerShell 指令，會先切換到專案目錄，且不包含 PowerShell 畫面上的 `PS` 提示符。

首頁 Hero 先顯示 CMP180 Blender 渲染圖，點擊「啟用 360° 檢視」才下載本機立體模型與檢視器。支援拖曳、觸控、縮放、視角快捷鍵、重設、可暫停自轉與全螢幕；其他工作區或背景頁面會暫停自轉。載入失敗保留靜態圖並提供重試，不依賴外部 CDN、不綁定量測或 RF API。操作與重建說明見 [3D 檢視器](cmp180-3d-viewer.md)；下一階段改善見 [全站檢視計畫](web-audit-2026-09-10.md)。

實機量測與示範訓練都使用「單點／頻率掃描／功率掃描」三級分頁。切換實機分頁會同步後端 action；單點不顯示掃描欄位，只有頻率或功率掃描才展開掃描設定。結果圖表使用固定 900 × 300 工程座標；滾輪只縮放 X 軸，拖曳只水平平移且限制在資料畫布內。靠近量測點會顯示十字游標與完整 EVM、功率、頻率誤差及 VALID／INVALID 狀態。

說明頁的命令順序為 Git clone、進入專案、建立 Python 3.11 虛擬環境、安裝、啟動 Demo、驗證兩份 YAML、唯讀連線檢查、由 `results.csv` 產生 SVG，以及由既有 Run 資料夾重建 HTML 報告。實機服務命令獨立收合；啟動服務本身不會送 RF。

### 目前可測試範圍

Web GUI 同時提供完整 Mock 操作，以及預設鎖定、只允許本機 loopback bind 的固定 profile 實機 SingleShot。Mock 頁面不會控制 CMP180，也不會開啟 RF。可測試：

- 繁體中文／英文即時切換。
- 亮／暗主題切換（右上角按鈕，預設為暗色，選擇會存在瀏覽器 `localStorage`，下次開啟延續）。
- 手機、平板與桌面響應式版面。
- 單一頻點 Mock 量測。
- 起始頻率、結束頻率與步進的 Mock 頻率掃描。
- 固定頻率、起始功率、結束功率與步進的 Mock 功率掃描（Power vs EVM）。
- EVM、Burst Power、Frequency Error 結果表格與圖表（X 軸依掃描類型自動切換頻率或功率）。
- 每次 run 輸出 CSV、JSON、metadata 與離線 HTML report。
- Demo 結果在畫面顯示 `示範資料`／`DEMO DATA`，artifact 仍保存
  `simulated=true`，不得視為 CMP180 實機量測。

實機 SingleShot 已完成 HIL；一般本機啟動會直接提供受保護的實機控制，`--demo-only` 則停用儀器連線。固定三點頻率與四點有效功率掃描已完成 CLI HIL，但新的自訂 Profile 仍須逐一 HIL。硬體模式沒有登入／RBAC，目前禁止綁定非 loopback 位址。模式集中顯示於右上角與量測工作區狀態，不使用遮擋內容的底部常駐列。

Mock 頻率與功率掃描現在使用非同步 Job API，提供 queued／running／stopping／complete／cancelled／failed 狀態、逐點進度、單一 active-job 鎖與 cooperative cancel。2026-08-20 瀏覽器驗收確認 11 點頻率掃描可在第 3 點取消並只保存 3 點 partial result；四點功率掃描顯示 4/4 complete，CSV／JSON／HTML 為可點連結，窄版 viewport 無水平溢出。這只驗證 Mock Job 與 UI；尚未授權實機 Web sweep。

實機 Web Sweep 會使用畫面上「掃描設定」建立的同一份自訂計畫，不再把使用者輸入改跑固定 6085／6105／6125 MHz profile。送出前 Web 會先呼叫 preview API 產生點位、fingerprint 與 RF workflow 檢查結果；若目前 workflow 不接受該組合，畫面會顯示拒絕原因且不送出 RF。取消只在每點完成 STOP／RF Off 的邊界生效，並由最外層再次 STOP／ABORt、RF Off 與 read-back。2026-08-20 現場 Web HIL 已完成：頻率掃描 3/3 正常完成；功率掃描於第一點後送出取消，安全邊界於 2/4 停止並保存 partial artifacts。獨立查詢確認 RF `OFF`、measurement `RDY`、error queue empty。

實機頁另新增 `GPRF 能力掃描`，使用 CMP180 的 GPRF Generator／Measurement power workflow 展示儀器 tune 與功率量測能力。此模式可在 400 MHz–8 GHz 規劃頻率掃描，或在固定頻率下規劃功率掃描，並保存 CSV／JSON／metadata／HTML artifacts；但結果欄位是 `measured_power_dbm` 與 `reliability`，不是 WLAN EVM、不是 OFDM 解調，也不得作為 compliance claim。GPRF 執行仍需 `RF1.1-RF1.5` route、操作員在場、最後確認與 RF Off cleanup；PA profile 不要求固定外部衰減器，Web 可用「載入 approved PA profile」帶入無衰減器安全裁切範圍，CLI 也會依當次 fixture 自動夾住 safe stop。若任一點出現 SCPI error、reliability 非 0 或 SA safe limit，會在該點 STOP／RF Off 後停止後續掃描並保存 partial artifact。

GPRF 結果圖表會以高對比藍色曲線顯示實測功率，並以橘色虛線標出 Expected Power。Power 軸掃描的 Burst Power 圖使用 `Expected Power = Generator Power` 對角線，適合判讀線性度；Frequency 軸掃描則使用固定 expected power 水平線，適合判讀功率平坦度。`Power Error (dB)` 指標定義為 `measured - expected`；切換到該指標時，0 dB 參考線代表完全貼齊設定功率。這裡的 expected curve 是圖表判讀基準，不代表每一點都會把 Analyzer `ENPower` SCPI 安全設定改成相同數值。Summary 會直接顯示 Average Power、Expected Power、Mean Error、Max |Error|、Peak-to-Peak Ripple、Std Dev 與 Valid 點數，適合用於說明 RF1.1-RF1.5 loopback 下的儀器功率平坦度或線性度。亮色與暗色主題都使用高對比線條，避免深色背景上曲線與圓點不可讀。

GPRF 名稱跟隨掃描軸：Frequency 軸顯示 `GPRF Frequency Sweep – Power Flatness`；Power 軸顯示 `GPRF Power Sweep – Linearity`。切換量測頁籤或 Axis 時，頁首與 Review 摘要會立即同步。結果圖的 X、Y 軸都明確標示工程單位；X 軸為 Frequency (MHz) 或 Generator Power (dBm)，Y 軸則顯示目前選取指標的單位。

量測紀錄可只勾選一筆後按「查看所選圖表」，也可勾選 2–8 筆進行比較。兩種模式都只讀取既有 `/api/runs` artifacts，不會啟動量測或 RF；單筆模式仍可切換指標、Zoom／Pan、A/B 游標與匯出圖表。

### 下一步規格範圍量測規劃

1. **GPRF 儀器能力範圍**：以 RF1.1 Generator output → RF1.5 Analyzer input 先跑 4–8 GHz／100 MHz step／-40 dBm 的 flatness 基準；若現場時間允許，再補 400 MHz–8 GHz 的粗掃。這只宣稱 CMP180 tune 與 power measurement 能力，不宣稱 WLAN EVM 或 DUT compliance。
2. **WLAN EVM 已核准範圍**：重跑 P0 6 GHz／320 MHz golden baseline 與 2.4/5/6 GHz 已列入 HIL Campaign 的 WLAN sections，保存每個 section 的 CSV／JSON／HTML／metadata。這些才是 WLAN EVM workflow 的展示主體。
3. **重複性與追溯性**：對 P0 golden baseline 做 N=3 repeatability，確認 artifacts、RF Off cleanup、measurement `RDY` 與 error queue empty 都一致。
4. **暫不宣稱項目**：其他 RF routes、500 MHz analysis bandwidth、雙 VSA/VSG 需先 query-only discovery 與安全審核；未完成前只列為待核准能力，不放進主管展示結論。

前三個量測頁籤刻意保留為「示範單點／示範頻掃／示範功掃」：它們供教學、UI
驗證、CI 與沒有儀器時開發，永遠不送出 SCPI 或 RF。真正的 SingleShot、三點頻掃與
四點功掃集中在「實機量測」頁。若顯示 `LOCKED`，代表本次 server 使用
`--demo-only` 啟動，不代表實機功能尚未完成；只有本機 loopback 模式可顯示
`ARMED`。狀態 badge、安全檢查燈與模式選單都有雙語滑鼠提示。

每次結果在 artifact 按鈕上方顯示相對輸出位置，例如
`output/20260820T110057Z_real-frequency-sweep_afb64617df/`。GUI 不顯示絕對路徑，避免
洩漏使用者名稱或公司目錄；使用者可直接點 HTML／CSV／JSON／Metadata。

若按鈕出現 `Not found`，通常是更新程式後仍有舊 Python Web process 佔用相同 port。
新版 server 使用 exclusive bind，第二個相同 host／port 的 instance 會在啟動時直接失敗，
不再讓請求隨機落到不同版本。正常關閉請在啟動 Web 的 PowerShell 按 `Ctrl+C`，更新後再
啟動一次；不要同時開多個 `python -m cmp180_evm.web`。

目前 GUI 是功能 MVP。第二輪 UI/UX 將加入即時 workflow step、執行動畫、取消與 cleanup 狀態、欄位連動驗證、圖表 tooltip／縮放、artifact 下載按鈕、run history，以及更完整的空白／錯誤／手機版狀態。

「量測紀錄」頁會唯讀掃描本機 `output/` 中有效的 metadata，依時間由新到舊顯示
實機／示範來源、狀態、完成點數與 Run ID。使用者可直接開啟 HTML、CSV、JSON 與
Metadata；API 不回傳本機絕對路徑或 raw SCPI。按「重新整理」即可看到剛完成的 run，
此功能本身不會連線儀器、啟動量測或開啟 RF。

### 啟動方式

在專案根目錄執行：

```powershell
.\.venv\Scripts\Activate.ps1
python -m cmp180_evm.web
```

看到以下訊息後，以瀏覽器開啟 `http://127.0.0.1:8765`：

```text
CMP180 Web GUI: http://127.0.0.1:8765
Mode: MOCK only; real-hardware controls are locked.
```

停止服務時，在 PowerShell 按 `Ctrl+C`。

### 建議驗收流程

1. 在「單點量測」保留 6105 MHz、320 MHz、-40 dBm，按「執行 Mock 單點」。
2. 確認頁面切到「結果與圖表」，並顯示 `示範資料`。
3. 到「頻率掃描」輸入 5925、6125、20 MHz，執行 Mock Sweep。
4. 確認產生 11 個資料點、圖表與 PASS/FAIL 表格。
5. 到「功率掃描」保留預設 -60 至 -40 dBm、5 dBm 步進，執行 Mock 功率掃描，確認圖表 X 軸改成 dBm、EVM 隨功率變化。
6. 按右上角 `EN`，確認所有主要文字切換英文。
7. 縮小瀏覽器寬度，確認欄位由雙欄改成單欄，表格可水平捲動。
8. 到畫面底部確認 CSV、JSON 與 HTML report 的輸出位置。

### 輸出位置

每次 Mock run 會建立：

```text
output/<timestamp>_<test-name>_<run-id>/
├─ metadata.json
├─ results.csv
├─ results.json
└─ report.html
```

這些檔案只包含模擬資料。正式實機版會沿用相同 schema，另外保存 config snapshot、原始 SCPI 回應、logs 與 plots。

### 受保護的實機單點模式

完整 Python SingleShot 已通過後，Web GUI 新增固定 profile 的實機頁面。預設啟動仍鎖定；只有操作員在場且確認接線時才使用：

```powershell
python -m cmp180_evm.web --host 127.0.0.1 --port 8765
```

GUI 右上角會顯示「實機模式」，工作區顯示「已啟用實機控制」，實機頁顯示
`ARMED`。執行前必須：

1. 確認 RF1.1 → RF1.5 cable。
2. 確認操作員位於 CMP180 旁。
3. 在確認欄輸入完全相同的 `RF1.1-RF1.5`。
4. 選擇單點、頻率掃描或功率掃描。掃描會直接使用畫面上的 Start／Stop／Step／Dwell／Bandwidth／Power 設定，不會改跑固定 profile。只有再次確認後才會送出 RF，取消則不送出任何 RF。

上述操作員確認可直接在 Web 完成，不需要每次回到對話工具重新輸入授權文字；但後端安全包絡、接線路徑檢查與錯誤 cleanup 不可停用。
4. 勾選操作員在場。

目前規劃介面可輸入 400 MHz–8 GHz，但真正送 RF 仍須通過目前 workflow 的 routing、bandwidth、power、dwell、point-count 與 cleanup 驗證。Web 不會隱藏替換參數；若輸入 400 MHz 這類超出目前 RF workflow 的組合，會回報拒絕原因，不會偷跑已驗證的 6 GHz profile。每次 run 保存非模擬 CSV、JSON、metadata 與 raw response。錯誤時 service 會執行 workflow cleanup，並額外進行 emergency STOP／ABORt、RF Off 與最終 state read-back。

EVM limit 判定使用「dB 越負通常越好」的方向：量測 EVM 必須小於或等於 `maximum_evm_db` 才能通過。例如 limit 為 -32 dB 時，-36 dB 通過、-28 dB 失敗。沒有正式 approved limit profile 的實機結果只顯示 `MEASURED`，不宣稱 PASS。Power Reference Plane 尚未套用正式 Path Loss／Calibration Profile；metadata 會標示 `calibration_applied=false`，因此目前不能把 -45 dBm 設定值解讀成已補償後的正式參考面功率。

2026-08-19 已完成 Web API 端到端 HIL 驗收。錯誤確認資料先被 HTTP 400 拒絕；正確確認後完成新實機 SingleShot，結果為 EVM All -36.51843 dB、Burst Power -40.18850 dBm、Frequency Error 6.986657 Hz，run ID `2d099714ee`。回傳 `simulated=false`，CSV 與 raw artifact 均存在；獨立收尾稽核確認 RF `OFF`、measurement `RDY` 且 error queue 為空。

第二輪介面採用公司 TMXLAB KIT Demo 的深色儀器控制台作為資訊層級參考，以青色表示可操作／量測狀態、紅色表示 RF 風險。接線確認改為可輸入的建議選單；使用者能輸入自訂路徑，但只有已驗證的 `RF1.1-RF1.5` 能解鎖 RF。結果頁使用可點擊的 CSV、JSON、Metadata、Raw SCPI 與 HTML Report 按鈕。獨立「異常測試」頁已移除，改由正常流程即時警告空白接線、未驗證路徑、操作員未在場、重複送出與硬體模式鎖定。

---

### 2026-08-25 介面與實機啟動更新

- 實機與自訂安全掃描由使用者的 Windows 工作階段以 `python -m cmp180_evm.web --host 127.0.0.1 --port 8765` 啟動；需要純示範時加入 `--demo-only`。啟動伺服器本身不會送出 RF；仍需在 Web 頁面完成接線、操作員與最終摘要確認。
- 首頁提供互動 RF 系統架構，說明量測計畫、安全閘門、CMP180、結果正規化與 artifacts 的資料流。
- 結果圖表支援滾輪縮放、拖曳平移、Reset，以及 A/B 測點游標。這些功能只改變瀏覽器檢視，不會修改原始結果或重新量測。
- 實機與首頁採響應式安全邊距；亮色模式的刪除按鈕維持紅色破壞性操作語意。

### 直接式實機控制

實機頁以單點、頻率掃描與功率掃描三個分頁直接設定工作，不再顯示 Generator／Analyzer／Measurement Flow 裝飾積木，也不使用量測模式下拉選單。Run 仍走既有 route／操作員／Profile／最終 RF 摘要確認。多點掃描的 Pause 只在目前點完成 STOP 與 RF Off 後生效；Resume 從下一點繼續，Stop 執行 cooperative cancellation 並保留 partial artifacts。SingleShot 不支援中途 Pause。

實機頁採用固定 SOP 排版：STEP 1 先選 SingleShot、WLAN frequency sweep、WLAN power sweep 或 GPRF power sweep 並設定數值；STEP 2 才確認 RF1.1 Generator output 到 RF1.5 Analyzer input 的接線與操作員在場；STEP 3 顯示目前計畫 Review；STEP 4 才允許送出實機量測。GPRF power sweep 只用來展示 CMP180 調諧與功率讀值能力，不會被標示成 WLAN EVM。

掃描設定固定顯示，不使用可收合選單。頻率 Start、Stop、Step 與 Center Frequency 各自有緊鄰欄位的 MHz／GHz 選單；切換會先換算為 Hz 再顯示等值數字。量測 Job 每完成一點且完成 cleanup／RF Off 後，API 才發布該點快照，頁面同步更新進度、最新 EVM 與即時趨勢，不會為了畫圖額外送 SCPI。

頻率／功率掃描按下「執行實機量測」時，會先用目前欄位建立 preview，再以同一份計畫送出 custom-sweep；前端不再呼叫固定三點／四點 profile endpoint。若 preview 顯示不可執行，按鈕會停在規劃狀態並顯示後端拒絕原因，不會改跑其他 profile。

### HIL 批次工具

1. 以本機實機模式啟動 Web，開啟「HIL 批次」。
2. 按「準備／重新檢查矩陣」。工具只執行設定與既有 profile gate，不會在這一步送 RF。
3. 頁面會依重要度排序：P0 黃金點最優先，P1 為已核准的 11 個 WLAN EVM section，P2 為功率邊界，P3／HOLD 為尚未核准的 route、analysis bandwidth、waveform 或雙 VSA/VSG 能力；同一重要度內採 2.4G→5G→6G、頻寬由小到大的現場常用順序。
4. `READY` 表示現有 workflow 可執行；`BLOCKED` 會顯示缺少的 band setter、waveform、route profile 或專用 backend，不會改跑 RF1.1→RF1.5 的既有案例。
5. 依畫面「目前接線指示」確認 RF1.1 Generator output → RF1.5 Analyzer input，確認操作員在場，再按單列 `Run` 或「執行下一個 READY」。
6. Pause／Stop 經 Job API 在點位 cleanup／RF Off 邊界生效；成功、失敗與 artifact 路徑保存於 `output/hil-campaign/state.json`。
7. 關閉瀏覽器不會清除進度。若 Web server 在執行中重啟，該列轉為 `INTERRUPTED`；重新 Prepare 後才能再跑，避免把消失的背景 thread 誤標成執行中。

重設 Campaign 只重設矩陣狀態，不刪除既有量測 artifacts。新增 route、bandwidth 或 waveform 的 RF 權限仍須先補入正式 command registry、workflow 與 capability profile；介面按鈕本身不會繞過後端限制。

### 2026-09-10 校正表單與匯出防呆更新

校正頁 7 個欄位改為明確的 `label for` 綁定，點欄位名稱會直接聚焦到輸入框；`?` 說明按鈕移到欄位右上角，功能不變。校正工具列的 adapter 下拉在 640px 以下獨佔一行，390px 手機不再整頁橫向捲動。

結果頁的 SVG、Web PNG 與 CSV 匯出在圖表沒有測點時會停用並顯示「目前沒有可匯出的測點」，避免匯出空白但看似正式的報告；取得測點後自動恢復。此變更只影響瀏覽器端匯出行為，不改變任何量測、SCPI 或 RF 邏輯。

## English Version

### Current interface hierarchy

The primary navigation only switches Home, Measurement, Calibration, Results, Runs, and Help, and each page presents one main functional heading. Measurement uses Hardware/Demo Training to select the data source, while advanced hardware ranges are consistently named Sweep Setup. Help provides copyable PowerShell commands that change to the project directory first and do not include the visual `PS` prompt.

The home-page hero initially displays a CMP180 Blender render; selecting “Explore in 360°” loads the local model and viewer. Drag, touch, zoom, view presets, reset, optional auto-rotation, and fullscreen are supported. Auto-rotation pauses when the viewer is hidden or the page is in the background. Failed loads preserve the still image and offer retry. There is no external CDN or measurement/RF API binding. See the [3D viewer guide](cmp180-3d-viewer.md) and [website improvement plan](web-audit-2026-09-10.md).

Hardware and Demo Training both use Single, Frequency Sweep, and Power Sweep tabs. A hardware-tab change synchronizes the backend action. Single hides sweep fields, while frequency or power opens Sweep Setup. Result charts use a fixed 900 by 300 engineering coordinate system. The wheel zooms only the X axis, panning is horizontal and clamped to the data canvas, and the Y axis cannot drift. Moving near a point displays a crosshair and complete EVM, power, frequency-error, and VALID/INVALID values.

Help now proceeds through Git clone, entering the repository, creating a Python 3.11 virtual environment, installation, Demo startup, both YAML validations, query-only connection testing, SVG generation from `results.csv`, and HTML-report reconstruction from a saved run directory. The hardware server command is separately collapsed; starting the server does not itself transmit RF.

### Currently testable scope

The Web GUI currently provides a complete mock workflow. It does not control the CMP180 or enable RF. You can test:

- Instant Traditional Chinese/English switching.
- Light/dark theme toggle (top-right button; defaults to dark; the choice persists in browser `localStorage`).
- Responsive phone, tablet, and desktop layouts.
- A mock single-frequency measurement.
- A mock frequency sweep using start, stop, and step.
- A mock power sweep at a fixed frequency using start power, stop power, and step (Power vs EVM).
- EVM, Burst Power, and Frequency Error result tables and plots (the chart X axis switches between frequency and power automatically depending on the sweep type).
- CSV, JSON, metadata, and offline HTML output for every run.
- Demo results display `DEMO DATA`; artifacts retain `simulated=true` and must not be
  treated as real CMP180 measurements.

Real hardware SingleShot has completed HIL. Normal local startup exposes guarded hardware control, while `--demo-only` disables instrument access. The fixed three-point frequency and four-point numeric power sweeps completed HIL, but each new custom profile still requires controlled HIL. Mode is shown in the top-right status and workspace control-state card without a content-obscuring persistent bottom bar.

Mock frequency and power sweeps now use an asynchronous Job API with queued/running/stopping/complete/cancelled/failed states, per-point progress, a single-active-job lock, and cooperative cancellation. Browser acceptance on 2026-08-20 cancelled an 11-point frequency sweep at point 3 and preserved only three partial points. A four-point power sweep displayed 4/4 complete, CSV/JSON/HTML were clickable, and a narrow viewport had no horizontal overflow. This validates only the Mock Job/UI path; it does not authorize Web hardware sweeps.

The Web hardware Sweep path now uses the exact custom plan shown in Sweep Setup instead of silently falling back to the fixed 6085/6105/6125 MHz profile. Before execution, the Web UI calls the preview API to build points, compute the fingerprint, and revalidate the current RF workflow. If the workflow rejects the plan, the UI shows the rejection reason and transmits no RF. Cancellation takes effect only at a point boundary after STOP/RF Off, followed by outer STOP/ABORt, RF Off, and read-back. On-site Web HIL passed on 2026-08-20: frequency completed 3/3; power cancellation was requested after the first point and safely stopped at the next boundary with 2/4 partial artifacts. Independent queries confirmed RF `OFF`, measurement `RDY`, and an empty error queue.

The hardware page also adds `GPRF Capability Sweep`, which uses the CMP180 GPRF Generator/Measurement power workflow to demonstrate instrument tune and power-measurement capability. This mode can plan frequency sweeps across 400 MHz to 8 GHz, or power sweeps at a fixed frequency, and saves CSV, JSON, metadata, and HTML artifacts. Its result fields are `measured_power_dbm` and `reliability`; it is not WLAN EVM, not OFDM demodulation, and must not be used as a compliance claim. GPRF execution still requires the `RF1.1-RF1.5` route, operator presence, final confirmation, and RF Off cleanup. The PA profile does not require one fixed external attenuator; it clips the safe stop from the current fixture. If any point reports a SCPI error, non-zero reliability, or the SA safe limit, the worker stops after that point's STOP/RF Off boundary and saves partial artifacts.

GPRF result charts show measured power as a high-contrast blue trace and draw an orange dashed Expected Power reference line. A power-axis Burst Power chart uses the `Expected Power = Generator Power` diagonal for linearity review; a frequency-axis sweep uses a fixed expected-power horizontal line for power-flatness review. The `Power Error (dB)` metric is defined as `measured - expected`; when selected, a 0 dB reference line represents perfect agreement with the configured power. The expected curve is a chart interpretation reference, not a promise that every point writes the Analyzer `ENPower` SCPI safety setting to the same value. The Summary displays Average Power, Expected Power, Mean Error, Max |Error|, Peak-to-Peak Ripple, Std Dev, and Valid points so the RF1.1-RF1.5 loopback flatness or linearity can be explained directly. Both light and dark themes use high-contrast trace colors so curves and markers remain readable.

GPRF naming follows the selected sweep axis. Frequency axis is shown as `GPRF Frequency Sweep – Power Flatness`; power axis is shown as `GPRF Power Sweep – Linearity`. The page heading and Review summary update immediately when the measurement tab or Axis changes. Result charts label both axes with engineering units: Frequency (MHz) or Generator Power (dBm) on X, and the selected metric's unit on Y.

Run History now accepts either one selected run for plotting or 2–8 runs for comparison. Both modes only read existing `/api/runs` artifacts and never start a measurement or RF. Single-run mode retains metric switching, zoom/pan, A/B cursors, and chart export.

### Next spec-range measurement plan

1. **GPRF instrument-capability range**: first run the RF1.1 Generator output to RF1.5 Analyzer input flatness baseline at 4–8 GHz, 100 MHz step, and -40 dBm. If on-site time allows, add a coarse 400 MHz–8 GHz sweep. This claims CMP180 tune and power-measurement capability only, not WLAN EVM or DUT compliance.
2. **Approved WLAN EVM range**: rerun the P0 6 GHz / 320 MHz golden baseline and the 2.4/5/6 GHz WLAN sections listed in HIL Campaign, preserving CSV, JSON, HTML, and metadata artifacts for each section. These are the main WLAN EVM workflow demonstrations.
3. **Repeatability and traceability**: run N=3 repeatability on the P0 golden baseline and confirm artifacts, RF Off cleanup, measurement `RDY`, and an empty error queue are consistent.
4. **Do not claim yet**: other RF routes, 500 MHz analysis bandwidth, and dual VSA/VSG require query-only discovery and safety approval first. Until then they remain unapproved capabilities and must not be used in supervisor-facing conclusions.

The first three measurement tabs intentionally remain Demo Single, Demo Frequency
Sweep, and Demo Power Sweep. They support training, UI validation, CI, and development
without an instrument; they never send SCPI or RF. Real SingleShot and the custom-plan
frequency/power sweep entry points are grouped under Hardware Measurement.
`LOCKED` means the current server was started with `--demo-only`; it does not
mean hardware scanning is unfinished. Only local loopback mode may show `ARMED`. Status
badges, preflight lights, and the mode selector provide bilingual hover explanations.

Every result shows a relative output location above its artifact buttons, for example
`output/20260820T110057Z_real-frequency-sweep_afb64617df/`. The GUI hides absolute paths
to avoid exposing user names or company directory details. Users can open HTML, CSV,
JSON, and Metadata directly.

If a button reports `Not found`, a stale Python Web process may still own the same port
after a code update. The current server uses an exclusive bind: a second instance on the
same host/port fails immediately instead of randomly splitting requests across versions.
Stop the Web process with `Ctrl+C`, then start it once after updating; do not run multiple
`python -m cmp180_evm.web` instances on the same port.

The current GUI is a functional MVP. The second UI/UX pass adds live workflow steps, running animation, cancellation and cleanup state, cross-field validation, plot tooltips/zoom, artifact download buttons, run history, and stronger empty/error/mobile states.

The Run History page read-only scans valid metadata under local `output/` and lists runs
newest first with hardware/demo source, status, completed-point count, and Run ID. Users
can open HTML, CSV, JSON, and Metadata directly. The API does not expose absolute local
paths or raw SCPI. Refresh shows newly completed runs; this feature never connects to the
instrument, starts a measurement, or enables RF.

### Start the GUI

Run from the project root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m cmp180_evm.web
```

When the messages below appear, open `http://127.0.0.1:8765` in a browser:

```text
CMP180 Web GUI: http://127.0.0.1:8765
Mode: MOCK only; real-hardware controls are locked.
```

Press `Ctrl+C` in PowerShell to stop the server.

### Recommended acceptance flow

1. Keep 6105 MHz, 320 MHz, and -40 dBm on the Single screen, then select Run Mock Single.
2. Confirm the page switches to Results & Plots and displays `DEMO DATA`.
3. On Frequency Sweep, enter 5925, 6125, and 20 MHz, then run the mock sweep.
4. Confirm that 11 points, a plot, and a PASS/FAIL table appear.
5. On Power Sweep, keep the default -60 to -40 dBm range with a 5 dBm step, run the mock power sweep, and confirm the chart X axis switches to dBm with EVM varying by power.
6. Select `EN`/`中文` at the top right and confirm that primary UI text changes language.
7. Narrow the browser and confirm fields collapse from two columns to one while the table scrolls horizontally.
8. Confirm the CSV, JSON, and HTML report paths at the bottom of the results page.

### Output location

Every mock run creates:

```text
output/<timestamp>_<test-name>_<run-id>/
├─ metadata.json
├─ results.csv
├─ results.json
└─ report.html
```

These files contain simulated data only. The real-hardware version will retain the same schema and add a configuration snapshot, raw SCPI responses, logs, and plots.

### Guarded hardware single mode

After the complete Python SingleShot passed, the Web GUI gained a guarded hardware screen. Use hardware mode only with an operator present and confirmed cabling:

```powershell
python -m cmp180_evm.web --host 127.0.0.1 --port 8765
```

The top-right status displays `Hardware Mode`, the workspace displays
`Hardware control enabled`, and the hardware panel displays `ARMED`. Before a run:

1. Confirm the RF1.1-to-RF1.5 cable.
2. Confirm that an operator is beside the CMP180.
3. Select or enter the route `RF1.1-RF1.5`.
4. Choose Single, Frequency Sweep, or Power Sweep. Sweeps use the Start/Stop/Step/Dwell/Bandwidth/Power values currently shown on the page and never substitute a fixed profile. RF starts only after the final browser confirmation; cancelling transmits no RF.

The operator can complete these confirmations entirely in the Web UI and does not need
to repeat an authorization phrase in a chat tool. Backend safety envelopes, route checks,
and deterministic error cleanup remain mandatory.

The planning UI accepts 400 MHz to 8 GHz, but RF transmission must still pass the current workflow checks for routing, bandwidth, power, dwell, point count, and cleanup. The Web UI does not hide or replace parameters: if a 400 MHz plan is outside the current RF workflow, the page reports the rejection reason and does not run a verified 6 GHz profile instead. Every run saves non-simulated CSV, JSON, metadata, and raw response artifacts. On error, the service runs workflow cleanup followed by independent emergency STOP/ABORt, RF Off, and final-state read-back.

EVM limit evaluation uses the correct "more negative is normally better" dB direction: measured EVM must be less than or equal to `maximum_evm_db` to pass. For example, with a -32 dB limit, -36 dB passes and -28 dB fails. Hardware results without an approved limit profile are shown as `MEASURED`, not PASS. Power Reference Plane compensation is not yet applied; metadata reports `calibration_applied=false`, so a -45 dBm setting must not be interpreted as a formally compensated reference-plane power.

End-to-end Web API HIL acceptance passed on 2026-08-19. Invalid confirmation data was first rejected with HTTP 400. Correct confirmation then completed a new hardware SingleShot with EVM All -36.51843 dB, Burst Power -40.18850 dBm, Frequency Error 6.986657 Hz, and run ID `2d099714ee`. The response reported `simulated=false`; CSV and raw artifacts existed. Independent final auditing confirmed RF `OFF`, measurement `RDY`, and an empty error queue.

The second UI pass uses the company TMXLAB KIT Demo as an information-hierarchy reference: cyan represents actionable/measurement state and red represents RF risk. Cable confirmation is now an editable suggestion list. Users can type a custom route, but only the verified `RF1.1-RF1.5` route can unlock RF. Results use clickable CSV, JSON, Metadata, Raw SCPI, and HTML Report buttons. The separate Fault Tests screen has been removed; the normal workflow now warns about an empty route, an unverified route, missing operator presence, duplicate submission, and locked hardware mode.
### 2026-08-25 UI and hardware-startup update

- Real and custom safe sweeps are served from the user's Windows session with `python -m cmp180_evm.web --host 127.0.0.1 --port 8765`; add `--demo-only` for training. Starting the server does not transmit RF. Route, operator-presence, and final summary confirmation are still required in the Web UI.
- The home page includes an interactive RF system architecture that explains the flow through planning, the safety gate, CMP180 control, result normalization, and artifacts.
- Result charts support wheel zoom, drag pan, reset, and A/B point cursors. These controls only change the browser view; they do not modify source results or start a measurement.
- The hardware workspace and home page use responsive safe margins. Destructive Delete actions remain red in the light theme.

### Direct hardware controls

The hardware page uses direct Single, Frequency Sweep, and Power Sweep tabs. Decorative Generator, Analyzer, and Measurement Flow blocks and the measurement-mode dropdown have been removed. Run still follows the existing route/operator/profile/final-RF-summary confirmations. For a multi-point sweep, Pause takes effect only after the current point completes STOP and RF Off; Resume continues with the next point, while Stop performs cooperative cancellation and preserves partial artifacts. SingleShot cannot pause mid-transaction.

The hardware page now follows a fixed SOP layout: STEP 1 selects SingleShot, WLAN frequency sweep, WLAN power sweep, or GPRF power sweep and sets values; STEP 2 confirms the RF1.1 Generator output to RF1.5 Analyzer input cable and operator presence; STEP 3 reviews the active plan; and STEP 4 is the only place where live hardware execution is submitted. GPRF power sweep is presented only as CMP180 tuning and power-readback capability, not as WLAN EVM.

Sweep Setup stays visible rather than using a collapsible control. Start, Stop, Step, and Center Frequency each have an adjacent MHz/GHz selector; switching normalizes through Hz and preserves the physical value. A job publishes each point snapshot only after cleanup/RF Off, allowing the page to update progress, latest EVM, and a live trend without issuing extra SCPI for plotting.

When Frequency Sweep or Power Sweep is executed, the UI first builds a preview from the current fields and then starts `custom-sweep` with the same plan. The frontend no longer calls the fixed three-point or four-point hardware endpoints from the main hardware sweep controls. If preview says the plan is not executable, the page remains in planning state, displays the backend rejection reason, and transmits no RF.
### HIL campaign tool

1. Start the Web application locally in hardware mode and open **HIL Campaign**.
2. Select **Prepare / Recheck Matrix**. This applies configuration and the existing profile gate only; it transmits no RF.
3. The page sorts cases by importance: P0 is the golden point, P1 covers the approved 11 WLAN EVM sections, P2 covers the power boundary, and P3/HOLD covers unapproved routes, analysis bandwidth, waveform, or dual VSA/VSG capabilities. Within the same priority, cases follow the common operator order: 2.4G, 5G, 6G, and lower bandwidth before higher bandwidth.
4. `READY` means the current workflow can execute the case. `BLOCKED` identifies a missing band setter, waveform, route profile, or dedicated backend and never substitutes the existing RF1.1-to-RF1.5 case.
5. Follow the **Current cabling instruction** on screen, confirm RF1.1 Generator output → RF1.5 Analyzer input and operator presence, then select a row's **Run** button or **Run Next READY**.
6. Pause and Stop use the Job API and take effect at point cleanup/RF-Off boundaries. Success, failure, and artifact locations persist in `output/hil-campaign/state.json`.
7. Closing the browser preserves progress. If the Web server restarts during execution, the row becomes `INTERRUPTED`; Prepare it again before rerunning so a vanished worker is never presented as active.

Reset Campaign clears matrix progress but does not delete measurement artifacts. A new route, bandwidth, or waveform still requires a supported command-registry entry, workflow, and capability profile before RF execution; the UI cannot bypass the backend gate.
