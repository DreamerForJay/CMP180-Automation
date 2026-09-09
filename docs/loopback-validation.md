# Loopback RF Performance Validation

## 中文版本

### 目的與流程

Loopback Validation 在 DUT 量測前檢查 CMP180、Cable、UD Box、RF routing、波形與設定是否可重複且合理。它不驗證 DUT，也不把單次量測的 CMP180 內部統計誤稱為跨次 baseline。每個 repeat 都執行完整且獨立的 `configure → RF On → INITiate → RDY → FETCh → STOP → RF Off`。暫停與取消只在 RF Off 邊界生效。

INVALID 會完整保存並繼續下一次，以計算 invalid rate；SCPI error、cleanup error 或無法確認 RF Off 則立即停止。Web 即時圖只顯示已完成 cleanup 的 repeat，不會因繪圖額外送 SCPI。

### 分層判定

- Validity：Reliability 必須為 0，且 EVM All、Burst Power、Frequency Error 都是有限數值。
- Stability：比較跨 repeat 的 sample standard deviation（`ddof=1`）、invalid ratio 與 configurable thresholds。
- Reasonableness：在 analyzer input reference plane 計算 `Measured Power − Expected RX Power`。Expected RX Power 與 Analyzer ranging 使用的 `expected_nominal_power_dbm=-20 dBm` 不同。

Overall 判定優先序為 `LOOPBACK_INVALID` → `LOOPBACK_UNSTABLE` → `LOOPBACK_RF_ABNORMAL` → `LOOPBACK_UNVERIFIED` → `LOOPBACK_READY`。Validity 與 Stability 不需要 RF baseline 即可判定，因此實質失敗必須優先於「證據不足」，避免 draft profile 把真實硬體異常顯示成 `LOOPBACK_UNVERIFIED`。Repeat 數不足但沒有 INVALID 時仍屬 `LOOPBACK_UNVERIFIED`，不會誤報為 `LOOPBACK_INVALID`。

Draft profile 只能顯示 `DRAFT_PASS`／`DRAFT_FAIL`，在 validity 與 stability 都沒有失敗時 overall 維持 `LOOPBACK_UNVERIFIED`；`LOOPBACK_RF_ABNORMAL` 只由 approved profile 產生。只有具來源與簽核的 approved profile，連同有效且穩定的結果，才可產生 `LOOPBACK_READY`。

### 統計、Outlier 與 Artifacts

只用 valid finite data 計算 mean、min、max、range、sample standard deviation；Frequency Error 另保存 max absolute value。IQR 1.5 fences 逐 metric 標記 outlier，少於四筆時不宣稱 outlier。Outlier 不會從 raw data 或統計輸入中刪除。Web 趨勢圖會把 IQR outlier 點標成紅色放大點並在 tooltip 註明，INVALID 則以紅色 `×` 呈現；兩者都只是標示，不影響資料保存。

每次 Run 保存 `raw_measurements.csv`、`raw_measurements.json`、`validation_result.json`、`profile_snapshot.json`、`metadata.json`、HTML report 與逐 repeat raw SCPI response。第一版支援單頻點 repeats；多頻點 frequency × repeat 是下一個增量階段。

2026-09-03 已在 RF1.1 → RF1.5 direct-cable path 完成 6105 MHz、320 MHz、−40 dBm、Repeat=10 實機 HIL。結果 10/10 valid，EVM／Power／Frequency Error sample std 分別為 0.03178 dB、0.000604 dB、9.3989 Hz，且 final RF `OFF`、measurement `RDY`、cleanup error 空。Repeat 1 的 Frequency Error 為 IQR outlier，但仍在 approved stability threshold 內且未刪除。來源為 `output/20260903T101748Z_loopback-validation_865ca580c5`；只有精確相同的 RF 條件、門檻與至少 10 repeats 會選到 `rf1.1-rf1.5-6105-bw320-loopback-v1` approved profile，其他組合自動降回 draft。升級後再跑一次 Repeat=10，`output/20260903T102312Z_loopback-validation_76df94aae2` 為 10/10 valid、Stability PASS、Reasonableness PASS、`LOOPBACK_READY`；三項 sample std 為 0.04384 dB、0.000614 dB、12.2401 Hz，final cleanup 同樣安全。

### 全 WLAN Section 批次

