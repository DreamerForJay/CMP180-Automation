"""Read-only discovery of the configured CMP180 WLAN measurement instance."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass

from RsInstrument import RsInstrument


@dataclass(frozen=True)
class QueryResult:
    name: str
    command: str
    response: str | None
    scpi_error: str | None
    exception: str | None


QUERIES: tuple[tuple[str, str], ...] = (
    ("standard", "CONF:WLAN:MEAS:ISIG:STAN?"),
    ("bandwidth", "CONF:WLAN:MEAS:ISIG:BWID?"),
    ("rf_path_catalog", "CAT:WLAN:MEAS:SPAT?"),
    ("rf_path", "ROUT:WLAN:MEAS:SPAT?"),
    ("rf_path_count", "ROUT:WLAN:MEAS:SPAT:COUN?"),
    ("external_attenuation", "CONF:WLAN:MEAS:RFSettings:EATT?"),
    ("expected_nominal_power", "CONF:WLAN:MEAS:RFSettings:ENP?"),
    ("band", "CONF:WLAN:MEAS:RFSettings:FREQ:BAND?"),
    ("center_frequency", "CONF:WLAN:MEAS:RFSettings:FREQ?"),
    ("channels", "CONF:WLAN:MEAS:RFSettings:FREQ:CHAN?"),
    ("trigger_source_catalog", "TRIG:WLAN:MEAS:MEV:CAT:SOUR?"),
    ("trigger_source", "TRIG:WLAN:MEAS:MEV:SOUR?"),
    ("trigger_threshold", "TRIG:WLAN:MEAS:MEV:THR?"),
    ("trigger_offset", "TRIG:WLAN:MEAS:MEV:OFFS?"),
    ("trigger_min_gap", "TRIG:WLAN:MEAS:MEV:MGAP?"),
    ("trigger_slope", "TRIG:WLAN:MEAS:MEV:SLOP?"),
    ("trigger_timeout", "TRIG:WLAN:MEAS:MEV:TOUT?"),
    ("measurement_state", "FETC:WLAN:MEAS:MEV:STAT?"),
    ("measurement_states", "FETC:WLAN:MEAS:MEV:STAT:ALL?"),
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
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
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
        results = [query_one(instrument, name, command) for name, command in QUERIES]
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
