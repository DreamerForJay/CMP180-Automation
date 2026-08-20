# CMP180 專案交接 / Project Handoff

## 中文版本

### 狀態（2026-08-20）

- 分支：`feature/power-sweep-hil-entry`（頻率掃描 PR #10 已合併至 `main`）。
- Python 實機 SingleShot 已通過：RF1.1 → RF1.5、6105 MHz、320 MHz、-40 dBm。
- Web GUI 已有雙語響應式版面（亮／暗主題切換，預設暗色）、Mock 單點／頻率掃描／功率掃描、受保護實機 SingleShot、artifacts 與圖表。
- 實機 Web 只允許 loopback bind；尚無 authentication／RBAC，不得對內網公開 RF endpoint。
- 安全短掃描核心（頻率與功率）與 Mock tests 已完成；固定三點頻率 HIL 已通過，功率 HIL 未完成，Web 實機 sweep 仍鎖定。
- Run `bb3e8db580` 完成 6085／6105／6125 MHz 三點實機掃頻；三點 errors 均空，最終 RF `OFF`、measurement `RDY`、error queue empty，完整 artifacts 已保存。
- 功率掃描 run `56ab9c982e` 在 -60 dBm 回傳 `INV`，舊核心錯標 complete；安全收尾正常。已補有限關鍵指標閘門，需重新 HIL，原 artifacts 保持不變作為 finding 證據。
- 修正版 run `b8db34c0f4` 在 -60 dBm 正確立即停止、標示 partial，未執行較高功率；最終 RF OFF／RDY／error queue empty。下一個候選有效批次為 -55 至 -40 dBm。
- Run `e6e86fe3d7` 完成 -55／-50／-45／-40 dBm 四點有效功率掃描；四點 errors 均空，最終 RF OFF／RDY／error queue empty，20 份 raw 與完整 artifacts 已保存。
- Web Mock Sweep 已改為非同步 Job API，支援進度、單一 active job、取消與 partial artifacts；瀏覽器驗收通過取消 3/11、完成 4/4、檔案連結與窄版無溢出；該批驗收未控制實機。
- 實機 Web Frequency／Power Sweep 已接固定 HIL profile，取消只在 RF Off 點邊界生效且有外層 emergency cleanup；97 tests 通過，尚待現場 Web HIL。
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

1. 設計並驗證 Web Sweep progress、cancel、emergency cleanup；通過前保持實機按鈕鎖定。
2. Sweep partial-result metadata、Web progress 與 cancel（頻率與功率掃描都需要）。
3. DUT 控制、正式 WLAN limits、path-loss／calibration tables。
4. 內網 deployment 所需 authentication、RBAC 與 audit log。
5. 獨立 CSV／JSON redraw CLI。

實機前先跑連線與 query-only Generator discovery，確認 RF OFF、measurement RDY、error queue empty，再依 [hardware SOP](docs/hardware-test-sop.md) 操作。

## English Version

### Status (2026-08-20)

- Branch: `feature/power-sweep-hil-entry` (frequency-sweep PR #10 is merged into `main`).
- Python hardware SingleShot passed at RF1.1 to RF1.5, 6105 MHz, 320 MHz, and -40 dBm.
- The Web GUI provides a bilingual responsive layout (light/dark theme toggle, dark by default), mock single/frequency-sweep/power-sweep, guarded hardware SingleShot, artifacts, and plots.
- Hardware Web mode is loopback-only. Authentication/RBAC are absent, so never expose the RF endpoint to the network.
- The safe short-sweep cores (frequency and power) and mock tests are complete. Fixed three-point frequency HIL passed, power HIL is pending, and the Web hardware sweep buttons remain locked.
- Run `bb3e8db580` completed the 6085/6105/6125 MHz hardware sweep with empty per-point errors, final RF `OFF`, measurement `RDY`, an empty error queue, and complete artifacts.
- Power-sweep run `56ab9c982e` returned `INV` at -60 dBm and the old core mislabeled it complete; cleanup was safe. A finite critical-metric gate is now implemented and requires new HIL. Original artifacts remain unchanged as finding evidence.
- Corrected run `b8db34c0f4` stopped immediately at -60 dBm, recorded partial status, and did not run higher powers; final RF OFF/RDY/error queue empty. The next candidate numeric batch is -55 through -40 dBm.
- Run `e6e86fe3d7` completed the -55/-50/-45/-40 dBm numeric power sweep with empty per-point errors, final RF OFF/RDY/error queue empty, 20 raw responses, and complete artifacts.
- Web Mock Sweep now uses an asynchronous Job API with progress, one active job, cancellation, and partial artifacts. Browser acceptance passed cancel at 3/11, complete at 4/4, clickable artifact links, and narrow-layout overflow checks; that batch did not control hardware.
- Web hardware Frequency/Power Sweep is connected to fixed HIL profiles. Cancellation occurs only at an RF-Off point boundary with outer emergency cleanup. All 97 tests pass; on-site Web HIL is pending.
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

1. Design and validate Web Sweep progress, cancellation, and emergency cleanup; keep hardware controls locked until acceptance passes.
2. Sweep partial-result metadata plus Web progress/cancel (for both sweep types).
3. DUT control, formal WLAN limits, and path-loss/calibration tables.
4. Authentication, RBAC, and audit logging for intranet deployment.
5. A standalone CSV/JSON redraw CLI.

Before live work, run connection and query-only Generator discovery, confirm RF OFF, measurement RDY, and an empty error queue, then follow the [hardware SOP](docs/hardware-test-sop.md).
