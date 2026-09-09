# CMP180 實習結案報告 PPT 規格

## 1. 文件目的

本文件定義實習結案報告簡報的內容規格，用來把 CMP180 WLAN TX EVM 自動化專案從「做了哪些功能」整理成一份可對主管、mentor 與同事說明的期末成果報告。

簡報應呈現三件事：

- 實習期間學到的 RF、EVM、SCPI、自動化與軟體工程能力。
- 專案從手動 CMsquares 量測演進到 Python／Web 自動化的成果。
- 已驗證能力、限制邊界與交接後下一步。

簡報不得把 Mock、dry-run、CMsquares 手動操作、預覽、單獨 stored `FETCh` 或未核准 DUT／UDBox route 說成新的完整 Python 實機量測。

## 2. 簡報定位

| 項目 | 規格 |
|---|---|
| 建議檔名 | `CMP180-final-project.pptx` |
| 建議頁數 | 12 到 15 頁 |
| 建議時長 | 10 到 15 分鐘 |
| 語言 | 主要使用繁體中文；SCPI、RF 名詞、程式識別字保留英文 |
| 受眾 | RF 測試主管、mentor、同組工程師、實習成果評審 |
| 語氣 | 技術清楚、證據導向、誠實說明限制 |

## 3. 核心主張

結案報告的主軸建議如下：

> 我把原本依賴 CMsquares 手動操作的 CMP180 WLAN TX EVM 量測，整理成可重現、可稽核、失敗時可安全收尾的 Python 3.11+ 自動化系統，並補上 Web 操作介面、結果 artifacts、圖表、SOP、驗收文件與 GitHub/CI 整理。

## 4. 建議投影片結構

### Slide 1：封面

- 標題：CMP180 WLAN TX EVM 自動化量測系統
- 副標：實習結案報告
- 補充資訊：姓名、部門、mentor、日期
- 視覺：CMP180／Web 介面截圖或系統架構圖

### Slide 2：專案背景與問題

- 原本量測依賴 CMsquares GUI 手動設定。
- 手動流程容易出現頻率、功率、routing、expected power、統計清除與資料抄錄錯誤。
- 掃描多個 power／frequency point 時，重複操作成本高且難追溯。
- RF 開關與異常收尾若只靠人工記憶，風險較高。

### Slide 3：實習目標與交付範圍

- 建立 Python 3.11+ CMP180 自動化專案。
- 支援 WLAN TX EVM SingleShot、Frequency Sweep、Power Sweep。
- 輸出 CSV、JSON、metadata、raw response、HTML report 與圖表。
- 建立 Web GUI、Mock mode、SOP、README、使用手冊、SCPI matrix 與 Demo。
- 說明 scope gap：MCS sweep、Constellation、5G NR FR1、正式 DUT／UDBox compliance 尚未完成。

### Slide 4：學習與工具鏈

- RF／EVM 基礎：dBm、dB、EVM 越負越好、frequency error、burst power。
- CMP180 與 CMsquares 操作模型。
- RsInstrument、SCPI、OPC、error queue 與 timeout。
- Python 分層架構、Pydantic YAML validation、pytest、GitHub Actions。
- Web 前端：雙語介面、job progress、run history、圖表互動。

### Slide 5：系統架構

- 圖示：CLI/Web → Workflow → Service → SCPI Registry → InstrumentSession → CMP180。
- 強調 GUI 不直接碰 SCPI，實機與 Mock 透過 protocol 抽象切換。
- SCPI command 集中在 `configs/scpi_command_map.yaml` 與 typed registry。
- 未驗證命令維持 `null`，避免套用其他儀器指令。

### Slide 6：RF 安全設計

- RF On 前檢查 routing、frequency、bandwidth、power、expected power、attenuation 與 operator confirmation。
- 已核准 loopback route：RF1.1 → RF1.5。
- 功率與 WLAN section 由 approved/HIL profile gate 控制。
- RF workflow 使用 `try/finally`，錯誤、逾時、取消時仍 Stop／Abort 並 RF Off。
- 不自動 Reset 儀器或 Workspace。

### Slide 7：SingleShot 量測流程

- 流程：連線 → 驗證身分 → 設定 Generator/Analyzer → readback → RF On → INIT → fetch → artifact → cleanup。
- 解釋 `READ`／`INITiate` 會啟動量測，`FETCh` 只讀 stored result。
- 28 欄 OFDM SISO 結果與 5 種 statistics 均保存。
- `INV`、缺值與非 finite critical metrics 不會被轉成 0 或 PASS。

### Slide 8：Sweep 與 HIL 成果

- Frequency Sweep：WLAN 合法 section／channel center 量測成果。
- Power Sweep：安全功率範圍內的自動掃描與 invalid 停止策略。
- Loopback：11 個 approved WLAN section 代表點，每點 Repeat=10，共 110/110 valid。
- 每份 artifact 保存 profile snapshot、raw repeats、outlier、cleanup evidence 與 final RF state。

### Slide 9：Web GUI 與操作體驗

- 單點、WLAN Frequency Sweep、WLAN Power Sweep、GPRF Power Reading 分類清楚。
- Preview 會顯示 rejection reason、修正方式與正確範圍；未通過不送 RF。
- 非同步 job 顯示進度、最新結果、趨勢、取消與 partial artifacts。
- Run History 可搜尋、篩選、排序、載入歷史設定與比較 2 到 8 筆 run。
- 中英語言切換只重繪既有資料，不重新呼叫 RF API。

