# CMP180 EVM Automation 使用者操作指南

量測紀錄區分載入中、空清單、無符合條件與更新失敗；失敗會保留上次資料並提示重新整理。唯讀紀錄請求逾時為 15 秒。錯誤通知保留至手動關閉；新通知會取代舊通知。亮／暗主題共用提示配色，中英切換更新紀錄狀態、通知標題、主題提示與結果圖的無有效數值說明；原始診斷內容保留原文。切換不重新送出量測或 RF 請求。

首頁文案已依實作校對：區分實機執行與驗證狀態、取消與部分結果、校正草稿與正式套用；圖表的「重新載入圖表」不會自動播放。校對依據見 [首頁文案校對紀錄](home-copy-review.md)。

首頁主標題採逐字打字機效果（每字 160 ms），以逐字色彩插值保留雙行漸層，避免動畫字元透明消失；由 JavaScript 逐字顯示，完成後清除隱藏設定；相同語言的狀態更新不重播，切換中英語言才重新播放。系統設定「減少動態效果」時直接顯示完整標題。此效果僅為前端顯示，不操作儀器。

本文件說明目前工具。除了設定、Mock、連線與唯讀探索外，固定安全 profile 的 Python 實機 SingleShot、頻率／功率掃描與本機 Web GUI 已完成 HIL。自訂兩點頻率 HIL 曾在第二點收到 `INV` 並安全停止，因此自訂實機掃描仍須重新驗收；不得把該次結果描述為通過。完成一次量測後，仍可使用下列唯讀工具擷取上一筆 28 欄 OFDM SISO 結果：

首頁右側先顯示 CMP180 靜態渲染圖。按「啟用 360° 檢視」後可用滑鼠或觸控拖曳旋轉、滾輪／雙指縮放；下方提供正面、背面、側面、重設、自動旋轉與全螢幕。「靜態圖」會結束 3D 檢視；載入失敗可以重試。此元件只呈現外觀，不會建立儀器連線、送出 SCPI 或啟用 RF。完整操作與離線資產說明見 [3D 檢視器指南](cmp180-3d-viewer.md)。

```powershell
python scripts\cmp180_wlan_result_discover.py
```

此工具只使用 `FETCh`，不會開啟 RF 或啟動新量測。

## 1. 開啟專案

在 PowerShell 進入專案：

```powershell
cd <project-root>
```

確認目前分支：

```powershell
git branch --show-current
```

功能開發應位於專用 feature branch，不要直接在 `main` 修改；分支名稱以當次 PR／交接文件為準，不在操作指南寫死。

## 2. 啟用環境

環境已建立時：

```powershell
.\.venv\Scripts\Activate.ps1
```

第一次建立環境時：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev,hardware]"
```

## 3. 驗證設定檔

驗證 CMP180 連線設定：

```powershell
.\.venv\Scripts\python.exe -m cmp180_evm validate-config `
  configs\instrument.example.yaml
```

驗證 WLAN baseline：

```powershell
.\.venv\Scripts\python.exe -m cmp180_evm validate-config `
  configs\wlan_baseline.example.yaml
```

看到 `OK (instrument)` 或 `OK (wlan_baseline)` 才表示設定格式通過。
格式通過不代表 CMP180 專屬 SCPI 指令已完成驗證。

## 4. Dry Run

Dry Run 只列出預計步驟，不建立儀器連線，也不送出 SCPI：

```powershell
.\.venv\Scripts\python.exe -m cmp180_evm dry-run `
  --instrument-config configs\instrument.example.yaml `
  --config configs\wlan_baseline.example.yaml
```

目前輸出的 EVM、RF OFF 等項目是未來 workflow 計畫，不代表功能已實作。

## 5. Mock 連線

不需要 CMP180：

```powershell
.\.venv\Scripts\python.exe -m cmp180_evm test-connection --mock
```

成功時應顯示：

- `Connected successfully (mock)`
- Mock IDN（使用與實機相同的 `CMP` model token，顯示為 `CMP-MOCK`）
- Mock options
- `Error queue: empty`

## 6. 啟動 GUI

早期的 Tkinter 桌面 GUI（僅支援設定驗證、Dry Run、Test Connection）已移除；這些功能改用 CLI（見上方章節）即可，單點量測、頻率掃描與圖表請改用 Web GUI：

```powershell
python -m cmp180_evm.web
```

詳見 [Web GUI 操作指南](web-gui-guide.md)。

## 7. 執行測試

```powershell
New-Item -ItemType Directory -Force output | Out-Null
.\.venv\Scripts\python.exe -m pytest -q --basetemp=output\pytest-tmp
```

2026-08-27 本機基準為 `152 passed`；後續新增功能時，以當次完整測試輸出為準並同步更新文件。

已驗證 WLAN query-only discovery 時，可執行：

```powershell
python scripts\cmp180_wlan_discover.py |
  Tee-Object output\wlan-discovery-YYYY-MM-DD.txt
