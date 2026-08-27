# 下一次 CMP180 實機驗收批次

## 中文版

### 目標

下一次取得機台時，不再零散驗證單一按鍵。一次批次收集「已安裝能力、可用 WLAN 波形、RF 路由、設定回讀、有效解調範圍與安全清理」證據，據此擴大 Web 的核准 Profile。型錄能力不是執行授權；只有已安裝選件、應用支援、路徑校正與 HIL 證據共同成立的組合，才能在 Web 開放 RF。

### 預先準備（不占用機台）

1. 準備線材、轉接頭、衰減器與功率計識別碼及校正有效期。
2. 決定要驗證的 WLAN standard、bandwidth、waveform/MCS、RF route 與功率區間。
3. 先在 Mock 執行所有計畫，確認點數、預估時間、輸出路徑及中止流程。
4. 預先建立驗收表；每個案例必須保存設定、raw response、normalized result、error queue、最終 measurement state 與 RF state。

### 90 分鐘現場批次

| 階段 | 時間 | RF | 工作 | 通過條件 |
|---|---:|---|---|---|
| A. 能力快照 | 10 分 | Off | IDN、options、RF port catalog、WLAN application、bandwidth/waveform/trigger catalog | 查詢成功、error queue empty |
| B. 設定回讀 | 15 分 | Off | 逐組寫入後 query routing、frequency、bandwidth、waveform、trigger、ranging 與 expected power | 寫入值與回讀一致；不送 RF |
| C. 參考點 | 15 分 | 最低安全功率 | 每個候選組合先跑一個中心頻率 SingleShot | 非 `INV`、關鍵欄位有限值、cleanup 完整 |
| D. 邊界點 | 20 分 | 低功率 | 每組只跑最低／中心／最高頻率與最低／最高核准功率 | 無 overdrive；失敗案例正確保存且停止 |
| E. 短掃描 | 20 分 | 低功率 | 通過 C、D 的組合執行最多 11 點掃描 | 每點有效或遇首個異常停止；artifacts 完整 |
| F. 稽核 | 10 分 | Off | 比對 artifacts、error queue、RF Off 與量測狀態 | RF Off、無未處理錯誤、證據可追溯 |

### 停止條件

遇到 `INV`、Input Overdriven、trigger timeout、SCPI error、讀回值不一致、接線／衰減變更、供電異常或 RF 狀態不明時，立即停止該批；執行 STOP／ABORt、RF Off 並保存 partial artifacts。不得為了跑完矩陣而忽略失敗。

### 擴大 Web 範圍的規則

1. Catalog：只描述 CMP180 型錄上限。
2. Installed：由機台 options 與 query catalog 取得。
3. Approved：由 RF 負責人依路徑、線損、輸入保護與公司 SOP 核准。
4. HIL verified：只有通過上述現場案例的組合。

Web 應顯示 Installed 範圍供選擇，但只有 Approved 且 HIL verified 的組合可執行 RF；其餘組合可建立計畫並顯示缺少的驗證，不得假裝已支援。這樣才能逐步接近 CMP180 的實際已安裝能力，同時避免把 400 MHz–8 GHz 或最高 500 MHz 分析頻寬誤當成所有 WLAN waveform 都可直接使用。

### 現有批次入口

- `scripts/cmp180_frequency_sweep_wide_validate.py`：11 點、200 MHz 頻率掃描候選案例。
- `scripts/cmp180_power_sweep_dense_validate.py`：10 點、2 dB 步進功率掃描候選案例。

這兩個入口目前是待現場驗收的候選案例，不是新的通過證據；執行前仍需閱讀 `docs/hardware-test-sop.md` 並提供腳本要求的所有確認旗標。

---

## English Version

### Objective

The next instrument session must collect installed-capability, WLAN waveform, RF-route, setting-readback, valid-demodulation-range, and deterministic-cleanup evidence as one campaign instead of testing isolated buttons. The Web approved profile is expanded only from that evidence. Catalog capability is not execution authorization. RF is exposed only when the installed option, application support, calibrated route, and HIL evidence all agree.

### Preparation before instrument access

1. Record cable, adapter, attenuator, and power-meter identifiers and calibration validity.
2. Define the WLAN standards, bandwidths, waveform/MCS combinations, RF routes, and power ranges to validate.
3. Run every plan in Mock first and verify point counts, duration, output paths, and cancellation.
4. Prepare an acceptance table. Every case must retain settings, raw responses, normalized results, the error queue, final measurement state, and final RF state.

### Ninety-minute on-site campaign

| Phase | Time | RF | Work | Pass condition |
|---|---:|---|---|---|
| A. Capability snapshot | 10 min | Off | IDN, options, RF-port catalog, WLAN application, bandwidth/waveform/trigger catalogs | Queries succeed and error queue is empty |
| B. Setting readback | 15 min | Off | Write then query routing, frequency, bandwidth, waveform, trigger, ranging, and expected power | Readback matches; no RF |
| C. Reference point | 15 min | Lowest safe power | One center-frequency SingleShot per candidate combination | Not `INV`, finite critical fields, complete cleanup |
| D. Boundary points | 20 min | Low power | Minimum/center/maximum frequency and minimum/maximum approved power | No overdrive; failures are retained and stop correctly |
| E. Short sweep | 20 min | Low power | Up to 11 points for combinations that passed C and D | Every point is valid or the first anomaly stops the run; artifacts are complete |
| F. Audit | 10 min | Off | Review artifacts, error queue, RF Off, and measurement state | RF Off, no unhandled error, traceable evidence |

### Stop conditions

Stop the campaign on `INV`, input overdrive, trigger timeout, SCPI error, readback mismatch, cabling/attenuation changes, power instability, or unknown RF state. Execute STOP/ABORt and RF Off and preserve partial artifacts. Never ignore a failure just to complete the matrix.

### Rules for expanding the Web range

1. Catalog describes only the CMP180 catalog limits.
2. Installed comes from instrument options and query catalogs.
3. Approved is authorized by the RF owner using route, path loss, input protection, and company SOP data.
4. HIL verified contains only combinations that passed the on-site campaign.

The Web may display the Installed range for planning, but RF execution is enabled only for combinations that are both Approved and HIL verified. Other combinations may be planned with a clear missing-evidence message. This allows measured expansion toward the instrument's installed capability without incorrectly treating 400 MHz–8 GHz or up-to-500 MHz analysis bandwidth as universally valid for every WLAN waveform.

### Existing campaign entry points

- `scripts/cmp180_frequency_sweep_wide_validate.py`: candidate 11-point, 200 MHz frequency campaign.
- `scripts/cmp180_power_sweep_dense_validate.py`: candidate 10-point, 2 dB power campaign.

These are candidates awaiting on-site acceptance, not new passing evidence. Read `docs/hardware-test-sop.md` and supply every confirmation flag required by the scripts before execution.
