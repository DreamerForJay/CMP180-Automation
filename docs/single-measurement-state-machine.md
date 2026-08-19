# 安全單次量測狀態機／Safe Single-Measurement State Machine

## 中文版

### 目的

`src/cmp180_evm/workflow/single_measurement.py` 是 Issue #1 的第一個安全核心。它不包含任何尚未驗證的 SCPI，也不會自行連接 CMP180；它只規定完整量測必須依照固定階段執行，並在所有結束路徑嘗試停止量測與關閉 RF。

### 階段

```text
VALIDATING → CONFIGURING → RF_ON → MEASURING → FETCHING
                                            ↓
                              CLEANING_UP → COMPLETE
```

### 目前的安全檢查

- 操作者必須明確確認實機 RF 測試。
- Generator 與 Analyzer 不可使用同一個 RF port。
- 頻率與頻寬必須大於零。
- Generator power 不可超過測試計畫允許上限；目前 loopback 參考上限為 −30 dBm，已驗證點為 −40 dBm。

### 清理保證

- `rf_on()` 一旦被嘗試，`finally` 就會嘗試 `rf_off()`。
- `initiate_single()` 一旦被嘗試，`finally` 就會嘗試 `stop_measurement()`。
- Stop 失敗不會阻止後續 RF Off。
- 成功、Fetch 失敗、錯誤佇列失敗、逾時或未來取消流程都使用同一清理路徑。

### 目前限制與下一步

Transport-independent workflow、Mock tests 與真實 CMP180 backend 均已完成；固定 loopback profile 的 setters、RF On／Off、INIT／STOP／ABORT、Fetch 與 cleanup 已通過實機驗證。尚未驗證的其他 profile 或指令仍必須在 command map 保持 `null`。

後續順序：

1. 完成 3 點低功率 frequency sweep HIL。
2. 加入正式 limit profile、path-loss 與 calibration metadata。
3. 加入取消、進度、partial results 與稽核紀錄。

### 2026-08-18 內建 Help 探索更新

已從 CMP180 內建 Help 確認下列命令樹；目前只把查詢形式接到唯讀探索工具，尚未讓 Python 寫入設定或開啟 RF。

| 功能 | 內建 Help 命令 |
|---|---|
| Generator 頻率 | `SOURce:GPRF:GEN<i>:RFSettings:FREQuency` |
| Generator RMS/base level | `SOURce:GPRF:GEN<i>:RFSettings:LEVel` |
| Generator peak power 查詢 | `SOURce:GPRF:GEN<i>:RFSettings:PEPower?` |
| Generator RF 狀態 | `SOURce:GPRF:GEN<i>:STATe` |
| Generator RF path | `ROUTe:GPRF:GEN<i>:SPATh` |
| 啟動 WLAN 量測 | `INITiate:WLAN:MEAS<i>:MEValuation` |
| 停止 WLAN 量測 | `STOP:WLAN:MEAS<i>:MEValuation` |
| 中止 WLAN 量測 | `ABORt:WLAN:MEAS<i>:MEValuation` |

`scripts/cmp180_generator_discover.py` 只執行帶 `?` 的查詢，且每次查詢後讀取 `SYST:ERR?`。2026-08-18 實機驗證結果為 6105 MHz、-40 dBm、RF `OFF`、path `"RF1.1-RF1.8"`，所有查詢均為 `0,"No error"`。它不會送出 setter、`INITiate`、`STOP`、`ABORt` 或 RF On/Off。

## English Version

### Purpose

`src/cmp180_evm/workflow/single_measurement.py` is the first safety core for Issue #1. It contains no unverified SCPI and does not connect to the CMP180 by itself. It defines the required measurement phases and attempts measurement stop plus RF off on every exit path.

### Phases

```text
VALIDATING → CONFIGURING → RF_ON → MEASURING → FETCHING
                                            ↓
                              CLEANING_UP → COMPLETE
```

### Current safety checks

- The operator must explicitly confirm a live RF test.
- Generator and analyzer ports must differ.
- Frequency and bandwidth must be positive.
- Generator power may not exceed the plan limit. The current loopback reference limit is −30 dBm and the verified point is −40 dBm.

### Cleanup guarantees

- Once `rf_on()` is attempted, `finally` attempts `rf_off()`.
- Once `initiate_single()` is attempted, `finally` attempts `stop_measurement()`.
- A stop failure does not prevent RF off.
- Success, fetch failure, error-queue failure, timeout, and future cancellation use the same cleanup path.

### Current limitation and next step

Only the transport-independent workflow and mock tests exist. The real CMP180 SCPI backend is intentionally absent because generator/analyzer writes, RF on/off, and INIT/STOP commands still require built-in Help or controlled hardware verification. They remain `null` in the command map until verified.

Next sequence:

1. Confirm current RF and measurement state queries read-only.
2. Obtain generator routing, frequency, power, and RF on/off commands from built-in Help.
3. Verify each low-risk setter with an immediate `SYST:ERR?` check.
4. Verify WLAN analyzer setters and the SingleShot lifecycle.
5. Implement the SCPI backend and hardware-marked tests before exposing it through CLI or GUI.

### 2026-08-18 built-in Help discovery update

The CMP180 built-in Help confirms the command trees below. Only their query forms are connected to the read-only discovery tool; Python still cannot write settings or enable RF.

| Capability | Built-in Help command |
|---|---|
| Generator frequency | `SOURce:GPRF:GEN<i>:RFSettings:FREQuency` |
| Generator RMS/base level | `SOURce:GPRF:GEN<i>:RFSettings:LEVel` |
| Generator peak power query | `SOURce:GPRF:GEN<i>:RFSettings:PEPower?` |
| Generator RF state | `SOURce:GPRF:GEN<i>:STATe` |
| Generator RF path | `ROUTe:GPRF:GEN<i>:SPATh` |
| Start WLAN measurement | `INITiate:WLAN:MEAS<i>:MEValuation` |
| Stop WLAN measurement | `STOP:WLAN:MEAS<i>:MEValuation` |
| Abort WLAN measurement | `ABORt:WLAN:MEAS<i>:MEValuation` |

`scripts/cmp180_generator_discover.py` sends only queries ending in `?` and reads `SYST:ERR?` after each one. Hardware verification on 2026-08-18 returned 6105 MHz, -40 dBm, RF `OFF`, path `"RF1.1-RF1.8"`, and `0,"No error"` for every query. It never sends a setter, `INITiate`, `STOP`, `ABORt`, or RF On/Off.
