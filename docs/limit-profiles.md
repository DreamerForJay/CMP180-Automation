# Limit Profile 規格

## 中文版本

### 目的與能力邊界

Limit Profile 將量測值、限制值、版本與判定結果綁定，讓 CSV、JSON、Metadata、HTML
與 GUI 可追溯同一組規則。目前 `configs/limits.example.yaml` 是軟體開發範例，生命週期
為 `draft`，不是公司、IEEE 或 Wi-Fi Alliance 核准規範，也不得用來宣稱 DUT
compliance。

### Profile 欄位

- `profile_id`：穩定識別碼。
- `revision`：規則版本；數值變更必須更新。
- `lifecycle`：只能是 `draft` 或 `approved`。
- `description`：適用標準、頻寬、MCS、模式及限制來源。
- `maximum_evm_db`：EVM 上限；量測值必須小於或等於此值。
- `maximum_absolute_frequency_error_hz`：Frequency Error 絕對值上限。
- `maximum_absolute_power_error_db`：量測功率相對 expected power 的絕對誤差上限。

### 判定規則

任何必要值為 `INV`、缺失、NaN 或無限值時，整點為 `INVALID`，不得轉為零或 Pass。
每個指標分別保存 PASS／FAIL 與 margin。Draft profile 的總結果只能是
`DRAFT_PASS`／`DRAFT_FAIL`；只有經正式核准且 `lifecycle: approved` 的 profile 才能輸出
未加前綴的 PASS／FAIL。Workflow 是否正常、SCPI 是否無錯誤與 RF 是否安全關閉仍是獨立
狀態，不得與 RF compliance 混為一談。

### 正式核准前的工作

RF／測試負責人需依 DUT 類型、802.11 模式、頻寬、MCS、測試方法、path loss、校正狀態
與公司規範確認數值，記錄來源與簽核者，新增不可變 revision，經 review 後才改為
`approved`。目前 GUI 顯示 Draft 警示，Artifacts 保存 profile snapshot 與
`compliance_claim=false`。

---

## English Version

### Purpose and capability boundary

A Limit Profile binds measured values, limits, version, and decisions so CSV, JSON,
Metadata, HTML, and the GUI can trace the same rule set. `configs/limits.example.yaml`
is currently a software-development example with lifecycle `draft`. It is not an
approved company, IEEE, or Wi-Fi Alliance specification and cannot support a DUT
compliance claim.

### Profile fields

- `profile_id`: stable identifier.
- `revision`: rule revision; change it whenever a value changes.
- `lifecycle`: either `draft` or `approved`.
- `description`: applicable standard, bandwidth, MCS, mode, and limit source.
- `maximum_evm_db`: maximum EVM; the measurement must be at or below it.
- `maximum_absolute_frequency_error_hz`: maximum absolute Frequency Error.
- `maximum_absolute_power_error_db`: maximum absolute measured-to-expected power error.

### Decision rules

If any required value is `INV`, missing, NaN, or infinite, the point is `INVALID`; it
must never be converted to zero or Pass. Each metric retains PASS/FAIL and margin. A
draft profile can produce only `DRAFT_PASS` or `DRAFT_FAIL`. Only a formally approved
profile with `lifecycle: approved` may produce unprefixed PASS/FAIL. Workflow health,
SCPI errors, and safe final RF state remain separate from RF compliance.

### Work required before formal approval

The RF/test owner must confirm values against DUT type, 802.11 mode, bandwidth, MCS,
test method, path loss, calibration state, and company rules; record the source and
approver; create an immutable revision; and complete review before setting `approved`.
The current GUI shows a Draft warning, while artifacts save the profile snapshot and
`compliance_claim=false`.
