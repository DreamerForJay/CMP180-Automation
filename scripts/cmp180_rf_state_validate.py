"""Run a brief -40 dBm CMP180 Generator RF On/Off validation pulse."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from RsInstrument import RsInstrument

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.rf_state_validation import validate_low_power_rf_pulse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", default="TCPIP::192.168.200.50::5025::SOCKET")
    parser.add_argument("--timeout-ms", type=int, default=10_000)
    parser.add_argument(
        "--command-map", type=Path, default=Path("configs/scpi_command_map.yaml")
    )
    parser.add_argument("--confirm-direct-cable", action="store_true")
    parser.add_argument("--confirm-operator-present", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not (args.confirm_direct_cable and args.confirm_operator_present):
        # 兩個人工確認缺一不可，避免遠端或線路未知時產生 RF。
        print(
            "Refusing RF pulse. Confirm both direct cable and operator presence.",
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
        result = validate_low_power_rf_pulse(
            instrument,
            registry,
            operator_confirmed_direct_cable=True,
        )
        print(
            f"PASS RF pulse frequency={result.frequency_hz / 1e6:g} MHz "
            f"power={result.power_dbm:g} dBm state={result.on_state}->{result.final_state}"
        )
        print(f"PASS RF On error  [{result.on_error}]")
        print(f"PASS RF Off error [{result.off_error}]")
    except Exception as exc:
        print(f"RF state validation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3
    finally:
        if instrument is not None:
            instrument.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
