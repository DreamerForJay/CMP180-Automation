# CMP180 Hardware and CMsquares Discovery

Discovery date: 2026-08-13  
Source: CMP180 local Device UI and read-only SCPI queries  
Device address: `192.168.200.50`

## 1. Identity and connectivity

| Item | Confirmed value |
|---|---|
| Product | Rohde & Schwarz CMP180 |
| `*IDN?` model field | `CMP` |
| Device identifier | `1201.0002K18-102502` |
| Base firmware | `6.0.50.23` |
| Device UI | `http://192.168.200.50/deviceui/testenvironment` |
| Raw Socket | TCP 5025, verified |
| HiSLIP | TCP 4880 reachable; R&S VISA not installed on controller |
| Current Python resource | `TCPIP::192.168.200.50::5025::SOCKET` |
| Backend | RsInstrument `SelectVisa='socketio'` |
| `*OPC?` | `1` |
| Error queue | `0,"No error"` at discovery time |

Do not store or publish license keys, activation data, or unrestricted device
footprints in this repository.

## 2. Hardware

| Type | Part name | Part number/version | State |
|---|---|---|---|
| CMP-B40H | CMPSINGLE INTERFACE | `1212.3372.09` | Present |
| CMP-B805I | CMP RF UNIT 500 | `1212.3414.10` | Present |
| CMP-PB18I | CMP180 BASIC ASSEMBLY | `1212.1986.10` | Present |

## 3. Relevant software

| Component | Version |
|---|---|
| COMPLETE_SETUP | `2025.31.0.10` |
| BASE | `6.0.50.23` |
| CMDSET1 | `6.0.50.48` |
| MEASSCPI | `6.0.0.167` |
| GPRF_GEN | `6.0.50.11` |
| GPRF_MEAS | `6.0.50.11` |
| WLAN | `6.0.50.14` |
| WEBGUI | `6.0.32.18` |
| LICENSE_SERVER | `2.18.1.1833` |

Package state is `approved`, configuration is `Release`, status is `active`, and
target type is 64-bit.

## 4. Relevant permanent licenses

| Option | Designation | Count |
|---|---|---:|
| CMP-K105 | ENABLE TRX2 RFU 500 | 1 |
| CMP-K108 | CMP SMART CHANNEL | 1 |
| CMP-K168 | 8 GHZ EXTENSION | 1 |
| CMP-K185 | BANDWIDTH 500MHZ | 1 |
| CMP-KB805 | CMP RF UNIT 500 PERF | 1 |
| CMP-KM350 | WLAN SISO MEAS | 1 |
| CMP-KM351 | WLAN AX SISO MEAS | 1 |
| CMP-KM352 | WLAN BE SISO MEAS | 1 |
| CMP-KV350 | WLAN WAVELIB FSET0 | 1 |
| CMP-KV351 | WLAN WAVELIB FSET1 | 1 |
| CMP-KV352 | WLAN WAVELIB FSET2 | 1 |

Discovery conclusion: the device has a valid license basis for WLAN SISO,
802.11ax SISO, 802.11be SISO, and WLAN waveform libraries.

## 5. Current CMsquares WLAN TX workspace

The following values were read without starting a measurement or changing settings.

### Signal and RF routing

| Parameter | Current value |
|---|---|
| Measurement | WLAN TX Meas 1 / Multi Evaluation |
| State | Off |
| Signal Path | Standalone |
| Standard | 802.11be |
| Receive Mode | SISO |
| Bandwidth | 20 MHz |
| Connection | RF1 5 |
| FDA DUT to MRT | 0.00 dB |
| External Attenuation | 0.00 dB |
| Expected Nominal Power | 0.00 dBm |
| Band | 5 GHz |
| Center Channel | 36 |
| Center Frequency | 5180 MHz |
| User Margin | 3.00 dB |
| Ranging/Interval | Adjust Level / 10.0 ms |
| Modulation Filter | All |

### Measurement control and modulation

