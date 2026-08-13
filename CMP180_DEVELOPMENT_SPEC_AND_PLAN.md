# CMP180 WLAN TX EVM 自動化量測系統

## 完整開發規格與執行計畫

文件版本：0.1.0  
文件狀態：Draft / Hardware Connected, WLAN Discovery Required  
目前階段：Phase 2 — Connection Framework  
目標儀器：Rohde & Schwarz CMP180 Radio Communication Tester  
開發環境：Python 3.11+

已確認基線（2026-08-13）：CMP180 位址 `192.168.200.50`；Raw Socket 5025
搭配 RsInstrument `socketio` 後端連線成功；`*IDN?` 回傳型號欄為 `CMP`、韌體為
`6.0.50.23`；`*OPC?` 回傳 `1`；SCPI error queue 回傳 `0,"No error"`。

---

## 1. 專案目的

將目前透過 CMsquares GUI 手動執行的 CMP180 WLAN TX EVM 測試，轉為可重現、可追溯、可批次執行的 Python 自動化流程。

系統最終應能自動完成：

1. CMP180 連線、能力與狀態檢查。
2. 載入 WLAN TX 測試設定。
3. 建立或套用 CMsquares 對應的 WLAN 測試情境。
4. 觸發 DUT 封包傳輸或等待 DUT 發射。
5. 執行 WLAN TX 擷取與解調分析。
6. 取得 EVM、Power、Frequency Error 等結果。
7. 執行 channel、power、MCS 或其他參數掃描。
8. 保存原始結果、設定、log、統計、圖表與 HTML 報告。

### 1.1 本版調整

- CMP180 是唯一主要儀器。
- 不再以 SMW200A 訊號產生器與 FSW85 分析儀雙機架構作為主流程。
- CMsquares GUI 現有操作是需求探索及結果比對基準。
- 目前缺少 CMP180 型號專屬 WLAN 遠端控制資料，因此先完成 connection framework 與 hardware discovery。

---

## 2. 專案範圍

### 2.1 首版納入

- 單一 CMP180 session 管理。
- LAN/VISA/RsInstrument 連線。
- 儀器識別、韌體與已安裝 option discovery。
- SCPI command、query、同步、狀態與錯誤佇列處理。
- WLAN TX 單點 EVM 量測。
- 主要結果解析與有效性檢查。
- 結果 CSV/JSON、log、PNG 與 HTML。
- 至少一種經實機驗證的 WLAN PHY profile。
- CMsquares 手動結果與自動化結果比對。
- power/channel sweep；其他 sweep 依 discovery 結果排定。

### 2.2 暫不納入

- 非 WLAN 技術的完整支援。
- 多台 CMP180 的平行排程。
- 完整取代所有 CMsquares 功能。
- 通用化為多廠牌測試平台。
- 未取得官方命令依據前，直接假設 CMsquares 操作可由一般 SCPI 一對一重現。
- GUI 為首版必要交付物；首版以 CLI 與設定檔為主。

---

## 3. 成功標準

- 乾淨環境可依 README 在 30 分鐘內完成安裝與 `doctor`。
- `doctor` 可辨識 CMP180，記錄 `*IDN?`、resource、韌體與可查得 option。
- 一次 WLAN TX 單點測試可在不操作 CMsquares GUI 的情況下完成。
- 自動化與 CMsquares 在同一 DUT、接線與設定下，結果落在 RF 團隊核准的差異範圍。
- 每次執行有唯一 Run ID，並保存完整設定、結果、事件、錯誤與版本資訊。
- 中斷、timeout、SCPI error、解調失敗或無效值不會被記成成功。
- 長時間掃描中斷後，已完成點仍可讀取與追溯。
- 非開發者能依使用者手冊完成 golden scenario。

---

## 4. 角色與使用情境

### 4.1 角色

- 測試操作者：執行既定 profile、查看結果與報告。
- WLAN/RF 工程師：定義 PHY 設定、測試 limits 與合理性。
- 自動化開發者：維護通訊、CMP180 adapter、workflow 與 tests。
- 專案驗收者：比對 CMsquares baseline 與自動化結果。

### 4.2 核心情境

