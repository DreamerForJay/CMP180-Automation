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
from cmp180_evm.workflow.cmp180_single_backend import (
    VERIFIED_TRIGGER_SOURCE,
    VERIFIED_TRIGGER_THRESHOLD_DB,
    VERIFIED_WLAN_BAND_READBACK,
    VERIFIED_WLAN_STANDARD_READBACK,
    Cmp180SingleMeasurementBackend,
)
from cmp180_evm.workflow.frequency_sweep import FrequencySweepPlan, run_frequency_sweep
from cmp180_evm.workflow.power_sweep import PowerSweepPlan, run_power_sweep
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan, run_single_measurement

VERIFIED_ARB_WAVEFORM = (
    "KV352_lib8_WLAN_11be_EHT_MU_BW320-1_4xLTF_GI32_MCS11_LEN4096_LDPC.wv"
)


def _measurement_diagnostics(
    backend: Cmp180SingleMeasurementBackend,
    plan: SingleMeasurementPlan,
) -> dict[str, object]:
    """Return the verified configuration and observed state trace for artifacts."""
    # 這些值都已在 RF On 前完成 readback；保存快照不會額外控制儀器。
    return {
        # Adapter 測試替身可能不提供狀態追蹤；正式 backend 仍會保存完整轉換序列。
        "measurement_state_trace": list(
            getattr(backend, "last_measurement_states", [])
        ),
        "wlan_standard": VERIFIED_WLAN_STANDARD_READBACK,
        "wlan_band": VERIFIED_WLAN_BAND_READBACK,
        "trigger_source": VERIFIED_TRIGGER_SOURCE,
        "trigger_threshold_db": VERIFIED_TRIGGER_THRESHOLD_DB,
        "expected_nominal_power_dbm": plan.expected_nominal_power_dbm,
        "external_attenuation_db": plan.external_attenuation_db,
        "ranging_strategy": "expected_nominal_power_fixed",
    }


def _web_point(
    index: int, axis_value: float, values: dict[str, object], axis: str
) -> dict[str, object]:
    def optional_float(field: str) -> float | None:
        try:
            return float(values[field])
        except (KeyError, TypeError, ValueError):
            # INV 必須保留在 raw artifact；Web 正規化用 null 表示該數值不可用，避免遮蔽失敗原因。
            return None

    normalized = {
        "evm_all_db": optional_float("evm_all_carriers_db"),
        "evm_data_db": optional_float("evm_data_carriers_db"),
        "evm_pilot_db": optional_float("evm_pilot_carriers_db"),
        "burst_power_dbm": optional_float("burst_power_dbm"),
        "frequency_error_hz": optional_float("frequency_error_hz"),
        "clock_error_ppm": optional_float("clock_error_ppm"),
    }
    critical_valid = all(
        normalized[field] is not None
        for field in ("evm_all_db", "burst_power_dbm", "frequency_error_hz")
    )
    return {
        "point_index": index,
        "frequency_hz": axis_value if axis == "frequency" else 6_105_000_000.0,
        "generator_power_dbm": axis_value if axis == "power" else -40.0,
        "bandwidth_hz": 320_000_000.0,
        **normalized,
        "valid": critical_valid,
        "limit_status": "MEASURED" if critical_valid else "INVALID",
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
        if axis == "frequency":
            plan = FrequencySweepPlan(
                single, 6_085_000_000, 6_125_000_000, 20_000_000, maximum_points=3
            )
            def callback(count, point):
                # callback 發生在單點 cleanup 完成後；即時圖只讀已完成點，不延長 RF On。
                value = 6_085_000_000 + (count - 1) * 20_000_000
                job.point_completed(count, _web_point(count - 1, value, point.values, axis))
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
                    **_measurement_diagnostics(backend, single),
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
            def callback(count, point):
                # 功率點同樣只在 RF Off 邊界發布，INVALID 會保留而不偽造為有效數值。
                value = -55 + (count - 1) * 5
                job.point_completed(count, _web_point(count - 1, value, point.values, axis))
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
                    **_measurement_diagnostics(backend, single),
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
            def callback(count, point):
                # 預覽點位已在 request 重新驗證；只發布完成後的正規化資料供 Web 即時顯示。
                value = preview.points[count - 1]
                web_point = _web_point(count - 1, value, point.values, "frequency")
                web_point["generator_power_dbm"] = preview.generator_power_dbm
                job.point_completed(count, web_point)
            result = run_frequency_sweep(
                backend,
                plan,
                should_cancel=job.is_cancel_requested,
                on_point_complete=callback,
            )
            metadata.update(_measurement_diagnostics(backend, single))
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
            def callback(count, point):
                value = preview.points[count - 1]
                web_point = _web_point(count - 1, value, point.values, "power")
                web_point["frequency_hz"] = preview.center_frequency_hz
                job.point_completed(count, web_point)
            result = run_power_sweep(
                backend,
                plan,
                should_cancel=job.is_cancel_requested,
                on_point_complete=callback,
            )
            metadata.update(_measurement_diagnostics(backend, single))
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
                **_measurement_diagnostics(backend, plan),
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
