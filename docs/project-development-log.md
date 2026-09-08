# CMP180 專案 Week 1–12 詳細開發日誌與完成度盤點

## 繁體中文

### 1. 文件目的與證據邊界

本文件以 2026-09-03 的 repository 狀態為基準，將實習簡報的交付要求對照目前 CMP180 WLAN TX EVM 自動化專案，並重建可追溯的開發日誌。依據包括 Git commit 歷史、`HANDOFF.md`、`README.md`、`SPEC.MD`、測試、程式碼與具日期的硬體證據。

這不是聊天逐字稿；無法由 repository 證明的對話或決策不會被虛構。Mock、dry-run、CMsquares 手動操作、預覽與單獨 stored `FETCh` 均不算新的完整 Python 實機量測。簡報中的指示只作為需求來源，不會覆寫本專案的 RF 安全規則、SCPI 驗證規則或文件權威順序。

### 2. 最新簡報要求

`RF_Intern_EVM_Plan_CMP180.pptx`（2026 年 7 月版）共 10 頁，核心交付為：

- CMP180 Python／SCPI 自動化：RF Port／Route、Trigger、Sweep、Data Log 與 Chart。
- WLAN／5G NR FR1 EVM，以及 Power／Frequency／MCS 掃描。
- EVM vs Power／Frequency／MCS 測試報告、README、使用手冊、GitHub repository 與 10–15 分鐘 Demo。
- Week 9：Trigger／Timeout 診斷與 RF Path Loss／Calibration Profile。
- Week 10：錯誤處理、Logging、Retry 與 README。
- Week 11：Loopback／DUT／UDBox 多情境測試與 Demo 準備。
- Week 12：最終測試、GitHub 整理與期末 Demo。

簡報第 8 頁實際列的是 CMP180 Product Page／Manual 與公司 SOP；使用者補充的 Anritsu RF Fundamentals 與 FSW-K70 VSA Manual 可列為延伸教材，但不能拿 FSW／CMW 的 SCPI 猜測 CMP180 命令。

### 3. 官方學習資源評估

