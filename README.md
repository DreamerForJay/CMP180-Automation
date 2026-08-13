# ROHDE & SCHWARZ CMP180 · AUTOMATION PROJECT

## CMP180 WLAN EVM 自動化量測系統

**CMP180 WLAN TX EVM 自動化量測與分析系統 — 取代手動 CMsquares GUI 操作**

| 項目 | 狀態 |
|---|---|
| SPEC Version | `0.1.0` |
| Status | Draft / Hardware Connected |
| Current Phase | Phase 2 — Connection Framework |
| Runtime | Python 3.11+ |

本專案用於自動化 Rohde & Schwarz CMP180 Radio Communication Tester 的 WLAN TX EVM
量測流程，取代目前透過 CMsquares GUI 手動操作、容易出錯且難以重現的測試方式。

目前先以 CMP180 為唯一目標儀器。已於 2026-08-13 完成首次 Raw Socket
連線驗證。完整需求、架構、里程碑與驗收方式請參閱
[CMP180 開發規格與計畫](CMP180_DEVELOPMENT_SPEC_AND_PLAN.md)。

## 已確認的實機資訊

| 項目 | 結果 |
|---|---|
| IP | `192.168.200.50` |
| Raw Socket | TCP `5025`，已驗證 |
| HiSLIP | TCP `4880` 可達；尚未安裝 R&S VISA |
| RsInstrument resource | `TCPIP::192.168.200.50::5025::SOCKET` |
| RsInstrument backend | `SelectVisa='socketio'` |
| `*IDN?` | `Rohde&Schwarz,CMP,1201.0002k18/102502,6.0.50.23` |
| Firmware | `6.0.50.23` |
| CMsquares Complete Setup | `2025.31.0.10` |
| WLAN software | `6.0.50.14` |
| `*OPC?` | `1` |
| SCPI error | `0,"No error"` |

Detailed hardware, license and current WLAN workspace discovery is recorded in
[docs/hardware-discovery.md](docs/hardware-discovery.md). The planned user interface
is described in [docs/gui-spec.md](docs/gui-spec.md).

## 目前階段目標

Phase 2 只建立安全、可診斷、可測試的連線框架：

- 從外部設定載入 CMP180 位址與通訊參數。
- 建立及關閉 RsInstrument/VISA session。
- 執行 `*IDN?`，保存型號與韌體識別資訊。
- 執行 `*CLS`、`*OPC?` 與 SCPI error queue 檢查。
- 提供 `doctor` 診斷命令。
- 在沒有實機時以 fake transport 完成單元與 contract tests。
- 進行 hardware discovery，確認 CMP180 實際 VISA resource、WLAN 選件、韌體與遠端命令來源。

此階段尚不宣稱已完成 WLAN EVM 自動量測。儀器專屬 SCPI 命令必須先由 CMP180
官方手冊、CMsquares command log/recorder 或實機 query 驗證。

## 規劃中的 CLI

```text
cmp180-auto doctor --config configs/lab.local.yaml
cmp180-auto discover --config configs/lab.local.yaml
cmp180-auto single --config configs/wlan_tx.yaml
cmp180-auto sweep-power --config configs/wlan_tx.yaml
cmp180-auto report --run output/<run_id>
```

目前可直接執行的連線診斷：

```powershell
.\.venv\Scripts\python.exe .\scripts\cmp180_doctor.py
```

唯讀 WLAN 設定與狀態 discovery：

```powershell
.\.venv\Scripts\python.exe .\scripts\cmp180_wlan_discover.py
```

已驗證的 WLAN commands 與 28 欄 OFDM SISO 結果 schema 位於
[docs/scpi-command-matrix.md](docs/scpi-command-matrix.md)。

## 安全原則

- 不在程式碼內寫死儀器 IP、內網資訊或敏感路徑。
- 所有設定先驗證，通過後才操作儀器。
- timeout、SCPI error、無效結果不得靜默忽略。
- 每次執行保存設定、儀器身分、結果、事件與日誌。
- 未完成 hardware discovery 前，不臆造 CMP180 專屬 WLAN SCPI 命令。
