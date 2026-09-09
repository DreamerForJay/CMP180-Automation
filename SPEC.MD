下面這份 SPEC 會以你目前實際狀況為基礎來規劃，不把尚未確認的 CMP180 SCPI 命令、Option 名稱、量測 Query 路徑硬寫成「已知事實」。

新增 Loopback baseline 能力：正式 DUT 判定前，以獨立 SingleShot repeats 驗證 Tester path。Validity、Stability 與 Reasonableness 必須分層；Draft 或未指定 threshold 不得產生正式 `LOOPBACK_READY`。Raw repeats、outlier 標記、profile snapshot、統計與 cleanup evidence 必須可追溯。第一版為單頻點 repeats，多頻點 frequency × repeat 後續增量加入。2026-09-03 Repeat=10 實機 HIL 已核准 6105 MHz／320 MHz／−40 dBm／RF1.1-RF1.5 固定 baseline；只有相同門檻與至少 10 repeats 可使用該 approved profile，其他條件維持 draft。

全 WLAN section Loopback 批次固定涵蓋 11 個已核准 section 代表點，每點 Repeat=10 且逐 profile 保存 artifact。執行只能使用 RF1.1-RF1.5 direct-cable route；任一 SCPI／cleanup error 必須停止後續 profile。2026-09-03 的 110/110 valid HIL 已讓各代表點取得獨立 source evidence 並升級為 approved。這不授權其他頻率、功率、route 或 UD Box path。

相同 11 個代表點在升級後必須直接選到 approved lifecycle，且只有 validity、stability、reasonableness 均通過才可輸出 `LOOPBACK_READY`。2026-09-03 升級後回歸為 110/110 valid、11/11 `LOOPBACK_READY`。Web 所有量測與校正檢查計畫、Preview、安全阻擋原因、修正方式及最後確認必須隨中文／English 選擇即時切換；語言切換不得重新送出 SCPI、Preview API 或 RF job。

GPRF power sweep 可作為 PA Gain／Pout／P1dB 圖的軟體計算入口：以既有 GPRF Generator／Measurement power 讀值產生 `pin_dbm`、`pout_dbm`、`gain_db` 與 P1dB 摘要，並保存到 CSV／JSON／metadata／圖表。參考面補償只可由使用者輸入 input cable loss、output cable loss、external gain、external attenuator 與 SA safe limit 後套用於 artifact 計算，不得放寬 CMP180 frequency/power planning guard 或替代實體 attenuator。若 power sweep 尚未觀察到 1 dB gain compression，必須顯示 `not_found` 與最大已觀察 compression／Pin／Pout，不得把最後一點宣稱為 P1dB。此能力目前為軟體與 Mock／離線測試通過，尚未形成新的 PA 實機 RF 驗證證據。

示範模式必須與實機 RF workflow 分離：Mock／Demo 不連接 CMP180、不送 RF，可為訓練展示輸入較寬的功率範圍並模擬 PA Pin／Pout／Gain／P1dB、未來 OIP3／harmonic／ACP 等圖表入口；不得套用或顯示實機「安全短掃描上限」作為 demo 輸入限制。所有 demo artifact 必須保留 simulated 標記，且不得作為 HIL、DUT compliance 或 PA 實機特性證據。

目前已確認的基礎是：

* 儀器為 **Rohde & Schwarz CMP180 Radio Communication Tester**
* 使用 **CMsquares Workspace**
* 筆電可透過瀏覽器連到 `192.168.200.50`
* 目前前面板可見：

  * `RF1.1` 已接線
  * `RF1.5` 已接線
* CMsquares 中目前存在：

  * `GPRF Gen 1`
  * `GPRF Meas 1`
  * `WLAN TX 1`
* WLAN TX Measurement 的 Analyzer Routing 顯示為 `RF1.5`
* 畫面已能取得 WLAN EVM、Burst Power、Peak Power、Frequency Error 等結果
* 目前訊號顯示為：

  * EHT_MU
  * MCS 11
  * 1024-QAM 5/6
  * 1 Spatial Stream
  * GI 3.2 μs
  * 4×LTF
* 畫面曾出現 `Band = 5 GHz`、`Center Frequency = 6105 MHz` 的設定不一致
* 原 PDF 的專案目標是完成 EVM 量測自動化、功率／頻率掃描、資料記錄、圖表、操作文件與 Demo；原始設備是 SMW200A + FSW85，但你目前實際設備是 CMP180，因此此 SPEC 會保留原專案精神，改成 CMP180 版本。

---

# CMP180 WLAN EVM 自動化量測系統

## Software Requirements Specification

建議專案名稱：

```text
cmp180-wlan-evm-automation
```

建議中文名稱：

```text
CMP180 WLAN EVM 自動化量測與分析系統
```

建議版本：

```text
SPEC Version: 0.1.0
Status: Draft / Hardware Discovery Required
```

---

# 1. 專案背景

目前 EVM 量測主要透過 CMsquares GUI 手動操作。

手動操作能完成：

* 訊號產生
* RF Routing
* Analyzer Level 設定
* WLAN TX Measurement
* EVM 顯示
* Burst Power 顯示
* 多次量測統計
* 各種結果頁面切換

但若後續要執行：

* 多個 Power Point
* 多個 Frequency Point
* 多個 MCS
* 多個 Bandwidth
* 重複測試
* 自動記錄
* 自動畫圖
* 自動產生報告

純 GUI 操作容易出現：

* 忘記清除前一筆統計
* Generator 與 Analyzer 頻率不同步
* External Attenuation 設錯
* Expected Power 未更新
* 不同測試點的量測條件不一致
* 手動複製數值錯誤
* 測試重現困難
* 無法追蹤當時的設定與儀器狀態

因此需要建立一套 Python 自動化框架，讓量測流程可重複、可記錄、可檢查、可輸出。

---

# 2. 專案目標

## 2.1 核心目標

建立一套可在 VS Code 執行的 Python 專案，用於控制 CMP180 完成 WLAN TX EVM 自動化量測。

系統最終應能完成：

```text
載入測試設定
→ 連接 CMP180
→ 驗證儀器身分
→ 設定 Generator
→ 設定 WLAN Analyzer
→ 設定 RF Routing
→ 設定 Frequency / Power / Bandwidth / MCS
→ 開啟 RF
→ 執行 Level Adjustment
→ 執行量測
→ 讀取 EVM / Power / Frequency Error
→ 驗證量測有效性
→ 儲存原始資料
→ 繪製圖表
→ 產生報告
→ 關閉 RF
```

---

## 2.2 主要交付物

依照 PDF 原始規劃，交付物包含：

1. 完整 Python 自動化程式
2. 功率掃描
3. 頻率掃描
4. 測試資料 CSV
5. 測試圖表 PNG
6. 測試報告 HTML
7. README
8. 使用者操作手冊
9. 測試設定範例
10. 儀器 SCPI 命令對照文件
11. GitHub Repository
12. 10～15 分鐘 Demo

這些項目與原 PDF 的預期交付一致，只是儀器實作改為 CMP180。

---

# 3. 專案範圍

