# CMP180 WLAN EVM V1 Demo 腳本

## 繁體中文

### 目標與時間

此 Demo 約 10–15 分鐘，展示已驗證能力與安全邊界。除非現場已依硬體 SOP 完成接線、授權與 preflight，預設使用 Demo mode 與既有實機 artifacts，不送 RF。

1. **專案定位（1 分鐘）**：說明 CMP180、CMsquares 參考角色、Python/Web 自動化與 RF1.1 → RF1.5 loopback 邊界。
2. **安全與能力矩陣（2 分鐘）**：展示 RF OFF、measurement idle、approved WLAN sections，以及 Mock／HIL／Approved Profile 的差異。
3. **量測流程（3 分鐘）**：以 Demo mode 執行 Single 或短掃描，展示逐點狀態、INVALID 停止、Pause/Stop 與 artifacts。
4. **歷史單筆圖表（2 分鐘）**：在量測紀錄只勾一筆，按「查看所選圖表」，切換 EVM、Burst Power、Frequency Error，展示 Hover、Zoom/Pan 與匯出。
5. **多 Run 比較（2 分鐘）**：勾選 2–8 筆，展示相容性警告、Trace 命名／樣式與 CSV/SVG/PNG 匯出。
6. **校正與限制（2 分鐘）**：展示 Draft Profile、核准必要欄位與 acceptance report；明確說明 Draft 不能形成 compliance PASS。
7. **結論（1 分鐘）**：展示 176/176 HIL 與 V1 尚待 RF/Test Owner 核准的兩個 gate。

Demo 前執行 `scripts\precommit_check.ps1`。若使用實機，必須另依 `docs/hardware-test-sop.md`，不得為了 Demo 略過 final RF summary 或 cleanup。

---

## English

### Goal and timing

This 10–15 minute Demo presents validated capability and safety boundaries. Unless the hardware SOP, cabling, authorization, and preflight are complete on site, use Demo mode and saved live-hardware artifacts without transmitting RF.

1. **Project position (1 minute):** Explain the CMP180, CMsquares as the reference interface, Python/Web automation, and the RF1.1-to-RF1.5 loopback boundary.
2. **Safety and capability matrix (2 minutes):** Show RF OFF, measurement idle, approved WLAN sections, and the distinction among Mock, HIL, and Approved Profiles.
3. **Measurement workflow (3 minutes):** Run a Demo Single or short sweep and show point status, INVALID stop, Pause/Stop, and artifacts.
4. **Single historical plot (2 minutes):** Select one Run History item, choose Plot Selected Run, switch among EVM, Burst Power, and Frequency Error, then show hover, zoom/pan, and export.
5. **Multi-run comparison (2 minutes):** Select 2–8 runs and show compatibility warnings, trace naming/styles, and CSV/SVG/PNG export.
6. **Calibration and limits (2 minutes):** Show Draft Profiles, required approval fields, and the acceptance report. State clearly that Draft cannot produce a compliance PASS.
7. **Conclusion (1 minute):** Show the 176/176 HIL evidence and the two V1 gates still awaiting RF/Test Owner approval.

Run `scripts\precommit_check.ps1` before the Demo. If live hardware is used, also follow `docs/hardware-test-sop.md`; never bypass the final RF summary or cleanup for presentation convenience.