```

此工具只從集中式 `configs/scpi_command_map.yaml` 讀取已驗證 query，
不包含任何 WLAN setter、measurement initiate 或 RF control command。

保存量測後可完全離線重建圖表、量測報告與 V1 驗收狀態；下列命令只讀設定與 artifacts，不會連線儀器：

```powershell
python scripts\plot_results.py output\<run-folder>\results.csv
python scripts\plot_results.py output\<run-folder>\results.csv --engine pandas-matplotlib
python scripts\plot_results.py output\<run-folder>\results.csv --engine both
python scripts\build_report.py output\<run-folder>
python -m cmp180_evm validate-limits configs\limits.example.yaml
python scripts\build_v1_acceptance.py --evidence output\<real-run-folder>
```

預設 `svg` 不需要 Pandas／Matplotlib；`--engine pandas-matplotlib` 以 Pandas
DataFrame 讀取 stored CSV，並使用 headless `Agg` backend 產生 PNG；`both` 同時輸出
兩種格式。三者都只讀 artifact，不會連線 CMP180 或送 RF。

Web 的歷史分析可勾選一筆直接查看圖表，或選取 2–8 筆比較；可拖拉曲線排序、直接改名並調整顏色、線型與點型，也可匯出 SVG、PNG 與整理後 CSV。

新執行的單點或 Sweep 完成後，「結果與圖表」會同時顯示兩類圖：上方是可切換指標、滾輪縮放、滑鼠拖曳水平平移、hover 十字游標、A/B 游標與匯出的 Web 互動 SVG；下方「Pandas DataFrame + Matplotlib PNG」是後端從該 Run 的 `results.csv` 自動產生的 160 DPI 原圖。Matplotlib 區塊使用選單切換 EVM、Burst Power、Frequency Error 或 Clock Error，只顯示目前選取的一張 PNG，並可按「開啟原圖」。檔案位於該 Run 的 `plots-matplotlib/`。既有舊 Run 不會被自動改寫；需要時可用 `plot_results.py --engine pandas-matplotlib` 補產生。

實機「單點」分頁可在 CMP180 400–8000 MHz envelope 內執行中心頻率，並選擇 20／40／80／160／320 MHz 頻寬與 -55～-30 dBm Generator 功率。先按「檢查單點計畫」，再完成 RF1.1 → RF1.5 接線、無額外衰減器、操作員在場及最後 RF 確認。落在已核准 WLAN section 的點標示 `APPROVED`；區段外單點沿用已驗證的 EHT／B6GHz measurement template，實際 Generator 與 Analyzer center frequency 仍採輸入值並 readback，結果標示 `HIL_PENDING`。這項放寬只適用單點；頻率與功率掃描仍受 approved section gate 保護。後端會以 fingerprint 重新驗證同一組值後才建立 CMP180 session。`HIL_PENDING`、未校正或沒有正式 Limit Profile 的結果不得作為 DUT compliance。

2026-09-10 的 400 MHz／320 MHz／-40 dBm 實機測試證實兩端可設定並回讀
400 MHz，但 EHT／B6GH template 回傳 reliability `74` 且所有量測欄位為 `INV`。
因此 Web 允許執行不代表該組合可有效解調；遇到 `INV` 後應停止，不可自行提高功率
或連續重試。該次 artifact run ID 為 `8ad94d4884`，最終 RF `OFF`、measurement
`RDY`、error queue empty。

## 8. 第一次連接 CMP180

只有在以下條件都滿足後才需要接實機：

- 離線測試全部通過。
- Git 工作區乾淨。
- CMP180 沒有正在執行量測。
- CMP180 IP 仍為 `192.168.200.50`。
- `configs/scpi_command_map.yaml` 的 CMP180 專屬命令仍為 `null`。

執行：

```powershell
.\.venv\Scripts\python.exe -m cmp180_evm test-connection `
  --instrument-config configs\instrument.example.yaml
```

此步驟只允許 `*IDN?`、`*OPT?` 與 `SYST:ERR?`。完整安全規則請見
[hardware-readonly-validation.md](hardware-readonly-validation.md)。

