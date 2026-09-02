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

### WLAN band enum 實機探索 / WLAN band enum hardware discovery

2026-09-01 以 `scripts/cmp180_band_discovery.py` 在 CMP180 韌體 `6.0.50.23` 上探索。
全程 Generator RF `OFF`、量測 idle，僅寫入 Analyzer band 後立即讀回，結束後還原為
`B6GH` 並確認 RF 仍為 `OFF`。此探索未發射 RF。

| 候選字串 | 儀器回應 | Readback | 結論 |
|---|---|---|---|
| `B24Ghz` | 接受，error queue 空 | `B24G` | 2.4 GHz 可用 |
| `B24GHz` | 接受，error queue 空 | `B24G` | 2.4 GHz 可用（採用此拼法） |
| `B2G4` | `-141,"Invalid character data"` | — | 不支援 |
| `B5GHz` | 接受，error queue 空 | `B5GH` | 5 GHz 可用（採用此拼法） |
| `B5GH` | 接受，error queue 空 | `B5GH` | 5 GHz 可用 |
| `B5Ghz` | 接受，error queue 空 | `B5GH` | 5 GHz 可用 |
| `B6GHz` | 接受，error queue 空 | `B6GH` | 6 GHz，先前已驗證 |

副作用：改變 Analyzer 的 WLAN band 設定（不影響 RF 輸出、routing 或 workspace）。
已填入 `src/cmp180_evm/workflow/wlan_bands.py`。

**band setter 可用不等於該 band 已可量測**：2.4／5 GHz 仍缺該 band 專屬的 ARB
waveform 與完整 HIL，且 `configs/instrument_capabilities.example.yaml` 的
approved profile 仍只授權 5925–7125 MHz，因此這兩個 band 目前不會送出 RF。

English: on 2026-09-01 `scripts/cmp180_band_discovery.py` probed firmware `6.0.50.23`
with generator RF `OFF` and the measurement idle, writing each candidate to the analyzer
band, reading it back, then restoring `B6GH` and confirming RF stayed `OFF`. No RF was
transmitted. `B2G4` was rejected with `-141,"Invalid character data"`; every other
candidate was accepted with an empty error queue. A working band setter does **not**
authorize measurement in that band: 2.4/5 GHz still lack a band-specific ARB waveform and
full HIL, and the approved profile still limits RF to 5925-7125 MHz.
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
| Repetition | `CONFigure:WLAN:MEAS<i>:MEValuation:REPetition` | `SINGleshot` for remote fixed-condition results | WebHelp + HIL verified 2026-09-01 |
| Modulation statistic count | `CONFigure:WLAN:MEAS<i>:MEValuation:SCOunt:MODulation` | 10 intervals per SingleShot | WebHelp + HIL verified 2026-09-01 |

`INITiate` was verified twice with Generator RF off: `INITiate -> STOP` and
`INITiate -> ABORt` both returned `0,"No error"`. `FETCh...` returns the previous
result without initiating a new measurement.

2026-09-01 中文：CMsquares 的 `Continuous` + Stop Condition `None` 會使遠端 INIT
持續為 `RUN`。backend 現在於 RF Off 強制設定並 read-back `SINGleshot` 與
Statistic Count 10。黃金點、49 點頻率與 26 點功率 campaign 均通過。

English: CMsquares `Continuous` with Stop Condition `None` keeps a remote INIT in `RUN`.
The backend now sets and reads back `SINGleshot` and Statistic Count 10 while RF is off.
The golden point, 49-point frequency sweep, and 26-point power campaign all passed.

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

**2026-08-20 更新**：`workflow/cmp180_single_backend.py` 已在同一次真實 SingleShot
依序查詢並保存 `CURRent`／`AVERage`／`MINimum`／`MAXimum`／`SDEViation`。五個
responses 各有完整 28 欄，instrument／cleanup errors 為空；獨立收尾確認 RF
`OFF`、measurement `RDY`、error queue empty。證據為 run `e854e20fd8`，詳見
`docs/hardware-discovery.md`。這只驗證固定 profile SingleShot，不代表 Sweep HIL。

## English: complete SingleShot verification