## 3.1 第一階段納入範圍

第一階段先限定為：

* 單台 CMP180
* 單一 LAN 連線
* 單一 Generator Instance
* 單一 WLAN TX Measurement Instance
* 單一路徑：

  * Generator Port：待確認，暫定可能為 RF1.1
  * Analyzer Port：目前已確認 GUI 顯示 RF1.5
* WLAN TX EVM
* 單 Spatial Stream
* 單頻點量測
* Power Sweep
* Frequency Sweep
* CSV
* PNG
* HTML Report
* Logging
* Error Handling
* Dry Run
* Simulation／Mock Mode

---

## 3.2 第一階段不納入範圍

以下暫不保證在第一版完成：

* 多台 CMP180 同時控制
* 多 DUT 平行測試
* MIMO 多鏈路同步
* OTA Chamber
* DUT 自動控制
* Wi-Fi Signaling Test
* Trigger Cable 同步
* 外部 Switch Matrix
* VNA 自動補償
* 自動校正
* 5G NR 自動化
* LTE 自動化
* 資料庫伺服器
* 雲端上傳
* CI 中直接連接真實儀器
* 未經確認的 CMP180 專有 SCPI

---

# 4. 目前硬體基線

## 4.1 已確認項目

| 項目                  | 目前狀態              |
| ------------------- | ----------------- |
| 儀器                  | R&S CMP180        |
| 控制介面                | CMsquares         |
| Browser IP          | `192.168.200.50`  |
| 儀器連線                | Ethernet          |
| Analyzer Port       | GUI 顯示 RF1.5      |
| RF1.1               | 已接線，但功能尚未完全確認     |
| RF1.5               | 已接黃色 RF 線         |
| WLAN TX Measurement | 已建立               |
| EVM 結果              | 已有量測數值            |
| Burst Power         | 已有量測數值            |
| Multi Evaluation    | 畫面可見              |
| Standard            | 畫面顯示 EHT_MU       |
| MCS                 | 畫面顯示 11           |
| Modulation          | 1024-QAM 5/6      |
| Frequency           | 畫面顯示 6105 MHz     |
| Band                | 畫面曾顯示 5 GHz，疑似不一致 |

---

## 4.2 尚待確認項目

這些不能先假設，開發前需要實測或從儀器匯出設定確認：

| 項目                    | 待確認內容                              |
| --------------------- | ---------------------------------- |
| RF1.1 功能              | 是否確實為目前 Generator Output           |
| RF1.1 到 RF1.5 路徑      | 是否直接 Loopback、是否經過 DUT、衰減器或其他模組    |
| External Attenuation  | 真實線損是多少                            |
| Generator Instance    | 是 GPRF Generator 還是 WLAN Generator |
| WLAN Generator        | 是否真的由 CMP180 產生 EHT 波形             |
| Remote Interface      | VISA、HiSLIP、Raw Socket 哪個可用        |
| SCPI Port             | 若使用 Raw Socket，實際 Port 未確認         |
| CMP180 Firmware       | 版本未確認                              |
| Installed Options     | `*OPT?` 尚未取得                       |
| SCPI Recorder         | 所在選單與匯出格式尚未確認                      |
| WLAN Measurement SCPI | 尚未取得                               |
| Screenshot SCPI       | 尚未取得                               |
| Statistic Clear SCPI  | 尚未取得                               |
| Adjust Level SCPI     | 尚未取得                               |
| Fetch EVM SCPI        | 尚未取得                               |
| Fetch Power SCPI      | 尚未取得                               |
| Result Format         | 單值、CSV 字串或陣列尚未確認                   |

這些項目應列入 Discovery 階段，不應由 AI 猜測。

---

# 5. 系統使用情境

## 5.1 使用者角色

主要使用者：

```text
RF 實習生／RF 測試工程師
```

使用者具備：

* 基礎 Python 能力
* 基礎 RF 概念
* 可操作 CMsquares
* 可查看儀器面板與線路
* 可修改 YAML 設定
* 不一定熟悉 SCPI

---

## 5.2 使用情境 A：單次量測

使用者希望：

```text
在指定頻率、功率、MCS 與 Bandwidth 下，
執行一次 WLAN TX EVM 量測，
取得所有必要數值並保存。
```

輸入：

* Frequency
* Band
* Bandwidth
* Standard
* MCS
* GI
* Spatial Stream
* Generator Power
* External Attenuation
* Expected Power
* Burst Count

輸出：

* EVM All
* EVM Data
* EVM Pilot
* Burst Power
* Peak Power
* Crest Factor
* Frequency Error
* Symbol Clock Error
* IQ Offset
* Detected Standard
* Detected Bandwidth
* Pass／Fail
* Timestamp
* Configuration Snapshot

---

## 5.3 使用情境 B：功率掃描

使用者指定：

```text
start = -30 dBm
stop  = -10 dBm
step  = 2 dB
```

系統依序：

```text
-30
-28
-26
...
-10 dBm
```

每個功率點執行：

1. 設定 Generator Power
2. 等待穩定
3. 更新 Expected Power
4. 必要時 Adjust Level
5. 清除統計
6. 執行固定 Burst 數
7. 讀取結果
8. 驗證結果
9. 儲存資料
10. 繼續下一點

最後產生：

* EVM vs Generator Power
* EVM vs Measured Power
* Burst Power vs Generator Power
* Frequency Error vs Power
* EVM Std Dev vs Power

---

## 5.4 使用情境 C：頻率掃描

使用者指定多個 Frequency：

```yaml
frequencies_hz:
  - 5.180e9
  - 5.500e9
  - 5.805e9
```

或：

```yaml
start_hz: 5.18e9
stop_hz: 5.805e9
step_hz: 20e6
```

系統必須：

* 同步修改 Generator Frequency
* 同步修改 Analyzer Center Frequency
* 更新 Band
* 更新 Channel，若系統有 Channel Lookup
* 重新 Level Adjustment
* 重新量測
* 記錄每個頻點結果

---

# 6. 系統架構

建議架構分為七層。

```text
CLI / User Interface
        ↓
Test Orchestrator
        ↓
Measurement Workflows
        ↓
CMP180 Domain Services
        ↓
SCPI Command Adapter
        ↓
RsInstrument / VISA / Socket
        ↓
CMP180
```

另外橫向包含：

```text
Configuration
Logging
Validation
Data Storage
Report Generation
Safety Guard
Mock Instrument
```

---

# 7. 專案目錄結構

建議 VS Code Repository：

