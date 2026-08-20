# CMP180 WLAN SCPI 指令矩陣 / SCPI Command Matrix

## 中文版本：Generator 唯讀探索

CMP180 內建 Help 與受控實機測試已確認 Generator 的 frequency、level、RF state、RF path，以及 WLAN Analyzer setters、measurement lifecycle 與結果查詢。固定低功率 profile 的 RF On／Off 與完整 SingleShot 已通過；未驗證的其他命令仍保持 `null`。

執行方式：

```powershell
python scripts\cmp180_generator_discover.py
```

| 功能 | 唯讀查詢 | 目前狀態 |
|---|---|---|
| 頻率 | `SOURce:GPRF:GEN:RFSettings:FREQuency?` | 已驗證：`6.105000E+09` Hz |
| RMS/base level | `SOURce:GPRF:GEN:RFSettings:LEVel?` | 已驗證：`-4.000000E+01` dBm |
| Peak power | `SOURce:GPRF:GEN:RFSettings:PEPower?` | 已驗證：RF Off 時為 `INV` |
| RF state | `SOURce:GPRF:GEN:STATe?` | 已驗證：`OFF` |
| 所有 RF states | `SOURce:GPRF:GEN:STATe:ALL?` | 已驗證：`OFF,ADJ` |
| RF path | `ROUTe:GPRF:GEN:SPATh?` | 已驗證：`"RF1.1-RF1.8"` |

### Generator setter

| 功能 | 指令模板 | 驗證方式 | 狀態 |
|---|---|---|---|
| 設定頻率 | `SOURce:GPRF:GEN:RFSettings:FREQuency {frequency_hz}` | RF Off、同值寫回、`*OPC?`、`SYST:ERR?`、read-back | 2026-08-19 實機驗證：6105 MHz |
| 設定 RMS/base level | `SOURce:GPRF:GEN:RFSettings:LEVel {power_dbm}` | RF Off、同值寫回、`*OPC?`、`SYST:ERR?`、read-back | 2026-08-19 實機驗證：-40 dBm |
| RF On/Off | `SOURce:GPRF:GEN:STATe ON/OFF` | -40 dBm、人工確認線材、finally 強制 Off | 2026-08-19 實機驗證：`ON → OFF` |

### WLAN Analyzer setter

2026-08-19 在 Generator `OFF`、measurement `RDY` 下完成同值寫回驗證：

| 功能 | 指令模板 | 實機結果 |
|---|---|---|
| RF path | `ROUTe:WLAN:MEAS:SPATh {rf_path}` | `"RF1.5"`，通過 |
| Bandwidth | `CONFigure:WLAN:MEAS:ISIGnal:BWIDth {bandwidth}` | `BW32`（320 MHz），通過 |
| Center frequency | `CONFigure:WLAN:MEAS:RFSettings:FREQuency {frequency_hz}` | 6105 MHz，通過 |
| External attenuation | `CONFigure:WLAN:MEAS:RFSettings:EATTenuation {external_attenuation_db}` | 0 dB，通過 |
| Expected nominal power | `CONFigure:WLAN:MEAS:RFSettings:ENPower {expected_power_dbm}` | -20 dBm，通過 |

所有項目均 read-back 一致並回傳 `0,"No error"`；最後 Generator `OFF`、measurement `RDY`。

## English version: Generator read-only discovery

CMP180 built-in Help and controlled hardware tests confirm Generator frequency, level, RF state, and RF path, together with WLAN Analyzer setters, measurement lifecycle, and result queries. RF On/Off and a complete fixed low-power SingleShot have passed; other unverified commands remain `null`.

Run:

```powershell
python scripts\cmp180_generator_discover.py
```

| Capability | Read-only query | Current status |
|---|---|---|
| Frequency | `SOURce:GPRF:GEN:RFSettings:FREQuency?` | Verified: `6.105000E+09` Hz |
| RMS/base level | `SOURce:GPRF:GEN:RFSettings:LEVel?` | Verified: `-4.000000E+01` dBm |
| Peak power | `SOURce:GPRF:GEN:RFSettings:PEPower?` | Verified: `INV` while RF is off |
| RF state | `SOURce:GPRF:GEN:STATe?` | Verified: `OFF` |
| All RF states | `SOURce:GPRF:GEN:STATe:ALL?` | Verified: `OFF,ADJ` |
| RF path | `ROUTe:GPRF:GEN:SPATh?` | Verified: `"RF1.1-RF1.8"` |