The first complete Python hardware SingleShot passed on 2026-08-19. It configured the verified profile, enabled RF, sent `INITiate`, waited for `RDY`, fetched the 28-field average result, sent `STOP`, and disabled RF. EVM All was -36.23029 dB, Burst Power -40.47938 dBm, and Frequency Error -16.30075 Hz; instrument and cleanup error lists were empty. Independent queries confirmed final RF `OFF` and measurement `RDY`.

**2026-08-20 update**: `workflow/cmp180_single_backend.py` has now queried and saved
`CURRent`/`AVERage`/`MINimum`/`MAXimum`/`SDEViation` sequentially in one real
SingleShot. All five responses contained 28 fields, instrument/cleanup errors were empty,
and independent final auditing confirmed RF `OFF`, measurement `RDY`, and an empty error
queue. Evidence is run `e854e20fd8` in `docs/hardware-discovery.md`. This validates only
the fixed-profile SingleShot and does not qualify as Sweep HIL.

## 中文：2026-08-25 新確認的控制命令

下列命令由 CMP180 6.0.50.23 內建 Help 確認，並完成 setter/readback。ARB 模式必須
使用 Sequencer state；通用 Generator state 不代表 ARB 正在播放。也必須檢查
`FETCh:...:STATe:ALL?`，因為主狀態 `RDY` 仍可能同時含 `INV`。

| 功能 | Setter／Query | 狀態 |
|---|---|---|
| ARB On/Off | `SOURce:GPRF:GEN:SEQuencer:STATe ON/OFF`、同樹 `?` | Help + hardware verified |
| ARB repetition | `SOURce:GPRF:GEN:SEQuencer:REPetition CONT`、同樹 `?` | Help + hardware verified |
| WLAN standard | `CONFigure:WLAN:MEAS:ISIGnal:STANdard EHTofdm` | Help + `EHT` readback |
| WLAN band | `CONFigure:WLAN:MEAS:RFSettings:FREQuency:BAND B6GHz` | Help + `B6GH` readback |
| Trigger threshold | `TRIGger:WLAN:MEAS:MEValuation:THReshold -45` | Help + readback；尚無有效結果 |
| Trigger source | `TRIGger:WLAN:MEAS:MEValuation:SOURce "GPRF Gen1: Restart Marker"` | Help + readback；終態仍 `INV` |

## English: newly confirmed control commands on 2026-08-25

The following commands were confirmed by CMP180 6.0.50.23 built-in Help and exercised
with setter/readback checks. ARB mode must use the Sequencer state; the generic Generator
state does not indicate ARB playback. `FETCh:...:STATe:ALL?` must also be checked because
a main `RDY` state can still contain an `INV` substate.

| Function | Setter/query | Status |
|---|---|---|
| ARB On/Off | `SOURce:GPRF:GEN:SEQuencer:STATe ON/OFF` and same-tree `?` | Help + hardware verified |
| ARB repetition | `SOURce:GPRF:GEN:SEQuencer:REPetition CONT` and same-tree `?` | Help + hardware verified |
| WLAN standard | `CONFigure:WLAN:MEAS:ISIGnal:STANdard EHTofdm` | Help + `EHT` readback |
| WLAN band | `CONFigure:WLAN:MEAS:RFSettings:FREQuency:BAND B6GHz` | Help + `B6GH` readback |
| Trigger threshold | `TRIGger:WLAN:MEAS:MEValuation:THReshold -45` | Help + readback; no valid result yet |
| Trigger source | `TRIGger:WLAN:MEAS:MEValuation:SOURce "GPRF Gen1: Restart Marker"` | Help + readback; final state still `INV` |

## 中文：2026-08-27 Baseband ARB 狀態樹修正

本固定 profile 使用 GPRF Baseband ARB，因此 RF workflow 必須使用
`SOURce:GPRF:GEN:STATe ON/OFF` 與同樹 query。`...:SEQuencer:STATe` 僅適用 ARB
Sequencer mode，不得拿來啟動已由 Baseband ARB 選取的 waveform。本修正已由有效
SingleShot、三點頻率 sweep 與四點功率 sweep 實機驗證。

## English: 2026-08-27 Baseband ARB state-tree correction

