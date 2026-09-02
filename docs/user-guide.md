# CMP180 EVM Automation 使用者操作指南

本文件說明目前工具。除了設定、Mock、連線與唯讀探索外，固定安全 profile 的 Python 實機 SingleShot、頻率／功率掃描與本機 Web GUI 已完成 HIL。自訂兩點頻率 HIL 曾在第二點收到 `INV` 並安全停止，因此自訂實機掃描仍須重新驗收；不得把該次結果描述為通過。完成一次量測後，仍可使用下列唯讀工具擷取上一筆 28 欄 OFDM SISO 結果：

```powershell
python scripts\cmp180_wlan_result_discover.py
```

此工具只使用 `FETCh`，不會開啟 RF 或啟動新量測。

## 1. 開啟專案

在 PowerShell 進入專案：

```powershell
cd <project-root>
```

確認目前分支：

```powershell
git branch --show-current
```

功能開發應位於專用 feature branch，不要直接在 `main` 修改；分支名稱以當次 PR／交接文件為準，不在操作指南寫死。

## 2. 啟用環境

環境已建立時：

```powershell
.\.venv\Scripts\Activate.ps1
```

第一次建立環境時：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev,hardware]"
```

## 3. 驗證設定檔

驗證 CMP180 連線設定：

```powershell
.\.venv\Scripts\python.exe -m cmp180_evm validate-config `
  configs\instrument.example.yaml
```

驗證 WLAN baseline：

```powershell
.\.venv\Scripts\python.exe -m cmp180_evm validate-config `
  configs\wlan_baseline.example.yaml
```

看到 `OK (instrument)` 或 `OK (wlan_baseline)` 才表示設定格式通過。
格式通過不代表 CMP180 專屬 SCPI 指令已完成驗證。

## 4. Dry Run

Dry Run 只列出預計步驟，不建立儀器連線，也不送出 SCPI：

```powershell
.\.venv\Scripts\python.exe -m cmp180_evm dry-run `
  --instrument-config configs\instrument.example.yaml `
  --config configs\wlan_baseline.example.yaml
```

目前輸出的 EVM、RF OFF 等項目是未來 workflow 計畫，不代表功能已實作。

## 5. Mock 連線

不需要 CMP180：

```powershell
.\.venv\Scripts\python.exe -m cmp180_evm test-connection --mock
```

成功時應顯示：

- `Connected successfully (mock)`
- Mock IDN（使用與實機相同的 `CMP` model token，顯示為 `CMP-MOCK`）
- Mock options
- `Error queue: empty`

## 6. 啟動 GUI

早期的 Tkinter 桌面 GUI（僅支援設定驗證、Dry Run、Test Connection）已移除；這些功能改用 CLI（見上方章節）即可，單點量測、頻率掃描與圖表請改用 Web GUI：

```powershell
python -m cmp180_evm.web
```

詳見 [Web GUI 操作指南](web-gui-guide.md)。

## 7. 執行測試

```powershell
New-Item -ItemType Directory -Force output | Out-Null
.\.venv\Scripts\python.exe -m pytest -q --basetemp=output\pytest-tmp
```

2026-08-27 本機基準為 `152 passed`；後續新增功能時，以當次完整測試輸出為準並同步更新文件。

已驗證 WLAN query-only discovery 時，可執行：

```powershell
python scripts\cmp180_wlan_discover.py |
  Tee-Object output\wlan-discovery-YYYY-MM-DD.txt
```

此工具只從集中式 `configs/scpi_command_map.yaml` 讀取已驗證 query，
不包含任何 WLAN setter、measurement initiate 或 RF control command。

保存量測後可完全離線重建圖表與報告；這兩個命令只讀 artifacts，不會連線儀器：

```powershell
python scripts\plot_results.py output\<run-folder>\results.csv
python scripts\build_report.py output\<run-folder>
```

Web 的歷史比較可拖拉曲線排序、直接改名並調整顏色、線型與點型，也可匯出
SVG、PNG 與整理後 CSV。

## 8. 第一次連接 CMP180

只有在以下條件都滿足後才需要接實機：

- 離線測試全部通過。
- Git 工作區乾淨。
- CMP180 沒有正在執行量測。
- CMP180 IP 仍為 `192.168.200.50`。
- `configs/scpi_command_map.yaml` 的 CMP180 專屬命令仍為 `null`。

執行：

```powershell
.\.venv\Scripts\python.exe -m cmp180_evm test-connection `
  --instrument-config configs\instrument.example.yaml
```

