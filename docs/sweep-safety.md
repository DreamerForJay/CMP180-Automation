# 安全短掃描規格 / Safe Short Sweep Specification

## 中文版本

### 目前狀態

安全短掃描（頻率掃描與功率掃描）的 Python 核心與 Mock 測試都已完成，但都尚未開放 Web 實機按鈕。固定三點頻率掃描、功率掃描 `INV` 立即停止，以及 -55 至 -40 dBm 四點有效功率批次皆已完成 CLI 實機 HIL。11 點／200 MHz span 頻率掃描與 10 點／2 dB step 功率掃描的腳本已備妥，但尚未實機執行。Web 掃描仍是 Mock，需獨立驗收後才可解鎖。

### 三點頻率掃描 HIL 入口

第一版實機入口固定為 RF1.1 → RF1.5、6085／6105／6125 MHz、320 MHz、-40 dBm、expected power -20 dBm、100 ms dwell，不接受任意 RF 參數。每點均執行完整 SingleShot，點與點之間會 STOP 並 RF Off；外層 `finally` 再執行 emergency STOP／ABORt、RF Off、狀態與 error queue 回讀。

只有在當次已重新確認單一 cable 直連且操作員在儀器旁時，才可執行：

```powershell
python scripts\cmp180_frequency_sweep_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present `
  --confirm-three-point-sweep
```

未帶齊三個確認旗標時，程式會在連線與送出 SCPI 前拒絕執行。成功或部分失敗都會在 `output\<run-id>\` 保存 CSV、JSON、metadata、raw responses 與 HTML；partial metadata 會記錄成功點數、失敗頻率與錯誤。

### 十一點頻率掃描 HIL 入口（已備妥腳本，尚未實機執行）

以三點批次為基礎，把單次掃描擴大到現有硬性包絡在 `frequency_sweep.py` 允許的最大值：
11 點、200 MHz span，以已驗證的 6105 MHz 為中心對稱往外取
6005／6025／6045／6065／6085／6105／6125／6145／6165／6185／6205 MHz，其餘設定
（RF1.1 → RF1.5、320 MHz、-40 dBm、expected power -20 dBm、100 ms dwell）與三點批次
相同。這批只是把「已驗證」點數往「硬性上限」補齊，沒有更動任何安全常數。

```powershell
python scripts\cmp180_frequency_sweep_wide_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present `
  --confirm-eleven-point-sweep
```

尚未在實機執行；執行後請把結果（含 partial/失敗點）補進
`docs/hardware-discovery.md` 才能視為完成 HIL。

### 頻率掃描安全範圍

- Routing：只允許已驗證的 RF1.1 → RF1.5。
- 頻率：5925–7125 MHz。
- 最大 span：200 MHz。
- 最大點數：11 點。
- Generator power：不得高於 -40 dBm。
- Bandwidth：固定為已驗證的 320 MHz。
- Dwell：100–2000 ms。

### 功率掃描安全範圍

- Routing：只允許已驗證的 RF1.1 → RF1.5。
- Generator power：-60 至 -40 dBm。
- 最大點數：11 點。
- Dwell：100–2000 ms。
- 頻率固定於單一已驗證值（目前對應 6105 MHz）。
- Bandwidth 固定為已驗證的 320 MHz。

### 四點功率掃描 HIL 入口

探索已確認 -60 dBm 回傳 `INV`；候選入口固定 6105 MHz、320 MHz、expected power -20 dBm，依序量測 -55、-50、-45、-40 dBm。從最低有效功率往上執行，且不接受任意 RF 參數。每點完整 SingleShot 後 STOP／RF Off；無效結果、error queue 或 cleanup 異常立即停止。

只有當次重新確認 RF1.1 → RF1.5 單一 cable 直連、無衰減器且操作員在儀器旁，才可執行：

```powershell
python scripts\cmp180_power_sweep_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present `
  --confirm-four-point-power-sweep
