# CMP180 WLAN TX EVM Automation

### Language / 語言

[繁體中文](#中文版本) · [English](#english-version)

> GitHub 使用者可透過上方語言選單跳轉；專案文件一律先繁體中文、再英文。
>
> GitHub users can use the language menu above. Project documents always present complete Traditional Chinese content before English.

## 中文版本

Web 現已加入獨立的 Loopback 驗證頁：可執行真正獨立的 WLAN SingleShot repeats、顯示完成 cleanup 後的即時 EVM／Power／Frequency Error 趨勢、標記 INVALID 與 IQR outlier，並分開輸出 Validity、Stability、Reasonableness 與 Overall。2026-09-03 的 6105 MHz／320 MHz／−40 dBm Repeat=10 實機 HIL 為 10/10 valid、Stability PASS、Reasonableness DRAFT_PASS，且 RF 最終為 OFF；該固定條件已升級為具 artifact 來源的 approved loopback profile，核准後第二次 Repeat=10 回歸得到 `LOOPBACK_READY`。其他輸入仍維持 draft，不會宣稱 `LOOPBACK_READY`。

「一鍵執行全部」會依序跑完 11 個已核准 WLAN section 代表點，每點 Repeat=10，共 110 次獨立 SingleShot。2026-09-03 實機批次為 110/110 valid，全部 Stability 與 Reasonableness 通過，且每份 artifact 最終 RF `OFF`、measurement `RDY`、cleanup error 空；11 個代表點已各自以其 HIL artifact 升級為 approved loopback profile。未列入此矩陣的頻率、功率、route 或 UD Box 仍為 draft／blocked。

升級後的 11 個相同代表點已再次完成 Repeat=10 回歸：110/110 valid，11/11 均為 `approved`、Stability PASS、Reasonableness PASS 與正式 `LOOPBACK_READY`。Web 的 SingleShot、WLAN Sweep、GPRF、Loopback、HIL Campaign 與 Calibration 檢查計畫、Preview、安全提示及最後確認會隨中英切換即時更新；切換語言不會重新呼叫 Preview 或 RF endpoint。

Python 3.11+ 的 Rohde & Schwarz CMP180 WLAN TX EVM 自動化系統，用可重現、可稽核的流程取代重複的 CMsquares 手動操作，長期產品為中英雙語、響應式公司內網 Web 工具。

### CMP180 Blender 立體外觀模型

可編輯的 CMP180 Blender 外觀模型、GLB 與驗證渲染位於 [`assets/cmp180_3d/`](assets/cmp180_3d/README.md)。這是依官方資料與參考照片建立的視覺模型，不是機構 CAD，且不會連線或控制儀器。

[![CMP180 系統架構圖](docs/diagrams/system-architecture.png)](docs/diagrams/README.md)

<sub>系統架構：操作員瀏覽器 → Web API → RF 安全閘門 → RF Workflow → CMP180 實機。
可互動版本與 SingleShot 生命週期圖見[架構圖](docs/diagrams/README.md)。</sub>

### 目前能力

- Web 新增可恢復的 `HIL Campaign Runner`：按「準備」可把頻段／頻寬、代表功率、其他 RF route、500 MHz、雙 VSA／VSG 與長 waveform 分類成 READY／BLOCKED；READY 可逐列或按「執行下一個」啟動，進度保存於 `output/hil-campaign/state.json`。BLOCKED 案例不會偷換成既有 profile 執行。

- YAML 驗證、Mock／實機連線、Generator／Analyzer setter、measurement lifecycle 與 RF On／Off。
- 已完成 RF1.1 → RF1.5、6105 MHz、320 MHz、-40 dBm 的 Python 實機 SingleShot。
- 已用同一支 Python 工具完成 11 個 WLAN 區段：2.4／5／6 GHz 搭配合法的 20／40／80／160／320 MHz 組合，共 176/176 個 channel center 有效；完整 400 MHz–8 GHz 仍不是 WLAN 頻段。
- 解析 28 欄 OFDM SISO，輸出 CSV、JSON、metadata、raw response 與 HTML report。
- 雙語響應式橫向量測工作區：Dark／Light、依分頁切換的專業工作區標題、整合式 Demo／實機量測、量測紀錄、多 Run 疊圖比較、可自訂 Trace 名稱／顏色／顯示、Draft 校正 SOP，以及完整 artifacts 與可復原紀錄管理。歷史分析會預先讀取既有 CSV／JSON，不會送出 RF。
- 首頁提供 CMP180 360° 立體檢視：點擊載入後可拖曳／觸控旋轉、縮放、切換正面／背面／側面、重設、手動開啟自轉與全螢幕；載入失敗保留靜態圖並可重試。模型與固定版本檢視器皆為本機資產，首頁互動不呼叫量測或 RF API。操作與重建方式見 [3D 檢視器](docs/cmp180-3d-viewer.md)，全站改善順序見 [網站檢視與改進計畫](docs/web-audit-2026-09-10.md)。
- 首頁直接嵌入 `docs/diagrams/` 的系統架構與 SingleShot 生命週期互動圖，使用 `present=1` 互動／簡報模式；可切換、重新載入或全頁開啟，圖表操作不會呼叫量測 API。
- 導覽明確區分示範與實機量測；一般本機啟動直接提供受保護的實機控制，`--demo-only` 才會停用儀器連線。結果頁顯示安全的相對輸出位置。
- 實機與示範量測共用單點／頻率掃描／功率掃描分頁；結果圖表提供固定座標、受限水平 Zoom／Pan、十字游標與完整點位標值。說明頁涵蓋 GitHub clone、安裝、CLI、Web 與離線報告流程。
- 示範模式不送 RF、不套用實機功率安全上限，可輸入較寬的功率範圍來展示 PA Pin／Pout／Gain／P1dB；「進階 PA 指標」另提供 OIP3／IM3、H2／H3 與 ACP／ACLR 三張模擬圖及 JSON／CSV／HTML。輸出仍一律標註 simulated，不能當成實機證據。
- 實機執行確認可完全在 Web 完成：Route、操作員在場與安全 profile 通過後，最後摘要會列出實際頻率／功率／頻寬；取消不送 RF，後端限制與 cleanup 不可繞過。
- Runs Table 支援全文搜尋、日期／來源／狀態篩選與時間／頻率／功率／點數／Worst EVM 排序；詳情在原列下方展開，輸出直接由瀏覽器開啟，刪除需 Run ID 二次確認並移至可復原 Trash。
- 實機量測頁改為單點／頻率／功率三個直接操作分頁，不再顯示裝飾性積木或量測模式下拉選單；Run 仍走完整安全確認，掃描 Pause 只在 RF Off 點位邊界生效，Stop 保留 cooperative cancellation 與 emergency cleanup。
- 掃描設定永久展開；頻率 Start／Stop／Step／Center 欄位各自提供 MHz／GHz 等值切換。實機頻率掃描預設為已核准的 5925→6125 MHz／320 MHz 區段；頻率／功率掃描會使用畫面上的同一份自訂計畫，不再落回固定 6085／6105／6125 MHz profile。若計畫尚未被 RF workflow 接受，Web 會顯示拒絕原因且不送 RF。執行期間顯示逐點進度、最新 EVM 與即時趨勢圖，資料只取自已完成的 RF-Off 點位。
- GPRF 功率掃描新增 PA 參考面計算欄位：可輸入 input/output cable loss、external gain、external attenuator 與 SA safe limit，artifact 會保存 `pin_dbm`、`pout_dbm`、`gain_db` 與 P1dB 分析摘要。若掃描尚未觀察到 1 dB 壓縮，P1dB 會標示 `not_found`，並列出最大已觀察 compression、最大 Pin 與最大 Pout；此變更目前只經 Mock／離線單元測試驗證，尚未做新的 PA 實機 RF 量測。
- Limit 判定明確採用 EVM dB 越負越好的規則：量測 EVM 必須小於或等於 `maximum_evm_db` 才能通過；沒有正式 limit profile 的實機結果只顯示 `MEASURED`，不宣稱 PASS。Power Reference Plane 尚未套用正式 +5 dB compensation；metadata 會記錄 `calibration_applied=false`。
- 多 Run 分析提供 Trace 名稱、顏色鎖、線型、點型、Hide／Solo／移除、拖曳排序、相容性警告與 SVG／PNG／比較 CSV 匯出。EVM 不使用一般升降箭頭，INVALID 點不連線。
- Mock Sweep 使用非同步 Job API，支援逐點進度、取消、partial artifacts 與單一 active-job 鎖。
- Web 核准 profile 已納入 11 個完成 HIL 的 WLAN band／bandwidth 區段；後端只在 RF OFF／measurement idle 時依 20／40／80／160／320 MHz 自動選取匹配 waveform，並做絕對路徑 readback。仍只允許 RF1.1 → RF1.5 loopback 與 -55～-30 dBm，不授權非 WLAN 空隙。
- GitHub Actions 執行 Windows／Python 3.11 unit、Mock 與設定驗證；不執行實機 RF。
- 離線圖表同時支援 dependency-free SVG 與 Pandas／Matplotlib `Agg` PNG；query-only 連線診斷具 0–5 次 bounded transient retry，每次重試前關閉 session，且不會自動重送 RF／SCPI write。
- 新 Web Run 會從保存後的 CSV 自動產生 `plots-matplotlib/*.png`，並在「結果與圖表」以選單切換單張 Matplotlib PNG 預覽與原圖連結；互動圖的 X／Y 軸標題、工程單位與完整刻度已分離排版，並支援滑鼠拖曳水平平移。
- 實機 SingleShot 可直接在 CMP180 400–8000 MHz envelope 內送出單點：已核准 WLAN section 標示 `APPROVED`，區段外則沿用已驗證的 EHT/B6GHz measurement template 並標示 `HIL_PENDING`。兩者都保留 RF1.1 → RF1.5、-55～-30 dBm、readback 與 cleanup 限制；掃描仍只允許 approved section。CMsquares 只保留探索／除錯用途。

### 功能狀態

| 模組 | 狀態 | 說明 |
|---|---|---|
| Mock／Demo | 可用 | 不連接 CMP180、不送 RF，適合介面與流程訓練 |
| 實機 SingleShot | 400–8000 MHz 軟體執行路徑完成；區段外待 HIL | 已核准 section 顯示 `APPROVED`；其他中心頻率顯示 `HIL_PENDING`，仍限 RF1.1 → RF1.5 與 -55～-30 dBm |
| 頻率／頻寬矩陣 | HIL 已通過並納入 Web 核准 | 11 個合法 band／bandwidth 區段、176/176 點；執行時自動匹配 waveform |
| 固定功率掃描 | 歷史 HIL 已通過；目前 Profile 待重驗 | 已驗證四點掃描與取消／cleanup；最新 waveform 仍需排除 `INV` |
| 自訂量測規劃 | 型錄範圍可輸入；實機執行依 RF workflow | 規劃介面支援 400 MHz–8 GHz 與 WLAN 20／40／80／160／320 MHz；Web 不再把自訂輸入改跑固定 profile，未通過 workflow 的計畫會顯示拒絕原因且不送 RF |
| Path Loss 校正 | Draft workflow | 可建立、載入與審查 Profile；正式外部校正儀器 adapter 尚待 HIL |
| 歷史分析 | 可用、唯讀 | 單一 Run 圖表、2–8 Run 比較、Hover、Zoom、Pan、A/B 游標與匯出 |
| 多圖同步 | 規劃中 | 下一階段同步 EVM、Power 與 Frequency Error 的 X 軸及游標 |

Mock、dry-run、CMsquares 手動量測或單獨 stored `FETCh` 不得描述成新的完整 Python 實機量測。

### 快速開始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,hardware]"
python -m pytest -m "not hardware"
python -m cmp180_evm validate-config configs\instrument.example.yaml
python -m cmp180_evm validate-config configs\wlan_baseline.example.yaml
python -m cmp180_evm validate-calibration configs\calibration.example.yaml
python -m cmp180_evm validate-limits configs\limits.example.yaml
python -m cmp180_evm validate-pa-sweep configs\pa_sweep.example.yaml
python scripts\build_v1_acceptance.py --evidence output\<real-run-folder>
```

```powershell
# 本機受保護實機控制；啟動服務本身不會送 RF
python -m cmp180_evm.web --host 127.0.0.1 --port 8765

# 純示範／訓練模式；不連接 CMP180、不送 RF
python -m cmp180_evm.web --host 127.0.0.1 --port 8765 --demo-only
```

實機前必須閱讀 [硬體 SOP](docs/hardware-test-sop.md)，並確認操作員在場、routing、頻率、頻寬、功率與線路損耗。

PA／P1dB GPRF profile 已可固定化：`configs\pa_sweep.example.yaml` 保存 start/stop/step、
預期 DUT gain、RF1.5 safe limit 與核准資訊。換 DUT 時不需重填掃描參數，只需確認
profile、接線與人在場，然後執行；若現場沒有衰減器，程式會自動把 stop power 夾到
RF1.5 安全範圍內，不會要求一定接 30 dB：

Web 實機頁可切到 `RF 功率讀值（GPRF）` 後直接按「載入 approved PA profile」；
此按鈕預設載入無衰減器的安全裁切範圍 `-55 → -25 dBm`。若現場有受控 DUT／實體
output attenuator，再把 `Output attenuator` 改成實際值並重新檢查計畫即可。

```powershell
python scripts\cmp180_pa_sweep_validate.py `
  --dut-id DUT-001 `
  --confirm-direct-cable `
  --confirm-operator-present
```

現場若有外部衰減器，可加 `--output-attenuator-db 30` 讓 profile 掃到更高 stop power。
此入口使用 GPRF scalar power，不是 WLAN EVM；任一點出現 SCPI error、reliability 非 0
或 SA safe limit 會在 RF Off 邊界停止並保存 partial artifact。

### 文件導覽

| 文件 | 用途 |
|---|---|
| [使用者指南](docs/user-guide.md) | 安裝、CLI、GUI、Mock 與實機操作 |
| [硬體 SOP](docs/hardware-test-sop.md) | 接線、安全與執行順序 |
| [ADL5611 PA／P1dB SOP](docs/adl5611-pa-p1db-sop.md) | ADL5611 現場 PA Gain／P1dB 量測前檢查與判讀 |
| [Web GUI](docs/web-gui-guide.md) | 啟動、硬體鎖定與 artifacts |
| [CMsquares Workspace 借鑑](docs/cmsquares-workspace-lessons.md) | 安全 Pause、狀態回饋與 `RDY,ADJ,INV` 診斷；不複製其積木排版 |
| [Google Apps Script 分享版](docs/google-apps-script-deployment.md) | 固定網址部署、更新與去識別化歷史分析 |
| [Web V2 設計（封存參考）](docs/web-v2-design.md) | 未採用版型與可回用互動的設計紀錄 |
| [RF 工作站 UX 規格](docs/rf-workstation-ux-plan.md) | Runs Table、多 Run 比較、Trace、主題與 RF 安全設計 |
| [UI/UX roadmap](docs/ui-ux-roadmap.md) | 公司內部控制台資訊架構與改版階段 |
| [量測欄位](docs/measurement-example-and-fields.md) | 正確輸出與 EVM／Power／Frequency Error |
| [SCPI matrix](docs/scpi-command-matrix.md) | 指令來源、驗證與 schema |
| [硬體探索](docs/hardware-discovery.md) | 已驗證事實與量測證據 |
| [SingleShot 狀態機](docs/single-measurement-state-machine.md) | RF workflow 與 cleanup |
| [架構圖](docs/diagrams/README.md) | 互動式系統架構圖與 SingleShot 生命週期圖 |
| [安全短掃描](docs/sweep-safety.md) | 頻率／功率 sweep 限制與 HIL gate |
| [Limit Profile](docs/limit-profiles.md) | Draft／Approved 判定、margin 與追溯規則 |
| [Calibration Profile](docs/calibration-profiles.md) | 線損資料、內插、有效期限與核准閘門 |
| [Calibration Adapters](docs/calibration-adapters.md) | 外部儀器介面、安全限制與 HIL 閘門 |
| [Custom Hardware Sweep](docs/custom-hardware-sweep.md) | 自訂掃描安全包絡、雙重啟動閘門與 HIL SOP |
| [下一次 HIL 驗收批次](docs/next-hil-campaign.md) | 90 分鐘能力快照、邊界點、短掃描與擴大 Web Profile 的驗收方式 |
| [視覺化規格](docs/result-visualization-spec.md) | artifacts 與圖表要求 |
| [開發流程](docs/development-workflow.md) | 測試與文件規則 |
| [專案開發日誌與 Week 9–12 計畫](docs/project-development-log.md) | 簡報差距、問題／解法、逐日進度與收尾計畫 |
| [交接](HANDOFF.md) | 最新狀態與下一步 |

完整分類與權威文件說明請見 [文件中心](docs/README.md)。

### 專案結構

```text
configs/   可提交的 YAML／CSV 範例與 SCPI command map
deploy/    Google Apps Script 唯讀分享版
docs/      中英雙語 SOP、規格、驗證紀錄與開發文件
scripts/   操作員與 HIL 驗證入口；不放核心商業邏輯
src/       Python package、workflow、Web API 與正式 static 前端
tests/     unit／mock／安全與 artifact 測試
presentation/ open-slide 期末專案簡報原始碼與匯出檔
output/    本機量測成果與測試暫存，不納入 Git
```

權威需求文件是 `SPEC.MD`；`CMP180_DEVELOPMENT_SPEC_AND_PLAN.md` 是早期詳細計畫，`DEVELOPMENT_SPEC_AND_PLAN.md` 是已封存的 SMW200A／FSW85 歷史資料。正式 Web 前端位於 `src/cmp180_evm/web/static/`；`static_v2/` 僅保留為封存設計參考。

### 安全原則

不自動 Reset；SCPI 集中管理；RF On 前完成安全驗證；所有 RF workflow 在成功、錯誤、逾時與取消時 STOP／ABORT 並 RF Off；invalid token 不轉成 0；沒有正式 limit 時不得宣稱 RF compliance PASS；不提交 output、憑證、license／activation data、測試 cache 或私人裝置 dump。

交付給夥伴與擴大儀器能力的方式，請參閱[交付方式與 CMP180 能力擴充](docs/deployment-and-capability-expansion.md)。

## English Version

The Web UI now includes a dedicated Loopback Validation page. It runs independent WLAN SingleShot repeats, shows live post-cleanup EVM/Power/Frequency Error trends, flags INVALID and IQR outlier values, and reports separate Validity, Stability, Reasonableness, and Overall states. The 2026-09-03 live HIL at 6105 MHz/320 MHz/−40 dBm completed 10/10 valid repeats with Stability PASS, Reasonableness DRAFT_PASS, and final RF OFF; that exact condition is now a source-linked approved loopback profile, and a second Repeat=10 regression under the approved profile produced `LOOPBACK_READY`. Other inputs remain draft and cannot claim `LOOPBACK_READY`.

Run All executes representative points for all 11 approved WLAN sections sequentially, with Repeat=10 at each point for 110 independent SingleShots. The 2026-09-03 live batch completed 110/110 valid measurements; every profile passed Stability and Reasonableness, and every artifact ended with RF `OFF`, measurement `RDY`, and no cleanup errors. All 11 representative points now have separately source-linked approved loopback profiles. Frequencies, powers, routes, and UD Box paths outside this matrix remain draft or blocked.

The same 11 representative points were then rerun after promotion with Repeat=10 each. All 110 measurements were valid, and all 11 profiles recorded the `approved` lifecycle, Stability PASS, Reasonableness PASS, and formal `LOOPBACK_READY`. SingleShot, WLAN Sweep, GPRF, Loopback, HIL Campaign, and Calibration plan checks, previews, safety guidance, and final confirmations now update immediately with the Chinese/English selector. Switching language does not call a preview or RF endpoint again.

This Python 3.11+ system automates Rohde & Schwarz CMP180 WLAN TX EVM measurements with reproducible, auditable workflows. The long-term product is a bilingual responsive intranet Web tool.

### CMP180 Blender exterior model

The editable CMP180 Blender exterior model, GLB, and validation render are available in [`assets/cmp180_3d/`](assets/cmp180_3d/README.md). This is a visual model derived from official information and reference photographs, not mechanical CAD, and it neither connects to nor controls the instrument.

### Current capabilities

- The Web UI includes a resumable `HIL Campaign Runner`. Prepare classifies band/bandwidth, representative power, alternate RF routes, 500 MHz, dual VSA/VSG, and long-waveform cases as READY or BLOCKED. READY cases can run by row or through Run Next, while progress persists in `output/hil-campaign/state.json`. BLOCKED cases are never substituted with an existing profile.

- YAML validation, mock/real connection, hardware-verified setters, measurement lifecycle, and RF On/Off.
- Complete Python hardware SingleShot at RF1.1 to RF1.5, 6105 MHz, 320 MHz, and -40 dBm.
- One Python tool completed 11 legal WLAN band/bandwidth sections across 2.4, 5, and 6 GHz, with 176/176 valid channel centers for 20/40/80/160/320 MHz. The non-WLAN gaps in the 400 MHz–8 GHz tuning range remain out of scope.
- 28-field OFDM SISO parsing with CSV, JSON, metadata, raw-response, and HTML artifacts.
- Bilingual responsive horizontal workspace with working Dark/Light themes, contextual workspace headings, integrated demo/guarded-hardware measurement, eagerly loaded run history, multi-run overlays, editable trace names/colours/visibility, a Draft calibration SOP, artifacts, and recoverable run management.
- The home page provides an opt-in CMP180 360° viewer with mouse/touch orbit, zoom, front/rear/side presets, reset, optional auto-rotation, and fullscreen. A failed load preserves the still image and offers retry. The model and pinned viewer are local assets; home interactions call no measurement or RF API. See the [3D viewer guide](docs/cmp180-3d-viewer.md) and [website review and improvement plan](docs/web-audit-2026-09-10.md).
- The home page embeds the interactive system-architecture and SingleShot-lifecycle diagrams from `docs/diagrams/` in `present=1` interaction/presentation mode. Users can switch, reload, or open them full-page; diagram actions call no measurement API.
- Dependency-free offline `results.csv` to SVG charts and a self-contained bilingual HTML report; Web comparisons support drag-to-reorder, rename/style controls, and SVG/PNG/CSV export.
- The operator-approved horizontal workspace in `static/` is the served frontend. It supports read-only comparison of 2–8 saved runs with editable trace names, colours, visibility, and discontinuities at invalid points; this analysis never transmits RF.
- Navigation clearly separates demo and hardware measurements. Normal local startup exposes guarded hardware control; `--demo-only` disables instrument access. Results show a safe relative output location.
- Hardware and Demo share Single/Frequency Sweep/Power Sweep tabs. Result charts provide fixed coordinates, bounded horizontal zoom/pan, crosshairs, and complete point values. Help covers GitHub clone, installation, CLI, Web, and offline-report workflows.
- Hardware execution confirmation is fully in-Web: after route, operator-presence, and safe-profile checks, a final summary lists the actual frequency, power, and bandwidth. Cancellation transmits no RF, while backend limits and cleanup remain non-bypassable.
- The Runs Table supports full-text search, date/source/status filters, and time/frequency/power/point-count/worst-EVM sorting. Details expand below their source row, outputs open in the browser, and deletion requires exact Run-ID confirmation before moving to recoverable Trash.
- The hardware page uses direct Single/Frequency/Power tabs with no decorative blocks or measurement-mode dropdown. Run retains complete safety confirmation, sweep Pause takes effect only at an RF-Off point boundary, and Stop preserves cooperative cancellation plus emergency cleanup.
- Sweep settings stay expanded. Frequency Start/Stop/Step/Center fields each provide an adjacent MHz/GHz selector with value-preserving conversion. Hardware frequency sweep defaults to the approved 5925→6125 MHz / 320 MHz section; frequency/power sweeps use the exact custom plan shown on screen instead of falling back to the fixed 6085/6105/6125 MHz profile. If the current RF workflow rejects the plan, the UI shows the reason and transmits no RF. During execution, the page shows point progress, latest EVM, and a live trend built only from completed RF-Off points.
- Limit evaluation explicitly treats more-negative EVM dB as better: measured EVM must be less than or equal to `maximum_evm_db`. Hardware results without an approved limit profile are shown as `MEASURED`, not PASS. Power Reference Plane compensation is not yet applied; metadata records `calibration_applied=false`.
- Multi-run analysis provides trace naming, colour lock, line/point styles, Hide/Solo/remove, drag ordering, compatibility warnings, and SVG/PNG/comparison-CSV export. EVM avoids generic up/down arrows, and INVALID points never connect to valid data.
- Mock Sweep uses an asynchronous Job API with per-point progress, cancellation, partial artifacts, and a single-active-job lock.
- The Web approved profile now includes all 11 HIL-complete WLAN band/bandwidth sections. While RF is OFF and measurement is idle, the backend automatically selects the matching 20/40/80/160/320 MHz waveform and verifies its absolute-path readback. Execution remains limited to the RF1.1-to-RF1.5 loopback and -55 to -30 dBm; non-WLAN gaps are never authorized.
- Windows/Python 3.11 GitHub Actions for unit, mock, and configuration checks; CI never runs live RF.
- Offline plotting supports dependency-free SVG and Pandas/Matplotlib `Agg` PNG output. Query-only connection diagnostics use a 0–5 bounded transient retry that closes the session before retrying and never automatically repeats RF or SCPI writes.
- New Web runs generate `plots-matplotlib/*.png` from saved CSV and show a selector-driven single Matplotlib PNG preview plus original-image links on Results. The interactive chart separates X/Y titles, engineering units, and full tick labels, and supports horizontal mouse-drag panning.
- Hardware SingleShot can transmit one point across the CMP180 400-8000 MHz envelope. Approved WLAN sections are labelled `APPROVED`; points outside those sections use the verified EHT/B6GHz measurement template and are labelled `HIL_PENDING`. Both retain the RF1.1-to-RF1.5, -55 to -30 dBm, readback, and cleanup limits; sweeps remain restricted to approved sections. CMsquares remains a discovery/debug reference.

### Capability status

| Module | Status | Notes |
|---|---|---|
| Mock/Demo | Available | Does not connect to CMP180 or transmit RF |
| Hardware SingleShot | 400-8000 MHz software execution path complete; out-of-section HIL pending | Approved sections show `APPROVED`; other center frequencies show `HIL_PENDING` and remain limited to RF1.1-to-RF1.5 and -55 to -30 dBm |
| Frequency/bandwidth matrix | HIL passed and Web-approved | 11 legal band/bandwidth sections and 176/176 points; execution auto-selects the matching waveform |
| Fixed power sweep | Historical HIL passed; current profile needs revalidation | Four-point execution/cancellation passed historically; the latest waveform still produces `INV` |
| Custom measurement planning | Catalog range available; RF execution is profile-gated | Planning accepts 400 MHz–8 GHz and WLAN 20/40/80/160/320 MHz; only approved HIL combinations may transmit RF |
| Path-loss calibration | Draft workflow | Profile generation/review exists; external-instrument adapter still needs HIL |
| Historical analysis | Available, read-only | Single-run plots, 2–8 run comparison, hover, zoom, pan, A/B cursors, and exports |
| Synchronized multi-chart view | Planned | Next stage synchronizes EVM, Power, and Frequency Error X axes and cursors |

Do not describe mock, dry-run, manual CMsquares operation, or a standalone stored `FETCh` as a new complete Python hardware measurement.

### Quick start

Use the commands in the Chinese section above. Normal local startup enables guarded hardware control; add `--demo-only` for training without instrument access. Starting the server never transmits RF. Hardware execution still requires the route, operator-presence, approved-profile, and final-summary confirmations in the Web UI.

### Documentation

The documentation table above is authoritative for operator, SCPI, state-machine, sweep,
GUI, visualization, and handoff material. The [UI/UX roadmap](docs/ui-ux-roadmap.md)
defines the internal-console information architecture, design principles, delivery phases,
and responsive acceptance criteria. Read the [hardware SOP](docs/hardware-test-sop.md)
before any live operation.

The [architecture diagrams](docs/diagrams/README.md) are self-contained interactive HTML: a layered system map whose nodes cite real files and line numbers, and the SingleShot measurement lifecycle.
See the [documentation centre](docs/README.md) for categorized authoritative, supporting, and archived references.
See the [project development log and Week 9–12 plan](docs/project-development-log.md) for the deck gap review, reconstructed problem/solution history, and daily closeout plan.
See [Delivery and CMP180 capability expansion](docs/deployment-and-capability-expansion.md) for partner handoff and the layered capability model.
Use the [next HIL campaign](docs/next-hil-campaign.md) to expand the approved Web range during the next instrument session.

### Repository structure

`configs/` contains shareable examples and the command map; `deploy/` contains the read-only Google Apps Script viewer; `docs/` contains bilingual specifications and SOPs; `scripts/` contains operator and HIL entry points; `src/` contains the package, workflows, API, and served frontend; `tests/` contains automated checks; `presentation/` contains the open-slide final-project deck and its exports; and ignored `output/` contains local artifacts.

`SPEC.MD` is the authoritative requirement specification. `CMP180_DEVELOPMENT_SPEC_AND_PLAN.md` is an early detailed plan, while `DEVELOPMENT_SPEC_AND_PLAN.md` is archived SMW200A/FSW85 history. The served frontend is `src/cmp180_evm/web/static/`; `static_v2/` is an archived design reference.

### Safety principles

Never reset automatically; centralize SCPI; validate every RF input before RF On; STOP/ABORT and RF Off on every exit path; preserve invalid values; separate workflow success from compliance; never commit outputs, credentials, license/activation data, caches, or private device dumps.


### PA 掃描摘要與有效性（2026-09-09）

在結果頁開啟含 PA 欄位的 GPRF 紀錄：功率掃描摘要顯示 Small-signal Gain、Max Pout、Max Compression、IP1dB、OP1dB 與 Valid Points；頻率掃描顯示 Mean Gain、Gain Peak-to-Peak Ripple 與 Gain Std Dev（母體標準差）。PA 統計只納入有效且 Pin／Pout／Gain 齊全的點。`not_found` 表示有效掃描範圍內未觀察到 1 dB 壓縮，`insufficient_points` 表示資料不足；缺值不補零。

Analyzer measured／expected power 的誤差與 PA Gain 是不同物理量；不得把 Analyzer error ripple 當成 Gain flatness。無 PA 欄位的舊 GPRF 結果保留明確標示 Analyzer 參考面的摘要，dBm 平均為算術平均。重新產生的 SVG／Matplotlib 圖會排除 INVALID 並切斷曲線；既有 PNG 不會自動更新，須由原 CSV 重新產圖。原始 CSV／JSON 保留診斷數值。

本次驗證為合成資料／Mock 回歸及既有 stored artifact 查閱，未執行新的實機 RF 量測。


### 圖表縮放與拖曳（2026-09-09）

游標放在繪圖區內，滾輪前滾放大、後滾縮小；X 軸以游標位置縮放，Y 軸依可見有效測點自動調整。按住滑鼠左鍵可左右拖曳，放開即停止；拖曳範圍受資料邊界限制，縮小最多回到全圖。Reset 或雙擊恢復完整範圍。A/B 模式下左鍵改為選點；縮放／拖曳會清除舊游標，避免位置誤讀。座標軸與文字固定在圖框內，資料超出範圍時只裁切資料層。以上操作只讀取既有結果，不送 SCPI 或 RF。