## 9. 目前不能做的操作

固定安全 profile（RF1.1 → RF1.5、6105 MHz、320 MHz、-40 dBm）的 RF ON、Generator／Analyzer setter、Initiate/Stop/Abort 與 EVM／Burst Power／Frequency Error 讀值已完成實機驗證，可透過 CLI SingleShot 或一般本機 Web 啟動使用；`--demo-only` 會停用儀器控制。以下項目仍未完成：

- 固定 profile 的 frequency／power sweep 已完成 CLI 與 Web HIL；自訂實機掃描仍待針對 `INV` finding 完成 trigger／ranging 複查與重新 HIL。
- 正式 WLAN Pass/Fail 判定（尚無正式 limit、path-loss／calibration table，目前只能顯示 workflow health 或示範 threshold）。
- 超出已驗證安全包絡的任意頻率／功率／DUT 輸入；Web 可在 400 MHz–8 GHz 型錄頻率與 WLAN 頻寬內建立計畫，但正式送 RF 仍受 Approved Profile 與 HIL 狀態限制。
- 內網 deployment 所需 authentication、RBAC 與 audit log。

上述功能必須先完成對應的 CMP180 HIL 驗證、命令審核與安全檢查。

## 10. Git 顯示 dubious ownership

若此專案曾由 Codex 建立或提交 `.git`，Windows Git 可能因 Codex 沙箱帳號與
目前登入帳號不同而顯示：

```text
fatal: detected dubious ownership in repository
```

這不代表儲存庫損壞。只對這個確定的專案路徑加入 Git 安全清單：

```powershell
git config --global --add safe.directory `
  <project-root>
```

確認設定：

```powershell
git config --global --get-all safe.directory
git branch --show-current
git status
```

不要將 `*`、整個磁碟或不認識的路徑加入 `safe.directory`。若相同路徑被重複
加入通常不影響 Git；可用 `--get-all` 查看目前清單。

---

# CMP180 EVM Automation User Guide

### 直接式實機控制

實機頁面使用單點、頻率掃描與功率掃描三個直接分頁，不再顯示裝飾性 Generator／Analyzer／Flow 積木，也不要求從下拉選單選擇模式。頻率掃描預設帶入已核准的 5925→6125 MHz／320 MHz 區段，避免剛切到掃描軸就落入非 WLAN 空隙；若改成 5085 MHz 或其他未核准組合，畫面仍會拒絕並保持 RF Off。Run 仍會觸發既有安全表單與最終 RF 摘要確認。多點掃描可按 Pause，系統會等目前點 STOP 且 RF Off 後才顯示 `PAUSED`；Resume 從下一點繼續，Stop 則結束並保存 partial artifacts。SingleShot 不支援中途 Pause。

### GPRF PA 功率掃描與 P1dB 圖

GPRF power sweep 可作為第一版 PA conducted scalar 量測入口：選擇 `Power` 軸，填入固定頻率、Start／Stop／Step、dwell、input cable loss、output cable loss、external gain、output attenuator 與 SA safe limit。Preview 會顯示 DUT Pin 範圍；執行後 CSV／JSON 會保存 `pin_dbm`、`pout_dbm`、`gain_db`，結果頁可直接切換 PA Pin、PA Pout 與 PA Gain 圖。`pout_dbm` 由 analyzer power 加回 output cable loss 與 attenuator；`pin_dbm` 由 generator power 加 external gain、扣 input cable loss。

若已使用 approved PA profile，現場換 DUT 不需重填上述工程參數。先驗證 profile：

```powershell
python -m cmp180_evm validate-pa-sweep configs\pa_sweep.example.yaml
```

確認 RF1.1 → RF1.5 route 與操作員在場後執行；若沒有外部衰減器，程式會自動把
stop power 夾到 RF1.5 safe limit 內：

```powershell
python scripts\cmp180_pa_sweep_validate.py `
  --dut-id DUT-001 `
  --confirm-direct-cable `
  --confirm-operator-present
```

現場若有外部衰減器，才加上例如 `--output-attenuator-db 30`。這會讓安全估算允許掃到
更高 Generator stop power，但不會把該衰減器寫入 CMP180 measurement EATT。

Web 操作不必輸入 CLI：進入實機量測，切到 `RF 功率讀值（GPRF）`，按「載入 approved
PA profile」會帶入目前 approved envelope。預設沒有實體輸出衰減器，因此畫面先載入
`-55 → -25 dBm`；若現場使用受控 DUT／實體 attenuator，才把 `Output attenuator`
改成實際值並把 stop 調到 profile 允許的 `-20 dBm`，再按「檢查 GPRF 計畫」與
「執行實機量測」。