```text
cmp180-wlan-evm-automation/
│
├─ README.md
├─ pyproject.toml
├─ .gitignore
├─ .env.example
├─ LICENSE
│
├─ configs/
│  ├─ instrument.example.yaml
│  ├─ wlan_baseline.example.yaml
│  ├─ power_sweep.example.yaml
│  ├─ frequency_sweep.example.yaml
│  └─ logging.yaml
│
├─ src/
│  └─ cmp180_evm/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ main.py
│     │
│     ├─ config/
│     │  ├─ loader.py
│     │  ├─ models.py
│     │  └─ validators.py
│     │
│     ├─ instrument/
│     │  ├─ base.py
│     │  ├─ cmp180.py
│     │  ├─ session.py
│     │  ├─ capabilities.py
│     │  ├─ error_queue.py
│     │  └─ mock_cmp180.py
│     │
│     ├─ scpi/
│     │  ├─ common.py
│     │  ├─ generator.py
│     │  ├─ wlan_tx.py
│     │  ├─ screenshots.py
│     │  ├─ templates.py
│     │  └─ registry.py
│     │
│     ├─ domain/
│     │  ├─ enums.py
│     │  ├─ measurement.py
│     │  ├─ result.py
│     │  ├─ test_point.py
│     │  └─ validation.py
│     │
│     ├─ workflows/
│     │  ├─ discovery.py
│     │  ├─ baseline.py
│     │  ├─ single_measurement.py
│     │  ├─ power_sweep.py
│     │  ├─ frequency_sweep.py
│     │  └─ cleanup.py
│     │
│     ├─ data/
│     │  ├─ csv_writer.py
│     │  ├─ json_writer.py
│     │  ├─ metadata.py
│     │  └─ paths.py
│     │
│     ├─ plotting/
│     │  ├─ evm_power.py
│     │  ├─ evm_frequency.py
│     │  └─ common.py
│     │
│     ├─ reports/
│     │  ├─ html_report.py
│     │  ├─ templates/
│     │  │  └─ report.html.j2
│     │  └─ report_models.py
│     │
│     ├─ safety/
│     │  ├─ limits.py
│     │  ├─ guards.py
│     │  └─ interlocks.py
│     │
│     └─ utils/
│        ├─ logging.py
│        ├─ retry.py
│        ├─ timing.py
│        └─ exceptions.py
│
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  ├─ hardware/
│  └─ fixtures/
│
├─ scripts/
│  ├─ discover_instrument.py
│  ├─ test_connection.py
│  ├─ export_scpi_log.py
│  └─ validate_config.py
│
├─ docs/
│  ├─ 01_hardware_setup.md
│  ├─ 02_manual_baseline.md
│  ├─ 03_scpi_discovery.md
│  ├─ 04_power_sweep.md
│  ├─ 05_frequency_sweep.md
│  ├─ 06_troubleshooting.md
│  ├─ scpi_command_map.md
│  └─ known_unknowns.md
│
├─ outputs/
│  └─ .gitkeep
│
└─ logs/
   └─ .gitkeep
```

---

# 8. 設定檔 SPEC

## 8.1 儀器設定

`configs/instrument.yaml`

```yaml
instrument:
  name: cmp180-main

  resource:
    type: visa
    type: rsinstrument
    address: "TCPIP::192.168.200.50::5025::SOCKET"
    options: "SelectVisa='socketio'"

  connection:
    timeout_ms: 10000
    opc_timeout_ms: 30000
    query_delay_ms: 0
    retry_count: 3
    retry_interval_ms: 1000

  identity:
    expected_manufacturer: "Rohde&Schwarz"
    expected_model_contains: "CMP"  # CMP180 reports model token CMP in *IDN?

  session:
    reset_on_connect: false
    clear_status_on_connect: true
    check_error_after_write: true
    close_on_finish: true

  logging:
    scpi_enabled: true
    scpi_log_file: "logs/scpi.log"
    mask_sensitive_data: true
```

注意：

* `resource.address` 目前只是預設設計值。
* 已於 2026-08-13 使用 RsInstrument `SelectVisa='socketio'` 驗證
  `TCPIP::192.168.200.50::5025::SOCKET` 可連線；CMP180 專屬 WLAN SCPI
  指令仍須逐項完成 Discovery。
* 不可以把它寫死在程式碼。

---

## 8.2 RF Routing

```yaml
routing:
  generator_port: "RF1.1"
  analyzer_port: "RF1.5"

  generator_port_confirmed: false
  analyzer_port_confirmed: true

  path_description: "CMP180 internal/external loopback path"
  external_attenuation_db: 0.0

  require_manual_confirmation_before_rf_on: true
```

其中：

```yaml
generator_port_confirmed: false
```

要保留，因為照片只能證明 RF1.1 已接線，不能證明目前 Generator 一定配置在 RF1.1。

確認後才改成：

```yaml
generator_port_confirmed: true
```

---

## 8.3 WLAN Baseline

`configs/wlan_baseline.yaml`

```yaml
test:
  id: wlan-baseline-001
  description: "CMP180 WLAN TX EVM baseline measurement"

signal:
  standard: "EHT"
  burst_type: "EHT_MU"

  band: "6_GHZ"
  center_frequency_hz: 6105000000

  bandwidth_hz: null
  channel: null

  mcs_index: 11
  modulation: "1024QAM_5_6"

  spatial_streams: 1
  space_time_streams: 1

  guard_interval_us: 3.2
  ltf_size: "4XLTF"

generator:
  enabled: true
  output_power_dbm: -30.0
  rf_on_at_start: false

analyzer:
  expected_nominal_power_dbm: -30.0
  external_attenuation_db: 0.0
  user_margin_db: 3.0
  modulation_filter: "ALL"
  iq_swap: false

measurement:
  mode: "multi_evaluation"
  burst_count: 20
  timeout_s: 30
  clear_statistics_before_run: true
  adjust_level_before_run: true

output:
  save_csv: true
  save_json: true
  save_screenshots: false
  generate_plots: true
  generate_html_report: true
```

### 重要限制

`bandwidth_hz` 目前不能亂填。

因為你提供的畫面中沒有明確證明實際 Bandwidth。應保持：

```yaml
bandwidth_hz: null
```

直到你從 Generator 或 Common Settings 確認後再填入。

---

# 9. 資料模型

## 9.1 TestPoint

```python
class TestPoint:
    test_id: str
    point_index: int

    frequency_hz: float
    generator_power_dbm: float

    band: str | None
    channel: int | None
    bandwidth_hz: float | None

    standard: str
    burst_type: str | None
    mcs_index: int | None

    spatial_streams: int | None
    guard_interval_us: float | None
    ltf_size: str | None
```

---

## 9.2 MeasurementResult

```python
class MeasurementResult:
    test_id: str
    point_index: int
    timestamp_utc: str
    timestamp_local: str

    valid: bool
    status: str
    error_message: str | None

    set_frequency_hz: float
    set_generator_power_dbm: float

    measured_burst_power_dbm: float | None
    measured_ltf_power_dbm: float | None
    measured_preamble_power_dbm: float | None
    measured_data_power_dbm: float | None
    measured_peak_power_dbm: float | None
    crest_factor_db: float | None

    evm_all_current_db: float | None
    evm_all_average_db: float | None
    evm_all_max_db: float | None
    evm_all_std_dev_db: float | None

    evm_data_current_db: float | None
    evm_data_average_db: float | None
    evm_data_max_db: float | None
    evm_data_std_dev_db: float | None

    evm_pilot_current_db: float | None
    evm_pilot_average_db: float | None
    evm_pilot_max_db: float | None
    evm_pilot_std_dev_db: float | None

    center_frequency_error_hz: float | None
    symbol_clock_error_ppm: float | None
    iq_offset_db: float | None

    detected_standard: str | None
    detected_bandwidth_hz: float | None
    detected_mcs: int | None

    measured_symbols: int | None
    payload_symbols: int | None
    payload_bytes: int | None

    reliability_status: str | None
    instrument_error: str | None

    raw_result: dict
```

