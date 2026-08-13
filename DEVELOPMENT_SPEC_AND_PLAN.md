# 已由 CMP180 規格取代

此文件原先依資料夾內的 SMW200A + FSW85 簡報建立，已不再是目前專案的主規格。

目前專案目標已改為 **Rohde & Schwarz CMP180 WLAN TX EVM 自動化量測系統**。

請改用 [CMP180_DEVELOPMENT_SPEC_AND_PLAN.md](CMP180_DEVELOPMENT_SPEC_AND_PLAN.md)。

以下舊內容僅保留作為歷史參考，不應作為開發或驗收依據。

---

# [Legacy] R&S SMW200A + FSW85 EVM 量測自動化

## 完整開發規格與執行計畫

文件版本：v1.0  
規劃日期：2026-08-13  
專案週期：12 週  
適用對象：RF 實習生、指導工程師、測試／驗收人員

---

## 1. 文件目的

本文件將資料夾內兩份來源文件轉為可直接執行的軟體開發規格：

- `RF_Intern_EVM_Plan_Presentation.pdf`：定義專案目標、12 週節奏、交付物及評估比重。
- `Remote_Control_SCPI_GettingStarted_en_04.pdf`：定義 SCPI 通訊、語法、狀態查詢、錯誤佇列及同步原則。

本規格涵蓋需求、架構、模組、流程、設定、資料格式、例外處理、測試、文件、排程、驗收及風險。儀器專屬 SCPI 命令仍須以 SMW200A 與 FSW85/K70 的實機版本及 Command Reference 驗證；本文件不臆造未由現有資料提供的型號專屬命令。

---

## 2. 專案願景與成功定義

### 2.1 核心目標

使用 Python 透過 LAN/VISA 控制 R&S SMW200A 向量訊號產生器與 R&S FSW85 訊號暨頻譜分析儀，自動完成 EVM 量測，至少支援：

1. 儀器連線與識別。
2. 訊號與分析參數設定。
3. 單點 EVM 量測。
4. EVM vs Power 功率掃描。
5. EVM vs Frequency 頻率掃描。
6. 結果記錄、統計、圖表及 Constellation 截圖。
7. 可重現的測試報告。
8. 5G NR 與 LTE 兩種量測設定檔。

### 2.2 可量化成功標準

- 新環境依 README 可在 30 分鐘內完成安裝與首次連線。
- 每次執行都產生唯一 Run ID、完整設定快照、原始結果、摘要、日誌及圖表。
- 每一掃描點均可追溯至時間、儀器身分、頻率、功率、標準與量測品質狀態。
- 通訊中斷、逾時、SCPI 錯誤或無效數值時不靜默失敗；須記錄且依政策重試、跳點或終止。
- 掃描點數、輸出資料列數與成功／失敗／跳過點數可互相核對。
- 固定條件下重複量測結果須落在專案於 Week 5 與 RF 指導者確認的允收界線內。
- Demo 可於 10–15 分鐘內完成：連線、單點量測、至少一種掃描、結果視覺化與報告展示。

### 2.3 非目標（首版）

- 不建立通用儀器控制平台或多廠牌抽象層。
- 不以 GUI 取代 CLI／設定檔；GUI 可列為延伸功能。
- 不在未校正的環境宣稱量測具備實驗室認證或可直接作為產品規格判定。
- 不保證支援未驗證的儀器韌體、未安裝的 FSW K70 選件或任意 waveform 格式。
- 不把 Trigger 同步、自訂 waveform 及 HTML 報告列為最小可行版本的阻斷條件；它們屬第二階段功能。

---

## 3. 使用情境與角色

### 3.1 角色

- 操作者：選擇設定檔並執行量測，查看結果與錯誤訊息。
- RF 工程師：定義訊號標準、分析參數、EVM 指標與合理性界線。
- 開發者：維護儀器驅動、量測流程、資料與測試。
- 審查／驗收者：依驗收矩陣確認交付物及可重現性。

### 3.2 主要使用情境

- UC-01 檢查環境與兩台儀器是否可用。
- UC-02 執行單點 EVM，快速確認鏈路與設定。
- UC-03 固定頻率、依功率清單掃描並繪製 EVM vs Power。
- UC-04 固定功率、依頻率清單掃描並繪製 EVM vs Frequency。
- UC-05 套用 5G NR 或 LTE profile 執行相同流程。
- UC-06 儲存 Constellation 截圖與關鍵結果。
- UC-07 從既有 Run 重新產生圖表與報告，不重新操作儀器。
- UC-08 在錯誤或中斷後查明失敗點，必要時從未完成點續跑。

---

## 4. 功能需求

