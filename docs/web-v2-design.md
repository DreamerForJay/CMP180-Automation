# CMP180 Web V2 設計規格 / CMP180 Web V2 Design Specification

## 中文版本

### 重建原則

V2 保留既有 Python workflow、SCPI registry、安全限制、Job、artifact 與 API，但完全停止載入
舊版 `static/` 的 HTML、CSS 與 JavaScript。新前端位於 `static_v2/`，只使用一份 `app.css`
與一份 `app.js`，避免不同載入順序、快取或 selector specificity 造成畫面不一致。

### 操作模型

桌面版採左側五項功能列：量測、結果、紀錄、校正、指南。手機版相同功能列固定在底部。
量測是首頁核心任務，畫面只分為兩個區域：左側量測設定，右側執行摘要與安全狀態。
單點、頻率掃描與功率掃描共用同一張表單，切換量測類型時只顯示相關欄位。

### 互動規則

- 輸入變更時即時計算點數、預估時間與最大功率。
- Demo 限制最多 11 點，Generator 功率不得高於 -40 dBm。
- 不符合限制時按鍵立即停用，並在相同畫面顯示原因。
- 執行後自動切換至結果頁，顯示指標、圖表與 artifact 連結。
- 供電不穩定期間只允許 Demo；指南明確標記實機 RF 暫停。
- 實機權限仍由後端 startup gate 決定，前端外觀不得繞過安全限制。

### 響應式與一致性

- 大於 1050 px：左側導覽、雙欄量測工作區。
- 721–1050 px：窄版導覽、單欄量測設定，摘要改為雙卡片。
- 720 px 以下：底部導覽、單欄欄位與卡片。
- 所有尺寸共用相同 DOM 與設計 token，不建立另一套手機頁。
- 支援鍵盤 focus、文字換行及 reduced motion。

## English Version

### Rebuild principle

V2 preserves the existing Python workflows, SCPI registry, safety limits, jobs, artifacts, and
APIs, but stops loading all legacy `static/` HTML, CSS, and JavaScript. The new frontend lives in
`static_v2/` and uses exactly one `app.css` and one `app.js`, preventing load order, caching, and
selector-specificity differences.

### Interaction model

Desktop uses a five-item left navigation: Measure, Results, Runs, Calibration, and Guide. Mobile
uses the same navigation at the bottom. Measurement is the primary task and has two areas only:
settings on the left and execution/safety summary on the right. Single, frequency sweep, and
power sweep share one form and reveal only relevant fields.

### Interaction rules

- Recalculate points, estimated time, and maximum power whenever inputs change.
- Demo plans allow no more than 11 points and no Generator power above -40 dBm.
- Disable execution immediately and explain the reason when a plan is invalid.
- After execution, open Results automatically with metrics, a plot, and artifact links.
- During unstable power, allow Demo only and clearly mark hardware RF as on hold.
- Hardware authority remains controlled by backend startup gates; frontend styling cannot bypass it.

### Responsive consistency

- Above 1050 px: left navigation and two-column measurement workspace.
- 721–1050 px: compact navigation, single-column settings, and two summary cards.
- 720 px and below: bottom navigation and single-column fields/cards.
- Every size uses the same DOM and design tokens; there is no separate mobile page.
- Keyboard focus, text reflow, and reduced motion are supported.