- UC-01：診斷控制電腦與 CMP180 的連線狀態。
- UC-02：探索 CMP180 韌體、options、applications 與 WLAN 能力。
- UC-03：執行單一 WLAN TX EVM 測試。
- UC-04：以 channel/frequency 進行掃描。
- UC-05：以 DUT power 或量測條件進行掃描。
- UC-06：切換 WLAN PHY/MCS/bandwidth profile。
- UC-07：將自動化結果與 CMsquares baseline 比對。
- UC-08：由既有 run 離線重製圖表與報告。

---

## 5. 開發階段

### Phase 1 — Manual Baseline & Requirements

狀態：應補齊或追認。

- 記錄 CMsquares 完整操作步驟。
- 保存至少一個可重現的 WLAN TX EVM golden scenario。
- 定義接線、DUT 控制方式、衰減、觸發及安全限制。
- 定義必須取得的 TX 結果及單位。
- 輸出 CMsquares-to-Automation mapping 初稿。

### Phase 2 — Connection Framework

狀態：目前階段。

- 建立 Python 專案與品質工具。
- 建立 config schema 與 local override。
- 建立 Transport abstraction、RsInstrument transport 與 fake transport。
- 建立 CMP180 session lifecycle。
- 完成 `*IDN?`、`*CLS`、`*OPC?`、status/error queue 共用行為。
- 提供 `doctor` 與 `discover` CLI。
- 驗證實際 VISA resource、LAN protocol、timeout 與 session locking。
- 建立 discovery report，列出已確認與未知能力。

Phase 2 完成不等於 EVM 功能完成。完成條件是連線框架在實機與 fake transport 均可診斷、可清理、可測試。

### Phase 3 — CMP180 WLAN Command Discovery

- 取得 CMP180 User Manual、Remote Control/SCPI Manual 與 WLAN application 文件。
- 研究 CMsquares 是否提供 command log、automation API、project export 或 remote interface。
- 將 GUI 步驟映射至 command/API。
- 實機逐項驗證 configure/query/execute/fetch。
- 建立帶來源與韌體版本的 command matrix。

### Phase 4 — Single Measurement MVP

- 建立 WLAN profile schema。
- 實作 setup、trigger/acquire、wait、fetch、validate。
- 保存單點結果、完整 metadata 與 log。
- 與 CMsquares golden scenario 比對。

### Phase 5 — Sweep & Analysis

- 實作 channel/frequency、power 與核准參數 sweep。
- 逐點保存、retry/skip/abort、checkpoint。
- 統計、圖表、limits 與結果摘要。

### Phase 6 — Reporting, Hardening & Release

- HTML 報告、離線重製與 artifact 索引。
- timeout、斷線、invalid result 與中止測試。
- 文件、Demo、release 與移交。

---

## 6. 功能需求

| ID | 優先級 | 需求 | 驗收方式 |
|---|---:|---|---|
| FR-001 | P0 | 由 YAML 載入 CMP180 resource、timeout 與 run 設定 | 無效設定在連線前失敗 |
| FR-002 | P0 | 開啟、鎖定及關閉儀器 session | 正常、例外、Ctrl+C 均釋放 session |
| FR-003 | P0 | 查詢並驗證 `*IDN?` | 非 CMP180 預設拒絕執行 |
| FR-004 | P0 | `doctor` 顯示環境與連線診斷 | 回傳明確 pass/fail 與修正方向 |
| FR-005 | P0 | `discover` 保存韌體、option、application 與通訊能力 | 生成結構化 discovery JSON/Markdown |
| FR-006 | P0 | 統一 command/query API | command 與 query 可被 fake transport 驗證 |
| FR-007 | P0 | 支援 `*OPC?` 或經驗證的非同步完成判斷 | timeout 不產生假成功結果 |
| FR-008 | P0 | 查詢及清空 SCPI error queue | 完整保存 code/text |
| FR-009 | P0 | command trace 可選擇性啟用 | 不記錄秘密；可重建命令順序 |
| FR-010 | P0 | 以 profile 設定 WLAN TX 分析 | 設定後 query-back 關鍵值 |
| FR-011 | P0 | 執行單點 WLAN TX EVM | 回傳結構化結果與有效性狀態 |
| FR-012 | P0 | 逐點寫入 CSV | 中途失敗不遺失已完成點 |
| FR-013 | P0 | 保存 resolved config 與 instrument metadata | 任一結果可追溯 |
| FR-014 | P1 | Channel/frequency sweep | 點數、順序、結果列一致 |
| FR-015 | P1 | Power 或 DUT level sweep | 參數來源與實際值明確 |
| FR-016 | P1 | 支援多個 WLAN profile | 主 workflow 不散落 profile-specific command |
| FR-017 | P1 | 產生 EVM 圖表與統計 | 無效點不以 0 取代 |
| FR-018 | P1 | HTML 報告與離線重製 | 不連儀器可重建相同摘要 |
| FR-019 | P1 | CMsquares baseline comparison | 顯示差值與核准 tolerance |
| FR-020 | P1 | retry/skip/abort 政策 | 每次決策有事件紀錄 |
| FR-021 | P2 | checkpoint/resume | 設定與儀器身分相符才可續跑 |
| FR-022 | P2 | 量測畫面或 constellation artifact | 可與 point_index 關聯 |