需求優先級：P0＝首版必要、P1＝12 週內應完成、P2＝有餘裕再完成。

| ID | 優先級 | 需求 | 驗收重點 |
|---|---:|---|---|
| FR-001 | P0 | 由 YAML 設定檔載入儀器位址、標準、頻率、功率、逾時、輸出與掃描參數 | 格式錯誤在連線前即回報欄位與原因 |
| FR-002 | P0 | 分別開啟 SMW200A 與 FSW85 session | 可查得並記錄 `*IDN?`；型號不符時預設拒絕執行 |
| FR-003 | P0 | 支援 LAN/VISA resource string，預設優先 HiSLIP 或 VXI-11 | 位址不寫死於程式碼 |
| FR-004 | P0 | 提供 `doctor`／連線自檢 | 顯示 Python、RsInstrument、兩台儀器、選件與錯誤佇列狀態 |
| FR-005 | P0 | 建立可預測初始狀態 | 執行重設／清狀態策略並等待完成；策略可由設定控制 |
| FR-006 | P0 | 設定 SG 頻率、功率、RF 輸出及訊號 profile | 設定後可 query-back 驗證關鍵值 |
| FR-007 | P0 | 設定 SA 中心頻率、分析模式與標準 profile | 設定後可 query-back；缺少 K70 時回報明確錯誤 |
| FR-008 | P0 | 執行單點 EVM 量測 | 等待量測完成後取得有效 EVM 與狀態 |
| FR-009 | P0 | 執行功率掃描 | 支援 start/stop/step 或明確 list；每點記錄結果 |
| FR-010 | P0 | 執行頻率掃描 | 支援 start/stop/step 或明確 list；SG/SA 頻率一致 |
| FR-011 | P0 | 將逐點結果寫入 CSV | 即使中途失敗，已完成點仍保留 |
| FR-012 | P0 | 產生 PNG 圖表 | 座標、單位、標題、Run ID 與失敗點標記完整 |
| FR-013 | P0 | 結構化 logging | Console 與檔案皆有時間、層級、Run ID、步驟及儀器代號 |
| FR-014 | P0 | 定期清查 SCPI error queue | 錯誤碼與文字須保留，不得只記「失敗」 |
| FR-015 | P0 | 安全關閉 | 正常、例外與 Ctrl+C 均關閉 RF 輸出並釋放 session |
| FR-016 | P1 | 支援 5G NR、LTE profile | 量測主流程不因標準而分叉；差異封裝於 profile/driver |
| FR-017 | P1 | 儲存 Constellation 截圖 | 檔名與 CSV 量測點可關聯 |
| FR-018 | P1 | 計算平均、標準差、min、max、有效樣本數 | 忽略無效值但保留其原始紀錄與原因 |
| FR-019 | P1 | 產生 HTML 報告 | 含設定、儀器資訊、摘要、圖表、異常與檔案索引 |
| FR-020 | P1 | 支援外部 Trigger／同步設定 | 有 query-back 與 timeout；未同步不得回傳成功值 |
| FR-021 | P1 | 載入自訂 waveform | 驗證本機檔案、儀器端路徑、傳輸結果與啟用狀態 |
| FR-022 | P1 | retry／skip／abort 錯誤政策 | 每類錯誤行為明確、可設定並記錄實際決策 |
| FR-023 | P1 | 離線重製報告 | 僅由某次 run 的 CSV/metadata 產生相同摘要與圖表 |
| FR-024 | P2 | checkpoint/resume | 不重測已成功點；續跑前比對設定與儀器身分 |
| FR-025 | P2 | 效能統計 | 報告每點耗時、總耗時、重試與通訊時間 |

---

## 5. 非功能需求

### 5.1 可靠性

- 每個儀器 session 必須有 connect、identify、configure、measure、error-check、close 生命週期。
- 長時間操作必須使用同步機制，不以固定 `sleep` 當唯一完成判斷。
- 量測資料採逐點落盤或原子 checkpoint，避免最後一次性寫入造成全失。
- RF Output 的預設與 finally 狀態均為 OFF。

### 5.2 可維護性

- Python 3.11 或團隊核准的固定版本。
- 對外函式具 type hints；公開類別／複雜函式有 docstring。
- 儀器專屬 SCPI 僅出現在 driver 或 command profile，不散落於 workflow。
- 單一函式原則上只負責一個階段；設定、I/O、運算與呈現分離。
- formatter、linter、type checker 與 test 可由單一命令執行。

### 5.3 可重現性與追溯

- 保存原始 YAML 副本、正規化後設定、程式版本／Git commit、開始結束時間、時區、主機資訊、`*IDN?`、韌體與可查得的 option 清單。
- 原始結果不可被後處理覆寫；衍生檔可重新產生。
- 任何人工修改或重跑均產生新 Run ID。

