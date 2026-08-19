"""Guarded real-hardware service used by the local Web GUI."""

from __future__ import annotations

from pathlib import Path

from cmp180_evm.results.artifacts import save_single_result
from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.cmp180_single_backend import Cmp180SingleMeasurementBackend
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan, run_single_measurement


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