---

## 7. WLAN 測試設定需求

實際欄位應由 Phase 1/3 discovery 確認。Schema 預留：

- WLAN standard/generation：例如 802.11a/b/g/n/ac/ax/be；只啟用實機已驗證項目。
- Band 與 channel/frequency。
- Channel bandwidth。
- PHY mode、MCS、modulation、coding、spatial stream。
- PPDU/frame format 與 packet length。
- Guard interval、preamble 及其他標準特定設定。
- Expected nominal power 與 input attenuation/path loss。
- Trigger source、level、timeout。
- Capture length、measurement count、averaging。
- EVM result scope：overall、data、pilot、per stream/carrier/symbol 等。
- Limits 與 CMsquares baseline tolerance。

不可在尚未確認 CMP180/CMsquares 語意前，把同名 GUI 欄位直接視為同一 SCPI 單位或值域。

---

## 8. 建議架構

```text
CLI
 ├─ doctor
 ├─ discover
 ├─ single
 ├─ sweep
 └─ report
      │
Config Loader + Schema + Safety Validation
      │
Run Orchestrator / State Machine
      ├─ CMP180 WLAN Adapter
      │    ├─ Capability Discovery
      │    ├─ WLAN Configuration
      │    ├─ Acquisition & Synchronization
      │    └─ Result Fetch & Parsing
      │
      ├─ Instrument Session
      │    ├─ RsInstrument Transport
      │    └─ Fake/Transcript Transport
      │
      └─ Storage / Analysis / Reporting
```

### 8.1 模組責任

- `cli`：參數、exit code、簡潔結果；不直接寫 SCPI。
- `config`：schema、預設值、單位正規化、安全範圍。
- `transport`：write/query/read binary、timeout、session lock。
- `instrument`：CMP180 身分、初始化、同步、狀態及 error queue。
- `wlan`：能力 discovery、profile、量測配置與結果 parser。
- `workflows`：single/sweep/compare，不保存型號專屬命令。
- `storage`：逐點 append、metadata、events、checkpoint。
- `analysis/reporting`：統計、圖表、HTML，只讀 run artifact。

### 8.2 建議目錄

```text
src/cmp180_auto/
├─ cli.py
├─ config.py
├─ models.py
├─ exceptions.py
├─ transport/{base.py,rsinstrument.py,fake.py}
├─ instrument/{session.py,cmp180.py,discovery.py}
├─ wlan/{profile.py,commands.py,parser.py}
├─ workflows/{single.py,sweep.py,compare.py}
├─ storage/{run_store.py,csv_writer.py}
├─ analysis/{statistics.py,plots.py}
└─ reporting/html.py
```

---

## 9. Session 與狀態機

### 9.1 Run 狀態

`CREATED → VALIDATED → CONNECTING → CONNECTED → DISCOVERED → CONFIGURED → ACQUIRING → FETCHING → SAVING → COMPLETED`

例外分支：

- `RETRYING`：可恢復 timeout 或暫時性通訊失敗。
- `POINT_FAILED`：掃描中的單點失敗。
- `FAILED`：不可恢復錯誤。
- `CANCELLED`：使用者中止。

### 9.2 CMP180 session lifecycle

1. 建立 Run ID 並保存原始設定。
2. 開啟 transport。
3. 執行 `*IDN?`。
4. 驗證 CMP180 型號與可接受韌體。
5. 依核准政策執行 `*CLS`；`*RST` 是否使用須由 discovery 確認。
6. 檢查 stale error queue。
7. 執行 capability discovery 或載入已驗證 capability cache。
8. 配置、量測、fetch、保存。
9. 最後檢查 error queue。
10. finally 關閉 session；若專案控制 DUT，亦需恢復 DUT 安全狀態。