Profile 會把實體 `output_attenuator_db` 與 CMP180 measurement
`measurement_external_attenuation_db` 分開；前者只用於 RF1.5 安全預估與離線 Pout/Gain，
不得誤寫成儀器 EATT。任一點出現 SCPI error、reliability 非 0 或 SA safe limit 時，
workflow 會在該點 STOP／RF Off 後停止後續掃描並保存 partial artifact。

Profile 另有必填的 `dut_max_input_dbm`，代表 DUT 參考面能承受的輸入上限。它與
`sa_safe_limit_dbm` 是兩條互相獨立的保護：後者只保護 CMP180 analyzer，前者才保護 DUT
本身。`safe_stop` 取兩者較嚴的一邊；起始功率就已超過 `dut_max_input_dbm` 時整份 profile
會被拒絕載入。只要 request 宣告了非零的 `expected_dut_gain_db`（代表路徑上有 DUT），
未填 `dut_max_input_dbm` 的 GPRF 計畫一律阻擋。

P1dB 只在功率掃描資料已觀察到 Gain 下降 1 dB 時輸出 `IP1dB` 與 `OP1dB`。若最高功率仍未讓 Gain 下降 1 dB，結果會顯示 `not_found`，並同時列出最大已觀察 compression、最大 Pin 與最大 Pout，避免把最後一點誤當成 P1dB。SA safe limit 是資料有效性門檻；超過時該點標示 `SA_LIMIT` 且不納入 P1dB，實體保護仍必須靠正確衰減器、接線與現場操作員確認。2026-09-09 已完成 RF1.1 → RF1.5 低功率 GPRF PA sweep 實機驗證；擴大到 `-20 dBm` 的 P1dB 掃描仍需使用 profile／fixture 安全裁切，不得把失敗 finding 當成 P1dB 證據。

示範模式的單點、頻率掃描與功率掃描不連接 CMP180，也不送 RF，因此不套用實機功率安全上限；功率掃描會以固定的模擬 PA 曲線產生 Pin、Pout、Gain compression 與 P1dB 摘要。「進階 PA 指標」可輸入中心頻率、Pin、雙音間距與通道頻寬，產生 OIP3／IM3、H2／H3 及 ACP／ACLR 三張教學圖，並保存 JSON／CSV／HTML。這些數值來自固定模擬公式，不代表 SG、SA 或 DUT 的實際能力；所有 artifact 均標示 `SIMULATED`，不得當成新的 PA 實機量測證據。

### Converter DUT（UDBox 類）的頻率解耦

PA 的輸入與輸出同頻，因此 GPRF 掃描原本把 generator 與 analyzer 寫在同一個頻率。
Up/Down converter 不成立：送進去的是 IF、量到的是 RF，兩端寫同頻只會讓 analyzer 停在
底噪。GPRF request 加上 `conversion` 區塊後，兩端才會分開設定：

```yaml
conversion:
  direction: up          # up：generator 送 IF、analyzer 收 RF；down 相反
  sideband: high         # high：RF = LO + IF；low：RF = LO − IF
  lo_frequency_hz: 6000000000
  limits:                # DUT 端可調範圍，預設為 UD Box 0630
    if_min_hz: 1000000000
    if_max_hz: 8000000000
    rf_min_hz: 6000000000
    rf_max_hz: 30000000000
    lo_min_hz: 6000000000
    lo_max_hz: 30000000000
```

掃描軸永遠是 **generator 端**：`up` 掃 IF、`down` 掃 RF，另一端每點依 LO 與 sideband
重新解算。Preview 會逐點驗證，只檢查端點會漏掉中間落出範圍的頻率。IF、RF、LO 任一項
超出 DUT 範圍，或 generator／analyzer 任一端超出 CMP180 的 400 MHz–8 GHz，計畫都會被
阻擋並指出是哪一項。

**只適用單次轉換。** 若 UD Box 的 Up 與 Down channel 被接成級聯迴路（RF1 → RF2 迴路線、CMP180 只接 IF1 與 IF2），共用 LO 會讓兩次轉換互相抵銷，analyzer 頻率等於 generator 頻率，此時**不可**送 `conversion`，否則 analyzer 會被調到單次轉換的 RF 頻率而量到底噪。該接線請改用 `configs/udbox_cascade_loopback.example.yaml`與 `docs/udbox-loopback-test-plan.md`。