The fixed profile uses GPRF Baseband ARB, so its RF workflow must use
`SOURce:GPRF:GEN:STATe ON/OFF` and same-tree queries. `...:SEQuencer:STATe` applies only
to ARB Sequencer mode and must not start a waveform selected through Baseband ARB. The
correction is hardware-verified by a valid SingleShot, three-point frequency sweep, and
four-point power sweep.

## 中文：2026-09-02 ARB waveform 盤點與選擇

| 功能 | Query／Setter | 實機結果 | 副作用 |
|---|---|---|---|
| ARB 絕對路徑 | `SOURce:GPRF:GEN:ARB:FILE? ABSPath` | Help 確認；回傳選取檔，error queue empty | 唯讀 |
| 路徑 alias | `MMEMory:ALIases?` | Base Help 確認；回傳 `@WAVEFORM` 等 alias | 唯讀 |
| 目錄盤點 | `MMEMory:CATalog? "{path_pattern}"` | Base Help 確認；WLAN 目錄回傳 2,766 個 `.wv` | 唯讀 |
| 選擇 ARB | `SOURce:GPRF:GEN:ARB:FILE "{arb_file}"` | GPRF Help 確認；五種頻寬皆通過 setter、OPC、error 與 readback | 改變 baseband 檔案；只可在 RF OFF／measurement idle 執行 |

## English: 2026-09-02 ARB waveform inventory and selection

| Function | Query/setter | Hardware result | Side effect |
|---|---|---|---|
| ARB absolute path | `SOURce:GPRF:GEN:ARB:FILE? ABSPath` | Help-confirmed; returned the selected file with an empty error queue | Query-only |
| Path aliases | `MMEMory:ALIases?` | Base Help-confirmed; returned aliases including `@WAVEFORM` | Query-only |
| Directory inventory | `MMEMory:CATalog? "{path_pattern}"` | Base Help-confirmed; WLAN directory returned 2,766 `.wv` files | Query-only |
| Select ARB | `SOURce:GPRF:GEN:ARB:FILE "{arb_file}"` | GPRF Help-confirmed; all five bandwidths passed setter, OPC, error, and readback checks | Changes the baseband file; RF must be OFF and measurement idle |

## 中文：2026-09-02 GPRF Power measurement 命令

下列命令屬於 CMP180 **GPRF power measurement** application，量測的是 RF 功率，
**不是 WLAN EVM 解調**。其結果不得呈現為 WLAN 解調數據或合規宣告。呼叫端為
`src/cmp180_evm/web/gprf_service.py` 的 `run_gprf_power_sweep()`。

出處建立方式：`scripts/cmp180_gprf_measurement_discover.py`（純唯讀，逐條發問後讀
`SYST:ERR?`，由儀器回答支不支援）與 `scripts/cmp180_gprf_measurement_setter_validate.py`
（RF Off 下同值寫回 + `*OPC?` + error queue + read-back）。

| 功能 | 完整命令 | 參數／單位 | 回傳欄位／單位 | 狀態副作用 |
|---|---|---|---|---|
| 設定量測頻率 | `CONFigure:GPRF:MEASurement1:RFSettings:FREQuency {frequency_hz}` | `frequency_hz`，Hz | 無（write-only） | 改變 GPRF measurement instance 1 的 RF 設定；不改 routing 或 workspace |
| 啟動 power 量測 | `INITiate:GPRF:MEASurement1:POWer` | 無 | 無 | **改變 measurement state**（idle → 量測中）；必須搭配 `STOP` 收尾 |
| 停止 power 量測 | `STOP:GPRF:MEASurement1:POWer` | 無 | 無 | 停止 GPRF power measurement；cleanup 路徑必用 |
| 讀取目前 power | `FETCh:GPRF:MEASurement1:POWer:CURRent?` | 無 | `reliability,power_dbm`：reliability 為整數指標（`0` 表示有效），power 單位 dBm | 唯讀，只讀已存結果，不啟動量測 |
| 查詢量測頻率 | `CONFigure:GPRF:MEASurement1:RFSettings:FREQuency?` | 無 | Hz，實測 `6.105000E+09` | 唯讀 |
| 量測端 RF path | `ROUTe:GPRF:MEASurement1:SPATh?`／`... {rf_path}` | 帶引號 port 字串，如 `"RF1.5"` | 帶引號 port，實測原值 `"RF1.6"` | **改變量測端 routing**；只可在 RF OFF 時寫入 |
| 量測端可用 port | `CATalog:GPRF:MEASurement1:SPATh?` | 無 | 16 個 port：`"RF1.1"`…`"RF2.8"` | 唯讀 |
| Expected nominal power | `CONFigure:GPRF:MEASurement1:RFSettings:ENPower?`／`... {expected_power_dbm}` | dBm | dBm，實測原值 `0.000000E+00` | 改變量測端 ranging；只可在 RF OFF 時寫入 |
| External attenuation | `CONFigure:GPRF:MEASurement1:RFSettings:EATTenuation?`／`... {external_attenuation_db}` | dB | dB，實測原值 `0.000000E+00` | 改變量測端位準修正；只可在 RF OFF 時寫入 |
| User margin | `CONFigure:GPRF:MEASurement1:RFSettings:UMARgin?` | 無 | dB，實測 `0.000000E+00` | 唯讀（本專案未寫入） |

