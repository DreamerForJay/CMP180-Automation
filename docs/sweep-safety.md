# 安全短掃描規格 / Safe Short Sweep Specification

## 中文版本

### 目前狀態

安全短掃描（頻率掃描與功率掃描）的 Python 核心與 Mock 測試都已完成，但都尚未開放 Web 實機按鈕。固定三點頻率掃描、功率掃描 `INV` 立即停止，以及 -55 至 -40 dBm 四點有效功率批次皆已完成 CLI 實機 HIL。Web 掃描仍是 Mock，需獨立驗收後才可解鎖。

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

### 兩者共通規則

- 每一點都執行完整 SingleShot，並在換頻／換功率前 STOP measurement 與 RF Off。
- 任一點失敗即停止後續點，保存先前成功點與失敗的頻率／功率。
- EVM、Burst Power、Frequency Error 必須為有限數值；`INV` 即使 error queue 空也視為失敗。
- 所有設定必須在第一個 SCPI 指令前完成驗證。
- 頻率／功率上下限、span 與最大點數是程式內硬性上限；呼叫端只能縮小，不能放寬。

### 尚待完成

1. 功率掃描：用固定頻率、多組低功率點完成實機 HIL。
2. 以實機失敗案例驗證 partial-result CSV／JSON metadata；程式與 unit test 已完成。
3. 設計 Web 掃頻的 progress、cancel 與獨立 emergency cleanup，再做安全審查。
4. Web 實機掃頻必須另行驗證，不因 CLI 三點 HIL 通過而自動解鎖。

## English Version

### Current status

The Python core and mock tests for both safe short sweeps (frequency and power) are implemented, but neither has a Web hardware button yet. The fixed three-point frequency sweep, immediate-stop-on-`INV` power behavior, and the -55 through -40 dBm four-point numeric power batch have all passed CLI hardware HIL. Web sweeps remain mock-only and require separate acceptance before unlock.

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

### Rules shared by both

- Every point runs a complete SingleShot and performs measurement STOP plus RF Off before changing frequency/power.
- The sweep stops on the first failed point and preserves earlier successful points plus the failed frequency/power.
- EVM, Burst Power, and Frequency Error must be finite numeric values. `INV` fails even when the error queue is empty.
- Every setting is validated before the first SCPI command.
- Frequency/power bounds, span, and point count are hard-coded ceilings. Callers may
  narrow them but cannot relax them.

### Remaining work

1. Power sweep: perform a controlled HIL run across several low-power levels at a fixed frequency.
2. Validate partial-result CSV/JSON metadata with a live failure case; implementation and unit tests are complete.
3. Design Web sweep progress, cancellation, and independent emergency cleanup, then perform a safety review.
4. Validate the Web hardware sweep separately; the CLI three-point HIL does not automatically unlock it.