`configs/udbox_sweep.example.yaml` 是 UD Box 0630 的規劃範例，頻率計畫為
IF 1000 MHz + LO 6000 MHz → RF 7000 MHz。挑這組的原因：RF 7000 MHz 落在已核准的 6 GHz
WLAN section 內，之後要改量 WLAN EVM 不必另開 section；不要的邊帶 `|LO − IF|` = 5000 MHz
與 LO 洩漏 6000 MHz 也都在 CMP180 範圍內，同一次接線就能順便觀測。Preview 會用
`mirror_observable` 與 `lo_leakage_observable` 標示這兩個頻率是否看得到。

Web 操作：切到 `RF 功率讀值（GPRF）`，按「載入 UDBox 0630 範例」會一次帶入上述頻率
計畫與功率設定並自動勾選轉換器選項。手動填寫時，勾選「DUT 是頻率轉換器」才會出現
direction、sideband 與 LO frequency 三個欄位；未勾選就不送出 `conversion`，兩端維持同頻。

Converter 是淨損耗元件，`expected_dut_gain_db` 必須能填負值（UD Box 0630 datasheet
conversion loss 10 dB typ）。安全設定要注意三件事：

- **CMP180 generator 最大輸出是 +8 dBm**，GPRF 規劃上限已對齊此值。這代表
  **UD Box 0630 的 P1dB 量不到**：datasheet Tx Output P1dB ≥ 0 dBm、conversion loss
  10 dB，反推 IF 端要約 +10 dBm 才進入壓縮，至少差 2 dB（P1dB 是「Min.」值，實際
  只會更高）。因此這條路徑只量得到 conversion gain 與平坦度；要量 P1dB 必須在 IF
  路徑外加驅動放大器，那是另一組接線與安全分析。
- UDBox RF 輸出端建議實體加掛 10 dB 衰減器。generator 上限 +8 dBm、conversion loss
  10 dB，最高輸出約 −2 dBm，距離 `sa_safe_limit_dbm` 只有 2 dB，對首次上線的未驗證
  route 太薄；加 pad 後 analyzer 端最高約 −12 dBm，保留 12 dB 餘裕，低端 −40 dBm 仍在
  已驗證的量測功率範圍內。
- `dut_max_input_dbm` 必填。UD Box 0630 datasheet 的 RF Specifications 表只給 P1dB
  （線性度），**沒有 absolute maximum rating**，因此範例值由 Tx Output P1dB 0 dBm 加回
  10 dB conversion loss 再留 3 dB 觀測餘裕得到，屬於工作上限而非損傷閾值。真正的
  absolute max 仍應向原廠索取後更新該欄。

建議在插入 UDBox 之前，先以 RF1.1 → RF1.5 直接對接、同一個 IF 頻率跑一次 back-to-back
基準掃描。這條基準讓你之後能把線損與 CMP180 絕對功率誤差從 conversion gain 中扣掉；
沒有它，量到的增益會混入未知線損。基準掃描是同頻量測，不需要勾選轉換器選項。

RF owner 已核准 UDBox route（2026-09-09）。但仍沒有該 route 的 HIL 證據，
`dut_max_input_dbm` 也還是 P1dB 推導的工作上限而非原廠損傷閾值，因此結果只能標
`MEASURED`，不得作為 compliance 宣稱。

## Loopback 驗證

開啟「Loopback 驗證」，設定固定中心頻率、頻寬、Generator power 與 2–100 次 repeats。Expected RX Power 必須代表 analyzer input reference plane，不是 Analyzer ranging 的 -20 dBm。確認 RF1.1 → RF1.5、固定 Cable／UD Box path 與操作員在場後，Review 並完成最後 RF 確認。紅色列表示 INVALID 或 outlier，原始值仍完整保存。11 個 WLAN section 代表點、核准門檻與至少 10 repeats 會選用各自的 2026-09-03 HIL approved profile，成功時直接產生正式 `LOOPBACK_READY`；改動代表頻率、頻寬、功率、route 或門檻會自動回到 draft。

若要一次建立所有 WLAN section baseline，勾選相同的接線與操作員確認後按「一鍵執行全部 11 Profiles × Repeat 10」。Preview 必須顯示 11 profiles／110 SingleShots；最後確認後系統依序執行，每個 profile 產生獨立 report。此按鈕不包含其他 route、UD Box 或未核准頻率。

