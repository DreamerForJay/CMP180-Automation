"""Validate CMP180 GPRF measurement setters by writing back current values with RF off."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from RsInstrument import RsInstrument

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.gprf_measurement_validation import (
    validate_gprf_measurement_setters,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", default="TCPIP::192.168.200.50::5025::SOCKET")
    parser.add_argument("--timeout-ms", type=int, default=10_000)
    parser.add_argument(
        "--command-map", type=Path, default=Path("configs/scpi_command_map.yaml")
    )
    parser.add_argument(
        "--confirm-same-value-write",
        action="store_true",
        help="Confirm writing the current GPRF routing/level values back while RF is OFF.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.confirm_same_value_write:
        print(
            "Refusing to write. Re-run with --confirm-same-value-write after checking RF is OFF.",
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
        result = validate_gprf_measurement_setters(instrument, registry)
        for check in result.checks:
            print(
                f"PASS {check.name:22} original={check.original!r} "
                f"readback={check.readback!r} [{check.error}]"
            )
        print(f"PASS RF state              {result.initial_rf_state} -> {result.final_rf_state}")
    except Exception as exc:
        print(f"GPRF setter validation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3
    finally:
        if instrument is not None:
            instrument.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