### Generator setters

| Capability | Command template | Validation method | Status |
|---|---|---|---|
| Set frequency | `SOURce:GPRF:GEN:RFSettings:FREQuency {frequency_hz}` | RF off, same-value write, `*OPC?`, `SYST:ERR?`, read-back | Hardware verified 2026-08-19: 6105 MHz |
| Set RMS/base level | `SOURce:GPRF:GEN:RFSettings:LEVel {power_dbm}` | RF off, same-value write, `*OPC?`, `SYST:ERR?`, read-back | Hardware verified 2026-08-19: -40 dBm |
| RF On/Off | `SOURce:GPRF:GEN:STATe ON/OFF` | -40 dBm, operator-confirmed cable, forced Off in finally | Hardware verified 2026-08-19: `ON → OFF` |

### WLAN Analyzer setters

Same-value hardware validation completed on 2026-08-19 with Generator `OFF` and measurement `RDY`:

| Capability | Command template | Hardware result |
|---|---|---|
| RF path | `ROUTe:WLAN:MEAS:SPATh {rf_path}` | `"RF1.5"`, passed |
| Bandwidth | `CONFigure:WLAN:MEAS:ISIGnal:BWIDth {bandwidth}` | `BW32` (320 MHz), passed |
| Center frequency | `CONFigure:WLAN:MEAS:RFSettings:FREQuency {frequency_hz}` | 6105 MHz, passed |
| External attenuation | `CONFigure:WLAN:MEAS:RFSettings:EATTenuation {external_attenuation_db}` | 0 dB, passed |
| Expected nominal power | `CONFigure:WLAN:MEAS:RFSettings:ENPower {expected_power_dbm}` | -20 dBm, passed |

Every value matched its read-back and returned `0,"No error"`; final states were Generator `OFF` and measurement `RDY`.

## Existing WLAN command reference

Status: 19 WLAN configuration/state queries verified; result/write discovery in progress
Instrument software: BASE `6.0.50.23`, WLAN `6.0.50.14`  
Source: CMP180 built-in WLAN and base-software help

`<i>` is the measurement instance; omitted suffix means instance 1. `<antenna>`
and `<stream>` similarly default to 1 where supported. Short forms in implementation
must be checked against the long-form command documented here.

## Configuration

| Capability | Official command | Unit/values | Current GUI value | Hardware query |
|---|---|---|---|---|
| WLAN standard | `CONFigure:WLAN:MEAS<i>:ISIGnal:STANdard` | 802.11 family enum | 802.11be | Verified: `EHT` |
| Bandwidth | `CONFigure:WLAN:MEAS<i>:ISIGnal:BWIDth` | Hz/bandwidth enum | 20 MHz | Verified: `BW20` |
| Available RF paths | `CATalog:WLAN:MEAS<i>:SPATh<stream>?` | path list | RF1/RF2 groups | Verified: RF1.1–8, RF2.1–8 |
| RF path | `ROUTe:WLAN:MEAS<i>:SPATh` | path | RF1 5 | Verified: `"RF1.5"` |
| RF path count | `ROUTe:WLAN:MEAS<i>:SPATh:COUNt?` | integer | SISO | Verified: `1` |
| External attenuation | `CONFigure:WLAN:MEAS<i>:RFSettings:EATTenuation<antenna>` | dB; negative means gain | 0 dB | Verified: `0.0` |
| Expected nominal power | `CONFigure:WLAN:MEAS<i>:RFSettings:ENPower<antenna>` | dBm | 0 dBm | Verified: `0.0` |
| Band | `CONFigure:WLAN:MEAS<i>:RFSettings:FREQuency:BAND` | band enum | 5 GHz | Verified: `B5GH` |
| Center frequency | `CONFigure:WLAN:MEAS<i>:RFSettings:FREQuency` | Hz | 5.18 GHz | Verified: `5.18E9` |
| Channel list | `CONFigure:WLAN:MEAS<i>:RFSettings:FREQuency:CHANnels` | channel(s) | 36 | Verified: `36` |
| Channel item | `CONFigure:WLAN:MEAS<i>:RFSettings:FREQuency:CHANnels<Ch>` | channel | 36 | Pending |