| 資源 | 可用程度 | 本專案可採用內容 | 不可直接採用內容 |
|---|---|---|---|
| [RsInstrument Step-by-step Guide](https://rsinstrument.readthedocs.io/en/latest/StepByStepGuide.html) | 高 | `visa_timeout`／`opc_timeout` 分工、`query_opc()`、`*_with_opc()`、error queue、SCPI logger、timeout suppressor | 範例位址、Reset 與示意 SCPI；本專案明確禁止未授權 Reset |
| [RsInstrument API](https://rsinstrument.readthedocs.io/en/latest/RsInstrument.html) | 高 | `query_all_errors*()`、OPC 同步、資源鎖、binary transfer 與 logger API | 不能取代 CMP180 command help 或本機 typed registry |
| [R&S Examples](https://github.com/Rohde-Schwarz/Examples) | 中高 | 專案結構、session lifecycle、status checking、reliability handling、shared-session pattern | repository 沒有可直接套用的 CMP180 WLAN EVM 範例；CMW／SMW／FSW 命令不可複製成 CMP180 命令 |
| [R&S GitHub](https://github.com/Rohde-Schwarz) | 中高 | RsInstrument 原始碼、R&S 維護的 driver 與範例，可供通信層與測試方式參考 | 特定儀器 driver 的 API 不代表 CMP180 已安裝或已驗證 |
| [CMP180 Product Page](https://www.rohde-schwarz.com/us/products/test-and-measurement/wireless-tester-rf-analyzer-generator/cmp180-radio-communication-tester_63493-1081280.html) | 高，能力邊界 | 最高 8 GHz、最高 500 MHz、2×VSA／2×VSG、2×8 RF ports、WLAN 與 5G FR1 的型錄能力 | 型錄能力不等於本機 option、Approved Profile 或 HIL 已完成 |
| [Anritsu RF Fundamentals](https://www.anritsu.com/en-us/test-measurement/support/training-and-education/elearning/rf-fundamentals) | 中高，理論 | dB、modulation、RF impairment、coaxial cable、components 與 propagation 基礎 | 不提供 CMP180 SCPI 或本專案驗收證據 |
| [FSW-K70 VSA Manual](https://www.rohde-schwarz.com/au/manual/r-s-fsw-k70-vsa-user-manual-manuals_78701-29049.html) | 中，量測概念 | VSA、EVM、demodulation、結果判讀與遠端量測觀念 | FSW-K70 是不同儀器／應用；其 SCPI 不得直接加入 CMP180 command map |

建議採用順序：先讀 RsInstrument 的連線、timeout、OPC、logging 與 error handling；再讀 CMP180 內建 Help／官方 manual 驗證每一條 SCPI；R&S Examples 用來學設計模式；Anritsu 與 FSW-K70 只補 RF／VSA 理論。

### 4. 對照簡報的完成度

狀態定義：`完成` 表示程式、測試、文件與所需證據一致；`部分完成` 表示核心存在但交付形式或 HIL 尚缺；`未完成` 表示目前不能合理宣稱具備該能力。

| 簡報要求 | 狀態 | repository 證據與判定 |
|---|---|---|
| CMP180 連線、`*IDN?`、基本 SCPI | 完成 | RsInstrument session、ID 驗證、query-only discovery 與實機連線證據均存在 |
| WLAN SingleShot：setup → initiate → fetch | 完成 | 完整 Python workflow、28 欄 × 5 statistics、CSV／JSON／metadata／raw／HTML；有新實機 RF HIL |
| 功率掃描（EVM vs Power） | 完成核心；目前 profile 待重驗 | 固定四點 HIL 曾通過；另有 -55～-30 dBm campaign 證據。最新 waveform/profile 的固定 power profile 仍需重驗 |
| Pandas + Matplotlib 圖表 | 完成並接入 Web（2026-09-03 軟體驗證） | 新 Run 從 CSV/DataFrame 自動產生 Matplotlib Agg PNG，結果頁以選單切換單張 PNG 預覽與原圖連結；功率掃描 PNG 使用 Generator Power (dBm) 作為 X 軸；保留 dependency-free SVG／HTML。此功能只讀 stored CSV，不連線儀器 |
| Frequency／Channel 掃描 | 完成（WLAN 合法區段） | 2.4／5／6 GHz、20／40／80／160／320 MHz，11 區段、176/176 channel centers HIL 通過 |
| MCS 掃描 | 未完成 | 目前以 EHT MCS11 為已驗證基線，尚無自動 MCS 軸與多 MCS HIL matrix |
| 5G NR FR1 profile／EVM | 未完成 | CMP180 型錄支援不等於本 repository 已實作；目前產品範圍是 WLAN TX EVM |
| Constellation | 未完成 | 目前 artifacts／圖表集中 EVM、Power、Frequency Error、Clock Error，無 constellation acquisition／rendering |
| Reliability／Limit PASS-FAIL | 部分完成 | `RDY/ADJ/INV`、critical-metric validity、Draft／Approved limit lifecycle 已完成；目前正式證據只適用核准的 V1 loopback 情境，不是 DUT compliance |
| Trigger／Timeout 診斷 | 大致完成 | trigger source／threshold readback、measurement state snapshots、60/120 秒 timeout 問題與 SingleShot repetition 修復都有證據；仍可把 RsInstrument 原生 OPC timeout 與 timeout exception 分類整合得更完整 |
| RF Path Loss／Calibration Profile | 部分完成 | lifecycle、0–30 dB、內插、禁止外插、expiry、Web wizard、adapter framework 與套用核心已完成；真實 traceable readings／正式 external adapter HIL 尚缺 |
| 錯誤處理與 cleanup | 完成核心 | RF workflow 使用 `try/finally`，錯誤、取消、逾時仍 STOP／ABORT、RF Off，並記錄 error queue／final state |
| Logging | 部分完成 | `application.log`、`scpi.log` 與敏感資料邊界已有；尚未完整採用 RsInstrument logger／結構化 audit log，內網 RBAC 也未完成 |
| 測試重試機制 | 部分完成（安全核心完成） | bounded retry 限制 0–5 次，只用於 query-only connection diagnostic 的 transient connection/timeout；每次重試前關閉 session。SCPI write、RF workflow、safety rejection 與 `INV` 不會自動重試 |
| README／使用手冊／測試報告 | 完成核心 | 中英雙語 README、SOP、Web guide、acceptance report、Demo script 與 artifacts 均存在 |
| Loopback | 完成 | RF1.1 → RF1.5 direct-cable 多輪 SingleShot／sweep HIL |
| DUT／UDBox | 未完成 | 尚無已核准 routing、path-loss profile、接線證據與 HIL；不能用 Loopback 結果代替 |
| GitHub／CI／Demo | 大致完成 | Git history、PR 合併、Windows Python 3.11 CI、final-project deck 與 10–15 分鐘 Demo script 已有；最終現場演練與交付 tag/release 仍待執行 |

### 5. 依評估標準的現況

這是 gap review，不是假裝成導師正式打分。

| 權重 | 現況 | 強項 | 主要扣分風險 |
|---|---|---|---|
| 40% 技術實現 | 接近完成 WLAN loopback 主線 | 完整 SingleShot、頻率／功率 sweep、安全 cleanup、Web jobs、artifacts、176 點頻寬矩陣、Pandas／Matplotlib PNG 與連線診斷 bounded retry | MCS、NR FR1、Constellation、DUT／UDBox、正式 calibration 與 RF workflow retry policy 尚缺 |
| 25% 程式碼品質 | 良好 | transport／registry／workflow／results／Web 分層，安全限制可單測，繁中關鍵註解 | ruff／mypy 仍非阻斷；retry 與 structured audit logging 尚未產品化 |
| 20% 文件與報告 | 強 | README、使用手冊、SOP、SCPI matrix、acceptance、Demo、雙語文件與 raw/normalized artifacts | 需要一份正式最終測試報告，並將此日誌持續每日更新 |
| 15% 學習態度 | repository 可證明主動迭代 | 問題留下 evidence，錯誤結果不刪除；多次主動修正安全、UI 與 HIL 流程 | 態度仍須由 mentor 依週報、提問與合作行為評分，Git 歷史只能作輔證 |

### 6. 已發生問題、解法與選擇理由

| 問題 | 如何發現 | 解法 | 為何這樣選 |
|---|---|---|---|
| CMP 型號字串不符合過窄判斷 | 真實 `*IDN?` 連線失敗 | 接受經驗證的 CMP model token，保留 identity gate | 兼容實機回應，同時避免連錯儀器 |
| `SYST:ERR?` 無錯誤回應可能以 `+0` 開頭 | setter 後被誤判為錯誤 | 接受已觀察的 no-error prefixes | 依實機證據修正 parser，不硬編單一字面值 |
| SingleShot 只保存 average | 五組 statistics HIL 需求 | 保存 average/current/min/max/std_dev 全部 28 欄 | 保留完整儀器資訊，便於診斷與報告重建 |
| -60 dBm power point 回傳 `INV`，舊流程仍標 complete | power sweep HIL | critical fields 必須 finite，遇 `INV` 立即停止並保留 partial artifacts | `INV` 不能轉成 0 或 PASS；部分結果是重要故障證據 |
| Web 自訂掃描曾顯示自訂值但執行固定 profile | 輸入與實際頻點不一致 | UI plan 與 backend 使用同一計畫；拒絕時顯示原因且不送 RF | 防止 operator 認知與實際 RF 行為分離 |
| 量測長時間維持 `RUN` | 60／120 秒 timeout 與 CMsquares 唯讀檢查 | 將 Measurement Repetition 明確設為 `SINGleshot` 並 readback；不碰未驗證 ARB Sequencer | 根因是 state/profile drift；最小化狀態變更比 Reset 安全 |
| `RDY` 主狀態但結果含 `INV` | 28 欄結果與 full substate 對照 | 同時檢查 full state、reliability 與 critical numeric fields | 單看主狀態會產生 false PASS |
| GPRF power 約差 15.8 dB | 量測值與 generator 設定比較 | 將 GPRF power measurement 切成 CW；完成後恢復 ARB/waveform | WLAN ARB burst 不適合當作 CW path-power 基準；回復原狀避免影響 WLAN |
| 校正值可能被誤當正式證書 | Draft 0 dB example 與正式使用路徑審查 | Draft／Approved、證據／核准者／日期、expiry、route match、禁止外插 | 防止看似合理但無 traceability 的 correction 汙染結果 |
| Web run history 曾空白／卡住 | DOM mutation loop | 改成 deterministic row rendering 與 eager loading | 降低非同步 UI 狀態互相觸發造成的不穩定 |
| 舊 Web server 共用 port 導致新頁面打到舊 API | `Not found` 與 stale process | exclusive bind | 讓錯誤在啟動時明確失敗，避免隱性版本錯配 |
| 實機 driver 未安裝會破壞 CI collection | 非硬體 CI import | 將 RsInstrument 延遲到 `connect()` 時匯入 | Mock、config 與 unit tests 不應依賴可選硬體套件 |

### 7. 歷史開發日誌（由可追溯紀錄重建）

| 日期 | 當日進度 | 問題／學習 | 下一個開發日 |
|---|---|---|---|
| 2026-08-13 | 初始化 Python 3.11 CMP180 automation repository | 先建立可測試骨架，避免直接把 SCPI 寫進 GUI | 建立 config、transport、Mock 與 workflow 分層 |
| 2026-08-18 | 整合 phase-2 framework；完成 query-only hardware validation、文件流程、real connection 與 WLAN query registry | 真實 ID token 與預期不同 | 依實機回應修正 identity validation，開始 SingleShot |
| 2026-08-19 | 完成 SingleShot、安全驗證、28 欄 artifacts、Web GUI 與 GitHub Actions | 需嚴格分清 Mock 與實機證據 | 將硬體 HIL 與 CI 分開，補齊操作文件 |
| 2026-08-20 | 保存五組 statistics；完成 frequency／power sweep core、Web jobs、run history、limit draft、UI 與多輪 HIL | `INV` 曾被誤標 complete；-60 dBm 無效 | 加 finite/validity gate、停止策略與 partial artifacts；改跑 -55～-40 dBm |
| 2026-08-25 | 完成 calibration profile／wizard／adapter framework、自訂 sweep software path、run 管理與進階 Web 分析 | 固定 profile 因 waveform／trigger drift 回 `INV`；V2 UI 不符操作習慣 | 保留失敗證據；恢復正式 `static/`，把有價值分析功能移回；等待受控 HIL |
| 2026-08-27 | 找到 Baseband ARB／ARB Sequencer 混用與 profile drift；SingleShot、3 點 frequency、4 點 power 重過 HIL；補診斷 snapshots 與能力模型 | 狀態集合容易被誤讀，且自訂 UI 可能與實際固定 profile 不一致 | 增加 full-state evidence 與 capability layers；下一日修正 plan execution contract |
| 2026-08-28 | 自訂 plan 與實際 hardware action 對齊；拒絕理由、直接單位、live progress／trend 完成 | 400 MHz 輸入不得被靜默替換成 6 GHz fixed sweep | 讓 workflow gate 明確拒絕未核准組合，不做 fallback RF |
| 2026-09-01 | 新增 resumable HIL Campaign Runner；處理 `RUN` timeout；設定 `SINGleshot` repetition 後 golden／49 點 frequency／26 點 power campaign 通過 | cleanup 曾誤碰 ARB Sequencer；repetition 漂移為 Continuous | 限定只用已驗證 Baseband ARB state tree，將 repetition/readback 納入 backend |
| 2026-09-02 | 完成 11 個 WLAN band/bandwidth 區段、176/176 channel centers；建立 GPRF power workflow，修正 route 與 CW mode；核准 Web WLAN sections | WLAN ARB burst 造成 GPRF power 偏差；formal calibration 仍缺 | 用 CW 做 path-power，結束恢復 ARB；下一日完成 acceptance gate 與交付文件 |
| 2026-09-03 | 新增 acceptance sign-off gate、核准 V1 profiles、修 CI optional-driver import、架構圖、final-project deck、Pandas/Matplotlib PNG、bounded connection retry 與 Week 1–12 日誌；同日把 PNG 自動同步至 Web、補齊圖表軸標題／刻度、開放 profile-gated 自訂 SingleShot 輸入；後續修正為 Single/Frequency/Power 共用同一套 Web SVG 互動與 Matplotlib 選單式單張預覽，功率掃描 PNG 依 Generator Power 畫 X 軸，首頁互動圖改用 `present=1` 模式；query-only preflight 與完整測試通過 | V1 loopback acceptance 不能被說成 DUT compliance；自訂 SingleShot 尚未做新實機回歸，DUT／UDBox／正式校正缺少現場輸入；先前縮圖設計會讓使用者誤以為只有 SingleShot 同步 | 取得 calibration equipment、route、power limit 與 owner approval，再做低功率 HIL |

### 8. Week 1–8 逐日開發日誌與原計畫對照

下表把簡報的前八週拆成每日工作單位，並以現有 Git／HIL 證據標示實際成果。日期不是虛構的逐字工時紀錄；沒有獨立 commit 日期的工作，以 `規劃／整併` 標示。

| 週／日 | 當日主題 | 實際進度／證據 | 問題與決策 | 隔日目標 |
|---|---|---|---|---|
| W1-D1 | RF 與 dB 基礎 | 建立 frequency、power、loss、input limit 的名詞與單位邊界 | dBm 與 dB 不可混用 | 整理 EVM 指標 |
| W1-D2 | EVM 概念 | 定義 all/data/pilot EVM、越負越好與 invalid token | EVM dB 方向容易反判 | 建立 validity 規則 |
| W1-D3 | CMP180 架構 | 確認 2×VSA／2×VSG、2×8 ports 與 catalog capability | 型錄不代表 option/HIL | 建立 capability layers |
| W1-D4 | RF 安全 | 定義 routing、expected input、attenuation、power envelope 與 RF Off 原則 | 不允許用 Reset 當除錯捷徑 | 撰寫 preflight |
| W1-D5 | 第一週回顧 | 形成安全 invariants 與學習資源清單 | RF 理論與 CMP180 指令來源必須分開 | 進入手動流程研究 |
| W2-D1 | CMsquares 導覽 | 觀察 Generator／Analyzer／Measurement flow | GUI 狀態不可直接等同 SCPI | 記錄 route/waveform |
| W2-D2 | Loopback 接線 | 建立 RF1.1 → RF1.5 參考路徑 | path loss 尚未 traceable | 保留 0 dB 為 Draft |
| W2-D3 | WLAN 手動流程 | 對照 setup、initiate、fetch、stop | stored `FETCh` 不是新量測 | 定義完整 workflow |
| W2-D4 | Trigger／ranging | 觀察 IF Power、threshold、expected nominal power | profile drift 會造成 `INV` | 規劃 readback evidence |
| W2-D5 | 第二週回顧 | 整理 CMsquares lessons 與 operator SOP | 只借鑑安全互動，不複製未驗證控制 | 進入 Python 架構 |
| W3-D1 | Python 專案骨架 | 2026-08-13 初始化 Python 3.11 repository | 避免把 GUI、SCPI、business logic 混在一起 | 建 config models |
| W3-D2 | Typed config | 建立 instrument／routing／WLAN models 與 YAML | cross-field safety 不能只靠型別 | 建 validators |
| W3-D3 | Session abstraction | 建立 real／Mock instrument interface | RsInstrument 是 optional dependency | 延遲匯入 driver |
| W3-D4 | SCPI registry | 集中 command map 與 typed registry | 未驗證 command 維持 `null` | 補 query-only discovery |
| W3-D5 | 單元測試 | 建立 Mock、loader、identity、registry tests | CI 不應需要實機 | 建 connection diagnostic |
| W4-D1 | Query-only 連線 | 2026-08-18 完成 `*IDN?`／`*OPT?`／error queue | 真實 model token 不同 | 只擴充經驗證 token |
| W4-D2 | WLAN discovery | 註冊經內建 Help／實機確認的 query | 不移植其他 R&S 儀器命令 | 建 setter validation |
| W4-D3 | Generator setter | 同值寫入、readback、error queue 與 RF Off gate | setter 也有狀態副作用 | 保持顯式確認 |
| W4-D4 | Analyzer setter | frequency、bandwidth、expected power、trigger readback | 單看 write 成功不足 | 以 readback 驗收 |
| W4-D5 | 第四週回顧 | real connection 與基本控制層完成 | 仍未構成完整量測 | 進入 SingleShot |
| W5-D1 | State machine | 定義 connect→configure→RF on→initiate→fetch→cleanup | 任一例外都可能留下 RF | 全流程 `try/finally` |
| W5-D2 | SingleShot backend | 2026-08-19 完成完整 Python workflow | `READ/INIT` 會啟動量測 | 嚴格 gate 與 timeout |
| W5-D3 | 28 欄 parser | 保存 raw response 與 normalized fields | `INV` 不可轉 0 | 建 validity checks |
| W5-D4 | Artifacts | CSV、JSON、metadata、raw、HTML | 報告必須離線重建 | 補 visualization |
| W5-D5 | SingleShot HIL | RF1.1→RF1.5、6105 MHz、320 MHz、-40 dBm 通過 | Mock 與 live evidence 分開 | 擴充五組 statistics |
| W6-D1 | Power sweep core | 2026-08-20 建立安全 power plan／point loop | caller 不可放寬硬上限 | 加 bypass tests |
| W6-D2 | Invalid point handling | -60 dBm 回 `INV` 曾被誤標完成 | 立即停止並保留 partial artifact | 改跑有效候選區間 |
| W6-D3 | Power HIL | -55／-50／-45／-40 dBm 四點通過 | profile/waveform 仍會漂移 | 保存 final RF/state/errors |
| W6-D4 | Web power job | async progress、cancel、single-active-job | cancel 只能在 RF Off 點界生效 | 加 job tests |
| W6-D5 | 圖表 | Web EVM vs Power 與 dependency-free SVG | 簡報指定 Pandas/Matplotlib 尚缺 | 後續補 PNG engine |
| W7-D1 | Frequency sweep | 三點 frequency HIL 與 bounded plan | 頻率、功率、點數皆為 hard ceiling | 擴大 WLAN matrix |
| W7-D2 | Channel/bandwidth model | 2.4／5／6 GHz 合法中心與頻寬規則 | 400 MHz–8 GHz 不全是 WLAN | 分段 Approved Profile |
| W7-D3 | Waveform matching | 依 bandwidth 選 waveform 並 absolute-path readback | waveform drift 造成結果失效 | RF Off/idle 才切換 |
| W7-D4 | MCS review | 確認現況只有 EHT MCS11 基線 | 無多 MCS 自動 sweep/HIL | 列為 scope gap |
| W7-D5 | NR FR1 review | 確認型錄能力但 repository 未實作 | catalog 不等於 installed/verified | 列為獨立 scope expansion |
| W8-D1 | Reliability | full state、reliability 與 critical metrics 聯合判定 | `RDY` 仍可能伴隨 `INV` | 保存 diagnostic snapshot |
| W8-D2 | Limit profile | Draft／Approved lifecycle、margin、compliance claim | 沒 approved limit 不顯示 PASS | 取得 owner approval |
| W8-D3 | Offline report | SVG／HTML、saved CSV redraw | GUI 不能是唯一報告路徑 | 補 Pandas/Matplotlib |
| W8-D4 | Run analysis | history、2–8 run compare、trace、export | 不允許歷史分析觸發 RF | 維持 read-only API |
| W8-D5 | 第八週回顧 | WLAN core、報告與 reliability 已成形 | Constellation、MCS、NR 仍缺 | 進入 trigger/calibration 優化 |

### 9. Week 9–12 逐日執行計畫

每一天都要留下：commit／PR、測試結果、Mock／stored／live RF 證據類型、問題與隔日計畫。實機日開始前必須讀 `docs/hardware-test-sop.md`，確認 RF Off、measurement idle、error queue、routing、frequency、bandwidth、power、loss 與 input limit；所有 RF workflow 保持 `try/finally` cleanup。

| 週／日 | 當日目標 | 完成定義 | 隔日銜接 |
|---|---|---|---|
| W9-D1 | 建立 trigger／timeout fault taxonomy | 區分 VISA I/O、OPC、measurement RUN、invalid result；對應錯誤碼與 log 欄位 | 寫 deterministic unit/Mock fault tests |
| W9-D2 | timeout 與 cancellation 測試 | timeout／cancel 均驗證 STOP／ABORT、RF Off、final state、error queue | 準備 query-only trigger matrix |
| W9-D3 | trigger／ranging readback review | 核對 source、threshold、timeout、expected nominal power；未知 SCPI 保持 `null` | 只有通過 review 才申請短 HIL |
| W9-D4 | Path Loss data contract | 確認 route ID、equipment ID、certificate、date、expiry、frequency/loss schema | 準備校正設備 adapter 或人工 CSV SOP |
| W9-D5 | Calibration Profile dry run／review | Draft 建立、內插、越界拒絕、核准欄位測試全過；不宣稱正式校正 | 安排 RF owner 與校正設備時段 |
| W10-D1 | 錯誤分類與 retry policy | **已完成安全核心**：僅 transient connection/timeout 可 retry；SCPI error、safety rejection、`INV` 不 retry | 評估是否需要 RF workflow 專用 policy |
| W10-D2 | retry engine 與 cleanup | **已完成 query-only 連線診斷整合**：0–5 次、每次 retry 前 disconnect；測試成功／耗盡／非 transient | 不自動重送 SCPI write；先做 HIL review |
| W10-D3 | logging／audit schema | run ID、operator、action、profile revision、SCPI redaction、state transition、attempt、elapsed time | 加 log tests 與 retention/redaction 文件 |
| W10-D4 | README／user guide 同步 | 快速開始、功能矩陣、Mock/stored/live labels、failure recovery 完整雙語 | 交由 mentor 依新手路徑走讀 |
| W10-D5 | quality gate | pytest、兩份 YAML validation、`git diff --check`；ruff/mypy findings 分類 | 修阻斷問題，凍結 Week 11 HIL candidate |
| W11-D1 | Loopback regression | golden SingleShot + bounded frequency/power sweep；保存完整 cleanup evidence | 若通過，鎖定 reference baseline |
| W11-D2 | 正式 path-loss capture | 以校正過的 source/receiver 或核准設備取得 readings；RF owner 審查 | 建立 Approved profile，不使用 0 dB placeholder |
| W11-D3 | DUT 接法 preflight | 確認 port、attenuator、DUT output、trigger、maximum input、reference plane；先 query-only | 取得明確現場授權後才跑低功率短測 |
| W11-D4 | UDBox 接法 preflight／短測 | 建立獨立 route/profile，不沿用 loopback 校正；完成 safe short HIL 或記錄 blocker | 比較三情境 metadata 與結果有效性 |
| W11-D5 | Demo rehearsal 1 | 10–15 分鐘：Demo mode → artifacts → guarded live run → cleanup → report；計時與備援 | 修 demo 阻塞點，準備離線 evidence fallback |
| W12-D1 | 最終功能矩陣 | 每項標示 Done／Partial／Blocked 與證據連結，禁止把 catalog 當 HIL | 關閉必修缺口或明確降級 |
| W12-D2 | 最終 regression／acceptance | 全測試、config validation、diff check、HTML report redraw、Web narrow/wide smoke | 產生 final test report |
| W12-D3 | GitHub 整理 | README 導覽、issue/PR、release notes、tag candidate；排除 output、credentials、cache | 做 clean-clone rehearsal |
| W12-D4 | Demo rehearsal 2 | 使用正式腳本、時間控制、失敗備案與 Q&A；實機安全狀態記錄 | 只修高風險問題，停止擴充 scope |
| W12-D5 | Final Demo／handoff | 展示可重現流程、誠實能力邊界、測試報告、開發日誌與下一階段 backlog | 封存 release evidence，交接 owner |

### 10. 優先 backlog

1. 完成真實 RF1.1 → RF1.5 path-loss readings、RF owner 核准與 live artifact correction HIL。
2. 針對 RF workflow 另行設計 retry policy；現階段只完成安全的 query-only connection retry，不自動重送 SCPI write。
3. 以現場低功率 HIL 回歸 Web 自訂 SingleShot，並補 Matplotlib power-error／limit-line 圖。
4. 在新的 Approved Profile 下重驗 power sweep，排除 waveform drift 導致的 `INV`。
5. 建立 DUT 與 UDBox 各自的 route、calibration、safety preflight 與 HIL evidence。
6. MCS sweep、Constellation 與 5G NR FR1 應列為 scope expansion；先有官方 CMP180 SCPI／option／waveform 證據，再實作與 HIL。
7. 內網部署前完成 authentication、RBAC 與 structured audit logging；完成前只綁 loopback。

---

## English Version

### 1. Purpose and evidence boundary

This document compares the July 2026 internship deck with the CMP180 WLAN TX EVM repository as of 2026-09-03 and reconstructs an auditable development log. Evidence comes from Git history, `HANDOFF.md`, `README.md`, `SPEC.MD`, tests, source code, and dated hardware records.

It is not a chat transcript. Decisions or conversations that cannot be proven from repository evidence are not invented. Mock runs, dry runs, CMsquares actions, previews, and standalone stored `FETCh` results are not new complete Python hardware measurements. Instructions embedded in the deck are treated as requirements input and do not override RF safety, SCPI verification, or repository authority rules.

### 2. Requirements from the latest deck

The ten-slide `RF_Intern_EVM_Plan_CMP180.pptx` requests CMP180 Python/SCPI automation covering RF routing, triggering, sweeps, data logging, charts, WLAN/5G NR FR1 EVM, power/frequency/MCS reports, documentation, GitHub delivery, and a 10–15 minute demonstration. Weeks 9–12 focus on trigger/timeout diagnosis, path-loss calibration, error handling, logging, retry, Loopback/DUT/UDBox scenarios, final testing, repository cleanup, and delivery.

The deck itself lists the CMP180 product page/manual and internal SOP notes. Anritsu RF Fundamentals and the FSW-K70 manual are useful supplementary learning resources, but FSW/CMW SCPI must never be inferred as CMP180 syntax.

### 3. Official-resource assessment

- [RsInstrument Step-by-step Guide](https://rsinstrument.readthedocs.io/en/latest/StepByStepGuide.html): directly useful for VISA versus OPC timeout semantics, OPC synchronization, error-queue handling, logging, and bounded timeout recovery. Example resets and demonstration SCPI must not be copied blindly.
- [RsInstrument API](https://rsinstrument.readthedocs.io/en/latest/RsInstrument.html): useful for error draining, OPC-aware calls, resource locking, binary transfer, and logger APIs.
- [R&S Examples](https://github.com/Rohde-Schwarz/Examples) and [R&S GitHub](https://github.com/Rohde-Schwarz): useful for session, reliability, status-checking, and shared-session patterns. No directly reusable CMP180 WLAN EVM example was identified; other-instrument commands remain non-authoritative.
- [CMP180 Product Page](https://www.rohde-schwarz.com/us/products/test-and-measurement/wireless-tester-rf-analyzer-generator/cmp180-radio-communication-tester_63493-1081280.html): authoritative for catalogue capability such as up to 8 GHz, up to 500 MHz, 2×VSA, 2×VSG, and 2×8 RF ports. Catalogue capability is not installed-option, approved-profile, or HIL evidence.
- [Anritsu RF Fundamentals](https://www.anritsu.com/en-us/test-measurement/support/training-and-education/elearning/rf-fundamentals): useful for dB, modulation, impairments, coaxial cables, components, and propagation.
- [FSW-K70 VSA Manual](https://www.rohde-schwarz.com/au/manual/r-s-fsw-k70-vsa-user-manual-manuals_78701-29049.html): useful for VSA/EVM and result-interpretation concepts, but not as a CMP180 SCPI source.

Recommended order: learn RsInstrument connection, timeout, OPC, logging, and error-handling patterns; verify every actual command in CMP180 built-in Help or its official manual; use GitHub examples for architecture patterns; use Anritsu and FSW-K70 only for RF/VSA theory.

### 4. Completion against the deck

The WLAN loopback core is strong: connection and discovery, a complete Python SingleShot, 28 fields across five statistics, guarded frequency and power sweeps, deterministic cleanup, result artifacts, Web jobs, and 176/176 channel centres across 11 legal WLAN band/bandwidth sections all have evidence.

The following remain partial or incomplete:

- Pandas CSV/DataFrame loading and Matplotlib Agg PNG output are implemented, tested, and synchronized to the Web Results selector for newly saved runs. Power-sweep PNGs use Generator Power (dBm) as the X axis, and the dependency-free SVG/HTML path remains available.
- MCS sweep, constellation acquisition/rendering, and 5G NR FR1 automation are not implemented.
- Trigger/timeout diagnosis is substantially implemented, but native RsInstrument OPC/timeout classification can be integrated more completely.
- Calibration lifecycle, interpolation, expiry, evidence gates, Web wizard, adapter framework, and application logic exist; traceable real readings and external-adapter HIL do not.
- Error cleanup is implemented. File logging exists, but structured audit logging and intranet RBAC remain incomplete.
- A bounded 0–5 retry core now handles only transient query-only connection diagnostics and disconnects before each retry. It never automatically repeats SCPI writes, RF workflows, safety rejections, or invalid results.
- Loopback is hardware verified. DUT and UDBox routes, calibration profiles, safety preflights, and HIL are not complete.
- README, guides, acceptance material, final-project deck, CI, and demo script exist; a final on-site rehearsal and release/tag remain delivery tasks.

### 5. Evaluation view

- **40% technical implementation:** strong WLAN loopback core, with material gaps in the named Pandas/Matplotlib deliverable, MCS, NR FR1, constellation, formal calibration, retry, DUT, and UDBox.
- **25% code quality:** good separation among transport, registry, workflows, results, and Web layers; safety rules are unit-testable. Ruff and mypy remain advisory, and retry/audit logging still need productization.
- **20% documentation and reporting:** strong bilingual README, operator guides, SOP, SCPI matrix, acceptance report, demo script, and raw/normalized artifacts. A final signed test report and continuously maintained daily log are still needed.
- **15% learning attitude:** Git evidence shows iterative diagnosis, preservation of failed evidence, and proactive safety/UX improvement. Mentor observation remains required for the actual score.

### 6. Key problems, solutions, and rationale

- Real ID matching was too narrow; it was expanded only for the verified CMP token so connection remained fail-safe.
- `+0` no-error responses were initially misclassified; parsing was aligned to observed instrument evidence.
- Only average results were stored; all five statistics are now preserved for diagnosis and reproducibility.
- An invalid -60 dBm point was once marked complete; finite/validity gates now stop safely and retain partial artifacts.
- Custom Web inputs once executed fixed profiles; the UI and backend now share one plan, and rejected plans transmit no RF.
- Measurements remained in `RUN` because repetition drifted to Continuous; the backend now sets and reads back `SINGleshot` without resetting the workspace.
- Main state `RDY` hid invalid substate/data; full state, reliability, and critical numeric fields are now evaluated together.
- GPRF path-power readings were biased by a burst WLAN ARB waveform; CW is used for power characterization and ARB/waveform state is restored afterward.
- Draft calibration values could look official; approval evidence, owner/date, expiry, route matching, and no-extrapolation gates prevent untraceable correction.
- A Web history mutation loop and stale shared server port caused UI failures; deterministic rendering and exclusive bind made failures explicit and reproducible.
- Optional RsInstrument imports broke non-hardware CI collection; the driver is now imported only on real connection.

### 7. Reconstructed daily history

- **2026-08-13:** initialized the Python 3.11 repository and chose a testable layered structure.
- **2026-08-18:** integrated the framework, query-only validation, documentation workflow, real connection, and verified WLAN queries; corrected real identity matching.
- **2026-08-19:** completed SingleShot, safety validation, artifacts, Web GUI, and CI; separated Mock/CI claims from live RF evidence.
- **2026-08-20:** added five statistics, frequency/power sweeps, asynchronous jobs, run history, draft limits, UI work, and multiple HIL runs; fixed invalid-point completion and preserved partial evidence.
- **2026-08-25:** added calibration profiles, wizard, adapter framework, custom-sweep software wiring, run management, and richer analysis; retained failed `INV` evidence and restored the supported `static/` UI after review.
- **2026-08-27:** resolved Baseband ARB versus ARB Sequencer state mixing and profile drift; passed SingleShot and fixed short sweeps; added diagnostic snapshots and layered capability reporting.
- **2026-08-28:** aligned the displayed custom plan with actual RF execution, exposed rejection reasons, and added direct units and live point-boundary results.
- **2026-09-01:** added the resumable campaign runner, diagnosed Continuous repetition as the `RUN` timeout cause, enforced SingleShot, and passed golden, 49-point frequency, and 26-point power campaigns.
- **2026-09-02:** completed 11 WLAN bandwidth sections and 176/176 channel centres; corrected GPRF routing and CW measurement; approved the verified Web WLAN sections.
- **2026-09-03:** completed acceptance gates, V1 profile approval, optional-driver CI repair, architecture diagrams, and the final-project deck; then synchronized Matplotlib PNGs to Web Results, repaired chart axes/ticks, added profile-gated custom SingleShot input, changed Matplotlib display to a selector-driven single preview, fixed power-sweep PNG X-axis selection, and embedded both diagrams in `present=1` interactive mode on the home page.

### 8. Week 1–8 daily history

The following table mirrors the detailed Chinese history. Rows without a separately dated commit are reconstructed planning units rather than invented time records.

| Week/day | Topic | Progress/evidence | Problem and decision | Next workday |
|---|---|---|---|---|
| W1-D1 | RF and dB basics | Defined frequency, power, loss, and input-limit units | dBm and dB must not be mixed | Organize EVM metrics |
| W1-D2 | EVM concepts | Defined all/data/pilot EVM, more-negative-is-better, and invalid tokens | EVM direction is easy to reverse | Define validity rules |
| W1-D3 | CMP180 architecture | Confirmed 2×VSA, 2×VSG, 2×8 ports, and catalogue capability | Catalogue is not option/HIL proof | Define capability layers |
| W1-D4 | RF safety | Defined routing, expected input, attenuation, power envelope, and RF-Off rules | Reset is not a debugging shortcut | Write preflight rules |
| W1-D5 | Review | Consolidated safety invariants and learning resources | RF theory and CMP180 command evidence must remain separate | Study the manual workflow |
| W2-D1 | CMsquares tour | Observed Generator, Analyzer, and Measurement flow | GUI state is not SCPI evidence | Record route and waveform |
| W2-D2 | Loopback cabling | Established the RF1.1-to-RF1.5 reference route | Path loss was not traceable | Keep 0 dB as Draft only |
| W2-D3 | Manual WLAN flow | Compared setup, initiate, fetch, and stop | Stored `FETCh` is not a new measurement | Define the complete workflow |
| W2-D4 | Trigger/ranging | Observed IF Power, threshold, and expected nominal power | Profile drift can produce `INV` | Plan readback evidence |
| W2-D5 | Review | Consolidated CMsquares lessons and operator SOP | Borrow safe interaction patterns only | Begin Python architecture |
| W3-D1 | Python skeleton | Initialized the Python 3.11 repository on 2026-08-13 | GUI, SCPI, and business logic must not be mixed | Build config models |
| W3-D2 | Typed config | Added instrument, routing, WLAN models, and YAML | Cross-field safety needs separate validation | Build validators |
| W3-D3 | Session abstraction | Added real and Mock instrument interfaces | RsInstrument is optional | Delay driver import |
| W3-D4 | SCPI registry | Centralized command map and typed registry | Unverified commands remain `null` | Add query-only discovery |
| W3-D5 | Unit testing | Added Mock, loader, identity, and registry tests | CI must not require hardware | Build connection diagnostics |
| W4-D1 | Query-only connection | Completed ID, options, and error-queue checks on 2026-08-18 | Real model token differed | Expand only the verified token |
| W4-D2 | WLAN discovery | Registered queries confirmed by Help/hardware | Never transplant commands from other instruments | Build setter validation |
| W4-D3 | Generator setter | Added same-value write, readback, error queue, and RF-Off gate | Setters still change state | Keep explicit confirmation |
| W4-D4 | Analyzer setter | Added frequency, bandwidth, expected-power, and trigger readback | Write success alone is insufficient | Accept by readback |
| W4-D5 | Review | Completed real connection and basic control layers | This was not yet a complete measurement | Begin SingleShot |
| W5-D1 | State machine | Defined connect, configure, RF on, initiate, fetch, and cleanup | Any exception may leave RF active | Use `try/finally` throughout |
| W5-D2 | SingleShot backend | Completed the Python workflow on 2026-08-19 | `READ/INIT` starts measurement | Apply strict gates/timeouts |
| W5-D3 | 28-field parser | Preserved raw and normalized fields | `INV` must not become zero | Add validity checks |
| W5-D4 | Artifacts | Added CSV, JSON, metadata, raw, and HTML | Reports must be reproducible offline | Add visualization |
| W5-D5 | SingleShot HIL | Passed RF1.1-to-RF1.5 at 6105 MHz, 320 MHz, -40 dBm | Separate Mock and live evidence | Add all five statistics |
| W6-D1 | Power-sweep core | Added a bounded safe plan/point loop on 2026-08-20 | Callers must not relax hard limits | Add bypass tests |
| W6-D2 | Invalid-point handling | Found -60 dBm `INV` incorrectly marked complete | Stop and retain partial artifacts | Use the valid candidate range |
| W6-D3 | Power HIL | Passed -55, -50, -45, and -40 dBm | Profile/waveform can drift | Preserve final RF/state/errors |
| W6-D4 | Web power job | Added async progress, cancellation, and one-active-job lock | Cancel only at an RF-Off point boundary | Add job tests |
| W6-D5 | Charts | Added Web EVM-vs-power and dependency-free SVG | Pandas/Matplotlib was still missing | Add PNG engine later |
| W7-D1 | Frequency sweep | Passed three-point HIL with a bounded plan | Frequency, power, and points are hard ceilings | Expand WLAN matrix |
| W7-D2 | Channel/bandwidth model | Added legal 2.4/5/6 GHz centres and bandwidth rules | 400 MHz–8 GHz is not all WLAN | Use segmented approved profiles |
| W7-D3 | Waveform matching | Select by bandwidth and verify absolute-path readback | Waveform drift invalidates results | Switch only while RF Off/idle |
| W7-D4 | MCS review | Confirmed only an EHT MCS11 baseline | No multi-MCS sweep/HIL | Record as a scope gap |
| W7-D5 | NR FR1 review | Confirmed catalogue capability but no repository implementation | Catalogue is not installed/verified | Treat as separate expansion |
| W8-D1 | Reliability | Combined full state, reliability, and critical metrics | `RDY` can coexist with `INV` | Save diagnostic snapshots |
| W8-D2 | Limit profile | Added Draft/Approved lifecycle, margin, and compliance claim | No approved limit means no PASS | Obtain owner approval |
| W8-D3 | Offline report | Added SVG/HTML redraw from saved CSV | GUI cannot be the only report path | Add Pandas/Matplotlib |
| W8-D4 | Run analysis | Added history, 2–8-run comparison, traces, and exports | Historical analysis must never trigger RF | Keep APIs read-only |
| W8-D5 | Review | WLAN core, reporting, and reliability were established | Constellation, MCS, and NR remained open | Begin trigger/calibration hardening |

### 9. Week 9–12 daily plan

The Chinese table above is the authoritative detailed daily checklist. In summary:

- **Week 9:** formalize trigger/timeout fault classes and tests; review readbacks; define calibration evidence; validate draft profiles; schedule traceable capture.
- **Week 10:** define safe retry policy; implement bounded retries with per-attempt cleanup and audit fields; complete structured logging, bilingual documentation, and the quality gate.
- **Week 11:** regress Loopback; capture and approve path loss; separately preflight and test DUT and UDBox routes; rehearse the 10–15 minute demonstration with an offline fallback.
- **Week 12:** freeze the evidence-based capability matrix; run final regression and acceptance; clean repository navigation and release notes; rehearse again; deliver with explicit limitations and next-stage backlog.

Every day must record its commit/PR, validation results, evidence type (Mock, stored, or new live RF), problem encountered, resolution, rationale, and next working-day plan.

### 9. Priority backlog

1. Capture traceable RF1.1-to-RF1.5 path loss, obtain RF-owner approval, and verify live artifact correction.
2. Design a separate RF-workflow retry policy; the implemented retry remains limited to safe query-only connection diagnostics and never repeats SCPI writes automatically.
3. Regress the Web custom-value SingleShot through a low-power on-site HIL, then add Matplotlib power-error and limit-line plots.
4. Revalidate the power profile against waveform drift.
5. Create independent DUT and UDBox route, calibration, safety, and HIL evidence.
6. Treat MCS sweep, constellation, and 5G NR FR1 as controlled scope expansion requiring official CMP180 command/option/waveform evidence before implementation.
7. Complete authentication, RBAC, and structured audit logging before any non-loopback deployment.

---

## 2026-09-03 追加開發紀錄：掃描 artifact 同步、GPRF 分類與異常說明

### 繁體中文

#### 今日目標

使用者回報 Frequency Sweep、Power Sweep、GPRF Frequency Sweep 的 Matplotlib PNG 顯示不一致，且四個實機模式的命名容易讓 GPRF 被誤解為 WLAN EVM。今日目標是確認前後端 artifact 是否同步、補上缺漏的 PNG 產生路徑、把異常原因改成可操作的「原因／如何解決／正確範圍」，並重新分類 SingleShot、Frequency Sweep、Power Sweep、GPRF。

#### 發現的問題

1. WLAN SingleShot、WLAN Frequency Sweep、WLAN Power Sweep 已走 `results.artifacts`，該流程已會從 CSV 透過 Pandas DataFrame 與 Matplotlib Agg 產生 PNG。
2. GPRF 使用獨立的 `web.gprf_service._save_gprf_result()` 保存 CSV／JSON／metadata／HTML，沒有呼叫同一個 Matplotlib 產圖器，因此 GPRF run 即使有 CSV 也不會自動出現 Matplotlib PNG。
3. 前端被拒絕時多半只顯示 `rejection_reason`，使用者知道「被擋」，但不知道「要改哪個欄位、改到什麼範圍」。
4. UI 上的「單點、頻率掃描、功率掃描、GPRF 頻率／功率掃描」沒有清楚說明前三個是 WLAN EVM，GPRF 是 General Purpose RF power reading，不是 WLAN EVM 或 compliance。

#### 解法

1. 在 GPRF 保存流程加入 `write_pandas_matplotlib_plots(csv_path)`，讓 GPRF run 也產生與 WLAN run 一致的 `plots-matplotlib/*.png`，並把 `matplotlib_burst_power_dbm` 等路徑放回 artifacts。
2. 在 WLAN custom plan preview 與 GPRF preview 增加 `rejection_help` 與 `correct_range`，讓後端 API 帶出更完整的可修正資訊。
3. 在 Web 前端新增共用的拒絕訊息格式，顯示：
   - 原因：實際被擋的 gate。
   - 如何解決：該調整頻率、頻寬、功率、dwell、點數、span 或 route。
   - 正確範圍：CMP180 UI planning range 與目前 approved/HIL RF execution range。
4. 將四種模式重新命名與分類：
   - WLAN EVM SingleShot：單一中心頻率的 WLAN EVM 量測。
   - WLAN EVM Frequency Sweep：固定功率，量測 EVM 對頻率變化。
   - WLAN EVM Power Sweep：固定頻率，量測 EVM 對 Generator power 變化。
   - RF Power Reading (GPRF)：General Purpose RF，只讀 RF power，檢查 tune／power flatness，不是 WLAN EVM。

#### 為何這樣選

GPRF 的能力與 WLAN EVM 不同；如果把 GPRF 改成共用 WLAN workflow，會造成 measurement family 混淆，也可能讓使用者誤以為 RF power reading 是 EVM compliance。正確作法是保留 GPRF 獨立 workflow，但讓它共用同一個 artifact/plot 產生器，確保結果頁體驗一致，同時在 UI 和 metadata 中明確標示 `measurement_family=GPRF_POWER` 與 `compliance_claim=false`。

SingleShot 的 400–8000 MHz 輸入範圍保留為 CMP180 型錄／UI planning envelope；但真正送 RF 仍受 WLAN approved/HIL profile 及現場確認限制。這不是拖延，而是避免在準備接 UDBOX0630 時，用未校正路徑或未知 DUT 保護狀態直接發射 RF。

#### 驗證

- JavaScript syntax check：`node --check` 通過 `app.js`、`hardware.js`、`custom-plan.js`、`gprf-power.js`。
- Targeted unit tests：`tests/unit/test_gprf_power_service.py` 與 `tests/unit/test_custom_plans.py` 共 19 passed。
- 測試資料類型：Mock／offline unit test；沒有新 live RF，也沒有 UDBOX0630 HIL。

#### 明日／下一工作日計畫

1. 針對 UDBOX0630 建立「一鍵 evidence package」工作流：先跑低功率 HIL，成功後同步 run artifacts、metadata、開發日誌 entry、README update draft；若任一步失敗，保留 partial artifact，不自動宣稱完成。
2. 取得正式 Path Loss／DUT／UDBox 接線資料、reference plane、RF owner 核准與實機時段。
3. 用低功率 SOP 驗證 UDBOX0630 route，先證明 RF OFF cleanup、error queue、power reading 與 metadata 正確，再考慮 WLAN EVM DUT profile。

### English

#### Goal

The user reported that Matplotlib PNG artifacts were inconsistent for Frequency Sweep, Power Sweep, and GPRF Frequency Sweep, and that the four hardware modes were difficult to classify. The goal was to verify frontend/backend synchronization, fill the missing PNG path, make rejection messages actionable, and separate WLAN EVM workflows from GPRF RF-power checks.

#### Findings

1. WLAN SingleShot, WLAN Frequency Sweep, and WLAN Power Sweep already use the shared `results.artifacts` path, which generates Matplotlib PNGs from CSV/DataFrame data.
2. GPRF used its own `web.gprf_service._save_gprf_result()` path and did not call the shared Matplotlib generator.
3. The frontend mostly displayed only `rejection_reason`, which explained that a plan was blocked but not how to fix it.
4. The four mode labels did not clearly show that the first three modes are WLAN EVM workflows while GPRF is General Purpose RF power reading, not WLAN EVM or compliance.

#### Resolution

1. Added shared Matplotlib artifact generation to the GPRF save path.
2. Added `rejection_help` and `correct_range` fields to WLAN custom-plan and GPRF previews.
3. Added a shared frontend formatter that displays reason, fix guidance, and valid range.
4. Reclassified the modes as WLAN EVM SingleShot, WLAN EVM Frequency Sweep, WLAN EVM Power Sweep, and RF Power Reading (GPRF).

#### Rationale

GPRF must remain a separate measurement family because it is RF power reading, not WLAN EVM demodulation. Sharing the artifact generator gives users a consistent report experience without overstating compliance capability. The 400–8000 MHz SingleShot input range remains a planning/UI envelope, but live RF execution remains profile-gated until HIL and safety approval are complete.

#### Validation

- JavaScript syntax checks passed for `app.js`, `hardware.js`, `custom-plan.js`, and `gprf-power.js`.
- Targeted unit tests passed: 19 tests across `tests/unit/test_gprf_power_service.py` and `tests/unit/test_custom_plans.py`.
- Evidence type: Mock/offline unit tests only; no new live RF or UDBOX0630 HIL was run.

#### Next working day

Build the UDBOX0630 evidence-package workflow, obtain formal path-loss and routing approvals, then execute low-power HIL under SOP before claiming any DUT/UDBox WLAN EVM capability.