頁面右上角可切換中文／English。SingleShot、WLAN Sweep、GPRF、Loopback、HIL Campaign 與 Calibration 的檢查步驟、Preview、安全阻擋原因、修正方式與最後確認都會立即切換；已顯示的 Preview 只在前端重繪，不會因切換語言重新送出 SCPI、Preview API 或 RF job。

## 12. 產生 CMP180 Blender 外觀模型

下列指令會在本機重建可編輯 `.blend`、GLB 與驗證渲染：

```powershell
uv run --python 3.13 --with bpy==5.2.1 python scripts/build_cmp180_blender.py
```

產物位於 `assets/cmp180_3d/`。這個流程只建立離線 3D 外觀資產，不會連接儀器、傳送 SCPI、啟動量測或開啟 RF。模型是依照片估算的視覺參考，不是原廠機構 CAD。

## English Version

### Loopback validation

Open Loopback Validation and enter a fixed center frequency, bandwidth, generator power, and 2–100 repeats. Expected RX Power must describe the analyzer-input reference plane; it is not the -20 dBm analyzer-ranging value. Confirm RF1.1 → RF1.5, the unchanged cable/UD Box path, and on-site operator presence, then review and accept the final RF confirmation. Red rows identify INVALID or outlier values while preserving raw measurements. The 11 WLAN-section representative points use their own 2026-09-03 HIL-approved profiles when the approved thresholds and at least 10 repeats are selected; a successful run directly produces formal `LOOPBACK_READY`. Changing the representative frequency, bandwidth, power, route, or thresholds falls back to draft.

To create every WLAN-section baseline in one operation, confirm the same route and operator-presence checks and select Run All 11 Profiles × Repeat 10. Preview must show 11 profiles and 110 SingleShots. After final confirmation, profiles run sequentially and each receives an independent report. This action excludes other routes, UD Box paths, and unapproved frequencies.

Use the top-right selector to switch between Chinese and English. The check steps, previews, safety rejection reasons, correction guidance, and final confirmations for SingleShot, WLAN Sweep, GPRF, Loopback, HIL Campaign, and Calibration update immediately. An already displayed preview is redrawn locally; changing language does not resend SCPI, call a preview endpoint, or start an RF job.

This guide describes the current tool. Configuration validation, Mock operation,
connection checks, query-only discovery, the fixed-profile Python hardware SingleShot,
frequency and power sweeps, and the local Web GUI have completed their applicable
validation. A custom two-point frequency HIL returned `INV` at its second point and
stopped safely, so custom live execution still requires trigger/ranging review and a new
HIL. It must not be reported as a passing run.

The home page initially displays a CMP180 still render. Select “Explore in 360°” for mouse/touch orbit and wheel/pinch zoom. Controls provide front, rear, side, reset, auto-rotation, and fullscreen. “Still image” ends the 3D session; failed loads can be retried. This exterior viewer does not connect to an instrument, transmit SCPI, or enable RF. See the [3D viewer guide](cmp180-3d-viewer.md) for operation and offline assets.

### 1. Open the project

Open PowerShell in `<project-root>` and run `git branch --show-current`. Develop on a
dedicated feature branch rather than directly on `main`; use the current PR or handoff
document as the source of truth for the branch name.

### 12. Generate the CMP180 Blender exterior model

The following command locally rebuilds the editable `.blend`, GLB, and validation render:

```powershell
uv run --python 3.13 --with bpy==5.2.1 python scripts/build_cmp180_blender.py
```

Outputs are written to `assets/cmp180_3d/`. The workflow creates offline 3D exterior assets only; it does not connect to an instrument, transmit SCPI, start a measurement, or enable RF. The model is a photo-estimated visual reference, not manufacturer mechanical CAD.

### 2. Activate the environment

Run `\.venv\Scripts\Activate.ps1`. For a new environment, create it with
`python -m venv .venv`, then install `-e ".[dev,hardware]"` with the virtual-environment
Python.

### 3. Validate configuration

Run `python -m cmp180_evm validate-config` for both
`configs\instrument.example.yaml` and `configs\wlan_baseline.example.yaml`. An `OK`
result validates the file format; it does not independently revalidate every CMP180 SCPI
command.

### 4. Dry run

Use `python -m cmp180_evm dry-run --instrument-config ... --config ...` to preview the
workflow. A dry run opens no instrument session and sends no SCPI. Planned EVM or RF-Off
steps in its output are not evidence of a completed hardware workflow.

### 5. Mock connection

Run `python -m cmp180_evm test-connection --mock`. The expected output includes a Mock
identity, options, and an empty error queue. No CMP180 is required.