### 5.4 效能

- 首版以正確與穩定優先，不先承諾固定每點秒數。
- Week 6 建立基準：連線、configure、acquire、fetch、screenshot、save 分段計時。
- Week 9 的優化不得減少同步、錯誤檢查或資料追溯。

### 5.5 安全與環境

- 儀器 IP、網段、帳號或敏感路徑不得提交至公開倉庫；以 `.env` 或未追蹤 local config 覆寫。
- 設定檔需有限制：最大輸出功率、允許頻率範圍、最大點數、最大 timeout。
- 執行前顯示 sweep 邊界；超越 soft limit 時拒絕執行。
- 實機接線、衰減器、最大輸入功率及校正責任由 RF 工程師核准並記錄。

---

## 6. 建議系統架構

```text
CLI
 ├─ doctor / single / sweep-power / sweep-frequency / report
 └─ Config Loader + Validator
          │
          v
 Measurement Orchestrator
 ├─ Run lifecycle / state machine
 ├─ Sweep point generator
 ├─ Retry and failure policy
 └─ Safety guard
       │                 │
       v                 v
 SMW200A Driver      FSW85 Driver
       └────── Instrument Session ──────┘
               RsInstrument / VISA
                      │
              SMW200A + FSW85

 Measurement Orchestrator
       ├─ Result model → CSV / JSON metadata
       ├─ Plot service → PNG
       ├─ Screenshot service → PNG
       └─ Report service → HTML
```

### 6.1 分層責任

- `cli`：解析參數、顯示摘要、設定 exit code；不直接送 SCPI。
- `config`：schema、預設值、單位正規化、範圍與互斥欄位驗證。
- `drivers`：儀器連線、SCPI 封裝、query-back、錯誤查詢與截圖。
- `profiles`：5G NR/LTE 的標準特定設定與結果欄位映射。
- `workflows`：單點、功率掃描、頻率掃描、trigger、waveform 流程。
- `models`：設定、單點結果、錯誤、Run metadata 的資料模型。
- `storage`：run 目錄、逐點 append、metadata 與 checkpoint。
- `analysis`：統計、有效值判定、圖表資料整理。
- `reporting`：PNG 與 HTML；不得直接讀取儀器。

### 6.2 建議目錄

```text
cmp180-evm/
├─ pyproject.toml
├─ README.md
├─ CHANGELOG.md
├─ .env.example
├─ configs/
│  ├─ example.local.yaml
│  ├─ profiles/5g_nr.yaml
│  └─ profiles/lte.yaml
├─ src/cmp180_evm/
│  ├─ cli.py
│  ├─ config.py
│  ├─ models.py
│  ├─ exceptions.py
│  ├─ drivers/{base.py,smw200a.py,fsw85.py}
│  ├─ workflows/{single.py,power_sweep.py,frequency_sweep.py}
│  ├─ storage/{run_store.py,csv_writer.py}
│  ├─ analysis/{statistics.py,plots.py}
│  └─ reporting/html.py
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  ├─ hardware/
│  └─ fixtures/
├─ docs/
│  ├─ user-guide.md
│  ├─ developer-guide.md
│  ├─ scpi-command-matrix.md
│  └─ test-report-template.md
└─ output/                 # gitignored
```

---

## 7. 量測流程與狀態機

### 7.1 標準流程

1. 解析 CLI 與 YAML。
2. Schema、單位、limit、點數及輸出路徑驗證。
3. 建立 Run ID 與輸出目錄，保存設定快照。
4. 連線 SMW200A、FSW85；執行 `*IDN?` 並檢查型號。
5. 清查既有 error queue；依策略 reset/clear/synchronize。
6. 驗證 FSW85 K70 與 profile 所需能力。
7. RF Output 維持 OFF，先完成 SG 與 SA 設定及 query-back。
8. 若需要，載入 waveform 與設定 trigger。
9. 啟用 RF Output。
10. 對每個掃描點：設定 → 同步 → 擷取 → fetch → 驗證 → error-check → 落盤。
11. 依設定保存 Constellation 截圖。
12. 關閉 RF Output、釋放 session。
13. 計算統計、產生圖表與 HTML。
14. 寫入 run final status 與摘要，回傳 exit code。

### 7.2 Run 狀態

`CREATED → VALIDATED → CONNECTED → CONFIGURED → RUNNING → FINALIZING → COMPLETED`

異常分支：

- 可重試：`RUNNING → RETRYING → RUNNING`
- 可跳點：`RUNNING → POINT_FAILED → RUNNING`
- 不可恢復：任一狀態 `→ ABORTING → FAILED`
- 使用者中止：任一執行狀態 `→ CANCELLED`

