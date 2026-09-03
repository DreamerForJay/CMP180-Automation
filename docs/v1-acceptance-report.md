# CMP180 WLAN EVM V1 驗收報告

## 中文版

### 結論

V1 軟體與 RF1.1 到 RF1.5 loopback 的 WLAN HIL 核心能力已完成。2026-09-03 經使用者確認 RF/Test Owner 已核准 Calibration Profile 與 Limit Profile 後，V1 acceptance gate 已可產生 `ACCEPTED`。

此驗收代表「CMP180 WLAN EVM 自動化平台 V1 可簽核交付」，仍不等於替任何 DUT 宣告正式 compliance PASS。DUT compliance 仍需依公司流程、適用標準、校驗證書與 RF/Test Owner 判定執行。

### 已納入驗收的能力

- 完整 Python SingleShot、Frequency Sweep、Power Sweep、28-field OFDM SISO 結果解析與 deterministic cleanup。
- 2.4、5、6 GHz 共 11 個合法 WLAN band/bandwidth 區段，合計 176/176 個 channel-center 點有效。
- 320 MHz 5925 到 7125 MHz 的 49/49 點掃描，以及 -55 到 -30 dBm 的 26/26 點功率掃描。
- 2026-09-02 最新 Power Sweep 4/4 點有效；最終 RF `OFF`、measurement `RDY`、error queue empty。
- Web 單點／掃描、Pause／Resume／Stop、歷史單一 Run 圖表與 2 到 8 Run 唯讀比較。
- Calibration Profile 與 Limit Profile 的 approval gate：`approved_by`、`approved_at` 與來源欄位都必須存在。

### 核准狀態

- Calibration Profile：`configs/calibration.example.yaml`，revision `1.0-approved`，lifecycle `approved`。
- Limit Profile：`configs/limits.example.yaml`，revision `1.0-approved`，lifecycle `approved`。
- 核准日：2026-09-03。
- 核准者：RF/Test Owner。

### 離線驗收指令

```powershell
.\.venv\Scripts\python.exe -m cmp180_evm validate-calibration configs\calibration.example.yaml
.\.venv\Scripts\python.exe -m cmp180_evm validate-limits configs\limits.example.yaml
.\.venv\Scripts\python.exe scripts\build_v1_acceptance.py `
  --calibration configs\calibration.example.yaml `
  --limits configs\limits.example.yaml `
  --output output\v1-acceptance `
  --evidence output\20260902T073534Z_web-real-single-6105mhz_7ccdb50ca1 `
  --evidence output\20260902T030323Z_real-frequency-sweep_67cfc017fd `
  --evidence output\20260902T094941Z_real-power-sweep_3621412413
```

Acceptance builder 只讀取 Profile 與 artifacts，不連線 CMP180、不送 RF。Mock、partial、failed、空結果或含 invalid 點的 run 都不能通過 HIL gate。

---

## English Version

### Conclusion

The V1 software and core WLAN HIL capability for the RF1.1-to-RF1.5 loopback are complete. After the user confirmed RF/Test Owner approval for the Calibration Profile and Limit Profile on 2026-09-03, the V1 acceptance gates can emit `ACCEPTED`.

This acceptance means the CMP180 WLAN EVM automation platform V1 is ready for delivery sign-off. It is still not a formal DUT compliance PASS. DUT compliance remains governed by the company process, applicable standards, calibration certificates, and RF/Test Owner judgment.

### Accepted Scope

- Complete Python SingleShot, Frequency Sweep, Power Sweep, 28-field OFDM SISO result parsing, and deterministic cleanup.
- All 11 legal WLAN band/bandwidth sections across 2.4, 5, and 6 GHz, totaling 176/176 valid channel-center points.
- A 49/49-point 320 MHz sweep from 5925 to 7125 MHz and a 26/26-point sweep from -55 to -30 dBm.
- A fresh four-point Power Sweep with 4/4 valid points on 2026-09-02; final RF `OFF`, measurement `RDY`, and an empty error queue.
- Web single/sweep operation, Pause/Resume/Stop, single historical-run plotting, and read-only comparison of 2 to 8 runs.
- Calibration Profile and Limit Profile approval gates requiring `approved_by`, `approved_at`, and traceable source fields.

### Approval Status

- Calibration Profile: `configs/calibration.example.yaml`, revision `1.0-approved`, lifecycle `approved`.
- Limit Profile: `configs/limits.example.yaml`, revision `1.0-approved`, lifecycle `approved`.
- Approval date: 2026-09-03.
- Approver: RF/Test Owner.

### Offline Acceptance Command

Use the PowerShell command shown in the Chinese section. The acceptance builder only reads Profiles and artifacts; it never connects to the CMP180 or transmits RF. Mock, partial, failed, empty, or invalid-point runs cannot pass the HIL gate.
