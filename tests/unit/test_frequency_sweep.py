import pytest

from cmp180_evm.utils.exceptions import SafetyGuardError
from cmp180_evm.workflow.frequency_sweep import FrequencySweepPlan, run_frequency_sweep
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan


class SweepBackend:
    def __init__(self, fail_frequency_hz=None, instrument_error_frequency_hz=None):
        self.frequency = 0.0
        self.fail_frequency_hz = fail_frequency_hz
        self.instrument_error_frequency_hz = instrument_error_frequency_hz
        self.calls = []

    def configure(self, plan):
        self.frequency = plan.center_frequency_hz
        self.calls.append(("configure", self.frequency))

    def rf_on(self):
        self.calls.append(("rf_on", self.frequency))

    def initiate_single(self):
        self.calls.append(("initiate", self.frequency))

    def wait_ready(self):
        self.calls.append(("wait", self.frequency))
        if self.frequency == self.fail_frequency_hz:
            raise TimeoutError("point timeout")

    def fetch_result(self):
        return {
            "frequency_hz": self.frequency,
            "reliability": "0",
            "evm_all_carriers_db": -36.0,
            "burst_power_dbm": -45.0,
            "frequency_error_hz": 1.0,
        }

    def stop_measurement(self):
        self.calls.append(("stop", self.frequency))

    def rf_off(self):
        self.calls.append(("rf_off", self.frequency))

    def drain_error_queue(self):
        if self.frequency == self.instrument_error_frequency_hz:
            return ['-200,"Execution error"']
        return []


def sweep_plan(**overrides):
    single = SingleMeasurementPlan("RF1.1", "RF1.5", 6_105e6, 320e6, -40, -20, 0, True, -40)
    values = dict(
        single=single,
        start_frequency_hz=6_085e6,
        stop_frequency_hz=6_125e6,
        step_frequency_hz=20e6,
        dwell_time_s=0.1,
    )
    values.update(overrides)
    return FrequencySweepPlan(**values)


def test_short_sweep_runs_cleanup_for_every_point():
    backend = SweepBackend()
    waits = []
    result = run_frequency_sweep(backend, sweep_plan(), sleeper=waits.append)
    assert result.completed is True
    assert len(result.points) == 3
    assert [call[0] for call in backend.calls].count("rf_off") == 3
    assert waits == [0.1, 0.1]


def test_catalog_frequency_sweep_generates_all_requested_points():
    single = SingleMeasurementPlan("RF1.1", "RF1.5", 5_085e6, 320e6, -45, -45, 0, True, -30)
    plan = sweep_plan(
        single=single,
        start_frequency_hz=5_085e6,
        stop_frequency_hz=6_125e6,
        step_frequency_hz=20e6,
    )
    points = plan.frequencies()
    assert len(points) == 53
    assert points[0] == 5_085e6
    assert points[-1] == 6_125e6


def test_failure_stops_sweep_and_preserves_completed_points():
    backend = SweepBackend(fail_frequency_hz=6_105e6)
    result = run_frequency_sweep(backend, sweep_plan(), sleeper=lambda _: None)
    assert result.completed is False
    assert len(result.points) == 1
    assert result.failed_frequency_hz == 6_105e6
    assert backend.calls[-1] == ("rf_off", 6_105e6)


def test_error_queue_stops_before_next_frequency():
    backend = SweepBackend(instrument_error_frequency_hz=6_105e6)
    result = run_frequency_sweep(backend, sweep_plan(), sleeper=lambda _: None)
    assert result.completed is False
    assert len(result.points) == 2
    assert result.failed_frequency_hz == 6_105e6
    assert result.error is not None and "Execution error" in result.error
    assert ("configure", 6_125e6) not in backend.calls


def test_invalid_critical_result_stops_before_next_frequency():
    backend = SweepBackend()
    original_fetch = backend.fetch_result

    def fetch_result():
        values = original_fetch()
        if backend.frequency == 6_105e6:
            values["evm_all_carriers_db"] = "INV"
        return values

    backend.fetch_result = fetch_result
    result = run_frequency_sweep(backend, sweep_plan(), sleeper=lambda _: None)
    assert result.completed is False
    assert len(result.points) == 2
    assert result.failed_frequency_hz == 6_105e6
    assert result.error == "Invalid critical result fields: evm_all_carriers_db"
    assert ("configure", 6_125e6) not in backend.calls


def test_nonzero_reliability_stops_before_next_frequency():
    backend = SweepBackend()
    original_fetch = backend.fetch_result

    def fetch_result():
        values = original_fetch()
        if backend.frequency == 6_105e6:
            values["reliability"] = "6"
        return values

    backend.fetch_result = fetch_result
    result = run_frequency_sweep(backend, sweep_plan(), sleeper=lambda _: None)
    assert result.completed is False
    assert result.failed_frequency_hz == 6_105e6
    assert result.error == "Invalid critical result fields: reliability"
    assert ("configure", 6_125e6) not in backend.calls


def test_cancel_stops_at_rf_off_point_boundary():
    backend = SweepBackend()
    completed = []
    result = run_frequency_sweep(
        backend,
        sweep_plan(),
        sleeper=lambda _: None,
        should_cancel=lambda: len(completed) == 1,
        on_point_complete=lambda count, _point: completed.append(count),
    )
    assert result.completed is False and result.error == "Cancelled"
    assert len(result.points) == 1
    assert backend.calls[-1] == ("rf_off", 6_085e6)


@pytest.mark.parametrize(
    "overrides",
    [
        {"start_frequency_hz": 399e6},
        {"stop_frequency_hz": 8_001e6},
        {"step_frequency_hz": 1e6, "maximum_points": 3},
        {"dwell_time_s": 0},
    ],
)
def test_unsafe_sweep_is_rejected_before_rf(overrides):
    backend = SweepBackend()
    with pytest.raises(SafetyGuardError):
        run_frequency_sweep(backend, sweep_plan(**overrides), sleeper=lambda _: None)
    assert backend.calls == []


def test_caller_can_narrow_but_not_exceed_cmp180_catalog_range():
    backend = SweepBackend()
    # 呼叫端以 profile/校正資料設定的較窄下限必須被遵守。
    narrowed = sweep_plan(
        start_frequency_hz=5_800e6,
        stop_frequency_hz=5_900e6,
        minimum_frequency_hz=6_000e6,
    )
    with pytest.raises(SafetyGuardError):
        run_frequency_sweep(backend, narrowed, sleeper=lambda _: None)

    too_many = sweep_plan(start_frequency_hz=400e6, stop_frequency_hz=8e9, step_frequency_hz=1)
    with pytest.raises(SafetyGuardError):
        run_frequency_sweep(backend, too_many, sleeper=lambda _: None)
    assert backend.calls == []


def test_supported_wlan_bandwidths_are_allowed_before_rf():
    backend = SweepBackend()
    plan = sweep_plan()
    single = SingleMeasurementPlan(**(vars(plan.single) | {"bandwidth_hz": 160e6}))
    result = run_frequency_sweep(
        backend,
        FrequencySweepPlan(**(vars(plan) | {"single": single})),
        sleeper=lambda _: None,
    )
    assert result.completed is True
