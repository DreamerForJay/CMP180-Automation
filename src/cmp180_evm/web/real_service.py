"""Guarded real-hardware service used by the local Web GUI."""

from __future__ import annotations

from pathlib import Path

from cmp180_evm.limits import DRAFT_LOOPBACK_LIMIT_PROFILE, LimitProfile, evaluate_limits
from cmp180_evm.results.artifacts import (
    save_frequency_sweep_result,
    save_power_sweep_result,
    save_single_result,
)
from cmp180_evm.calibration import CalibrationProfile
from cmp180_evm.workflow.calibration_application import (
    resolve_calibration,
    uncalibrated_metadata,
)
from cmp180_evm.results.validity import (
    IQ_ESTIMATE_FIELDS,
    evaluate_estimator_confidence,
    evaluate_point_validity,
)
from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.utils.exceptions import SafetyGuardError
from cmp180_evm.web.custom_plans import build_custom_sweep_preview
from cmp180_evm.web.jobs import SweepJob
from cmp180_evm.workflow.cmp180_single_backend import (
    VERIFIED_TRIGGER_SOURCE,
    VERIFIED_TRIGGER_THRESHOLD_DB,
    VERIFIED_WLAN_STANDARD_READBACK,
    Cmp180SingleMeasurementBackend,
    waveform_for_bandwidth,
)
from cmp180_evm.workflow.frequency_sweep import FrequencySweepPlan, run_frequency_sweep
from cmp180_evm.workflow.power_sweep import PowerSweepPlan, run_power_sweep
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan, run_single_measurement
from cmp180_evm.workflow.wlan_bands import executable_band_for

VERIFIED_ARB_WAVEFORM = waveform_for_bandwidth(320_000_000)
# 2026-08-20 HIL 已驗證的 analyzer 接收參考面；讓它跟隨 generator 功率會導致 INV。
VERIFIED_EXPECTED_NOMINAL_POWER_DBM = -20.0


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
        "wlan_band": executable_band_for(plan.center_frequency_hz).band_readback,
        "trigger_source": VERIFIED_TRIGGER_SOURCE,
        "trigger_threshold_db": VERIFIED_TRIGGER_THRESHOLD_DB,
        "expected_nominal_power_dbm": plan.expected_nominal_power_dbm,
        "external_attenuation_db": plan.external_attenuation_db,
        "ranging_strategy": "expected_nominal_power_fixed",
    }