此步驟只允許 `*IDN?`、`*OPT?` 與 `SYST:ERR?`。完整安全規則請見
[hardware-readonly-validation.md](hardware-readonly-validation.md)。

## 9. 目前不能做的操作

固定安全 profile（RF1.1 → RF1.5、6105 MHz、320 MHz、-40 dBm）的 RF ON、Generator／Analyzer setter、Initiate/Stop/Abort 與 EVM／Burst Power／Frequency Error 讀值已完成實機驗證，可透過 CLI SingleShot 或一般本機 Web 啟動使用；`--demo-only` 會停用儀器控制。以下項目仍未完成：

- 固定 profile 的 frequency／power sweep 已完成 CLI 與 Web HIL；自訂實機掃描仍待針對 `INV` finding 完成 trigger／ranging 複查與重新 HIL。
- 正式 WLAN Pass/Fail 判定（尚無正式 limit、path-loss／calibration table，目前只能顯示 workflow health 或示範 threshold）。
- 超出已驗證安全包絡的任意頻率／功率／DUT 輸入；Web 可在 400 MHz–8 GHz 型錄頻率與 WLAN 頻寬內建立計畫，但正式送 RF 仍受 Approved Profile 與 HIL 狀態限制。
- 內網 deployment 所需 authentication、RBAC 與 audit log。

上述功能必須先完成對應的 CMP180 HIL 驗證、命令審核與安全檢查。

## 10. Git 顯示 dubious ownership

若此專案曾由 Codex 建立或提交 `.git`，Windows Git 可能因 Codex 沙箱帳號與
目前登入帳號不同而顯示：

```text
fatal: detected dubious ownership in repository
```

這不代表儲存庫損壞。只對這個確定的專案路徑加入 Git 安全清單：

```powershell
git config --global --add safe.directory `
  <project-root>
```

確認設定：

```powershell
git config --global --get-all safe.directory
git branch --show-current
git status
```

不要將 `*`、整個磁碟或不認識的路徑加入 `safe.directory`。若相同路徑被重複
加入通常不影響 Git；可用 `--get-all` 查看目前清單。

---

# CMP180 EVM Automation User Guide

### 直接式實機控制

實機頁面使用單點、頻率掃描與功率掃描三個直接分頁，不再顯示裝飾性 Generator／Analyzer／Flow 積木，也不要求從下拉選單選擇模式。Run 仍會觸發既有安全表單與最終 RF 摘要確認。多點掃描可按 Pause，系統會等目前點 STOP 且 RF Off 後才顯示 `PAUSED`；Resume 從下一點繼續，Stop 則結束並保存 partial artifacts。SingleShot 不支援中途 Pause。

## English Version

This guide describes the current tool. Configuration validation, Mock operation,
connection checks, query-only discovery, the fixed-profile Python hardware SingleShot,
frequency and power sweeps, and the local Web GUI have completed their applicable
validation. A custom two-point frequency HIL returned `INV` at its second point and
stopped safely, so custom live execution still requires trigger/ranging review and a new
HIL. It must not be reported as a passing run.

### 1. Open the project

Open PowerShell in `<project-root>` and run `git branch --show-current`. Develop on a
dedicated feature branch rather than directly on `main`; use the current PR or handoff
document as the source of truth for the branch name.

### 2. Activate the environment

Run `\.venv\Scripts\Activate.ps1`. For a new environment, create it with
`python -m venv .venv`, then install `-e ".[dev,hardware]"` with the virtual-environment
Python.

### 3. Validate configuration

Run `python -m cmp180_evm validate-config` for both
`configs\instrument.example.yaml` and `configs\wlan_baseline.example.yaml`. An `OK`
result validates the file format; it does not independently revalidate every CMP180 SCPI
command.

### 4. Dry run

Use `python -m cmp180_evm dry-run --instrument-config ... --config ...` to preview the
workflow. A dry run opens no instrument session and sends no SCPI. Planned EVM or RF-Off
steps in its output are not evidence of a completed hardware workflow.

### 5. Mock connection

Run `python -m cmp180_evm test-connection --mock`. The expected output includes a Mock
identity, options, and an empty error queue. No CMP180 is required.

### 6. Start the Web GUI

Run `python -m cmp180_evm.web`, then open `http://127.0.0.1:8765`. The served frontend is
the horizontal workspace in `src/cmp180_evm/web/static/`; `static_v2/` is an archived
design reference. Normal startup enables guarded local hardware control; add `--demo-only`
for training without instrument access. Starting the service does not transmit RF. The old
Tkinter GUI has been removed.

