# CMP180 Hardware and CMsquares Discovery

Initial discovery date: 2026-08-13
Latest hardware verification: 2026-08-20
Source: CMP180 local Device UI and read-only SCPI queries  
Device address: `192.168.200.50`

## 1. Identity and connectivity

| Item | Confirmed value |
|---|---|
| Product | Rohde & Schwarz CMP180 |
| `*IDN?` model field | `CMP` |
| Device identifier | Redacted; not required for automation |
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

## 2. Hardware, software, and options

The required WLAN SISO capability was confirmed on the lab instrument. Detailed
part numbers, license inventories, activation data, and license-server details
are intentionally excluded from this repository because they are not required
to operate or test the automation code.

## 3. Current CMsquares WLAN TX workspace

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
- Returned `*IDN?`: `Rohde&Schwarz,CMP,1201.0002k18/REDACTED,6.0.50.23`
- Finding: CMP180 uses the model field `CMP`, not `CMP180`; identity validation
  was corrected to parse the model field instead of searching the whole IDN.
- Returned `*OPT?`:
  `CMP-B40H,CMP-B805I,CMP-K105,CMP-K108,CMP-K168,CMP-K185,CMP-KB805,`
  `CMP-KH40,CMP-KH805,CMP-KM310,CMP-KM350,CMP-KM351,CMP-KM352,CMP-KV310,`
  `CMP-KV350,CMP-KV351,CMP-KV352,CMP-PB18I`
- Final error queue: empty
- Result: the Python connection framework can identify the real CMP180, read
  its installed option identifiers, drain the error queue, and disconnect
  without resetting the workspace or changing RF/measurement settings.
- Scope limit: this proves the control connection only. It is not WLAN TX EVM
  measurement evidence and does not validate any CMP180-specific command.

## 2026-08-18 WLAN MEAS1 query-only discovery

All 19 queries completed successfully and every immediate `SYST:ERR?` returned
`0,"No error"`.

| Field | Real response | Interpreted value |
|---|---|---|
| Standard | `EHT` | IEEE 802.11be |
| Bandwidth | `BW20` | 20 MHz |
| RF path | `"RF1.5"` | Analyzer input RF1.5 |
| RF path count | `1` | SISO path count |
| External attenuation | `0.000000E+00` | 0 dB |
| Expected nominal power | `0.000000E+00` | 0 dBm |
| Band | `B5GH` | 5 GHz |
| Center frequency | `5.180000E+09` | 5180 MHz |
| Channel | `36` | Channel 36 |
| Trigger source | `"IF Power"` | IF Power trigger |
| Trigger threshold | `-3.000000E+01` | -30 dB |
| Trigger offset | `0.000000E+00` | 0 s |
| Trigger minimum gap | `5.000000E-06` | 5 us |
| Trigger slope | `REDG` | Rising edge |
| Trigger timeout | `1.000000E+00` | 1 s |
| Measurement state | `OFF` | Measurement is off |
| All measurement states | `OFF,ADJ,INV` | Off, adjust/invalid result state |

The RF path catalog returned RF1.1 through RF1.8 and RF2.1 through RF2.8. The
trigger catalog returned 11 available sources. The exact raw output is stored
locally under `output/` and is intentionally excluded from Git.

This discovery validates query-only configuration/state commands. It does not
validate setters, measurement initiation, RF control, or EVM result queries.

## 2026-08-18 controlled RF loopback verification

A direct 50-ohm coaxial cable connected generator port RF1.1 to WLAN analyzer
port RF1.5. No external attenuator was present. The test was performed through
CMsquares with both resources initially Off.

| Parameter | Verified setting |
|---|---|
| Generator routing | RF1.1 only |
| Analyzer routing | RF1.5 |
| Generator waveform | `KV352_lib8_WLAN_11be_EHT_MU_BW320-1_4xLTF_GI32_MCS11_LEN4096_LDPC.wv` |
| Standard / bandwidth | IEEE 802.11be / 320 MHz |
| Center frequency | 6105 MHz (6 GHz, center channel 31) |
| Generator level | -40 dBm RMS/indicated peak output power |
| External attenuation | 0 dB |
| Measurement repetition | SingleShot |