---

## 9.3 RunMetadata

每次完整測試還要額外保存：

```python
class RunMetadata:
    run_id: str
    project_version: str
    git_commit: str | None

    start_time: str
    end_time: str | None

    instrument_idn: str
    instrument_options: str | None
    instrument_firmware: str | None

    instrument_resource: str
    workspace_name: str | None

    generator_port: str
    analyzer_port: str

    external_attenuation_db: float
    config_file: str

    operator: str | None
    notes: str | None
```

---

# 10. SCPI 抽象層 SPEC

這一層很重要。

不要把 SCPI 字串散落在：

* `main.py`
* `power_sweep.py`
* `frequency_sweep.py`

所有命令都應集中管理。

## 10.1 Command Registry

```python
class ScpiCommandRegistry:
    identify: str
    options: str
    clear_status: str
    system_error: str

    set_generator_frequency: str | None
    set_generator_power: str | None
    generator_rf_on: str | None
    generator_rf_off: str | None

    set_analyzer_frequency: str | None
    set_expected_power: str | None
    set_external_attenuation: str | None

    adjust_level: str | None
    clear_statistics: str | None
    initiate_measurement: str | None
    abort_measurement: str | None

    query_evm_all: str | None
    query_evm_data: str | None
    query_evm_pilot: str | None
    query_burst_power: str | None
    query_frequency_error: str | None
```

尚未取得的命令一律保持：

```python
None
```

執行前若發現命令為 `None`，系統要明確報錯：

```text
SCPI command 'query_evm_all' is not configured.
Run SCPI discovery and update scpi_command_map.yaml.
```

不允許 AI 自動補猜。

---

## 10.2 SCPI Mapping File

```yaml
common:
  identify: "*IDN?"
  options: "*OPT?"
  clear_status: "*CLS"
  operation_complete: "*OPC?"
  system_error: "SYST:ERR?"

generator:
  set_frequency: null
  set_power: null
  rf_on: null
  rf_off: null

wlan_tx:
  set_frequency: null
  set_band: null
  set_expected_power: null
  set_external_attenuation: null
  adjust_level: null
  clear_statistics: null
  initiate: null
  abort: null

results:
  burst_power_current: null
  burst_power_average: null
  evm_all_current: null
  evm_all_average: null
  evm_all_max: null
  evm_all_std_dev: null
  evm_data_average: null
  evm_pilot_average: null
  frequency_error_average: null
  symbol_clock_error_average: null
```

這份檔案在 Discovery 階段逐項填入。

---

# 11. SCPI Discovery 階段

在正式開發前，必須有一個獨立階段叫：

```text
Phase 0: SCPI and Capability Discovery
```

## 11.1 Discovery 目標

確認：

* 可用連線方式
* 儀器 ID
* Firmware
* Options
* Workspace 架構
* Generator Instance 名稱
* WLAN Measurement Instance 名稱
* RF Routing 命令
* Frequency 命令
* Power 命令
* RF ON／OFF 命令
* Adjust Level 命令
* Clear Statistics 命令
* Initiate／Abort 命令
* EVM Result Query
* Power Result Query
* Reliability Query
* Screenshot Query

---

## 11.2 每個命令的取得方法

一次只操作一個 GUI 參數。

例如取得 Generator Power 命令：

```text
1. 開啟 SCPI Recorder
2. 清空 Recorder
3. 將 Power 從 -30 dBm 改成 -29 dBm
4. 停止 Recorder
5. 匯出命令
6. 比較變化
7. 回到 -30 dBm
8. 再錄一次
9. 確認真正代表 Power 的命令
10. 加入 mapping file
```

取得 Frequency 命令：

```text
1. 只改 Generator Frequency
2. 匯出命令
3. 只改 Analyzer Frequency
4. 匯出命令
5. 確認兩者是不同命令
```

取得 EVM Query：

```text
1. 開啟結果頁面
2. 查看 Recorder 是否產生 Query
3. 若沒有，查詢 CMP180 Remote Manual
4. 使用官方 Command Help 搜尋 Result Name
5. 在 Console 執行
6. 比對 GUI 顯示值與 Query 回傳值
```

---

## 11.3 Discovery 驗收標準

每個 SCPI 命令必須有：

| 欄位       | 說明                           |
| -------- | ---------------------------- |
| 名稱       | 例如 `set_generator_power`     |
| SCPI     | 真實命令                         |
| 來源       | Recorder／Manual／Command Help |
| 測試值      | 例如 -30 dBm                   |
| GUI 對照   | GUI 顯示是否一致                   |
| Query 結果 | 回傳內容                         |
| 單位       | dBm／Hz／dB                    |
| Instance | Gen 1／WLAN TX 1              |
| 已驗證      | Yes／No                       |
| 備註       | 特殊行為                         |

---

# 12. 儀器連線模組

## 12.1 必要功能

`InstrumentSession` 必須支援：

```python
connect()
disconnect()
write(command)
query(command)
query_float(command)
query_int(command)
query_csv(command)
wait_opc()
clear_status()
drain_error_queue()
```

---

## 12.2 連線驗證

連線後執行：

```text
*IDN?
*OPT?
SYST:ERR?
```

檢查：

* 回傳非空
* 型號包含 CMP180
* Error Queue 為 No Error
* 不自動 Reset

若型號不符：

```text
Expected CMP180 but received:
<actual idn>
```

程式應停止，不可繼續送 WLAN 命令。

---

# 13. 測試工作流程

## 13.1 Baseline Workflow

```text
START
  ↓
Load Config
  ↓
Validate Config
  ↓
Connect Instrument
  ↓
Query IDN / OPT / Firmware
  ↓
Confirm Generator Port
  ↓
Confirm Analyzer Port
  ↓
Check Power Safety
  ↓
RF OFF
  ↓
Configure Generator
  ↓
Configure Analyzer
  ↓
Query Error Queue
  ↓
RF ON
  ↓
Wait Stabilization
  ↓
Adjust Level
  ↓
Clear Statistics
  ↓
Run Measurement
  ↓
Wait for Burst Count / Completion
  ↓
Fetch Results
  ↓
Validate Results
  ↓
Save CSV / JSON
  ↓
Generate Plots / Report
  ↓
RF OFF
  ↓
Close Session
  ↓
END
```

---

## 13.2 Power Sweep Workflow

```text
for each power point:
    set generator power
    wait settling time
    update expected nominal power
    adjust level
    clear statistics
    run measurement
    wait until enough bursts
    fetch result
    validate result
    save result immediately
```

每一點都要立即寫檔，不能等全部完成才存。

原因是中途可能：

* 斷線
* 程式崩潰
* 儀器 Timeout
* 使用者終止
* RF Error

---

## 13.3 Frequency Sweep Workflow

