"""Run the eleven-point, 200 MHz-span CMP180 WLAN frequency-sweep HIL.

Extends the earlier three-point (6085/6105/6125 MHz) HIL to the maximum span
and point count the safety envelope in workflow/frequency_sweep.py allows in
a single sweep (VERIFIED_MAXIMUM_SPAN_HZ=200e6, VERIFIED_MAXIMUM_POINTS=11).
Centered on the already-verified 6105 MHz point.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from RsInstrument import RsInstrument

from cmp180_evm.results.artifacts import save_frequency_sweep_result
from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.cmp180_single_backend import Cmp180SingleMeasurementBackend
from cmp180_evm.workflow.frequency_sweep import FrequencySweepPlan, run_frequency_sweep
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan

FREQUENCIES_HZ = (
    6_005_000_000.0,
    6_025_000_000.0,
    6_045_000_000.0,
    6_065_000_000.0,
    6_085_000_000.0,
    6_105_000_000.0,
    6_125_000_000.0,
    6_145_000_000.0,
    6_165_000_000.0,
    6_185_000_000.0,
    6_205_000_000.0,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", default="TCPIP::192.168.200.50::5025::SOCKET")
    parser.add_argument("--command-map", type=Path, default=Path("configs/scpi_command_map.yaml"))
    parser.add_argument("--output-root", type=Path, default=Path("output"))
    parser.add_argument("--confirm-direct-cable", action="store_true")
    parser.add_argument("--confirm-operator-present", action="store_true")
    parser.add_argument("--confirm-eleven-point-sweep", action="store_true")
    return parser.parse_args()


def _emergency_cleanup(instrument: RsInstrument, registry) -> tuple[str, str, list[str]]:
    """Best-effort STOP/ABORT and RF Off followed by final state read-back."""
    try:
        instrument.write_str(registry.require("wlan_tx.stop"))
        instrument.query_str(registry.require("common.operation_complete"))
    except Exception:
        # STOP 失敗時才送 ABORt；清理流程不可因單一步驟失敗而跳過 RF Off。
        try:
            instrument.write_str(registry.require("wlan_tx.abort"))
        except Exception:
            pass
    instrument.write_str(registry.require("generator.rf_off"))
    instrument.query_str(registry.require("common.operation_complete"))
    rf_state = instrument.query_str(registry.require("generator_query.state")).strip()
    measurement_state = instrument.query_str(
        registry.require("wlan_tx_query.measurement_state")
    ).strip()
    errors: list[str] = []
    for _ in range(50):
        response = instrument.query_str(registry.require("common.system_error")).strip()
        if response.startswith(("0,", "+0,")):
            break
        errors.append(response)
    return rf_state, measurement_state, errors


def main() -> int:
    args = parse_args()
    if not (
        args.confirm_direct_cable
        and args.confirm_operator_present
        and args.confirm_eleven_point_sweep
    ):
        print("Refusing live sweep without all three confirmations.", file=sys.stderr)
        return 2

    registry = load_scpi_command_map(args.command_map)
    instrument: RsInstrument | None = None
    exit_code = 0
    try:
        instrument = RsInstrument(
            args.resource, id_query=False, reset=False, options="SelectVisa='socketio'"
        )
        instrument.visa_timeout = 15_000
        print(f"IDN: {instrument.query_str(registry.require('common.identify')).strip()}")
        backend = Cmp180SingleMeasurementBackend(instrument, registry, timeout_s=15.0)
        single = SingleMeasurementPlan(
            generator_port="RF1.1",
            analyzer_port="RF1.5",
            center_frequency_hz=FREQUENCIES_HZ[0],
            bandwidth_hz=320_000_000,
            generator_power_dbm=-40.0,
            expected_nominal_power_dbm=-20.0,
            external_attenuation_db=0.0,
            operator_confirmed=True,
            maximum_generator_power_dbm=-40.0,
        )
        # 這批固定 11 點、200 MHz span、100 ms dwell，是現有硬性包絡在單次掃描下的
        # 最大值；不開放任意頻率或功率參數。
        plan = FrequencySweepPlan(
            single=single,
            start_frequency_hz=FREQUENCIES_HZ[0],
            stop_frequency_hz=FREQUENCIES_HZ[-1],
            step_frequency_hz=20_000_000,
            dwell_time_s=0.1,
            maximum_points=11,
            minimum_frequency_hz=FREQUENCIES_HZ[0],
            maximum_frequency_hz=FREQUENCIES_HZ[-1],
            maximum_span_hz=200_000_000,
        )
        result = run_frequency_sweep(backend, plan)
        points = []
        for frequency_hz, point in zip(result.requested_frequencies_hz, result.points):
            points.append({"frequency_hz": frequency_hz, **point.values})
        artifacts = save_frequency_sweep_result(
            points,
            args.output_root,
            requested_frequencies_hz=result.requested_frequencies_hz,
            completed=result.completed,
            failed_frequency_hz=result.failed_frequency_hz,
            error=result.error,
            metadata={
                "resource": args.resource,
                "generator_port": "RF1.1",
                "analyzer_port": "RF1.5",
                "bandwidth_hz": 320_000_000,
                "generator_power_dbm": -40.0,
                "expected_nominal_power_dbm": -20.0,
                "dwell_time_s": 0.1,
                "point_instrument_errors": [point.instrument_errors for point in result.points],
                "point_cleanup_errors": [point.cleanup_errors for point in result.points],
            },
        )
        for index, (frequency_hz, point) in enumerate(
            zip(result.requested_frequencies_hz, result.points), start=1
        ):
            print(
                f"POINT {index}/{len(FREQUENCIES_HZ)} {frequency_hz / 1e6:.0f} MHz: "
                f"EVM={point.values['evm_all_carriers_db']} dB, "
                f"Power={point.values['burst_power_dbm']} dBm, "
                f"FreqError={point.values['frequency_error_hz']} Hz"
            )
        print(f"Artifacts: {json.dumps(artifacts)}")
        if not result.completed:
            print(
                f"Sweep stopped at {result.failed_frequency_hz}: {result.error}", file=sys.stderr
            )
            exit_code = 3
    except Exception as exc:
        print(f"Real frequency sweep failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        exit_code = 3
    finally:
        if instrument is not None:
            try:
                rf_state, measurement_state, errors = _emergency_cleanup(instrument, registry)
                print(
                    f"Final state: RF={rf_state}, measurement={measurement_state}, "
                    f"error_queue={json.dumps(errors)}"
                )
                if rf_state != "OFF" or measurement_state not in {"OFF", "RDY"} or errors:
                    exit_code = 4
            except Exception as exc:
                print(f"Emergency cleanup failed: {type(exc).__name__}: {exc}", file=sys.stderr)
                exit_code = 4
            finally:
                instrument.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