### Direct hardware controls

Hardware uses direct Single, Frequency Sweep, and Power Sweep tabs. Decorative Generator,
Analyzer, and Flow blocks and the measurement-mode dropdown have been removed. Run still
requires the existing safety form and final RF summary. Sweep Pause takes effect only after
the current point has stopped and RF is off; Resume continues at the next point, while Stop
preserves partial artifacts. SingleShot cannot pause mid-transaction.

### 7. Run tests

Run `\.venv\Scripts\python.exe -m pytest -q --basetemp=output\pytest-tmp`. The local
baseline on 2026-08-27 is `152 passed`; always treat the current full test output as
authoritative. The WLAN discovery script is query-only and does not send setters,
measurement initiation, or RF-control commands.

After saving a run, use `python scripts\plot_results.py <results.csv>` and
`python scripts\build_report.py <run-folder>` to rebuild charts and a self-contained
report entirely offline. The Web history comparison supports drag-to-reorder, inline
trace renaming, colour/line/point styling, and SVG, PNG, or normalized CSV export.

### 8. First CMP180 connection

Connect only after the PC and instrument addressing, Ethernet path, and TCP port have
been confirmed. Start with `test-connection`; this path is limited to `*IDN?`, `*OPT?`,
and `SYST:ERR?`. See `hardware-readonly-validation.md` for the complete rules.

### 9. Current limitations

Fixed-profile SingleShot, frequency sweep, and power sweep have passed their CLI/Web HIL.
Custom hardware sweep remains gated after the `INV` finding. Formal WLAN compliance is
also unavailable until approved limits and an approved Path Loss/Calibration Profile
exist. Inputs outside the verified safety envelope are prohibited, and intranet exposure
still requires authentication, RBAC, and audit logging.

### 10. Git dubious ownership

If Windows Git reports dubious ownership after sandbox activity, add only the confirmed
project path with `git config --global --add safe.directory <project-root>`. Never add
`*`, a whole drive, or an unknown directory. Verify the result with `--get-all`, then run
`git branch --show-current` and `git status`.

### 11. Block-based hardware control

The GPRF Generator, WLAN TX Analyzer, and Measurement Flow blocks on the hardware page expose per-resource state. Run still delegates to the guarded form and final RF-summary confirmation; the Generator block cannot enable RF independently. For multi-point sweeps, Pause waits until the current point has completed STOP and RF Off before reporting `PAUSED`; Resume continues at the next point, and Stop terminates while preserving partial artifacts. SingleShot cannot pause mid-transaction.

## 中文：全 WLAN waveform 與頻段工具

先用 query-only 工具一次盤點儀器 waveform，再用單一 HIL 工具跑 11 個合法區段：

```powershell
.\.venv\Scripts\python.exe scripts\cmp180_waveform_catalog.py
.\.venv\Scripts\python.exe scripts\cmp180_full_wlan_campaign_validate.py `
  --confirm-direct-cable --confirm-no-attenuator `
  --confirm-operator-present --confirm-full-wlan-campaign
```

中斷後可重複 `--section 2.4GHz-bw20` 只補指定區段。每次切換 waveform 前都要求
RF OFF／measurement idle；每個 channel center 都是完整 SingleShot 並在 finally
Stop／Abort／RF Off。11 個完成 HIL 的 section 已納入 Web approved profile；一般 Web
自訂掃描會在 RF OFF／measurement idle 時依頻寬自動切換並回讀匹配 waveform。
400 MHz–8 GHz 仍只是儀器調諧型錄範圍，非 WLAN 空隙不會被核准執行。

## English: full WLAN waveform and band tools

First inventory the instrument waveform directory with the query-only tool, then use one
HIL tool for all 11 legal sections:

```powershell
.\.venv\Scripts\python.exe scripts\cmp180_waveform_catalog.py
.\.venv\Scripts\python.exe scripts\cmp180_full_wlan_campaign_validate.py `
  --confirm-direct-cable --confirm-no-attenuator `
  --confirm-operator-present --confirm-full-wlan-campaign
```

After interruption, repeat `--section 2.4GHz-bw20` to resume only a named section. Every
waveform switch requires RF OFF and an idle measurement. Every channel center is a complete
SingleShot with Stop/Abort/RF Off in `finally`. All 11 HIL-complete sections are now in
the Web approved profile. Normal Web custom sweeps select and read back the matching
waveform while RF is OFF and measurement is idle. The 400 MHz–8 GHz figure remains an
instrument tuning catalog range; non-WLAN gaps are not approved for execution.