每一點必須按照固定順序：

```text
RF OFF
→ Set Generator Frequency
→ Set Analyzer Frequency
→ Set Band
→ Update Channel if available
→ Query Error Queue
→ RF ON
→ Adjust Level
→ Clear Statistics
→ Measure
→ Fetch
→ Save
```

不能只改 Analyzer，不改 Generator。

---

# 14. 量測有效性驗證

程式不能只看 EVM 有數字。

必須建立 `ResultValidator`。

## 14.1 必要有效條件

一筆結果要標記為 `valid = true`，至少滿足：

```text
1. EVM query 成功
2. Burst Power query 成功
3. 數值不是 NaN
4. 數值不是無窮大
5. 沒有 SCPI Error
6. Measured Symbols > 0
7. Reliability 沒有 Critical Error
8. Detected Standard 與預期相符，若此欄可取得
9. Detected Bandwidth 與預期相符，若此欄可取得
10. Frequency Error 不為 invalid marker
```

---

## 14.2 Invalid Marker

CMP180 有可能回傳：

* 空字串
* `---`
* 超大代表值
* `NCAP`
* `NAN`
* `INF`
* 特殊狀態碼

目前尚未確認實際 SCPI 回傳格式，因此 Parser 必須可設定：

```yaml
invalid_tokens:
  - ""
  - "---"
  - "NCAP"
  - "NAN"
  - "INF"
  - "INVALID"
```

不能直接把所有非數字都轉成 0。

---

## 14.3 驗證結果狀態

```python
class ResultStatus(Enum):
    PASS = "PASS"
    FAIL_LIMIT = "FAIL_LIMIT"
    INVALID_MEASUREMENT = "INVALID_MEASUREMENT"
    CONFIG_MISMATCH = "CONFIG_MISMATCH"
    INSTRUMENT_ERROR = "INSTRUMENT_ERROR"
    TIMEOUT = "TIMEOUT"
    SKIPPED = "SKIPPED"
```

---

# 15. Pass／Fail SPEC

第一版不應自行假設 Wi-Fi 7 EVM 標準門檻。

原因是 Pass／Fail 需要確認：

* IEEE Standard
* PPDU Type
* MCS
* Bandwidth
* RU
* Spatial Stream
* 測試方法
* 公司內部規範
* 儀器判定方式

因此第一版採：

```yaml
limits:
  enabled: false
```

或由使用者明確輸入：

```yaml
limits:
  enabled: true
  evm_all_max_db: -35.0
  source: "internal_spec_xxx"
```

如果沒有來源，報告只能寫：

```text
Measured EVM: -49.55 dB
No pass/fail limit was configured.
```

不能自動宣稱 Pass。

---

# 16. RF 安全規格

## 16.1 RF ON 前檢查

程式必須執行：

```text
Generator Port 已確認
Analyzer Port 已確認
Output Power 在軟體限制內
External Attenuation 已填寫
使用者已確認線路
預期 Analyzer Input 未超出自訂安全上限
```

---

## 16.2 軟體安全限制

```yaml
safety:
  generator_power_min_dbm: -60.0
  generator_power_max_dbm: -10.0

  analyzer_input_soft_limit_dbm: -5.0

  require_port_confirmation: true
  require_attenuation_confirmation: true
  force_rf_off_on_exception: true
```

數字只是專案初始的軟體保護範例，不代表 CMP180 硬體最大規格。

實際值必須由：

* 儀器手冊
* Port 標示
* Mentor
* 公司 SOP

確認後設定。

---

## 16.3 Exception Cleanup

不論任何錯誤：

```python
try:
    run_test()
finally:
    try:
        generator_rf_off()
    finally:
        instrument.close()
```

RF OFF 必須放在 `finally`。

---

# 17. Logging SPEC

## 17.1 Application Log

檔案：

```text
logs/application.log
```

內容包含：

```text
Timestamp
Log Level
Run ID
Test Point
Module
Action
Message
Exception
```

例如：

```text
2026-07-28 14:35:21 INFO run=abc123 point=003 generator
Set generator power to -26.0 dBm
```

---

## 17.2 SCPI Log

檔案：

```text
logs/scpi.log
```

內容：

```text
Timestamp
Direction
Command
Response
Duration
```

例如：

```text
14:35:21.125 TX <command>
14:35:21.147 RX <response>
14:35:21.147 ELAPSED 22 ms
```

---

## 17.3 Error Log

```text
logs/errors.log
```

記錄：

* Python Exception
* VISA Error
* Timeout
* SCPI Error Queue
* Invalid Result
* Config Validation Error

---

# 18. Retry 規格

不是所有錯誤都重試。

## 18.1 可重試

* 暫時性 Timeout
* Query 無回覆
* Measurement 尚未完成
* 暫時性 Connection Busy
* Single Burst 未捕捉

## 18.2 不可重試

* Model 不符
* Port 未確認
* Power 超限
* SCPI Command 未配置
* Config 格式錯誤
* Band 與 Frequency 明顯不一致
* 儀器回報不可恢復錯誤

---

## 18.3 Retry Policy

```yaml
retry:
  max_attempts: 3
  initial_delay_s: 1.0
  multiplier: 2.0
  max_delay_s: 5.0
```

目前實作先限制於 query-only connection diagnostic：`retry_count` 為初次 attempt
之外的重試次數，硬限制 0–5；只處理 transient connection／timeout，且每次 retry
前關閉可能半開的 session。SCPI write、RF workflow、Safety rejection、SCPI error 與
`INV` 不會自動重試，避免重複副作用。RF measurement retry 必須另經 HIL review。

Current implementation is intentionally limited to query-only connection diagnostics.
`retry_count` means retries after the initial attempt and is hard-bounded to 0–5. Only
transient connection/timeout failures qualify, and any half-open session is closed before
retrying. SCPI writes, RF workflows, safety rejections, SCPI errors, and `INV` results are
never retried automatically. RF-measurement retry requires a separate HIL review.

---

# 19. Band 與 Frequency 驗證

你目前曾出現：

```text
Band = 5 GHz
Frequency = 6105 MHz
```

程式要主動攔截這類錯誤。

例如：

```python
def validate_band_frequency(band: str, frequency_hz: float) -> None:
    ...
```

但 Frequency Range 規則不要散落硬編碼。

建議放在：

```yaml
band_rules:
  "2_4_GHZ":
    min_hz: 2400000000
    max_hz: 2500000000

  "5_GHZ":
    min_hz: 5000000000
    max_hz: 5925000000

  "6_GHZ":
    min_hz: 5925000000
    max_hz: 7125000000
```

這組範圍仍應在導入正式規範前由 Mentor 或標準文件確認。

系統偵測到不一致時：

```text
Configuration error:
6105 MHz does not match selected band 5_GHZ.
Suggested band: 6_GHZ.
```

---

# 20. 資料輸出規格

每次測試建立獨立目錄：