### 實機驗證證據

- 驗證日期：2026-09-02。儀器 `Rohde&Schwarz,CMP,1201.0002k18/REDACTED`，Base firmware `6.0.50.23`。
- 執行路徑：Web `/api/jobs/hardware/gprf-power-sweep`，單點 6105 MHz、Generator -40 dBm、
  dwell 200 ms、RF1.1 → RF1.5 直連、0 dB 衰減、操作員在場。
- Query 探索（唯讀）：7 條候選全部支援，error queue 全空，結束時 Generator RF 仍為 `OFF`。
- Setter 驗證（同值寫回，RF Off）：`rf_path` `"RF1.6"`、`expected_power`
  `0.000000E+00`、`external_attenuation` `0.000000E+00` 三項皆 `0,"No error"`
  且 read-back 一致，RF `OFF → OFF`。
- 修正前 run：`252bbbe39a`（`output/20260902T040938Z_gprf-power-sweep_252bbbe39a/`），
  回應 `0,-8.087470E+01` → -80.8747 dBm。當時量測端停在**未接線的 `"RF1.6"`**，
  此數值實為雜訊底，不是路徑損耗。
- 修正後 run：`d3c259178c`（`output/20260902T064552Z_gprf-power-sweep_d3c259178c/`）。
  workflow 已在 RF Off 時寫入並 read-back `"RF1.5"`、ENPower -40 dBm、EATT 0 dB。
  回應 `3,-5.625053E+01` → **reliability `3`（非 0）**、-56.2505 dBm。
  `error_queue` 與 `cleanup_errors` 皆為空；獨立查詢確認最終 Generator RF `OFF`、
  error queue `0,"No error"`。

### 落差修正進度與仍未解決的問題

已解決：

1. **error queue 證據**：`gprf_service.py` 每點量測後與 cleanup 後都查詢 `SYST:ERR?`
   （每點記入 `error_queue` 欄，收尾記入 `cleanup_errors`），非空時該點一律標為
   `INVALID`。run `d3c259178c` 已具備 error-queue 證據（空佇列）。
2. **量測端 RF path**：`ROUTe:GPRF:MEASurement1:SPATh` 已取得出處並納入 command map；
   workflow 現在依 `cable_confirmation` 解析出的 analyzer port 明確寫入並 read-back，
   不符即中止，不再沿用儀器殘留設定。
3. **量測端位準**：ENPower 依每點 generator 功率設定、EATTenuation 明確寫入，皆在 RF Off 時完成。
4. **出處**：query 與 setter 皆由儀器在韌體 `6.0.50.23` 上回答並附 error-queue 證據，
   取代先前不存在的「既有 GPRF Gen/Meas 實測腳本」說法。

5. **突發 ARB 導致的量值偏低與 reliability `3`**：中間 run `d3c259178c` 仍讀到
   -56.25 dBm 且 reliability `3`。根因是產生器當時播放突發 WLAN ARB 波形
   （`KV352_lib8_WLAN_11be_EHT_MU_BW320-1_4xLTF_GI32_MCS11_LEN4096_LDPC.wv`），
   功率計把閒置期一併平均。改用 CW 後兩者同時消失（見下節）。本專案仍**沒有**
   reliability 數值對照表的正式出處，因此只記錄「CW 下觀察到 `0`」這個事實，
   不推斷代碼 `3` 的語意。

