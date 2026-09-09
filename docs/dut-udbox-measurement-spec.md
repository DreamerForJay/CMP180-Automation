# DUT／UDBox 量測功能實作規格

## 1. 目的與交付邊界

本規格供後續 Agent 實作 CMP180 WLAN TX EVM 的 DUT／UDBox 量測功能。新的目標很單純：讓操作員能選擇 DUT／UDBox 連線方式、輸入必要量測條件、執行一次或少量重複的 WLAN TX EVM 量測，並取得可閱讀、可下載的結果 artifact。

本功能不是 DUT compliance 驗證系統，也不是 Path Loss 校正追溯系統。不要為了這個需求新增 route approval、Calibration Profile approval、Limit Profile approval、Go／No-Go 驗證頁、或 LOOPBACK_READY 類型的 profile 升級流程。

量測結果只代表「本次儀器在此設定下讀到的數值」。若未來要做正式規範判定，應另開需求，不要混在這個最小量測功能內。

## 2. 一天內 MVP 範圍

一天內只做能交付使用的最小量測路徑：

1. 新增 DUT／UDBox 量測 request model，欄位保持簡單。
2. 新增 Web「DUT／UDBox 量測」頁或既有頁面入口。
3. 支援 Mock 量測與實機量測兩種模式。
4. 實機模式只執行受限 SingleShot 或少量 repeats，不做 sweep。
5. 儲存 JSON／CSV／HTML artifact，讓操作員能看 EVM、Power、Frequency Error、validity 與 raw response。
6. 量測前顯示人工確認摘要，量測後保證停止量測並 RF Off。
7. 更新必要文件與測試，不新增大型驗證框架。

## 3. 操作員輸入欄位

只要求量測必要欄位：

- DUT 名稱或編號：自由文字，方便 artifact 辨識。
- UDBox path 或 port：自由文字或下拉選單，先不要求自動 readback。
- CMP180 Analyzer port：例如 `RF1.5`。
- WLAN frequency：Hz 或 MHz，但 artifact 必須保存標準化 Hz。
- Bandwidth：20／40／80／160／320 MHz。
- Standard／MCS：沿用既有 SingleShot 支援欄位。
- Expected input power：dBm，用於提醒操作員，不做正式校正判定。
- Repeats：預設 1，上限建議 10。
- Operator note：自由文字，記錄接線或 DUT 狀態。

不要強制要求 calibration profile、route asset、接線照片、owner approval 或 DUT firmware。這些可以當 optional metadata 保存，但缺少時不可阻止量測。

## 4. 基本安全限制

雖然不做驗證系統，仍必須保留 RF 安全下限：

- 不得 Reset 儀器或 Workspace。
- DUT／UDBox 量測時，CMP180 Generator 預設必須保持 `OFF`。
- RF workflow 必須使用 `try/finally`，錯誤、逾時、取消與成功都要嘗試 STOP／ABORT measurement 並 RF Off。
- 若使用者輸入的 expected input power 高於專案設定的 analyzer soft limit，必須阻止執行並要求操作員降低輸入或確認衰減。
- 第一版不要自動控制 DUT TX 或 UDBox switch；若沒有可靠 adapter，就以「請操作員手動啟動／停止 DUT TX」處理。
- artifact 必須保存最終 RF state、measurement state 與 SCPI error queue。

這些限制是為了避免傷儀器，不是為了建立合規驗證流程。

## 5. 建議資料模型

```yaml
measurement_id: dut-udbox-example
mode: dut_udbox_measurement
instrument:
  resource: 192.168.200.50:5025
  analyzer_port: RF1.5
dut:
  label: null
  note: null
udbox:
  enabled: true
  path_label: null
measurement:
  standard: WLAN
  frequency_hz: null
  bandwidth_hz: null
  mcs: null
  expected_input_dbm: null
  repeats: 1
operator:
  name: null
  note: null
output:
  save_json: true
  save_csv: true
  save_html: true
```

