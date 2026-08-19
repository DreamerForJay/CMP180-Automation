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

已完成設定驗證、Mock／實機連線、WLAN discovery、Generator／Analyzer setter、measurement lifecycle、RF On/Off，以及 RF1.1→RF1.5、6105 MHz、320 MHz、-40 dBm 的完整 Python SingleShot。完整 SingleShot 後已擷取並保存 28 欄 OFDM SISO 結果。Frequency sweep 與 GUI 實機模式仍未完成；不得把 dry-run、Mock、CMsquares 操作或單獨 stored `FETCh` 說成新的完整 Python 自動量測。

### 硬體安全與開發規則

1. 未經要求不得 Reset 儀器或 Workspace。
2. 預設 query-only；`FETCh` 只讀，`READ`／`INITiate` 會啟動量測。
3. RF On 前確認 routing、頻率、頻寬、功率、線材／衰減與輸入限制。
4. RF workflow 必須用 `try/finally`，在錯誤、逾時與取消時仍 Stop／Abort 並 RF Off。
5. SCPI 字串只放 command map 與 typed registry；未驗證命令維持 `null`。
6. 每次功能修改都要更新測試與相關文件，文件必須中文在前、英文在後。
7. 執行 pytest、兩份 YAML validation 與 `git diff --check`，並標示使用 Mock、stored result 或新實機 RF 量測。

---

## English Version

This file defines the working rules for humans and coding agents in this repository. It applies to the entire repository.

## Project goal

Build a reproducible Python 3.11+ automation system for Rohde & Schwarz CMP180 WLAN TX EVM measurements. The long-term product is a bilingual, responsive intranet web application. CMsquares remains the reference UI during hardware discovery and troubleshooting.

## Current capability boundary

- Implemented: configuration validation, mock and real connection checks, WLAN discovery, Generator/Analyzer setters, measurement lifecycle, RF On/Off, and a complete Python SingleShot with 28-field OFDM SISO result artifacts.
- Hardware verified: `192.168.200.50:5025`, WLAN MEAS1, RF1.1-to-RF1.5 direct-cable loopback, 6105 MHz, 320 MHz, -40 dBm Generator power, -20 dBm expected power, and deterministic cleanup.
- Not yet implemented: real frequency sweep and unlocked real-hardware Web GUI operation.

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

1. Inspect `git status` and preserve unrelated user changes.
2. Make the smallest safe change and add/update tests.
3. Update every affected document in the same change. Consider `README.md`, `docs/user-guide.md`, `docs/hardware-test-sop.md`, `docs/scpi-command-matrix.md`, and `docs/hardware-discovery.md`.
4. Run:

   ```powershell
   .\.venv\Scripts\python.exe -m pytest --basetemp .pytest-tmp
   .\.venv\Scripts\python.exe -m cmp180_evm validate-config configs\instrument.example.yaml
   .\.venv\Scripts\python.exe -m cmp180_evm validate-config configs\wlan_baseline.example.yaml
   git diff --check
   ```

5. State clearly which checks used mock data, stored hardware results, or a new live RF measurement.

## Architecture direction

- Keep instrument sessions and SCPI transport out of GUI code.
- Model measurement execution as an explicit state machine.
- Keep safety validation independent and unit-testable.
- Store raw instrument responses together with normalized results.
- The future web UI must support Traditional Chinese and English, responsive layouts, progress, cancellation, audit logs and role-based access for RF-changing actions.

## Important references

- `README.md`: setup and overview
- `docs/hardware-test-sop.md`: operator SOP
- `docs/hardware-discovery.md`: verified device facts and golden result
- `docs/scpi-command-matrix.md`: command status and result schema
- `docs/user-guide.md`: current user commands
- `CMP180_DEVELOPMENT_SPEC_AND_PLAN.md`: broader development plan