## 中文：2026-09-02 GPRF Generator baseband mode（CW）

GPRF power sweep 的用途是量測 WLAN 涵蓋不到的範圍（400 MHz–8 GHz 掃頻、線損校正、
port 頻率響應），因此必須使用連續波；WLAN EVM 則必須使用 ARB 波形。兩者對訊號的
要求互斥，所以 workflow 改為進入 GPRF 前切 CW、收尾還原原始 baseband 與 waveform。

| 功能 | 完整命令 | 參數／值 | 回傳 | 狀態副作用 |
|---|---|---|---|---|
| 查詢 baseband mode | `SOURce:GPRF:GEN:BBMode?` | 無 | 實測原值 `ARB` | 唯讀 |
| 設定 baseband mode | `SOURce:GPRF:GEN:BBMode {mode}` | 已驗證值：`CW`、`ARB` | 無 | **改變產生器 baseband**；只可在 RF OFF 時寫入 |

出處：`scripts/cmp180_gprf_bbmode_discovery.py`，韌體 `6.0.50.23`，2026-09-02。
`CW` 與 `ARB` 皆被接受、readback 一致、error queue 全空。其他候選 header
（`CATalog:GPRF:GEN:BBMode?`、`SOURce:GPRF:GEN:BBMode:CATalog?`、
`SOURce:GPRF:GEN:ARB:STATe?`、`...:LIST:STATe?`、`...:DTONe:STATe?`）皆回
`-113,"Undefined header"`，故未納入 command map。

**重要實機發現**：切換 baseband mode 到 `CW` 再切回 `ARB` **不會清除**已選取的 ARB
waveform；探索與實測都確認還原後絕對路徑完全相同。即使如此，`gprf_service.py` 仍在
收尾時比對 waveform，不一致就用已驗證的 setter 重新指定，並把不符記為 `cleanup_errors`。

### CW 修正後的實機證據

- Run `67ccd62048`（`output/20260902T073149Z_gprf-power-sweep_67ccd62048/`），
  6105 MHz、Generator -40 dBm、`baseband_mode=CW`、量測端 `"RF1.5"`、ENPower -40 dBm。
- 回應 `0,-3.971061E+01` → **reliability `0`**、-39.7106 dBm。相對 -40 dBm 僅差
  **0.29 dB**，與直連線的預期損耗一致。`valid=true`、`limit_status=MEASURED`，
  `error_queue` 與 `cleanup_errors` 皆空。
- 收尾還原確認：baseband `ARB`、ARB waveform 絕對路徑與原值相同、Generator RF `OFF`、
  WLAN measurement `RDY`、error queue `0,"No error"`。
- WLAN 回歸驗證（run `7ccdb50ca1`）：同一條線與 profile 下 EVM data carriers
  **-36.86 dB**、burst power -39.80 dBm、頻率誤差 4.15 Hz、MCS11／GI32，
  與 CW 切換前的歷史結果一致，確認 WLAN 能力未受影響。

進度總結：三個量測數值落差（-80.87 → -56.25 → -39.71 dBm）已全部歸因並修正。
GPRF power 現在可用於其設計用途；但線損校正若要成為正式數據，仍需依
`docs/development-workflow.md` 完成 Calibration Profile 核准流程。

## English: 2026-09-02 GPRF power measurement commands

The commands below belong to the CMP180 **GPRF power measurement** application. They
measure RF power and are **not WLAN EVM demodulation**; their results must never be
presented as WLAN demodulation data or a compliance claim. The caller is
`run_gprf_power_sweep()` in `src/cmp180_evm/web/gprf_service.py`.

Provenance was established with `scripts/cmp180_gprf_measurement_discover.py` (query-only:
each candidate is asked, then `SYST:ERR?` is read, so the instrument itself answers whether
it supports the header) and `scripts/cmp180_gprf_measurement_setter_validate.py` (same-value
write-back with RF off, plus `*OPC?`, error queue, and read-back).

