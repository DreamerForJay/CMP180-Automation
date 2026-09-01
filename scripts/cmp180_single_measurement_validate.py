"""Run the first controlled real CMP180 WLAN loopback SingleShot."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from RsInstrument import RsInstrument

from cmp180_evm.results.artifacts import save_single_result
from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.cmp180_single_backend import Cmp180SingleMeasurementBackend
from cmp180_evm.workflow.single_measurement import (
    SingleMeasurementPlan,
    run_single_measurement,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", default="TCPIP::192.168.200.50::5025::SOCKET")
    parser.add_argument("--command-map", type=Path, default=Path("configs/scpi_command_map.yaml"))
    parser.add_argument("--confirm-direct-cable", action="store_true")
    parser.add_argument("--confirm-operator-present", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not (args.confirm_direct_cable and args.confirm_operator_present):
        # 真實 SingleShot 會產生 RF，必須同時確認接線與現場操作員。
        print("Refusing live measurement without both confirmations.", file=sys.stderr)
        return 2
    registry = load_scpi_command_map(args.command_map)
    instrument: RsInstrument | None = None
    try:
        instrument = RsInstrument(
            args.resource,
            id_query=False,
            reset=False,
            options="SelectVisa='socketio'",
        )
        instrument.visa_timeout = 15_000
        print(f"IDN: {instrument.query_str(registry.require('common.identify')).strip()}")
        # Statistic Count 10 的實機 SingleShot 可能超過 15 秒；只延長等待，
        # 不改功率、路徑或 trigger，逾時仍由 workflow 執行 STOP 與 RF Off。
        backend = Cmp180SingleMeasurementBackend(instrument, registry, timeout_s=60.0)
        plan = SingleMeasurementPlan(
            generator_port="RF1.1",
            analyzer_port="RF1.5",
            center_frequency_hz=6_105_000_000,
            bandwidth_hz=320_000_000,
            generator_power_dbm=-40.0,
            expected_nominal_power_dbm=-20.0,
            external_attenuation_db=0.0,
            operator_confirmed=True,
            maximum_generator_power_dbm=-40.0,
        )
        result = run_single_measurement(backend, plan)
        artifacts = save_single_result(
            result.values,
            Path("output"),
            test_name="real-single-6105mhz",
            simulated=False,
            metadata={
                "resource": args.resource,
                "frequency_hz": plan.center_frequency_hz,
                "bandwidth_hz": plan.bandwidth_hz,
                "generator_power_dbm": plan.generator_power_dbm,
                "expected_nominal_power_dbm": plan.expected_nominal_power_dbm,
                "generator_port": plan.generator_port,
                "analyzer_port": plan.analyzer_port,
                "instrument_errors": result.instrument_errors,
                "cleanup_errors": result.cleanup_errors,
            },
        )
        # 儀器可能以 RDY 結束但回傳 INV；不可把無效量測誤報為實機 PASS。
        critical_fields = ("evm_all_carriers_db", "burst_power_dbm", "frequency_error_hz")
        invalid_fields = []
        for field in critical_fields:
            try:
                valid = math.isfinite(float(result.values[field]))
            except (KeyError, TypeError, ValueError):
                valid = False
            if not valid:
                invalid_fields.append(field)
        if invalid_fields:
            print(
                f"FAIL invalid critical result fields: {', '.join(invalid_fields)}",
                file=sys.stderr,
            )
            print(f"  Artifacts: {json.dumps(artifacts)}")
            return 4
        print("PASS real SingleShot")
        print(f"  EVM all: {result.values['evm_all_carriers_db']} dB")
        print(f"  Burst power: {result.values['burst_power_dbm']} dBm")
        print(f"  Frequency error: {result.values['frequency_error_hz']} Hz")
        print(f"  Phases: {','.join(phase.value for phase in result.phases)}")
        print(f"  Cleanup errors: {json.dumps(result.cleanup_errors)}")
        print(f"  Instrument errors: {json.dumps(result.instrument_errors)}")
        print(f"  Artifacts: {json.dumps(artifacts)}")
    except Exception as exc:
        print(f"Real SingleShot failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3
    finally:
        if instrument is not None:
            instrument.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
