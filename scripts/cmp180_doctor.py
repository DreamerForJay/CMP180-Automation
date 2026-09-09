"""Minimal, read-only CMP180 connection diagnostic."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

from RsInstrument import RsInstrument


@dataclass(frozen=True)
class DiagnosticResult:
    resource: str
    idn: str
    opc: str
    error: str


def diagnose(resource: str, timeout_ms: int, options: str) -> DiagnosticResult:
    instrument: RsInstrument | None = None
    try:
        instrument = RsInstrument(
            resource,
            id_query=False,
            reset=False,
            options=options,
        )
        instrument.visa_timeout = timeout_ms
        idn = instrument.query_str("*IDN?").strip()
        opc = instrument.query_str("*OPC?").strip()
        error = instrument.query_str("SYST:ERR?").strip()
        return DiagnosticResult(resource, idn, opc, error)
    finally:
        if instrument is not None:
            instrument.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--resource",
        default="TCPIP::192.168.200.50::5025::SOCKET",
        help="VISA resource string for the CMP180",
    )
    parser.add_argument(
        "--options",
        default="SelectVisa='socketio'",
        help="RsInstrument driver options",
    )
    parser.add_argument("--timeout-ms", type=int, default=10_000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(f"Resource : {args.resource}")
    try:
        result = diagnose(args.resource, args.timeout_ms, args.options)
    except Exception as exc:  # Diagnostic CLI must show vendor exception details.
        print("Status   : FAIL", file=sys.stderr)
        print(f"Error    : {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3

    print("Status   : PASS")
    print(f"IDN      : {result.idn}")
    print(f"OPC      : {result.opc}")
    print(f"SCPI Err : {result.error}")

    idn_fields = [field.strip().upper() for field in result.idn.split(",")]
    if len(idn_fields) < 2 or idn_fields[1] not in {"CMP", "CMP180"}:
        print("Warning  : Instrument identity is not CMP/CMP180.", file=sys.stderr)
        return 3
    if result.opc != "1":
        print("Warning  : Unexpected *OPC? response.", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
