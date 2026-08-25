# Web UI／UX 重構規格 / Web UI/UX Restructure Specification

## 中文版本

### 設計目標

這不是一般展示網站，而是會控制 RF 儀器的實驗室量測控制台。介面必須讓操作員在十秒內回答：
目前連到哪一台儀器、接線與校正是否有效、將執行什麼計畫、是否會送 RF、進度到哪裡、
結果是否有效，以及輸出存在哪裡。安全資訊不得只靠顏色表示。

### 資訊架構

主導覽只保留四個工作區：

1. **量測**：實機與示範共用同一套欄位語言；實機／示範為第一層切換，單點／頻率／功率為第二層。
2. **校正**：器材登錄、讀值取得、線損檢查、核准狀態四步流程。
3. **結果**：目前 Run 的指標、圖表、Pass／Fail、警告及輸出檔案。
4. **紀錄**：過去 Run 的搜尋、篩選、查看、重新建立計畫、開啟資料夾及可復原刪除。

示範單點、示範頻掃與示範功掃不得再占用三個主頁籤。自訂掃描也不是獨立的「預覽工具」，
而是量測計畫的一種模式。

### 量測工作流

量測頁依序顯示：

1. 儀器與路徑：連線、Generator、Analyzer、線材、衰減器、Calibration Profile。
2. 計畫：單點／頻掃／功掃、頻率、功率、頻寬、步進、點數、dwell 與測試名稱。
3. 即時安全摘要：實際點位、預估時間、最大輸出、預估 Analyzer 輸入及所有限制原因。
4. 現場確認：只有實機模式顯示，且確認內容必須與當前 fingerprint 綁定。
5. 執行與進度：狀態機、目前點、取消、STOP／ABORT／RF Off 收尾狀態。

`Custom Safe Sweep Preview` 改名為「自訂量測計畫」。安全檢查應在輸入旁即時顯示，
而不是要求使用者先理解 fingerprint 或複製內部確認字串。Fingerprint 保留在 audit metadata，
一般操作員只需確認人員、接線、衰減器與摘要；高風險或未驗證計畫由角色權限擋下。

### 紀錄與檔案

- 原 `Load` 其實只顯示內容，因此改名「查看詳情」。
- 真正的「載入為新計畫」必須建立一份可編輯副本，不得修改歷史紀錄。
- 「開啟資料夾」點擊後直接交由本機檔案總管開啟，成功或失敗必須顯示明確訊息。
- 表格預設欄位為時間、名稱、類型、結果、點數與主要動作；Run ID、來源與檔案格式移至展開詳情。
- 後端必須支援分頁、搜尋、日期／來源／結果篩選，避免一次掃描全部 `output/` 造成頁面卡頓。
- 375–767 px 改用卡片列表；768 px 以上使用可調整欄寬的表格，並保存使用者欄寬偏好。

### 校正工作流

校正頁採四步精靈，而不是一次顯示所有欄位：

1. 選擇路徑並掃描／輸入線材、轉接頭與外部儀器識別。
2. 選擇 adapter 或匯入 CSV；顯示頻點覆蓋與單位。
3. 顯示 Source、Receiver、Path Loss 曲線、異常點與外插缺口。
4. 建立 Draft、送審或由 RF Owner 核准；一般使用者不得自行把 Draft 改成 Approved。

每個不直觀欄位提供可鍵盤操作的 `?`，內容必須說明用途、單位、允許範圍、資料來源與錯誤後果。

### 視覺與無障礙

- 使用緊湊、低干擾的深色工程控制台；青色表示可操作／選取，綠色只表示已驗證成功，黃色表示注意，紅色只表示危險或失敗。
- Badge 意義必須同時有文字或圖示，不能只靠色彩。
- 所有按鍵具 hover、focus-visible、disabled 與 processing 狀態；不可用按鍵旁要直接說明原因。
- 文字、Run ID 與路徑允許換行；不以截斷隱藏必要資訊。
- 支援 375、768、1024、1440 px、200% zoom 與 `prefers-reduced-motion`。
- 圖表遇到 `INV`／`null` 必須斷線並標記無效點，不能補零、連線或讓頁面崩潰。

