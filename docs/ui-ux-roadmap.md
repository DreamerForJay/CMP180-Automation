# 公司內部量測控制台 UI/UX 路線圖 / Internal Measurement Console UI/UX Roadmap

## 中文版本

### 目標

Web GUI 必須讓第一次使用的公司同仁能辨認目前模式、完成安全設定、執行量測、
判讀結果並取得 artifacts，同時讓維護工程師能快速定位狀態與錯誤。視覺採簡潔的
深色 RF 控制台，不以重複警告或開發階段說明占用主要工作區。

### 設計原則

- 模式只在右上角與工作區控制狀態顯示；不使用底部常駐橫幅。
- 真實 RF 警示只在實機操作與最後確認階段出現。
- Mock 在介面稱為 `Demo`，結果資料仍永久保存 `simulated=true` 供稽核。
- 一個畫面只有一個主要執行按鈕，紅色只用於 RF、Stop 與重大錯誤。
- 輸入欄位同時顯示單位、允許範圍與欄位級錯誤，不只依賴 toast。
- 無效結果不得當作零，也不得與有效點連成正常資料線。
- 桌面以操作為主；手機可查看結果，但未來預設不得啟動實機 RF。

### 資訊架構

目標導覽為 Dashboard、Single、Sweep、Results 與 Diagnostics。Mock／Hardware 是
執行模式，不是兩套重複功能頁。Sweep 內再選 Frequency 或 Power。實機操作遵循
`Configure → Preflight → Run → Review`，並顯示狀態機、進度、取消與 cleanup 結果。

### 分階段交付

1. UI-1：移除重複模式提示與大 Hero、建立緊湊工作區、統一深色視覺與安全文案。
2. UI-2：加入 Dashboard，合併 Demo／Hardware 功能資訊架構，建立步驟式流程。
3. UI-3：圖表 tooltip／limit line／zoom、結果篩選、artifact 按鈕與 PNG export。
4. UI-4：Sweep progress／cancel／partial results 與 final RF-state audit；需先通過 HIL。
5. UI-5：內網 authentication、RBAC、audit log、run history 與多使用者互斥。

### UI-1 驗收條件

- 不再存在底部 `SIMULATED`／`HARDWARE` 常駐列。
- 首屏直接呈現量測工作區、已驗證 profile 與控制狀態。
- Demo／Hardware 模式切換不會產生矛盾文案。
- Demo Single 與兩種 Demo Sweep 使用正式安全輪廓：-40 dBm、最多 11 點。
- 1440、1024、768、390 px 寬度不重疊、不截斷主要操作且可鍵盤使用。
- 中文與英文都完整顯示，狀態不只依賴顏色辨識。

## English Version

### Goal

The Web GUI must let a first-time internal user identify the active mode, complete safe
configuration, run a measurement, interpret results, and retrieve artifacts. Maintainers
must be able to locate state and errors quickly. The visual direction is a clean dark RF
console without repetitive warnings or development-stage explanations occupying the main
workspace.

### Design principles

- Show mode only in the top-right status and workspace control state; do not use a
  persistent bottom banner.
- Show real-RF warnings only in hardware operation and final-confirmation contexts.
- Call mock mode `Demo` in the UI while permanently retaining `simulated=true` in results.
- Provide one primary action per screen; reserve red for RF, Stop, and critical errors.
- Show units, allowed ranges, and field-level errors beside inputs instead of relying only
  on toast messages.
- Never present invalid results as zero or connect them as normal valid plot segments.
- Optimize desktop for operation. Mobile may review results but should not enable live RF.

### Information architecture

The target navigation is Dashboard, Single, Sweep, Results, and Diagnostics. Demo and
Hardware are execution modes, not duplicate feature pages. Sweep contains Frequency and
Power variants. Hardware operation follows `Configure → Preflight → Run → Review` and
shows state-machine progress, cancellation, and cleanup results.

### Delivery phases

1. UI-1: remove duplicate mode messaging and the large hero; add a compact workspace and
   consistent dark-console visual and safety copy.
2. UI-2: add Dashboard, unify Demo/Hardware information architecture, and add a step flow.
3. UI-3: add chart tooltips/limit lines/zoom, result filtering, artifact controls, and PNG.
4. UI-4: add sweep progress/cancel/partial results and final RF-state audit after HIL.
5. UI-5: add intranet authentication, RBAC, audit logs, run history, and user locking.

### UI-1 acceptance criteria

- No persistent bottom `SIMULATED`/`HARDWARE` bar remains.
- The first viewport presents the measurement workspace, verified profile, and control state.
- Demo/Hardware mode changes do not produce contradictory copy.
- Demo Single and both Demo Sweeps use the production safety shape: -40 dBm and 11 points.
- Layouts at 1440, 1024, 768, and 390 px do not overlap or hide primary actions and remain
  keyboard usable.
- Both languages render completely, and state is never communicated by color alone.
