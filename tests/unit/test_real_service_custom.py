import json
import sys
from pathlib import Path
from types import SimpleNamespace

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.web import real_service
from cmp180_evm.web.jobs import SweepJob

REGISTRY = load_scpi_command_map(Path("configs/scpi_command_map.yaml"))


class CleanupInstrument:
    def __init__(self):
        self.visa_timeout = 0
        self.writes = []
        self.closed = False

    def write_str(self, command):
        self.writes.append(command)

    def query_str(self, command):
        if command == REGISTRY.require("generator_query.state"):
            return "OFF"
        if command == REGISTRY.require("wlan_tx_query.measurement_state"):
            return "RDY"
        if command == REGISTRY.require("generator_query.rf_path"):
            return '"RF1.1"'
        return "1"

    def close(self):
        self.closed = True


class CustomBackend:
    configured_plans = []

    def __init__(self, _instrument, _registry, timeout_s):
        self.plan = None

    def configure(self, plan):
        self.plan = plan
        self.__class__.configured_plans.append(plan)

    def rf_on(self):
        pass

    def initiate_single(self):
        pass

    def wait_ready(self):
        pass

    def fetch_result(self):
        return {
            "reliability": "0",
            "evm_all_carriers_db": -36,
            "evm_data_carriers_db": -35,
            "evm_pilot_carriers_db": -37,
            "burst_power_dbm": -45,
            "frequency_error_hz": 5,
            "clock_error_ppm": 0.1,
        }

    def stop_measurement(self):
        pass

    def rf_off(self):
        pass

    def drain_error_queue(self):
        return []


class InvalidSecondPointBackend(CustomBackend):
    calls = 0

    def fetch_result(self):
        self.__class__.calls += 1
        values = super().fetch_result()
        if self.__class__.calls == 2:
            values["evm_all_carriers_db"] = "INV"
        return values


def test_custom_real_service_revalidates_runs_saves_and_cleans_up(monkeypatch, tmp_path):
    instrument = CleanupInstrument()
    CustomBackend.configured_plans = []
    monkeypatch.setitem(
        sys.modules,
        "RsInstrument",
        SimpleNamespace(RsInstrument=lambda *args, **kwargs: instrument),
    )
    monkeypatch.setattr(real_service, "Cmp180SingleMeasurementBackend", CustomBackend)
    request = {
        "axis": "frequency",
        "start_hz": 6_085_000_000,
        "stop_hz": 6_125_000_000,
        "step_hz": 20_000_000,
        "bandwidth_hz": 320_000_000,
        "generator_power_dbm": -45,
        "dwell_ms": 100,
    }
    job = SweepJob("job", "hardware-custom-frequency", 3)
    result = real_service.run_custom_real_sweep(job, request=request, output_root=tmp_path)
    assert result["simulated"] is False
    assert len(result["points"]) == 3
    assert result["measurement_failed"] is False
    assert job.completed_points == 3
    assert [plan.center_frequency_hz for plan in CustomBackend.configured_plans] == [
        6_085_000_000,
        6_105_000_000,
        6_125_000_000,
    ]
    assert {plan.generator_power_dbm for plan in CustomBackend.configured_plans} == {-45}
    # expected nominal power 固定為已驗證的 -20 dBm；跟隨 generator 功率會讓實機回傳 INV
    # （2026-08-28 實機驗收證實）。
    assert {plan.expected_nominal_power_dbm for plan in CustomBackend.configured_plans} == {-20}
    assert instrument.closed is True
    assert REGISTRY.require("generator.rf_off") in instrument.writes


def test_custom_real_single_uses_reviewed_web_values(monkeypatch, tmp_path):
    instrument = CleanupInstrument()
    CustomBackend.configured_plans = []
    monkeypatch.setitem(
        sys.modules,
        "RsInstrument",
        SimpleNamespace(RsInstrument=lambda *args, **kwargs: instrument),
    )
    monkeypatch.setattr(real_service, "Cmp180SingleMeasurementBackend", CustomBackend)
    result = real_service.run_custom_real_single(
        request={
            "center_frequency_hz": 6_105_000_000,
            "bandwidth_hz": 320_000_000,
            "generator_power_dbm": -45,
        },
        output_root=tmp_path,
    )
    plan = CustomBackend.configured_plans[-1]
    assert plan.center_frequency_hz == 6_105_000_000
    assert plan.bandwidth_hz == 320_000_000
    assert plan.generator_power_dbm == -45
    assert plan.expected_nominal_power_dbm == -20
    assert result["points"][0]["frequency_hz"] == 6_105_000_000
    assert Path(result["artifacts"]["matplotlib_evm_all_carriers_db"]).is_file()
    assert instrument.closed is True