| Parameter | Current value |
|---|---|
| Measured Symbols (OFDM) | 1377 symbols |
| Repetition | Continuous |
| Stop Condition | None |
| Synchronization Mode | Normal |
| Measure on Exception | Off |
| Statistic Count | 10 |
| Power evaluation | Enabled |
| Modulation Accuracy | Enabled |
| Unused Tone Error | Disabled |
| Payload Bytes | Disabled |
| Tracking Phase | Enabled |
| Tracking Timing | Enabled |
| Tracking Level | Disabled |
| Channel Estimation | Payload |
| Interpolation | Wiener |
| Smoothing | Disabled |
| Taps | 21 |
| Pilots for Tracking | According to Standard |

### Spectrum, power and trigger

| Parameter | Current value |
|---|---|
| Spectrum Statistic Count | 10 |
| Spectrum Trigger Time | 5000 ns |
| Average Number of FFTs | 8 |
| Occupied Bandwidth | 99% |
| Power vs Time Statistic Count | 10 |
| Average Length | 1 |
| Reference Power | Maximum |
| Trigger Source | IF Power |
| Trigger Threshold | -30.0 dB |
| Trigger Offset | 0.000 us |
| IF Power Minimum Gap | 5 us |
| Trigger Slope | RisingEdge |
| Trigger Timeout | 1000 ms |

Limits dialogs are available for Modulation, Transmit Spectrum Mask, Spectrum
Flatness and Power vs Time. Their limit values were not opened or changed during
this discovery.

## 6. Remote Trace discovery

CMsquares contains a General Configuration > Remote Trace function.

- Current state: OFF.
- Destinations: screen, file, or screen and file.
- Available metadata: ID, data, event type, timestamps, execution duration,
  VISA resource, connection ID and instrument number.
- Available event classes: input, output, error, RIM call and RIM result.
- File destination: session log folder under `RemoteTrace/RemoteTrace.log`.
- The session log alias can be queried with `MMEM:ALIases?` and checking
  `@SESSION`.
- Relevant configuration command exposed by built-in help:
  `[CONFigure:]BASE:RTRace:TARGet`.

Controlled testing confirmed that Remote Trace monitors external remote connections;
it does not translate internal CMsquares GUI changes into SCPI. With only GUI activity,
the square reported zero open connections and no trace rows. It remains useful for
monitoring and diagnosing the Python client after automation begins. GUI-to-command
mapping must use each parameter's built-in Help > Remote command reference.

## 7. Remaining discovery work

1. Continue reading built-in WLAN Help for required commands and result schemas.
2. Validate every selected query against the hardware without initiating a measurement.
3. Validate configuration writes only against a saved and approved test profile.
4. Use Remote Trace later to observe and diagnose the Python remote connection.
5. Record an actual DUT golden result; the current workspace was Off during this
   discovery, so no EVM result was collected.

## 8. Read-only SCPI validation

The script `scripts/cmp180_wlan_discover.py` validated 19 queries against the
hardware. Every query returned `0,"No error"` afterward.

| Item | Instrument response |
|---|---|
| Standard | `EHT` |
| Bandwidth | `BW20` |
| RF path | `"RF1.5"` |
| RF path count | `1` |
| External attenuation | `0.0` |
| Expected nominal power | `0.0` |
| Band | `B5GH` |
| Center frequency | `5.18E9` Hz |
| Channel | `36` |
| Trigger source | `"IF Power"` |
| Trigger threshold | `-30.0` dB |
| Trigger offset | `0.0` s |
| IF power minimum gap | `5.0E-6` s |
| Trigger slope | `REDG` |
| Trigger timeout | `1.0` s |
| Measurement state | `OFF` |
| Detailed state | `OFF,ADJ,INV` |
# 2026-08-18 query-only connection verification

- PC Ethernet: `192.168.200.12/24`
- CMP180: `192.168.200.50:5025`
- TCP connection: passed through the Ethernet interface
- Returned `*IDN?`: `Rohde&Schwarz,CMP,1201.0002k18/102502,6.0.50.23`
- Finding: CMP180 uses the model field `CMP`, not `CMP180`; identity validation
  was corrected to parse the model field instead of searching the whole IDN.
- `*OPT?` and the final error-queue result must be captured by rerunning the
  query-only connection command after this correction.
