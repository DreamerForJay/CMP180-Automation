# CMP180 WLAN Loopback Test SOP

## 中文版

本 SOP 記錄已驗證的 RF1.1 到 RF1.5 WLAN 自發自收流程，並區分 CMsquares 人工操作與 Python 已實作功能。

### 1. 工具分工

| 工具 | 用途 | 是否啟動 RF／量測 |
|---|---|---|
| PowerShell 網路命令 | 確認乙太網路與 TCP | 否 |
| `cmp180_evm test-connection` | 讀取身分、選配與錯誤佇列 | 否 |
| `cmp180_wlan_discover.py` | 唯讀 WLAN 設定與狀態 | 否 |
| Chrome 操作 CMsquares | 設定並人工啟停儀器 | 按下 Run／Start 時會 |
| `cmp180_wlan_result_discover.py` | 讀取並解析上一筆結果 | 否 |

早期驗證由 CMsquares 啟動後再以 Python `FETCh` 讀取；目前 Python 已完成固定安全 profile 的完整 SingleShot。`cmp180_wlan_result_discover.py` 仍只讀取上一筆結果，不會啟動新量測。

### 2. 前置條件與測試前檢查

- CMP180 與 CMsquares 已啟動。
- 控制電腦乙太網路位於 `192.168.200.0/24` 且沒有 IP 衝突。
- CMP180 為 `192.168.200.50`，TCP 5025 可連線。
- RF1.1 以已知 50 Ω 同軸線連接 RF1.5；若加入衰減器必須先記錄。

```powershell
Test-NetConnection 192.168.200.50 -Port 5025
python -m cmp180_evm validate-config configs\instrument.example.yaml
python -m cmp180_evm test-connection `
  --instrument-config configs\instrument.example.yaml
