# CMP180 專案交接 / Project Handoff

## 中文版本

### 狀態（2026-08-20）

- 分支：`feature/ui-console-refresh`（PR #8；五統計 HIL 已由 PR #9 合併）。
- Python 實機 SingleShot 已通過：RF1.1 → RF1.5、6105 MHz、320 MHz、-40 dBm。
- Web GUI 已有雙語響應式版面（亮／暗主題切換，預設暗色）、Mock 單點／頻率掃描／功率掃描、受保護實機 SingleShot、artifacts 與圖表。
- 實機 Web 只允許 loopback bind；尚無 authentication／RBAC，不得對內網公開 RF endpoint。
- 安全短掃描核心（頻率與功率）與 Mock tests 已完成；實機 HIL 未完成，Web 實機 sweep 鎖定。
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

1. 6085／6105／6125 MHz 三點低功率頻率 sweep HIL；固定頻率、多組低功率點的功率 sweep HIL。
2. Sweep partial-result metadata、Web progress 與 cancel（頻率與功率掃描都需要）。
3. DUT 控制、正式 WLAN limits、path-loss／calibration tables。
4. 內網 deployment 所需 authentication、RBAC 與 audit log。
5. 獨立 CSV／JSON redraw CLI。

實機前先跑連線與 query-only Generator discovery，確認 RF OFF、measurement RDY、error queue empty，再依 [hardware SOP](docs/hardware-test-sop.md) 操作。

## English Version

### Status (2026-08-20)

- Branch: `feature/ui-console-refresh` (PR #8; five-statistic HIL merged in PR #9).
- Python hardware SingleShot passed at RF1.1 to RF1.5, 6105 MHz, 320 MHz, and -40 dBm.
- The Web GUI provides a bilingual responsive layout (light/dark theme toggle, dark by default), mock single/frequency-sweep/power-sweep, guarded hardware SingleShot, artifacts, and plots.
- Hardware Web mode is loopback-only. Authentication/RBAC are absent, so never expose the RF endpoint to the network.
- The safe short-sweep cores (frequency and power) and mock tests are complete. Hardware HIL is pending for both and the Web hardware sweep buttons remain locked.
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

1. Three-point low-power frequency sweep HIL at 6085/6105/6125 MHz; a power sweep HIL run at a fixed frequency across several low power levels.
2. Sweep partial-result metadata plus Web progress/cancel (for both sweep types).
3. DUT control, formal WLAN limits, and path-loss/calibration tables.
4. Authentication, RBAC, and audit logging for intranet deployment.
5. A standalone CSV/JSON redraw CLI.

Before live work, run connection and query-only Generator discovery, confirm RF OFF, measurement RDY, and an empty error queue, then follow the [hardware SOP](docs/hardware-test-sop.md).
