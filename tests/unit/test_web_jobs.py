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


def test_running_job_exposes_completed_points_for_read_only_live_plot():
    manager = JobManager()
    points = [simulate_point(6_105e6, 320e6, -40, index) for index in range(2)]
    job = manager.start(
        "live-preview",
        len(points),
        lambda active: manager.run_mock_points(active, points, lambda rows: {}, 0.02),
    )
    while manager.get(job.job_id).completed_points == 0:
        time.sleep(0.005)
    public = manager.get(job.job_id).public()
    # 即時資料來自已完成點，不會觸發額外量測或 SCPI 查詢。
    assert len(public["live_points"]) >= 1
    assert public["live_points"][0]["point_index"] == 0


def test_pause_waits_at_point_boundary_then_resumes() -> None:
    manager = JobManager()
    points = [simulate_point(6_105e6, 320e6, -40, index) for index in range(5)]
    job = manager.start(
        "mock-frequency-sweep",
        len(points),
        lambda active: manager.run_mock_points(
            active, points, lambda rows: {"count": len(rows)}, 0.02
        ),
    )
    while manager.get(job.job_id).completed_points == 0:
        time.sleep(0.005)
    manager.pause(job.job_id)
    for _ in range(100):
        if manager.get(job.job_id).state == "paused":
            break
        time.sleep(0.005)
    paused = manager.get(job.job_id)
    assert paused.state == "paused"
    paused_count = paused.completed_points
    time.sleep(0.04)
    # 暫停期間不得進入下一點；實機 workflow 同樣在 RF Off 邊界呼叫此 gate。
    assert manager.get(job.job_id).completed_points == paused_count
    manager.resume(job.job_id)
    done = wait_terminal(manager, job.job_id)
    assert done.state == "complete"
    assert done.completed_points == 5


def test_cancel_unblocks_a_paused_job() -> None:
    manager = JobManager()
    points = [simulate_point(6_105e6, 320e6, -40, index) for index in range(5)]
    job = manager.start(
        "mock-frequency-sweep",
        len(points),
        lambda active: manager.run_mock_points(
            active, points, lambda rows: {"count": len(rows)}, 0.02
        ),
    )
    manager.pause(job.job_id)
    for _ in range(100):
        if manager.get(job.job_id).state == "paused":
            break
        time.sleep(0.005)
    manager.cancel(job.job_id)
    done = wait_terminal(manager, job.job_id)
    assert done.state == "cancelled"
    assert done.cancel_requested is True


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


def test_measurement_failure_keeps_partial_result_and_failed_state():
    manager = JobManager()
    job = manager.start(
        "hardware-custom",
        3,
        lambda _active: {
            "measurement_failed": True,
            "error": "INV at point 2",
            "points": [{"point_index": 0}],
            "artifacts": {"run_id": "partial"},
        },
    )
    done = wait_terminal(manager, job.job_id)
    assert done.state == "failed"
    assert done.error == "INV at point 2"
    assert done.result["artifacts"]["run_id"] == "partial"