The first attempt used an expected nominal power of -40 dBm and returned
`Input Overdriven`. RF output and measurement were stopped immediately. The
generator routing was then rechecked: RF1.1 was enabled and RF1.2 through
RF1.8, including RF1.5, were disabled.

The generator level remained at -40 dBm. Only the analyzer expected nominal
power was changed to -20 dBm to provide additional measurement range. The
second SingleShot completed and returned `Ready` without the overdrive error.
The generator was then returned to Off.

This confirms that the physical RF1.1-to-RF1.5 loopback can generate and
capture the configured 802.11be waveform. It does not yet provide recorded EVM
or power values in the CMsquares workspace because no numeric WLAN result view
was configured there.

The subsequent query-only Python result discovery successfully fetched the
stored SingleShot result. All five aggregate modulation queries returned
`0,"No error"` and exactly 28 OFDM SISO fields.

| Statistic | EVM all carriers | Burst power | Frequency error |
|---|---:|---:|---:|
| Current | -36.12723 dB | -40.56531 dBm | -23.80315 Hz |
| Average | -36.14424 dB | -40.56650 dBm | -6.496213 Hz |
| Minimum | -36.25381 dB | -40.56822 dBm | -3.635299 Hz |
| Maximum | -36.02105 dB | -40.56469 dBm | -35.87564 Hz |
| Standard deviation | 0.08628786 dB | 0.001082599 dB | 17.81418 Hz |

The measurement state was `RDY`. The discovery used only `FETCh` commands and
did not start a measurement or enable RF. Run it with:

```powershell
python scripts\cmp180_wlan_result_discover.py
```

This is the first quantitative WLAN loopback reference result for the project.
It verifies result retrieval and parsing, but Python-controlled configuration,
RF enable/disable and measurement initiation are still pending.
## 中文：2026-08-19 Generator setter 驗證

在 CMP180 序號 REDACTED 上執行 `scripts/cmp180_generator_setter_validate.py --confirm-same-value-write`。工具先確認 RF 為 `OFF`，再將目前的 6105 MHz 與 -40 dBm 原值寫回。兩個 setter 的 read-back 均與原值一致，`SYST:ERR?` 均回傳 `0,"No error"`，最後 RF state 為 `OFF`。本次沒有 RF On，也沒有啟動 WLAN 量測。

## 中文：2026-08-19 WLAN Analyzer setter 驗證

第一次執行時 measurement state 為 `RDY`，舊安全閘門要求 `OFF`，因此工具在任何寫入前正確拒絕。唯讀 discovery 隨後確認 `RDY,ADJ,INV`，且 19 項查詢均無錯誤。將 `RDY` 明確列為 idle/ready 狀態並補測試後，完成 RF1.5、`BW32`、6105 MHz、0 dB external attenuation 與 -20 dBm expected power 的同值寫回。所有 read-back 一致且錯誤佇列為空，最終狀態為 Generator `OFF`、measurement `RDY`。

## English: 2026-08-19 Generator setter validation

`scripts/cmp180_generator_setter_validate.py --confirm-same-value-write` was run against CMP180 serial REDACTED. The tool first required RF `OFF`, then wrote the existing 6105 MHz and -40 dBm values back. Both read-backs matched, every `SYST:ERR?` returned `0,"No error"`, and final RF state remained `OFF`. This validation did not enable RF or initiate a WLAN measurement.

## English: 2026-08-19 WLAN Analyzer setter validation

The first attempt found measurement state `RDY`; the original safety gate required `OFF`, so the tool correctly refused before sending any write. Read-only discovery then confirmed `RDY,ADJ,INV`, with all 19 queries error-free. After explicitly treating `RDY` as idle/ready and adding tests, same-value writes passed for RF1.5, `BW32`, 6105 MHz, 0 dB external attenuation, and -20 dBm expected power. Every read-back matched, the error queue remained empty, and final states were Generator `OFF` and measurement `RDY`.

