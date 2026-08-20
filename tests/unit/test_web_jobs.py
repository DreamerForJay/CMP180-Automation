import time

import pytest

from cmp180_evm.web.jobs import JobManager
from cmp180_evm.web.mock_service import simulate_point


def wait_terminal(manager, job_id):
    for _ in range(100):
        job = manager.get(job_id)
        if job.state in {"complete", "cancelled", "failed"}:
            return job
        time.sleep(0.005)
    raise AssertionError("job did not finish")


def test_job_reports_progress_and_complete_result():
    manager = JobManager()
    points = [simulate_point(6_105e6 + index * 20e6, 320e6, -40, index) for index in range(3)]
    job = manager.start(
        "mock-frequency-sweep",
        len(points),
        lambda active: manager.run_mock_points(
            active, points, lambda rows: {"count": len(rows)}, 0
        ),
    )
    done = wait_terminal(manager, job.job_id)
    assert done.state == "complete"
    assert done.completed_points == 3
    assert done.public()["progress_percent"] == 100


def test_cancel_stops_before_remaining_points_and_preserves_partial():
    manager = JobManager()
    points = [simulate_point(6_105e6, 320e6, -40, index) for index in range(5)]
    job = manager.start(
        "mock-frequency-sweep",
        len(points),
        lambda active: manager.run_mock_points(
            active, points, lambda rows: {"count": len(rows)}, 0.03
        ),
    )
    while manager.get(job.job_id).completed_points == 0:
        time.sleep(0.005)
    manager.cancel(job.job_id)
    done = wait_terminal(manager, job.job_id)
    assert done.state == "cancelled"
    assert done.completed_points < 5
    assert done.result["partial"] is True


def test_only_one_active_job_is_allowed():
    manager = JobManager()
    points = [simulate_point(6_105e6, 320e6, -40, index) for index in range(2)]
    first = manager.start(
        "mock",
        2,
        lambda active: manager.run_mock_points(active, points, lambda rows: {}, 0.05),
    )
    with pytest.raises(RuntimeError, match="already active"):
        manager.start("mock", 1, lambda active: {})
    wait_terminal(manager, first.job_id)