### 6. Start the Web GUI

Run `python -m cmp180_evm.web`, then open `http://127.0.0.1:8765`. The served frontend is
the horizontal workspace in `src/cmp180_evm/web/static/`; `static_v2/` is an archived
design reference. Normal startup enables guarded local hardware control; add `--demo-only`
for training without instrument access. Starting the service does not transmit RF. The old
Tkinter GUI has been removed.

### Direct hardware controls

Hardware uses direct Single, Frequency Sweep, and Power Sweep tabs. Decorative Generator,
Analyzer, and Flow blocks and the measurement-mode dropdown have been removed. Run still
requires the existing safety form and final RF summary. Sweep Pause takes effect only after
the current point has stopped and RF is off; Resume continues at the next point, while Stop
preserves partial artifacts. SingleShot cannot pause mid-transaction.

### 7. Run tests

Run `\.venv\Scripts\python.exe -m pytest -q --basetemp=output\pytest-tmp`. The local
baseline on 2026-08-27 is `152 passed`; always treat the current full test output as
authoritative. The WLAN discovery script is query-only and does not send setters,
measurement initiation, or RF-control commands.

After saving a run, use `python scripts\plot_results.py <results.csv>` and
`python scripts\build_report.py <run-folder>` to rebuild charts and a self-contained
report entirely offline. Validate limits with `python -m cmp180_evm validate-limits
configs\limits.example.yaml`, and build the offline V1 gate report with `python
scripts\build_v1_acceptance.py --evidence output\<real-run-folder>`. The Web history
analysis accepts one run for plotting or 2–8 runs for comparison, with drag-to-reorder,
inline trace renaming, colour/line/point styling, and SVG, PNG, or normalized CSV export.
Add `--engine pandas-matplotlib` for Pandas/Matplotlib PNG files or `--engine both` for
both dependency-free SVG and PNG output. These commands read stored artifacts only.

After a new single or sweep run completes, Results shows two plot families. The upper chart is the interactive Web SVG with metric selection, wheel zoom, horizontal mouse-drag panning, hover crosshairs, A/B cursors, and export. The lower “Pandas DataFrame + Matplotlib PNG” area contains 160 DPI images generated automatically from the run's saved `results.csv`. Use its selector to switch among EVM, Burst Power, Frequency Error, or Clock Error; only the selected PNG is shown, with an open-original link. Files live in the run's `plots-matplotlib/` directory. Existing historical runs are not rewritten automatically.

The Hardware Single tab can execute a center frequency across the CMP180 400-8000 MHz envelope with 20/40/80/160/320 MHz bandwidth and -55 to -30 dBm generator power. Review the plan, then confirm RF1.1-to-RF1.5 direct cabling with no added attenuator, operator presence, and the final RF dialog. A point in an approved WLAN section is labelled `APPROVED`. An out-of-section point uses the verified EHT/B6GHz measurement template while the generator and analyzer center frequencies still use and read back the entered value; its result is labelled `HIL_PENDING`. This relaxation applies only to SingleShot; frequency and power sweeps retain the approved-section gate. The backend revalidates the values and fingerprint before opening the CMP180 session. `HIL_PENDING`, uncalibrated, or no-formal-limit results are not DUT-compliance claims.

The Hardware Sweep tabs use direct Single/Frequency/Power controls. Frequency sweep defaults to the approved 5925→6125 MHz / 320 MHz section so the initial plan is executable; changing it to 5085 MHz or another unapproved combination is still rejected with RF left off. Multi-point runs can be paused only at point cleanup/RF-Off boundaries, then resumed from the next point or stopped with partial artifacts saved.

### 8. First CMP180 connection

Connect only after the PC and instrument addressing, Ethernet path, and TCP port have
been confirmed. Start with `test-connection`; this path is limited to `*IDN?`, `*OPT?`,
and `SYST:ERR?`. See `hardware-readonly-validation.md` for the complete rules.

### 9. Current limitations

Fixed-profile SingleShot, frequency sweep, and power sweep have passed their CLI/Web HIL.
The custom-value SingleShot software path is complete but still needs an on-site regression;
custom hardware sweep remains gated after the `INV` finding. Formal WLAN compliance is
also unavailable until approved limits and an approved Path Loss/Calibration Profile
exist. Inputs outside the verified safety envelope are prohibited, and intranet exposure
still requires authentication, RBAC, and audit logging.

### 10. Git dubious ownership

