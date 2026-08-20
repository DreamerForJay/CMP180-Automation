import pytest

from cmp180_evm.utils.exceptions import SafetyGuardError
from cmp180_evm.workflow.power_sweep import PowerSweepPlan, run_power_sweep
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan


class SweepBackend:
    def __init__(
        self,
        fail_power_dbm=None,
        instrument_error_power_dbm=None,
        invalid_power_dbm=None,
    ):
        self.power = 0.0
        self.fail_power_dbm = fail_power_dbm
        self.instrument_error_power_dbm = instrument_error_power_dbm
        self.invalid_power_dbm = invalid_power_dbm
        self.calls = []

    def configure(self, plan):
        self.power = plan.generator_power_dbm
        self.calls.append(("configure", self.power))

    def rf_on(self):
        self.calls.append(("rf_on", self.power))

    def initiate_single(self):
        self.calls.append(("initiate", self.power))

    def wait_ready(self):
        self.calls.append(("wait", self.power))
        if self.power == self.fail_power_dbm:
            raise TimeoutError("point timeout")

    def fetch_result(self):
        if self.power == self.invalid_power_dbm:
            return {
                "generator_power_dbm": self.power,
                "evm_all_carriers_db": "INV",
                "burst_power_dbm": "INV",
                "frequency_error_hz": "INV",
            }
        return {
            "generator_power_dbm": self.power,
            "evm_all_carriers_db": -36.0,
            "burst_power_dbm": -40.5,
            "frequency_error_hz": -10.0,
        }

    def stop_measurement(self):
        self.calls.append(("stop", self.power))

    def rf_off(self):
        self.calls.append(("rf_off", self.power))

    def drain_error_queue(self):
        if self.power == self.instrument_error_power_dbm:
            return ['-200,"Execution error"']
        return []


def sweep_plan(**overrides):
    single = SingleMeasurementPlan("RF1.1", "RF1.5", 6_105e6, 320e6, -40, -20, 0, True, -40)
    values = dict(
        single=single,
        start_power_dbm=-50.0,
        stop_power_dbm=-40.0,
        step_power_dbm=5.0,
        dwell_time_s=0.1,
    )
    values.update(overrides)
    return PowerSweepPlan(**values)


def test_short_sweep_runs_cleanup_for_every_point():
    backend = SweepBackend()
    waits = []
    result = run_power_sweep(backend, sweep_plan(), sleeper=waits.append)
    assert result.completed is True
    assert len(result.points) == 3
    assert [call[0] for call in backend.calls].count("rf_off") == 3
    assert waits == [0.1, 0.1]


def test_failure_stops_sweep_and_preserves_completed_points():
    backend = SweepBackend(fail_power_dbm=-45.0)
    result = run_power_sweep(backend, sweep_plan(), sleeper=lambda _: None)
    assert result.completed is False
    assert len(result.points) == 1
    assert result.failed_power_dbm == -45.0
    assert backend.calls[-1] == ("rf_off", -45.0)


def test_error_queue_stops_before_higher_power():
    backend = SweepBackend(instrument_error_power_dbm=-45.0)
    result = run_power_sweep(backend, sweep_plan(), sleeper=lambda _: None)
    assert result.completed is False
    assert len(result.points) == 2
    assert result.failed_power_dbm == -45.0
    assert result.error is not None and "Execution error" in result.error
    assert ("configure", -40.0) not in backend.calls


def test_invalid_metrics_stop_before_higher_power_even_with_empty_error_queue():
    backend = SweepBackend(invalid_power_dbm=-50.0)
    result = run_power_sweep(backend, sweep_plan(), sleeper=lambda _: None)
    assert result.completed is False
    assert len(result.points) == 1
    assert result.failed_power_dbm == -50.0
    assert result.error is not None and "evm_all_carriers_db" in result.error
    assert ("configure", -45.0) not in backend.calls


def test_cancel_stops_at_rf_off_point_boundary():
    backend = SweepBackend()
    completed = []
    result = run_power_sweep(
        backend,
        sweep_plan(),
        sleeper=lambda _: None,
        should_cancel=lambda: len(completed) == 1,
        on_point_complete=lambda count, _point: completed.append(count),
    )
    assert result.completed is False and result.error == "Cancelled"
    assert len(result.points) == 1
    assert backend.calls[-1] == ("rf_off", -50.0)


@pytest.mark.parametrize(
    "overrides",
    [
        {"stop_power_dbm": -30.0},
        {"start_power_dbm": -70.0, "stop_power_dbm": -65.0},
        {"step_power_dbm": 1.0, "maximum_points": 3},
        {"dwell_time_s": 0},
    ],
)
def test_unsafe_sweep_is_rejected_before_rf(overrides):
    backend = SweepBackend()
    with pytest.raises(SafetyGuardError):
        run_power_sweep(backend, sweep_plan(**overrides), sleeper=lambda _: None)
    assert backend.calls == []


@pytest.mark.parametrize(
    "single_overrides",
    [
        {"center_frequency_hz": 2_437e6},
        {"bandwidth_hz": 160e6},
    ],
)
def test_unverified_fixed_profile_is_rejected_before_rf(single_overrides):
    backend = SweepBackend()
    plan = sweep_plan()
    values = vars(plan.single) | single_overrides
    with pytest.raises(SafetyGuardError):
        run_power_sweep(
            backend, PowerSweepPlan(**(vars(plan) | {"single": SingleMeasurementPlan(**values)}))
        )
    assert backend.calls == []


def test_caller_cannot_raise_hard_power_or_point_limits():
    backend = SweepBackend()
    permissive_single = SingleMeasurementPlan(
        "RF1.1", "RF1.5", 6_105e6, 320e6, -30, -20, 0, True, -30
    )
    with pytest.raises(SafetyGuardError):
        run_power_sweep(
            backend,
            PowerSweepPlan(permissive_single, -50, -30, 5, maximum_power_dbm=-30),
        )
    with pytest.raises(SafetyGuardError):
        run_power_sweep(
            backend,
            PowerSweepPlan(
                sweep_plan().single,
                -60,
                -40,
                1,
                maximum_points=100,
            ),
        )
    assert backend.calls == []
