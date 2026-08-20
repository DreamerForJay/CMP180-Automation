# CMP180 響應式 Web GUI 使用指南 / Responsive Web GUI Guide

## 中文版本

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

實機 SingleShot 已完成 HIL，可用 `--enable-hardware` 在本機啟用；固定三點頻率與四點有效功率掃描已完成 CLI HIL，但 Web progress／cancel／emergency cleanup 尚未驗證，因此 Web 實機 Sweep 仍保持鎖定。硬體模式沒有登入／RBAC，目前禁止綁定非 loopback 位址。模式集中顯示於右上角與量測工作區狀態，不使用遮擋內容的底部常駐列。

Mock 頻率與功率掃描現在使用非同步 Job API，提供 queued／running／stopping／complete／cancelled／failed 狀態、逐點進度、單一 active-job 鎖與 cooperative cancel。2026-08-20 瀏覽器驗收確認 11 點頻率掃描可在第 3 點取消並只保存 3 點 partial result；四點功率掃描顯示 4/4 complete，CSV／JSON／HTML 為可點連結，窄版 viewport 無水平溢出。這只驗證 Mock Job 與 UI；尚未授權實機 Web sweep。

實機 Web Sweep 只接上 CLI-HIL 核准的固定 profile：頻率 6085／6105／6125 MHz，以及功率 -55／-50／-45／-40 dBm。取消只在每點完成 STOP／RF Off 的邊界生效，並由最外層再次 STOP／ABORt、RF Off 與 read-back。2026-08-20 現場 Web HIL 已完成：頻率掃描 3/3 正常完成；功率掃描於第一點後送出取消，安全邊界於 2/4 停止並保存 partial artifacts。獨立查詢確認 RF `OFF`、measurement `RDY`、error queue empty。

前三個量測頁籤刻意保留為「示範單點／示範頻掃／示範功掃」：它們供教學、UI
驗證、CI 與沒有儀器時開發，永遠不送出 SCPI 或 RF。真正的 SingleShot、三點頻掃與
四點功掃集中在「實機量測」頁。若顯示 `LOCKED`，代表本次 server 未以
`--enable-hardware` 啟動，不代表實機功能尚未完成；只有本機 loopback 模式可顯示
`ARMED`。狀態 badge、安全檢查燈與模式選單都有雙語滑鼠提示。

