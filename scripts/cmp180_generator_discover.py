"""Read CMP180 GPRF Generator settings without changing RF or configuration."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from RsInstrument import RsInstrument

from cmp180_evm.scpi.registry import load_scpi_command_map

QUERY_NAMES = ("frequency", "level", "peak_power", "state", "states", "rf_path")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", default="TCPIP::192.168.200.50::5025::SOCKET")
    parser.add_argument("--timeout-ms", type=int, default=10_000)
    parser.add_argument(
        "--command-map", type=Path, default=Path("configs/scpi_command_map.yaml")
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = load_scpi_command_map(args.command_map)
    instrument: RsInstrument | None = None
    failed = False
    try:
        instrument = RsInstrument(
            args.resource,
            id_query=False,
            reset=False,
            options="SelectVisa='socketio'",
        )
        instrument.visa_timeout = args.timeout_ms
        print(f"IDN: {instrument.query_str(registry.require('common.identify')).strip()}")
        for name in QUERY_NAMES:
            command = registry.require(f"generator_query.{name}")
            response = instrument.query_str(command).strip()
            error = instrument.query_str(registry.require("common.system_error")).strip()
            passed = error.startswith("0,")
            failed = failed or not passed
            print(f"{'PASS' if passed else 'FAIL'} {name:12} {response!r} [{error}]")
    except Exception as exc:
        print(f"Generator discovery failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3
    finally:
        if instrument is not None:
            instrument.close()
    return 4 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