---

## 10. SCPI 與同步規範

- 設定 command 與 query 原則上分開發送。
- 關鍵設定必須 query-back，並做單位與 tolerance 比較。
- 短操作可使用 `*OPC?`；長操作使用經 CMP180 驗證的 status/SRQ/polling。
- 禁止以固定 sleep 作為唯一完成條件。
- polling 必須有 deadline、間隔與最後狀態紀錄。
- `9.91E37`、NAN、INF 或 CMP180 文件定義的 sentinel 均視為 invalid。
- binary block 依 SCPI definite block 長度解析，不依 newline 猜測。
- error queue 讀取後會消耗項目，必須先完整寫入 events/log。
- `*RST` 可能改變 application 狀態；未確認影響前不得無條件執行。
- CMsquares 與外部自動化可能爭用儀器；Phase 2 必須驗證 session locking 與共存政策。

---

## 11. Hardware Discovery 規格

### 11.1 必查資訊

- `*IDN?` 完整回應。
- CMP180 韌體、base software、CMsquares 版本。
- WLAN 相關硬體／軟體 options 與 license。
- VISA resource string 與可用 protocol（HiSLIP、VXI-11、socket 等）。
- session lock、同時 client、CMsquares 共存限制。
- reset/preset 對目前 application 與 RF routing 的影響。
- CMP180 WLAN TX application 的 remote control interface。
- measurement initiate、completion status、fetch commands。
- result unit、array ordering、invalid sentinel、limit status。
- screenshot、trace 或 result export 能力。
- DUT control 方法及是否由 CMP180/CMsquares 管理。

### 11.2 Discovery 輸出

`discover` 產生：

- `discovery.json`：機器可讀結果。
- `discovery.md`：人員審查表。
- `command-trace.log`：僅在核准時保存安全命令。
- `capabilities.json`：已確認、未支援、未知三態。

未知不得自動等同不支援；未經驗證的命令不得標為 supported。

### 11.3 Command matrix

| 功能 | GUI 步驟 | Command/API | Query-back | 回傳型別/單位 | 同步方式 | 韌體/CMsquares 版本 | 官方來源 | 實機驗證 |
|---|---|---|---|---|---|---|---|---|
| 選擇 WLAN TX application | TBD | TBD | TBD | TBD | TBD | TBD | TBD | Pending |
| 設定 channel/frequency | TBD | TBD | TBD | Hz/channel | TBD | TBD | TBD | Pending |
| 設定 bandwidth | TBD | TBD | TBD | Hz/enum | TBD | TBD | TBD | Pending |
| 設定 PHY/MCS | TBD | TBD | TBD | enum | TBD | TBD | TBD | Pending |
| 設定 input attenuation | TBD | TBD | TBD | dB | TBD | TBD | TBD | Pending |
| 開始 TX analysis | TBD | TBD | TBD | status | TBD | TBD | TBD | Pending |
| 取得 EVM | TBD | TBD | TBD | dB/% | after complete | TBD | TBD | Pending |
| 取得 TX power | TBD | TBD | TBD | dBm | after complete | TBD | TBD | Pending |
| 取得 frequency error | TBD | TBD | TBD | Hz/ppm | after complete | TBD | TBD | Pending |

---

## 12. 設定檔範例

```yaml
run:
  name: wlan_tx_evm_baseline
  operator: local_user
  output_root: output

instrument:
  model: CMP180
  resource: TCPIP::cmp180-host::hislip0
  timeout_ms: 120000
  reset_on_connect: false
  lock_session: true

wlan:
  profile: configs/profiles/golden_wlan_tx.yaml
  standard: discovery_required
  band: discovery_required
  channel: null
  frequency_hz: null
  bandwidth_hz: null
  mcs: null

measurement:
  repetitions: 3
  trigger: discovery_required
  save_artifacts: true

safety:
  max_points: 501
  max_timeout_ms: 300000
  require_verified_profile: true

error_policy:
  retries: 2
  on_point_error: retry_then_skip
```

`discovery_required` 是草稿標記；正式執行時 validator 必須拒絕此值。

---

## 13. 結果資料規格

### 13.1 Run 目錄

```text
output/<timestamp>_<name>_<run-id>/
├─ config.original.yaml
├─ config.resolved.json
├─ metadata.json
├─ discovery.json
├─ measurements.csv
├─ events.jsonl
├─ run.log
├─ summary.json
├─ plots/
├─ artifacts/
└─ report.html
```