終止前均執行 best-effort safety cleanup；cleanup 自己的錯誤亦須另行記錄。

---

## 8. SCPI 與通訊設計規範

### 8.1 連線

- 使用 RsInstrument 作為 Python 高階通訊層，底層由 VISA 處理。
- LAN 協定依環境選擇 HiSLIP、VXI-11 或 raw socket；典型 port 分別為 4880、動態 RPC、5025/5125。
- resource string 必須外部設定，不依賴固定 IP。
- connect timeout、operation timeout、query delay、termination 必須可設定且有合理預設。

### 8.2 初始化

- 測試開始前建立可預測狀態；建議基線為 `*RST`、`*CLS` 與完成同步。
- 是否允許 reset 應可設定，避免破壞共享實驗室儀器上其他人的暫存狀態。
- 初始化後記錄 `*IDN?`，清查 `SYSTem:ERRor:ALL?` 或逐筆 `SYSTem:ERRor?` 直到 `0,"No error"`。

### 8.3 命令規則

- 優先使用文件定義的短式或長式之一並保持全專案一致。
- 命令與 query 原則上分開發送，避免同一 program message 的執行順序不確定。
- 設定關鍵值後使用 query-back；query 回傳數值通常無單位，程式內統一轉為基本 SI 單位。
- Boolean query 需接受 `0/1`；文字結果可能為短式。
- 將 `9.91E37`、NAN、INF/NINF 或 profile 指定 sentinel 判定為無效量測，不當作一般浮點數繪圖。
- 檔案或波形等大量資料使用 definite block data，解析 `#<digits><length><data>`，不得依 newline 猜測結束。

### 8.4 同步

- 短操作優先 `*OPC?`；儀器回傳 `1` 後才進下一階段。
- 長操作可採 `*OPC` 搭配 ESR/STB/SRQ 或 serial poll，降低阻塞。
- 若 polling，間隔建議在 50–1000 ms 內依實測調整；過度 polling 會拖慢儀器。
- `*WAI` 僅在適合且有 timeout 保護時使用，因其缺乏直接回應。
- 禁止以單一固定 sleep 宣告量測完成。

### 8.5 狀態與錯誤

- `*STB?`、`*ESR?` 或 VISA `read_stb()` 用於高階狀態；VISA serial poll 可避免干擾 output buffer。
- 發生 SRQ、SCPI 例外、無效值、逾時及測試階段的每個重要設定區塊後，查詢 error queue。
- error queue 每次讀取會移除項目；需將完整 code/text 寫入本地 log。
- 錯誤分類：connection、timeout、command、execution、device、query、validation、safety、data、user-cancel。

### 8.6 儀器命令矩陣（開發前必填）

需新增 `docs/scpi-command-matrix.md`，每列至少包含：

| 儀器 | 能力 | Set command | Query command | 回傳型別／單位 | 同步方法 | 已驗證韌體 | 來源頁碼 | 實機結果 |
|---|---|---|---|---|---|---|---|---|
| SMW200A | Frequency | TBD | TBD | Hz | query-back | TBD | Product manual TBD | TBD |
| SMW200A | Power | TBD | TBD | dBm | query-back | TBD | Product manual TBD | TBD |
| SMW200A | RF Output | TBD | TBD | Boolean | query-back | TBD | Product manual TBD | TBD |
| FSW85 | Center Frequency | TBD | TBD | Hz | query-back | TBD | Product manual TBD | TBD |
| FSW85/K70 | Start/Single | TBD | TBD | status | OPC/SRQ | TBD | K70 manual TBD | TBD |
| FSW85/K70 | EVM Result | TBD | TBD | dB or % | after complete | TBD | K70 manual TBD | TBD |
| FSW85 | Screenshot | TBD | TBD | block/file | OPC | TBD | Product manual TBD | TBD |

---

## 9. 設定規格

### 9.1 YAML 範例

```yaml
run:
  name: nr_power_sweep
  output_root: output
  operator: local_user
  reset_instruments: true

instruments:
  generator:
    model: SMW200A
    resource: TCPIP::smw200a-host::hislip0
    timeout_ms: 30000
  analyzer:
    model: FSW85
    resource: TCPIP::fsw85-host::hislip0
    timeout_ms: 120000

safety:
  max_generator_power_dbm: 0
  min_frequency_hz: 100000000
  max_frequency_hz: 85000000000
  max_points: 501
  rf_off_on_exit: true

signal:
  standard: 5g_nr
  profile: configs/profiles/5g_nr.yaml
  waveform: null

measurement:
  frequency_hz: 3500000000
  power_dbm: -20
  repetitions: 3
  trigger: immediate
  save_constellation: true

sweep:
  kind: power
  start: -40
  stop: -10
  step: 1
  settle_ms: 100
  on_point_error: retry_then_skip
  retries: 2
```

