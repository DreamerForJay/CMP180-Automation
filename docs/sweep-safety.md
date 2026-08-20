# 安全短掃描規格 / Safe Short Sweep Specification

## 中文版本

### 目前狀態

安全短掃描（頻率掃描與功率掃描）的 Python 核心與 Mock 測試都已完成，但都尚未開放 Web 實機按鈕。頻率掃描已有固定三點的 CLI HIL 入口與 partial-result artifacts；尚未完成實機執行。實機啟用前必須在操作員與 CMP180 旁完成受控 HIL 驗證。現在的 Web「頻率掃描」與「功率掃描」都仍是 Mock；可驗證輸入、CSV／JSON、表格與 EVM／Power／Frequency Error 圖表，不會產生 RF。

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

### 兩者共通規則

- 每一點都執行完整 SingleShot，並在換頻／換功率前 STOP measurement 與 RF Off。
- 任一點失敗即停止後續點，保存先前成功點與失敗的頻率／功率。
- 所有設定必須在第一個 SCPI 指令前完成驗證。
- 頻率／功率上下限、span 與最大點數是程式內硬性上限；呼叫端只能縮小，不能放寬。

### 尚待完成

1. 頻率掃描：用 3 點低功率範例完成實機 HIL（6085、6105、6125 MHz）。
2. 功率掃描：用固定頻率、多組低功率點完成實機 HIL。
3. 兩者都要驗證各點 Generator／Analyzer read-back、error queue 與最終 RF OFF。
4. 以實機失敗案例驗證 partial-result CSV／JSON metadata；程式與 unit test 已完成。
5. 通過 HIL 後才在 Web GUI 加入對應的實機短掃描執行按鈕、進度與取消。

## English Version

### Current status

The Python core and mock tests for both safe short sweeps (frequency and power) are implemented, but neither has a Web hardware button yet. Frequency sweep now has a fixed three-point CLI HIL entry point and partial-result artifacts; the live run has not yet been performed. Controlled HIL validation beside the CMP180 and an operator is required before enabling either one. The current Web Frequency Sweep and Power Sweep screens remain mock-only; they validate inputs, CSV/JSON, tables, and EVM/Power/Frequency Error charts without producing RF.

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

### Rules shared by both

- Every point runs a complete SingleShot and performs measurement STOP plus RF Off before changing frequency/power.
- The sweep stops on the first failed point and preserves earlier successful points plus the failed frequency/power.
- Every setting is validated before the first SCPI command.
- Frequency/power bounds, span, and point count are hard-coded ceilings. Callers may
  narrow them but cannot relax them.

### Remaining work

1. Frequency sweep: perform a controlled three-point low-power HIL run at 6085, 6105, and 6125 MHz.
2. Power sweep: perform a controlled HIL run across several low-power levels at a fixed frequency.
3. Both: verify Generator/Analyzer read-back, error queue, and final RF OFF at every point.
4. Validate partial-result CSV/JSON metadata with a live failure case; implementation and unit tests are complete.
5. Enable each Web hardware sweep button, progress, and cancellation only after its own HIL passes.
