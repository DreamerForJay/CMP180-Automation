# CMP180 實機量測範例與結果判讀 / Hardware Measurement Example and Result Interpretation

## 中文版本

### 1. 目前可執行的實機範例

目前已驗證的是 CMP180 自打自收 loopback，不是 DUT 測試：

```text
GPRF Generator RF1.1 ──單條 RF cable──> WLAN TX Analyzer RF1.5
Frequency:              6105 MHz
Waveform bandwidth:     320 MHz
Generator RMS level:    -40 dBm
Analyzer expected power:-20 dBm
External attenuation:   0 dB
Waveform:               802.11be EHT MU, MCS11, 4xLTF, GI 3.2 us
```

訊號方向是 RF1.1 輸出、RF1.5 接收。沒有 DUT 時，不可把結果解讀成產品性能；此 loopback 用來驗證儀器、SCPI、trigger、parser、cleanup 與軟體資料流。

### 2. GUI 操作

使用硬體模式啟動：

```powershell
python -m cmp180_evm.web --enable-hardware
```

開啟 `http://127.0.0.1:8765`，進入「實機單點」：

1. 目視確認 RF1.1 → RF1.5 cable。
2. 在接線選單選擇 `RF1.1 → RF1.5（已驗證）`。
3. 勾選「我人在 CMP180 旁並能觀察儀器」。
4. 按「執行實機 SingleShot」。
5. 執行期間不要拔除 RF cable、關閉 CMP180 或在 CMsquares 修改同一 measurement instance。
6. 完成後確認結果頁顯示 `HARDWARE`／`simulated=false`，並確認 RF 最終為 Off。

### 3. 已驗證的正確輸出範例

兩筆完整 Python 實機量測範例：

| 來源 | EVM All | Burst Power | Frequency Error | 最終狀態 |
|---|---:|---:|---:|---|
| CLI SingleShot | -36.23029 dB | -40.47938 dBm | -16.30075 Hz | RF Off / Meas RDY |
| Web GUI HIL | -36.51843 dB | -40.18850 dBm | 6.986657 Hz | RF Off / Meas RDY |

合理檢查不是要求每次數字完全相同，而是：

- `simulated=false`。
- EVM、power 與 frequency error 為有效數字，不是 `INV`、`NAN` 或空值。
- Burst Power 接近設定的 -40 dBm；小幅差異是量測與路徑造成。
- 流程到達 `RDY`，instrument error 與 cleanup error 為空。
- 最終 RF state 為 `OFF`。
- CSV、JSON、Metadata、Raw SCPI 與 HTML Report 按鈕都能開啟。

### 3.1 已保存的統計種類

CSV／JSON 現在保存全部 5 組已驗證統計查詢，不只 average：`evm_all_carriers_db` 等欄位沿用無前綴命名代表 average（向後相容既有欄位），另外加前綴保存 `current_*`（目前值）、`min_*`（最小值）、`max_*`（最大值）、`stddev_*`（標準差）。對應的 raw SCPI 回應也各自存成 `raw/modulation_{average,current,minimum,maximum,std_dev}.txt`。

### 4. 主要欄位意義

| 欄位 | 意義 | 單位／方向 |
|---|---|---|
| EVM All | 所有有效子載波的調變誤差向量幅度 | dB；通常越負越好 |
| EVM Data | Data subcarriers 的 EVM | dB；越負越好 |
| EVM Pilot | Pilot subcarriers 的 EVM | dB；越負越好 |
| Burst Power | 封包 burst 的平均量測功率 | dBm；應接近預期輸入功率 |
| Peak Power | burst 內峰值功率 | dBm；用於 crest／overdrive 檢查 |
| Frequency Error | 接收訊號相對分析器中心頻率的偏差 | Hz；絕對值越小通常越好 |
| Clock Error | OFDM symbol clock 偏差 | ppm；絕對值越小通常越好 |
| IQ Offset | I/Q DC offset 表現 | dB；判讀依標準與 DUT 規格 |
| Gain Imbalance | I 與 Q 增益不平衡 | dB；絕對值越小通常越好 |
| Quadrature Error | I/Q 正交角誤差 | degree；絕對值越小通常越好 |
| Reliability | CMP180 對 demodulation/result 的可靠性指標 | 必須依內建 Help 定義判讀 |
| valid | parser 與儀器結果是否有效 | `true/false`；無效值不可當 0 |
| simulated | 是否為 Mock 資料 | 實機結果必須為 `false` |

### 5. Pass／Fail 限制

目前 GUI 不應以 -32 dB 或其他任意數字判定 DUT Pass／Fail。正式 limits 必須由以下資訊共同決定：

1. IEEE 802.11 對應 standard、PPDU type、MCS 與 bandwidth 的規範。
2. 公司產品規格與 guard band。
3. DUT operating mode、channel、power、chain、temperature 與校正條件。
4. Cable/path loss、external attenuation 與量測不確定度。
5. 測試封包數、統計方式及 worst/average 判定規則。

目前 loopback 結果的 `PASS` 只能代表流程健康或示範 threshold，不代表 DUT compliance。正式 GUI 會把「Workflow PASS」與「RF Limit PASS」分開顯示。

### 6. 使用者異常操作與警示

GUI 不再提供獨立的 fault injection 頁面。警示直接整合到正常操作流程：接線空白、未驗證自訂接線、操作員未在場、重複送出，以及伺服器未啟用硬體模式時，頁面會顯示紅色警示並禁止 RF 輸出。

