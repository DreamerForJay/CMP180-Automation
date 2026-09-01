"""Discover which CMP180 WLAN band enums this instrument accepts.

這支腳本不發射 RF：它只設定 Analyzer 的 WLAN band、讀回結果、檢查 error queue，
最後把 band 還原成原始值。執行前仍會強制要求 Generator RF 為 OFF 且量測為 idle。

用途：`workflow/wlan_bands.py` 只允許已驗證 enum 的 band 送出 SCPI，2.4／5 GHz 的
enum 目前是 None。本腳本產生的證據要填回 `wlan_bands.py` 與
`docs/scpi-command-matrix.md`（含韌體版本與驗證日期）之後，那些 band 才可執行。

候選字串來自已驗證的 `B6GHz` → readback `B6GH` 命名規律。這裡是「詢問儀器接不接受」，
不是把猜測當成已驗證結果：不被接受的候選會被記錄為 rejected，不會寫進 wlan_bands。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from RsInstrument import RsInstrument

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.analyzer_setter_validation import ALLOWED_IDLE_MEASUREMENT_STATES

# 依 B6GHz/B6GH 規律列出的候選；接受與否完全由儀器回答。
CANDIDATE_BAND_ENUMS = (
    "B24Ghz",
    "B24GHz",
    "B2G4",
    "B5GHz",
    "B5GH",
    "B5Ghz",
    "B6GHz",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", default="TCPIP::192.168.200.50::5025::SOCKET")
    parser.add_argument("--command-map", type=Path, default=Path("configs/scpi_command_map.yaml"))
    parser.add_argument("--confirm-operator-present", action="store_true")
    parser.add_argument(
        "--confirm-analyzer-config-write",
        action="store_true",
        help="Acknowledge that the analyzer WLAN band is written and restored (no RF).",
    )
    return parser.parse_args()


def _drain_errors(instrument: RsInstrument, registry) -> list[str]:
    errors: list[str] = []
    for _ in range(50):
        response = instrument.query_str(registry.require("common.system_error")).strip()
        if response.startswith(("0,", "+0,")):
            break
        errors.append(response)
    return errors


def main() -> int:
    args = parse_args()
    if not (args.confirm_operator_present and args.confirm_analyzer_config_write):
        print("Refusing band discovery without both confirmations.", file=sys.stderr)
        return 2

    registry = load_scpi_command_map(args.command_map)
    instrument: RsInstrument | None = None
    exit_code = 0
    original_band: str | None = None
    try:
        instrument = RsInstrument(
            args.resource, id_query=False, reset=False, options="SelectVisa='socketio'"
        )
        instrument.visa_timeout = 15_000
        # 被拒絕的候選本身就是探索結果；關閉自動狀態例外，改用本腳本的 SYST:ERR? 輪詢，
        # 否則第一個不被接受的字串就會中止整輪探索。
        instrument.instrument_status_checking = False
        print(f"IDN: {instrument.query_str(registry.require('common.identify')).strip()}")

        # 安全前置：Generator 必須 OFF、量測必須 idle，否則不進行任何設定寫入。
        rf_state = instrument.query_str(registry.require("generator_query.state")).strip()
        if rf_state != "OFF":
            print(f"Refusing discovery while generator RF is {rf_state}.", file=sys.stderr)
            return 3
        measurement_state = instrument.query_str(
            registry.require("wlan_tx_query.measurement_state")
        ).strip()
        if measurement_state not in ALLOWED_IDLE_MEASUREMENT_STATES:
            print(f"Refusing discovery while measurement is {measurement_state}.", file=sys.stderr)
            return 3

        original_band = instrument.query_str(registry.require("wlan_tx_query.band")).strip()
        print(f"Original band readback: {original_band}")
        _drain_errors(instrument, registry)

        results: list[dict[str, object]] = []
        for candidate in CANDIDATE_BAND_ENUMS:
            try:
                instrument.write_str(
                    registry.require("wlan_tx.set_band").format(band=candidate)
                )
                instrument.query_str(registry.require("common.operation_complete"))
                errors = _drain_errors(instrument, registry)
            except Exception as exc:  # noqa: BLE001 - 記錄拒絕原因後繼續下一個候選
                errors = [f"{type(exc).__name__}: {exc}"]
                _drain_errors(instrument, registry)
            readback = instrument.query_str(registry.require("wlan_tx_query.band")).strip()
            accepted = not errors
            results.append(
                {
                    "candidate": candidate,
                    "accepted": accepted,
                    "readback": readback,
                    "errors": errors,
                }
            )
            print(
                f"{candidate:>8} -> accepted={accepted} readback={readback!r} errors={errors}"
            )
        print(f"RESULTS: {json.dumps(results)}")
        print(
            "\nRecord every accepted candidate (enum + readback + firmware + date) in "
            "docs/scpi-command-matrix.md, then fill band_enum/band_readback in "
            "src/cmp180_evm/workflow/wlan_bands.py. Do not treat this output alone as "
            "authorization to sweep a new band: each band still needs its own ARB waveform "
            "and a full HIL run."
        )
    except Exception as exc:
        print(f"Band discovery failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        exit_code = 3
    finally:
        if instrument is not None:
            try:
                # 一律還原原始 band，避免把儀器留在探索過程的中間設定。
                if original_band:
                    instrument.write_str(
                        registry.require("wlan_tx.set_band").format(band=original_band)
                    )
                    instrument.query_str(registry.require("common.operation_complete"))
                    restored = instrument.query_str(
                        registry.require("wlan_tx_query.band")
                    ).strip()
                    errors = _drain_errors(instrument, registry)
                    print(f"Restored band: {restored} (errors={errors})")
                    if restored != original_band:
                        print("Band restore mismatch", file=sys.stderr)
                        exit_code = 4
                final_rf = instrument.query_str(registry.require("generator_query.state")).strip()
                print(f"Final generator RF: {final_rf}")
                if final_rf != "OFF":
                    exit_code = 4
            except Exception as exc:
                print(f"Restore failed: {type(exc).__name__}: {exc}", file=sys.stderr)
                exit_code = 4
            finally:
                instrument.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
