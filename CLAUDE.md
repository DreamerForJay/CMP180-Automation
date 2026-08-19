# CLAUDE.md

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

`workflow/frequency_sweep.py` builds a bounded sweep out of repeated, fully-cleaned-up `run_single_measurement` calls (never a single long-running sweep primitive). `FrequencySweepPlan.frequencies()` hard-enforces: RF1.1→RF1.5 only, ≤ -40 dBm, dwell 0.1–2.0s, frequencies within the approved 6 GHz range, span ≤ 200 MHz, ≤ 11 points. On any point failure it returns a partial `FrequencySweepResult` (previously-succeeded points preserved) rather than losing the whole run — this is why sweep artifacts must always be checked for `completed=False`.

Other `workflow/*_validation.py` modules (`analyzer_setter_validation.py`, `generator_setter_validation.py`, `measurement_lifecycle_validation.py`, `rf_state_validation.py`) are the safety/domain-rule checks paired with the `scripts/cmp180_*_validate.py` hardware discovery/validation scripts of the same name — treat script + workflow-validation module + matrix doc update as one unit of work.

### Config: pydantic models + separate cross-field validators

`config/models.py` mirrors `configs/instrument.example.yaml` and `configs/wlan_baseline.example.yaml` field-for-field; pydantic enforces types/required-ness only. Cross-field domain rules that need more than one field of context (e.g. band-vs-frequency consistency) live in `config/validators.py`, not in the models. `config/loader.py` detects config kind (instrument vs. WLAN baseline) and loads/validates accordingly; `actions.validate_config()` combines both layers and is what the CLI's `validate-config` command calls.

### `actions.py` is the shared logic layer for CLI and Tkinter GUI

`cli.py` (argparse) and `gui/app.py` (Tkinter) are both thin presentation layers over `actions.py` — neither duplicates the other's logic. When adding a new user-facing action, add it to `actions.py` first, then wire a thin CLI subcommand and/or GUI handler.

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
- **Documentation language**: new or rewritten docs must be written in full Traditional Chinese first, then full English — not just translated headings/summaries. Code identifiers, SCPI commands, and necessary technical terms may stay in English.
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
