# CMP180 EVM Automation 使用者操作指南

本文件說明目前 Phase 2 已完成的功能。現階段可以驗證設定、預覽流程、
使用 Mock 測試連線、啟動 GUI，以及對 CMP180 執行 query-only 連線測試；
尚未支援真正的 WLAN TX EVM 量測、功率掃描或頻率掃描。

## 1. 開啟專案

在 PowerShell 進入專案：

```powershell
cd C:\Users\TMYA0006\Desktop\PROJECT\CMP180v0
```

確認目前分支：

```powershell
git branch --show-current
```

目前開發應位於 `feature/phase2-integration`，不要直接在 `main` 修改。

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
- Mock IDN
- Mock options
- `Error queue: empty`

## 6. 啟動 GUI

```powershell
.\.venv\Scripts\python.exe -m cmp180_evm.gui
```

建議操作順序：

1. 保持 `Use mock instrument` 勾選。
2. 選擇 `configs/instrument.example.yaml`。
3. 按下 Validate Config。
4. 選擇 `configs/wlan_baseline.example.yaml`。
5. 執行 Dry Run。
6. 執行 Test Connection，確認 Result 與 Technical log。

取消 Mock 代表會連接真實硬體；完成唯讀驗證前不要取消。

## 7. 執行測試

```powershell
New-Item -ItemType Directory -Force output | Out-Null
.\.venv\Scripts\python.exe -m pytest -q --basetemp=output\pytest-tmp
```

目前基準為 `43 passed`。

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

- RF ON
- Generator power/frequency 設定
- WLAN TX Measurement 設定
- Initiate/Abort measurement
- EVM、Burst Power、Frequency Error 正式讀值
- Power sweep 或 frequency sweep
- Pass/Fail 判定

上述功能必須先完成 CMP180 SCPI Discovery、命令審核、Mock 測試與安全檢查。

## 10. Git 顯示 dubious ownership

若此專案曾由 Codex 建立或提交 `.git`，Windows Git 可能因 Codex 沙箱帳號與
目前登入帳號不同而顯示：

```text
fatal: detected dubious ownership in repository
```

這不代表儲存庫損壞。只對這個確定的專案路徑加入 Git 安全清單：

```powershell
git config --global --add safe.directory `
  C:/Users/TMYA0006/Desktop/PROJECT/CMP180v0
```

確認設定：

```powershell
git config --global --get-all safe.directory
git branch --show-current
git status
```

不要將 `*`、整個磁碟或不認識的路徑加入 `safe.directory`。若相同路徑被重複
加入通常不影響 Git；可用 `--get-all` 查看目前清單。
