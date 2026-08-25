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
        return "1"

    def close(self):
        self.closed = True


class CustomBackend:
    def __init__(self, _instrument, _registry, timeout_s):
        self.plan = None

    def configure(self, plan):
        self.plan = plan

    def rf_on(self):
        pass

    def initiate_single(self):
        pass

    def wait_ready(self):
        pass

    def fetch_result(self):
        return {
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
    assert instrument.closed is True
    assert REGISTRY.require("generator.rf_off") in instrument.writes


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
