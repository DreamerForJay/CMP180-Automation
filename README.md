# CMP180 WLAN TX EVM Automation

### Language / 語言

[繁體中文](#中文版本) · [English](#english-version)

> GitHub 使用者可透過上方語言選單跳轉；專案文件一律先繁體中文、再英文。
>
> GitHub users can use the language menu above. Project documents always present complete Traditional Chinese content before English.

## 中文版本

Python 3.11+ 的 Rohde & Schwarz CMP180 WLAN TX EVM 自動化系統，用可重現、可稽核的流程取代重複的 CMsquares 手動操作，長期產品為中英雙語、響應式公司內網 Web 工具。

### 目前能力

- Web 新增可恢復的 `HIL Campaign Runner`：按「準備」可把頻段／頻寬、代表功率、其他 RF route、500 MHz、雙 VSA／VSG 與長 waveform 分類成 READY／BLOCKED；READY 可逐列或按「執行下一個」啟動，進度保存於 `output/hil-campaign/state.json`。BLOCKED 案例不會偷換成既有 profile 執行。

- YAML 驗證、Mock／實機連線、Generator／Analyzer setter、measurement lifecycle 與 RF On／Off。
- 已完成 RF1.1 → RF1.5、6105 MHz、320 MHz、-40 dBm 的 Python 實機 SingleShot。
- 解析 28 欄 OFDM SISO，輸出 CSV、JSON、metadata、raw response 與 HTML report。
- 雙語響應式橫向量測工作區：Dark／Light、依分頁切換的專業工作區標題、整合式 Demo／實機量測、量測紀錄、多 Run 疊圖比較、可自訂 Trace 名稱／顏色／顯示、Draft 校正 SOP，以及完整 artifacts 與可復原紀錄管理。歷史分析會預先讀取既有 CSV／JSON，不會送出 RF。
- 首頁提供產品定位、功能介紹、量測能力、安全邊界、五步標準流程與操作手冊入口；首頁 CTA 只切換工作區，不呼叫任何量測或 RF API。動畫使用本機 CSS，無外部影音依賴。
- 導覽明確區分示範與實機量測；一般本機啟動直接提供受保護的實機控制，`--demo-only` 才會停用儀器連線。結果頁顯示安全的相對輸出位置。
- 實機與示範量測共用單點／頻率掃描／功率掃描分頁；結果圖表提供固定座標、受限水平 Zoom／Pan、十字游標與完整點位標值。說明頁涵蓋 GitHub clone、安裝、CLI、Web 與離線報告流程。
- 實機執行確認可完全在 Web 完成：Route、操作員在場與安全 profile 通過後，最後摘要會列出實際頻率／功率／頻寬；取消不送 RF，後端限制與 cleanup 不可繞過。
- Runs Table 支援全文搜尋、日期／來源／狀態篩選與時間／頻率／功率／點數／Worst EVM 排序；詳情在原列下方展開，輸出直接由瀏覽器開啟，刪除需 Run ID 二次確認並移至可復原 Trash。
- 實機量測頁改為單點／頻率／功率三個直接操作分頁，不再顯示裝飾性積木或量測模式下拉選單；Run 仍走完整安全確認，掃描 Pause 只在 RF Off 點位邊界生效，Stop 保留 cooperative cancellation 與 emergency cleanup。
- 掃描設定永久展開；頻率 Start／Stop／Step／Center 欄位各自提供 MHz／GHz 等值切換。實機頻率／功率掃描會使用畫面上的同一份自訂計畫，不再落回固定 6085／6105／6125 MHz profile；若計畫尚未被 RF workflow 接受，Web 會顯示拒絕原因且不送 RF。執行期間顯示逐點進度、最新 EVM 與即時趨勢圖，資料只取自已完成的 RF-Off 點位。
- Limit 判定明確採用 EVM dB 越負越好的規則：量測 EVM 必須小於或等於 `maximum_evm_db` 才能通過；沒有正式 limit profile 的實機結果只顯示 `MEASURED`，不宣稱 PASS。Power Reference Plane 尚未套用正式 +5 dB compensation；metadata 會記錄 `calibration_applied=false`。
- 多 Run 分析提供 Trace 名稱、顏色鎖、線型、點型、Hide／Solo／移除、拖曳排序、相容性警告與 SVG／PNG／比較 CSV 匯出。EVM 不使用一般升降箭頭，INVALID 點不連線。
- Mock Sweep 使用非同步 Job API，支援逐點進度、取消、partial artifacts 與單一 active-job 鎖。
- 安全短掃描核心（頻率與功率）：最大 11 點、-40 dBm 上限與逐點 cleanup；CLI HIL 與 Web 實機三點頻率／功率取消驗收均已通過。Web 實機模式仍只允許 loopback 本機啟用與固定安全 profile。
- GitHub Actions 執行 Windows／Python 3.11 unit、Mock 與設定驗證；不執行實機 RF。

### 功能狀態

| 模組 | 狀態 | 說明 |
|---|---|---|
| Mock／Demo | 可用 | 不連接 CMP180、不送 RF，適合介面與流程訓練 |
| 實機 SingleShot | HIL 已通過 | RF1.1 → RF1.5、6105 MHz、320 MHz、-40 dBm |
| 固定頻率掃描 | 歷史 HIL 已通過；目前 Profile 待重驗 | 受固定安全 Profile 與 Web 最終確認保護 |
| 固定功率掃描 | 歷史 HIL 已通過；目前 Profile 待重驗 | 已驗證四點掃描與取消／cleanup；最新 waveform 仍需排除 `INV` |
| 自訂量測規劃 | 型錄範圍可輸入；實機執行依 RF workflow | 規劃介面支援 400 MHz–8 GHz 與 WLAN 20／40／80／160／320 MHz；Web 不再把自訂輸入改跑固定 profile，未通過 workflow 的計畫會顯示拒絕原因且不送 RF |
| Path Loss 校正 | Draft workflow | 可建立、載入與審查 Profile；正式外部校正儀器 adapter 尚待 HIL |
| 歷史分析 | 可用、唯讀 | 搜尋／篩選 Runs、2–8 Run 比較、Hover、Zoom、Pan、A/B 游標與匯出 |
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
```

```powershell
# 本機受保護實機控制；啟動服務本身不會送 RF
python -m cmp180_evm.web --host 127.0.0.1 --port 8765

# 純示範／訓練模式；不連接 CMP180、不送 RF
python -m cmp180_evm.web --host 127.0.0.1 --port 8765 --demo-only
```

實機前必須閱讀 [硬體 SOP](docs/hardware-test-sop.md)，並確認操作員在場、routing、頻率、頻寬、功率與線路損耗。

### 文件導覽

| 文件 | 用途 |
|---|---|
| [使用者指南](docs/user-guide.md) | 安裝、CLI、GUI、Mock 與實機操作 |
| [硬體 SOP](docs/hardware-test-sop.md) | 接線、安全與執行順序 |
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
| [安全短掃描](docs/sweep-safety.md) | 頻率／功率 sweep 限制與 HIL gate |
| [Limit Profile](docs/limit-profiles.md) | Draft／Approved 判定、margin 與追溯規則 |
| [Calibration Profile](docs/calibration-profiles.md) | 線損資料、內插、有效期限與核准閘門 |
| [Calibration Adapters](docs/calibration-adapters.md) | 外部儀器介面、安全限制與 HIL 閘門 |
| [Custom Hardware Sweep](docs/custom-hardware-sweep.md) | 自訂掃描安全包絡、雙重啟動閘門與 HIL SOP |
| [下一次 HIL 驗收批次](docs/next-hil-campaign.md) | 90 分鐘能力快照、邊界點、短掃描與擴大 Web Profile 的驗收方式 |
| [視覺化規格](docs/result-visualization-spec.md) | artifacts 與圖表要求 |
| [開發流程](docs/development-workflow.md) | 測試與文件規則 |
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
output/    本機量測成果與測試暫存，不納入 Git
```

權威需求文件是 `SPEC.MD`；`CMP180_DEVELOPMENT_SPEC_AND_PLAN.md` 是早期詳細計畫，`DEVELOPMENT_SPEC_AND_PLAN.md` 是已封存的 SMW200A／FSW85 歷史資料。正式 Web 前端位於 `src/cmp180_evm/web/static/`；`static_v2/` 僅保留為封存設計參考。

### 安全原則

不自動 Reset；SCPI 集中管理；RF On 前完成安全驗證；所有 RF workflow 在成功、錯誤、逾時與取消時 STOP／ABORT 並 RF Off；invalid token 不轉成 0；沒有正式 limit 時不得宣稱 RF compliance PASS；不提交 output、憑證、license／activation data、測試 cache 或私人裝置 dump。

交付給夥伴與擴大儀器能力的方式，請參閱[交付方式與 CMP180 能力擴充](docs/deployment-and-capability-expansion.md)。

## English Version

This Python 3.11+ system automates Rohde & Schwarz CMP180 WLAN TX EVM measurements with reproducible, auditable workflows. The long-term product is a bilingual responsive intranet Web tool.

### Current capabilities

- The Web UI includes a resumable `HIL Campaign Runner`. Prepare classifies band/bandwidth, representative power, alternate RF routes, 500 MHz, dual VSA/VSG, and long-waveform cases as READY or BLOCKED. READY cases can run by row or through Run Next, while progress persists in `output/hil-campaign/state.json`. BLOCKED cases are never substituted with an existing profile.

- YAML validation, mock/real connection, hardware-verified setters, measurement lifecycle, and RF On/Off.
- Complete Python hardware SingleShot at RF1.1 to RF1.5, 6105 MHz, 320 MHz, and -40 dBm.
- 28-field OFDM SISO parsing with CSV, JSON, metadata, raw-response, and HTML artifacts.
- Bilingual responsive horizontal workspace with working Dark/Light themes, contextual workspace headings, integrated demo/guarded-hardware measurement, eagerly loaded run history, multi-run overlays, editable trace names/colours/visibility, a Draft calibration SOP, artifacts, and recoverable run management.
- The product home explains capabilities, safety boundaries, the five-step standard workflow, and operator-manual entry points. Home-page CTAs only navigate between workspaces and call no measurement or RF API. Motion uses local CSS with no external media dependency.
- Dependency-free offline `results.csv` to SVG charts and a self-contained bilingual HTML report; Web comparisons support drag-to-reorder, rename/style controls, and SVG/PNG/CSV export.
- The operator-approved horizontal workspace in `static/` is the served frontend. It supports read-only comparison of 2–8 saved runs with editable trace names, colours, visibility, and discontinuities at invalid points; this analysis never transmits RF.
- Navigation clearly separates demo and hardware measurements. Normal local startup exposes guarded hardware control; `--demo-only` disables instrument access. Results show a safe relative output location.
- Hardware and Demo share Single/Frequency Sweep/Power Sweep tabs. Result charts provide fixed coordinates, bounded horizontal zoom/pan, crosshairs, and complete point values. Help covers GitHub clone, installation, CLI, Web, and offline-report workflows.
- Hardware execution confirmation is fully in-Web: after route, operator-presence, and safe-profile checks, a final summary lists the actual frequency, power, and bandwidth. Cancellation transmits no RF, while backend limits and cleanup remain non-bypassable.
- The Runs Table supports full-text search, date/source/status filters, and time/frequency/power/point-count/worst-EVM sorting. Details expand below their source row, outputs open in the browser, and deletion requires exact Run-ID confirmation before moving to recoverable Trash.
- The hardware page uses direct Single/Frequency/Power tabs with no decorative blocks or measurement-mode dropdown. Run retains complete safety confirmation, sweep Pause takes effect only at an RF-Off point boundary, and Stop preserves cooperative cancellation plus emergency cleanup.
- Sweep settings stay expanded. Frequency Start/Stop/Step/Center fields each provide an adjacent MHz/GHz selector with value-preserving conversion. Hardware frequency/power sweeps now use the exact custom plan shown on screen instead of falling back to the fixed 6085/6105/6125 MHz profile. If the current RF workflow rejects the plan, the UI shows the reason and transmits no RF. During execution, the page shows point progress, latest EVM, and a live trend built only from completed RF-Off points.
- Limit evaluation explicitly treats more-negative EVM dB as better: measured EVM must be less than or equal to `maximum_evm_db`. Hardware results without an approved limit profile are shown as `MEASURED`, not PASS. Power Reference Plane compensation is not yet applied; metadata records `calibration_applied=false`.
- Multi-run analysis provides trace naming, colour lock, line/point styles, Hide/Solo/remove, drag ordering, compatibility warnings, and SVG/PNG/comparison-CSV export. EVM avoids generic up/down arrows, and INVALID points never connect to valid data.
- Mock Sweep uses an asynchronous Job API with per-point progress, cancellation, partial artifacts, and a single-active-job lock.
- Safety-bounded short-sweep cores (frequency and power) with 11-point and -40 dBm limits plus per-point cleanup. CLI HIL and Web hardware three-point frequency/cancellation acceptance have passed. Hardware Web mode remains loopback-only and limited to fixed safe profiles.
- Windows/Python 3.11 GitHub Actions for unit, mock, and configuration checks; CI never runs live RF.

### Capability status

| Module | Status | Notes |
|---|---|---|
| Mock/Demo | Available | Does not connect to CMP180 or transmit RF |
| Hardware SingleShot | HIL passed | RF1.1 to RF1.5, 6105 MHz, 320 MHz, -40 dBm |
| Fixed frequency sweep | Historical HIL passed; current profile needs revalidation | Protected by a fixed safe profile and final Web confirmation |
| Fixed power sweep | Historical HIL passed; current profile needs revalidation | Four-point execution/cancellation passed historically; the latest waveform still produces `INV` |
| Custom measurement planning | Catalog range available; RF execution is profile-gated | Planning accepts 400 MHz–8 GHz and WLAN 20/40/80/160/320 MHz; only approved HIL combinations may transmit RF |
| Path-loss calibration | Draft workflow | Profile generation/review exists; external-instrument adapter still needs HIL |
| Historical analysis | Available, read-only | Run filters, 2–8 run comparison, hover, zoom, pan, A/B cursors, and exports |
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

See the [documentation centre](docs/README.md) for categorized authoritative, supporting, and archived references.
See [Delivery and CMP180 capability expansion](docs/deployment-and-capability-expansion.md) for partner handoff and the layered capability model.
Use the [next HIL campaign](docs/next-hil-campaign.md) to expand the approved Web range during the next instrument session.

### Repository structure

`configs/` contains shareable examples and the command map; `deploy/` contains the read-only Google Apps Script viewer; `docs/` contains bilingual specifications and SOPs; `scripts/` contains operator and HIL entry points; `src/` contains the package, workflows, API, and served frontend; `tests/` contains automated checks; and ignored `output/` contains local artifacts.

`SPEC.MD` is the authoritative requirement specification. `CMP180_DEVELOPMENT_SPEC_AND_PLAN.md` is an early detailed plan, while `DEVELOPMENT_SPEC_AND_PLAN.md` is archived SMW200A/FSW85 history. The served frontend is `src/cmp180_evm/web/static/`; `static_v2/` is an archived design reference.

### Safety principles

Never reset automatically; centralize SCPI; validate every RF input before RF On; STOP/ABORT and RF Off on every exit path; preserve invalid values; separate workflow success from compliance; never commit outputs, credentials, license/activation data, caches, or private device dumps.