### 9.2 驗證規則

- `start/stop/step` 與 `values` 二擇一。
- `step` 不得為 0，方向須能從 start 到 stop；以十進位安全方式生成端點。
- 頻率與功率須同時通過設定 soft limit 與儀器 query 得到的能力範圍。
- `repetitions >= 1`、`retries >= 0`、`max_points >= 實際點數`。
- `standard` 必須對應存在且通過 schema 的 profile。
- 正式 run 不允許 placeholder resource、TBD profile 或空 operator。

---

## 10. 資料與輸出規格

### 10.1 Run 目錄

```text
output/20260813T143012+0800_nr_power_sweep_ab12cd34/
├─ config.original.yaml
├─ config.resolved.json
├─ metadata.json
├─ measurements.csv
├─ events.jsonl
├─ run.log
├─ summary.json
├─ plots/evm_vs_power.png
├─ screenshots/point_0001_constellation.png
└─ report.html
```

### 10.2 `measurements.csv` 最低欄位

| 欄位 | 型別／單位 | 說明 |
|---|---|---|
| run_id | string | 唯一執行識別 |
| point_index | int | 由 0 開始且不重複 |
| attempt | int | 此點第幾次嘗試 |
| timestamp | ISO 8601 | 含時區 |
| standard | enum | `5g_nr`／`lte` |
| frequency_hz | float | 實際 query-back 或明確標記 setpoint |
| generator_power_dbm | float | 實際 query-back 或 setpoint |
| repetition | int | 重複量測序號 |
| evm_value | float/null | EVM 主值 |
| evm_unit | enum | `dB` 或 `%`，不可混用 |
| measurement_status | enum | success/invalid/timeout/scpi_error/skipped |
| elapsed_ms | int | 單次量測耗時 |
| scpi_error_code | int/null | 若有錯誤 |
| scpi_error_message | string/null | 若有錯誤 |
| screenshot_path | string/null | 相對 run 目錄 |

標準特定結果（例如 peak/average EVM、頻率誤差、功率、symbol/carrier 指標）可另增欄位，但須在 data dictionary 定義。

### 10.3 Metadata

- Run ID、狀態、開始／結束時間、CLI command、操作者。
- Git commit、package version、Python 與依賴版本。
- 控制電腦名稱與 OS；不得收集不必要的個資。
- 兩台儀器 IDN、韌體、resource、已驗證 option。
- resolved config hash、結果檔 hash、成功／失敗／跳過點數。

### 10.4 圖表

- X 軸：Power (dBm) 或 Frequency (Hz/kHz/MHz/GHz，自動選合理單位)。
- Y 軸：EVM，單位必須與資料一致。
- 重複量測以平均線＋標準差 error bar；可選擇疊加原始點。
- invalid/failed 點以不同標記顯示，不以 0 取代。
- 標題包含標準、固定條件、Run ID；圖下注記成功樣本數及生成時間。

---

## 11. CLI 規格

```text
evm-auto doctor --config configs/lab.local.yaml
evm-auto single --config configs/run.yaml
evm-auto sweep-power --config configs/run.yaml
evm-auto sweep-frequency --config configs/run.yaml
evm-auto report --run output/<run_id>
evm-auto commands validate --instrument fsw85
```

### 11.1 Exit code

- `0`：完成且所有必要點成功。
- `2`：設定／CLI 驗證失敗。
- `3`：連線或儀器身分／能力不符。
- `4`：量測失敗或成功率低於門檻。
- `5`：資料／報告輸出失敗。
- `130`：使用者中止。

Console 結尾固定顯示 Run ID、狀態、成功／總點數、輸出路徑及首要錯誤。

---

## 12. 錯誤處理與恢復政策

| 類型 | 預設行為 | 重試 | 是否繼續下一點 |
|---|---|---:|---:|
| Config/Safety | 連線前終止 | 0 | 否 |
| 身分／選件不符 | 終止 | 0 | 否 |
| 暫時性 timeout | 清查狀態、重試該點 | 2 | 是，依政策 |
| Connection lost | 嘗試重連與重新設定 | 1 | 僅重建成功時 |
| SCPI command error | 記錄 queue，預設終止 | 0 | 否 |
| Measurement invalid | 重量測 | 2 | 是，可標 invalid |
| Screenshot failure | 記錄警告 | 1 | 是，若截圖非必要 |
| CSV write failure | 立即終止並保留 log | 0 | 否 |
| Report failure | run 標 partial；原始量測保留 | 0 | 不適用 |