| Function | Full command | Params/units | Return fields/units | State side effect |
|---|---|---|---|---|
| Set measurement frequency | `CONFigure:GPRF:MEASurement1:RFSettings:FREQuency {frequency_hz}` | `frequency_hz`, Hz | None (write-only) | Changes the RF settings of GPRF measurement instance 1; does not change routing or workspace |
| Start power measurement | `INITiate:GPRF:MEASurement1:POWer` | None | None | **Changes measurement state** (idle → measuring); requires a matching `STOP` |
| Stop power measurement | `STOP:GPRF:MEASurement1:POWer` | None | None | Stops the GPRF power measurement; required on the cleanup path |
| Read current power | `FETCh:GPRF:MEASurement1:POWer:CURRent?` | None | `reliability,power_dbm`: reliability is an integer indicator (`0` means valid), power in dBm | Query-only; returns the stored result without initiating a measurement |
| Query measurement frequency | `CONFigure:GPRF:MEASurement1:RFSettings:FREQuency?` | None | Hz; measured `6.105000E+09` | Query-only |
| Measurement RF path | `ROUTe:GPRF:MEASurement1:SPATh?` / `... {rf_path}` | Quoted port string, e.g. `"RF1.5"` | Quoted port; original value measured as `"RF1.6"` | **Changes measurement-side routing**; write only while RF is OFF |
| Available measurement ports | `CATalog:GPRF:MEASurement1:SPATh?` | None | 16 ports, `"RF1.1"`…`"RF2.8"` | Query-only |
| Expected nominal power | `CONFigure:GPRF:MEASurement1:RFSettings:ENPower?` / `... {expected_power_dbm}` | dBm | dBm; original value measured as `0.000000E+00` | Changes measurement-side ranging; write only while RF is OFF |
| External attenuation | `CONFigure:GPRF:MEASurement1:RFSettings:EATTenuation?` / `... {external_attenuation_db}` | dB | dB; original value measured as `0.000000E+00` | Changes measurement-side level correction; write only while RF is OFF |
| User margin | `CONFigure:GPRF:MEASurement1:RFSettings:UMARgin?` | None | dB; measured `0.000000E+00` | Query-only (not written by this project) |

### Hardware verification evidence

- Verification date: 2026-09-02. Instrument `Rohde&Schwarz,CMP,1201.0002k18/REDACTED`,
  base firmware `6.0.50.23`.
- Execution path: Web `/api/jobs/hardware/gprf-power-sweep`, one point at 6105 MHz,
  -40 dBm generator power, 200 ms dwell, direct RF1.1 → RF1.5 cable, 0 dB attenuation,
  operator present.
- Query discovery (read-only): all seven candidates were supported with an empty error
  queue, and generator RF was still `OFF` at the end.
- Setter validation (same-value write-back, RF off): `rf_path` `"RF1.6"`, `expected_power`
  `0.000000E+00`, and `external_attenuation` `0.000000E+00` each returned `0,"No error"`
  with a matching read-back, and RF went `OFF → OFF`.
- Pre-fix run: `252bbbe39a` (`output/20260902T040938Z_gprf-power-sweep_252bbbe39a/`)
  returned `0,-8.087470E+01` → -80.8747 dBm. The measurement side was still parked on the
  **uncabled `"RF1.6"`** port, so that figure is a noise floor, not a path loss.
- Post-fix run: `d3c259178c` (`output/20260902T064552Z_gprf-power-sweep_d3c259178c/`). The
  workflow wrote and read back `"RF1.5"`, ENPower -40 dBm, and EATT 0 dB while RF was off.
  The response was `3,-5.625053E+01` → **reliability `3` (not 0)**, -56.2505 dBm.
  Both `error_queue` and `cleanup_errors` were empty, and independent queries confirmed a
  final generator RF of `OFF` with an error queue of `0,"No error"`.

### Gap remediation status and unresolved issues

Resolved:

1. **Error-queue evidence**: `gprf_service.py` queries `SYST:ERR?` after every measured
   point and again after cleanup (per point in `error_queue`, cleanup in `cleanup_errors`),
   and a non-empty queue forces that point to `INVALID`. Run `d3c259178c` carries
   error-queue evidence (empty queue).
