# CMP180 能力與 HIL 驗收矩陣

[繁體中文](#繁體中文) · [English](#english)

## 繁體中文

### 判定原則

CMP180 型錄規格、這台儀器已安裝的能力、Web 可建立的計畫、已核准的 RF Profile，
以及已完成實機驗收的組合是五件不同的事。只有同時通過設定、read-back、有效量測、
error queue 與 cleanup 證據的組合，才可標示為 HIL 已驗證。型錄能力不得直接轉換為
RF 執行權限。

目前可確認的最高層級是：RF1.1 → RF1.5 直連、EHT、6 GHz band、320 MHz waveform，
5925–7125 MHz 的 49 點頻率掃描，以及 6105 MHz、-55 至 -30 dBm 的 26 點功率掃描。
這代表此組合可重現，不代表所有 16 個 RF port、2.4／5 GHz、所有 WLAN 頻寬、
500 MHz 分析頻寬或雙 VSA／VSG 都已驗收。

### 目前能力矩陣

| 項目 | 型錄／規劃能力 | 目前 Approved Profile | 實機證據 | 狀態 |
|---|---|---|---|---|
| RF 頻率 | 400 MHz–8 GHz | 5925–7125 MHz | 49 點、25 MHz step | 6 GHz HIL 通過；完整型錄範圍未驗 |
| WLAN 頻寬 | 20／40／80／160／320 MHz | 320 MHz | EHT BW320 | 320 MHz HIL 通過；其餘未驗 |
| 分析頻寬 | 型錄最高 500 MHz | 320 MHz | 目前 waveform/read-back 為 320 MHz | 500 MHz 未驗，且不等於 WLAN 500 MHz channel |
| Generator 功率 | 依硬體、路由與校正 | -55 至 -30 dBm | 26 點、1 dB step | 此直連路徑 HIL 通過 |
| Dwell | 10–10000 ms 可規劃 | 100–2000 ms | 100／200 ms | 100／200 ms 有證據，其餘仍需邊界 HIL |
| RF 路徑 | 最多 16 ports，依選件 | RF1.1→RF1.5 | 單一 cable、無衰減器 | 此路徑 HIL 通過；其他路徑未驗 |
| VSA／VSG | 型錄最多各 2 組 | 各 1 組 workflow | WLAN MEAS1 + GPRF Gen1 | 單組 HIL；雙組並行未驗 |
| Waveform | 依 WLAN 選件與檔案 | EHT MU BW320 LEN4096 | lib8 waveform | EVM 可用；IQ estimator symbol 數不足 |
| Trigger／Ranging | 依量測設計 | IF Power、-45 dB、expected -20 dBm | read-back 與有效結果 | 目前組合 HIL 通過 |
| Path Loss | 依外部校正 | 尚無 Approved calibration | metadata=`calibration_applied=false` | 未完成 |
| Limit | 依測試規格／MCS | Draft -32 dB example | DRAFT_PASS／DRAFT_FAIL | 非正式 DUT compliance |

### 已完成證據

- `output/20260828T072935Z_real-frequency-sweep_f0e961bf77`：5925–7125 MHz、
  25 MHz step、49/49 有效點。
- `output/20260828T073121Z_real-power-sweep_5964f567f2`：6105 MHz、-55 至
  -30 dBm、1 dB step、26/26 有效點。
- `output/20260828T075247Z_real-frequency-sweep_a522a8b6a4`：5085–6125 MHz、
  20 MHz step、53 點的工程探索。此 run 證明軟體不再錯縮成三點，但 5085 MHz 搭配
  B6GH／BW320 不是已核准 WLAN 組合，因此不能用來擴大 Approved Profile。

### 下一次上機驗收順序

1. **唯讀能力快照**：保存 `*IDN?`、`*OPT?`、RF path catalog、WLAN standard／band／
   bandwidth、trigger、ranging 與 measurement state；不得 Reset。
2. **RF Off setter/read-back**：逐一確認 2.4／5／6 GHz band enum、20／40／80／160／
   320 MHz、routing 與 waveform；未知 SCPI 維持 `null`。
3. **低功率基準點**：每個新 band／bandwidth／route 先做單點低功率 SingleShot，
   驗證 reliability=0、EVM／Power／Frequency Error 有限、error queue empty。
4. **輸入保護與功率邊界**：套用路徑損耗與 analyzer 最大輸入限制，再由低功率往上；
   第一個 `INV`、overload、error 或 cleanup 異常立即停止。
5. **Waveform／統計**：準備 LEN≥32768 的合法 waveform，並先從 CMP180 Help／Recorder
   驗證 Statistic Count setter/read-back，再驗收 ≥16 symbols 與 ≥20 PPDUs。
6. **路由矩陣**：每條 cable／adapter／attenuator 組合各自建立 calibration profile；
   不可把 RF1.1→RF1.5 的證據複製到其他 port。
7. **正式 limit**：由 RF 負責人核准 MCS、bandwidth、measurement method 與限值版本後，
   才把 lifecycle 改為 `approved` 並產生正式 PASS／FAIL。

每一列 HIL 必須保存：輸入參數、read-back、raw response、normalized result、error queue、
最終 RF／measurement state、儀器與軟體版本、線材／衰減器／校正識別，以及 artifact 路徑。

### 目前不能宣稱的事項

- 尚未達成「400 MHz–8 GHz 任意 WLAN 組合均可執行」。
- 尚未驗證所有 ports、雙 VSA／VSG、500 MHz 分析頻寬、2.4／5 GHz enum。
- 尚未套用正式 Path Loss，也尚未有 Approved EVM limit。
- LEN4096 不足以把 Gain Imbalance／Quadrature Error 當成已收斂結果。
- Statistic Count setter 尚未由官方 Help 或 controlled discovery 驗證，不能猜測 SCPI。

## English

### Decision rule

CMP180 catalog specifications, installed capabilities on this unit, plannable Web inputs,
approved RF profiles, and hardware-verified combinations are five different layers. A
combination is HIL-verified only when configuration, read-back, valid measurements, the
error queue, and deterministic cleanup all have recorded evidence. Catalog capability
never grants RF execution by itself.

The highest currently supported combination is an RF1.1-to-RF1.5 direct loopback, EHT,
6 GHz band, a 320 MHz waveform, a 49-point 5925–7125 MHz frequency sweep, and a 26-point
-55 to -30 dBm power sweep at 6105 MHz. This proves that combination is reproducible; it
does not verify all 16 RF ports, 2.4/5 GHz, every WLAN bandwidth, 500 MHz analysis
bandwidth, or dual VSA/VSG operation.

### Current capability matrix

| Item | Catalog/planning capability | Current approved profile | Hardware evidence | Status |
|---|---|---|---|---|
| RF frequency | 400 MHz–8 GHz | 5925–7125 MHz | 49 points, 25 MHz step | 6 GHz HIL passed; full catalog range unverified |
| WLAN bandwidth | 20/40/80/160/320 MHz | 320 MHz | EHT BW320 | 320 MHz passed; others unverified |
| Analysis bandwidth | Catalog maximum 500 MHz | 320 MHz | Current waveform/read-back is 320 MHz | 500 MHz unverified and not a 500 MHz WLAN channel |
| Generator power | Depends on hardware, route, and calibration | -55 to -30 dBm | 26 points, 1 dB step | Passed for this direct route |
| Dwell | 10–10000 ms plannable | 100–2000 ms | 100/200 ms | Evidence exists for 100/200 ms; other bounds need HIL |
| RF route | Up to 16 ports by option | RF1.1 to RF1.5 | One cable, no attenuator | This route passed; others unverified |
| VSA/VSG | Catalog maximum two each | One workflow each | WLAN MEAS1 + GPRF Gen1 | Single pair passed; dual operation unverified |
| Waveform | Depends on WLAN option/files | EHT MU BW320 LEN4096 | lib8 waveform | EVM usable; IQ estimator lacks symbols |
| Trigger/ranging | Measurement dependent | IF Power, -45 dB, expected -20 dBm | Read-back and valid results | Current combination passed |
| Path loss | External calibration dependent | No approved calibration | `calibration_applied=false` | Incomplete |
| Limit | Test-spec/MCS dependent | Draft -32 dB example | DRAFT_PASS/DRAFT_FAIL | Not DUT compliance |

### Completed evidence

- `output/20260828T072935Z_real-frequency-sweep_f0e961bf77`: 5925–7125 MHz,
  25 MHz step, 49/49 valid points.
- `output/20260828T073121Z_real-power-sweep_5964f567f2`: 6105 MHz, -55 to
  -30 dBm, 1 dB step, 26/26 valid points.
- `output/20260828T075247Z_real-frequency-sweep_a522a8b6a4`: an engineering
  5085–6125 MHz, 20 MHz, 53-point exploration. It proves the software no longer silently
  collapses a plan to three points, but 5085 MHz with B6GH/BW320 is not an approved WLAN
  combination and cannot expand the approved profile.

### Next instrument-session sequence

1. **Query-only capability snapshot**: save identity, options, RF-path catalog, WLAN
   standard/band/bandwidth, trigger, ranging, and measurement state; never reset.
2. **RF-Off setter/read-back**: verify 2.4/5/6 GHz enums, 20/40/80/160/320 MHz, routing,
   and waveform. Unknown SCPI remains `null`.
3. **Low-power reference point**: each new band/bandwidth/route starts with one low-power
   SingleShot and requires reliability=0, finite EVM/power/frequency error, and an empty
   error queue.
4. **Input protection and power boundary**: apply route loss and analyzer input limits,
   then increase power from the low end. Stop on the first invalid, overload, error, or
   cleanup failure.
5. **Waveform/statistics**: prepare a legal LEN≥32768 waveform and verify the Statistic
   Count setter/read-back from CMP180 Help/Recorder before accepting ≥16 symbols and
   ≥20 PPDUs.
6. **Route matrix**: every cable/adapter/attenuator route needs its own calibration profile;
   RF1.1-to-RF1.5 evidence cannot be copied to another port.
7. **Formal limits**: only an RF-owner-approved MCS, bandwidth, measurement method, and
   limit revision can set lifecycle=`approved` and produce compliance PASS/FAIL.

Every HIL row must retain inputs, read-backs, raw and normalized results, error queue,
final RF/measurement state, instrument/software versions, cable/attenuator/calibration
identity, and artifact path.

### Claims that are not yet supported

- Arbitrary WLAN execution over the full 400 MHz–8 GHz catalog range is not verified.
- All ports, dual VSA/VSG, 500 MHz analysis bandwidth, and 2.4/5 GHz enums are unverified.
- Formal path loss and an approved EVM limit are not applied.
- LEN4096 is insufficient to claim converged Gain Imbalance/Quadrature Error.
- The Statistic Count setter has not been verified from official Help or controlled
  discovery, so its SCPI command must not be guessed.