重試只能針對具冪等性或已明確重建狀態的步驟。每次重試前記錄原因；不得用重試掩蓋持續性 SCPI command error。

---

## 13. 測試策略

### 13.1 測試層級

- Unit：設定驗證、掃描點生成、數值解析、sentinel 判定、統計、命名、exit code。
- Driver contract：使用 fake transport 驗證命令順序、query-back、同步、error queue 與 cleanup。
- Integration（無儀器）：以 transcript／simulator 重播正常與錯誤回應，產生完整 run artifact。
- Hardware-in-the-loop：在實驗室驗證兩台實機、profile、trigger、waveform、效能與重現性。
- End-to-end：由乾淨環境依 README 執行指定 golden scenario。

### 13.2 必要測試案例

| ID | 案例 | 預期 |
|---|---|---|
| TC-001 | 合法設定載入 | 正規化單位與預設值正確 |
| TC-002 | step=0／方向錯誤／點數超限 | 連線前拒絕 |
| TC-003 | IDN 型號不符 | RF 不開啟、exit 3 |
| TC-004 | K70 不存在 | 明確列出缺少能力，RF 不開啟 |
| TC-005 | 初始化有 stale error | 記錄並依政策清除或終止 |
| TC-006 | 單點成功 | CSV 一列、metadata 完整、RF 最終 OFF |
| TC-007 | 功率掃描包含端點 | 點數及 setpoint 次序正確 |
| TC-008 | 頻率掃描 | SG/SA 每點一致且完成同步 |
| TC-009 | `*OPC?` timeout | 依政策重試，無假成功資料 |
| TC-010 | SCPI command error | 保留 error code/text、停止或跳點符合設定 |
| TC-011 | 回傳 9.91E37/NAN | 標 invalid，不進平均、不畫成正常點 |
| TC-012 | 中途 Ctrl+C | 已完成 CSV 保留、RF OFF、狀態 CANCELLED |
| TC-013 | 連線中斷後重連 | 重新 IDN、重新設定後才恢復量測 |
| TC-014 | Constellation 截圖 | 可開啟且與 point_index 關聯 |
| TC-015 | 報告重製 | 不連儀器，摘要數值與原 run 一致 |
| TC-016 | CSV 寫入失敗 | run FAILED，日誌可診斷，RF OFF |
| TC-017 | 固定條件重複 10 次 | 結果穩定度符合 RF 核准界線 |
| TC-018 | README cold-start | 新使用者 30 分鐘內完成 doctor＋single |

### 13.3 品質閘門

- Unit/contract tests 全數通過。
- 核心模組覆蓋率建議 ≥ 80%，安全 cleanup、點生成與 parser 分支接近 100%。
- formatter、linter、type checker 無錯誤。
- 硬體 golden scenario 具簽核紀錄。
- 未解 P0 bug 為 0；P1 bug 需有風險與 workaround。

---

## 14. 12 週開發計畫

### Week 1：RF、EVM 與 FSW85/K70 手動基線

- 學習 EVM、RMS/peak、dB/%、SNR、頻率／相位／IQ 誤差關係。
- 完成接線、安全功率、衰減、校正與最大輸入規範確認。
- 使用 FSW85/K70 手動完成一組 EVM，保存設定與截圖。
- 產出：`docs/measurement-baseline.md`、術語表、手動 golden result。
- Gate：RF 指導者能依文件重做同一量測。

### Week 2：雙儀器手動操作與參數矩陣

- 熟悉 SMW200A 訊號建立、frequency/power/RF output/waveform。
- 以 5G NR 或 LTE 完成至少三組功率／頻率手動測試。
- 確認 K70 option、儀器韌體、LAN、resource string。
- 產出：接線圖、儀器 inventory、手動結果與安全 limits。
- Gate：定義首個自動化 golden scenario 與合理結果範圍。

### Week 3：Python、VISA、RsInstrument 與 SCPI Recorder

- 建立 repository、`pyproject.toml`、虛擬環境、品質工具與 CI。
- 完成兩台儀器 `*IDN?`、`*RST/*CLS/*OPC?`、error query 小程式。
- 使用儀器 SCPI Recorder 比對手動操作命令。
- 產出：doctor prototype、開發環境指南、首版 command matrix。
- Gate：可從 CLI 穩定辨識兩台儀器並安全關閉 session。

### Week 4：單機 driver 與 command 驗證

- 分別實作 SMW200A、FSW85 driver 與 fake transport。
- 驗證頻率、功率、RF output、分析模式、單次量測、EVM fetch。
- 建立 query-back、同步與 error queue 共用機制。
- 產出：driver contract tests、實機 transcript、命令來源頁碼。
- Gate：兩個 driver 可獨立通過正常／timeout／SCPI error 測試。

