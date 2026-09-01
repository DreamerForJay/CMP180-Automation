# 安全掃描規格 / Safe Sweep Specification

[繁體中文](#繁體中文) · [English](#english)

## 繁體中文

### 目前狀態

頻率與功率掃描已使用 cleanup-protected SingleShot 逐點執行，支援 Web 即時進度、
點位完成事件、取消、partial artifacts、INVALID 立即停止，以及最外層 emergency
STOP／ABORT／RF Off。2026-08-28 已完成下列實機 HIL：

- RF1.1 → RF1.5、6 GHz、320 MHz、-40 dBm，5925–7125 MHz、25 MHz step，
  49/49 有效頻率點。
- RF1.1 → RF1.5、6105 MHz、320 MHz，-55 至 -30 dBm、1 dB step，
  26/26 有效功率點。
- 5085–6125 MHz、20 MHz step 的 53 點工程探索證明 Web 計畫不再被替換成固定三點；
  但其中部分頻率不符合 B6GH／BW320 組合，所以不是 Approved WLAN Profile 證據。

### 四層範圍

1. **Catalog**：CMP180 型錄 400 MHz–8 GHz、最高 500 MHz 分析頻寬，只供顯示。
2. **Planning**：軟體可建立 400 MHz–8 GHz、WLAN 20／40／80／160／320 MHz 計畫。
3. **Approved Profile**：目前只允許 RF1.1→RF1.5、5925–7125 MHz、320 MHz、
   -55 至 -30 dBm、最多 49 點、100–2000 ms。
4. **Verified HIL**：必須有實機 artifacts、read-back、error queue 與 cleanup 證據；
   目前已知 dwell 證據為 100／200 ms。

Web 的 Review Plan 必須同時通過 workflow 硬性檢查、WLAN band/channel 組合與
Approved Profile。Catalog 或 planning 可接受，不代表可以送 RF。

### Workflow 硬性防護

- Generator 與 Analyzer port 不得相同。
- 頻率必須在 400 MHz–8 GHz。
- WLAN bandwidth 必須是 20／40／80／160／320 MHz；是否可執行仍由 band/profile 決定。
- 直連無衰減器時 Generator 不得高於 -30 dBm。
- Dwell 必須在 10–10000 ms。
- 規劃最多 100,000 點，避免極小 step 耗盡 Web job／瀏覽器資源；這是資源防呆，
  不是已驗證 RF 點數。
- RF 執行點數仍由 Approved Profile 限制，目前最多 49 點。

### 每點執行與中止

每一點依序執行設定、read-back、RF On、INIT／FETCh、STOP、RF Off。只有完成 cleanup
後的點才能發布到 Web 即時圖。下列任一條件立即停止整批並保存 partial artifacts：

- reliability 缺失或不為 0。
- EVM All、Burst Power 或 Frequency Error 是 `INV`、缺失、非數字或非有限值。
- SCPI error queue 非空。
- STOP／ABORT／RF Off cleanup 發生錯誤。
- 使用者取消；取消只在 RF Off 點位邊界生效。

INVALID 點不得與有效點連線。EVM limit 的 margin 定義為 `limit - measured`，因此
更負的 EVM 較好；只有 lifecycle=`approved` 的 profile 才可稱為正式 compliance
PASS／FAIL，Draft 只能顯示 DRAFT_PASS／DRAFT_FAIL。

### Power reference 與校正

目前 Analyzer expected nominal power 固定使用已驗證的 -20 dBm ranging 值，不能跟著
Generator power 變動。這不是 +5 dB path-loss compensation。沒有 Approved calibration
profile 時 metadata 必須保留 `calibration_applied=false`，Burst Power 也不得被宣稱為
已校正 DUT reference-plane power。

自 2026-09-01 起可選擇性套用已核准的 path-loss profile：

- 修正套用在 **analyzer external attenuation**（`wlan_tx.set_external_attenuation`，
  已通過 read-back 驗證），這是 CMP180 把量測換算回 DUT reference plane 的機制。
- **Expected nominal power 一律維持已驗證的 -20 dBm**。實機證據顯示讓它跟隨 generator
  power 會使 28 個欄位全部回傳 `INV`，因此校正不得改動它。
- 掃描時 path loss 逐點插值套用，因為損耗隨頻率變化。
- 下列任一情況直接拒絕，不會靜默送出未修正結果：profile 為 draft、已過期、route 不符、
  或任一掃描頻率超出校正範圍（禁止外插）。
- 未提供 profile 時行為與先前完全相同，metadata 保留 `calibration_applied=false`。

用法：在 custom sweep 請求加入 `calibration_profile_path`（相對於 `configs/`）。
**此路徑仍待實機 HIL**：改變 external attenuation 會影響 analyzer ranging，套用後的
第一次量測必須確認未觸發 `INV`。

### 執行入口

```powershell
python -m cmp180_evm.web --host 127.0.0.1 --port 8765
```

啟動服務不會自動送 RF；操作員仍需在 Web 確認 route、人在儀器旁與 Review Plan。
純示範模式使用 `--demo-only`。歷史固定腳本仍保留為回歸入口，但新能力以 Web custom
plan 與 `configs/instrument_capabilities.example.yaml` 為準。

### 能力邊界（期末報告必須誠實標示）

下列項目**尚未完成驗證**，任何報告或交付文件都不得宣稱已支援：

| 項目 | 現況 |
|---|---|
| 400 MHz–8 GHz 全部 WLAN 組合 | 不可宣稱。儀器可調諧該範圍，但有效 WLAN 量測受 band／waveform 限制 |
| 2.4 GHz、5 GHz band | 未完成 HIL；`wlan_bands.py` 的 `band_enum` 為 `None`，程式會拒絕執行 |
| 20／40／80／160 MHz 通道 | 未完成 HIL；僅 320 MHz 有實機證據 |
| 其他 RF ports | 僅 RF1.1 → RF1.5 有證據 |
| 雙 VSA／VSG 並行 | 未驗證，目前只使用一組 |
| 500 MHz analysis bandwidth | 未驗證 |
| Path Loss Calibration | 套用機制已完成（external attenuation，逐點插值，draft／過期／route 不符／外插一律拒絕），但**尚無已核准 profile，且套用後仍未經 HIL** |
| EVM Limit Profile | 仍為 `lifecycle: draft`，只能產生 `DRAFT_PASS`／`DRAFT_FAIL`，不得宣稱 DUT compliance |
| Authentication／RBAC／完整 audit log | 未實作 |
| 內網開放 | 因上一項，目前只能綁定本機 loopback，不應開放公司內網 |
| IQ 指標收斂 | 現有 `LEN4096` waveform 只有 2 個 data OFDM symbol，低於文件要求的 16；Gain Imbalance 與 Quadrature Error 不得宣稱已收斂 |

**解除 band 限制**：執行 `scripts/cmp180_band_discovery.py`（不發射 RF），把接受的
enum 與 readback 連同韌體版本、驗證日期記入 `docs/scpi-command-matrix.md`，再填入
`wlan_bands.py`。填入後該 band 自動變成可執行，但**仍需要該 band 專屬的 ARB waveform
與完整 HIL**才能宣稱支援。

**解除 RF route 限制**：route 核准清單由
`configs/instrument_capabilities.example.yaml` 的 `approved_profile.routes` 驅動
（`workflow/rf_routes.py`），不再寫死於程式。新增一條路徑的順序是：確認兩個 port 都在
`installed.rf_ports`、完成該路徑的線材與衰減確認、跑完整 HIL、再把 route 加入
`approved_profile.routes`。未列入者一律拒絕開啟 RF；port 存在不等於路徑已驗證。

### 尚待完成

完整未驗項目與下一次上機順序請見
[CMP180 能力與 HIL 驗收矩陣](cmp180-capability-hil-matrix.md)。在完成 2.4／5 GHz enum、
其他 bandwidth、route、Path Loss、long waveform、Statistic Count 與 Approved limit 前，
不得宣稱已達 CMP180 全型錄 WLAN 自動化能力。

## English

### Current status

Frequency and power sweeps execute one cleanup-protected SingleShot per point and support
live Web progress, completed-point events, cancellation, partial artifacts, immediate stop
on invalid results, and outer emergency STOP/ABORT/RF Off. Hardware HIL completed on
2026-08-28 includes:

- RF1.1 to RF1.5, 6 GHz, 320 MHz, -40 dBm, 5925–7125 MHz at 25 MHz steps,
  with 49/49 valid frequency points.
- RF1.1 to RF1.5, 6105 MHz, 320 MHz, -55 to -30 dBm at 1 dB steps,
  with 26/26 valid power points.
- A 53-point 5085–6125 MHz engineering exploration proved that the Web plan is no longer
  replaced by a fixed three-point sweep. Some points do not match the B6GH/BW320
  combination, so this is not approved WLAN-profile evidence.

### Four range layers

1. **Catalog**: the CMP180 400 MHz–8 GHz and up-to-500 MHz analysis-bandwidth figures are
   display-only.
2. **Planning**: software can build 400 MHz–8 GHz plans using WLAN 20/40/80/160/320 MHz.
3. **Approved profile**: currently RF1.1 to RF1.5, 5925–7125 MHz, 320 MHz,
   -55 to -30 dBm, at most 49 points, and 100–2000 ms.
4. **Verified HIL**: requires artifacts, read-back, error-queue, and cleanup evidence;
   current dwell evidence covers 100/200 ms.

Web Review Plan must pass the workflow hard guard, the WLAN band/channel combination, and
the approved profile. Catalog/planning acceptance does not authorize RF.

### Non-bypassable workflow guards

- Generator and analyzer ports must differ.
- Frequency must stay within 400 MHz–8 GHz.
- WLAN bandwidth must be 20/40/80/160/320 MHz; band/profile still decides execution.
- Direct loopback without attenuation cannot exceed -30 dBm generator power.
- Dwell must stay within 10–10000 ms.
- Planning is capped at 100,000 points to prevent tiny steps exhausting the Web job or
  browser. This is a resource guard, not verified RF capacity.
- RF execution is still capped by the approved profile, currently 49 points.

### Per-point execution and stop conditions

Each point performs configuration, read-back, RF On, INIT/FETCh, STOP, and RF Off. A point
is published to the live Web plot only after cleanup. The entire batch stops and preserves
partial artifacts when any of the following occurs:

- reliability is missing or nonzero;
- EVM All, Burst Power, or Frequency Error is `INV`, missing, non-numeric, or non-finite;
- the SCPI error queue is non-empty;
- STOP/ABORT/RF Off cleanup fails; or
- the user cancels at an RF-Off point boundary.

Invalid points never connect to valid points. EVM margin is `limit - measured`, so a more
negative EVM is better. Only lifecycle=`approved` may produce compliance PASS/FAIL;
Draft profiles produce DRAFT_PASS/DRAFT_FAIL.

### Power reference and calibration

Analyzer expected nominal power currently uses the HIL-verified fixed -20 dBm ranging
value and must not track generator power. This is not +5 dB path-loss compensation.
Without an approved calibration profile, metadata retains `calibration_applied=false`,
and Burst Power is not a calibrated DUT reference-plane power.

Since 2026-09-01 an approved path-loss profile may optionally be applied:

- The correction is applied to **analyzer external attenuation**
  (`wlan_tx.set_external_attenuation`, already read-back verified), which is how the CMP180
  refers measurements back to the DUT reference plane.
- **Expected nominal power always keeps the verified -20 dBm.** Hardware evidence shows that
  letting it track generator power returns `INV` for all 28 fields, so calibration must not
  touch it.
- Across a sweep the path loss is interpolated and applied per point, because loss varies
  with frequency.
- Any of the following is refused outright rather than silently producing an uncorrected
  result: a draft profile, an expired profile, a route mismatch, or any sweep frequency
  outside the calibrated range (extrapolation is blocked).
- With no profile supplied, behaviour is exactly as before and metadata keeps
  `calibration_applied=false`.

Usage: add `calibration_profile_path` (relative to `configs/`) to the custom sweep request.
**This path still needs hardware HIL**: changing external attenuation affects analyzer
ranging, so the first corrected run must confirm it does not trigger `INV`.

### Entry point

```powershell
python -m cmp180_evm.web --host 127.0.0.1 --port 8765
```

Starting the service does not transmit RF. The operator still confirms the route, physical
presence, and Review Plan in the Web UI. Use `--demo-only` for training. Historical fixed
scripts remain regression entry points, while new capabilities are governed by the Web
custom plan and `configs/instrument_capabilities.example.yaml`.

### Capability boundaries (must be stated honestly in any report)

The following are **not verified**. No report or deliverable may claim support for them:

| Item | Status |
|---|---|
| All WLAN combinations across 400 MHz-8 GHz | Not claimable. The instrument tunes that range, but valid WLAN measurement is limited by band and waveform |
| 2.4 GHz and 5 GHz bands | No HIL. `band_enum` is `None` in `wlan_bands.py`, so the code refuses to run there |
| 20/40/80/160 MHz channels | No HIL. Only 320 MHz has hardware evidence |
| Other RF ports | Only RF1.1 to RF1.5 has evidence |
| Dual VSA/VSG in parallel | Unverified; one set is used today |
| 500 MHz analysis bandwidth | Unverified |
| Path loss calibration | The application path is implemented (external attenuation, per-point interpolation, refusing draft/expired/route-mismatch/extrapolation), but **no approved profile exists and the corrected path has no HIL evidence** |
| EVM limit profile | Still `lifecycle: draft`; produces only `DRAFT_PASS`/`DRAFT_FAIL`, never DUT compliance |
| Authentication/RBAC/full audit log | Not implemented |
| Intranet exposure | Blocked by the previous row; loopback-only binding, must not be exposed on the company network |
| IQ estimator convergence | The current `LEN4096` waveform yields 2 data OFDM symbols, below the documented 16; Gain Imbalance and Quadrature Error must not be claimed as converged |

**To unlock a band**: run `scripts/cmp180_band_discovery.py` (emits no RF), record every accepted
enum and read-back with firmware version and verification date in
`docs/scpi-command-matrix.md`, then fill them into `wlan_bands.py`. That makes the band
executable, but claiming support still requires a band-specific ARB waveform and a full HIL run.

**To unlock an RF route**: the approved list is driven by `approved_profile.routes` in
`configs/instrument_capabilities.example.yaml` (`workflow/rf_routes.py`) rather than hardcoded.
To add a path: confirm both ports appear in `installed.rf_ports`, verify cabling and attenuation
for that path, complete a full HIL run, then add the route to `approved_profile.routes`. Anything
not listed is refused. A port existing on the instrument does not mean the path is verified.

### Remaining work

See the [CMP180 capability and HIL acceptance matrix](cmp180-capability-hil-matrix.md) for
the complete unverified list and next instrument-session order. Do not claim complete
CMP180 catalog WLAN automation until 2.4/5 GHz enums, other bandwidths, routes, path loss,
the long waveform, Statistic Count, and approved limits have passed HIL.
