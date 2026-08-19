import pytest

from cmp180_evm.utils.exceptions import SafetyGuardError
from cmp180_evm.workflow.single_measurement import (
    MeasurementPhase,
    SingleMeasurementPlan,
    run_single_measurement,
)


class RecordingBackend:
    def __init__(self, *, fail_at: str | None = None) -> None:
        self.calls: list[str] = []
        self.fail_at = fail_at

    def _call(self, name: str) -> None:
        self.calls.append(name)
        if self.fail_at == name:
            raise RuntimeError(name)

    def configure(self, plan: SingleMeasurementPlan) -> None:
        self._call("configure")

    def rf_on(self) -> None:
        self._call("rf_on")

    def initiate_single(self) -> None:
        self._call("initiate_single")

    def wait_ready(self) -> None:
        self._call("wait_ready")

    def fetch_result(self) -> dict[str, object]:
        self._call("fetch_result")
        return {"evm_all_carriers_db": -36.14}

    def stop_measurement(self) -> None:
        self._call("stop_measurement")

    def rf_off(self) -> None:
        self._call("rf_off")

    def drain_error_queue(self) -> list[str]:
        self._call("drain_error_queue")
        return []


def safe_plan(**overrides) -> SingleMeasurementPlan:
    values = {
        "generator_port": "RF1.1",
        "analyzer_port": "RF1.5",
        "center_frequency_hz": 6_105_000_000,
        "bandwidth_hz": 320_000_000,
        "generator_power_dbm": -40.0,
        "expected_nominal_power_dbm": -20.0,
        "external_attenuation_db": 0.0,
        "operator_confirmed": True,
    }
    values.update(overrides)
    return SingleMeasurementPlan(**values)


def test_success_always_stops_measurement_and_turns_rf_off():
    backend = RecordingBackend()
    result = run_single_measurement(backend, safe_plan())
    assert backend.calls == [
        "configure", "rf_on", "initiate_single", "wait_ready", "fetch_result",
        "drain_error_queue", "stop_measurement", "rf_off",
    ]
    assert result.values["evm_all_carriers_db"] == -36.14
    assert result.phases[-1] is MeasurementPhase.COMPLETE


@pytest.mark.parametrize(
    "fail_at", ["rf_on", "initiate_single", "wait_ready", "fetch_result", "drain_error_queue"]
)
def test_failure_still_stops_measurement_and_turns_rf_off(fail_at):
    backend = RecordingBackend(fail_at=fail_at)
    with pytest.raises(RuntimeError, match=fail_at):
        run_single_measurement(backend, safe_plan())
    if fail_at == "rf_on":
        assert backend.calls[-1:] == ["rf_off"]
    else:
        assert backend.calls[-2:] == ["stop_measurement", "rf_off"]


def test_stop_failure_does_not_prevent_rf_off():
    backend = RecordingBackend(fail_at="stop_measurement")
    result = run_single_measurement(backend, safe_plan())
    assert backend.calls[-1] == "rf_off"
    assert result.cleanup_errors[0].startswith("stop_measurement:")


@pytest.mark.parametrize(
    "overrides",
    [
        {"operator_confirmed": False},
        {"analyzer_port": "RF1.1"},
        {"generator_power_dbm": -20.0},
        {"center_frequency_hz": 0},
    ],
)
def test_safety_rejection_sends_no_backend_commands(overrides):
    backend = RecordingBackend()
    with pytest.raises(SafetyGuardError):
        run_single_measurement(backend, safe_plan(**overrides))
    assert backend.calls == []
