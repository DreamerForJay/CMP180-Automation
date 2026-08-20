# CMP180 專案交接 / Project Handoff

## 中文版本

### 狀態（2026-08-20）

- 分支：`feature/phase2-integration`。
- Python 實機 SingleShot 已通過：RF1.1 → RF1.5、6105 MHz、320 MHz、-40 dBm。
- Web GUI 已有雙語響應式版面（亮／暗主題切換，預設暗色）、Mock 單點／頻率掃描／功率掃描、受保護實機 SingleShot、artifacts 與圖表。
- 實機 Web 只允許 loopback bind；尚無 authentication／RBAC，不得對內網公開 RF endpoint。
- 安全短掃描核心（頻率與功率）與 Mock tests 已完成；實機 HIL 未完成，Web 實機 sweep 鎖定。
- Tkinter 桌面 GUI 已移除（功能已被 Web GUI 完全取代），改用 CLI／Web GUI。
- Result artifacts 現在保存全部 5 組已驗證統計（average／current／min／max／std_dev），不只 average。
- 新增 ruff／mypy（CI 中非阻斷）與 `scripts/precommit_check.ps1`。
- PR #7 接手審查已將 Frequency／Power Sweep 的頻率、頻寬、功率、span 與點數改為
  不可由呼叫端放寬的硬性安全包絡，並補上繞過測試；尚未執行新的實機 RF。
- 最新本機驗證：87 tests、兩份 YAML validation、JavaScript syntax 與
  `git diff --check` 通過；全部使用 unit／Mock，未執行新實機 RF。PR #7 原 head 的
  GitHub Actions 已通過，安全修正 push 後需等待新一輪 CI。

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

- Branch: `feature/phase2-integration`.
- Python hardware SingleShot passed at RF1.1 to RF1.5, 6105 MHz, 320 MHz, and -40 dBm.
- The Web GUI provides a bilingual responsive layout (light/dark theme toggle, dark by default), mock single/frequency-sweep/power-sweep, guarded hardware SingleShot, artifacts, and plots.
- Hardware Web mode is loopback-only. Authentication/RBAC are absent, so never expose the RF endpoint to the network.
- The safe short-sweep cores (frequency and power) and mock tests are complete. Hardware HIL is pending for both and the Web hardware sweep buttons remain locked.
- The Tkinter desktop GUI has been removed (fully superseded by the Web GUI); use the CLI/Web GUI instead.
- Result artifacts now save all 5 verified statistics (average/current/min/max/std_dev), not just average.
- Added ruff/mypy (non-blocking in CI) and `scripts/precommit_check.ps1`.
- The PR #7 takeover review changed Frequency/Power Sweep frequency, bandwidth, power,
  span, and point limits into hard safety ceilings that callers cannot relax, with
  bypass tests added. No new live RF run was performed.
- Latest local validation: 87 tests, both YAML validations, JavaScript syntax, and
  `git diff --check` passed. All checks used unit/mock paths; no new live RF run was
  performed. GitHub Actions passed on the original PR #7 head; wait for a new CI run
  after pushing the safety fixes.

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
