"""Thread-safe in-memory job state for local sweep execution."""

from __future__ import annotations

import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass, field


@dataclass
class SweepJob:
    job_id: str
    kind: str
    total_points: int
    state: str = "queued"
    completed_points: int = 0
    message: str = ""
    result: dict[str, object] | None = None
    error: str | None = None
    cancel_requested: bool = False
    _cancel_event: threading.Event = field(default_factory=threading.Event, repr=False)

    def public(self) -> dict[str, object]:
        # threading.Event 不可序列化；公開欄位明列，避免洩漏執行緒內部狀態。
        payload = {
            "job_id": self.job_id,
            "kind": self.kind,
            "total_points": self.total_points,
            "state": self.state,
            "completed_points": self.completed_points,
            "message": self.message,
            "result": self.result,
            "error": self.error,
            "cancel_requested": self.cancel_requested,
        }
        payload["progress_percent"] = round(
            self.completed_points / self.total_points * 100 if self.total_points else 0, 1
        )
        return payload

    def is_cancel_requested(self) -> bool:
        return self._cancel_event.is_set()

    def point_completed(self, count: int) -> None:
        self.completed_points = count
        self.message = f"Point {count}/{self.total_points}"


class JobManager:
    """Allow only one active sweep and expose cooperative cancellation."""

    def __init__(self) -> None:
        self._jobs: dict[str, SweepJob] = {}
        self._lock = threading.Lock()

    def start(
        self,
        kind: str,
        total_points: int,
        worker: Callable[[SweepJob], dict[str, object]],
    ) -> SweepJob:
        with self._lock:
            if any(job.state in {"queued", "running", "stopping"} for job in self._jobs.values()):
                raise RuntimeError("Another measurement job is already active")
            job = SweepJob(uuid.uuid4().hex[:12], kind, total_points)
            self._jobs[job.job_id] = job
        threading.Thread(target=self._run, args=(job, worker), daemon=True).start()
        return job

    def _run(self, job: SweepJob, worker: Callable[[SweepJob], dict[str, object]]) -> None:
        job.state = "running"
        try:
            job.result = worker(job)
            # 量測失敗仍保留 partial artifacts；狀態不可因 worker 正常回傳而誤標 complete。
            if job.result.get("measurement_failed") is True:
                job.error = str(job.result.get("error") or "Measurement failed")
                job.state = "failed"
            else:
                job.state = "cancelled" if job.cancel_requested else "complete"
        except Exception as exc:
            job.error = f"{type(exc).__name__}: {exc}"
            job.state = "failed"

    def get(self, job_id: str) -> SweepJob:
        try:
            return self._jobs[job_id]
        except KeyError as exc:
            raise KeyError("Measurement job not found") from exc

    def cancel(self, job_id: str) -> SweepJob:
        job = self.get(job_id)
        if job.state not in {"queued", "running", "stopping"}:
            return job
        # 取消採 cooperative gate；實機接入時由 workflow 在點與點間做 STOP/RF Off。
        job.cancel_requested = True
        job.state = "stopping"
        job._cancel_event.set()
        return job

    @staticmethod
    def run_mock_points(
        job: SweepJob,
        points: list[object],
        save: Callable[[list[object]], dict[str, object]],
        dwell_s: float,
    ) -> dict[str, object]:
        captured: list[object] = []
        for index, point in enumerate(points):
            if job._cancel_event.is_set():
                break
            captured.append(point)
            job.completed_points = index + 1
            job.message = f"Point {index + 1}/{job.total_points}"
            if index < len(points) - 1:
                time.sleep(dwell_s)
        artifacts = save(captured)
        return {
            "simulated": True,
            "points": [asdict(point) for point in captured],
            "artifacts": artifacts,
            "partial": len(captured) < len(points),
        }
