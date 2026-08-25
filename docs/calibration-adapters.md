# Calibration Instrument Adapter 規格

## 中文版本

### 目的與邊界

Adapter 將不同品牌校正儀器的連線與 SCPI 差異隔離在量測核心之外。每個 Adapter 必須提供
連線、儀器識別、單頻點讀值、輸出關閉與 session 關閉。共用 controller 負責 6 GHz 頻率、
-80 至 -40 dBm、2 至 11 點等硬性限制，並在成功或例外時以 `finally` 關閉輸出。

目前只有 `mock-reference` 可用。它是純軟體 DEMO，不連接儀器、不產生 RF，也不得作為正式
Calibration Profile。`external-scpi` 只顯示未設定狀態，直到型號、resource address、官方
SCPI、輸出限制及參考面定義都經確認後才可實作。

### Web 操作

1. 在「校正 SOP」選擇 Adapter。
2. 選擇 DEMO Adapter 時，必須再次確認它不是正式校正資料。
3. 按「從儀器擷取」後，Web 透過 Adapter API 取得 CSV schema 相同的讀值。
4. 頁面顯示最終輸出狀態；接著仍須按「計算 Draft Profile」並交由 Owner 審查。
5. 尚未設定的真實 Adapter 不能選取，也不會送出 SCPI。

### 新增真實 Adapter 所需資料

- 品牌、完整型號、韌體版本與已安裝選件。
- VISA/TCP Socket/USB/GPIB resource address。
- 官方 programming manual 與所需 SCPI。
- Source／Receiver 參考面、線材方向與功率單位。
- 儀器輸出與輸入安全限制、timeout、trigger 與錯誤佇列行為。
- 資產編號、校正證書與有效期限管理方式。

真實 Adapter 必須新增 Mock 單元測試、失敗 cleanup 測試、query-only discovery，以及現場低功率
HIL。HIL 完成前，registry 中的 `available` 必須維持 `false`。

---

## English Version

### Purpose and boundary

Adapters isolate vendor-specific connection and SCPI behavior from the calibration core. Each
adapter must implement connection, identity, single-frequency reading, output-off, and session
close operations. The shared controller enforces the 6 GHz range, -80 to -40 dBm, and 2-to-11
point hard limits, and uses `finally` cleanup to turn output off on success or failure.

Only `mock-reference` is currently available. It is a software-only demo that connects to no
instrument, emits no RF, and cannot support a formal Calibration Profile. `external-scpi`
remains unavailable until model, resource address, official SCPI, output limits, and reference
planes are confirmed.

### Web operation

1. Select an Adapter on the Calibration SOP page.
2. The DEMO adapter requires explicit acknowledgement that its readings are not formal data.
3. Capture from Instrument obtains readings through the Adapter API using the same CSV schema.
4. The page reports final output state; the operator must still calculate a Draft Profile and
   send it for owner review.
5. Unconfigured real adapters cannot be selected and send no SCPI.

### Required information for a real adapter

- Vendor, complete model, firmware version, and installed options.
- VISA/TCP Socket/USB/GPIB resource address.
- Official programming manual and required SCPI.
- Source/receiver reference planes, cable direction, and power units.
- Output/input safety limits, timeout, trigger, and error-queue behavior.
- Asset ID, calibration certificate, and expiry-management rules.

A real adapter requires Mock unit tests, failure-cleanup tests, query-only discovery, and an
on-site low-power HIL. Its registry `available` state must remain `false` until HIL passes.
