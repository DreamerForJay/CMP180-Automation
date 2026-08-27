# CMsquares Workspace 借鑑與安全積木控制

## 中文版本

### 目的

本文件整理 CMsquares 值得借鑑的工作區操作模型，並定義 CMP180 Automation 如何在不降低 RF 安全性的前提下採用。這不是 CMsquares 的逆向工程文件，也不把畫面操作推測成已驗證 SCPI。

### 可借鑑的優點

1. **資源具象化**：Generator、Analyzer、Measurement 以獨立方塊出現在 Workspace，操作員能直接看出路由、頻率與狀態。
2. **就地控制與回饋**：Run／Stop 與狀態靠近被控制的資源，減少在多個頁面間尋找目前執行對象。
3. **設定與執行同一情境**：選取方塊後，在側邊面板調整該資源參數；中央 Workspace 保留整體關係。
4. **可組合流程**：官方資料說明 CMsquares 可建立自訂 test scenario，Sequencer 能以 function blocks 組成圖形化測試序列，並可加入 Python API script。
5. **即時狀態可見**：執行時將 Generator、Analyzer 與 Measurement 的狀態留在各自方塊，而不是只顯示單一全域 spinner。

官方參考：

- [R&S CMP180：CMsquares 統一瀏覽器操作介面](https://www.rohde-schwarz.com/us/products/test-and-measurement/wireless-tester-rf-analyzer-generator/cmp180-radio-communication-tester_63493-1081280.html)
- [R&S NEWS 224：CMsquares Test Environment 與圖形化 Sequencer](https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/dl_common_library/dl_news_from_rs/magazin/NEWS_224__Web.pdf)

### 本專案的安全差異

- Generator 方塊不提供獨立 RF On。Run 一律轉送既有受保護量測表單，仍需 Route、操作員在場、安全 Profile 與最終 RF 摘要確認。
- Pause 不在 RF On 或資料擷取中途凍結儀器。它只提出 cooperative pause request，workflow 在一個點完成 STOP 且 RF Off 後才進入 `PAUSED`。
- Stop 是 cooperative cancellation；若從 Pause 執行 Stop，會解除等待並在相同 RF Off 邊界結束。外層仍保留 STOP／ABORT／RF Off emergency cleanup。
- SingleShot 是不可分割交易，目前不支援 Pause；只有多點頻率／功率掃描能安全暫停。
- `RDY` 不是單獨的成功條件。若完整狀態包含 `ADJ`／`INV` 或關鍵 EVM、Power、Frequency Error 無效，該點必須標示 INVALID 並停止整批。

### `RDY,ADJ,INV` 診斷順序

1. 在 RF Off 下保存 CMsquares 與 Python 的設定快照，不 Reset Workspace。
2. 比較 ARB waveform 檔名、standard、bandwidth、band、center frequency、MCS、GI、LTF 與 spatial streams。
3. 比較 Generator marker 與 Analyzer trigger source、threshold、offset、timeout 和 minimum gap。
4. 比較 expected nominal power、external attenuation、ranging／adjust-level 與輸入過載狀態。
5. 執行單點低功率 HIL；只有完整 state 不含 `INV`、三個關鍵欄位有效、error queue empty、最終 RF Off 時才算通過。
6. 單點通過後才恢復兩點或固定掃描，不用掃描掩蓋單點同步問題。

### 目前 Web 積木

- **GPRF Generator**：顯示 RF1.1、ARB、頻率與受 workflow 管理狀態。
- **WLAN TX Analyzer**：顯示 RF1.5、320 MHz、Multi Evaluation 與 IDLE／ACTIVE／PAUSED。
- **Measurement Flow**：提供 Run、Pause／Resume、Stop；Run 走安全表單，Pause 只在 RF Off 點位邊界生效。

### 新增的診斷追溯資料

從此版本起，新的實機 SingleShot 與掃描 artifact 會保存量測狀態轉換、WLAN standard／band、ARB waveform、trigger source／threshold、expected nominal power、external attenuation 與 ranging strategy。這些欄位來自 RF On 前已驗證的設定與量測期間觀察到的狀態，不會為了寫紀錄再送一次控制命令。舊有 artifact 不會被回填，因此缺少欄位不代表當時沒有設定。

## English Version

### Purpose

This document captures the useful CMsquares workspace interaction model and defines how CMP180 Automation adopts it without weakening RF safety. It is not a reverse-engineering document, and visible UI behavior is not treated as verified SCPI syntax.

### Advantages to adopt

1. **Concrete resources**: Generator, Analyzer, and Measurement appear as independent workspace blocks, making routing, frequency, and status visible.
2. **Local controls and feedback**: Run/Stop and state stay next to the controlled resource, reducing ambiguity about what is active.
3. **Configuration and execution share context**: selecting a block exposes its parameters while the central workspace preserves system relationships.
4. **Composable workflows**: official material describes custom test scenarios and a graphical Sequencer built from function blocks, including Python API scripts.
5. **Live per-resource state**: Generator, Analyzer, and Measurement retain individual execution states instead of collapsing everything into one global spinner.

Official references:

- [R&S CMP180: unified browser-based CMsquares operation](https://www.rohde-schwarz.com/us/products/test-and-measurement/wireless-tester-rf-analyzer-generator/cmp180-radio-communication-tester_63493-1081280.html)
- [R&S NEWS 224: CMsquares Test Environment and graphical Sequencer](https://scdn.rohde-schwarz.com/ur/pws/dl_downloads/dl_common_library/dl_news_from_rs/magazin/NEWS_224__Web.pdf)

### Safety differences in this project

- The Generator block does not expose standalone RF On. Run delegates to the existing guarded form and still requires route, operator presence, a safe profile, and final RF-summary confirmation.
- Pause never freezes the instrument during RF On or acquisition. It creates a cooperative pause request, and the workflow enters `PAUSED` only after one point has completed STOP and RF Off.
- Stop is cooperative cancellation. Stopping from Pause releases the wait and terminates at the same RF-Off boundary. Outer STOP/ABORT/RF-Off emergency cleanup remains mandatory.
- SingleShot is an indivisible transaction and does not support Pause. Only multi-point frequency or power sweeps can pause safely.
- `RDY` alone is not success. A full state containing `ADJ`/`INV`, or invalid critical EVM, power, or frequency-error fields, makes the point INVALID and stops the batch.

### `RDY,ADJ,INV` diagnostic order

1. Save CMsquares and Python setting snapshots while RF is Off; do not reset the workspace.
2. Compare ARB waveform filename, standard, bandwidth, band, center frequency, MCS, GI, LTF, and spatial streams.
3. Compare Generator marker and Analyzer trigger source, threshold, offset, timeout, and minimum gap.
4. Compare expected nominal power, external attenuation, ranging/adjust-level behavior, and overload state.
5. Run a low-power single-point HIL. Pass only when the full state excludes `INV`, all three critical fields are valid, the error queue is empty, and final RF is Off.
6. Restore two-point or fixed sweeps only after SingleShot passes; do not use a sweep to hide a single-point synchronization fault.

### Current Web blocks

- **GPRF Generator** shows RF1.1, ARB, frequency, and workflow-managed state.
- **WLAN TX Analyzer** shows RF1.5, 320 MHz, Multi Evaluation, and IDLE/ACTIVE/PAUSED.
- **Measurement Flow** provides Run, Pause/Resume, and Stop. Run uses the guarded form, while Pause only takes effect at an RF-Off point boundary.

### Added diagnostic traceability

New hardware SingleShot and sweep artifacts now preserve the measurement-state transition, WLAN standard/band, ARB waveform, trigger source/threshold, expected nominal power, external attenuation, and ranging strategy. These fields come from settings already verified before RF On and states observed during acquisition; artifact recording does not issue another control command. Historical artifacts are not backfilled, so an absent field does not mean that the setting was absent at the time.