2. **Measurement RF path**: `ROUTe:GPRF:MEASurement1:SPATh` now has provenance and is in the
   command map. The workflow explicitly writes and reads back the analyzer port parsed from
   `cable_confirmation` and aborts on a mismatch instead of inheriting instrument state.
3. **Measurement level settings**: ENPower is set from each point's generator power and
   EATTenuation is written explicitly, both while RF is off.
4. **Provenance**: the queries and setters were answered by the instrument itself on
   firmware `6.0.50.23` with error-queue evidence, replacing the earlier reference to a
   non-existent "existing GPRF Gen/Meas hardware script".

5. **Low readings and reliability `3` caused by the bursted ARB**: the intermediate run
   `d3c259178c` still read -56.25 dBm with reliability `3`. The cause was the generator
   playing a bursted WLAN ARB waveform
   (`KV352_lib8_WLAN_11be_EHT_MU_BW320-1_4xLTF_GI32_MCS11_LEN4096_LDPC.wv`), which the power
   meter averaged together with the idle periods. Switching to CW cleared both symptoms (see
   the next section). This project still has **no** sourced reliability-code table, so only
   the observed fact that CW yields `0` is recorded; the meaning of code `3` is not inferred.

## English: 2026-09-02 GPRF generator baseband mode (CW)

The GPRF power sweep exists to measure what WLAN mode cannot cover (400 MHz–8 GHz sweeps,
cable-loss calibration, port frequency response), so it needs a continuous wave, while WLAN
EVM needs the ARB waveform. Those requirements are mutually exclusive, so the workflow now
selects CW on entry and restores the original baseband mode and waveform during cleanup.

| Function | Full command | Params/values | Returns | State side effect |
|---|---|---|---|---|
| Query baseband mode | `SOURce:GPRF:GEN:BBMode?` | None | Original value measured as `ARB` | Query-only |
| Set baseband mode | `SOURce:GPRF:GEN:BBMode {mode}` | Verified values: `CW`, `ARB` | None | **Changes the generator baseband**; write only while RF is OFF |

Provenance: `scripts/cmp180_gprf_bbmode_discovery.py`, firmware `6.0.50.23`, 2026-09-02.
Both `CW` and `ARB` were accepted with matching read-backs and an empty error queue. The
other candidate headers (`CATalog:GPRF:GEN:BBMode?`, `SOURce:GPRF:GEN:BBMode:CATalog?`,
`SOURce:GPRF:GEN:ARB:STATe?`, `...:LIST:STATe?`, `...:DTONe:STATe?`) all returned
`-113,"Undefined header"` and were therefore not added to the command map.

**Important hardware finding**: switching the baseband mode to `CW` and back to `ARB` does
**not** clear the selected ARB waveform; both discovery and the live run confirmed an
identical absolute path after restore. Even so, `gprf_service.py` still compares the
waveform during cleanup, reselects it with the verified setter on any mismatch, and records
a mismatch in `cleanup_errors`.

### Hardware evidence after the CW fix

- Run `67ccd62048` (`output/20260902T073149Z_gprf-power-sweep_67ccd62048/`) at 6105 MHz with
  -40 dBm generator power, `baseband_mode=CW`, measurement port `"RF1.5"`, ENPower -40 dBm.
- Response `0,-3.971061E+01` → **reliability `0`**, -39.7106 dBm. That is only **0.29 dB**
  from the -40 dBm generator level, consistent with a direct cable. The point is
  `valid=true` and `limit_status=MEASURED`, with empty `error_queue` and `cleanup_errors`.
- Restore verified: baseband `ARB`, an ARB waveform absolute path identical to the original,
  generator RF `OFF`, WLAN measurement `RDY`, and an error queue of `0,"No error"`.
- WLAN regression check (run `7ccdb50ca1`): on the same cable and profile, EVM data carriers
  measured **-36.86 dB**, burst power -39.80 dBm, frequency error 4.15 Hz, MCS11/GI32 —
  consistent with results from before the CW change, confirming WLAN capability is intact.

Summary: all three measured-value discrepancies (-80.87 → -56.25 → -39.71 dBm) are now
explained and corrected. GPRF power is usable for its intended purpose, but cable-loss
figures still require the Calibration Profile approval flow in
`docs/development-workflow.md` before they become formal data.