「一鍵執行全部」固定建立 2.4 GHz 20/40 MHz、5 GHz 20/40/80/160 MHz、6 GHz 20/40/80/160/320 MHz 共 11 個代表點，每點 Repeat=10。批次只允許 RF1.1 → RF1.5，依序執行並在每個 repeat 及 profile 邊界完成 RF Off；任何 SCPI 或 cleanup error 立即停止後續案例。2026-09-03 批次 110/110 valid，11 個案例皆 Stability PASS、Reasonableness PASS/DRAFT_PASS，所有 metadata 均為 final RF `OFF`、measurement `RDY`、cleanup error 空。十個新 draft 因此各自以本次 artifact 升級為 approved；6105 MHz／320 MHz profile 維持原 approved source。

升級後以相同代表點再次執行 Repeat=10，得到 110/110 valid、11/11 `approved`、Stability PASS、Reasonableness PASS 與 `LOOPBACK_READY`。新正式證據如下：`b24-bw20` → `output/20260903T111307Z_loopback-validation_3d788aaab7`、`b24-bw40` → `output/20260903T111318Z_loopback-validation_10b78189c9`、`b5-bw20` → `output/20260903T111328Z_loopback-validation_80785bf1d1`、`b5-bw40` → `output/20260903T111338Z_loopback-validation_6ecefb0947`、`b5-bw80` → `output/20260903T111350Z_loopback-validation_0a101f3d1b`、`b5-bw160` → `output/20260903T111407Z_loopback-validation_aa0246c5f6`、`b6-bw20` → `output/20260903T111417Z_loopback-validation_c4ecb2633a`、`b6-bw40` → `output/20260903T111427Z_loopback-validation_4b1105336c`、`b6-bw80` → `output/20260903T111440Z_loopback-validation_ca5a87ac3c`、`b6-bw160` → `output/20260903T111456Z_loopback-validation_222d18bb0f`、`b6-bw320` → `output/20260903T111527Z_loopback-validation_582aded41f`。每份 metadata 皆記錄 final RF `OFF`、measurement `RDY`、cleanup error 空；14 個 IQR outlier 只標記並保留，不影響 validity 或 stability 判定。

Web 的 SingleShot、WLAN Sweep、GPRF、Loopback、HIL Campaign 與 Calibration 檢查計畫皆隨中文／English 切換。已顯示 Preview 只用既有回應重繪，不重新呼叫 API 或控制 RF；後端英文安全原因仍原樣保存供稽核，繁中畫面提供對應原因、修正方式與正確範圍。

---

## English Version

### Purpose and flow

Loopback Validation checks whether the CMP180, cable, UD Box, RF routing, waveform, and settings are repeatable and reasonable before DUT testing. It does not validate a DUT or confuse one measurement's internal CMP180 statistics with an across-run baseline. Every repeat performs an independent `configure → RF On → INITiate → RDY → FETCh → STOP → RF Off` cycle. Pause and cancellation take effect only at RF-Off boundaries.

INVALID measurements are retained and collection continues so the invalid rate can be measured; SCPI errors, cleanup errors, or inability to verify RF Off stop execution immediately. Live Web charts contain only repeats whose cleanup has completed and do not transmit extra SCPI.

### Layered decisions

- Validity: Reliability must be zero and EVM All, Burst Power, and Frequency Error must be finite.
- Stability: evaluates across-repeat sample standard deviation (`ddof=1`), invalid ratio, and configurable thresholds.
- Reasonableness: evaluates `Measured Power − Expected RX Power` at the analyzer-input reference plane. Expected RX Power is distinct from the `expected_nominal_power_dbm=-20 dBm` analyzer-ranging setting.

Overall precedence is `LOOPBACK_INVALID` → `LOOPBACK_UNSTABLE` → `LOOPBACK_RF_ABNORMAL` → `LOOPBACK_UNVERIFIED` → `LOOPBACK_READY`. Validity and stability are decidable without an RF baseline, so a substantive failure outranks insufficient evidence and a draft profile can never mask a real hardware anomaly as `LOOPBACK_UNVERIFIED`. Too few repeats with no INVALID measurement stays `LOOPBACK_UNVERIFIED` rather than being misreported as `LOOPBACK_INVALID`.

A draft profile can only produce `DRAFT_PASS` or `DRAFT_FAIL`; when neither validity nor stability fails, overall remains `LOOPBACK_UNVERIFIED`, and `LOOPBACK_RF_ABNORMAL` is reachable only from an approved profile. `LOOPBACK_READY` requires a traceable approved profile plus valid and stable results.