def test_custom_real_single_allows_catalog_edge_and_flags_non_standard_channel(
    monkeypatch, tmp_path
):
    instrument = CleanupInstrument()
    CustomBackend.configured_plans = []
    monkeypatch.setitem(
        sys.modules,
        "RsInstrument",
        SimpleNamespace(RsInstrument=lambda *args, **kwargs: instrument),
    )
    monkeypatch.setattr(real_service, "Cmp180SingleMeasurementBackend", CustomBackend)
    result = real_service.run_custom_real_single(
        request={
            "center_frequency_hz": 400_000_000,
            "bandwidth_hz": 320_000_000,
            "generator_power_dbm": -45,
        },
        output_root=tmp_path,
    )
    metadata = json.loads(Path(result["artifacts"]["metadata"]).read_text(encoding="utf-8"))
    assert CustomBackend.configured_plans[-1].center_frequency_hz == 400_000_000
    # 400 MHz 不在標準 WLAN channel plan 內，但仍可實際量測；artifact 保留標記。
    assert metadata["standard_wlan_channel"] is False
    assert metadata["compliance_claim"] is False


def test_custom_real_service_runs_full_user_frequency_plan(monkeypatch, tmp_path):
    instrument = CleanupInstrument()
    CustomBackend.configured_plans = []
    monkeypatch.setitem(
        sys.modules,
        "RsInstrument",
        SimpleNamespace(RsInstrument=lambda *args, **kwargs: instrument),
    )
    monkeypatch.setattr(real_service, "Cmp180SingleMeasurementBackend", CustomBackend)
    request = {
        "axis": "frequency",
        "start_hz": 5_925_000_000,
        "stop_hz": 7_125_000_000,
        "step_hz": 25_000_000,
        "bandwidth_hz": 320_000_000,
        "generator_power_dbm": -45,
        "dwell_ms": 100,
    }
    job = SweepJob("job-full", "hardware-custom-frequency", 49)
    result = real_service.run_custom_real_sweep(job, request=request, output_root=tmp_path)
    assert result["measurement_failed"] is False
    assert len(result["points"]) == 49
    assert job.total_points == 49
    assert job.completed_points == 49
    assert CustomBackend.configured_plans[0].center_frequency_hz == 5_925_000_000
    assert CustomBackend.configured_plans[-1].center_frequency_hz == 7_125_000_000


def test_custom_real_service_preserves_invalid_partial_result(monkeypatch, tmp_path):
    instrument = CleanupInstrument()
    InvalidSecondPointBackend.calls = 0
    monkeypatch.setitem(
        sys.modules,
        "RsInstrument",
        SimpleNamespace(RsInstrument=lambda *args, **kwargs: instrument),
    )
    monkeypatch.setattr(real_service, "Cmp180SingleMeasurementBackend", InvalidSecondPointBackend)
    request = {
        "axis": "frequency",
        "start_hz": 6_085_000_000,
        "stop_hz": 6_105_000_000,
        "step_hz": 20_000_000,
        "bandwidth_hz": 320_000_000,
        "generator_power_dbm": -45,
        "dwell_ms": 100,
    }
    job = SweepJob("job-invalid", "hardware-custom-frequency", 2)
    result = real_service.run_custom_real_sweep(job, request=request, output_root=tmp_path)
    assert result["measurement_failed"] is True
    assert "evm_all_carriers_db" in result["error"]
    assert len(result["points"]) == 2
    assert result["points"][1]["valid"] is False
    assert result["points"][1]["evm_all_db"] is None
    assert result["artifacts"]["csv"]
    assert instrument.closed is True


def test_loopback_real_service_records_final_cleanup_snapshot(monkeypatch, tmp_path):
    instrument = CleanupInstrument()
    CustomBackend.configured_plans = []
    monkeypatch.setitem(
        sys.modules,
        "RsInstrument",
        SimpleNamespace(RsInstrument=lambda *args, **kwargs: instrument),
    )
    monkeypatch.setattr(real_service, "Cmp180SingleMeasurementBackend", CustomBackend)
    request = {
        "center_frequency_hz": 6_105_000_000,
        "bandwidth_hz": 320_000_000,
        "generator_power_dbm": -45,
        "repeat_count": 2,
        "minimum_repeats": 2,
        "max_evm_std_db": 1.0,
        "max_power_std_db": 1.0,
        "max_freq_error_std_hz": 20.0,
        "max_invalid_ratio": 0.0,
        "expected_power_dbm": -45.0,
        "allowed_power_error_db": 1.0,
    }
    job = SweepJob("job-loopback", "hardware-loopback", 2)

    result = real_service.run_real_loopback_validation(
        job, request=request, output_root=tmp_path
    )

    assert result["measurement_family"] == "LOOPBACK_VALIDATION"
    assert job.completed_points == 2
    metadata = json.loads(Path(result["artifacts"]["metadata"]).read_text(encoding="utf-8"))
    # Loopback 正常完成後仍記錄 final safe state，方便 HIL 稽核 RF Off / RDY。
    assert metadata["final_cleanup"]["final_rf_state"] == "OFF"
    assert metadata["final_cleanup"]["final_measurement_state"] == "RDY"
    assert instrument.closed is True
