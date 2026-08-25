"""Guarded real-hardware service used by the local Web GUI."""

from __future__ import annotations

from pathlib import Path

from cmp180_evm.results.artifacts import (
    save_frequency_sweep_result,
    save_power_sweep_result,
    save_single_result,
)
from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.web.custom_plans import build_custom_sweep_preview
from cmp180_evm.web.jobs import SweepJob
from cmp180_evm.workflow.cmp180_single_backend import Cmp180SingleMeasurementBackend
from cmp180_evm.workflow.frequency_sweep import FrequencySweepPlan, run_frequency_sweep
from cmp180_evm.workflow.power_sweep import PowerSweepPlan, run_power_sweep
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan, run_single_measurement

VERIFIED_ARB_WAVEFORM = (
    "KV352_lib8_WLAN_11be_EHT_MU_BW320-1_4xLTF_GI32_MCS11_LEN4096_LDPC.wv"
)


def _web_point(
    index: int, axis_value: float, values: dict[str, object], axis: str
) -> dict[str, object]:
    return {
        "point_index": index,
        "frequency_hz": axis_value if axis == "frequency" else 6_105_000_000.0,
        "generator_power_dbm": axis_value if axis == "power" else -40.0,
        "bandwidth_hz": 320_000_000.0,
        "evm_all_db": float(values["evm_all_carriers_db"]),
        "evm_data_db": float(values["evm_data_carriers_db"]),
        "evm_pilot_db": float(values["evm_pilot_carriers_db"]),
        "burst_power_dbm": float(values["burst_power_dbm"]),
        "frequency_error_hz": float(values["frequency_error_hz"]),
        "clock_error_ppm": float(values["clock_error_ppm"]),
        "valid": True,
        "limit_status": "MEASURED",
    }


def run_verified_real_sweep(job: SweepJob, *, axis: str, output_root: Path) -> dict[str, object]:
    """Run only the two CLI-HIL-approved fixed sweep profiles."""
    from RsInstrument import RsInstrument

    registry = load_scpi_command_map(Path("configs/scpi_command_map.yaml"))
    instrument = RsInstrument(
        "TCPIP::192.168.200.50::5025::SOCKET",
        id_query=False,
        reset=False,
        options="SelectVisa='socketio'",
    )
    instrument.visa_timeout = 15_000
    try:
        backend = Cmp180SingleMeasurementBackend(instrument, registry, timeout_s=15.0)
        single = SingleMeasurementPlan(
            "RF1.1", "RF1.5", 6_105_000_000, 320_000_000, -40, -20, 0, True, -40
        )
        def callback(count, _point):
            job.point_completed(count)

        if axis == "frequency":
            plan = FrequencySweepPlan(
                single, 6_085_000_000, 6_125_000_000, 20_000_000, maximum_points=3
            )
            result = run_frequency_sweep(
                backend,
                plan,
                should_cancel=job.is_cancel_requested,
                on_point_complete=callback,
            )
            raw_points = [
                {"frequency_hz": value, **point.values}
                for value, point in zip(result.requested_frequencies_hz, result.points)
            ]
            artifacts = save_frequency_sweep_result(
                raw_points,
                output_root,
                requested_frequencies_hz=result.requested_frequencies_hz,
                completed=result.completed,
                failed_frequency_hz=result.failed_frequency_hz,
                error=result.error,
                metadata={
                    "source": "web_verified_frequency_sweep",
                    "arb_waveform_file": VERIFIED_ARB_WAVEFORM,
                },
            )
            web_points = [
                _web_point(index, value, point.values, axis)
                for index, (value, point) in enumerate(
                    zip(result.requested_frequencies_hz, result.points)
                )
            ]
        elif axis == "power":
            plan = PowerSweepPlan(single, -55, -40, 5, maximum_points=4, minimum_power_dbm=-55)
            result = run_power_sweep(
                backend,
                plan,
                should_cancel=job.is_cancel_requested,
                on_point_complete=callback,
            )
            raw_points = [
                {"generator_power_dbm": value, **point.values}
                for value, point in zip(result.requested_powers_dbm, result.points)
            ]
            artifacts = save_power_sweep_result(
                raw_points,
                output_root,
                requested_powers_dbm=result.requested_powers_dbm,
                completed=result.completed,
                failed_power_dbm=result.failed_power_dbm,
                error=result.error,
                metadata={
                    "source": "web_verified_power_sweep",
                    "arb_waveform_file": VERIFIED_ARB_WAVEFORM,
                },
            )
            web_points = [
                _web_point(index, value, point.values, axis)
                for index, (value, point) in enumerate(
                    zip(result.requested_powers_dbm, result.points)
                )
            ]
        else:
            raise ValueError("Unsupported hardware sweep axis")
        if not result.completed and not job.is_cancel_requested():
            raise RuntimeError(result.error or "Hardware sweep failed")
        return {
            "simulated": False,
            "sweep_axis": axis,
            "points": web_points,
            "artifacts": artifacts,
        }
    finally:
        # Web job 最外層永遠再送 STOP／RF Off，避免 worker 或取消留下 RF。
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
            rf_state = instrument.query_str(registry.require("generator_query.state")).strip()
            measurement_state = instrument.query_str(
                registry.require("wlan_tx_query.measurement_state")
            ).strip()
            if rf_state != "OFF" or measurement_state not in {"OFF", "RDY"}:
                raise RuntimeError(
                    f"Unsafe final state RF={rf_state}, measurement={measurement_state}"
                )
        finally:
            instrument.close()