### 分階段交付

1. IA-1：四主工作區、量測雙層切換、清楚命名與狀態文案。
2. MEAS-2：固定與自訂計畫合併、即時安全摘要、簡化 HIL 確認。
3. HIST-3：紀錄分頁／篩選、查看詳情、載入為新計畫與直接開啟資料夾。
4. CAL-4：四步校正精靈、曲線與審核生命週期。
5. QA-5：雙語、鍵盤、螢幕閱讀器、響應式與實機狀態機驗收。

## English Version

### Design objective

This is a laboratory measurement console that can control RF hardware, not a marketing site.
Within ten seconds, an operator must understand which instrument is connected, whether routing
and calibration are valid, what plan will run, whether RF will be transmitted, current progress,
result validity, and output location. Safety meaning must never depend on color alone.

### Information architecture

Keep only four primary workspaces:

1. **Measurement**: hardware and demo use the same field language; hardware/demo is the first
   level and single/frequency/power is the second level.
2. **Calibration**: a four-step equipment, capture, loss-review, and approval workflow.
3. **Results**: current-run metrics, plots, limits, warnings, and artifacts.
4. **History**: search, filter, inspect, recreate a plan, open its folder, or recoverably delete it.

Demo single, frequency, and power modes must not occupy three primary tabs. A custom sweep is a
measurement-plan mode, not a separate preview utility.

### Measurement workflow

Present the measurement page in this order:

1. Instrument and route: connection, Generator, Analyzer, cable, attenuator, and calibration.
2. Plan: single/frequency/power, frequency, power, bandwidth, step, points, dwell, and test name.
3. Live safety summary: actual points, estimated duration, maximum output, estimated Analyzer
   input, and every blocking reason.
4. On-site confirmation: hardware only and bound to the current plan fingerprint.
5. Execution and progress: state, current point, cancellation, and STOP/ABORT/RF-Off cleanup.

Rename `Custom Safe Sweep Preview` to “Custom Measurement Plan.” Show safety feedback next to
inputs instead of making operators understand fingerprints or copy internal confirmation tokens.
Keep the fingerprint in audit metadata. Operators confirm presence, cabling, attenuation, and the
summary; roles block high-risk or unverified plans.

### History and files

- Rename `Load` to “View details,” because it only displays a record.
- A real “Load as new plan” action creates an editable copy and never changes history.
- “Open folder” immediately asks the local file explorer to open the run and reports success or
  failure clearly.
- Default columns are time, name, type, outcome, points, and primary actions. Move Run ID, source,
  and file formats into details.
- Add backend pagination, search, and date/source/outcome filters so the browser never scans the
  entire output directory at once.
- Use cards at 375–767 px and a resizable, preference-persisted table at 768 px and above.

### Calibration workflow

Use a four-step wizard instead of exposing every field at once: identify route/equipment, select
an adapter or import CSV, review Source/Receiver/Path-Loss plots and gaps, then create Draft and
submit for RF-owner approval. Normal users cannot promote Draft to Approved. Every non-obvious
field gets keyboard-accessible help describing purpose, unit, range, source, and failure impact.

### Visual system and accessibility

- Use a compact, low-distraction dark engineering console. Cyan means selectable/actionable,
  green means verified success only, amber means attention, and red means danger/failure only.
- Badges require text or an icon in addition to color.
- Buttons require hover, focus-visible, disabled, and processing states. Explain disabled actions
  beside the action.
- Text, Run IDs, and paths reflow without hiding essential information.
- Support 375, 768, 1024, and 1440 px, 200% zoom, and `prefers-reduced-motion`.
- Plot `INV`/`null` as explicit gaps and invalid markers; never coerce to zero, connect across the
  gap, or crash the page.

### Delivery phases

1. IA-1: four workspaces, two-level measurement navigation, names, and status copy.
2. MEAS-2: merge fixed/custom plans, live safety summary, and simplified HIL confirmation.
3. HIST-3: pagination/filtering, details, load-as-new-plan, and direct folder opening.
4. CAL-4: four-step calibration wizard, plots, and approval lifecycle.
5. QA-5: bilingual, keyboard, screen-reader, responsive, and live state-machine acceptance.
