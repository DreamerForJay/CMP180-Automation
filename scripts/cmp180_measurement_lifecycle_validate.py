"""Validate CMP180 WLAN INITiate/STOP/ABORt with Generator RF off."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from RsInstrument import RsInstrument

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.measurement_lifecycle_validation import (
    validate_measurement_lifecycle,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", default="TCPIP::192.168.200.50::5025::SOCKET")
    parser.add_argument("--timeout-ms", type=int, default=10_000)
    parser.add_argument(
        "--command-map", type=Path, default=Path("configs/scpi_command_map.yaml")
    )
    parser.add_argument(
        "--confirm-analyzer-lifecycle",
        action="store_true",
        help="Confirm INIT/STOP and INIT/ABORT while Generator RF remains OFF.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.confirm_analyzer_lifecycle:
        # 明確確認參數避免操作員誤啟動 Analyzer measurement lifecycle。
        print(
            "Refusing lifecycle writes. Re-run with --confirm-analyzer-lifecycle.",
            file=sys.stderr,
        )
        return 2

    instrument: RsInstrument | None = None
    try:
        registry = load_scpi_command_map(args.command_map)
        instrument = RsInstrument(
            args.resource,
            id_query=False,
            reset=False,
            options="SelectVisa='socketio'",
        )
        instrument.visa_timeout = args.timeout_ms
        print(f"IDN: {instrument.query_str(registry.require('common.identify')).strip()}")
        result = validate_measurement_lifecycle(instrument, registry)
        for event in result.events:
            print(f"PASS {event.action:20} state={event.state!r} [{event.error}]")
        print(
            f"PASS final measurement={result.final_state}; "
            f"Generator={result.final_generator_state}"
        )
    except Exception as exc:
        print(f"Lifecycle validation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3
    finally:
        if instrument is not None:
            instrument.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