```

未帶齊三個確認旗標時，程式會在連線與送出 SCPI 前拒絕。完整與部分結果都保存 CSV、JSON、metadata、raw responses 與 HTML。

### 十點功率掃描 HIL 入口（已備妥腳本，尚未實機執行）

在已知有效的區間內加密解析度：固定 6105 MHz、320 MHz、expected power -20 dBm，
從 -58 dBm 開始以 2 dB step 量到 -40 dBm 共 10 點。刻意不含 -60 dBm——
2026-08-20 已兩度確認 -60 dBm 在目前 expected power／trigger 設定下回傳 `INV`，
而 `power_sweep.py` 在第一個無效點就會整批停止，若把 -60 dBm 放在起點會讓其餘
9 點完全跑不到，浪費一次上機時間。

```powershell
python scripts\cmp180_power_sweep_dense_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present `
  --confirm-ten-point-power-sweep
```

尚未在實機執行；執行後請把結果（含 partial/失敗點）補進
`docs/hardware-discovery.md` 才能視為完成 HIL。

### 兩者共通規則

- 每一點都執行完整 SingleShot，並在換頻／換功率前 STOP measurement 與 RF Off。
- 任一點失敗即停止後續點，保存先前成功點與失敗的頻率／功率。
- EVM、Burst Power、Frequency Error 必須為有限數值；`INV` 即使 error queue 空也視為失敗。
- 所有設定必須在第一個 SCPI 指令前完成驗證。
- 頻率／功率上下限、span 與最大點數是程式內硬性上限；呼叫端只能縮小，不能放寬。

### 尚待完成

1. 執行 `cmp180_frequency_sweep_wide_validate.py`（11 點／200 MHz span）與
   `cmp180_power_sweep_dense_validate.py`（10 點／2 dB step）兩批新腳本的實機
   HIL，並把結果補進 `docs/hardware-discovery.md`。
2. 以實機失敗案例驗證 partial-result CSV／JSON metadata；程式與 unit test 已完成。
3. 設計 Web 掃頻的 progress、cancel 與獨立 emergency cleanup，再做安全審查。
4. Web 實機掃頻必須另行驗證，不因 CLI 批次 HIL 通過而自動解鎖；`real_service.py`
   目前仍只重播固定的三點／四點 profile，尚未接受新批次的頻率／功率範圍。
5. 若要涵蓋整個 5925–7125 MHz，需要規劃多段各自 ≤200 MHz span 的掃描（目前
   11 點批次只涵蓋 6005–6205 MHz），不能靠單一掃描一次涵蓋全部範圍。

## English Version

### Current status

The Python core and mock tests for both safe short sweeps (frequency and power) are implemented, but neither has a Web hardware button yet. The fixed three-point frequency sweep, immediate-stop-on-`INV` power behavior, and the -55 through -40 dBm four-point numeric power batch have all passed CLI hardware HIL. Scripts for an 11-point/200 MHz-span frequency sweep and a 10-point/2 dB-step power sweep are ready but not yet run on hardware. Web sweeps remain mock-only and require separate acceptance before unlock.

### Three-point frequency-sweep HIL entry point

The first hardware entry point is fixed to RF1.1 to RF1.5, 6085/6105/6125 MHz, 320 MHz, -40 dBm, -20 dBm expected power, and 100 ms dwell. It accepts no arbitrary RF parameters. Every point runs a complete SingleShot and performs STOP plus RF Off before the next point. An outer `finally` performs emergency STOP/ABORt, RF Off, final-state read-back, and error-queue read-back.

Run it only after reconfirming the single direct cable and that the operator is beside the instrument for the current session:

```powershell
python scripts\cmp180_frequency_sweep_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present `
  --confirm-three-point-sweep
```

Without all three flags, the program refuses before connecting or sending SCPI. Complete and partial runs save CSV, JSON, metadata, raw responses, and HTML under `output\<run-id>\`. Partial metadata records the successful point count, failed frequency, and error.

### Eleven-point frequency-sweep HIL entry point (script ready, not yet run on hardware)

Extends the three-point batch to the largest single sweep the safety envelope in
`frequency_sweep.py` allows: 11 points spanning 200 MHz, centered symmetrically on
the already-verified 6105 MHz at 6005/6025/6045/6065/6085/6105/6125/6145/6165/
6185/6205 MHz. All other settings (RF1.1 to RF1.5, 320 MHz, -40 dBm, -20 dBm
expected power, 100 ms dwell) match the three-point batch. This only closes the
gap between "verified" and the existing hard ceiling — no safety constant changes.

```powershell
python scripts\cmp180_frequency_sweep_wide_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present `
  --confirm-eleven-point-sweep
```