Notes:

- 802.11ax requires CMP-KM351; confirmed installed.
- 802.11be requires CMP-KM352; confirmed installed.
- 320 MHz requires CMP-K185; confirmed installed.
- External attenuation corrects displayed power and affects maximum configurable
  input power.
- Reference level equals expected nominal power plus user margin.

## Trigger

| Capability | Official command | Current GUI value | Hardware query |
|---|---|---|---|
| Available sources | `TRIGger:WLAN:MEAS<i>:MEValuation:CATalog:SOURce?` | 11 sources returned | Verified |
| Source | `TRIGger:WLAN:MEAS<i>:MEValuation:SOURce` | IF Power | Verified: `"IF Power"` |
| Threshold | `TRIGger:WLAN:MEAS<i>:MEValuation:THReshold` | -30 dB | Verified: `-30.0` |
| Offset | `TRIGger:WLAN:MEAS<i>:MEValuation:OFFSet` | 0 us | Verified: `0.0 s` |
| IF Power minimum gap | `TRIGger:WLAN:MEAS<i>:MEValuation:MGAP` | 5 us | Verified: `5.0E-6 s` |
| Slope | `TRIGger:WLAN:MEAS<i>:MEValuation:SLOPe` | RisingEdge | Verified: `REDG` |
| Timeout | `TRIGger:WLAN:MEAS<i>:MEValuation:TOUT` | 1000 ms | Verified: `1.0 s` |

## Measurement lifecycle

| Capability | Official command | Notes | Hardware query |
|---|---|---|---|
| Start | `INITiate:WLAN:MEAS<i>:MEValuation` | Starts configured measurement | Not executed |
| Pause/stop | `STOP:WLAN:MEAS<i>:MEValuation` | Stops without abort semantics | Verified 2026-08-19: `RUN -> RDY` |
| Abort | `ABORt:WLAN:MEAS<i>:MEValuation` | Abort workflow | Verified 2026-08-19: `RUN -> OFF` |
| State | `FETCh:WLAN:MEAS<i>:MEValuation:STATe?` | Expected `RDY` after READ | Verified idle: `OFF` |
| All states | `FETCh:WLAN:MEAS<i>:MEValuation:STATe:ALL?` | Detailed status | Verified idle: `OFF,ADJ,INV` |

`INITiate` was verified twice with Generator RF off: `INITiate -> STOP` and
`INITiate -> ABORt` both returned `0,"No error"`. `FETCh...` returns the previous
result without initiating a new measurement.

## OFDM SISO scalar results

Primary query:

```text
FETCh:WLAN:MEAS<i>:MEValuation:MODulation:CURRent?
FETCh:WLAN:MEAS<i>:MEValuation:MODulation:AVERage?
FETCh:WLAN:MEAS<i>:MEValuation:MODulation:MINimum?
FETCh:WLAN:MEAS<i>:MEValuation:MODulation:MAXimum?
FETCh:WLAN:MEAS<i>:MEValuation:MODulation:SDEViation?
```

Hardware verification on 2026-08-18: the abbreviated `CURR`, `AVER`, `MIN`,
`MAX` and `SDEV` forms all returned 28 fields and `0,"No error"` from CMP180
serial REDACTED after the controlled RF loopback SingleShot.

`READ...` variants initiate a single measurement before returning data. `CALCulate...`
variants return limit-check results rather than measured values.

