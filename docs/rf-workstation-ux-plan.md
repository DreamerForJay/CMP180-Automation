# RF 量測工作站 UI/UX 規格 / RF Measurement Workstation UI/UX Specification

## 中文版本

### 1. 產品定位

Web 介面應是 RF 工程師的量測工作站，不是只有漂亮卡片的 Dashboard。它必須同時支援：

- 操作員：快速建立安全計畫、看懂目前狀態、避免誤送 RF。
- 測試工程師：比較多次 Run、尋找異常頻點、查看原始資料與重建圖表。
- RF／校正負責人：確認 Path Loss、限制條件、器材與校正有效期限。
- 主管／接手人員：快速搜尋、篩選、排序、匯出並追溯測試證據。

### 2. 舊版值得保留的優點

舊版版面與 CSS 不再沿用，但下列工作概念應在 V2 重新設計：

1. 亮／暗主題切換，並保存使用者選擇。
2. Table 可在同一畫面快速掃描大量 Run，而不是逐張卡片閱讀。
3. EVM、Power、Frequency Error 可切換 metric。
4. Preflight 狀態、RF 鎖定、進度、取消與 cleanup 有明確回饋。
5. 欄位旁的 `?` 說明與雙語提示。
6. 校正流程使用固定 SOP，而不是要求操作員記住 CLI 參數。
7. 歷史結果可以載入、查看 artifacts、開啟資料夾與安全移至 Trash。

### 3. 建議資訊架構

主導覽調整為五個穩定工作區：

1. **量測 Measure**：計畫、Preflight、進度、Stop／Abort、cleanup。
2. **分析 Analyze**：單一 Run 詳情、多 Run 疊圖、游標、限制線與資料表。
3. **紀錄 Runs**：大量資料搜尋、篩選、排序、欄位配置與批次比較。
4. **校正 Calibration**：器材、讀值、Path Loss、審核與有效期限。
5. **系統 System**：儀器連線、路由、使用指南、語言與顯示設定。

結果不應只是量測後暫時顯示；每次完成後自動前往 Analyze，並可由 Runs 隨時重新載入。

### 4. 亮暗與可讀性

- Dark：實驗室預設，降低暗室眩光並凸顯 trace、警示與狀態。
- Light：辦公室、投影、文件審閱與列印。
- System：跟隨作業系統；使用 `localStorage` 保存選擇。
- 顏色不得是唯一狀態訊號；PASS／FAIL／INVALID 同時使用文字、圖示與線型。
- RF Armed 使用琥珀／紅色並固定在 Header；Demo、View-only 與 Hardware 不得只靠背景顏色區分。
- Trace 使用色盲友善預設色盤，亮暗主題需各自驗證對比度。

### 5. Runs 紀錄 Table

桌面版預設使用 Table，手機版改為摘要列／可展開詳情。Table 工具列包含：

- 全文搜尋：Test name、Run ID、DUT ID、操作者、註記。
- 日期區間與快速篩選：今天、最近 7 天、最近 30 天。
- 篩選：Demo／Hardware、Complete／Partial／Failed、Single／Frequency／Power、頻寬、頻段、校正 Profile、Limit Profile。
- 欄位排序：時間、名稱、中心頻率、功率、點數、Avg/Worst EVM、狀態。
- 顯示欄位設定、欄寬拖曳、固定首欄、分頁或虛擬捲動。
- 多選 Run 後「加入比較」，不把刪除放在容易誤按的主要動作位置。
- 儲存常用檢視，例如「今日 320 MHz 實機失敗」或「本週 RF1.1→RF1.5」。

最少欄位：Timestamp、Test name、Run ID、Source、Mode、Route、Frequency range、Bandwidth、Power range、Points、Status、Worst EVM、Calibration、Artifacts。

### 6. RF 圖表分析工作區

#### 6.1 Trace 與比較

