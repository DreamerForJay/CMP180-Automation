# CMP180 WLAN SCPI Command Matrix

Status: discovery in progress  
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
| Pause/stop | `STOP:WLAN:MEAS<i>:MEValuation` | Stops without abort semantics | Not executed |
| Abort | `ABORt:WLAN:MEAS<i>:MEValuation` | Abort workflow | Not executed |
| State | `FETCh:WLAN:MEAS<i>:MEValuation:STATe?` | Expected `RDY` after READ | Verified idle: `OFF` |
| All states | `FETCh:WLAN:MEAS<i>:MEValuation:STATe:ALL?` | Detailed status | Verified idle: `OFF,ADJ,INV` |

The first hardware workflow will use `READ...` for a single-shot operation only after
DUT and RF safety conditions are confirmed. `FETCh...` returns the previous result
without initiating a new measurement.

## OFDM SISO scalar results

Primary query:

```text
FETCh:WLAN:MEAS<i>:MEValuation:MODulation:CURRent?
FETCh:WLAN:MEAS<i>:MEValuation:MODulation:AVERage?
FETCh:WLAN:MEAS<i>:MEValuation:MODulation:MINimum?
FETCh:WLAN:MEAS<i>:MEValuation:MODulation:MAXimum?
FETCh:WLAN:MEAS<i>:MEValuation:MODulation:SDEViation?
```

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
