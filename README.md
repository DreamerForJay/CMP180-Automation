# CMP180 WLAN EVM 自動化量測系統

自動化 Rohde & Schwarz **CMP180** Radio Communication Tester 的 WLAN TX EVM 量測流程，取代目前透過 CMsquares GUI 手動操作、容易出錯又難以重現的測試方式。

完整規格請見 [SPEC.MD](SPEC.MD)（中文，含背景、資料模型、SCPI 抽象層設計、驗收標準等完整細節）。本 README 只涵蓋「如何安裝、執行、開發」。也提供排版過的 [README.pdf](README.pdf) 版本，方便直接列印或傳給不會用 Git/Markdown 的人看；其設計原始檔是 [docs/README.html](docs/README.html)，內容有更新時可用下列指令重新產生 PDF（需要本機已安裝 Microsoft Edge）：

```powershell
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --disable-gpu --no-sandbox `
  --no-pdf-header-footer --print-to-pdf="README.pdf" "file:///%cd%/docs/README.html"
```

## 目前狀態

專案還在 **Phase 0 / Phase 2** 階段：

- 尚未完成 CMP180 SCPI Discovery，`configs/scpi_command_map.yaml` 內除了標準 IEEE-488.2 共通指令（`*IDN?` `*OPT?` `*CLS` `*OPC?` `SYST:ERR?`）之外，所有 CMP180 專屬指令（Generator、WLAN TX Measurement、EVM/Power 讀值）都刻意留白（`null`）。
- 尚未有真正的量測 workflow（single measurement / power sweep / frequency sweep），目前只有：設定檔載入與驗證、儀器連線骨架（含 Mock 模式）、CLI、Tkinter GUI（設定與連線頁面）。
- `RF1.1` 是否為 Generator 尚未確認；只有 `RF1.5`（Analyzer）已確認。**在完成硬體 Discovery 前，程式不會、也不應該真的開啟 RF。**

## 已驗證的實機基線

- CMP180 IP：`192.168.200.50`
- Resource：`TCPIP::192.168.200.50::5025::SOCKET`
- RsInstrument options：`SelectVisa='socketio'`
- 已驗證安全查詢：`*IDN?`、`*OPC?`、`SYST:ERR?`
- CMP180 專屬 WLAN SCPI 指令仍保持未設定，完成 Discovery 前不會開啟 RF。

既有的實機證據與命令研究資料會繼續保留：

- [硬體探索紀錄](docs/hardware-discovery.md)
- [SCPI command matrix](docs/scpi-command-matrix.md)
- [GUI 規格](docs/gui-spec.md)
- `scripts/cmp180_doctor.py`
- `scripts/cmp180_wlan_discover.py`

## 操作與開發文件

- [使用者操作指南](docs/user-guide.md)：安裝、設定、CLI、GUI、Mock 與實機驗證步驟。
- [功能開發與文件同步規則](docs/development-workflow.md)：每次功能修改必須更新的文件與測試清單。
- [第一次實機唯讀驗證](docs/hardware-readonly-validation.md)：接上 CMP180 前後的安全檢查。

## 安裝

需要 Python 3.11+。

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

若要用真實儀器連線（使用已在 CMP180 驗證的 RsInstrument Raw Socket），額外安裝：

```powershell
pip install -e ".[hardware]"
```

## 使用方式

### CLI

```powershell
# 驗證設定檔（自動判斷是 instrument 還是 wlan baseline 設定）
python -m cmp180_evm validate-config configs/wlan_baseline.example.yaml

# 印出計畫執行的步驟，不會送出任何真實 SCPI 指令
python -m cmp180_evm dry-run --config configs/wlan_baseline.example.yaml