## 中文：2026-08-19 Measurement lifecycle 驗證

在 Generator `OFF` 下完成兩個 Analyzer lifecycle：`INITiate → RUN → STOP → RDY` 與 `INITiate → RUN → ABORt → OFF`。每一步均回傳 `0,"No error"`；最終 Generator 與 measurement 都為 `OFF`。由於沒有 RF 訊號，本次只驗證控制流程，不是有效 EVM 量測。

## English: 2026-08-19 measurement lifecycle validation

Two Analyzer lifecycles were completed with Generator `OFF`: `INITiate → RUN → STOP → RDY` and `INITiate → RUN → ABORt → OFF`. Every step returned `0,"No error"`; final Generator and measurement states were both `OFF`. With no RF signal, this validates control flow only and is not a valid EVM measurement.

## 中文：2026-08-19 RF On/Off pulse 驗證

操作員當次確認 RF1.1 → RF1.5 單條 cable 且人在儀器旁後，於 6105 MHz、-40 dBm 執行極短 RF pulse。狀態 read-back 為 `ON → OFF`，RF On 與 RF Off 後的 `SYST:ERR?` 都回傳 `0,"No error"`。本次未啟動 Analyzer measurement，最後 RF 為 `OFF`。

## English: 2026-08-19 RF On/Off pulse validation

After current operator confirmation of the RF1.1-to-RF1.5 direct cable and physical presence, a brief RF pulse ran at 6105 MHz and -40 dBm. State read-back was `ON → OFF`, and `SYST:ERR?` returned `0,"No error"` after both RF On and RF Off. No Analyzer measurement was initiated, and final RF state was `OFF`.

## 中文：2026-08-19 完整 Python SingleShot

第一筆完整 Python 實機 SingleShot 已通過：RF1.1 → RF1.5、6105 MHz、320 MHz、Generator -40 dBm、Analyzer expected power -20 dBm。平均 EVM All 為 -36.23029 dB、Burst Power -40.47938 dBm、Frequency Error -16.30075 Hz；instrument errors 與 cleanup errors 都為空。獨立收尾查詢確認 RF `OFF`、measurement `RDY`。

最新 stored result 已保存為 run `872e0c12bf`，包含 CSV、JSON、metadata 與原始 modulation-average response。metadata 明確標記為完整 SingleShot 後的 stored `FETCh`，不是這次唯讀擷取工具所啟動的新量測。

## English: 2026-08-19 complete Python SingleShot

The first complete Python hardware SingleShot passed using RF1.1 to RF1.5, 6105 MHz, 320 MHz, -40 dBm Generator power, and -20 dBm Analyzer expected power. Average EVM All was -36.23029 dB, Burst Power -40.47938 dBm, and Frequency Error -16.30075 Hz; instrument and cleanup error lists were empty. Independent final queries confirmed RF `OFF` and measurement `RDY`.

The latest stored result was saved as run `872e0c12bf`, including CSV, JSON, metadata, and the raw modulation-average response. Metadata explicitly identifies it as a stored `FETCh` after the complete SingleShot, not a new measurement initiated by the read-only capture tool.

## 中文：2026-08-20 五統計完整 SingleShot HIL

操作員當次確認 RF1.1 → RF1.5 50 Ω 直連、無衰減器且人在 CMP180 旁後，執行固定
6105 MHz、320 MHz、Generator -40 dBm、Analyzer expected -20 dBm 的完整 Python
SingleShot。流程完整走過 validating、configuring、rf_on、measuring、fetching、
cleaning_up 與 complete；instrument／cleanup errors 均為空。

