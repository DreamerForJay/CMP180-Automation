"""Run the approved 320 MHz golden point, full 6 GHz sweep, and power sweep once."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from RsInstrument import RsInstrument

from cmp180_evm.results.artifacts import (
    save_frequency_sweep_result,
    save_power_sweep_result,
    save_single_result,
)
from cmp180_evm.results.validity import invalid_critical_fields
from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.cmp180_single_backend import Cmp180SingleMeasurementBackend
from cmp180_evm.workflow.frequency_sweep import FrequencySweepPlan, run_frequency_sweep
from cmp180_evm.workflow.power_sweep import PowerSweepPlan, run_power_sweep
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan, run_single_measurement

FREQUENCY_START_HZ = 5_925_000_000.0
FREQUENCY_STOP_HZ = 7_125_000_000.0
FREQUENCY_STEP_HZ = 25_000_000.0
POWER_START_DBM = -55.0
POWER_STOP_DBM = -30.0
POWER_STEP_DB = 1.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", default="TCPIP::192.168.200.50::5025::SOCKET")
    parser.add_argument("--command-map", type=Path, default=Path("configs/scpi_command_map.yaml"))
    parser.add_argument("--output-root", type=Path, default=Path("output"))
    parser.add_argument("--confirm-direct-cable", action="store_true")
    parser.add_argument("--confirm-no-attenuator", action="store_true")
    parser.add_argument("--confirm-operator-present", action="store_true")
    parser.add_argument("--confirm-full-campaign", action="store_true")
    return parser.parse_args()


def _single_plan(*, frequency_hz: float, power_dbm: float) -> SingleMeasurementPlan:
    return SingleMeasurementPlan(
        generator_port="RF1.1",
        analyzer_port="RF1.5",
        center_frequency_hz=frequency_hz,
        bandwidth_hz=320_000_000.0,
        generator_power_dbm=power_dbm,
        expected_nominal_power_dbm=-20.0,
        external_attenuation_db=0.0,
        operator_confirmed=True,
        maximum_generator_power_dbm=-30.0,
    )


def main() -> int:
    # 長批次必須立即顯示每點進度，避免 pipe buffering 讓操作員誤判卡住。
    sys.stdout.reconfigure(line_buffering=True)
    args = parse_args()
    confirmed = (
        args.confirm_direct_cable
        and args.confirm_no_attenuator
        and args.confirm_operator_present
        and args.confirm_full_campaign
    )
    if not confirmed:
        print("Refusing live campaign without all four confirmations.", file=sys.stderr)
        return 2

    registry = load_scpi_command_map(args.command_map)
    instrument: RsInstrument | None = None
    try:
        instrument = RsInstrument(
            args.resource, id_query=False, reset=False, options="SelectVisa='socketio'"
        )
        instrument.visa_timeout = 15_000
        print(f"IDN: {instrument.query_str(registry.require('common.identify')).strip()}")
        backend = Cmp180SingleMeasurementBackend(instrument, registry, timeout_s=30.0)

        print("STAGE 1/3 golden point: 6105 MHz, 320 MHz, -40 dBm")
        golden_plan = _single_plan(frequency_hz=6_105_000_000.0, power_dbm=-40.0)
        golden = run_single_measurement(backend, golden_plan)
        invalid = invalid_critical_fields(golden.values)
        if invalid or golden.cleanup_errors or golden.instrument_errors:
            raise RuntimeError(
                "Golden point failed: "
                f"invalid={invalid}, instrument={golden.instrument_errors}, "
                f"cleanup={golden.cleanup_errors}"
            )
        golden_artifacts = save_single_result(
            golden.values,
            args.output_root,
            test_name="real-full-campaign-golden-6105mhz",
            simulated=False,
            metadata={
                "campaign": "full-320mhz",
                "frequency_hz": golden_plan.center_frequency_hz,
                "bandwidth_hz": golden_plan.bandwidth_hz,
                "generator_power_dbm": golden_plan.generator_power_dbm,
                "expected_nominal_power_dbm": golden_plan.expected_nominal_power_dbm,
                "measurement_states": backend.last_measurement_states,
            },
        )
        print(
            "GOLDEN PASS "
            f"EVM={golden.values['evm_all_carriers_db']} dB "
            f"Power={golden.values['burst_power_dbm']} dBm "
            f"Artifacts={json.dumps(golden_artifacts)}"
        )

        print("STAGE 2/3 frequency: 5925..7125 MHz, 25 MHz step, 49 points")
        frequency_plan = FrequencySweepPlan(
            single=_single_plan(frequency_hz=FREQUENCY_START_HZ, power_dbm=-40.0),
            start_frequency_hz=FREQUENCY_START_HZ,
            stop_frequency_hz=FREQUENCY_STOP_HZ,
            step_frequency_hz=FREQUENCY_STEP_HZ,
            dwell_time_s=0.1,
            maximum_points=49,
            minimum_frequency_hz=FREQUENCY_START_HZ,
            maximum_frequency_hz=FREQUENCY_STOP_HZ,
            maximum_span_hz=FREQUENCY_STOP_HZ - FREQUENCY_START_HZ,
        )

        def frequency_progress(index: int, result) -> None:
            frequency_hz = frequency_plan.frequencies()[index - 1]
            print(
                f"FREQ {index}/49 {frequency_hz / 1e6:.0f} MHz "
                f"EVM={result.values['evm_all_carriers_db']} dB"
            )

        frequency = run_frequency_sweep(
            backend, frequency_plan, on_point_complete=frequency_progress
        )
        frequency_points = [
            {"frequency_hz": frequency_hz, **point.values}
            for frequency_hz, point in zip(frequency.requested_frequencies_hz, frequency.points)
        ]
        frequency_artifacts = save_frequency_sweep_result(
            frequency_points,
            args.output_root,
            requested_frequencies_hz=frequency.requested_frequencies_hz,
            completed=frequency.completed,
            failed_frequency_hz=frequency.failed_frequency_hz,
            error=frequency.error,
            metadata={"campaign": "full-320mhz", "bandwidth_hz": 320_000_000.0},
        )
        if not frequency.completed:
            raise RuntimeError(f"Frequency sweep stopped: {frequency.error}")
        print(f"FREQUENCY PASS 49/49 Artifacts={json.dumps(frequency_artifacts)}")

        print("STAGE 3/3 power: -55..-30 dBm, 1 dB step, 26 points")
        power_plan = PowerSweepPlan(
            single=_single_plan(frequency_hz=6_105_000_000.0, power_dbm=POWER_START_DBM),
            start_power_dbm=POWER_START_DBM,
            stop_power_dbm=POWER_STOP_DBM,
            step_power_dbm=POWER_STEP_DB,
            dwell_time_s=0.1,
            maximum_points=26,
            minimum_power_dbm=POWER_START_DBM,
            maximum_power_dbm=POWER_STOP_DBM,
        )

        def power_progress(index: int, result) -> None:
            power_dbm = power_plan.powers()[index - 1]
            print(
                f"POWER {index}/26 {power_dbm:.0f} dBm "
                f"EVM={result.values['evm_all_carriers_db']} dB"
            )

        power = run_power_sweep(backend, power_plan, on_point_complete=power_progress)
        power_points = [
            {"generator_power_dbm": power_dbm, **point.values}
            for power_dbm, point in zip(power.requested_powers_dbm, power.points)
        ]
        power_artifacts = save_power_sweep_result(
            power_points,
            args.output_root,
            requested_powers_dbm=power.requested_powers_dbm,
            completed=power.completed,
            failed_power_dbm=power.failed_power_dbm,
            error=power.error,
            metadata={"campaign": "full-320mhz", "frequency_hz": 6_105_000_000.0},
        )
        if not power.completed:
            raise RuntimeError(f"Power sweep stopped: {power.error}")
        print(f"POWER PASS 26/26 Artifacts={json.dumps(power_artifacts)}")
        print("CAMPAIGN PASS: golden + 49 frequency points + 26 power points")
        return 0
    except Exception as exc:
        print(f"CAMPAIGN FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3
    finally:
        if instrument is not None:
            # 外層再執行最後 STOP/RF Off，避免任一階段間的非預期例外留下 RF。
            try:
                instrument.write_str(registry.require("wlan_tx.stop"))
                instrument.query_str(registry.require("common.operation_complete"))
            except Exception:
                try:
                    instrument.write_str(registry.require("wlan_tx.abort"))
                except Exception:
                    pass
            try:
                instrument.write_str(registry.require("generator.rf_off"))
                instrument.query_str(registry.require("common.operation_complete"))
            finally:
                instrument.close()


if __name__ == "__main__":
    raise SystemExit(main())