- 同時比較 2–8 個 Run；預設不一次載入所有歷史資料。
- 每個 Trace 可設定顯示名稱、顏色、線型、點型與可見性。
- 左側 Trace List 支援拖曳排序；順序同步到 legend 與匯出圖。
- 可複製 Run、暫時隱藏、Solo、鎖定顏色及移除比較。
- 比較前檢查 bandwidth、waveform、MCS、route、calibration 與 limit profile；條件不同時顯示不可忽略的比較警告。

#### 6.2 RF 必要圖表

- Frequency／Generator Power vs. EVM All、Data、Pilot。
- Frequency／Generator Power vs. Burst Power、Peak Power。
- 設定功率 vs. 經 Path Loss 修正後量測功率，並顯示 Power Error。
- Frequency vs. Frequency Error、Clock Error。
- PASS／FAIL／INVALID 點位狀態與正式 Limit line。
- 後續擴充 Spectrum Mask、Flatness、Power vs. Time 與 constellation／IQ reference。

EVM dB 數值越負通常越好，UI 必須標示「更負為佳」，避免用一般的上升／下降箭頭誤導。

#### 6.3 互動

- 滑鼠 hover 顯示 Run、頻率、設定功率、EVM、Burst Power、Frequency Error、狀態與時間。
- 框選 Zoom、滾輪縮放、拖曳 Pan、Reset view。
- A/B 雙游標顯示 ΔFrequency、ΔPower、ΔEVM。
- 多圖同步 X 軸與游標；可解除同步。
- 點擊 INVALID／FAIL 點開啟該點 raw response、error queue、trigger/ranging 與 cleanup 狀態。
- 無效點必須斷線，不得和有效點連成正常 trace。
- 支援 PNG／SVG、可重建設定 JSON 與比較 CSV 匯出。

### 7. 量測操作與 RF 安全

- Measurement Plan 使用 Basic／Advanced 分層，預設只顯示常用參數。
- Preflight 以 Routing、Cable/Attenuator、Path Loss、Frequency、Bandwidth、Power、Expected Power、Trigger、Calibration、Instrument State 分項顯示。
- 每項狀態包含結果、原因、修正建議與資料來源，不只顯示綠燈。
- 實機執行固定經過 `Configure → Preflight → Armed → Running → Cleanup → Review`。
- Running 顯示目前點、總點數、實際頻率／功率與最後有效結果；取消只在安全點邊界生效。
- 結束必須顯示 RF Off、Measurement RDY/OFF、Error queue 與 artifact 保存狀態。

### 8. 校正與追溯

- 校正頁改為四步精靈：器材識別 → 擷取／匯入讀值 → Loss curve 審查 → 核准。
- 顯示線損曲線、頻率覆蓋、插值點、禁止外插區與到期警示。
- 每次 Run 保存 calibration snapshot、revision、器材 ID、日期與 applied/not-applied。
- 比較圖可選擇 Raw Power 或 Corrected Power，但必須明確標籤，禁止混在同一軸而沒有說明。

### 9. 實作階段

#### P0：日常可用

1. Dark／Light／System 切換與持久化。
2. Runs Table、全文搜尋、主要篩選、排序與欄位顯示。
3. Analyze 頁 metric 切換、完整逐點 Table、tooltip、limit/invalid 呈現。
4. 從 Runs 載入到 Analyze；輸出位置與 artifacts 維持可追溯。

#### P1：RF 比較工作站

1. 多 Run 疊圖、Trace List、名稱／顏色／線型與拖曳排序。
2. Zoom、Pan、A/B cursor、同步 X 軸與點位詳情。
3. Power Error、校正前後切換、比較條件相容性警告。
4. PNG／SVG／比較 CSV 匯出。

#### P2：公司內網產品化

1. 校正精靈與 Approved Profile 工作流。
2. Authentication、RBAC、Audit Log、多人互斥與操作員識別。
3. Saved views、DUT／project tags、註記、批次報告與公司資料庫整合。
4. 大量 Run 的後端查詢、分頁與虛擬捲動。