### 13.2 CSV 最低欄位

- `run_id`, `point_index`, `attempt`, `timestamp`。
- `profile_id`, `standard`, `band`, `channel`, `frequency_hz`。
- `bandwidth_hz`, `mcs`, `expected_power_dbm`。
- `evm_value`, `evm_unit`。
- `tx_power_dbm`, `frequency_error_hz`；若未支援則為 null 並標原因。
- `measurement_status`, `limit_status`, `elapsed_ms`。
- `instrument_error_code`, `instrument_error_message`。
- `artifact_path`, `baseline_delta`。

結果欄位需區分 setpoint、query-back 與 measured value，不得用同一欄混淆。

---

## 14. CLI 與 Exit Code

```text
cmp180-auto doctor --config <file>
cmp180-auto discover --config <file>
cmp180-auto single --config <file>
cmp180-auto sweep --config <file> --axis channel
cmp180-auto compare --run <run-id> --baseline <baseline-id>
cmp180-auto report --run <run-id>
```

- `0`：成功。
- `2`：CLI/config validation error。
- `3`：連線、身分、韌體或 capability error。
- `4`：measurement error 或成功率未達門檻。
- `5`：storage/report error。
- `130`：使用者中止。

---

## 15. 錯誤政策

| 錯誤 | 預設處理 |
|---|---|
| 設定或安全驗證失敗 | 連線前終止 |
| 非 CMP180 或韌體未核准 | 終止並保存 discovery |
| CMsquares/session lock 衝突 | 不強制搶占；提示關閉或依核准共存流程 |
| 暫時性 timeout | 查狀態與 error queue，最多重試設定次數 |
| SCPI command error | 保存 code/text；預設終止該 workflow |
| 解調失敗／無封包 | 重試或標 invalid，不填 0 |
| 連線中斷 | 重連後重新 IDN 與完整 configure，再決定續跑 |
| CSV 寫入失敗 | 立即停止量測，保存 log |
| 報告失敗 | 原始 run 保留，狀態標 partial |
| Ctrl+C | 保存既有點、關閉 session、狀態 CANCELLED |

---

## 16. 測試規格

### 16.1 無硬體測試

- Config/schema 與 discovery placeholder validation。
- Fake transport 的 command/query transcript。
- Session cleanup、timeout、重試、error queue。
- 狀態機合法／非法轉移。
- WLAN 結果 parser：正常、缺欄、sentinel、單位錯誤。
- Sweep point 端點、方向、重複與最大點數。
- CSV append、checkpoint、離線報告。

### 16.2 實機測試

| ID | 測試 | 通過條件 |
|---|---|---|
| HIL-001 | CMP180 `*IDN?` | 型號與 metadata 正確 |
| HIL-002 | 連續連線/關閉 20 次 | 無 session leak/lock 殘留 |
| HIL-003 | CMsquares 開啟時連線 | 行為已記錄且不破壞現有測試 |
| HIL-004 | `*OPC?`/status 同步 | 不讀到 stale result |
| HIL-005 | error queue 注入 | code/text 完整保存 |
| HIL-006 | WLAN single golden run | 成功取得 EVM 與必要結果 |
| HIL-007 | CMsquares baseline compare | 落在核准差異範圍 |
| HIL-008 | 10 次重複量測 | repeatability 落在核准範圍 |
| HIL-009 | 中途取消 | 已完成點保留且 session 關閉 |
| HIL-010 | 短 sweep | 點數、順序、結果、報告一致 |

---

## 17. 12 週計畫

### Week 1 — CMsquares 流程盤點

- 錄製完整 WLAN TX EVM 手動操作。
- 保存設定、畫面、結果及輸出檔。
- 定義 DUT、接線、衰減、trigger 與安全條件。
- Gate：第二位操作者可依文件重現 golden scenario。

### Week 2 — CMP180 Hardware Discovery

- 盤點 IDN、韌體、options、CMsquares、LAN 與 VISA resource。
- 取得所有必要官方手冊。
- 確認 CMsquares automation/command log/export 能力。
- Gate：完成 discovery report 與未知項目 owner。

### Week 3 — Connection Framework

- 建立 repository、Python 3.11、依賴、lint/type/test。
- 建立 transport abstraction、RsInstrument 與 fake transport。
- Gate：fake contract tests 與實機 `doctor` 通過。