Run `e854e20fd8` 的 average EVM All 為 -36.14103 dB、Burst Power -40.49398 dBm、
Frequency Error -15.33705 Hz。`CURRent`、`AVERage`、`MINimum`、`MAXimum` 與
`SDEViation` 五個 raw responses 各含完整 28 欄，JSON 明確標記 `simulated=false`。
EVM All 五組值依序為 current -36.07222 dB、average -36.14103 dB、minimum
-36.33857 dB、maximum -35.79554 dB、standard deviation 0.1727547 dB。

獨立 query-only 收尾確認 Generator 6105 MHz／-40 dBm 且 RF `OFF`，Analyzer
RF1.5／BW32／6105 MHz／expected -20 dBm，measurement `RDY`；所有查詢的 error
queue 均為 `0,"No error"`。本次正式完成「同一 SingleShot 連續擷取並保存五統計」
的實機 HIL，但尚未驗證 Frequency／Power Sweep。

## English: 2026-08-20 complete five-statistic SingleShot HIL

After the operator reconfirmed a direct 50-ohm RF1.1-to-RF1.5 cable with no attenuator
and physical presence beside the CMP180, a complete Python SingleShot ran at 6105 MHz,
320 MHz, -40 dBm Generator power, and -20 dBm Analyzer expected power. It completed the
validating, configuring, rf_on, measuring, fetching, cleaning_up, and complete phases
with empty instrument and cleanup error lists.

Run `e854e20fd8` produced average EVM All -36.14103 dB, Burst Power -40.49398 dBm,
and Frequency Error -15.33705 Hz. The `CURRent`, `AVERage`, `MINimum`, `MAXimum`, and
`SDEViation` raw responses each contained all 28 fields, and JSON recorded
`simulated=false`. EVM All was current -36.07222 dB, average -36.14103 dB, minimum
-36.33857 dB, maximum -35.79554 dB, and standard deviation 0.1727547 dB.

Independent query-only auditing confirmed Generator 6105 MHz/-40 dBm with RF `OFF`,
Analyzer RF1.5/BW32/6105 MHz/expected -20 dBm, and measurement `RDY`; every error-queue
query returned `0,"No error"`. This completes hardware HIL for fetching and saving all
five statistics in one SingleShot. Frequency and Power Sweep remain unverified on hardware.

## 中文：2026-08-20 三點頻率掃描 HIL

操作員重新確認 RF1.1 → RF1.5 50 Ω 直連、無衰減器且人在 CMP180 旁後，執行固定
6085／6105／6125 MHz、320 MHz、Generator -40 dBm、Analyzer expected -20 dBm、
100 ms dwell 的完整 Python 三點頻率掃描。三點結果如下：

| 頻率 | EVM All（平均） | Burst Power（平均） | Frequency Error（平均） |
|---:|---:|---:|---:|
| 6085 MHz | -36.15892 dB | -40.48821 dBm | -20.14753 Hz |
| 6105 MHz | -36.22592 dB | -40.44269 dBm | -8.378243 Hz |
| 6125 MHz | -36.20570 dB | -40.44243 dBm | -31.73889 Hz |

Run `bb3e8db580` 完成三點，`simulated=false`、`status=complete`、沒有失敗頻率；
每點 instrument／cleanup errors 均為空。每一個頻點都保存 average／current／minimum／
maximum／standard deviation 五組、每組 28 欄的 raw response。CSV、JSON、metadata、raw
與 HTML report 均已成功產生。最外層收尾確認 RF `OFF`、measurement `RDY`、error queue
空。這正式完成固定三點頻率掃描的實機 HIL；功率掃描與 Web 實機掃頻仍未驗證／開放。

## English: 2026-08-20 three-point frequency-sweep HIL

After the operator reconfirmed a direct 50-ohm RF1.1-to-RF1.5 cable, no attenuator,
and physical presence beside the CMP180, Python ran the fixed 6085/6105/6125 MHz,
320 MHz, -40 dBm Generator, -20 dBm Analyzer expected-power, 100 ms dwell sweep.