### 10. 驗收準則

- 10,000 筆測試紀錄仍可在 2 秒內完成伺服器端搜尋／排序回應。
- 任意兩筆條件相容的 Run 可在 3 次操作內加入比較。
- 圖表 hover、Zoom、Pan、游標與 legend 在桌機可用；手機提供簡化檢視而不強迫精密拖曳。
- Light／Dark 在 320、768、1280、1920 px 寬度無水平溢出。
- 無效資料不連線，Raw／Corrected、Demo／Hardware 與 Draft／Approved 不會視覺混淆。
- 所有刪除仍採 Run ID 二次確認與可復原 Trash；圖表分析與歷史載入不控制 RF。

---

## English Version

### 1. Product position

The Web UI is an RF engineer's measurement workstation, not merely a dashboard with attractive cards. It must support:

- Operators who need fast, safe plan creation and unambiguous instrument state.
- Test engineers who compare runs, investigate anomalous points, and reproduce analysis from raw data.
- RF/calibration owners who review path loss, limits, equipment, and calibration validity.
- Managers and maintainers who search, filter, sort, export, and trace test evidence.

### 2. Strengths worth retaining from the legacy UI

The legacy layout and CSS remain retired, but V2 should redesign these workflow strengths:

1. Persistent Light/Dark themes.
2. A compact table for scanning many runs on one screen.
3. Metric selection for EVM, power, and frequency error.
4. Explicit preflight, RF lock, progress, cancellation, and cleanup feedback.
5. Field-level help and bilingual explanations.
6. A fixed calibration SOP instead of requiring operators to remember CLI arguments.
7. Loading history, opening artifacts/folders, and recoverable Trash operations.

### 3. Recommended information architecture

Use five stable workspaces:

1. **Measure**: plan, preflight, progress, Stop/Abort, and cleanup.
2. **Analyze**: one-run details, multi-run overlays, cursors, limit lines, and point tables.
3. **Runs**: high-volume search, filtering, sorting, column configuration, and comparison selection.
4. **Calibration**: equipment, readings, path loss, approval, and validity.
5. **System**: instrument connection, routing, guides, language, and display preferences.

Results are not temporary post-run content. Completion opens Analyze automatically, and any saved run can be reopened from Runs.

### 4. Themes and readability

- Dark is the laboratory default for reduced glare and clear traces/alarms.
- Light supports offices, projection, document review, and printing.
- System follows the OS; persist the choice in `localStorage`.
- Color is never the only state indicator. PASS/FAIL/INVALID also use text, icons, and line styles.
- RF Armed remains visible in the header with amber/red treatment. Demo, View-only, and Hardware use explicit text and icons.
- Use color-blind-safe trace palettes and verify contrast separately for both themes.

### 5. Runs table

Desktop defaults to a table; mobile uses summary rows with expandable details. The toolbar provides:

- Full-text search across test name, Run ID, DUT ID, operator, and notes.
- Date ranges and Today/7-day/30-day shortcuts.
- Filters for Demo/Hardware, Complete/Partial/Failed, mode, bandwidth, band, calibration profile, and limit profile.
- Sorting by time, name, center frequency, power, point count, Avg/Worst EVM, and status.
- Column visibility, resizable widths, a pinned first column, and pagination or virtualization.
- Multi-select Add to Compare. Delete is not a prominent inline action.
- Saved views such as “Today's 320 MHz hardware failures.”

Minimum columns are Timestamp, Test name, Run ID, Source, Mode, Route, Frequency range, Bandwidth, Power range, Points, Status, Worst EVM, Calibration, and Artifacts.

### 6. RF chart analysis workspace

#### 6.1 Traces and comparison

