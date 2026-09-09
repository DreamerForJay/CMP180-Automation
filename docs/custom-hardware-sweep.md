# 自訂 CMP180 實機掃描 / Custom CMP180 Hardware Sweep

## 中文版本

### 能力狀態

自訂頻率／功率掃描的軟體執行路徑已接通 Web Job、既有 SingleShot backend、取消、
partial artifacts 與 emergency cleanup。**HIL／approved profile 已不再作為執行閘門**：
未經實機驗證的頻段、頻寬與功率組合一樣可以量測。但「可以執行」不等於「已通過驗證」，
任何未經 HIL 的結果都不得作為 compliance 或驗收宣稱。

### 仍會阻擋執行的限制（儀器物理能力）

- Port：Generator 與 Analyzer 必須是不同的 RF port。
- 頻率：中心／掃描頻率必須落在 CMP180 400 MHz–8 GHz 調諧範圍。
- 頻寬：必須是已安裝且可解調的 20／40／80／160／320 MHz。
- Dwell：每點 0.01–10 秒。
- 點數：上限 100,000，屬於瀏覽器與 Job 的資源防呆，不是 RF 限制。

### 由操作員負責、軟體不再代為把關的項目

- **Generator 功率上限**：由 request 的 `maximum_generator_power_dbm` 宣告；未指定時
  等於本次要求的功率，即不額外設限。原本寫死的 -30 dBm 保守值已移除，因此
  analyzer 最大輸入準位、線損與衰減器是否足夠，必須由操作員在送 RF 前自行確認。
- **標準 WLAN channel plan 之外的組合**：不再阻擋，只在 preview 與 artifact 標示
  `band_supported` / `standard_wlan_channel=false`。這類點多半會回 INV。
- 每點均執行完整 SingleShot cleanup；`INV`、error queue、逾時或例外立即停止後續點。
- 每批結束再次執行 STOP／ABORT、RF Off 並讀回 RF `OFF` 與 measurement `OFF/RDY`。
- 尚未提供 Approved Calibration Profile，因此目前 metadata 明確記錄 `calibration_applied=false`。

### 啟動與執行閘門

一般本機啟動會提供受保護的實機控制：

```powershell
python -m cmp180_evm.web --host 127.0.0.1 --port 8765
```

純示範模式使用：

```powershell
python -m cmp180_evm.web --host 127.0.0.1 --port 8765 --demo-only
```

啟動服務不會送 RF。規劃介面可輸入 400 MHz–8 GHz 與 WLAN
20／40／80／160／320 MHz 頻寬，但超出 Approved Profile 的計畫只能預覽。Web 預覽會產生
計畫 fingerprint 與確認字串；執行 API 會重新驗證所有輸入並重新計算字串，避免使用者
預覽後再修改 request。實機服務目前仍只允許 loopback 綁定。

### HIL 驗收順序

1. Query-only 確認連線、IDN、RF `OFF`、measurement `RDY`、error queue empty。
2. 操作員確認 RF1.1 仍直接接 RF1.5、無衰減器且人在儀器旁。
3. 先跑最小的 2 點、-45 dBm 頻率掃描。
4. 檢查每點結果、raw、error queue 與最終狀態。
5. 再跑 2 點低功率功率掃描；任一 `INV` 立即停止。
6. 通過後才擴大到既有安全包絡，並更新 HIL 文件與 Profile 狀態。

### 2026-08-25 首次自訂頻率 HIL 結果

- 計畫：6085／6105 MHz、步進 20 MHz、320 MHz、Generator -45 dBm、每點 100 ms。
- Fingerprint：`34F76E0BED46`；Job：`8b385c3eb620`。
- 第 2 點回傳 `INV`，整批依規則停止，不得視為通過。
- 收尾唯讀確認 Generator `OFF`、Analyzer `RDY`，所有查詢的 SCPI error queue 均為
  `0,"No error"`。
- Web 正規化層曾嘗試將 `INV` 轉為浮點數，導致 partial artifact 未完整回傳；修正後
  `INV` 保留於 raw artifact，Web 欄位使用 `null`／`INVALID`，frequency sweep 也會在
  第一個無效關鍵欄位立即停止。
- 找出 -45 dBm 下正確的 trigger／ranging 設定並取得新現場授權前，不得重跑或擴大範圍。

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

### Startup and execution gates

Normal local startup exposes guarded hardware control:

```powershell
python -m cmp180_evm.web --host 127.0.0.1 --port 8765
```

Use Demo-only mode for training without instrument access:

```powershell
python -m cmp180_evm.web --host 127.0.0.1 --port 8765 --demo-only
```

Starting the service does not transmit RF. Planning accepts 400 MHz–8 GHz and WLAN
20/40/80/160/320 MHz bandwidths, while plans outside an Approved Profile remain preview-only.
Preview produces a plan fingerprint and confirmation. Execution revalidates all inputs and
recomputes the confirmation so a request cannot be changed after preview. Hardware service
binding remains loopback-only.

### HIL acceptance order

1. Query-only connection, IDN, RF `OFF`, measurement `RDY`, and empty error queue.
2. Operator confirms direct RF1.1-to-RF1.5 cabling, no attenuator, and on-site presence.
3. Run the smallest two-point, -45 dBm frequency sweep first.
4. Check every point, raw data, error queue, and final state.
5. Run a two-point low-power power sweep; stop immediately on any `INV`.
6. Expand only after passing, and update HIL evidence and profile state.

### First custom-frequency HIL result on 2026-08-25

- Plan: 6085/6105 MHz, 20 MHz step, 320 MHz bandwidth, -45 dBm Generator, and 100 ms
  dwell per point.
- Fingerprint: `34F76E0BED46`; job: `8b385c3eb620`.
- Point 2 returned `INV`; the batch stopped as required and did not pass acceptance.
- Read-only cleanup verification confirmed Generator `OFF`, Analyzer `RDY`, and
  `0,"No error"` for all queried SCPI error queues.
- The Web normalization layer had attempted to convert `INV` to a float, preventing the
  partial artifact from being returned completely. The correction retains `INV` in raw
  artifacts, represents unavailable Web values as `null`/`INVALID`, and stops a frequency
  sweep on the first invalid critical field.
- Do not rerun or expand the range until the correct -45 dBm trigger/ranging settings are
  identified and fresh on-site authorization is provided.
