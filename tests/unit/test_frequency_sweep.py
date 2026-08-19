import pytest

from cmp180_evm.utils.exceptions import SafetyGuardError
from cmp180_evm.workflow.frequency_sweep import FrequencySweepPlan, run_frequency_sweep
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan


class SweepBackend:
    def __init__(self, fail_frequency_hz=None):
        self.frequency = 0.0
        self.fail_frequency_hz = fail_frequency_hz
        self.calls = []

    def configure(self, plan): self.frequency = plan.center_frequency_hz; self.calls.append(("configure", self.frequency))
    def rf_on(self): self.calls.append(("rf_on", self.frequency))
    def initiate_single(self): self.calls.append(("initiate", self.frequency))
    def wait_ready(self):
        self.calls.append(("wait", self.frequency))
        if self.frequency == self.fail_frequency_hz: raise TimeoutError("point timeout")
    def fetch_result(self): return {"frequency_hz": self.frequency, "evm_all_carriers_db": -36.0}
    def stop_measurement(self): self.calls.append(("stop", self.frequency))
    def rf_off(self): self.calls.append(("rf_off", self.frequency))
    def drain_error_queue(self): return []


def sweep_plan(**overrides):
    single = SingleMeasurementPlan("RF1.1", "RF1.5", 6_105e6, 320e6, -40, -20, 0, True, -40)
    values = dict(single=single, start_frequency_hz=6_085e6, stop_frequency_hz=6_125e6, step_frequency_hz=20e6, dwell_time_s=.1)
    values.update(overrides)
    return FrequencySweepPlan(**values)


def test_short_sweep_runs_cleanup_for_every_point():
    backend = SweepBackend()
    waits = []
    result = run_frequency_sweep(backend, sweep_plan(), sleeper=waits.append)
    assert result.completed is True
    assert len(result.points) == 3
    assert [call[0] for call in backend.calls].count("rf_off") == 3
    assert waits == [.1, .1]


def test_failure_stops_sweep_and_preserves_completed_points():
    backend = SweepBackend(fail_frequency_hz=6_105e6)
    result = run_frequency_sweep(backend, sweep_plan(), sleeper=lambda _: None)
    assert result.completed is False
    assert len(result.points) == 1
    assert result.failed_frequency_hz == 6_105e6
    assert backend.calls[-1] == ("rf_off", 6_105e6)


@pytest.mark.parametrize("overrides", [
    {"stop_frequency_hz": 6_405e6},
    {"step_frequency_hz": 1e6, "maximum_points": 3},
    {"dwell_time_s": 0},
])
def test_unsafe_sweep_is_rejected_before_rf(overrides):
    backend = SweepBackend()
    with pytest.raises(SafetyGuardError):
        run_frequency_sweep(backend, sweep_plan(**overrides), sleeper=lambda _: None)
    assert backend.calls == []
