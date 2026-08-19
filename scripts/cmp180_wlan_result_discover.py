"""Fetch the previous CMP180 WLAN OFDM SISO result without starting RF."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from RsInstrument import RsInstrument

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.results.ofdm_siso import RESULT_FIELDS, parse_result
from cmp180_evm.results.artifacts import save_single_result


QUERY_NAMES = (
    "modulation_current", "modulation_average", "modulation_minimum",
    "modulation_maximum", "modulation_std_dev",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", default="TCPIP::192.168.200.50::5025::SOCKET")
    parser.add_argument("--timeout-ms", type=int, default=10_000)
    parser.add_argument(
        "--command-map", type=Path, default=Path("configs/scpi_command_map.yaml")
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--save-output",
        action="store_true",
        help="Save the latest stored result without initiating a measurement.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = load_scpi_command_map(args.command_map)
    instrument: RsInstrument | None = None
    payload: dict[str, object] = {"read_only": True, "results": {}}
    failed = False
    try:
        instrument = RsInstrument(
            args.resource,
            id_query=False,
            reset=False,
            options="SelectVisa='socketio'",
        )
        instrument.visa_timeout = args.timeout_ms
        payload["idn"] = instrument.query_str("*IDN?").strip()
        payload["state"] = instrument.query_str(
            registry.require("wlan_tx_query.measurement_state")
        ).strip()
        results = payload["results"]
        assert isinstance(results, dict)
        for name in QUERY_NAMES:
            command = registry.require(f"results.{name}")
            response = instrument.query_str(command).strip()
            error = instrument.query_str("SYST:ERR?").strip()
            item: dict[str, object] = {"command": command, "raw": response, "error": error}
            try:
                item["values"] = parse_result(response)
            except ValueError as exc:
                item["parse_error"] = str(exc)
                failed = True
            if not error.startswith("0,"):
                failed = True
            results[name] = item
    except Exception as exc:
        print(f"Result discovery failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3
    finally:
        if instrument is not None:
            instrument.close()

    artifacts: dict[str, str] | None = None
    if args.save_output:
        average = payload["results"]["modulation_average"]
        if isinstance(average, dict) and isinstance(average.get("values"), dict):
            # 這裡保存的是最新 stored FETCh；不把它誤標成這支工具啟動的新量測。
            artifacts = save_single_result(
                {"raw": average["raw"], **average["values"]},
                Path("output"),
                test_name="stored-after-real-single",
                simulated=False,
                metadata={
                    "source": "stored_fetch_after_verified_single_shot",
                    "measurement_state": payload["state"],
                    "instrument_id": payload["idn"],
                },
            )
        else:
            failed = True

    if args.as_json:
        if artifacts is not None:
            payload["artifacts"] = artifacts
        print(json.dumps(payload, indent=2))
    else:
        print(f"IDN: {payload['idn']}")
        print(f"State: {payload['state']}")
        results = payload["results"]
        assert isinstance(results, dict)
        for name, item in results.items():
            assert isinstance(item, dict)
            values = item.get("values")
            if isinstance(values, dict):
                print(
                    f"PASS {name:22} EVM(all)={values['evm_all_carriers_db']} dB "
                    f"Power={values['burst_power_dbm']} dBm "
                    f"FreqErr={values['frequency_error_hz']} Hz [{item['error']}]"
                )
            else:
                print(f"FAIL {name:22} {item.get('parse_error')} [{item['error']}]")
        if artifacts is not None:
            print(f"Artifacts: {json.dumps(artifacts)}")
    return 4 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