### Slide 10：資料輸出與報告

- 每次 run 產出 CSV、JSON、metadata、raw response、HTML report。
- Matplotlib/Pandas PNG 與 dependency-free SVG/HTML 供不同環境使用。
- 圖表包含 EVM、Burst Power、Frequency Error 等核心指標。
- Invalid point 不連線、不補 0；報告在沒有 approved limit 時只標示 `MEASURED`。

### Slide 11：遇到的問題與解法

建議挑 4 到 6 個最能展現學習的案例：

- 真實 CMP180 `*IDN?` model token 與預期不同，因此修正 identity gate。
- `+0` no-error response 曾被誤判，依實機證據修正 parser。
- -60 dBm power point 回 `INV`，改成 critical field gate 並保留 partial artifact。
- Web 曾顯示自訂值但執行固定 profile，後來讓前後端共用同一個 plan。
- Measurement 長時間 `RUN`，追到 repetition 漂移為 Continuous，改為設定與 readback `SINGleshot`。
- GPRF power 受 WLAN ARB burst 影響，改用 CW 量測並在結束後恢復 ARB/waveform。

### Slide 12：完成度與限制邊界

- 已完成：連線、設定驗證、Mock、SCPI registry、SingleShot、掃描核心、artifacts、Web GUI、Loopback HIL、文件與 CI。
- 部分完成：Calibration profile lifecycle、GPRF power reading、structured logging、retry policy。
- 未完成或不得宣稱：正式 DUT／UDBox compliance、MCS sweep、Constellation、5G NR FR1、未核准 route／power／limit profile。
- 清楚說明 V1 loopback acceptance 不等於 DUT compliance。

### Slide 13：交付物總覽

- Repository：Python source、tests、configs、scripts。
- 文件：`README.md`、`SPEC.MD`、`docs/user-guide.md`、`docs/hardware-test-sop.md`、`docs/scpi-command-matrix.md`、`docs/v1-acceptance-report.md`。
- 視覺與報告：`presentation/exports/CMP180-final-project.pptx`、架構圖、生命週期圖、HTML report、PNG plots。
- Artifacts：`output/` 中具日期的實機／stored evidence。

### Slide 14：Demo 流程

- 先展示 README 與 docs 導覽。
- 啟動 Web GUI，以 Mock/Demo 展示不送 RF 的操作。
- 展示實機頁面的 preview gate、最後確認與被拒絕原因。
- 開啟既有 run history、CSV/JSON/metadata、HTML report 與圖表。
- 展示架構圖與 SingleShot lifecycle。
- 現場若沒有 RF 授權，僅展示 stored artifacts，不啟動新量測。

### Slide 15：結論與下一步

- 結論：專案已把 WLAN loopback 量測主線產品化到可交接、可重現、可稽核的程度。
- 下一步 1：取得正式 path-loss、DUT／UDBox route 與 RF owner approval。
- 下一步 2：完成 approved calibration/limit profile 後再宣稱 compliance。
- 下一步 3：擴充 MCS sweep、Constellation、5G NR FR1 與 RBAC/audit logging。

## 5. 建議講稿節奏

| 時間 | 內容 |
|---|---|
| 0:00–1:00 | 背景、問題與專案目標 |
| 1:00–3:00 | 架構、SCPI 邊界與 RF 安全 |
| 3:00–6:00 | SingleShot、Sweep、Loopback HIL 成果 |
| 6:00–8:00 | Web GUI、artifacts 與報告 |
| 8:00–11:00 | 問題診斷案例與學習成果 |
| 11:00–13:00 | 完成度、限制與下一步 |
| 13:00–15:00 | Demo 或 Q&A |

## 6. 視覺素材清單

- `docs/diagrams/system-architecture.png`
- `docs/diagrams/single-measurement-lifecycle.png`
- `presentation/slides/cmp180-final-project/assets/architecture.png`
- `presentation/slides/cmp180-final-project/assets/lifecycle.png`
- 具代表性的 Web GUI 截圖。
- 具代表性的 HTML report、CSV、JSON、metadata 與 Matplotlib PNG。

若新增實機截圖，需避免暴露序號、授權資訊、內部網路細節或敏感 workspace 資訊。

## 7. 證據引用規則

簡報每個量測成果應能回指到以下至少一種 evidence：

- `HANDOFF.md` 的具日期紀錄。
- `docs/hardware-discovery.md` 或 `docs/loopback-validation.md`。
- `output/` 中的具日期 artifacts。
- 測試紀錄或 CI 結果。
- `docs/project-development-log.md` 的完成度盤點。

若沒有 evidence，只能列為「下一步」、「待驗證」或「scope gap」。

## 8. 與現有簡報的同步

現有可編輯簡報來源：

- `presentation/slides/cmp180-final-project/index.tsx`
- `presentation/exports/CMP180-final-project.pptx`

若依本規格擴充內容，建議把目前 12 頁版本補成 15 頁：

- 新增「學習與工具鏈」。
- 新增「資料輸出與報告」。
- 新增「Demo 流程」。

簡報原始碼與匯出的 `.pptx` 應保持同步；若只修改其中一份，需在交接時註明哪一份是最新版本。
