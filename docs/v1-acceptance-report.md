# CMP180 WLAN EVM V1 驗收報告

## 繁體中文

### 結論

V1 軟體與 RF1.1 → RF1.5 loopback 的 WLAN HIL 核心能力已完成；正式產品簽核狀態目前為 `BLOCKED`，不是因為量測流程失敗，而是 Calibration Profile 與 Limit Profile 仍為 `draft`。在 RF／Test Owner 補齊可追溯來源與核准欄位前，不得宣稱 DUT compliance PASS。

### 已通過範圍

- 完整 Python SingleShot、Frequency Sweep、Power Sweep、28 欄 OFDM SISO 結果與 deterministic cleanup。
- 2.4／5／6 GHz 的 11 個合法 WLAN band／bandwidth 區段，共 176/176 channel-center 點有效。
- 320 MHz 5925–7125 MHz 共 49/49 點，以及 -55 至 -30 dBm 共 26/26 點。
- 2026-09-02 四點 Power Sweep 4/4 有效；最終 RF `OFF`、measurement `RDY`、error queue empty。
- Web 單點／掃描、Pause／Resume／Stop、歷史單一 Run 圖表與 2–8 Run 唯讀比較。

### 尚待簽核

1. 以校正過的外部 Source／Receiver 或有效證書取得 path-loss 讀值，記錄線材、轉接頭、參考面與設備編號。
2. 由 RF Owner 在 Calibration Profile 填寫 `source_evidence`、`approved_by`、`approved_at`，並建立不可變 revision。
3. 由 Test Owner 指定適用 DUT／standard／bandwidth／MCS 的限制來源，在 Limit Profile 填寫 `source_reference`、`approved_by`、`approved_at`。
4. 執行離線 acceptance builder；只有所有 gate 都是 `PASS` 時才會輸出 `ACCEPTED`。
   報告一律保持 `compliance_claim=false`：驗收通過代表「V1 交付可簽核」，
   不等於對 DUT 的正式合規宣告，該宣告仍屬 RF／測試負責人的權責。

```powershell
python -m cmp180_evm validate-calibration configs\calibration.example.yaml
python -m cmp180_evm validate-limits configs\limits.example.yaml
python scripts\build_v1_acceptance.py `
  --calibration path\to\approved-calibration.yaml `
  --limits path\to\approved-limits.yaml `
  --evidence output\<real-single-run> `
  --evidence output\<real-frequency-run> `
  --evidence output\<real-power-run>
```

Acceptance builder 只讀取 Profile 與 artifacts，不連線 CMP180、不送 RF。Mock、partial、failed、空結果或含 invalid 點的 run 都不能通過 HIL gate。

---

## English

### Conclusion

The V1 software and core WLAN HIL capability for the RF1.1-to-RF1.5 loopback are complete. Formal product acceptance is currently `BLOCKED`, not because the measurement workflow failed, but because the Calibration and Limit Profiles remain `draft`. No DUT compliance PASS may be claimed until the RF/test owner supplies traceable sources and approval fields.

### Accepted scope

- Complete Python SingleShot, Frequency Sweep, Power Sweep, 28-field OFDM SISO results, and deterministic cleanup.
- All 11 legal WLAN band/bandwidth sections across 2.4, 5, and 6 GHz, totaling 176/176 valid channel-center points.
- A 49/49-point 320 MHz sweep from 5925 to 7125 MHz and a 26/26-point sweep from -55 to -30 dBm.
- A fresh four-point Power Sweep with 4/4 valid points on 2026-09-02; final RF `OFF`, measurement `RDY`, and an empty error queue.
- Web single/sweep operation, Pause/Resume/Stop, single historical-run plotting, and read-only comparison of 2–8 runs.

### Approvals still required

1. Obtain path-loss readings from a calibrated external source/receiver or a valid certificate, recording cable, adapter, reference-plane, and equipment identities.
2. Have the RF Owner fill `source_evidence`, `approved_by`, and `approved_at` in an immutable Calibration Profile revision.
3. Have the Test Owner identify the applicable DUT/standard/bandwidth/MCS specification source and fill `source_reference`, `approved_by`, and `approved_at` in the Limit Profile.
4. Run the offline acceptance builder. It emits `ACCEPTED` only when every gate passes.
   The report always keeps `compliance_claim=false`: acceptance means the V1 delivery is
   ready to sign off, not that the tool makes a formal compliance claim about a DUT, which
   remains the RF/test owner's responsibility.

Use the PowerShell command shown in the Chinese section. The acceptance builder only reads Profiles and artifacts; it never connects to the CMP180 or transmits RF. Mock, partial, failed, empty, or invalid-point runs cannot pass the HIL gate.
