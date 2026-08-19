"""Read-only discovery of the configured CMP180 WLAN measurement instance."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from RsInstrument import RsInstrument
from cmp180_evm.scpi.registry import load_scpi_command_map


@dataclass(frozen=True)
class QueryResult:
    name: str
    command: str
    response: str | None
    scpi_error: str | None
    exception: str | None


QUERY_NAMES: tuple[str, ...] = (
    "standard", "bandwidth", "rf_path_catalog", "rf_path", "rf_path_count",
    "external_attenuation", "expected_nominal_power", "band",
    "center_frequency", "channels", "trigger_source_catalog",
    "trigger_source", "trigger_threshold", "trigger_offset",
    "trigger_min_gap", "trigger_slope", "trigger_timeout",
    "measurement_state", "measurement_states",
)


def query_one(instrument: RsInstrument, name: str, command: str) -> QueryResult:
    try:
        response = instrument.query_str(command).strip()
    except Exception as exc:
        return QueryResult(name, command, None, None, f"{type(exc).__name__}: {exc}")

    try:
        error = instrument.query_str("SYST:ERR?").strip()
    except Exception as exc:
        error = f"Error query failed: {type(exc).__name__}: {exc}"

    return QueryResult(name, command, response, error, None)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--resource",
        default="TCPIP::192.168.200.50::5025::SOCKET",
    )
    parser.add_argument("--timeout-ms", type=int, default=10_000)
    parser.add_argument(
        "--command-map",
        type=Path,
        default=Path("configs/scpi_command_map.yaml"),
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = load_scpi_command_map(args.command_map)
    queries = [
        (name, registry.require(f"wlan_tx_query.{name}"))
        for name in QUERY_NAMES
    ]
    instrument: RsInstrument | None = None
    try:
        instrument = RsInstrument(
            args.resource,
            id_query=False,
            reset=False,
            options="SelectVisa='socketio'",
        )
        instrument.visa_timeout = args.timeout_ms
        idn = instrument.query_str("*IDN?").strip()
        results = [query_one(instrument, name, command) for name, command in queries]
    except Exception as exc:
        print(f"Connection failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3
    finally:
        if instrument is not None:
            instrument.close()

    payload = {
        "resource": args.resource,
        "idn": idn,
        "read_only": True,
        "results": [asdict(result) for result in results],
    }
    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"IDN: {idn}")
        for result in results:
            if result.exception:
                print(f"FAIL {result.name:26} {result.command:50} {result.exception}")
            else:
                print(
                    f"PASS {result.name:26} {result.response!r} "
                    f"[{result.scpi_error}]"
                )

    failures = [result for result in results if result.exception]
    scpi_errors = [
        result
        for result in results
        if result.scpi_error and not result.scpi_error.startswith("0,")
    ]
    return 4 if failures or scpi_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