- Compare 2–8 runs; never load all history by default.
- Configure display name, color, line style, point marker, and visibility per trace.
- Drag to reorder a Trace List; legend and exports follow the same order.
- Support duplicate, hide, solo, color lock, and remove.
- Check bandwidth, waveform, MCS, route, calibration, and limit-profile compatibility before comparison; mismatches produce a persistent warning.

#### 6.2 Required RF plots

- Frequency or Generator Power versus EVM All/Data/Pilot.
- Frequency or Generator Power versus Burst/Peak Power.
- Set power versus path-loss-corrected measured power, including Power Error.
- Frequency versus Frequency Error and Clock Error.
- Per-point PASS/FAIL/INVALID state and approved limit lines.
- Later Spectrum Mask, Flatness, Power vs. Time, and constellation/IQ references.

More-negative EVM in dB is normally better. The UI must say this explicitly and must not use generic up/down arrows that imply the opposite.

#### 6.3 Interaction

- Hover shows run, frequency, set power, EVM, burst power, frequency error, state, and timestamp.
- Box zoom, wheel zoom, drag pan, and Reset view.
- A/B cursors show ΔFrequency, ΔPower, and ΔEVM.
- Synchronize X axes/cursors across plots, with an unlock option.
- Clicking INVALID/FAIL opens raw response, error queue, trigger/ranging, and cleanup state.
- Invalid points break the line and never appear as a normal trace.
- Export PNG/SVG, reproducible view-settings JSON, and comparison CSV.

### 7. Measurement operation and RF safety

- Layer Measurement Plan into Basic and Advanced settings.
- Preflight covers routing, cable/attenuator, path loss, frequency, bandwidth, power, expected power, trigger, calibration, and instrument state.
- Every item shows result, reason, suggested correction, and evidence source—not just a green lamp.
- Hardware execution follows `Configure → Preflight → Armed → Running → Cleanup → Review`.
- Running shows current/total point, actual frequency/power, and latest valid result. Cancellation takes effect only at a safe point boundary.
- Completion shows RF Off, Measurement RDY/OFF, error queue, and artifact-save state.

### 8. Calibration and traceability

- Use a four-step wizard: equipment identity, capture/import, loss-curve review, and approval.
- Show loss curve, frequency coverage, interpolation points, forbidden extrapolation, and expiry warnings.
- Save calibration snapshot, revision, equipment IDs, dates, and applied/not-applied with every run.
- Analysis may switch Raw Power and Corrected Power, but both are explicitly labeled and never silently mixed.

### 9. Implementation phases

#### P0: daily usability

1. Persistent Dark/Light/System themes.
2. Runs table with full-text search, primary filters, sorting, and column visibility.
3. Analyze metric selection, complete point table, tooltip, limit, and invalid-state rendering.
4. Open any run from Runs in Analyze while preserving output and artifact traceability.

#### P1: RF comparison workstation

1. Multi-run overlays, Trace List, names/colors/styles, and drag ordering.
2. Zoom, pan, A/B cursors, synchronized X axes, and point details.
3. Power Error, raw/corrected switching, and comparison-compatibility warnings.
4. PNG/SVG/comparison-CSV exports.

#### P2: intranet productization

1. Calibration wizard and Approved Profile workflow.
2. Authentication, RBAC, audit logs, multi-user locks, and operator identity.
3. Saved views, DUT/project tags, notes, batch reports, and corporate data integration.
4. Server-side query/pagination and virtualization for large run collections.

### 10. Acceptance criteria

- Server-side search/sort responds within two seconds for 10,000 run records.
- Any two compatible runs can enter comparison within three actions.
- Desktop supports hover, zoom, pan, cursors, and legends; mobile offers a simplified view instead of precision dragging.
- Light/Dark layouts have no horizontal overflow at 320, 768, 1280, and 1920 px.
- Invalid data is not connected; Raw/Corrected, Demo/Hardware, and Draft/Approved are visually unambiguous.
- Deletion keeps Run-ID confirmation and recoverable Trash. Analysis and history loading never control RF.
