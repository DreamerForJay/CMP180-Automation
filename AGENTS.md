# AGENTS.md

## 程式註解規則／Code comment rule

所有新增或修改的程式碼，必須在安全限制、SCPI 副作用、狀態轉換、例外清理、單位轉換與不直觀邏輯旁加入簡潔的繁體中文註解。不得只寫逐行翻譯或重複程式本身的無意義註解；公開 API 可保留英文 docstring，但關鍵控制流程仍須有中文註解。

All new or modified code must include concise Traditional Chinese comments around safety limits, SCPI side effects, state transitions, exception cleanup, unit conversions, and non-obvious logic. Do not add line-by-line translations or comments that merely repeat the code. Public API docstrings may remain in English, but critical control flow still requires Chinese comments.

## 文件語言規則／Documentation language rule

本專案所有新增或改寫的說明文件，必須先提供完整繁體中文，再提供完整英文；不得只翻譯標題或摘要。程式識別字、SCPI 指令與必要技術名詞可保留英文。

All new or rewritten project documentation must contain a complete Traditional Chinese version first, followed by a complete English version. Translating only headings or summaries is not sufficient. Code identifiers, SCPI commands, and necessary technical terms may remain in English.

## 中文版

### 專案目標與能力邊界

本專案建立可重現的 CMP180 WLAN TX EVM Python 3.11+ 自動化系統，長期產品為中英雙語、響應式公司內網 Web 應用。CMsquares 在探索與除錯期間仍是參考介面。

已完成設定驗證、Mock／實機連線、WLAN discovery、Generator／Analyzer setter、measurement lifecycle、RF On/Off、SingleShot，以及固定三點頻率與四點功率掃描 HIL。Web 固定 profile HIL 已通過；自訂掃描的軟體執行路徑已完成但仍待新的現場 HIL。不得把 dry-run、Mock、預覽、CMsquares 操作或單獨 stored `FETCh` 說成新的完整 Python 自動量測。

### 硬體安全與開發規則

1. 未經要求不得 Reset 儀器或 Workspace。
2. 預設 query-only；`FETCh` 只讀，`READ`／`INITiate` 會啟動量測。
3. RF On 前確認 routing、頻率、頻寬、功率、線材／衰減與輸入限制。
4. RF workflow 必須用 `try/finally`，在錯誤、逾時與取消時仍 Stop／Abort 並 RF Off。
5. SCPI 字串只放 command map 與 typed registry；未驗證命令維持 `null`。
6. 每次功能修改都要更新測試與相關文件，文件必須中文在前、英文在後。
7. 執行 pytest、兩份 YAML validation 與 `git diff --check`，並標示使用 Mock、stored result 或新實機 RF 量測。

### Agent 導航與冗餘邊界

- 長任務與實機作業期間，每次中間回報必須同時說明「目前進度」與「下一步」；不得讓操作員在無狀態說明下等待。
- 本文件是專案 Agent 規則的唯一來源；`CLAUDE.md` 僅作相容性入口，不得視為第二套規則。
- 現行需求與安全邊界以 `SPEC.MD` 為準；文件分類、權威順序與封存狀態以 `docs/README.md` 為準。
- 正式 Web 前端是 `src/cmp180_evm/web/static/`；`static_v2/` 與 `docs/web-v2-design.md` 僅供封存參考。
- `CMP180_DEVELOPMENT_SPEC_AND_PLAN.md` 是早期 CMP180 計畫，`DEVELOPMENT_SPEC_AND_PLAN.md` 是 SMW200A／FSW85 歷史資料；兩者都不取代 `SPEC.MD`。
- `HANDOFF.md` 是累積的變更與硬體證據日誌；能力判定要交叉核對 `README.md`、`docs/README.md` 與最新證據，不只看舊的下一步清單。
- `output/` 是本機資料根目錄：被文件或 metadata 引用的 real／stored artifacts 是證據；`pytest-*`、cache、`__pycache__`、`*.egg-info`、`.venv` 與 `.tools` 是可重建產物，不是原始碼或規範。
- `workflow/*_validation.py`、對應的 `scripts/*_validate.py` 與測試是刻意的驗證分層，不得只因名稱相近就刪除或合併。
- 修改前先確認正式實作路徑、相鄰測試與 `docs/development-workflow.md`；不要自行刪除封存資料、量測證據或驗證入口。

---

## English Version

This file defines the working rules for humans and coding agents in this repository. It applies to the entire repository.

## Project goal

Build a reproducible Python 3.11+ automation system for Rohde & Schwarz CMP180 WLAN TX EVM measurements. The long-term product is a bilingual, responsive intranet web application. CMsquares remains the reference UI during hardware discovery and troubleshooting.