| Index | Field | Type/unit |
|---:|---|---|
| 1 | Reliability | decimal indicator |
| 2 | OutOfTol | % |
| 3 | MCSIndex | integer |
| 4 | Modulation | enum |
| 5 | PayloadSym | symbols |
| 6 | MeasuredSym | symbols |
| 7 | PayloadBytes | bytes |
| 8 | GuardInterval | enum |
| 9 | NoSS | integer |
| 10 | NoSTS | integer |
| 11 | BurstRate | % |
| 12 | PowerBackoff | dB |
| 13 | BurstPower | dBm |
| 14 | PeakPower | dBm |
| 15 | CrestFactor | dB |
| 16 | EVMAllCarr | dB |
| 17 | EVMDataCarr | dB |
| 18 | EVMPilotCarr | dB |
| 19 | FreqError | Hz |
| 20 | ClockError | ppm |
| 21 | IQOffset | dB |
| 22 | DCPower | dBm |
| 23 | GainImbalance | dB |
| 24 | QuadError | degree |
| 25 | LTFPower | dBm |
| 26 | DataPower | dBm |
| 27 | PreamblePower | dBm |
| 28 | CommonPhaseError | degree |

Support notes from built-in help:

- Field 28 was added in V6.0.50 and is expected on the current WLAN/base software.
- Timing Error requires a suitable external timing trigger; IF Power cannot provide
  expected timing for this result.
- IEEE test guidance shown by the instrument requires at least 20 PPDUs, each with
  at least 16 data OFDM symbols.

## Useful trace queries from the official example

```text
FETCh:WLAN:MEAS:MEValuation:TRACe:EVMagnitude:SYMBol:AVERage?
FETCh:WLAN:MEAS:MEValuation:TRACe:EVMagnitude:CARRier:AVERage?
FETCh:WLAN:MEAS:MEValuation:TRACe:IQConst:INPHase?
FETCh:WLAN:MEAS:MEValuation:TRACe:IQConst:QUADrature?
FETCh:WLAN:MEAS:MEValuation:TRACe:TSMask:AVERage?
FETCh:WLAN:MEAS:MEValuation:TRACe:TSMask:FREQuency?
FETCh:WLAN:MEAS:MEValuation:TRACe:PVTime:AVERage?
FETCh:WLAN:MEAS:MEValuation:TRACe:PVTime:TIME?
```

These are P1 visualization/reporting queries. The first MVP uses scalar results.

## 中文：完整 SingleShot 驗證

2026-08-19 完成第一筆完整 Python 實機 SingleShot。流程依序設定已驗證參數、RF On、`INITiate`、等待 `RDY`、`FETCh` 28 欄 average result、`STOP` 與 RF Off。EVM All 為 -36.23029 dB、Burst Power -40.47938 dBm、Frequency Error -16.30075 Hz；instrument／cleanup errors 均為空。獨立查詢確認最終 RF `OFF`、measurement `RDY`。

**2026-08-20 更新**：`workflow/cmp180_single_backend.py` 的 `fetch_result()` 改為依序查詢全部 5 組已驗證統計（`CURRent`／`AVERage`／`MINimum`／`MAXimum`／`SDEViation`），而不只是 average。5 個查詢個別都已如上驗證過，不需要新的 SCPI 驗證；但「一次 SingleShot 內連續查詢並保存全部 5 組」這個組合行為，**尚未在真實硬體上重新確認**，目前只有 mock/unit test 覆蓋。下一次實機 HIL 時應一併確認這 5 組查詢都能在同一次 SingleShot 內正常回應且不影響既有 average 結果與 cleanup 行為。

## English: complete SingleShot verification

The first complete Python hardware SingleShot passed on 2026-08-19. It configured the verified profile, enabled RF, sent `INITiate`, waited for `RDY`, fetched the 28-field average result, sent `STOP`, and disabled RF. EVM All was -36.23029 dB, Burst Power -40.47938 dBm, and Frequency Error -16.30075 Hz; instrument and cleanup error lists were empty. Independent queries confirmed final RF `OFF` and measurement `RDY`.

**2026-08-20 update**: `workflow/cmp180_single_backend.py`'s `fetch_result()` now queries all 5 verified statistics (`CURRent`/`AVERage`/`MINimum`/`MAXimum`/`SDEViation`) instead of only average. Each query was already individually verified above, so no new SCPI verification is required; however, fetching and saving all 5 in a row within one SingleShot has **not yet been reconfirmed on real hardware** — it is currently covered only by mock/unit tests. The next hardware HIL session should confirm all 5 queries respond correctly within one SingleShot without disturbing the existing average result or cleanup behavior.