### Week 4 — Session、同步與錯誤

- 建立 CMP180 session lifecycle、lock、IDN、CLS、OPC、error queue。
- 驗證 CMsquares 共存與 reset 政策。
- Gate：HIL-001～HIL-005 通過。

### Week 5 — WLAN Command Matrix

- 將 GUI 操作映射至 command/API。
- 逐項驗證 set/query-back/initiate/fetch。
- Gate：golden scenario 所需命令無 TBD。

### Week 6 — Single Measurement MVP

- 實作 WLAN profile、single workflow、parser、CSV/metadata。
- Gate：HIL-006 成功，錯誤不被記為正常結果。

### Week 7 — Baseline Comparison

- 對齊 CMsquares 與自動化設定、結果名稱與單位。
- 執行 repeatability 與 delta 分析。
- Gate：RF 工程師核准 tolerance，HIL-007/008 通過。

### Week 8 — Channel/Frequency Sweep

- 實作逐點落盤、retry/skip、圖表。
- Gate：HIL-009/010 通過。

### Week 9 — Power/MCS/Profile Expansion

- 依需求加入第二 sweep axis 與多 profile。
- Gate：profile 差異不污染通用 workflow。

### Week 10 — Reporting & Diagnostics

- HTML、離線重製、doctor 強化與 command trace。
- Gate：由 run artifact 可重建相同 summary。

### Week 11 — Hardening & User Test

- 故障注入、斷線、timeout、invalid、儲存失敗。
- 非開發者依 README 執行 golden scenario。
- Gate：P0 bug 為 0。

### Week 12 — Release & Demo

- clean install、完整回歸、release tag、限制、移交。
- 10–15 分鐘 Demo 與備用既有 run。
- Gate：交付與驗收矩陣簽核。

---

## 18. 最終交付物

- Python package 與 CLI。
- CMP180 connection/discovery framework。
- 經實機驗證的 WLAN command matrix。
- WLAN TX single 與 sweep workflows。
- CMsquares baseline 與 comparison report。
- CSV/JSON/events/log/plots/HTML artifacts。
- Fake/contract/unit/HIL tests。
- README、使用者手冊、開發者手冊與故障排除。
- Demo script、release notes、已知限制。

### Definition of Done

- 程式、schema、tests 與文件同步完成。
- 實機命令具有官方來源或明確實機驗證紀錄。
- 正常與失敗 cleanup 均通過測試。
- 結果具設定、儀器、版本及時間追溯資訊。
- 不含未處理 P0/P1 review issue。

---

## 19. 主要風險

| 風險 | 影響 | 因應 |
|---|---|---|
| CMP180 WLAN remote API 尚未確認 | 無法進入量測 MVP | Phase 2/3 優先取得手冊與實機 trace |
| CMsquares 封裝私有流程 | GUI 無法直接一對一轉 SCPI | 調查官方 automation interface，保留 adapter 邊界 |
| Option/license 不足 | WLAN 功能不可用 | Week 2 discovery，未確認前不承諾支援 |
| CMsquares 與 script 爭用 session | 測試中斷或狀態污染 | 驗證 locking；明定互斥/共存 SOP |
| GUI 與遠端預設值不同 | EVM 結果不一致 | 保存 resolved config、query-back、逐欄比對 |
| EVM 單位或結果 scope 混淆 | 錯誤判定 | data dictionary；overall/data/pilot 不混欄 |
| DUT 控制方法未知 | 無法穩定產生封包 | Phase 1 定義 DUT owner、trigger 與等待條件 |
| 自動化中斷造成資料損失 | 長測試需重跑 | 逐點 append、checkpoint、原始 artifact 不覆寫 |

---

## 20. 目前立即行動

1. 確認 CMP180 的 `*IDN?`、韌體、options、CMsquares 版本與 VISA resource。
2. 提供或取得 CMP180 Remote Control/SCPI Manual 與 WLAN/CMsquares automation 文件。
3. 保存一個完整 CMsquares WLAN TX EVM golden scenario：所有設定、DUT 條件、結果與畫面。
4. 建立 Phase 2 repository skeleton，先完成 fake transport、session、`doctor` 與 `discover`。
5. 在 command matrix 的 golden scenario 所需項目全部脫離 TBD 後，再開始實作 EVM workflow。