| Frequency | Average EVM All | Average Burst Power | Average Frequency Error |
|---:|---:|---:|---:|
| 6085 MHz | -36.15892 dB | -40.48821 dBm | -20.14753 Hz |
| 6105 MHz | -36.22592 dB | -40.44269 dBm | -8.378243 Hz |
| 6125 MHz | -36.20570 dB | -40.44243 dBm | -31.73889 Hz |

Run `bb3e8db580` completed all three points with `simulated=false`, `status=complete`,
and no failed frequency. Every point had empty instrument and cleanup error lists and
saved five 28-field raw responses: average, current, minimum, maximum, and standard
deviation. CSV, JSON, metadata, raw, and HTML artifacts were created successfully.
Outer cleanup confirmed RF `OFF`, measurement `RDY`, and an empty error queue. This
completes hardware HIL for the fixed three-point frequency sweep. Power-sweep HIL and
the Web hardware sweep remain unverified/locked.

## 中文：2026-08-20 五點功率掃描首次 HIL 發現

操作員確認 RF1.1 → RF1.5 直連、無衰減器且人在儀器旁後，於固定 6105 MHz、320 MHz、
expected power -20 dBm 執行 -60／-55／-50／-45／-40 dBm。Run `56ab9c982e`
的 -60 dBm 回傳 reliability `6`，其餘 27 個 average 欄位均為 `INV`；-55 至
-40 dBm 則取得數值。最終 RF `OFF`、measurement `RDY`、error queue empty，所有點的
instrument／cleanup errors 也為空。

這揭露原核心只依 error queue 與 cleanup 判斷成功，會把 `INV` 批次錯標成
`status=complete`。因此此 run 是 HIL finding，不是通過證據；其 artifacts 保留原貌，不
回寫竄改。程式已新增 EVM、Burst Power、Frequency Error 必須為有限數值的閘門，任一
為 `INV`／缺少／非有限值時即停止後續較高功率並保存 partial result。修正後仍需新的
現場確認與重測，才能判定功率掃描 HIL 是否通過。

## English: 2026-08-20 first five-point power-sweep HIL finding

After operator confirmation of the direct RF1.1-to-RF1.5 cable, no attenuator, and
on-site presence, the -60/-55/-50/-45/-40 dBm sweep ran at fixed 6105 MHz, 320 MHz,
and -20 dBm expected power. At -60 dBm, run `56ab9c982e` returned reliability `6`
and `INV` for the other 27 average fields; -55 through -40 dBm returned numeric data.
Final RF was `OFF`, measurement was `RDY`, the error queue was empty, and all point
instrument/cleanup error lists were empty.

This exposed that the original core relied only on the error queue and cleanup status,
so it incorrectly labeled the batch `status=complete`. This run is an HIL finding, not
passing evidence; its artifacts remain immutable and are not rewritten. A new gate now
requires finite EVM, Burst Power, and Frequency Error values. `INV`, missing, or non-finite
critical values stop all higher-power points and produce a partial result. A new on-site
confirmation and rerun are required before power-sweep HIL can pass.

## 中文：2026-08-20 `INV` 立即停止 HIL

修正版以相同接線與 -60／-55／-50／-45／-40 dBm 計畫重跑。Run `b8db34c0f4`
在第一點 -60 dBm 再次取得 `INV`，隨即標記 `status=partial`、
`failed_power_dbm=-60.0`，且錯誤明確列出 EVM、Burst Power、Frequency Error 三個
無效關鍵欄位。-55 至 -40 dBm 均未執行。該點 instrument／cleanup errors 為空，最終
RF `OFF`、measurement `RDY`、error queue empty；五組 raw response 均已保存。

這完成「遇到 `INV` 不得提高功率、立即停止並保存 partial result」的實機 HIL。它同時
確認 -60 dBm 在目前 expected power -20 dBm／trigger 設定下不是有效量測點。下一個
量測批次應以已取得有效數值的 -55 至 -40 dBm 為候選範圍，且不得為了取得 -60 dBm
數值而未經驗證自行改 expected power 或 trigger。