### Week 5：雙機整合與單點 EVM MVP

- 實作 config schema、run lifecycle、safety guard、單點 workflow。
- 保存 CSV、metadata、events、log；Ctrl+C 時 RF OFF。
- 對照 Week 1/2 手動 golden result。
- 產出：CLI `single`、MVP 測試紀錄。
- Gate：連續 10 次執行無資源洩漏，結果符合核准穩定界線。

### Week 6：功率掃描與視覺化

- 實作 point generator、逐點落盤、repetition、retry/skip。
- 產生 EVM vs Power PNG、統計與效能分段計時。
- 產出：CLI `sweep-power`、範例 CSV/PNG、單元測試。
- Gate：端點、步距、資料列數與圖表完全一致；中斷不丟失既有點。

### Week 7：頻率掃描與多標準 profile

- 實作 `sweep-frequency`，確保 SG/SA 每點同步。
- 將 5G NR、LTE 差異移入 profile／adapter。
- 產出：兩種 profile、兩條示範曲線、data dictionary。
- Gate：主 workflow 不包含散落的標準特定 if/else 與 SCPI。

### Week 8：截圖、統計與 HTML 報告

- 實作 Constellation screenshot 下載／命名／關聯。
- 完成 summary JSON、HTML 報告與離線重製。
- 產出：CLI `report`、測試報告模板、範例 HTML。
- Gate：報告數值可由 CSV 重新計算且一致；所有連結有效。

### Week 9：Trigger、Waveform 與效能優化

- 實作 trigger profile 與自訂 waveform 傳輸／選取／query-back。
- 依 Week 6 baseline 找出 configure/acquire/fetch 瓶頸。
- 只有在維持同步及錯誤檢查前提下，使用 command batching 或 SRQ。
- 產出：效能前後比較與同步測試。
- Gate：優化後結果一致，且總耗時有量化改善或明確結論。

### Week 10：韌性、Logging 與 README

- 完成錯誤分類、reconnect、checkpoint/resume（若納入）、cleanup 測試。
- 強化 log、exit code、doctor 診斷。
- 撰寫 README：安裝、設定、五分鐘入門、故障排除。
- Gate：故障注入案例 TC-009～TC-016 通過。

### Week 11：完整文件、多情境測試與 Demo 彩排

- 撰寫使用者手冊、開發者手冊、SCPI matrix、資料字典。
- 執行至少：NR power、NR frequency、LTE power、錯誤恢復四情境。
- 準備 10–15 分鐘 Demo 腳本、備用錄影／既有 run。
- Gate：非開發者依文件完成 doctor＋single；驗收缺口列表清零或簽核。

### Week 12：Release、最終驗收與移交

- 鎖定版本與依賴、執行全套測試、整理 GitHub。
- 建立 release tag、CHANGELOG、已知限制、維護責任。
- 完成 Demo、最終測試報告與 lessons learned。
- Gate：依第 16 節驗收矩陣簽核，交付物可從乾淨 clone 重建。

---

## 15. 工作分解與估點建議

以 1 點約半天專注工作估算；實機等待、RF 學習及審查另留 buffer。

| Epic | 估點 | 主要週次 |
|---|---:|---|
| RF/手動基線與安全 | 12 | W1–W2 |
| Repository/環境/CI | 6 | W3 |
| 通訊核心與 driver | 18 | W3–W4 |
| Config/models/run storage | 12 | W5 |
| 單點 workflow | 8 | W5 |
| Power/Frequency sweep | 16 | W6–W7 |
| 5G NR/LTE profiles | 10 | W7 |
| Analysis/plots/report | 14 | W6–W8 |
| Screenshot/trigger/waveform | 14 | W8–W9 |
| Resilience/diagnostics | 14 | W9–W10 |
| Tests/fixtures/HIL | 20 | 全期 |
| 文件/Demo/release | 16 | W10–W12 |
| 總計 | 160 | 12 週 |

每週保留約 20% 給實機排程、除錯、技術債與審查；若人力僅一名實習生，先確保 P0，再依序完成 FR-016～FR-023。

---

## 16. 最終交付與驗收矩陣