```text
outputs/
└─ 2026-07-28_143500_wlan_power_sweep/
   ├─ config_snapshot.yaml
   ├─ run_metadata.json
   ├─ results.csv
   ├─ results.json
   ├─ summary.json
   ├─ logs/
   │  ├─ application.log
   │  └─ scpi.log
   ├─ plots/
   │  ├─ evm_vs_set_power.png
   │  ├─ evm_vs_measured_power.png
   │  ├─ burst_power_vs_set_power.png
   │  └─ frequency_error_vs_power.png
   ├─ screenshots/
   └─ report.html
```

---

# 21. CSV 欄位

至少包含：

```text
run_id
test_id
point_index
timestamp
valid
status
error_message

standard
burst_type
band
channel
frequency_hz
bandwidth_hz
mcs_index
spatial_streams
guard_interval_us
ltf_size

generator_port
analyzer_port
generator_power_dbm
external_attenuation_db
expected_nominal_power_dbm

burst_power_current_dbm
burst_power_average_dbm
burst_power_max_dbm
burst_power_std_dev_db

peak_power_average_dbm
crest_factor_average_db

evm_all_current_db
evm_all_average_db
evm_all_max_db
evm_all_std_dev_db

evm_data_average_db
evm_pilot_average_db

center_frequency_error_average_hz
symbol_clock_error_average_ppm
iq_offset_average_db

detected_standard
detected_bandwidth_hz
measured_symbols
payload_symbols
payload_bytes

reliability_status
instrument_error
```

---

# 22. 圖表規格

## 22.1 Power Sweep

必要圖表：

```text
EVM All Average vs Generator Power
EVM Data Average vs Generator Power
EVM Pilot Average vs Generator Power
Measured Burst Power vs Generator Power
Frequency Error vs Generator Power
EVM Standard Deviation vs Generator Power
```

EVM 圖表需注意：

* EVM dB 越負通常越好
* 不可自動把 Y 軸反轉，除非報告有清楚標示
* Invalid Point 不應連線
* Invalid Point 應以缺值處理，不可當成 0 dB

---

## 22.2 Frequency Sweep

必要圖表：

```text
EVM All Average vs Frequency
Measured Burst Power vs Frequency
Frequency Error vs Frequency
EVM Std Dev vs Frequency
```

---

# 23. HTML 報告

報告至少包含：

1. 專案名稱
2. Run ID
3. 測試時間
4. 儀器 IDN
5. Firmware
6. Options
7. 測試線路
8. Generator Port
9. Analyzer Port
10. External Attenuation
11. WLAN 設定
12. Sweep 設定
13. 結果摘要
14. Invalid Point 數量
15. 圖表
16. 完整結果表格
17. SCPI Error 摘要
18. 測試限制
19. 未確認項目
20. 結論

結論不能自動寫成「通過」。

應依照 Limit 是否有設定：

```text
Pass/fail limits were not configured.
Results are reported for characterization only.
```

---

# 24. CLI SPEC

建議命令：

```powershell
python -m cmp180_evm discover
```

```powershell
python -m cmp180_evm validate-config configs/wlan_baseline.yaml
```

```powershell
python -m cmp180_evm test-connection
```

```powershell
python -m cmp180_evm baseline --config configs/wlan_baseline.yaml
```

```powershell
python -m cmp180_evm power-sweep --config configs/power_sweep.yaml
```

```powershell
python -m cmp180_evm frequency-sweep --config configs/frequency_sweep.yaml
```

```powershell
python -m cmp180_evm report outputs/<run_id>
```

```powershell
python -m cmp180_evm dry-run --config configs/power_sweep.yaml
```

---

# 25. Dry Run 模式

Dry Run 非常重要。

執行：

```powershell
python -m cmp180_evm dry-run --config configs/power_sweep.yaml
```

只顯示預計操作：

```text
[DRY RUN]
Connect to 192.168.200.50
Confirm generator port RF1.1
Confirm analyzer port RF1.5
Set frequency 6105 MHz
Set generator power -30 dBm
Set analyzer expected power -30 dBm
Adjust level
Measure 20 bursts
Query EVM
Save output
RF OFF
```

Dry Run 不得送出任何真實 SCPI Write。

---

# 26. Mock Instrument

為了讓你可以在沒有儀器的環境用 AI 開發，需要做 Mock。

```python
class MockCmp180:
    def set_generator_power(self, power_dbm: float) -> None:
        ...

    def set_frequency(self, frequency_hz: float) -> None:
        ...

    def measure(self) -> MeasurementResult:
        ...
```

Mock 可產生合理的測試資料，例如：

```text
低功率時 EVM 較差
中間功率時 EVM 較好
高功率時 EVM 再變差
```

但 Mock 結果必須在報告標註：

```text
SIMULATED DATA
```

不可與真實儀器資料混淆。

---

# 27. 測試規格

## 27.1 Unit Tests

必測：

* YAML 解析
* Band／Frequency 驗證
* Power Limit 驗證
* Invalid Token Parser
* CSV Writer
* JSON Writer
* EVM Percent Conversion
* Retry Logic
* SCPI Error Parser
* Result Validator
* Report Generation

---

## 27.2 Integration Tests

使用 Mock 測試：

```text
Baseline 完整流程
Power Sweep 完整流程
Frequency Sweep 完整流程
中途 Timeout
中途 Invalid Result
中途 KeyboardInterrupt
RF OFF Cleanup
斷點續跑
```

---

## 27.3 Hardware Tests

必須標記：

```python
@pytest.mark.hardware
```

不應在一般 CI 自動執行。

測試項目：

```text
*IDN?
*OPT?
SYST:ERR?
Generator RF OFF
Set low safe power
Set frequency
Analyzer routing
Single measurement
Fetch EVM
Fetch Power
RF OFF
```

---

# 28. 中斷與續跑

Power Sweep 若有 30 個點，中途失敗不應全部重跑。

每個點完成後在：

```text
checkpoint.json
```

記錄：

```json
{
  "run_id": "abc123",
  "last_completed_point": 8,
  "completed_points": [0, 1, 2, 3, 4, 5, 6, 7, 8]
}
```

續跑：

```powershell
python -m cmp180_evm power-sweep \
  --config configs/power_sweep.yaml \
  --resume outputs/abc123
```

---

# 29. 開發階段規劃

## Phase 0：Discovery

交付：

* `instrument_discovery.json`
* `scpi_command_map.md`
* `known_unknowns.md`
* 可用 Resource String
* IDN／OPT／Firmware
* RF Routing 確認
* SCPI Recorder 命令

驗收：

```text
Python 可成功 query *IDN?
已確認 Generator Port
已確認 Analyzer Port
至少取得 Generator Power、Frequency、RF ON/OFF 命令
至少取得一個 EVM Query
至少取得一個 Power Query
```

---

## Phase 1：Manual Baseline

交付：

* 手動操作 SOP
* Baseline Workspace
* Baseline Screenshot
* Baseline Result Table

驗收：

```text
Generator 與 Analyzer 頻率一致
Band 與 Frequency 一致
RF Routing 已確認
EVM 可重複量測
20 次 Burst 統計可取得
```

---

## Phase 2：Connection Framework

交付：

* InstrumentSession
* Logging
* Error Queue
* Config Loader
* CLI test-connection

驗收：

