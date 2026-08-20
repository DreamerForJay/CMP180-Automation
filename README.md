# CMP180 WLAN TX EVM Automation

## 中文版本

Python 3.11+ 的 Rohde & Schwarz CMP180 WLAN TX EVM 自動化系統，用可重現、可稽核的流程取代重複的 CMsquares 手動操作，長期產品為中英雙語、響應式公司內網 Web 工具。

### 目前能力

- YAML 驗證、Mock／實機連線、Generator／Analyzer setter、measurement lifecycle 與 RF On／Off。
- 已完成 RF1.1 → RF1.5、6105 MHz、320 MHz、-40 dBm 的 Python 實機 SingleShot。
- 解析 28 欄 OFDM SISO，輸出 CSV、JSON、metadata、raw response 與 HTML report。
- 雙語響應式 Web GUI（含亮／暗主題切換）、Mock 單點／頻率掃描／功率掃描、受保護實機 SingleShot、artifact links 與 EVM／Power／Frequency Error 圖表。
- 安全短掃描核心（頻率與功率）：最大 11 點、-40 dBm 上限與逐點 cleanup；固定三點頻率 CLI HIL 已通過，功率掃描的 `INV` 停止 HIL 已通過，-55 至 -40 dBm 四點有效批次待驗證，Web 按鈕保持鎖定。
- GitHub Actions 執行 Windows／Python 3.11 unit、Mock 與設定驗證；不執行實機 RF。

Mock、dry-run、CMsquares 手動量測或單獨 stored `FETCh` 不得描述成新的完整 Python 實機量測。

### 快速開始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,hardware]"
python -m pytest -m "not hardware"
python -m cmp180_evm validate-config configs\instrument.example.yaml
python -m cmp180_evm validate-config configs\wlan_baseline.example.yaml
```

```powershell
# Mock Web
python -m cmp180_evm.web

# 本機受保護實機 SingleShot；硬體模式禁止綁定非 loopback 位址
python -m cmp180_evm.web --host 127.0.0.1 --enable-hardware
```

實機前必須閱讀 [硬體 SOP](docs/hardware-test-sop.md)，並確認操作員在場、routing、頻率、頻寬、功率與線路損耗。

### 文件導覽

| 文件 | 用途 |
|---|---|
| [使用者指南](docs/user-guide.md) | 安裝、CLI、GUI、Mock 與實機操作 |
| [硬體 SOP](docs/hardware-test-sop.md) | 接線、安全與執行順序 |
| [Web GUI](docs/web-gui-guide.md) | 啟動、硬體鎖定與 artifacts |
| [UI/UX roadmap](docs/ui-ux-roadmap.md) | 公司內部控制台資訊架構與改版階段 |
| [量測欄位](docs/measurement-example-and-fields.md) | 正確輸出與 EVM／Power／Frequency Error |
| [SCPI matrix](docs/scpi-command-matrix.md) | 指令來源、驗證與 schema |
| [硬體探索](docs/hardware-discovery.md) | 已驗證事實與量測證據 |
| [SingleShot 狀態機](docs/single-measurement-state-machine.md) | RF workflow 與 cleanup |
| [安全短掃描](docs/sweep-safety.md) | 頻率／功率 sweep 限制與 HIL gate |
| [視覺化規格](docs/result-visualization-spec.md) | artifacts 與圖表要求 |
| [開發流程](docs/development-workflow.md) | 測試與文件規則 |
| [交接](HANDOFF.md) | 最新狀態與下一步 |

### 安全原則

不自動 Reset；SCPI 集中管理；RF On 前完成安全驗證；所有 RF workflow 在成功、錯誤、逾時與取消時 STOP／ABORT 並 RF Off；invalid token 不轉成 0；沒有正式 limit 時不得宣稱 RF compliance PASS；不提交 output、憑證、license／activation data、測試 cache 或私人裝置 dump。

## English Version

This Python 3.11+ system automates Rohde & Schwarz CMP180 WLAN TX EVM measurements with reproducible, auditable workflows. The long-term product is a bilingual responsive intranet Web tool.

### Current capabilities

- YAML validation, mock/real connection, hardware-verified setters, measurement lifecycle, and RF On/Off.
- Complete Python hardware SingleShot at RF1.1 to RF1.5, 6105 MHz, 320 MHz, and -40 dBm.
- 28-field OFDM SISO parsing with CSV, JSON, metadata, raw-response, and HTML artifacts.
- Bilingual responsive Web GUI (with a light/dark theme toggle), mock single/frequency-sweep/power-sweep, guarded hardware SingleShot, artifact links, and EVM/Power/Frequency Error plots.
- Safety-bounded short-sweep cores (frequency and power) with 11-point and -40 dBm limits plus per-point cleanup. The fixed three-point frequency CLI and power-sweep `INV` stop passed HIL. The -55 through -40 dBm four-point numeric batch remains to be validated, and Web hardware sweep controls stay locked.
- Windows/Python 3.11 GitHub Actions for unit, mock, and configuration checks; CI never runs live RF.

Do not describe mock, dry-run, manual CMsquares operation, or a standalone stored `FETCh` as a new complete Python hardware measurement.

### Quick start

Use the commands in the Chinese section above. Start mock Web with `python -m cmp180_evm.web`; guarded hardware SingleShot uses `python -m cmp180_evm.web --host 127.0.0.1 --enable-hardware`. Hardware mode is loopback-only until authentication and RBAC exist.

### Documentation

The documentation table above is authoritative for operator, SCPI, state-machine, sweep,
GUI, visualization, and handoff material. The [UI/UX roadmap](docs/ui-ux-roadmap.md)
defines the internal-console information architecture, design principles, delivery phases,
and responsive acceptance criteria. Read the [hardware SOP](docs/hardware-test-sop.md)
before any live operation.

### Safety principles

Never reset automatically; centralize SCPI; validate every RF input before RF On; STOP/ABORT and RF Off on every exit path; preserve invalid values; separate workflow success from compliance; never commit outputs, credentials, license/activation data, caches, or private device dumps.