| 交付物 | 必要內容 | 驗收方法 |
|---|---|---|
| Python 專案 | CLI、drivers、workflows、storage、analysis、reporting | clean clone 安裝並執行測試 |
| 功率掃描 | 設定、CSV、圖表、錯誤處理 | 實機 golden power sweep |
| 頻率掃描 | SG/SA 同步、CSV、圖表 | 實機 golden frequency sweep |
| 多標準 | 5G NR、LTE profile | 各完成至少一個核准案例 |
| 資料記錄 | metadata、events、log、逐點結果 | 隨機抽點追溯完整 |
| 圖表／報告 | EVM 曲線、統計、異常、HTML | 由 CSV 離線重製並比對 |
| 使用者文件 | README、使用手冊、故障排除 | 新使用者 cold-start 測試 |
| 開發文件 | 架構、命令矩陣、資料字典、測試策略 | 工程審查簽核 |
| GitHub | 歷史清楚、無敏感設定、tag、release notes | repository audit |
| Demo | 10–15 分鐘腳本與備援 | 現場展示並回答限制／錯誤策略 |

### 16.1 Definition of Done

一項功能只有在下列條件全部成立才算完成：

- 程式與設定 schema 已提交。
- 單元／contract 測試通過；涉及實機者有 HIL 證據。
- 錯誤、timeout、cleanup 路徑已驗證。
- log、metadata 與使用者錯誤訊息足以診斷。
- README／使用手冊／command matrix 已同步更新。
- 無未處理 P0/P1 review comment。

---

## 17. 風險與因應

| 風險 | 機率 | 衝擊 | 早期訊號 | 因應 |
|---|---:|---:|---|---|
| 缺少 FSW K70 或授權異常 | 中 | 高 | 手動 UI/option query 無 K70 | W2 即盤點；先準備 simulator 與排程替代儀器 |
| 儀器專屬命令／韌體差異 | 高 | 高 | Recorder 與 manual 不一致 | command matrix 綁版本；driver capability probe |
| 實驗室設備時間不足 | 中 | 高 | HIL case 延後 | W2 預約時段；建立 transcript/fake；批次驗證 |
| EVM 結果與手動不一致 | 中 | 高 | 自動值偏差或不穩 | 保存完整設定、query-back；以 golden scenario 逐項比對 |
| 同步不足造成 stale result | 中 | 高 | 值重複、偶發錯點 | `*OPC?`/STB/SRQ；禁止 sleep-only；加 point tag/時間 |
| 功率或接線造成設備風險 | 低 | 極高 | overload/ADC clipping | 軟限制、衰減與最大輸入簽核、RF OFF default |
| 資料單位混淆（dB/%、Hz/GHz） | 中 | 高 | 曲線異常或比較錯誤 | 儲存基本單位＋顯式 unit；schema 阻止混用 |
| 中斷導致結果全失 | 中 | 中 | 長 sweep 無輸出 | 逐點 append、checkpoint、finally cleanup |
| 過早優化降低可診斷性 | 中 | 中 | batching 後錯誤難定位 | W9 才優化；保留 debug command trace 模式 |
| 公開倉庫洩漏內網資訊 | 低 | 高 | config 含 IP/使用者路徑 | local config gitignore、secret scan、release audit |

---

## 18. 追蹤與治理

- 每週一次 30 分鐘 Demo：展示可執行成果，不只報告進度。
- 每週更新：已完成、下週目標、風險、實機使用需求、待決策。
- 關鍵決策以 ADR 保存：通訊協定、reset 政策、EVM 主指標、重試策略、資料單位。
- PR 建議小於 400 行核心差異；driver 命令需附 manual／Recorder 來源。
- 評分對齊來源簡報：技術實現 40%、程式品質 25%、文件報告 20%、學習與回報 15%。

---

## 19. 啟動前待確認事項

以下不是停止規劃的障礙，但必須最晚於對應週次前由負責人確認：

1. SMW200A、FSW85 完整型號、韌體、option（尤其 K70）與可用時段。
2. 實際連接架構、線材、外部衰減、reference clock、trigger 線與最大安全功率。
3. 首個 5G NR/LTE golden waveform 的來源、頻寬、SCS、調變、frame/slot 等設定。
4. EVM 主指標使用 dB 或 %，average/peak 或其他結果項目，以及允收範圍。
5. FSW85 與 SMW200A 的產品 Command Reference/K70 Manual。
6. reset 是否允許、儀器是否共用、LAN 協定與防火牆限制。
7. Python/RsInstrument 版本、GitHub 可見性與 CI 是否能接觸實機。
8. HTML 報告必備欄位、品牌格式及簽核人。

---

## 20. 建議立即執行的前三項工作

1. 補齊兩台儀器的 Command Reference 與 FSW K70 Manual，建立首版 SCPI command matrix。
2. 在實機上完成一個固定條件的手動 golden measurement，保存完整設定、EVM 結果及 Constellation。
3. 建立 Python repository skeleton 與 `doctor`，先驗證 `*IDN?`、reset/clear、`*OPC?`、error queue 及 RF OFF cleanup。
