# Path Loss、DUT 與 UDBox 現場 HIL 執行計畫

## 繁體中文

### 目前狀態

本文件保留為歷史參考，不是目前 DUT／UDBox 下一步需求。目前需求已收斂為
「能執行 DUT／UDBox 量測並產生 artifacts」，不要求建立獨立 route、Path Loss 追溯、
三階段 HIL gate、Go／No-Go 驗證或 profile approval。實作時請改依
`docs/dut-udbox-measurement-spec.md`。

### 目前唯讀安全快照

2026-09-03 已完成 query-only preflight，沒有啟動量測或傳送 RF：TCP 5025 經乙太網路
可達；儀器為 R&S CMP、firmware `6.0.50.23`，error queue 空。WLAN MEAS1 為 `RDY`、
RF1.5、external attenuation 0 dB、EHT／BW320／B6GH／6105 MHz／Channel 31、IF Power
trigger -45 dB、timeout 1 s、expected nominal power -20 dBm、SingleShot／statistic count 10。
序號不寫入本文件。

這只證明連線與目前量測設定可讀，不證明 Generator RF 已關閉，也不構成 Path Loss、DUT
或 UDBox 的 RF 執行授權。進入 RF 前仍須另外讀回 Generator state。

### 尚缺資料

以下任一資料未填即保持 `BLOCKED`：

- 校正設備 vendor、完整 model、asset ID、serial、firmware、校正證書與到期日。
- source／receiver reference plane、量測方向與功率單位。
- cable／adapter／attenuator asset ID、方向、額定功率與接線圖。
- 校正 route、2–11 個 frequency points 與最低安全起始功率。
- DUT 型號、供電、connector、預期／最大輸出、band／bandwidth／MCS。
- UDBox 型號、port mapping、switch state、額外 loss 與控制方式。
- RF owner、核准日期與 route／frequency／power envelope。
- 現場操作員與 emergency stop 方法。

### Phase A：正式 Path Loss

1. 登錄設備／線材識別與有效證書，明確定義兩端 reference plane。
2. 使用校正過的 reference source／receiver 取得
   `frequency_hz,source_reference_dbm,receiver_reading_dbm`；CMP180 自我量測只能稱為相對驗證。
3. 從最低安全功率開始；overload、timeout、error queue 或 cleanup 異常立即停止。
4. 用 `scripts/cmp180_calibration_profile.py` 產生 Draft；負 loss、超過 30 dB、重複／倒序
   頻率與外插一律拒絕。
5. RF owner 審查曲線、outlier、reference plane、設備與日期後，才填證據／核准欄位並轉
   Approved。
6. 用 Approved Profile 跑一個低功率 reference point，保存 profile snapshot、readback、
   raw response、error queue 與 final RF/output state。

### Phase B：DUT HIL

1. 建立 DUT 專用 route ID 與 Calibration Profile，不沿用 direct-loopback profile。
2. 計算 `analyzer_input_dbm = dut_output_dbm - path_loss_db`，低於 Analyzer soft limit 並保留
   至少 3 dB margin；不確定時加入已知且已校正的 attenuator。
3. 先做 RF-Off readback，再以最低安全 DUT output 執行單一 SingleShot。
4. 只有 reliability=0、critical metrics finite、error queue empty、cleanup 正常時，才能做
   最多三點的 bounded sweep；第一個 `INV`／overload／timeout 立即停止。
5. 沒有 DUT-specific Approved Limit 時只標 `MEASURED`，不得宣稱 PASS。

### Phase C：UDBox HIL

1. 把每條 UDBox path 視為新 route，記錄 port mapping、switch state、方向、loss 與控制版本。
2. 每條 path 建立獨立 Calibration Profile，不複製 RF1.1→RF1.5 數值。
3. 切換前確認 Generator RF Off、measurement idle；切換後重新 readback。
4. 先跑低功率 reference point，再做最多三點 sweep；Pause／Stop／切 path 僅在 RF-Off
   point boundary 生效。
5. 失敗時保存 partial artifacts，並在 `finally` 嘗試 CMP180 RF Off、STOP／ABORT、
   UDBox safe state／output off 與 session close。

### Go／No-Go

只有以下全部為 Yes 才能送 RF：

- [ ] Generator query 為 `OFF`，measurement 為 `OFF` 或 `RDY`，error queue 空。
- [ ] 實際 route 與 diagram／Approved Calibration Profile 完全一致且未過期。
- [ ] frequency、bandwidth、waveform／MCS 已確認。
- [ ] source/DUT power、path loss、attenuator、Analyzer input／maximum input 已計算。
- [ ] RF owner 已核准本次 envelope，操作員在場並知道 emergency stop。
- [ ] output/RF cleanup 可獨立執行。

任一項為 No 或 Unknown：維持 `BLOCKED`。目前下一步是取得上述現場資料，建立 Draft
route inventory／Calibration Profile，完成 Mock／validation，再於同一現場時段重新做
Go／No-Go。資料未齊前不執行 RF pulse、calibration capture、DUT 或 UDBox HIL。

---

## English Version

### Current query-only snapshot

On 2026-09-03, query-only preflight succeeded without starting a measurement or transmitting
RF. Ethernet TCP 5025 was reachable; the instrument was an R&S CMP with firmware 6.0.50.23;
the error queue was empty. WLAN MEAS1 reported `RDY`, RF1.5, zero external attenuation,
EHT/BW320/B6GH at 6105 MHz/channel 31, IF Power triggering at -45 dB with a one-second timeout,
-20 dBm expected nominal power, and SingleShot/statistic count 10. The serial is omitted.

This proves only that connection and measurement settings are readable. Generator RF state
was not verified, so it does not authorize Path Loss, DUT, or UDBox RF execution.

### Required inputs and phases

Work remains `BLOCKED` until calibrated-equipment identity/certificate/expiry, reference planes,
cable/adapter/attenuator identity and direction, calibration route and points, DUT output limits,
UDBox port mapping and loss, RF-owner approval, operator presence, and emergency-stop method are
recorded.

Phase A uses a calibrated source/receiver to capture 2–11 rows of
`frequency_hz,source_reference_dbm,receiver_reading_dbm`, starting at the lowest safe power. The
existing script creates a Draft and rejects negative or above-30-dB loss, invalid ordering, and
extrapolation. Only the RF owner may approve it after reviewing evidence and reference planes.

Phase B creates a DUT-specific route/profile, calculates worst-case Analyzer input with at least
3 dB margin, and starts with one lowest-power SingleShot. Only reliability zero, finite metrics,
an empty error queue, and correct cleanup permit a maximum three-point sweep. Without a
DUT-specific Approved Limit, results remain `MEASURED`.

Phase C treats every UDBox path as a separate route/profile. Switching occurs only while RF is
Off and measurement is idle, followed by readback, one low-power reference point, and at most
three sweep points. Failure preserves partial artifacts and triggers CMP180/UDBox cleanup.

RF is allowed only when Generator Off, measurement Off/Ready, empty error queue, exact approved
route, frequency/bandwidth/waveform, power/loss/input calculations, current calibration, owner
approval, operator presence, and independent cleanup are all confirmed. Any No or Unknown keeps
the case blocked. The next action is to collect these inputs, create Draft route/profile files,
run Mock/validation, and repeat same-session go/no-go. No RF HIL runs before that.