```text
可連線
可取得 IDN
可安全 Close
錯誤時能輸出明確訊息
```

---

## Phase 3：Single Measurement

交付：

* Baseline Python workflow
* EVM Parser
* Power Parser
* CSV／JSON

驗收：

```text
Python 結果與 GUI 差異在可接受範圍
每次執行都有完整 metadata
發生錯誤時 RF 會關閉
```

---

## Phase 4：Power Sweep

交付：

* Power Sweep
* Plot
* Checkpoint
* HTML Report

驗收：

```text
至少完成 5 個 Power Point
每點有有效性狀態
CSV 與圖表一致
中途停止可續跑
```

---

## Phase 5：Frequency Sweep

交付：

* Frequency Sweep
* Band Validation
* Frequency Plot

驗收：

```text
Generator 與 Analyzer 頻率同步
每個頻點重新 Level Adjustment
Band 不一致會被攔截
```

---

## Phase 6：文件與 Demo

交付：

* README
* 使用手冊
* Troubleshooting
* Demo Script
* GitHub 整理

---

# 30. Acceptance Criteria

## 30.1 基本驗收

```text
AC-001 可從 VS Code 執行
AC-002 可讀取 YAML
AC-003 可連接 CMP180
AC-004 可驗證 *IDN?
AC-005 可安全 RF OFF
AC-006 可執行單次 EVM
AC-007 可取得至少 EVM All 與 Burst Power
AC-008 可輸出 CSV
AC-009 可輸出 JSON
AC-010 可產生圖表
AC-011 可產生 HTML Report
```

---

## 30.2 Power Sweep 驗收

```text
AC-P01 支援 start/stop/step
AC-P02 每個點會儲存
AC-P03 每個點會驗證
AC-P04 Invalid Point 不會當成 0
AC-P05 中斷時 RF OFF
AC-P06 可續跑
```

---

## 30.3 Frequency Sweep 驗收

```text
AC-F01 Generator 與 Analyzer 同步
AC-F02 Band 不一致會報錯
AC-F03 每點可重新 Adjust Level
AC-F04 每點有 Frequency Error
AC-F05 輸出 EVM vs Frequency
```

---

# 31. AI 開發規則

你後續在 VS Code 使用 AI 時，建議在 Repository 根目錄建立：

```text
AGENTS.md
```

內容如下：

```markdown
# AI Development Rules

## Project
This project automates WLAN EVM measurements on a Rohde & Schwarz CMP180.

## Critical Rules

1. Do not invent CMP180 SCPI commands.
2. Use only commands present in `configs/scpi_command_map.yaml`.
3. If a command is missing, raise `ScpiCommandNotConfiguredError`.
4. Never enable RF before running safety validation.
5. Always disable RF in a `finally` block.
6. Do not reset the instrument automatically.
7. Do not convert invalid instrument responses to zero.
8. Store raw instrument responses.
9. Separate hardware code from workflow code.
10. All hardware access must go through the instrument abstraction.
11. All sweep points must be persisted immediately.
12. Every result must include a validity status.
13. Do not declare pass/fail without an explicit configured limit.
14. Do not hardcode the instrument IP.
15. Do not hardcode RF ports.
16. Do not assume RF1.1 is the generator until configuration marks it confirmed.
17. Use type hints.
18. Add tests for all parsing and validation logic.
19. Hardware tests must use the `hardware` pytest marker.
20. Mock results must be clearly labeled simulated.
```

---

# 32. AI 第一階段 Prompt

在 VS Code AI 中先下這個 Prompt：

```text
請依照 repository 中的 AGENTS.md 與 SPEC 實作第一階段專案骨架。

需求：
1. 使用 Python 3.11。
2. 使用 src layout。
3. 使用 pyproject.toml。
4. 建立 typed configuration models。
5. 建立 InstrumentSession protocol。
6. 建立 MockCmp180。
7. 建立 YAML loader。
8. 建立 config validation。
9. 建立 CLI：
   - validate-config
   - dry-run
   - test-connection
10. 不要產生任何未經確認的 CMP180 WLAN SCPI 命令。
11. Common SCPI 只允許先放：
   - *IDN?
   - *OPT?
   - *CLS
   - *OPC?
   - SYST:ERR?
12. 所有未知 WLAN 命令保留 null。
13. 若命令為 null，拋出明確例外。
14. 建立 pytest unit tests。
15. RF ON 邏輯目前不得實際啟用。
```

---

# 33. AI 第二階段 Prompt

等你完成 SCPI Discovery 後：

```text
根據 `configs/scpi_command_map.yaml` 中已驗證的命令，
實作 CMP180 Generator 與 WLAN TX Measurement adapter。

限制：
1. 不得增加 mapping file 中不存在的 SCPI。
2. 每個 write 後依設定檢查 SYST:ERR?。
3. 實作：
   - set_generator_frequency
   - set_generator_power
   - generator_rf_on
   - generator_rf_off
   - set_analyzer_frequency
   - set_expected_power
   - set_external_attenuation
   - adjust_level
   - clear_statistics
   - initiate_measurement
4. 所有 RF ON 必須先通過 SafetyGuard。
5. 所有工作流程必須在 finally 關閉 RF。
6. 新增 Mock 與 Unit Tests。
```

---

# 34. AI 第三階段 Prompt

```text
實作 single measurement workflow。

輸入：
- instrument config
- wlan baseline config
- scpi command map

輸出：
- run_metadata.json
- results.csv
- results.json
- application.log
- scpi.log

要求：
1. 依照 SPEC 的固定流程。
2. 取得 EVM All、EVM Data、EVM Pilot、Burst Power、Frequency Error。
3. 若 Query 尚未配置，清楚報錯。
4. 儲存 raw response。
5. Invalid token 不可轉成 0。
6. Result 必須包含 valid 與 status。
7. 中途錯誤時 RF OFF。
```

---

# 35. 必須避免的 AI 幻覺

AI 很容易在這類專案犯以下錯誤：

## 錯誤 1：自行生成 CMP180 SCPI

例如 AI 可能根據其他 R&S 儀器猜：

```text
CONF:WLAN:MEAS
FETC:EVM?
```

這些不一定適用 CMP180。

處理方式：

```text
一律不接受，除非命令出現在：
1. CMP180 SCPI Recorder
2. CMP180 官方 Remote Manual
3. 儀器內建 Command Help
4. 實機測試驗證
```

---

## 錯誤 2：把 FSW85 K70 命令直接套到 CMP180

PDF 原本提到 FSW85 K70，但目前是 CMP180。

兩者：

* Application 結構
* Instance
* Routing
* SCPI Tree
* Result Query

都可能不同。

---

## 錯誤 3：看到 EVM 數字就判定 Pass

沒有明確 Limit 就不能宣稱 Pass。

---

## 錯誤 4：把 `---` 當成 0

這會讓報表完全錯誤。

---

## 錯誤 5：未確認 RF1.1 就自動開 RF

照片只證明 RF1.1 有線，不證明它一定是 Generator。

---

## 錯誤 6：自動 Reset 儀器

可能清除現有 Workspace 與 Mentor 設定。