每次結果在 artifact 按鈕上方顯示相對輸出位置，例如
`output/20260820T110057Z_real-frequency-sweep_afb64617df/`。GUI 不顯示絕對路徑，避免
洩漏使用者名稱或公司目錄；使用者可直接點 HTML／CSV／JSON／Metadata。

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
python -m cmp180_evm.web --enable-hardware
```

GUI 右上角會顯示「實機模式」，工作區顯示「已啟用實機控制」，實機頁顯示
`ARMED`。執行前必須：

1. 確認 RF1.1 → RF1.5 cable。
2. 確認操作員位於 CMP180 旁。
3. 在確認欄輸入完全相同的 `RF1.1-RF1.5`。
4. 勾選操作員在場。

目前實機頁面只允許已驗證的 6105 MHz、320 MHz、-40 dBm、expected power -20 dBm profile；不能從網頁任意提高功率或變更頻段。每次 run 保存非模擬 CSV、JSON、metadata 與 raw response。錯誤時 service 會執行 workflow cleanup，並額外進行 emergency STOP／ABORt、RF Off 與最終 state read-back。

2026-08-19 已完成 Web API 端到端 HIL 驗收。錯誤確認資料先被 HTTP 400 拒絕；正確確認後完成新實機 SingleShot，結果為 EVM All -36.51843 dB、Burst Power -40.18850 dBm、Frequency Error 6.986657 Hz，run ID `2d099714ee`。回傳 `simulated=false`，CSV 與 raw artifact 均存在；獨立收尾稽核確認 RF `OFF`、measurement `RDY` 且 error queue 為空。

第二輪介面採用公司 TMXLAB KIT Demo 的深色儀器控制台作為資訊層級參考，以青色表示可操作／量測狀態、紅色表示 RF 風險。接線確認改為可輸入的建議選單；使用者能輸入自訂路徑，但只有已驗證的 `RF1.1-RF1.5` 能解鎖 RF。結果頁使用可點擊的 CSV、JSON、Metadata、Raw SCPI 與 HTML Report 按鈕。獨立「異常測試」頁已移除，改由正常流程即時警告空白接線、未驗證路徑、操作員未在場、重複送出與硬體模式鎖定。

---

## English Version

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

Real hardware SingleShot has completed HIL and can be enabled locally with `--enable-hardware`. The fixed three-point frequency and four-point numeric power sweeps have completed CLI HIL, but Web progress, cancellation, and emergency cleanup remain unverified, so Web hardware Sweep stays locked. Mode is shown in the top-right status and workspace control-state card without a content-obscuring persistent bottom bar.

Mock frequency and power sweeps now use an asynchronous Job API with queued/running/stopping/complete/cancelled/failed states, per-point progress, a single-active-job lock, and cooperative cancellation. Browser acceptance on 2026-08-20 cancelled an 11-point frequency sweep at point 3 and preserved only three partial points. A four-point power sweep displayed 4/4 complete, CSV/JSON/HTML were clickable, and a narrow viewport had no horizontal overflow. This validates only the Mock Job/UI path; it does not authorize Web hardware sweeps.

The Web hardware Sweep path is limited to CLI-HIL-approved fixed profiles: 6085/6105/6125 MHz frequency and -55/-50/-45/-40 dBm power. Cancellation takes effect only at a point boundary after STOP/RF Off, followed by outer STOP/ABORt, RF Off, and read-back. On-site Web HIL passed on 2026-08-20: frequency completed 3/3; power cancellation was requested after the first point and safely stopped at the next boundary with 2/4 partial artifacts. Independent queries confirmed RF `OFF`, measurement `RDY`, and an empty error queue.

The first three measurement tabs intentionally remain Demo Single, Demo Frequency
Sweep, and Demo Power Sweep. They support training, UI validation, CI, and development
without an instrument; they never send SCPI or RF. Real SingleShot, three-point
frequency sweep, and four-point power sweep are grouped under Hardware Measurement.
`LOCKED` means the current server was not started with `--enable-hardware`; it does not
mean hardware scanning is unfinished. Only local loopback mode may show `ARMED`. Status
badges, preflight lights, and the mode selector provide bilingual hover explanations.

Every result shows a relative output location above its artifact buttons, for example
`output/20260820T110057Z_real-frequency-sweep_afb64617df/`. The GUI hides absolute paths
to avoid exposing user names or company directory details. Users can open HTML, CSV,
JSON, and Metadata directly.

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

After the complete Python SingleShot passed, the Web GUI gained a fixed-profile hardware screen. Normal startup remains locked. Use hardware mode only with an operator present and confirmed cabling:

```powershell
python -m cmp180_evm.web --enable-hardware
```

The top-right status displays `Hardware Mode`, the workspace displays
`Hardware control enabled`, and the hardware panel displays `ARMED`. Before a run:

1. Confirm the RF1.1-to-RF1.5 cable.
2. Confirm that an operator is beside the CMP180.
3. Enter the exact confirmation text `RF1.1-RF1.5`.
4. Select the operator-present checkbox.

The hardware screen currently permits only the verified 6105 MHz, 320 MHz, -40 dBm, -20 dBm expected-power profile. The page cannot arbitrarily increase power or change bands. Every run saves non-simulated CSV, JSON, metadata, and raw response artifacts. On error, the service runs workflow cleanup followed by independent emergency STOP/ABORt, RF Off, and final-state read-back.

End-to-end Web API HIL acceptance passed on 2026-08-19. Invalid confirmation data was first rejected with HTTP 400. Correct confirmation then completed a new hardware SingleShot with EVM All -36.51843 dB, Burst Power -40.18850 dBm, Frequency Error 6.986657 Hz, and run ID `2d099714ee`. The response reported `simulated=false`; CSV and raw artifacts existed. Independent final auditing confirmed RF `OFF`, measurement `RDY`, and an empty error queue.

The second UI pass uses the company TMXLAB KIT Demo as an information-hierarchy reference: cyan represents actionable/measurement state and red represents RF risk. Cable confirmation is now an editable suggestion list. Users can type a custom route, but only the verified `RF1.1-RF1.5` route can unlock RF. Results use clickable CSV, JSON, Metadata, Raw SCPI, and HTML Report buttons. The separate Fault Tests screen has been removed; the normal workflow now warns about an empty route, an unverified route, missing operator presence, duplicate submission, and locked hardware mode.
