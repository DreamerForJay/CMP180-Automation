# CMP180 響應式 Web GUI 使用指南 / Responsive Web GUI Guide

## 中文版本

### 目前可測試範圍

Web GUI 同時提供完整 Mock 操作，以及預設鎖定、只允許本機 loopback bind 的固定 profile 實機 SingleShot。Mock 頁面不會控制 CMP180，也不會開啟 RF。可測試：

- 繁體中文／英文即時切換。
- 手機、平板與桌面響應式版面。
- 單一頻點 Mock 量測。
- 起始頻率、結束頻率與步進的 Mock frequency sweep。
- EVM、Burst Power、Frequency Error 結果表格與 EVM 圖表。
- 每次 run 輸出 CSV、JSON、metadata 與離線 HTML report。
- Mock 結果一律顯示 `SIMULATED`，不得視為 CMP180 實機量測。

實機 SingleShot 已完成 HIL，可用 `--enable-hardware` 在本機啟用；實機 Sweep 尚未完成 HIL，因此保持鎖定。硬體模式沒有登入／RBAC，目前禁止綁定非 loopback 位址。

目前 GUI 是功能 MVP。第二輪 UI/UX 將加入即時 workflow step、執行動畫、取消與 cleanup 狀態、欄位連動驗證、圖表 tooltip／縮放、artifact 下載按鈕、run history，以及更完整的空白／錯誤／手機版狀態。

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
2. 確認頁面切到「結果與圖表」，並顯示 `SIMULATED`。
3. 到「頻率掃描」輸入 5925、6125、20 MHz，執行 Mock Sweep。
4. 確認產生 11 個資料點、圖表與 PASS/FAIL 表格。
5. 按右上角 `EN`，確認所有主要文字切換英文。
6. 縮小瀏覽器寬度，確認欄位由雙欄改成單欄，表格可水平捲動。
7. 到畫面底部確認 CSV、JSON 與 HTML report 的輸出位置。

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

GUI 會顯示 `HARDWARE ENABLED` 與 `ARMED`。執行前必須：

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
- Responsive phone, tablet, and desktop layouts.
- A mock single-frequency measurement.
- A mock frequency sweep using start, stop, and step.
- EVM, Burst Power, and Frequency Error result tables plus an EVM plot.
- CSV, JSON, metadata, and offline HTML output for every run.
- Every mock result is labeled `SIMULATED` and must not be treated as a real CMP180 measurement.

Real hardware SingleShot has completed HIL and can be enabled locally with `--enable-hardware`; real hardware Sweep has not completed HIL and remains locked.

The current GUI is a functional MVP. The second UI/UX pass adds live workflow steps, running animation, cancellation and cleanup state, cross-field validation, plot tooltips/zoom, artifact download buttons, run history, and stronger empty/error/mobile states.

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
2. Confirm the page switches to Results & Plots and displays `SIMULATED`.
3. On Frequency Sweep, enter 5925, 6125, and 20 MHz, then run the mock sweep.
4. Confirm that 11 points, a plot, and a PASS/FAIL table appear.
5. Select `EN`/`中文` at the top right and confirm that primary UI text changes language.
6. Narrow the browser and confirm fields collapse from two columns to one while the table scrolls horizontally.
7. Confirm the CSV, JSON, and HTML report paths at the bottom of the results page.

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

The GUI displays `HARDWARE ENABLED` and `ARMED`. Before a run:

1. Confirm the RF1.1-to-RF1.5 cable.
2. Confirm that an operator is beside the CMP180.
3. Enter the exact confirmation text `RF1.1-RF1.5`.
4. Select the operator-present checkbox.

The hardware screen currently permits only the verified 6105 MHz, 320 MHz, -40 dBm, -20 dBm expected-power profile. The page cannot arbitrarily increase power or change bands. Every run saves non-simulated CSV, JSON, metadata, and raw response artifacts. On error, the service runs workflow cleanup followed by independent emergency STOP/ABORt, RF Off, and final-state read-back.

End-to-end Web API HIL acceptance passed on 2026-08-19. Invalid confirmation data was first rejected with HTTP 400. Correct confirmation then completed a new hardware SingleShot with EVM All -36.51843 dB, Burst Power -40.18850 dBm, Frequency Error 6.986657 Hz, and run ID `2d099714ee`. The response reported `simulated=false`; CSV and raw artifacts existed. Independent final auditing confirmed RF `OFF`, measurement `RDY`, and an empty error queue.

The second UI pass uses the company TMXLAB KIT Demo as an information-hierarchy reference: cyan represents actionable/measurement state and red represents RF risk. Cable confirmation is now an editable suggestion list. Users can type a custom route, but only the verified `RF1.1-RF1.5` route can unlock RF. Results use clickable CSV, JSON, Metadata, Raw SCPI, and HTML Report buttons. The separate Fault Tests screen has been removed; the normal workflow now warns about an empty route, an unverified route, missing operator presence, duplicate submission, and locked hardware mode.