## Current capability boundary

- Implemented: configuration validation, mock and real connection checks, WLAN discovery, Generator/Analyzer setters, measurement lifecycle, RF On/Off, and a complete Python SingleShot with 28-field OFDM SISO result artifacts.
- Hardware verified: `192.168.200.50:5025`, WLAN MEAS1, RF1.1-to-RF1.5 direct-cable loopback, 6105 MHz, 320 MHz, -40 dBm Generator power, -20 dBm expected power, and deterministic cleanup.
- Fixed frequency/power sweeps and guarded Web execution passed HIL. User-defined sweep execution is software-wired but remains locked behind a separate startup flag until a new on-site HIL passes.

Never describe a dry-run, mock result, CMsquares action, or a standalone stored `FETCh` as a new fully automated Python measurement. Only the verified end-to-end SingleShot workflow qualifies.

## Hardware safety invariants

1. Do not reset the instrument or workspace unless explicitly requested.
2. Default to query-only SCPI. `FETCh` reads a stored result; `READ` and `INITiate` start measurements and require an approved workflow.
3. Do not enable RF until routing, frequency, waveform bandwidth, expected input power, cable/attenuator loss, and maximum input level are confirmed.
4. Use low generator power for first loopback validation. The verified reference used RF1.1 to RF1.5, 6105 MHz, 320 MHz and -40 dBm.
5. Every RF workflow must use `try/finally` semantics and attempt measurement stop/abort and RF off on success, error, cancellation, and timeout.
6. After hardware access, query the SCPI error queue and record final RF and measurement state.
7. Do not publish license keys, activation data, unrestricted device dumps, or private company network information beyond the approved test address.

Read `docs/hardware-test-sop.md` before real-hardware operation.

## SCPI rules

- SCPI strings live only in `configs/scpi_command_map.yaml` and the typed registry in `src/cmp180_evm/scpi/registry.py`.
- A command remains `null` until confirmed by CMP180 built-in help, an official manual, or controlled hardware discovery.
- Do not copy commands from unrelated R&S instruments.
- Add a test and update `docs/scpi-command-matrix.md` whenever a command becomes verified.

## Change workflow

The full change procedure, doc-sync table, and pre-commit checklist live in
`docs/development-workflow.md` — follow that document. In addition to it,
every agent-run change must state clearly which checks used mock data,
stored hardware results, or a new live RF measurement.

## Architecture direction

- Keep instrument sessions and SCPI transport out of GUI code.
- Model measurement execution as an explicit state machine.
- Keep safety validation independent and unit-testable.
- Store raw instrument responses together with normalized results.
- The future web UI must support Traditional Chinese and English, responsive layouts, progress, cancellation, audit logs and role-based access for RF-changing actions.

## Agent navigation and clutter boundaries

- During long-running tasks and live-hardware work, every intermediate update must state
  both the current progress and the next step; do not leave the operator waiting without
  a status explanation.
- This file is the single source of project rules; `CLAUDE.md` is a compatibility entry point, not a second rule set.
- Treat `SPEC.MD` as the authority for current requirements and safety boundaries. Use `docs/README.md` for document classification, authority order, and archive status.
- The supported Web frontend is `src/cmp180_evm/web/static/`; `static_v2/` and `docs/web-v2-design.md` are archived references only.
- `CMP180_DEVELOPMENT_SPEC_AND_PLAN.md` is an early CMP180 plan, while `DEVELOPMENT_SPEC_AND_PLAN.md` is archived SMW200A/FSW85 history. Neither supersedes `SPEC.MD`.
- `HANDOFF.md` is a cumulative change and hardware-evidence log. Cross-check capability claims against `README.md`, `docs/README.md`, and the latest evidence instead of trusting old next-step lists alone.
- `output/` is local data: real/stored artifacts referenced by documentation are evidence; `pytest-*`, caches, `__pycache__`, `*.egg-info`, `.venv`, and `.tools` are rebuildable outputs, not source or policy.
- `workflow/*_validation.py`, matching `scripts/*_validate.py`, and their tests are intentional validation layers; do not remove or merge them merely because their names are similar.
- Before editing, confirm the supported implementation path, neighboring tests, and `docs/development-workflow.md`; do not delete archived material, measurement evidence, or validation entry points on your own.

## Important references

- `README.md`: setup and overview
- `docs/hardware-test-sop.md`: operator SOP
- `docs/hardware-discovery.md`: verified device facts and golden result
- `docs/scpi-command-matrix.md`: command status and result schema
- `docs/user-guide.md`: current user commands
- `CMP180_DEVELOPMENT_SPEC_AND_PLAN.md`: broader development plan