def _web_point(
    index: int,
    axis_value: float,
    values: dict[str, object],
    axis: str,
    *,
    bandwidth_hz: float = 320_000_000.0,
    fixed_frequency_hz: float = 6_105_000_000.0,
    fixed_power_dbm: float = -40.0,
    profile: LimitProfile = DRAFT_LOOPBACK_LIMIT_PROFILE,
    statistic_count: int | None = None,
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
    # Layer 1：量測有效性，集中定義於 results.validity，reason 完整保留而非只留 boolean。
    validity = evaluate_point_validity(values)
    generator_power_dbm = axis_value if axis == "power" else fixed_power_dbm

    # Layer 2：規格判定與模擬路徑共用同一個 profile 與 evaluate_limits，不另外複製邏輯。
    # margin = limit - measured，正值代表優於限值；此符號約定全專案一致。
    spec_limit_db = profile.maximum_evm_db
    if validity.valid:
        limit_result = evaluate_limits(
            profile,
            evm_db=float(normalized["evm_all_db"]),
            frequency_error_hz=float(normalized["frequency_error_hz"]),
            measured_power_dbm=float(normalized["burst_power_dbm"]),
            expected_power_dbm=generator_power_dbm,
        )
        limit_status = limit_result.overall_status
        margin_db = limit_result.evm_margin_db
    else:
        limit_status = "INVALID"
        margin_db = None

    # Layer 3：估計器信心。symbol 數不足時 IQ 類欄位不得當成可靠 RF 結果顯示。
    confidence = evaluate_estimator_confidence(values, statistic_count=statistic_count)
    iq_fields: dict[str, object] = {field: None for field in IQ_ESTIMATE_FIELDS}
    if confidence.estimate_valid:
        for field in IQ_ESTIMATE_FIELDS:
            iq_fields[field] = optional_float(field)

    return {
        "point_index": index,
        "frequency_hz": axis_value if axis == "frequency" else fixed_frequency_hz,
        "generator_power_dbm": generator_power_dbm,
        "bandwidth_hz": bandwidth_hz,
        **normalized,
        **validity.public(),
        "measured_evm_db": normalized["evm_all_db"],
        "spec_limit_db": spec_limit_db,
        "margin_db": margin_db,
        "limit_status": limit_status,
        # 儀器自己的判定，與 app 的 spec 判定分開呈現，避免雙重判定互相覆蓋。
        "instrument_out_of_tolerance_percent": optional_float("out_of_tolerance_percent"),
        **iq_fields,
        "estimator": confidence.public(),
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
        # 實機統計量測可能超過 VISA 的單次 I/O timeout；此處只延長狀態輪詢，
        # 例外與取消仍會在 finally 執行 STOP／ABORT 與 RF Off。
        backend = Cmp180SingleMeasurementBackend(instrument, registry, timeout_s=60.0)
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
    calibration_profile: CalibrationProfile | None = None,
) -> dict[str, object]:
    """Execute one revalidated custom plan inside the hard workflow safety envelope."""
    from RsInstrument import RsInstrument

    preview = build_custom_sweep_preview(request)
    if not preview.execution_allowed:
        # API 可能被直接呼叫；即使前端預覽已擋下，後端仍須在連線儀器前重驗核准 profile。
        raise SafetyGuardError(preview.rejection_reason or "Custom RF plan is not approved")
    registry = load_scpi_command_map(Path("configs/scpi_command_map.yaml"))
    instrument = RsInstrument(
        "TCPIP::192.168.200.50::5025::SOCKET",
        id_query=False,
        reset=False,
        options="SelectVisa='socketio'",
    )
    instrument.visa_timeout = 15_000
    try:
        # 掃描每點保留 60 秒 acquisition 窗口，不放寬任何 RF 安全限制。
        backend = Cmp180SingleMeasurementBackend(instrument, registry, timeout_s=60.0)
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
            # expected nominal power 必須沿用已驗證的 -20 dBm，不可跟隨 generator 功率。
            # 2026-08-28 實機驗收：-55 dBm 搭配 expected -55 dBm，28 個欄位全部回傳 INV；
            # 2026-08-20 HIL 則以同樣 -55 dBm 搭配 expected -20 dBm 取得有效 EVM。
            expected_nominal_power_dbm=VERIFIED_EXPECTED_NOMINAL_POWER_DBM,
            external_attenuation_db=0.0,
            operator_confirmed=True,
            maximum_generator_power_dbm=-30.0,
        )

        # 校正只在提供已核准且涵蓋本次頻率的 profile 時生效；否則維持未修正行為。
        calibration_frequencies = (
            preview.points
            if preview.axis == "frequency"
            else (float(preview.center_frequency_hz),)
        )
        calibration = resolve_calibration(
            calibration_profile,
            route=f"{single.generator_port}-{single.analyzer_port}",
            frequencies_hz=tuple(float(value) for value in calibration_frequencies),
        )
        metadata = {
            "source": "web_custom_hardware_sweep",
            "arb_waveform_file": waveform_for_bandwidth(preview.bandwidth_hz),
            "custom_plan_fingerprint": preview.plan_fingerprint,
            "custom_plan": preview.public(),
            "operator_authorization": "confirmed_at_request",
            **(
                calibration.metadata()
                if calibration
                else uncalibrated_metadata(
                    "No approved calibration profile supplied; analyzer expected power "
                    "uses the HIL-verified fixed -20 dBm ranging value"
                )
            ),
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
                web_point = _web_point(
                    count - 1,
                    value,
                    point.values,
                    "frequency",
                    bandwidth_hz=preview.bandwidth_hz,
                    fixed_power_dbm=float(preview.generator_power_dbm),
                )
                job.point_completed(count, web_point)
            result = run_frequency_sweep(
                backend,
                plan,
                should_cancel=job.is_cancel_requested,
                on_point_complete=callback,
                external_attenuation_for=(
                    calibration.loss_for if calibration else None
                ),
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
                    **_web_point(
                        index,
                        value,
                        point.values,
                        "frequency",
                        bandwidth_hz=preview.bandwidth_hz,
                        fixed_power_dbm=float(preview.generator_power_dbm),
                    ),
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
                web_point = _web_point(
                    count - 1,
                    value,
                    point.values,
                    "power",
                    bandwidth_hz=preview.bandwidth_hz,
                    fixed_frequency_hz=float(preview.center_frequency_hz),
                )
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
                    **_web_point(
                        index,
                        value,
                        point.values,
                        "power",
                        bandwidth_hz=preview.bandwidth_hz,
                        fixed_frequency_hz=float(preview.center_frequency_hz),
                    ),
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
        # 自訂掃描僅延長等待時間；cleanup 與功率上限維持不變。
        backend = Cmp180SingleMeasurementBackend(instrument, registry, timeout_s=60.0)
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
        point = _web_point(
            0,
            plan.center_frequency_hz,
            values,
            "frequency",
            bandwidth_hz=plan.bandwidth_hz,
            fixed_power_dbm=plan.generator_power_dbm,
        )
        return {
            "simulated": False,
            # SingleShot 與 sweep 共用相同 validity／limit／estimator 合約，避免結果頁兩套語意。
            "points": [point],
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
