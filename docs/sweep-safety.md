# 安全短掃描規格 / Safe Short Sweep Specification

## 中文版本

### 目前狀態

安全短掃描（頻率掃描與功率掃描）的 Python 核心與 Mock 測試都已完成，但都尚未開放 Web 實機按鈕。實機啟用前必須在操作員與 CMP180 旁完成受控 HIL 驗證。現在的 Web「頻率掃描」與「功率掃描」都仍是 Mock；可驗證輸入、CSV／JSON、表格與 EVM／Power／Frequency Error 圖表，不會產生 RF。

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
4. 將 partial result 寫入正式 CSV／JSON metadata。
5. 通過 HIL 後才在 Web GUI 加入對應的實機短掃描執行按鈕、進度與取消。

## English Version

### Current status

The Python core and mock tests for both safe short sweeps (frequency and power) are implemented, but neither has a Web hardware button yet. Controlled HIL validation beside the CMP180 and an operator is required before enabling either one. The current Web Frequency Sweep and Power Sweep screens remain mock-only; they validate inputs, CSV/JSON, tables, and EVM/Power/Frequency Error charts without producing RF.

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
4. Persist partial results in the production CSV/JSON metadata.
5. Enable each Web hardware sweep button, progress, and cancellation only after its own HIL passes.