## English: 2026-08-20 immediate-stop-on-`INV` HIL

The corrected version reran the same cabling and -60/-55/-50/-45/-40 dBm plan. Run
`b8db34c0f4` again received `INV` at the first -60 dBm point, immediately recorded
`status=partial` and `failed_power_dbm=-60.0`, and named EVM, Burst Power, and Frequency
Error as invalid critical fields. No -55 through -40 dBm point ran. The point had empty
instrument/cleanup error lists, final RF `OFF`, measurement `RDY`, an empty error queue,
and all five raw responses were saved.

This completes hardware HIL for stopping before higher power and preserving a partial
result on `INV`. It also shows that -60 dBm is not a valid measurement point with the
current -20 dBm expected-power and trigger configuration. The next candidate batch is
-55 through -40 dBm, where numeric data was previously observed. Do not change expected
power or trigger merely to recover -60 dBm without a separately validated plan.

## 中文：2026-08-20 四點有效功率掃描 HIL

在相同 RF1.1 → RF1.5 直連、6105 MHz、320 MHz、expected power -20 dBm 下，
run `e6e86fe3d7` 完成 -55／-50／-45／-40 dBm 四點批次：

| Generator 設定 | EVM All（平均） | Burst Power（平均） | Frequency Error（平均） |
|---:|---:|---:|---:|
| -55 dBm | -30.09611 dB | -55.46333 dBm | -62.52845 Hz |
| -50 dBm | -32.13561 dB | -50.47972 dBm | -62.10172 Hz |
| -45 dBm | -33.13222 dB | -45.80714 dBm | -29.48505 Hz |
| -40 dBm | -35.85040 dB | -40.83130 dBm | -37.78031 Hz |

Metadata 為 `simulated=false`、`status=complete`、四點完成且無失敗功率；每點
instrument／cleanup errors 均空。共保存 20 份 raw response（4 點 × 5 統計），以及
CSV、JSON、metadata、HTML。最終 RF `OFF`、measurement `RDY`、error queue empty。
這完成 -55 至 -40 dBm 固定功率掃描 CLI HIL；-60 dBm 維持已知無效點，不納入候選
有效範圍。Web 實機功率掃描仍需獨立的 progress／cancel／cleanup 驗收。

## English: 2026-08-20 four-point numeric power-sweep HIL

With the same direct RF1.1-to-RF1.5 path, 6105 MHz, 320 MHz, and -20 dBm expected
power, run `e6e86fe3d7` completed the -55/-50/-45/-40 dBm batch:

| Generator setting | Average EVM All | Average Burst Power | Average Frequency Error |
|---:|---:|---:|---:|
| -55 dBm | -30.09611 dB | -55.46333 dBm | -62.52845 Hz |
| -50 dBm | -32.13561 dB | -50.47972 dBm | -62.10172 Hz |
| -45 dBm | -33.13222 dB | -45.80714 dBm | -29.48505 Hz |
| -40 dBm | -35.85040 dB | -40.83130 dBm | -37.78031 Hz |

Metadata records `simulated=false`, `status=complete`, four completed points, and no
failed power. Every point had empty instrument/cleanup error lists. Twenty raw responses
(four points times five statistics), CSV, JSON, metadata, and HTML were saved. Final RF
was `OFF`, measurement was `RDY`, and the error queue was empty. This completes CLI HIL
for the fixed -55 through -40 dBm power sweep. -60 dBm remains a known invalid point and
is excluded from the candidate numeric range. Web hardware power sweep still requires
separate progress/cancel/cleanup acceptance.

## 中文：2026-08-20 Web 實機掃描與取消 HIL

在硬體模式只綁定 `127.0.0.1`、RF1.1 → RF1.5 直連且操作員在場的條件下，Web run
`afb64617df` 完成 6085／6105／6125 MHz 三點頻率掃描：

