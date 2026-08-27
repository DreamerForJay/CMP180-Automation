# CMP180 文件中心

[繁體中文](#繁體中文) · [English](#english)

## 繁體中文

本頁用來區分權威規格、操作文件、驗證證據、設計規劃與封存參考。功能修改時請依 `development-workflow.md` 同步程式、測試與相關文件。

### 操作員必讀

| 文件 | 用途 |
|---|---|
| [使用者指南](user-guide.md) | 安裝、CLI、Web、Mock 與實機操作 |
| [硬體量測 SOP](hardware-test-sop.md) | 接線、RF 安全、執行順序與異常處理 |
| [Web GUI 指南](web-gui-guide.md) | 模式、確認流程、結果與 artifacts |
| [CMsquares Workspace 借鑑](cmsquares-workspace-lessons.md) | 積木控制、安全 Pause 與 `RDY,ADJ,INV` 診斷 |
| [量測範例與欄位](measurement-example-and-fields.md) | EVM、Power、Frequency Error 與正確輸出解讀 |

### 安全、校正與實機驗證

| 文件 | 用途 |
|---|---|
| [安全掃描](sweep-safety.md) | 頻率／功率掃描包絡與 HIL gate |
| [自訂實機掃描](custom-hardware-sweep.md) | 自訂計畫、雙重啟動旗標與驗收 SOP |
| [Limit Profiles](limit-profiles.md) | PASS／FAIL／INVALID 與核准規則 |
| [Calibration Profiles](calibration-profiles.md) | Path Loss、內插、期限與追溯 |
| [Calibration Adapters](calibration-adapters.md) | 外部校正儀器 adapter 邊界 |
| [硬體探索](hardware-discovery.md) | 已驗證 CMP180 事實與結果證據 |
| [唯讀硬體驗證](hardware-readonly-validation.md) | Query-only 探索紀錄 |

### 工程與架構

| 文件 | 用途 |
|---|---|
| [SCPI Command Matrix](scpi-command-matrix.md) | 命令來源、狀態、副作用與 schema |
| [SingleShot 狀態機](single-measurement-state-machine.md) | 狀態轉換與 cleanup |
| [結果視覺化規格](result-visualization-spec.md) | CSV／JSON／HTML 與圖表要求 |
| [RF 工作站 UX](rf-workstation-ux-plan.md) | Runs、Trace、圖表與操作安全 UX |
| [UI/UX Roadmap](ui-ux-roadmap.md) | 介面階段與響應式驗收標準 |
| [開發流程](development-workflow.md) | Definition of Done、測試與文件同步 |
| [Google Apps Script 部署](google-apps-script-deployment.md) | 唯讀分享版部署與去識別化 |

### 文件權威順序與封存資料

1. 根目錄 `SPEC.MD` 是目前需求與安全邊界的權威規格。
2. `AGENTS.md` 定義程式註解、文件語言、實機安全與開發規則。
3. `README.md` 與本文件提供目前能力及導覽，不取代詳細 SOP。
4. `CMP180_DEVELOPMENT_SPEC_AND_PLAN.md` 是早期 CMP180 詳細計畫，若與 `SPEC.MD` 衝突，以 `SPEC.MD` 為準。
5. `DEVELOPMENT_SPEC_AND_PLAN.md` 是 SMW200A／FSW85 歷史資料，不作為目前驗收依據。
6. `web-v2-design.md` 與 `src/cmp180_evm/web/static_v2/` 是封存版型參考；正式前端是 `src/cmp180_evm/web/static/`。

能力範圍與交付方式另見[交付方式與 CMP180 能力擴充](deployment-and-capability-expansion.md)。

## English

This page distinguishes authoritative specifications, operator documents, validation evidence, design plans, and archived references. Follow `development-workflow.md` so implementation, tests, and affected documentation change together.

### Required operator reading

| Document | Purpose |
|---|---|
| [User guide](user-guide.md) | Installation, CLI, Web, mock, and hardware operation |
| [Hardware measurement SOP](hardware-test-sop.md) | Cabling, RF safety, execution order, and exception handling |
| [Web GUI guide](web-gui-guide.md) | Modes, confirmations, results, and artifacts |
| [CMsquares workspace lessons](cmsquares-workspace-lessons.md) | Block controls, safe Pause, and `RDY,ADJ,INV` diagnosis |
| [Measurement examples and fields](measurement-example-and-fields.md) | EVM, power, frequency error, and correct output interpretation |

### Safety, calibration, and hardware evidence

| Document | Purpose |
|---|---|
| [Sweep safety](sweep-safety.md) | Frequency/power safety envelope and HIL gate |
| [Custom hardware sweep](custom-hardware-sweep.md) | Custom plans, dual startup flags, and acceptance SOP |
| [Next HIL campaign](next-hil-campaign.md) | Time-boxed capability snapshot, boundary cases, short sweeps, and profile expansion |
| [Limit profiles](limit-profiles.md) | PASS/FAIL/INVALID and approval rules |
| [Calibration profiles](calibration-profiles.md) | Path loss, interpolation, expiry, and traceability |
| [Calibration adapters](calibration-adapters.md) | External calibration-instrument adapter boundary |
| [Hardware discovery](hardware-discovery.md) | Verified CMP180 facts and result evidence |
| [Read-only hardware validation](hardware-readonly-validation.md) | Query-only discovery records |

### Engineering and architecture

| Document | Purpose |
|---|---|
| [SCPI command matrix](scpi-command-matrix.md) | Command sources, status, side effects, and schema |
| [SingleShot state machine](single-measurement-state-machine.md) | State transitions and cleanup |
| [Result visualization specification](result-visualization-spec.md) | CSV/JSON/HTML and chart requirements |
| [RF workstation UX](rf-workstation-ux-plan.md) | Runs, traces, charts, and safe-operation UX |
| [UI/UX roadmap](ui-ux-roadmap.md) | UI phases and responsive acceptance criteria |
| [Development workflow](development-workflow.md) | Definition of Done, testing, and documentation synchronization |
| [Google Apps Script deployment](google-apps-script-deployment.md) | Read-only viewer deployment and de-identification |
| [Delivery and capability expansion](deployment-and-capability-expansion.md) | Partner handoff and layered CMP180 execution envelopes |

### Authority order and archived material

1. Root `SPEC.MD` is the authoritative requirements and safety-boundary specification.
2. `AGENTS.md` defines code comments, documentation language, hardware safety, and development rules.
3. `README.md` and this page provide status and navigation but do not replace detailed SOPs.
4. `CMP180_DEVELOPMENT_SPEC_AND_PLAN.md` is an early detailed CMP180 plan; `SPEC.MD` wins if they conflict.
5. `DEVELOPMENT_SPEC_AND_PLAN.md` is archived SMW200A/FSW85 history and is not an acceptance source.
6. `web-v2-design.md` and `src/cmp180_evm/web/static_v2/` are archived layout references; the served frontend is `src/cmp180_evm/web/static/`.
