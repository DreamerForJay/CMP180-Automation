# CMP180 專案交接 / Project Handoff

## 中文版本

### 狀態（2026-08-19）

- 分支：`feature/phase2-integration`。
- Python 實機 SingleShot 已通過：RF1.1 → RF1.5、6105 MHz、320 MHz、-40 dBm。
- Web GUI 已有雙語響應式版面、Mock 單點／掃頻、受保護實機 SingleShot、artifacts 與三種圖表。
- 實機 Web 只允許 loopback bind；尚無 authentication／RBAC，不得對內網公開 RF endpoint。
- 安全短掃頻核心與 Mock tests 已完成；3 點實機 HIL 未完成，Web 實機 sweep 鎖定。
- 最新驗證：95 tests、兩份 YAML validation、JavaScript syntax 與 `git diff --check` 通過。

### 安全基線與完成項目

- 核准測試 endpoint：`192.168.200.50:5025`；RF1.1 → RF1.5 單 cable loopback。
- 基線：6105 MHz、320 MHz、Generator -40 dBm、expected power -20 dBm。
- 最近收尾確認 RF `OFF`、measurement `RDY`、error queue empty；每次新 session 仍須重新查詢。
- 已完成設定／連線、discovery、setter、INIT／STOP／ABORT、RF On／Off、SingleShot backend、28 欄 parser、CSV／JSON／metadata／raw／HTML 與 Web GUI。
- GitHub Actions 只跑 unit／Mock／config validation，不連公司 CMP180。

### 下一步

1. 6085／6105／6125 MHz 三點低功率 sweep HIL。
2. Sweep partial-result metadata、Web progress 與 cancel。
3. DUT 控制、正式 WLAN limits、path-loss／calibration tables。
4. 內網 deployment 所需 authentication、RBAC 與 audit log。
5. 獨立 CSV／JSON redraw CLI。

實機前先跑連線與 query-only Generator discovery，確認 RF OFF、measurement RDY、error queue empty，再依 [hardware SOP](docs/hardware-test-sop.md) 操作。

## English Version

### Status (2026-08-19)

- Branch: `feature/phase2-integration`.
- Python hardware SingleShot passed at RF1.1 to RF1.5, 6105 MHz, 320 MHz, and -40 dBm.
- The Web GUI provides bilingual responsive mock single/sweep, guarded hardware SingleShot, artifacts, and three plots.
- Hardware Web mode is loopback-only. Authentication/RBAC are absent, so never expose the RF endpoint to the network.
- The safe short-sweep core and mock tests are complete. Three-point hardware HIL is pending and Web hardware sweep remains locked.
- Latest validation: 95 tests, both YAML validations, JavaScript syntax, and `git diff --check` passed.

### Safety baseline and completed work

- Approved test endpoint: `192.168.200.50:5025`; one RF1.1-to-RF1.5 loopback cable.
- Baseline: 6105 MHz, 320 MHz, -40 dBm Generator, and -20 dBm expected power.
- Latest cleanup confirmed RF `OFF`, measurement `RDY`, and an empty error queue. Re-query every new session.
- Configuration/connection, discovery, setters, INIT/STOP/ABORT, RF On/Off, SingleShot backend, 28-field parser, artifacts, and Web GUI are complete.
- GitHub Actions runs only unit/mock/config checks and cannot access the company CMP180.

### Next steps

1. Three-point low-power sweep HIL at 6085/6105/6125 MHz.
2. Sweep partial-result metadata plus Web progress/cancel.
3. DUT control, formal WLAN limits, and path-loss/calibration tables.
4. Authentication, RBAC, and audit logging for intranet deployment.
5. A standalone CSV/JSON redraw CLI.

Before live work, run connection and query-only Generator discovery, confirm RF OFF, measurement RDY, and an empty error queue, then follow the [hardware SOP](docs/hardware-test-sop.md).

