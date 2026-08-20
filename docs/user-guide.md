# CMP180 EVM Automation 使用者操作指南

本文件說明目前工具。除了設定、Mock、連線與唯讀探索外，固定安全 profile 的 Python 實機 SingleShot 與本機 Web GUI 已完成。實機 frequency sweep 尚未通過 HIL，因此保持鎖定。完成一次量測後，仍可使用下列唯讀工具擷取上一筆 28 欄 OFDM SISO 結果：

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

目前基準為 `95 passed`。

已驗證 WLAN query-only discovery 時，可執行：

```powershell
python scripts\cmp180_wlan_discover.py |
  Tee-Object output\wlan-discovery-YYYY-MM-DD.txt
```

此工具只從集中式 `configs/scpi_command_map.yaml` 讀取已驗證 query，
不包含任何 WLAN setter、measurement initiate 或 RF control command。

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

固定安全 profile（RF1.1 → RF1.5、6105 MHz、320 MHz、-40 dBm）的 RF ON、Generator／Analyzer setter、Initiate/Stop/Abort 與 EVM／Burst Power／Frequency Error 讀值已完成實機驗證，可透過 CLI SingleShot 或 `--enable-hardware` Web GUI 使用。以下項目仍未完成：

- 實機 frequency／power sweep（安全短掃頻核心與 Mock 已完成，3 點 HIL 尚未執行，Web 實機 sweep 鎖定）。
- 正式 WLAN Pass/Fail 判定（尚無正式 limit、path-loss／calibration table，目前只能顯示 workflow health 或示範 threshold）。
- 任意頻率／功率／DUT 輸入（Web 實機模式鎖定單一已驗證 profile）。
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