`expected_input_dbm` 只做安全提示與上限檢查；不要把它當作 Path Loss 或 DUT output 校正依據。

## 6. 量測流程

```text
IDLE -> PRECHECK -> WAIT_OPERATOR -> MEASURING -> CLEANUP -> DONE
                    |                |             |
                    +-> CANCELLED     +-> FAILED    +-> CLEANUP_FAILED
```

- `PRECHECK`：檢查必填欄位、repeats 上限、expected input power 上限、CMP180 連線與 Generator Off。
- `WAIT_OPERATOR`：顯示人工確認，提醒接線、UDBox path、DUT TX 狀態與 emergency stop。
- `MEASURING`：啟動 Analyzer SingleShot，讀取 raw response，轉成既有 28-field 結果。
- `CLEANUP`：STOP／ABORT measurement、RF Off、查詢 error queue。
- `DONE`：建立 artifact，狀態標示 `MEASURED`，不顯示 compliance PASS／FAIL。

若任何 repeat 出現 `INV`、timeout 或 SCPI error，停止後續 repeat，進入 cleanup，artifact 保存已取得的 partial result。

## 7. API 與 Web 要求

建議新增或調整：

- `POST /api/jobs/hardware/dut-udbox-measurement`：建立量測 job。
- `GET /api/jobs/{id}`：查詢狀態、目前 repeat、最新結果與 cleanup 狀態。
- `POST /api/jobs/{id}/cancel`：取消 job，進入 cleanup。

Web 畫面只需要呈現：

- 量測設定表單。
- 人工確認摘要。
- job 進度、目前 repeat、validity 與主要量測值。
- artifact 連結。
- 錯誤與 cleanup 狀態。

中英切換已改為全頁檢查計畫跟著語言切換；本功能新增文字依目前專案規則使用繁體中文即可。

## 8. Artifact 最低內容

每次量測建立獨立 run directory，至少保存：

- request snapshot。
- DUT label、UDBox path、operator note。
- frequency、bandwidth、MCS、expected input power、repeats。
- 每次 repeat 的 raw instrument response。
- normalized 28-field result。
- validity、error message、partial result。
- final RF state、measurement state、SCPI error queue。
- cleanup status。
- `measurement_claim: MEASURED`。
- `compliance_claim: false`。

HTML report 應清楚顯示「這是量測結果，不是正式驗證或認證判定」。

## 9. 測試與驗收

測試只覆蓋最小量測功能：

- 缺少必填欄位時不可建立 job。
- repeats 預設 1，且不得超過上限。
- expected input power 超過 soft limit 時阻止執行。
- Generator 非 OFF 時阻止執行。
- Mock 量測能產生 JSON／CSV／HTML artifact。
- `INV`、timeout、cancel 都會停止後續 repeat 並進入 cleanup。
- cleanup failure 會標示 `CLEANUP_FAILED`。
- Web 語言切換不重新送出 RF job。

不需要 Path Loss HIL、DUT HIL、UDBox HIL 三階段 gate；也不需要 profile approval 或 LOOPBACK_READY 類型升級。

## 10. 交給下一個 Agent 的執行指令

請先讀 `AGENTS.md`、`SPEC.MD`、`docs/development-workflow.md` 與本規格。任務是建立 DUT／UDBox「量測」功能，不是驗證系統。請不要新增 route approval、Path Loss approval、Limit Profile approval、Go／No-Go preview 或合規 PASS／FAIL 判定。

請沿用既有 SingleShot、job、artifact、Web static 架構完成最小功能：操作員輸入 DUT label、UDBox path、Analyzer port、frequency、bandwidth、MCS、expected input power 與 repeats 後，可以在 Mock 或實機模式產生 `MEASURED` artifact。所有 RF 路徑必須保留 `try/finally` cleanup、STOP／ABORT、RF Off 與 error queue 記錄。完成後執行必要單元測試、相關 YAML validation、JavaScript syntax check 與 `git diff --check`，並清楚標示使用 Mock、stored result 或新的 live RF。