| 頻率 | EVM All（平均） | Burst Power（平均） | Frequency Error（平均） |
|---:|---:|---:|---:|
| 6085 MHz | -36.33 dB | -40.34 dBm | -9.64 Hz |
| 6105 MHz | -36.41 dB | -40.30 dBm | -40.52 Hz |
| 6125 MHz | -36.40 dB | -40.29 dBm | -9.96 Hz |

頻率工作狀態為 `COMPLETE`、進度 3/3，並產生 CSV、JSON、metadata 與 HTML。接著 Web
run `7463d55002` 執行 -55／-50／-45／-40 dBm 功率掃描；第一點完成後送出取消，取消在
下一個 RF Off 安全邊界生效，狀態為 `CANCELLED`、進度 2/4，保存 -55 dBm（EVM
-30.32 dB）與 -50 dBm（EVM -32.24 dB）兩筆 partial results 及完整 artifacts。
獨立唯讀收尾確認 Generator `OFF`、measurement `RDY`，所有狀態查詢後的 error queue
均為 `0,"No error"`。因此 Web 實機進度、正常完成、cooperative cancellation、partial
artifact 與 emergency cleanup 驗收通過。

## English: 2026-08-20 Web hardware sweep and cancellation HIL

With hardware mode bound only to `127.0.0.1`, a direct RF1.1-to-RF1.5 cable, and the
operator present, Web run `afb64617df` completed the 6085/6105/6125 MHz frequency sweep:

| Frequency | Average EVM All | Average Burst Power | Average Frequency Error |
|---:|---:|---:|---:|
| 6085 MHz | -36.33 dB | -40.34 dBm | -9.64 Hz |
| 6105 MHz | -36.41 dB | -40.30 dBm | -40.52 Hz |
| 6125 MHz | -36.40 dB | -40.29 dBm | -9.96 Hz |

The frequency job reached `COMPLETE` at 3/3 and produced CSV, JSON, metadata, and HTML.
Web run `7463d55002` then started the -55/-50/-45/-40 dBm power sweep. Cancellation was
requested after the first point and took effect at the next RF-Off safe boundary. The job
ended `CANCELLED` at 2/4, preserving -55 dBm (EVM -30.32 dB) and -50 dBm (EVM -32.24 dB)
partial results and complete artifacts. Independent read-only cleanup checks confirmed
Generator `OFF`, measurement `RDY`, and `0,"No error"` after every status query. This
passes Web hardware progress, normal completion, cooperative cancellation, partial
artifact, and emergency-cleanup acceptance.

## 中文：2026-08-25 現場重驗與目前阻點

RF1.1 → RF1.5 單一直連、無衰減器且操作員在場。儀器韌體為 6.0.50.23。現場發現
儀器曾回到 CW、802.11a/g（`LOFD`）與 2.4 GHz（`B24G`）；已在 RF Off 狀態恢復
ARB、EHT、6 GHz、BW320，並載入目前儀器可用的
`KV352_lib1_11be_EHT_MU_BW320_4xLTF_GI08_MCS11_LEN4096_LDPC.wv`。原文件的
lib8/GI32 檔案目前不在 waveform pool，兩者不可視為同一固定 profile。

內建 Help 與實機 readback 確認 ARB Sequencer `STATe`、`REPetition CONT`、WLAN
standard/band、trigger threshold 與 trigger source setter。以 -40 dBm、6105 MHz、
320 MHz 重驗時，run `414f714ee6` 的五組 28 欄結果皆為 reliability `4` 加 27 個
`INV`；instrument/cleanup errors 均空。IF Power 與 `GPRF Gen1: Restart Marker`
兩種觸發都得到 `RUN → RDY`，但完整終態為 `RDY,ADJ,INV`。因此 2026-08-25
沒有新的有效 SingleShot，也沒有執行新的 frequency/power sweep。既有 2026-08-20
HIL 證據仍保留，但目前 waveform/profile 必須先完成同步或解調診斷才能重驗。

## English: 2026-08-25 on-site revalidation and current blocker

