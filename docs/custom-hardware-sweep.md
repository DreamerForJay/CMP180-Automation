# 自訂 CMP180 實機掃描 / Custom CMP180 Hardware Sweep

## 中文版本

### 能力狀態

自訂頻率／功率掃描的軟體執行路徑已接通 Web Job、既有 SingleShot backend、取消、
partial artifacts 與 emergency cleanup。目前仍是 **HIL pending**；在完成新的現場驗收前，
不得宣稱任意自訂計畫已通過實機驗證。

### 不可由前端放寬的限制

- 路徑：只允許 RF1.1 → RF1.5 直接線材，無衰減器。
- 頻寬：只允許已驗證的 320 MHz waveform。
- 頻率掃描：5925–7125 MHz、最大 span 200 MHz、最多 11 點、Generator 不高於 -40 dBm。
- 功率掃描：固定 6105 MHz、-60 至 -40 dBm、最多 11 點。
- Dwell：每點 100–2000 ms。
- 每點均執行完整 SingleShot cleanup；`INV`、error queue、逾時或例外立即停止後續點。
- 每批結束再次執行 STOP／ABORT、RF Off 並讀回 RF `OFF` 與 measurement `OFF/RDY`。
- 尚未提供 Approved Calibration Profile，因此目前 metadata 明確記錄 `calibration_applied=false`。

### 雙重啟動閘門

一般硬體模式只開放固定 HIL profile：

```powershell
python -m cmp180_evm.web --host 127.0.0.1 --enable-hardware
```

只有在現場準備執行自訂 HIL 時才使用：

```powershell
python -m cmp180_evm.web --host 127.0.0.1 `
  --enable-hardware `
  --enable-custom-hardware
```

`--enable-custom-hardware` 不能單獨使用，也不能綁定非 loopback 位址。Web 預覽會產生
計畫 fingerprint 與 `EXECUTE-CUSTOM-...` 確認字串；執行 API 會重新驗證所有輸入並重新計算
字串，避免使用者預覽後再修改 request。

### HIL 驗收順序

1. Query-only 確認連線、IDN、RF `OFF`、measurement `RDY`、error queue empty。
2. 操作員確認 RF1.1 仍直接接 RF1.5、無衰減器且人在儀器旁。
3. 先跑最小的 2 點、-45 dBm 頻率掃描。
4. 檢查每點結果、raw、error queue 與最終狀態。
5. 再跑 2 點低功率功率掃描；任一 `INV` 立即停止。
6. 通過後才擴大到既有安全包絡，並更新 HIL 文件與 Profile 狀態。

---

## English Version

### Capability status

The custom frequency/power sweep software path is connected to Web jobs, the existing
SingleShot backend, cancellation, partial artifacts, and emergency cleanup. It remains
**HIL pending**. Do not claim arbitrary custom plans are hardware-verified until the new
on-site acceptance is complete.

### Non-bypassable backend limits

- Route: direct RF1.1-to-RF1.5 cable with no attenuator only.
- Bandwidth: the verified 320 MHz waveform only.
- Frequency sweep: 5925–7125 MHz, 200 MHz maximum span, 11 points maximum, Generator no
  higher than -40 dBm.
- Power sweep: fixed 6105 MHz, -60 to -40 dBm, 11 points maximum.
- Dwell: 100–2000 ms per point.
- Every point uses full SingleShot cleanup. `INV`, error queue entries, timeout, or exception
  stops the remaining points immediately.
- Every batch repeats STOP/ABORT and RF Off, then reads back RF `OFF` and measurement
  `OFF/RDY`.
- No Approved Calibration Profile is supplied yet, so metadata explicitly records
  `calibration_applied=false`.

### Dual startup gate

Normal hardware mode exposes only fixed HIL profiles:

```powershell
python -m cmp180_evm.web --host 127.0.0.1 --enable-hardware
```

Use both flags only during an on-site custom HIL:

```powershell
python -m cmp180_evm.web --host 127.0.0.1 `
  --enable-hardware `
  --enable-custom-hardware
```

The custom flag cannot be used alone or on a non-loopback bind. Preview produces a plan
fingerprint and `EXECUTE-CUSTOM-...` confirmation. Execution revalidates all inputs and
recomputes the confirmation so a request cannot be changed after preview.

### HIL acceptance order

1. Query-only connection, IDN, RF `OFF`, measurement `RDY`, and empty error queue.
2. Operator confirms direct RF1.1-to-RF1.5 cabling, no attenuator, and on-site presence.
3. Run the smallest two-point, -45 dBm frequency sweep first.
4. Check every point, raw data, error queue, and final state.
5. Run a two-point low-power power sweep; stop immediately on any `INV`.
6. Expand only after passing, and update HIL evidence and profile state.