# 測試連線；沒有硬體時用 --mock
python -m cmp180_evm test-connection --mock
python -m cmp180_evm test-connection --instrument-config configs/instrument.example.yaml
```

### GUI（設定與連線）

```powershell
python -m cmp180_evm.gui
```

目前 GUI 涵蓋：載入/瀏覽設定檔、驗證設定檔、Dry Run 預覽、測試連線（可切換 Mock / 真實硬體）。之後量測 workflow（single measurement、power sweep、frequency sweep）完成後，GUI 會加入對應頁面——GUI 與 CLI 共用同一套 `cmp180_evm/actions.py`，不會各自維護一份邏輯。

畫面配置：
- **頂部連線狀態列**：一直顯示「未連線 / 已連線（Mock）/ 已連線（真實硬體，橘色警示）」，不用捲動日誌也能一眼看到目前狀態。
- **Actions 區**：每個按鈕旁邊都有一個「?」按鈕，點下去會跳出該功能的中文說明與操作範例；按鈕下方也有一行英文提示。取消勾選「Use mock instrument」後，checkbox 下方文字會變成橘色警示「⚠ Real hardware mode」，提醒這個操作會真的碰觸硬體。
- **Results 區（分頁）**：
  - 「Result」分頁：結果會用人看得懂的標籤＋數值呈現（例如「Generator port: RF1.1」而不是 `routing.generator_port`），並用圖示＋顏色標示狀態（✓ 綠色成功、✗ 紅色失敗、… 執行中）。
  - 「Technical log」分頁：保留完整的技術性文字紀錄（每行都有 `[HH:MM:SS]` 時間戳記，方便對照指令送出的時間），給需要除錯或想看原始細節的人用。

## 打包成執行檔

在已安裝 `pyinstaller` 的環境下（`pip install -e ".[build]"`），於專案根目錄執行：

```powershell
python -m PyInstaller --noconfirm --onefile --windowed `
  --name CMP180-EVM-GUI --paths src src/cmp180_evm/gui/__main__.py
```

產出的執行檔位於 `dist/CMP180-EVM-GUI.exe`。發布時請把 `configs/` 資料夾複製到 `dist/` 內、與 exe 放在同一層——`gui/app.py` 在打包後的執行檔會改成尋找「exe 所在目錄旁邊的 `configs/`」，而不是原始碼裡的路徑，這樣使用者才能直接編輯 YAML 設定檔、不需要重新打包整個程式。

## 測試

```powershell
pytest -q
```

硬體相關測試會標記 `@pytest.mark.hardware`，不會在一般 CI/本機測試中自動執行（需要真實連上 CMP180 才有意義）。

## 專案結構

```text
src/cmp180_evm/
├─ cli.py             # argparse CLI 入口
├─ actions.py         # CLI 與 GUI 共用的高階操作（validate/dry-run/test-connection）
├─ gui/                # Tkinter GUI
├─ config/             # YAML 載入、pydantic typed models、跨欄位驗證（band/frequency 等）
├─ instrument/         # InstrumentSession protocol、真實 CMP180 session（RsInstrument）、MockCmp180
├─ scpi/               # SCPI 指令唯一集中管理處：common 常數 + ScpiCommandRegistry
└─ utils/              # exceptions、logging

configs/
├─ instrument.example.yaml     # 儀器連線 + RF routing
├─ wlan_baseline.example.yaml  # 訊號/量測參數
└─ scpi_command_map.yaml       # CMP180 指令對照表（未確認指令保持 null）

tests/unit/            # pytest 單元測試
```

## 核心設計原則

這些規則來自 SPEC.MD，是本專案最容易被 AI 或新貢獻者不小心違反的地方，開發前請先讀過：

1. **不可自行編造 CMP180 SCPI 指令。** 只能使用 `configs/scpi_command_map.yaml` 中已確認的指令；缺指令時要丟出 `ScpiCommandNotConfiguredError`，不能用其他 R&S 儀器（如 FSW85/K70）的指令代替猜測。
2. **RF ON 前必須通過安全檢查**（generator/analyzer port 已確認、功率在軟體限制內），且無論流程如何結束都要在 `finally` 關閉 RF。
3. **絕不自動 Reset 儀器**（`reset_on_connect: false`），避免清掉既有的 CMsquares Workspace。
4. **無效量測值不可當成 0**（`---`、`NCAP`、`NAN`、`INF` 等一律視為 invalid，保留原始回應）。
5. **沒有明確設定 Limit 就不能宣稱 Pass。**
6. 所有 SCPI 存取都要走 `instrument/` + `scpi/` 抽象層，不可在 workflow/CLI/GUI 程式碼裡直接寫 SCPI 字串。

完整規則另見 [SPEC.MD 第 31、35 節](SPEC.MD)。

## 開發階段

依 SPEC.MD 第 29 節規劃：Phase 0 Discovery → Phase 1 Manual Baseline → Phase 2 Connection Framework → Phase 3 Single Measurement → Phase 4 Power Sweep → Phase 5 Frequency Sweep → Phase 6 文件與 Demo。目前完成到 Phase 2 的骨架部分；Phase 0（實機 SCPI Discovery）仍需要在儀器上手動操作 SCPI Recorder 才能繼續往下。