### Statistics, outliers, and artifacts

Mean, minimum, maximum, range, and sample standard deviation use valid finite data; Frequency Error also records maximum absolute value. IQR 1.5 fences flag per-metric outliers, while fewer than four values produce no outlier claim. Outliers are never removed from raw data or statistical inputs. The Web trend charts render IQR outliers as enlarged red points with a tooltip note and INVALID repeats as red `×` markers; both are annotations only and never alter stored data.

Each run saves `raw_measurements.csv`, `raw_measurements.json`, `validation_result.json`, `profile_snapshot.json`, `metadata.json`, an HTML report, and per-repeat raw SCPI responses. Version one supports repeats at one frequency; frequency-by-repeat execution is the next increment.

On 2026-09-03, a live Repeat=10 HIL completed on the RF1.1-to-RF1.5 direct-cable path at 6105 MHz, 320 MHz, and −40 dBm. All 10 repeats were valid; the EVM, power, and frequency-error sample standard deviations were 0.03178 dB, 0.000604 dB, and 9.3989 Hz. Final RF was `OFF`, measurement was `RDY`, and cleanup errors were empty. Repeat 1 was an IQR frequency-error outlier, but it remained inside the approved stability threshold and was not removed. The evidence source is `output/20260903T101748Z_loopback-validation_865ca580c5`. Only the exact RF conditions and thresholds with at least 10 repeats select the approved `rf1.1-rf1.5-6105-bw320-loopback-v1` profile; every other combination falls back to draft. A second Repeat=10 run after approval, `output/20260903T102312Z_loopback-validation_76df94aae2`, completed 10/10 valid with Stability PASS, Reasonableness PASS, and `LOOPBACK_READY`; its three sample standard deviations were 0.04384 dB, 0.000614 dB, and 12.2401 Hz, with the same safe final cleanup.

### All-WLAN-section batch

Run All defines 11 representative points covering 2.4 GHz 20/40 MHz, 5 GHz 20/40/80/160 MHz, and 6 GHz 20/40/80/160/320 MHz, with Repeat=10 at every point. The batch allows only RF1.1 to RF1.5, runs sequentially, and completes RF Off at every repeat and profile boundary. Any SCPI or cleanup error stops all later cases. The 2026-09-03 batch completed 110/110 valid measurements. All 11 cases passed Stability and Reasonableness or draft Reasonableness, and every metadata record ended with RF `OFF`, measurement `RDY`, and no cleanup errors. The ten new drafts were therefore promoted using their own batch artifacts; the 6105 MHz/320 MHz profile retains its original approved evidence source.

The same representative points were rerun after promotion with Repeat=10. The result was 110/110 valid measurements and 11/11 profiles with `approved` lifecycle, Stability PASS, Reasonableness PASS, and `LOOPBACK_READY`. The new formal evidence is: `b24-bw20` → `output/20260903T111307Z_loopback-validation_3d788aaab7`; `b24-bw40` → `output/20260903T111318Z_loopback-validation_10b78189c9`; `b5-bw20` → `output/20260903T111328Z_loopback-validation_80785bf1d1`; `b5-bw40` → `output/20260903T111338Z_loopback-validation_6ecefb0947`; `b5-bw80` → `output/20260903T111350Z_loopback-validation_0a101f3d1b`; `b5-bw160` → `output/20260903T111407Z_loopback-validation_aa0246c5f6`; `b6-bw20` → `output/20260903T111417Z_loopback-validation_c4ecb2633a`; `b6-bw40` → `output/20260903T111427Z_loopback-validation_4b1105336c`; `b6-bw80` → `output/20260903T111440Z_loopback-validation_ca5a87ac3c`; `b6-bw160` → `output/20260903T111456Z_loopback-validation_222d18bb0f`; and `b6-bw320` → `output/20260903T111527Z_loopback-validation_582aded41f`. Every metadata record reports final RF `OFF`, measurement `RDY`, and no cleanup errors. Fourteen IQR outliers remain flagged and preserved without affecting validity or stability.

The SingleShot, WLAN Sweep, GPRF, Loopback, HIL Campaign, and Calibration plan checks in the Web UI all follow the Chinese/English selector. A displayed preview is redrawn from its existing response and never recalls an API or controls RF. Original English backend safety reasons remain unchanged for audit evidence, while the Traditional Chinese UI shows localized reasons, correction guidance, and valid ranges.