python scripts\cmp180_wlan_discover.py
```

只有在 TCP 成功、儀器為 CMP serial REDACTED、錯誤佇列為空，而且 Generator 與 WLAN TX 量測皆 Off 時才能繼續。

### 3. 已驗證的 CMsquares 設定

GPRF Gen 1：RF1.1 only、ARB、6105 MHz、−40 dBm、External Attenuation 0 dB。波形為 `KV352_lib8_WLAN_11be_EHT_MU_BW320-1_4xLTF_GI32_MCS11_LEN4096_LDPC.wv`；RF1.2 到 RF1.8 不得啟用。

WLAN TX Meas 1：802.11be、SISO、320 MHz、RF1.5、6 GHz／Channel 31／6105 MHz、External Attenuation 0 dB、Expected Nominal Power −20 dBm、User Margin 3 dB、SingleShot、Statistic Count 10。

第一次將 Expected Nominal Power 設為 −40 dBm 時出現 `Input Overdriven`。不可提高 Generator 功率來修正；成功測試保持 −40 dBm，只把 Analyzer Expected Nominal Power 改為 −20 dBm以增加量程。

### 4. 人工執行順序

1. 確認 Generator 與 WLAN TX 量測皆 Off。
2. 開啟 `GPRF Gen 1` 並確認 Run。
3. 只啟動一次 `WLAN TX Meas 1`。
4. 等待 `Ready`，不要重複按 Start。
5. 遇到 Overdriven、逾時或錯誤時，立即停止量測並關閉 Generator。
6. 完成後關閉 Generator並目視確認 Off。

### 5. 使用 Python 讀取結果

確認 RF 已關閉後執行：

```powershell
python scripts\cmp180_wlan_result_discover.py
```

成功條件：狀態為 `RDY`、五組查詢皆為 `PASS` 與 `0,"No error"`、每組含 28 個 OFDM SISO 欄位。已驗證平均值為 EVM −36.14424 dB、Burst Power −40.56650 dBm、Frequency Error −6.496213 Hz；這些是開發參考值，不是量產限制。

### 6. 異常處理與結束檢查

- `Input Overdriven`：停止 RF，不提高輸出功率，檢查 RF1.1 only、RF1.5 Analyzer 與量程。
- 結果查詢失敗：確認量測已完成且為 `RDY`，檢查 `SYST:ERR?`，不可把 `FETCh` 換成會啟動量測的 `READ`。
- 離開前確認 Generator Off、量測非 Run、錯誤佇列已檢查、線材／衰減已記錄、結果已保存、文件已更新。

---

## 8. Generator 同值 setter 驗證（RF Off）

此步驟只驗證 frequency 與 level setter。工具先讀取目前值，確認 RF state 為 `OFF`，再將完全相同的值寫回並 read-back。它不包含 RF On 或量測啟動命令。

```powershell
python scripts\cmp180_generator_discover.py
python scripts\cmp180_generator_setter_validate.py --confirm-same-value-write
```

只有在第一個命令顯示 `state 'OFF'` 時才可執行第二個命令。預期 frequency 與 power 均為 `PASS`、error queue 為 `0,"No error"`，最後 RF state 必須仍為 `OFF`。任何不一致或錯誤都必須停止，不可接著嘗試 RF On。

## 9. WLAN Analyzer 同值 setter 驗證

此步驟只在 Generator 為 `OFF`，且 WLAN measurement 為 `OFF` 或 `RDY` 時執行。工具會依序寫回目前的 RF path、bandwidth、frequency、external attenuation 與 expected power；每項都執行 `*OPC?`、`SYST:ERR?` 與 read-back。

```powershell
python scripts\cmp180_wlan_discover.py
python scripts\cmp180_analyzer_setter_validate.py --confirm-same-value-write
```

`RDY` 表示量測已完成並處於 ready/idle 狀態。工具仍會拒絕 `RUN`、`ADJ`、`INV` 或其他狀態。此工具沒有 RF On 或 `INITiate` 指令。

## 10. Measurement lifecycle 驗證

此工具會啟動 Analyzer lifecycle，但 Generator RF 必須為 `OFF`。它依序執行 `INITiate → STOP` 與 `INITiate → ABORt`，每一步都查詢 state 與 error queue。

```powershell
python scripts\cmp180_measurement_lifecycle_validate.py --confirm-analyzer-lifecycle
```

正常結果為 `RUN → RDY` 及 `RUN → OFF`，最後 Generator 與 measurement 都必須 `OFF`。這不是有效 EVM 量測，因為 Generator 沒有開啟 RF。

## 11. RF On/Off pulse 驗證（需現場確認）

此步驟會真的輸出極短時間 RF，不能遠端或無人執行。操作員必須確認 RF1.1 → RF1.5 cable、目前功率不高於 -40 dBm、Analyzer 非 RUN，並留在儀器旁。

```powershell
python scripts\cmp180_rf_state_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present
```

工具先讀取並驗證安全條件，才送出 RF On；不啟動 WLAN measurement。RF Off 放在 `finally`，因此 RF On 後任何錯誤都會嘗試關閉。實機首次執行前仍須由操作員在當次對話重新確認接線與人在現場。

## 12. 固定三點頻率掃描 HIL（需逐次現場確認）

此入口固定為 RF1.1 → RF1.5、6085／6105／6125 MHz、320 MHz、-40 dBm、expected power -20 dBm。執行前先重跑連線與 query-only discovery，確認 Generator `OFF`、measurement `OFF` 或 `RDY`、error queue empty；再確認單一 cable 直連且操作員仍在現場。

```powershell
python scripts\cmp180_frequency_sweep_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present `
  --confirm-three-point-sweep
```

每點應輸出 EVM、burst power 與 frequency error。最後必須顯示 RF `OFF`、measurement `OFF` 或 `RDY`、error queue `[]`。只要任一條件不符就停止，不得接著執行 Web 實機掃頻。完整／部分結果皆保存在 `output`；完整限制與 artifacts 說明見 [安全短掃描規格](sweep-safety.md)。

## 13. 固定五點功率掃描 HIL（需逐次現場確認）

此入口固定 6105 MHz、320 MHz、expected power -20 dBm，依序從 -60 dBm 提高至 -40 dBm。執行前重新確認 Generator `OFF`、measurement `OFF` 或 `RDY`、error queue empty，以及 RF1.1 → RF1.5 單一 cable 直連、無衰減器、操作員在現場。

```powershell
python scripts\cmp180_power_sweep_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present `
  --confirm-five-point-power-sweep
