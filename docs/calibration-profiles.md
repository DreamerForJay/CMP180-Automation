# Path Loss／Calibration Profile 規格

## 中文版本

### 目的

Calibration Profile 保存指定 RF 路徑在不同頻率的實測插入損耗，讓報告可追溯
Generator 設定功率與 Analyzer 預期輸入功率之間的關係。被動路徑的 `loss_db` 使用正值，
計算式為 `expected_analyzer_input_dbm = source_power_dbm - loss_db`。

### 狀態與安全規則

- `draft`：可載入、驗證及預覽，但不得套用於正式量測。
- `approved`：只有在尚未過期、頻率落在校正範圍且路由相符時才可供量測使用。
- 至少需要兩個頻率點；頻率必須嚴格遞增且不得重複。
- `loss_db` 目前硬限制為 0–30 dB。
- 範圍內使用線性內插；禁止外插，避免未量測頻段被當成有效校正。
- `configs/calibration.example.yaml` 的 0 dB 是開發用 Draft 佔位值，不是校正證書。

### 操作

```powershell
python -m cmp180_evm validate-calibration configs\calibration.example.yaml
```

正式 Profile 應另建不含機密的 YAML，填入 profile ID、revision、路由、校正與到期日、
線材／轉接頭或校正設備參考編號，以及實測頻率／線損點。資料須由 RF／測試負責人審核後，
才能將 lifecycle 改為 `approved`。每次量測須在 metadata 保存完整 Profile snapshot；
不得只保存檔名，以免日後檔案內容改變而失去追溯性。

### 尚未解除的閘門

目前已完成資料模型、YAML 載入、驗證、內插、到期與核准閘門；尚未把 Draft 範例套入
實機 SCPI workflow。下一步是在取得真實線損後，核對路由並把 Approved snapshot 寫入
每個 CSV／JSON／metadata／HTML 報告。未取得核准資料前，既有固定 HIL profile 仍維持原設定。

---

## English Version

### Purpose

A Calibration Profile stores measured insertion loss versus frequency for a specific RF
route. It makes the relationship between Generator source power and expected Analyzer input
traceable. Passive-path `loss_db` is positive and the calculation is
`expected_analyzer_input_dbm = source_power_dbm - loss_db`.

### Lifecycle and safety rules

- `draft`: may be loaded, validated, and previewed, but cannot be applied to a formal run.
- `approved`: usable only while current and when frequency and route are covered.
- At least two strictly increasing, unique frequency points are required.
- `loss_db` is hard-bounded to 0–30 dB.
- In-range values use linear interpolation; extrapolation is blocked.
- The zero-loss values in `configs/calibration.example.yaml` are draft placeholders, not a
  calibration certificate.

### Operation

```powershell
python -m cmp180_evm validate-calibration configs\calibration.example.yaml
```

A production profile must be stored in a separate non-sensitive YAML and include its ID,
revision, route, calibration/expiry dates, cable/adapter or calibration-equipment reference,
and measured frequency/loss points. The RF/test owner must review it before lifecycle changes
to `approved`. Each run must preserve a complete profile snapshot in metadata rather than
only a filename, so later file edits cannot break traceability.

### Remaining gate

The data model, YAML loading, validation, interpolation, expiry check, and approval gate are
implemented. The draft example is not connected to the live SCPI workflow. After real loss
data is available, the next integration will verify route matching and write the approved
snapshot into CSV/JSON/metadata/HTML artifacts. Existing fixed HIL profiles remain unchanged
until approved data exists.