接線欄位是可輸入的建議選單。使用者可選擇 `RF1.1-RF1.5`，也可輸入其他路徑供後續設定；目前只有已完成 routing、功率與 cleanup 實機驗證的 `RF1.1-RF1.5` 可以解鎖量測。這個限制避免自訂文字與實際 SCPI routing 不一致。

---

## English Version

### 1. Currently supported hardware example

The verified setup is a CMP180 self-loopback, not a DUT test:

```text
GPRF Generator RF1.1 ──single RF cable──> WLAN TX Analyzer RF1.5
Frequency:              6105 MHz
Waveform bandwidth:     320 MHz
Generator RMS level:    -40 dBm
Analyzer expected power:-20 dBm
External attenuation:   0 dB
Waveform:               802.11be EHT MU, MCS11, 4xLTF, GI 3.2 us
```

Signal direction is RF1.1 output to RF1.5 input. Without a DUT, the result must not be interpreted as product performance. This loopback validates the instrument, SCPI, trigger, parser, cleanup, and software data flow.

### 2. GUI operation

Start hardware mode:

```powershell
python -m cmp180_evm.web --enable-hardware
```

Open `http://127.0.0.1:8765` and select Hardware Single:

1. Visually confirm the RF1.1-to-RF1.5 cable.
2. Select `RF1.1 → RF1.5 (Verified)` from the routing list.
3. Select the operator-present checkbox.
4. Select Run Hardware SingleShot.
5. During execution, do not remove the RF cable, power off the CMP180, or edit the same measurement instance in CMsquares.
6. After completion, confirm `HARDWARE`/`simulated=false` and final RF Off.

### 3. Verified correct-output examples

Two complete Python hardware measurements are available:

| Source | EVM All | Burst Power | Frequency Error | Final state |
|---|---:|---:|---:|---|
| CLI SingleShot | -36.23029 dB | -40.47938 dBm | -16.30075 Hz | RF Off / Meas RDY |
| Web GUI HIL | -36.51843 dB | -40.18850 dBm | 6.986657 Hz | RF Off / Meas RDY |

A reasonable check does not require identical numbers on every run. Instead verify:

- `simulated=false`.
- EVM, power, and frequency error are numeric rather than `INV`, `NAN`, or empty.
- Burst Power is close to the configured -40 dBm; small differences are expected from measurement and path effects.
- The workflow reaches `RDY`, with empty instrument and cleanup error lists.
- Final RF state is `OFF`.
- CSV, JSON, Metadata, Raw SCPI, and HTML Report buttons open successfully.

### 3.1 Saved statistics

CSV/JSON now save all 5 verified statistic queries, not just average: fields such as `evm_all_carriers_db` keep the unprefixed name for average (backward compatible), plus prefixed `current_*`, `min_*`, `max_*`, and `stddev_*` variants. The matching raw SCPI responses are saved as `raw/modulation_{average,current,minimum,maximum,std_dev}.txt`.

### 4. Main field meanings

| Field | Meaning | Unit/direction |
|---|---|---|
| EVM All | Modulation error-vector magnitude across valid subcarriers | dB; more negative is generally better |
| EVM Data | EVM of data subcarriers | dB; more negative is better |
| EVM Pilot | EVM of pilot subcarriers | dB; more negative is better |
| Burst Power | Average measured packet-burst power | dBm; should be near expected input power |
| Peak Power | Peak power within the burst | dBm; used for crest/overdrive checks |
| Frequency Error | Offset from Analyzer center frequency | Hz; smaller absolute value is generally better |
| Clock Error | OFDM symbol-clock offset | ppm; smaller absolute value is generally better |
| IQ Offset | I/Q DC-offset performance | dB; evaluate against standard and DUT requirements |
| Gain Imbalance | I/Q gain mismatch | dB; smaller absolute value is generally better |
| Quadrature Error | I/Q orthogonality error | degree; smaller absolute value is generally better |
| Reliability | CMP180 demodulation/result reliability indicator | Interpret using built-in Help definition |
| valid | Whether instrument output and parsing are valid | `true/false`; invalid must never become numeric zero |
| simulated | Whether data came from Mock | Hardware data must be `false` |

### 5. Pass/fail limits

The GUI must not classify DUT compliance using an arbitrary -32 dB or similar threshold. Formal limits require all of the following:

1. Applicable IEEE 802.11 standard, PPDU type, MCS, and bandwidth requirements.
2. Company product specification and guard band.
3. DUT operating mode, channel, power, chain, temperature, and calibration conditions.
4. Cable/path loss, external attenuation, and measurement uncertainty.
5. Packet count, statistical method, and worst/average decision rule.

Current loopback `PASS` can only indicate workflow health or a demonstration threshold, not DUT compliance. The final GUI will separate Workflow PASS from RF Limit PASS.

### 6. Abnormal user actions and warnings

The GUI no longer exposes a separate fault-injection screen. Warnings are integrated into the normal workflow. An empty route, an unverified custom route, missing operator presence, duplicate submission, or a server without hardware mode shows a red warning and blocks RF output.

The cable field is an editable suggestion list. Users can select `RF1.1-RF1.5` or type another route for future configuration. Only `RF1.1-RF1.5`, whose routing, power, and cleanup behavior have been hardware-verified, can currently unlock a measurement. This prevents custom text from disagreeing with the actual SCPI routing.