```

若低功率點無法觸發或任何 cleanup／error queue 異常，工具會停止後續點並保存 partial artifacts，不會自行提高功率或變更 expected power。結束時必須顯示 RF `OFF`、measurement `OFF` 或 `RDY`、error queue `[]`。

## English Version

This SOP records the verified RF1.1-to-RF1.5 WLAN loopback workflow. It separates CMsquares actions from operations already supported by Python.

## 1. Tool responsibilities

| Tool | Purpose | Starts RF or measurement? |
|---|---|---|
| PowerShell network commands | Verify Ethernet and TCP reachability | No |
| `cmp180_evm test-connection` | Read identity, options and error queue | No |
| `cmp180_wlan_discover.py` | Read WLAN configuration/state with SCPI | No |
| Chrome controlling CMsquares | Configure and manually start/stop the instrument | Yes, when Run/Start is clicked |
| `cmp180_wlan_result_discover.py` | Fetch and parse the previous stored result | No |

The verified measurement was started in CMsquares. Python then read the stored result with `FETCh`. Python does not yet perform the entire measurement cycle.

## 2. Prerequisites

- CMP180 and CMsquares are running.
- Controller Ethernet is in `192.168.200.0/24` without a duplicate address.
- CMP180 is `192.168.200.50`; TCP 5025 is reachable.
- The Python 3.11 virtual environment and dependencies are installed.
- RF1.1 is connected to RF1.5 with a known 50-ohm coaxial cable.
- Record any inserted attenuator before changing level compensation.

## 3. Preflight

From the repository root:

```powershell
Test-NetConnection 192.168.200.50 -Port 5025
python -m cmp180_evm validate-config configs\instrument.example.yaml
python -m cmp180_evm test-connection `
  --instrument-config configs\instrument.example.yaml
python scripts\cmp180_wlan_discover.py
```

Proceed only when TCP succeeds, the device is CMP serial REDACTED, the error queue is empty, and Generator and WLAN TX measurement are Off.

## 4. Verified CMsquares setup

### GPRF Gen 1

| Parameter | Value |
|---|---|
| Routing | RF1.1 only |
| Baseband mode | ARB |
| Waveform | `KV352_lib8_WLAN_11be_EHT_MU_BW320-1_4xLTF_GI32_MCS11_LEN4096_LDPC.wv` |
| Frequency | 6105 MHz |
| Level (RMS) | -40 dBm |
| External attenuation | 0 dB for the verified direct cable |

Confirm RF1.2 through RF1.8 are not enabled as generator outputs.

### WLAN TX Meas 1

| Parameter | Value |
|---|---|
| Standard / receive mode | 802.11be / SISO |
| Bandwidth | 320 MHz |
| Connection | RF1.5 |
| Band / center | 6 GHz / channel 31 / 6105 MHz |
| External attenuation | 0 dB for the verified direct cable |
| Expected nominal power | -20 dBm |
| User margin | 3 dB |
| Repetition / statistics | SingleShot / 10 |

The first trial with expected nominal power at -40 dBm reported `Input Overdriven`. Do not increase generator power to fix this. The successful trial kept generator power at -40 dBm and set analyzer expected nominal power to -20 dBm for additional range.

## 5. Manual execution

1. Confirm Generator and WLAN TX measurement show Off.
2. Turn on `GPRF Gen 1`; verify Run.
3. Start `WLAN TX Meas 1` once.
4. Wait for `Ready`; do not repeatedly click Start.
5. On overdrive, timeout or error, stop measurement and Generator immediately.
6. After `Ready`, turn off Generator and visually confirm Off.

## 6. Read the stored result with Python

With RF already Off:

```powershell
python scripts\cmp180_wlan_result_discover.py
```

Success criteria:

- State is `RDY`.
- Five aggregate queries report `PASS` and `0,"No error"`.
- Each response contains 28 OFDM SISO fields.

Verified average development reference:

| Result | Value |
|---|---:|
| EVM, all carriers | -36.14424 dB |
| Burst power | -40.56650 dBm |
| Frequency error | -6.496213 Hz |

These are development references, not production limits.

## 7. Troubleshooting

### TCP uses Wi-Fi instead of Ethernet

Check `InterfaceAlias` and `SourceAddress`. The verified controller address was `192.168.200.12/24`.

### Input Overdriven

- Stop measurement and RF output.
- Do not raise generator power.
- Confirm only RF1.1 is selected for Generator output and Analyzer uses RF1.5.
- Confirm expected nominal power and user margin provide sufficient range.
- Add a known attenuator before testing higher generator levels.

### Result query fails

- Confirm a measurement previously completed and state is `RDY`.
- Run query-only discovery and inspect `SYST:ERR?`.
- Do not replace `FETCh` with `READ`; `READ` starts a new measurement.