預設：

```yaml
reset_on_connect: false
```

---

# 36. 目前最適合的實際下一步

你現在不要直接讓 AI 開始做完整 Power Sweep。

應先完成以下順序：

```text
1. 儲存目前 CMsquares Workspace
2. 確認 RF1.1 在 GUI 中的實際功能
3. 畫出真實 RF 線路
4. 確認是否有 Attenuator／DUT
5. 確認 External Attenuation
6. 修正 Band = 5 GHz 與 6105 MHz 的不一致
7. 查詢 *IDN?
8. 查詢 *OPT?
9. 查詢 Firmware
10. 找到 SCPI Recorder
11. 錄下 Power 修改命令
12. 錄下 Frequency 修改命令
13. 錄下 RF ON／OFF 命令
14. 錄下 Adjust Level 命令
15. 錄下 EVM Query
16. 錄下 Burst Power Query
17. 建立 scpi_command_map.yaml
18. 再開始正式 Python 控制
```

---

# 37. 專案完成定義

這個專案不應以「程式可以跑」作為完成標準。

真正完成應是：

```text
同一份設定在相同硬體配置下可重複執行
每個測試點有完整設定紀錄
每個測試點有有效性判定
所有 SCPI 有來源與驗證紀錄
Generator 與 Analyzer 不會設定不同步
發生錯誤時 RF 一定被關閉
中途失敗不會遺失已完成資料
GUI 與 Python 結果能互相對照
報告不會把未確認結果寫成 Pass
另一位工程師依 README 可以重新執行
```

這才是符合原始 Plan 中「功能完整度、穩定性、程式碼品質、文件與報告」的交付成果。

---

# 38. 2026-09-02 Web 全 WLAN 核准邊界

Web RF 執行核准 RF1.1 → RF1.5、-55～-30 dBm，以及已完成 HIL 的 11 個
2.4／5／6 GHz WLAN band／bandwidth section。每個 section 必須同時匹配頻段、
中心頻率範圍與 20／40／80／160／320 MHz 頻寬；不得用整體 2412–7125 MHz
外框放行頻段間空隙。後端只能在 RF OFF 且 measurement idle 時選擇匹配 waveform，
完成 OPC、error queue 與絕對路徑 readback 後才能繼續設定及 RF On。

單點量測例外允許 CMP180 400–8000 MHz 型錄調諧範圍內的中心頻率。已核准
WLAN section 外的單點必須標示 `HIL_PENDING`，使用已驗證的 EHT／B6GHz
measurement template，並對實際 Generator／Analyzer center frequency 做 readback。
此例外不得套用到 Sweep 或 Loopback baseline，也不得產生 compliance PASS；Route、
功率、操作員確認、錯誤停止與 deterministic cleanup 限制維持不變。

400 MHz–8 GHz 是 CMP180 調諧型錄範圍，不等於 WLAN 可執行範圍。

## English: Loopback baseline requirement

Before formal DUT decisions, the system uses independent SingleShot repeats to validate the tester path. Validity, Stability, and Reasonableness remain separate. Draft or unspecified thresholds cannot produce formal `LOOPBACK_READY`. Raw repeats, outlier flags, profile snapshots, statistics, and cleanup evidence remain traceable. Version one supports one-frequency repeats; frequency-by-repeat execution is a later increment. The 2026-09-03 Repeat=10 live HIL approved the fixed 6105 MHz/320 MHz/−40 dBm/RF1.1-RF1.5 baseline. Only the same thresholds with at least 10 repeats may use that approved profile; other conditions remain draft.

The all-WLAN-section Loopback batch covers fixed representative points for all 11 approved sections, uses Repeat=10 per point, and saves independent artifacts per profile. Execution is restricted to the RF1.1-to-RF1.5 direct-cable route, and any SCPI or cleanup error must stop later profiles. The 2026-09-03 110/110-valid HIL gave every representative point its own source evidence and approved lifecycle. It does not authorize other frequencies, powers, routes, or UD Box paths.

The same 11 representative points must select the approved lifecycle after promotion, and `LOOPBACK_READY` requires passing validity, stability, and reasonableness. The 2026-09-03 post-promotion regression completed 110/110 valid measurements with 11/11 `LOOPBACK_READY`. Every Web measurement and calibration check plan, preview, safety rejection reason, correction instruction, and final confirmation must immediately follow the Chinese/English selector. A language change must not resend SCPI, call a preview endpoint, or start an RF job.

## English: 2026-09-02 Web full-WLAN approval boundary

Web RF execution approves the RF1.1-to-RF1.5 route, -55 to -30 dBm, and the 11
HIL-complete 2.4/5/6 GHz WLAN band/bandwidth sections. Each section must match its band,
center-frequency range, and 20/40/80/160/320 MHz bandwidth. The overall 2412–7125 MHz
envelope must never authorize gaps between WLAN bands. The backend may select a matching
waveform only while RF is OFF and measurement is idle, and must complete OPC, error-queue,
and absolute-path readback checks before configuration continues or RF is enabled.

As a SingleShot-only exception, the center frequency may use the CMP180 catalog tuning
range of 400-8000 MHz. A point outside an approved WLAN section must be labelled
`HIL_PENDING`, use the verified EHT/B6GHz measurement template, and read back the actual
generator and analyzer center frequencies. This exception must not apply to sweeps or the
Loopback baseline and must not produce a compliance PASS. Route, power, operator
confirmation, stop-on-error, and deterministic-cleanup limits remain unchanged.

The CMP180 400 MHz–8 GHz tuning catalog range is not the executable WLAN range.

---

# 39. V1 正式驗收閘門

V1 Acceptance 必須把「量測流程 HIL」與「正式 compliance 核准」分開。完整實機
SingleShot／Sweep artifacts 可證明自動化流程，但正式 `ACCEPTED` 還必須同時具備：

1. 未過期的 Approved Calibration Profile，含真實 `source_evidence`、`approved_by`、
   `approved_at` 與器材識別。
2. Approved Limit Profile，含適用規格 `source_reference`、`approved_by` 與
   `approved_at`。
3. 指定 artifacts 全部為非 Mock、`status=complete`、至少一點且所有點有效。

Acceptance builder 僅能離線讀取上述資料，不得連線儀器或送 RF。任何 gate 未通過時，
總狀態必須是 `BLOCKED` 且 `compliance_claim=false`。

## English: V1 formal acceptance gates

V1 acceptance must separate measurement-workflow HIL from formal compliance approval.
Complete live-hardware SingleShot/Sweep artifacts prove the automation workflow, but
formal `ACCEPTED` status also requires all of the following:

1. A current Approved Calibration Profile with real `source_evidence`, `approved_by`,
   `approved_at`, and equipment identity.
2. An Approved Limit Profile with an applicable `source_reference`, `approved_by`, and
   `approved_at`.
3. Selected artifacts that are non-Mock, `status=complete`, non-empty, and valid at every point.

The acceptance builder may only read these inputs offline; it must never connect to the
instrument or transmit RF. If any gate fails, overall status must be `BLOCKED` and
`compliance_claim=false`.