If Windows Git reports dubious ownership after sandbox activity, add only the confirmed
project path with `git config --global --add safe.directory <project-root>`. Never add
`*`, a whole drive, or an unknown directory. Verify the result with `--get-all`, then run
`git branch --show-current` and `git status`.

### 11. Block-based hardware control

The GPRF Generator, WLAN TX Analyzer, and Measurement Flow blocks on the hardware page expose per-resource state. Run still delegates to the guarded form and final RF-summary confirmation; the Generator block cannot enable RF independently. For multi-point sweeps, Pause waits until the current point has completed STOP and RF Off before reporting `PAUSED`; Resume continues at the next point, and Stop terminates while preserving partial artifacts. SingleShot cannot pause mid-transaction.

## 中文：全 WLAN waveform 與頻段工具

先用 query-only 工具一次盤點儀器 waveform，再用單一 HIL 工具跑 11 個合法區段：

```powershell
.\.venv\Scripts\python.exe scripts\cmp180_waveform_catalog.py
.\.venv\Scripts\python.exe scripts\cmp180_full_wlan_campaign_validate.py `
  --confirm-direct-cable --confirm-no-attenuator `
  --confirm-operator-present --confirm-full-wlan-campaign
```

中斷後可重複 `--section 2.4GHz-bw20` 只補指定區段。每次切換 waveform 前都要求
RF OFF／measurement idle；每個 channel center 都是完整 SingleShot 並在 finally
Stop／Abort／RF Off。11 個完成 HIL 的 section 已納入 Web approved profile；一般 Web
自訂掃描會在 RF OFF／measurement idle 時依頻寬自動切換並回讀匹配 waveform。
400 MHz–8 GHz 仍只是儀器調諧型錄範圍，非 WLAN 空隙不會被核准執行。

## English: full WLAN waveform and band tools

First inventory the instrument waveform directory with the query-only tool, then use one
HIL tool for all 11 legal sections:

```powershell
.\.venv\Scripts\python.exe scripts\cmp180_waveform_catalog.py
.\.venv\Scripts\python.exe scripts\cmp180_full_wlan_campaign_validate.py `
  --confirm-direct-cable --confirm-no-attenuator `
  --confirm-operator-present --confirm-full-wlan-campaign
```

After interruption, repeat `--section 2.4GHz-bw20` to resume only a named section. Every
waveform switch requires RF OFF and an idle measurement. Every channel center is a complete
SingleShot with Stop/Abort/RF Off in `finally`. All 11 HIL-complete sections are now in
the Web approved profile. Normal Web custom sweeps select and read back the matching
waveform while RF is OFF and measurement is idle. The 400 MHz–8 GHz figure remains an
instrument tuning catalog range; non-WLAN gaps are not approved for execution.


### PA 掃描摘要與有效性（2026-09-09）

在結果頁開啟含 PA 欄位的 GPRF 紀錄：功率掃描摘要顯示 Small-signal Gain、Max Pout、Max Compression、IP1dB、OP1dB 與 Valid Points；頻率掃描顯示 Mean Gain、Gain Peak-to-Peak Ripple 與 Gain Std Dev（母體標準差）。PA 統計只納入有效且 Pin／Pout／Gain 齊全的點。`not_found` 表示有效掃描範圍內未觀察到 1 dB 壓縮，`insufficient_points` 表示資料不足；缺值不補零。

Analyzer measured／expected power 的誤差與 PA Gain 是不同物理量；不得把 Analyzer error ripple 當成 Gain flatness。無 PA 欄位的舊 GPRF 結果保留明確標示 Analyzer 參考面的摘要，dBm 平均為算術平均。重新產生的 SVG／Matplotlib 圖會排除 INVALID 並切斷曲線；既有 PNG 不會自動更新，須由原 CSV 重新產圖。原始 CSV／JSON 保留診斷數值。

本次驗證為合成資料／Mock 回歸及既有 stored artifact 查閱，未執行新的實機 RF 量測。


### 圖表縮放與拖曳（2026-09-09）

游標放在繪圖區內，滾輪前滾放大、後滾縮小；X 軸以游標位置縮放，Y 軸依可見有效測點自動調整。按住滑鼠左鍵可左右拖曳，放開即停止；拖曳範圍受資料邊界限制，縮小最多回到全圖。Reset 或雙擊恢復完整範圍。A/B 模式下左鍵改為選點；縮放／拖曳會清除舊游標，避免位置誤讀。座標軸與文字固定在圖框內，資料超出範圍時只裁切資料層。以上操作只讀取既有結果，不送 SCPI 或 RF。