## 8. End-of-test checklist

- [ ] Generator is Off
- [ ] WLAN TX measurement is not Run
- [ ] SCPI error queue checked
- [ ] Cable/attenuator recorded
- [ ] Raw and normalized results saved
- [ ] Relevant documentation updated

## 9. Generator same-value setter validation (RF Off)

This step only validates the frequency and level setters. The tool reads the current values, requires RF state `OFF`, writes the exact same values back, and reads them back. It contains no RF-On or measurement-initiation command.

```powershell
python scripts\cmp180_generator_discover.py
python scripts\cmp180_generator_setter_validate.py --confirm-same-value-write
```

Run the second command only when the first command reports `state 'OFF'`. Frequency and power must both report `PASS`, the error queue must return `0,"No error"`, and final RF state must remain `OFF`. Stop on any mismatch or error; do not proceed to RF On.

## 10. WLAN Analyzer same-value setter validation

Run this step only when Generator is `OFF` and WLAN measurement is `OFF` or `RDY`. The tool writes back the current RF path, bandwidth, frequency, external attenuation, and expected power in sequence. Every item uses `*OPC?`, `SYST:ERR?`, and read-back verification.

```powershell
python scripts\cmp180_wlan_discover.py
python scripts\cmp180_analyzer_setter_validate.py --confirm-same-value-write
```

`RDY` means the previous measurement is complete and the instance is ready/idle. The tool still rejects `RUN`, `ADJ`, `INV`, and every other state. It contains no RF-On or `INITiate` command.

## 11. Measurement lifecycle validation

This tool starts the Analyzer lifecycle while requiring Generator RF `OFF`. It runs `INITiate → STOP` followed by `INITiate → ABORt`, querying state and the error queue after every step.

```powershell
python scripts\cmp180_measurement_lifecycle_validate.py --confirm-analyzer-lifecycle
```

Expected transitions are `RUN → RDY` and `RUN → OFF`; final Generator and measurement states must both be `OFF`. This is not a valid EVM measurement because Generator RF remains disabled.

## 12. RF On/Off pulse validation (on-site confirmation required)

This step produces a real, very brief RF output and must not run remotely or unattended. The operator must confirm the RF1.1-to-RF1.5 cable, current power no higher than -40 dBm, Analyzer not running, and physical presence beside the instrument.

```powershell
python scripts\cmp180_rf_state_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present
```

The tool reads and validates every safety condition before RF On and does not initiate a WLAN measurement. RF Off is in `finally`, so any failure after the RF-On attempt still triggers an Off attempt. The operator must reconfirm cabling and physical presence in the current session before the first hardware execution.

## 13. Fixed three-point frequency-sweep HIL (per-run on-site confirmation required)

This entry point is fixed to RF1.1 to RF1.5, 6085/6105/6125 MHz, 320 MHz, -40 dBm, and -20 dBm expected power. Before execution, rerun the connection and query-only discovery checks. Confirm Generator `OFF`, measurement `OFF` or `RDY`, an empty error queue, the single direct cable, and that the operator remains on site.

```powershell
python scripts\cmp180_frequency_sweep_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present `
  --confirm-three-point-sweep
```

Every point should print EVM, burst power, and frequency error. The final line must show RF `OFF`, measurement `OFF` or `RDY`, and error queue `[]`. Stop if any condition differs; do not proceed to a Web hardware sweep. Complete and partial results are saved under `output`. See the [safe short-sweep specification](sweep-safety.md) for the full limits and artifact behavior.

## 14. Fixed five-point power-sweep HIL (per-run on-site confirmation required)

This entry point is fixed to 6105 MHz, 320 MHz, -20 dBm expected power, and increases from -60 dBm to -40 dBm. Before execution, reconfirm Generator `OFF`, measurement `OFF` or `RDY`, an empty error queue, the single direct RF1.1-to-RF1.5 cable, no attenuator, and operator presence.

```powershell
python scripts\cmp180_power_sweep_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present `
  --confirm-five-point-power-sweep
```

If a low-power point cannot trigger, or any cleanup/error-queue error occurs, the tool stops and preserves partial artifacts. It never raises power or changes expected power automatically. The final line must show RF `OFF`, measurement `OFF` or `RDY`, and error queue `[]`.
