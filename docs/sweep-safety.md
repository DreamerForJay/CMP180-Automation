# 安全短掃頻規格 / Safe Short Frequency Sweep Specification

## 中文版本

### 目前狀態

安全短掃頻的 Python 核心與 Mock 測試已完成，但尚未開放 Web 實機按鈕。實機啟用前必須在操作員與 CMP180 旁完成受控 HIL 驗證。現在的 Web「頻率掃描」仍是 Mock；它可驗證輸入、CSV／JSON、表格與 EVM／Power／Frequency Error 圖表，不會產生 RF。

### 第一版安全範圍

- Routing：只允許已驗證的 RF1.1 → RF1.5。
- 頻率：5925–7125 MHz。
- 最大 span：200 MHz。
- 最大點數：11 點。
- Generator power：不得高於 -40 dBm。
- Dwell：100–2000 ms。
- 每一點都執行完整 SingleShot，並在換頻前 STOP measurement 與 RF Off。
- 任一點失敗即停止後續點，保存先前成功點與失敗頻率。
- 所有設定必須在第一個 SCPI 指令前完成驗證。

### 尚待完成

1. 用 3 點低功率範例完成實機 HIL：6085、6105、6125 MHz。
2. 驗證各點 Generator／Analyzer read-back、error queue 與最終 RF OFF。
3. 將 partial result 寫入正式 CSV／JSON metadata。
4. 通過 HIL 後才在 Web GUI 加入實機短掃頻執行按鈕、進度與取消。

## English Version

### Current status

The Python core and mock tests for a safe short sweep are implemented, but the Web hardware button remains unavailable. Controlled HIL validation beside the CMP180 and an operator is required before enabling it. The current Web Frequency Sweep screen remains mock-only; it validates inputs, CSV/JSON, tables, and EVM/Power/Frequency Error charts without producing RF.

### Initial safety envelope

- Routing: verified RF1.1 to RF1.5 only.
- Frequency: 5925–7125 MHz.
- Maximum span: 200 MHz.
- Maximum point count: 11.
- Generator power: no higher than -40 dBm.
- Dwell: 100–2000 ms.
- Every point runs a complete SingleShot and performs measurement STOP plus RF Off before changing frequency.
- The sweep stops on the first failed point and preserves earlier successful points plus the failed frequency.
- Every setting is validated before the first SCPI command.

### Remaining work

1. Perform a controlled three-point low-power HIL run at 6085, 6105, and 6125 MHz.
2. Verify Generator/Analyzer read-back, error queue, and final RF OFF at every point.
3. Persist partial results in the production CSV/JSON metadata.
4. Enable the Web hardware sweep button, progress, and cancellation only after HIL passes.