def run_custom_real_sweep(
    job: SweepJob,
    *,
    request: dict[str, object],
    output_root: Path,
) -> dict[str, object]:
    """Execute one revalidated custom plan inside the hard workflow safety envelope."""
    from RsInstrument import RsInstrument

    preview = build_custom_sweep_preview(request)
    registry = load_scpi_command_map(Path("configs/scpi_command_map.yaml"))
    instrument = RsInstrument(
        "TCPIP::192.168.200.50::5025::SOCKET",
        id_query=False,
        reset=False,
        options="SelectVisa='socketio'",
    )
    instrument.visa_timeout = 15_000
    try:
        backend = Cmp180SingleMeasurementBackend(instrument, registry, timeout_s=15.0)
        single = SingleMeasurementPlan(
            generator_port="RF1.1",
            analyzer_port="RF1.5",
            center_frequency_hz=(
                preview.points[0]
                if preview.axis == "frequency"
                else float(preview.center_frequency_hz)
            ),
            bandwidth_hz=preview.bandwidth_hz,
            generator_power_dbm=(
                float(preview.generator_power_dbm)
                if preview.axis == "frequency"
                else preview.points[0]
            ),
            # -20 dBm 是既有 CMP180 ranging 設定；Path Loss 核准前不得自行改寫。
            expected_nominal_power_dbm=-20.0,
            external_attenuation_db=0.0,
            operator_confirmed=True,
            maximum_generator_power_dbm=-40.0,
        )

        def callback(count, _point):
            job.point_completed(count)

        metadata = {
            "source": "web_custom_hardware_sweep",
            "arb_waveform_file": VERIFIED_ARB_WAVEFORM,
            "custom_plan_fingerprint": preview.plan_fingerprint,
            "custom_plan": preview.public(),
            "operator_authorization": "confirmed_at_request",
            "calibration_applied": False,
            "calibration_reason": "No approved calibration profile supplied",
        }
        if preview.axis == "frequency":
            plan = FrequencySweepPlan(
                single,
                preview.points[0],
                preview.points[-1],
                preview.points[1] - preview.points[0],
                dwell_time_s=preview.dwell_time_s,
            )
            result = run_frequency_sweep(
                backend,
                plan,
                should_cancel=job.is_cancel_requested,
                on_point_complete=callback,
            )
            raw_points = [
                {"frequency_hz": value, **point.values}
                for value, point in zip(result.requested_frequencies_hz, result.points)
            ]
            artifacts = save_frequency_sweep_result(
                raw_points,
                output_root,
                requested_frequencies_hz=result.requested_frequencies_hz,
                completed=result.completed,
                failed_frequency_hz=result.failed_frequency_hz,
                error=result.error,
                metadata=metadata,
            )
            web_points = [
                {
                    **_web_point(index, value, point.values, "frequency"),
                    "generator_power_dbm": preview.generator_power_dbm,
                }
                for index, (value, point) in enumerate(
                    zip(result.requested_frequencies_hz, result.points)
                )
            ]
        else:
            plan = PowerSweepPlan(
                single,
                preview.points[0],
                preview.points[-1],
                preview.points[1] - preview.points[0],
                dwell_time_s=preview.dwell_time_s,
            )
            result = run_power_sweep(
                backend,
                plan,
                should_cancel=job.is_cancel_requested,
                on_point_complete=callback,
            )
            raw_points = [
                {"generator_power_dbm": value, **point.values}
                for value, point in zip(result.requested_powers_dbm, result.points)
            ]
            artifacts = save_power_sweep_result(
                raw_points,
                output_root,
                requested_powers_dbm=result.requested_powers_dbm,
                completed=result.completed,
                failed_power_dbm=result.failed_power_dbm,
                error=result.error,
                metadata=metadata,
            )
            web_points = [
                {
                    **_web_point(index, value, point.values, "power"),
                    "frequency_hz": preview.center_frequency_hz,
                }
                for index, (value, point) in enumerate(
                    zip(result.requested_powers_dbm, result.points)
                )
            ]
        return {
            "simulated": False,
            "sweep_axis": preview.axis,
            "points": web_points,
            "artifacts": artifacts,
            "measurement_failed": not result.completed and not job.is_cancel_requested(),
            "error": result.error,
        }
    finally:
        # 外層 emergency cleanup 防止 backend 或 artifact 例外跳過 RF Off。
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
            rf_state = instrument.query_str(registry.require("generator_query.state")).strip()
            measurement_state = instrument.query_str(
                registry.require("wlan_tx_query.measurement_state")
            ).strip()
            if rf_state != "OFF" or measurement_state not in {"OFF", "RDY"}:
                raise RuntimeError(
                    f"Unsafe final state RF={rf_state}, measurement={measurement_state}"
                )
        finally:
            instrument.close()