Not yet run on real hardware. After running it, record the results (including any
partial run or failed point) in `docs/hardware-discovery.md` before treating this
as completed HIL.

### Frequency sweep safety envelope

- Routing: verified RF1.1 to RF1.5 only.
- Frequency: 5925–7125 MHz.
- Maximum span: 200 MHz.
- Maximum point count: 11.
- Generator power: no higher than -40 dBm.
- Bandwidth: fixed at the verified 320 MHz.
- Dwell: 100–2000 ms.

### Power sweep safety envelope

- Routing: verified RF1.1 to RF1.5 only.
- Generator power: -60 to -40 dBm.
- Maximum point count: 11.
- Dwell: 100–2000 ms.
- Frequency fixed at a single verified value (currently 6105 MHz).
- Bandwidth fixed at the verified 320 MHz.

### Four-point power-sweep HIL entry point

Exploration confirmed that -60 dBm returns `INV`. The candidate entry point is fixed to 6105 MHz, 320 MHz, -20 dBm expected power, and the sequence -55, -50, -45, and -40 dBm. It starts at the lowest valid power and accepts no arbitrary RF parameters. Every point performs a complete SingleShot followed by STOP/RF Off. Any invalid result, error-queue error, or cleanup error stops the run before power can increase.

Run only after reconfirming, for the current session, the single direct RF1.1-to-RF1.5 cable, no attenuator, and operator presence beside the instrument:

```powershell
python scripts\cmp180_power_sweep_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present `
  --confirm-four-point-power-sweep
```

Without all three flags, the program refuses before connecting or sending SCPI. Complete and partial runs save CSV, JSON, metadata, raw responses, and HTML.

### Ten-point power-sweep HIL entry point (script ready, not yet run on hardware)

Adds resolution inside the already-known-valid range: fixed at 6105 MHz, 320 MHz,
-20 dBm expected power, stepping 2 dB from -58 dBm up to -40 dBm (10 points).
Deliberately excludes -60 dBm — it was confirmed twice on 2026-08-20 to return
`INV` under the current expected-power/trigger configuration, and
`power_sweep.py` stops the entire sweep at the first invalid point, so starting
at -60 dBm would prevent all nine other points from running.

```powershell
python scripts\cmp180_power_sweep_dense_validate.py `
  --confirm-direct-cable `
  --confirm-operator-present `
  --confirm-ten-point-power-sweep
```

Not yet run on real hardware. After running it, record the results (including any
partial run or failed point) in `docs/hardware-discovery.md` before treating this
as completed HIL.

### Rules shared by both

- Every point runs a complete SingleShot and performs measurement STOP plus RF Off before changing frequency/power.
- The sweep stops on the first failed point and preserves earlier successful points plus the failed frequency/power.
- EVM, Burst Power, and Frequency Error must be finite numeric values. `INV` fails even when the error queue is empty.
- Every setting is validated before the first SCPI command.
- Frequency/power bounds, span, and point count are hard-coded ceilings. Callers may
  narrow them but cannot relax them.

### Remaining work

1. Run the two new batches on real hardware — `cmp180_frequency_sweep_wide_validate.py`
   (11 points / 200 MHz span) and `cmp180_power_sweep_dense_validate.py`
   (10 points / 2 dB step) — and record the results in `docs/hardware-discovery.md`.
2. Validate partial-result CSV/JSON metadata with a live failure case; implementation and unit tests are complete.
3. Design Web sweep progress, cancellation, and independent emergency cleanup, then perform a safety review.
4. Validate the Web hardware sweep separately; CLI batch HIL does not automatically
   unlock it. `real_service.py` still only replays the fixed three-point/four-point
   profiles and does not yet accept the new batches' frequency/power ranges.
5. Covering the full 5925–7125 MHz range needs several separate sweeps, each
   ≤200 MHz span (the current 11-point batch only covers 6005–6205 MHz) — it
   cannot be done in one continuous sweep under the existing span ceiling.
