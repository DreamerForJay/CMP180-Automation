# CLAUDE.md

## 中文版本

本文件提供 Claude Code 在此儲存庫工作的完整指引；所有 Agent 仍必須優先遵守
`AGENTS.md`。

### 專案

本專案以 Python 3.11+ 自動化 Rohde & Schwarz CMP180 WLAN TX EVM 量測，將
CMsquares 人工作業改為可重現、可稽核的流程。長期產品是繁體中文／英文雙語、
響應式公司內網 Web 工具；探索與除錯期間仍以 CMsquares 為參考介面。

Mock、dry-run、CMsquares 手動操作或單獨 stored `FETCh`，都不得描述成新的完整
Python 實機量測。現在唯一完成實機驗證的 profile 是 RF1.1 → RF1.5 直連線、
6105 MHz、320 MHz 與 -40 dBm；證據見 `docs/hardware-discovery.md`。

### 常用命令

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,hardware]"
python -m pytest -m "not hardware"
python -m pytest tests/unit/test_frequency_sweep.py
python -m cmp180_evm validate-config configs\instrument.example.yaml
python -m cmp180_evm validate-config configs\wlan_baseline.example.yaml
python -m cmp180_evm dry-run --config configs\wlan_baseline.example.yaml
python -m cmp180_evm test-connection --mock
python -m cmp180_evm.web
python -m cmp180_evm.web --host 127.0.0.1 --enable-hardware
.\scripts\precommit_check.ps1
git diff --check
git status --short
```

標記為 `hardware` 的測試需要真實 CMP180，CI 永遠不執行。GitHub Windows runner
無法連入實驗室網段；實機 RF 驗證只能在核准的 CMP180 與現場操作員旁進行。

### 架構

#### SCPI 集中管理

`src/cmp180_evm/scpi/registry.py` 與 `configs/scpi_command_map.yaml` 是 CMP180
SCPI 字串唯一位置。未經官方文件、內建 Help 或受控實機驗證的命令必須維持
`null`；不得從其他 R&S 儀器猜測命令。新增命令前，必須在
`docs/scpi-command-matrix.md` 記錄完整命令、參數／單位、回傳欄位、來源、韌體、
驗證日期、錯誤佇列與副作用。

#### Transport 與 workflow 分離

`instrument/base.py` 定義 session protocol；`instrument/session.py` 以
`RsInstrument` 實作真實 transport；`instrument/mock_cmp180.py` 提供 Mock。
Transport 不知道 WLAN 或 Generator 業務命令，workflow 也不得直接建立 GUI 相依。

#### 明確且安全優先的量測狀態機

`workflow/single_measurement.py` 在任何 RF 寫入前驗證操作員確認、routing、頻率、
頻寬與功率，並依 `VALIDATING → CONFIGURING → RF_ON → MEASURING → FETCHING →
CLEANING_UP → COMPLETE` 執行。無論成功、錯誤、逾時或取消，都必須在 `finally`
嘗試 Stop 與 RF Off，且 cleanup 錯誤不得遮蔽原始錯誤。

`frequency_sweep.py` 與 `power_sweep.py` 以多次完整 SingleShot 組成掃描。每點之間
都完成 cleanup；失敗時保留已成功點。

執行閘門只保留儀器物理上做不到的項目：Generator／Analyzer port 必須不同、
中心頻率 400 MHz–8 GHz、頻寬必須是已安裝的 20／40／80／160／320 MHz、
dwell 0.01–10 秒、點數上限 100,000（資源防呆）。**HIL／approved profile 已不再參與
執行判定**：未經 HIL 的頻段、頻寬與功率組合一律可以實際量測。

Generator 功率上限由呼叫端以 `maximum_generator_power_dbm` 宣告（依實際接線、
衰減器與 DUT 決定）；未指定時等於本次要求的功率，也就是不額外設限。專案不再
硬寫 -30 dBm 保守值擋住量測——這代表軟體不會替你確認 analyzer 最大輸入準位，
接線與衰減是否安全必須由操作員負責。

不在標準 WLAN channel plan 內的組合不再被擋下，只在 preview 與 artifact metadata
標示 `band_supported` / `standard_wlan_channel=false`；這類結果通常會是 INV，
且一律不得作為 compliance 宣稱。

其他 `workflow/*_validation.py` 與同名 `scripts/cmp180_*_validate.py`、SCPI matrix
必須視為同一組變更與驗證證據。

#### 設定驗證

`config/models.py` 對應兩份 YAML；跨欄位規則放在 `config/validators.py`；
`config/loader.py` 判斷設定種類；CLI 透過 `actions.validate_config()` 使用同一邏輯。

#### CLI 共用邏輯

`cli.py` 是 `actions.py` 上的薄層。舊 Tkinter GUI 已由 Web GUI 取代並移除；新增
CLI 功能時先實作共用 action，再接 CLI，不得複製量測邏輯。

#### 結果與原始資料並存

`results/ofdm_siso.py` 解析 28 欄 OFDM SISO；`results/artifacts.py` 為每次 run
保存 CSV、JSON、metadata、raw response 與已做 HTML escaping 的 report。儀器回應
跨越信任邊界，輸出 HTML 前必須 escape；raw response 必須保留供離線重解析。

#### Web GUI 與實機隔離

`web/server.py` 使用標準函式庫 HTTP server。`/api/mock/*` 永遠只回傳模擬資料；
`/api/hardware/single` 只有 `--enable-hardware`、loopback bind、正確線路確認與現場
操作員確認時才能使用，而且固定於已驗證 profile。`/artifacts` 必須檢查解析後路徑
仍位於 `output/`。`real_service.py` 在 workflow cleanup 外再做獨立緊急收尾，最後
必須確認 RF `OFF`、measurement `RDY`。目前沒有 authentication／RBAC，硬體模式
不得綁定內網位址。

### 專案規則

- 安全限制、SCPI 副作用、狀態轉換、例外清理、單位轉換與不直觀邏輯旁必須有
  簡潔繁體中文註解。
- 新增或改寫的說明文件以繁體中文撰寫即可，不再要求提供英文版本；程式識別字、SCPI 指令與必要技術名詞可保留英文，既有雙語文件不必為此回溯刪除英文。
- 未經要求不得 Reset 儀器或 Workspace；預設 query-only。
- RF On 前確認 routing、頻率、頻寬、功率、線材／衰減與輸入限制。
- 所有 RF workflow 都必須保證 Stop／Abort 與 RF Off cleanup。
- 功能修改必須同時更新測試與相關文件。
- 完成前執行 pytest、兩份 YAML validation 與 `git diff --check`，並說明使用的是
  Mock、stored result 或新實機 RF。
- 不得提交 `.venv`、logs、`output/`、credentials、license／activation data、cache、
  私人 device dump 或 `.claude/settings.local.json`。

## English Version

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Python 3.11+ automation for Rohde & Schwarz CMP180 WLAN TX EVM measurements, replacing manual CMsquares operation with reproducible, auditable workflows. Long-term product is a bilingual (Traditional Chinese/English), responsive intranet Web tool. CMsquares remains the reference UI during hardware discovery/troubleshooting.

Do not describe a mock result, dry-run, CMsquares manual action, or a standalone stored `FETCh` as a new fully automated Python hardware measurement — only a complete, live SingleShot/sweep run qualifies. The only currently hardware-verified profile is RF1.1 → RF1.5 direct-cable loopback, 6105 MHz, 320 MHz bandwidth, -40 dBm generator power (see `docs/hardware-discovery.md`).

## Commands

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,hardware]"

# Full test suite (excludes hardware-marked tests; this is what CI runs)
python -m pytest -m "not hardware"

# Single test file / test
python -m pytest tests/unit/test_frequency_sweep.py
python -m pytest tests/unit/test_frequency_sweep.py::test_name -v

# Config validation (also run in CI)
python -m cmp180_evm validate-config configs\instrument.example.yaml
python -m cmp180_evm validate-config configs\wlan_baseline.example.yaml

# Dry-run / mock connection (no SCPI writes)
python -m cmp180_evm dry-run --config configs\wlan_baseline.example.yaml
python -m cmp180_evm test-connection --mock

# Web GUI (mock-only by default)
python -m cmp180_evm.web
# Local guarded hardware SingleShot — hardware mode may bind ONLY to loopback
python -m cmp180_evm.web --host 127.0.0.1 --enable-hardware

# Pre-commit checklist (see docs/development-workflow.md)
New-Item -ItemType Directory -Force output | Out-Null
.\.venv\Scripts\python.exe -m pytest -q --basetemp=output\pytest-tmp
git diff --check
git status --short
```

Tests marked `hardware` require a real CMP180 connection and are never run in CI (`.github/workflows/ci.yml`, Windows/Python 3.11 runner — it cannot reach the lab CMP180 network segment). Real RF validation only happens against the approved lab endpoint `192.168.200.50:5025`.

## Architecture

### SCPI commands live in exactly one place

`src/cmp180_evm/scpi/registry.py` (`ScpiCommandRegistry`) is the *only* place SCPI command strings may live, backed by `configs/scpi_command_map.yaml`. Every generator/wlan_tx/results write command starts as `None` and stays `None` until verified on real hardware and recorded with full provenance in `docs/scpi-command-matrix.md` (function, exact command string, params/units, return fields/units, source manual/help/recorder, firmware version, verification date, success + error-queue evidence, and whether it changes RF/routing/workspace/measurement state). `registry.require("section.field")` raises `ScpiCommandNotConfiguredError` instead of returning `None` or guessing — never invent or borrow a command from another R&S instrument. Callers look commands up by dotted name (`generator.rf_off`, `wlan_tx_query.measurement_state`, ...); no module outside `scpi/` should hardcode a CMP180-specific SCPI string.

### Transport is separated from workflow logic

- `instrument/base.py` defines the `InstrumentSession` protocol (connect/disconnect/write/query/query_float/query_int/query_csv/wait_opc/clear_status/drain_error_queue).
- `instrument/session.py` (`Cmp180Session`) implements it via `RsInstrument`, imported lazily so the rest of the project works without the optional `hardware` extra installed. It knows nothing about WLAN/generator commands — only generic SCPI primitives; command strings are always passed in by callers via the registry.
- `instrument/mock_cmp180.py` implements the same protocol so workflow code is written once and runs unchanged against real or mock hardware.

### Measurement is an explicit, safety-first state machine

`workflow/single_measurement.py`: `SingleMeasurementPlan.validate_safety()` enforces operator confirmation, distinct generator/analyzer ports, and a power ceiling *before* any RF write. `run_single_measurement()` drives phases `VALIDATING → CONFIGURING → RF_ON → MEASURING → FETCHING → CLEANING_UP → COMPLETE` against a `MeasurementBackend` protocol (configure/rf_on/initiate_single/wait_ready/fetch_result/stop_measurement/rf_off/drain_error_queue). Cleanup (`stop_measurement`, `rf_off`) always runs in a `finally` block regardless of success, exception, or cancellation, and cleanup failures are collected rather than masking the original error. `workflow/cmp180_single_backend.py` is the real hardware implementation of `MeasurementBackend`.

`workflow/frequency_sweep.py` builds a sweep out of repeated, fully-cleaned-up `run_single_measurement` calls (never a single long-running sweep primitive). Execution is gated only by what the instrument can physically accept: distinct generator/analyzer ports, center frequency 400 MHz–8 GHz, an installed WLAN bandwidth (20/40/80/160/320 MHz), dwell 0.01–10 s, and a point-count resource guard. HIL/approved-profile evidence no longer gates execution — un-validated frequency, bandwidth, and power combinations run. The generator power ceiling comes from the caller's `maximum_generator_power_dbm` (defaulting to the requested power, i.e. no extra cap), so confirming the analyzer's maximum input level for the actual cabling/attenuation is the operator's responsibility, not the software's. Combinations outside the standard WLAN channel plan are flagged (`band_supported` / `standard_wlan_channel=false`) rather than blocked; they usually return INV and may never back a compliance claim. On any point failure it returns a partial `FrequencySweepResult` (previously-succeeded points preserved) rather than losing the whole run — this is why sweep artifacts must always be checked for `completed=False`.

Other `workflow/*_validation.py` modules (`analyzer_setter_validation.py`, `generator_setter_validation.py`, `measurement_lifecycle_validation.py`, `rf_state_validation.py`, `gprf_measurement_validation.py`) are the safety/domain-rule checks paired with the `scripts/cmp180_*_validate.py` hardware discovery/validation scripts of the same name (`gprf_measurement_validation.py` pairs with `scripts/cmp180_gprf_measurement_setter_validate.py`) — treat script + workflow-validation module + matrix doc update as one unit of work.

### Config: pydantic models + separate cross-field validators

`config/models.py` mirrors `configs/instrument.example.yaml` and `configs/wlan_baseline.example.yaml` field-for-field; pydantic enforces types/required-ness only. Cross-field domain rules that need more than one field of context (e.g. band-vs-frequency consistency) live in `config/validators.py`, not in the models. `config/loader.py` detects config kind (instrument vs. WLAN baseline) and loads/validates accordingly; `actions.validate_config()` combines both layers and is what the CLI's `validate-config` command calls.

### `actions.py` is the shared logic layer for the CLI

`cli.py` (argparse) is a thin presentation layer over `actions.py`'s config-validation/dry-run/connection-test functions. There was previously also a Tkinter GUI (`gui/`) sharing this layer; it only ever covered config validation/dry-run/test-connection (never single-measurement, sweep, or RF control) and has been removed now that the Web GUI covers everything it did and more — recoverable from git history if a non-browser interface is needed again. When adding a new CLI-facing action, add it to `actions.py` first, then wire a thin CLI subcommand.

### Results: normalized values + raw response kept side by side

`results/ofdm_siso.py` parses the 28-field OFDM SISO CMP180 response. `results/artifacts.py` (`save_single_result`) persists one immutable run directory (`output/<timestamp>_<test_name>_<run_id>/`) containing `results.csv`, `results.json`, `metadata.json`, `raw/` (raw instrument response, kept independent of parser/schema changes so it can be reprocessed offline), and an XSS-escaped `report.html` (instrument responses cross a trust boundary and must always be HTML-escaped before being written into the report).

### Web GUI: dependency-free stdlib HTTP server, mock/hardware strictly separated

`web/server.py` (`Cmp180WebHandler`, built on `http.server`) serves the static bilingual GUI and a small JSON API:
- `/api/mock/single`, `/api/mock/sweep` → `web/mock_service.py`, always return `simulated: true`, never touch real hardware.
- `/api/hardware/single` → only reachable if the server was started with `--enable-hardware`; requires `cable_confirmation` matching the single hardware-verified route (`RF1.1-RF1.5`) and explicit `operator_present: true`; lazily imports `web/real_service.py` (`run_verified_real_single`) so the mock-only server never loads hardware packages. This endpoint runs only the one fixed, pre-verified 6105 MHz/-40 dBm profile — it does not accept arbitrary frequency/power input.
- `validate_hardware_bind()` refuses to start with `--enable-hardware` unless `--host` is a loopback address — there is no authentication/RBAC yet, so the hardware endpoint must never be exposed beyond localhost.
- `/artifacts/<...>` serves files strictly from `output/`, resolving and checking the path stays under `output/` to block traversal.

`real_service.run_verified_real_single()` does an *additional* independent emergency-cleanup pass in its own `finally` block on top of `run_single_measurement`'s cleanup, and raises if the final read-back RF/measurement state isn't `OFF`/`RDY` — treat this belt-and-suspenders pattern as required, not redundant, for any new hardware-facing endpoint.

## Project-specific rules (from AGENTS.md — apply repo-wide)

- **Code comments**: all new/modified code must carry concise Traditional Chinese comments around safety limits, SCPI side effects, state transitions, exception/cleanup paths, unit conversions, and non-obvious logic. Don't add line-by-line translations or comments that just restate the code. Public API docstrings may stay in English.
- **Documentation language**: new or rewritten docs are written in Traditional Chinese; an English version is no longer required. Code identifiers, SCPI commands, and necessary technical terms may stay in English; existing bilingual docs do not need their English content retroactively removed.
- **Hardware safety invariants**:
  1. Never reset the instrument or workspace unless explicitly requested.
  2. Default to query-only SCPI; `FETCh` only reads a stored result — `READ`/`INITiate` start a measurement and require an approved workflow.
  3. Never enable RF before routing, frequency, bandwidth, expected power, cable/attenuator loss, and max input level are confirmed.
  4. Every RF workflow must use `try/finally` and attempt stop/abort + RF off on success, error, timeout, and cancellation.
  5. SCPI strings only ever live in `configs/scpi_command_map.yaml` + `scpi/registry.py`; unverified commands stay `null`.
  6. Every functional change updates tests and the relevant docs in the same change, Chinese section before English.
  7. Before considering work done: run pytest, both YAML `validate-config` checks, and `git diff --check`; explicitly state whether checks used mock data, a stored hardware result, or a new live RF measurement.
- **Definition of Done** (`docs/development-workflow.md`): code + tests + docs together — a feature with code but no updated user guide/YAML examples/validation evidence is not done. See that file's change-type → required-docs table before finishing a change (e.g. a CLI change touches `README.md` + `docs/user-guide.md` + CLI tests; an SCPI change touches the command map + `docs/scpi-command-matrix.md` + source evidence + registry tests).
- **SCPI documentation minimum**: before adding any command to the command map, record function name, full command/query string, params/units, return fields/units, source (CMP180 Remote Manual/Command Help/SCPI Recorder), firmware/WLAN software version, real-hardware verification date, success + error-queue result, and whether it changes RF/routing/workspace/measurement state. Never guess a CMP180 command from another R&S instrument's syntax.
- Never commit `.venv`, logs, `output/`, credentials, license/activation data, test caches, or private device dumps.