The setup used one direct RF1.1-to-RF1.5 cable, no attenuator, and an on-site operator.
The instrument firmware is 6.0.50.23. It had reverted to CW, 802.11a/g (`LOFD`), and
2.4 GHz (`B24G`). With RF off, it was restored to ARB, EHT, 6 GHz, and BW320, using
`KV352_lib1_11be_EHT_MU_BW320_4xLTF_GI08_MCS11_LEN4096_LDPC.wv`, the waveform
currently available on the instrument. The previously documented lib8/GI32 file is not
present in the current waveform pool, so these must not be treated as the same profile.

Built-in Help and hardware readback confirmed ARB Sequencer `STATe`, `REPetition CONT`,
WLAN standard/band, trigger-threshold, and trigger-source setters. At -40 dBm, 6105 MHz,
and 320 MHz, run `414f714ee6` returned reliability `4` plus 27 `INV` fields for all five
statistics, with empty instrument/cleanup error lists. Both IF Power and
`GPRF Gen1: Restart Marker` triggering produced `RUN → RDY`, but the full final state
was `RDY,ADJ,INV`. Therefore, no new valid SingleShot or frequency/power sweep was
completed on 2026-08-25. The 2026-08-20 HIL evidence remains recorded, but the current
waveform/profile needs synchronization or demodulation diagnosis first.

## 中文：2026-08-27 根因修正與重新 HIL

Chrome 現場檢查確認原 lib8/GI32 waveform 仍存在且已選取；8/25 的「只剩 lib1」判斷
已被本次實機證據推翻。實際漂移項目為 Generator/WLAN 頻率 5500 MHz、Analyzer 5 GHz、
expected power -32.48 dBm、Generator level -20 dBm，以及 RF connection 未正確顯示。
在 RF Off 下恢復 6105 MHz、6 GHz channel 31、RF1.5、expected -20 dBm、Generator
-40 dBm 後，CMsquares stored result run `5460070513` 得到 reliability 0、平均 EVM
-36.65688 dB。

Python 根因為把 GPRF Baseband ARB waveform 誤用 ARB Sequencer state tree。依內建 Help
改用 `SOURce:GPRF:GEN:STATe ON` 並以同樹 query 驗證後，run `5cabdc74de` 完整
SingleShot 通過：EVM -36.72543 dB、Burst Power -39.95473 dBm、Frequency Error
-18.1467 Hz，errors 與 cleanup errors 皆空。頻率 sweep `e0a40c3bab` 完成
6085/6105/6125 MHz；功率 sweep `5cbb6c37a7` 完成 -55/-50/-45/-40 dBm。兩批最終
皆 RF OFF、measurement RDY、error queue empty。

## English: 2026-08-27 root-cause correction and renewed HIL

On-site Chrome inspection confirmed that the original lib8/GI32 waveform is still present
and selected; the August 25 conclusion that only lib1 remained is superseded by this hardware
evidence. The actual drift was Generator/WLAN at 5500 MHz, Analyzer on 5 GHz, expected power
at -32.48 dBm, Generator level at -20 dBm, and an RF connection that was not correctly shown.
After restoring 6105 MHz, 6 GHz channel 31, RF1.5, -20 dBm expected power, and -40 dBm
Generator power while RF was off, CMsquares stored-result run `5460070513` returned
reliability 0 and average EVM of -36.65688 dB.

The Python root cause was using the ARB Sequencer state tree for a GPRF Baseband ARB
waveform. After switching to `SOURce:GPRF:GEN:STATe ON` with same-tree readback, complete
SingleShot run `5cabdc74de` passed with EVM -36.72543 dB, Burst Power -39.95473 dBm,
Frequency Error -18.1467 Hz, and empty instrument/cleanup errors. Frequency sweep
`e0a40c3bab` completed 6085/6105/6125 MHz, and power sweep `5cbb6c37a7` completed
-55/-50/-45/-40 dBm. Both batches ended with RF off, measurement ready, and an empty
error queue.
