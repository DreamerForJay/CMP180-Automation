# CMP180 專案交接 / Project Handoff

## 中文版本

### 狀態（2026-08-20）

- 分支：`feature/web-sweep-jobs`（Web Sweep PR #12）。
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

1. 加入 DUT 控制、正式 WLAN limits、path-loss／calibration tables。
2. 完成內網 deployment 所需 authentication、RBAC 與 audit log；完成前不得綁定非 loopback。
3. 增加 run history、取消／cleanup 細節與獨立 CSV／JSON redraw CLI。

實機前先跑連線與 query-only Generator discovery，確認 RF OFF、measurement RDY、error queue empty，再依 [hardware SOP](docs/hardware-test-sop.md) 操作。

## English Version

### Status (2026-08-20)

- Branch: `feature/web-sweep-jobs` (Web Sweep PR #12).
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

1. Add DUT control, formal WLAN limits, and path-loss/calibration tables.
2. Complete authentication, RBAC, and audit logging for intranet deployment; do not bind beyond loopback before then.
3. Add run history, richer cancellation/cleanup detail, and a standalone CSV/JSON redraw CLI.

Before live work, run connection and query-only Generator discovery, confirm RF OFF, measurement RDY, and an empty error queue, then follow the [hardware SOP](docs/hardware-test-sop.md).
