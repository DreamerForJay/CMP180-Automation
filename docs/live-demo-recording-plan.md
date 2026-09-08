# CMP180 實機成果錄影腳本

## 1. 目的

本文件用來準備實習成果展示影片。錄影重點不是重新證明所有 HIL，而是讓觀眾看懂系統如何安全地完成 CMP180 WLAN TX EVM 自動化量測、保存 artifacts、產生圖表與報告。

若現場沒有 RF owner 核准、接線確認或儀器時段，錄影只能使用 Mock／stored artifacts，不得啟動新的 RF job。

## 2. 建議影片長度

| 版本 | 長度 | 用途 |
|---|---:|---|
| 短版 | 3 到 5 分鐘 | 簡報中插播成果片段 |
| 完整版 | 8 到 12 分鐘 | 期末 Demo 或交接影片 |

## 3. 錄影前檢查

### 必須確認

- CMP180 與筆電網路連線正常。
- RF1.1 → RF1.5 loopback 線路與衰減條件符合 approved profile。
- Generator power、center frequency、bandwidth 與 expected power 均在核准範圍。
- 操作員與 RF owner 已同意這次實機展示。
- 螢幕不顯示序號、license、內部帳號、未公開 IP 清單或敏感 workspace 資訊。
- 已備妥 stored artifacts 作為 RF 無法執行時的備援展示。

### 禁止事項

- 不為了錄影 Reset 儀器或 Workspace。
- 不展示或公開 raw license／activation 資訊。
- 不把 Mock、Preview、stored `FETCh` 說成新的完整實機量測。
- 不在未核准 route、DUT、UDBox 或 power limit 下啟動 RF。

## 4. 推薦錄影流程

### Segment 1：開場與問題

畫面：簡報封面或 Web 首頁。

講稿重點：

- 原本 CMP180 WLAN TX EVM 量測依賴 CMsquares 手動操作。
- 手動流程容易出現設定漂移、資料抄錄錯誤與異常收尾風險。
- 這個專案把量測流程整理成 Python／Web 自動化。

### Segment 2：安全邊界

畫面：`docs/hardware-test-sop.md`、Web 實機頁 preview 區塊、最後確認視窗。

講稿重點：

- RF On 前必須確認 route、frequency、bandwidth、power、expected power 與 operator confirmation。
- 後端只允許 approved/HIL profile 通過的條件。
- 被拒絕的設定只顯示原因與修正範圍，不會送 RF。

### Segment 3：實機量測或備援展示

有 RF 核准時：

- 啟動 Web GUI。
- 選擇已核准的 WLAN EVM SingleShot 或 Loopback baseline。
- 展示 preview 通過、最後確認、job progress 與完成狀態。
- 量測結束後展示 final RF Off、measurement RDY 與 error queue 空。

沒有 RF 核准時：

- 展示既有 run history 與 stored artifacts。
- 說明這些 artifacts 來自已記錄的 HIL 或 stored evidence。
- 不啟動新的 RF job。

### Segment 4：Artifacts 與圖表

畫面：Run History、HTML report、CSV、JSON、metadata、Matplotlib PNG。

講稿重點：

- 每次 run 都保存 raw response 與 normalized results。
- CSV 可做資料分析，JSON/metadata 可追溯設定與儀器狀態。
- 圖表支援 EVM、Burst Power、Frequency Error。
- Invalid point 不補 0，也不宣稱 PASS。

### Segment 5：工程架構

畫面：`docs/diagrams/system-architecture.png` 與 `docs/diagrams/single-measurement-lifecycle.png`。

講稿重點：

- Web/CLI 不直接控制 SCPI。
- SCPI command 集中管理，未驗證命令維持 `null`。
- Workflow 對 InstrumentSession protocol 撰寫，所以 Mock 與 real backend 可以分開。
- RF 開啟後所有錯誤、逾時、取消都會進入 cleanup。

### Segment 6：結論與限制

畫面：結案簡報最後一頁或文件中心。

講稿重點：

- WLAN loopback 主線已能用可重現流程展示。
- V1 loopback acceptance 不等於 DUT compliance。
- DUT／UDBox、正式 calibration、limit profile、MCS sweep、Constellation 與 5G NR FR1 仍屬下一階段。

## 5. 建議錄影畫面順序

1. Web 首頁或簡報封面。
2. 文件中心與 hardware SOP。
3. Web 實機頁 preview gate。
4. 實機 job progress 或 stored run history。
5. HTML report。
6. CSV／JSON／metadata。
7. Matplotlib PNG。
8. 系統架構圖。
9. SingleShot lifecycle。
10. 結案簡報最後一頁。

## 6. 錄影檔命名

建議使用：

```text
CMP180_final_demo_YYYYMMDD_short.mp4
CMP180_final_demo_YYYYMMDD_full.mp4
```

若影片包含新實機 RF 執行，需在 `HANDOFF.md` 追加日期、條件、run id、final RF state、measurement state、error queue 與 artifacts 路徑。

## 7. 現場失敗備案

| 狀況 | 處理方式 |
|---|---|
| 儀器無法連線 | 改展示 Mock mode 與 stored artifacts |
| Preview 被 gate 擋下 | 展示 rejection reason 與 correct range，說明安全設計 |
| RF owner 未核准 | 不啟動 RF，只播放 stored HIL evidence |
| 量測回 `INV` | 保留 partial artifact，展示系統如何停止並 RF Off |
| 網頁或瀏覽器異常 | 改用 README、HTML report、CSV/JSON 與簡報截圖展示 |

## 8. 錄影後檢查

- 確認影片沒有序號、license、內部帳號或敏感 IP 清單。
- 確認講稿沒有把 Mock／stored evidence 說成新的 live RF。
- 確認所有畫面中的 run id 與文件敘述一致。
- 若影片包含新 live RF，更新 `HANDOFF.md` 與相關 evidence 文件。