def run_verified_real_single(
    *,
    resource: str = "TCPIP::192.168.200.50::5025::SOCKET",
    output_root: Path = Path("output"),
) -> dict[str, object]:
    """Run only the hardware-verified fixed 6105 MHz loopback profile."""
    from RsInstrument import RsInstrument

    registry = load_scpi_command_map(Path("configs/scpi_command_map.yaml"))
    instrument = RsInstrument(
        resource,
        id_query=False,
        reset=False,
        options="SelectVisa='socketio'",
    )
    instrument.visa_timeout = 15_000
    final_rf_state = "UNKNOWN"
    final_measurement_state = "UNKNOWN"
    try:
        backend = Cmp180SingleMeasurementBackend(instrument, registry, timeout_s=15.0)
        # Web 實機模式先鎖定已驗證 profile，不接受任意頻率或功率輸入。
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
        if result.cleanup_errors or result.instrument_errors:
            raise RuntimeError(
                f"SingleShot errors: instrument={result.instrument_errors}, "
                f"cleanup={result.cleanup_errors}"
            )
        artifacts = save_single_result(
            result.values,
            output_root,
            test_name="web-real-single-6105mhz",
            simulated=False,
            metadata={
                "source": "web_verified_single_shot",
                "frequency_hz": plan.center_frequency_hz,
                "bandwidth_hz": plan.bandwidth_hz,
                "generator_power_dbm": plan.generator_power_dbm,
                "expected_nominal_power_dbm": plan.expected_nominal_power_dbm,
                "generator_port": plan.generator_port,
                "analyzer_port": plan.analyzer_port,
                "arb_waveform_file": VERIFIED_ARB_WAVEFORM,
            },
        )
        values = result.values
        return {
            "simulated": False,
            "points": [
                {
                    "point_index": 0,
                    "frequency_hz": plan.center_frequency_hz,
                    "bandwidth_hz": plan.bandwidth_hz,
                    "generator_power_dbm": plan.generator_power_dbm,
                    "evm_all_db": float(values["evm_all_carriers_db"]),
                    "evm_data_db": float(values["evm_data_carriers_db"]),
                    "evm_pilot_db": float(values["evm_pilot_carriers_db"]),
                    "burst_power_dbm": float(values["burst_power_dbm"]),
                    "frequency_error_hz": float(values["frequency_error_hz"]),
                    "clock_error_ppm": float(values["clock_error_ppm"]),
                    "valid": True,
                    "limit_status": "MEASURED",
                }
            ],
            "artifacts": artifacts,
        }
    finally:
        # Web request 無論在哪裡失敗，都再做一次獨立 emergency cleanup 與 read-back。
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
            final_rf_state = instrument.query_str(
                registry.require("generator_query.state")
            ).strip()
            final_measurement_state = instrument.query_str(
                registry.require("wlan_tx_query.measurement_state")
            ).strip()
        finally:
            instrument.close()
        if final_rf_state != "OFF":
            raise RuntimeError(f"Emergency cleanup final RF state is {final_rf_state}")
        if final_measurement_state not in {"OFF", "RDY"}:
            raise RuntimeError(
                f"Emergency cleanup final measurement state is {final_measurement_state}"
            )
