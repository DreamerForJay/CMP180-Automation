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
    pause_requested: bool = False
    live_points: list[dict[str, object]] = field(default_factory=list)
    _cancel_event: threading.Event = field(default_factory=threading.Event, repr=False)
    _resume_event: threading.Event = field(default_factory=threading.Event, repr=False)

    def __post_init__(self) -> None:
        self._resume_event.set()

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
            "pause_requested": self.pause_requested,
            # 只公開已完成點的正規化快照；前端可即時畫圖，但不會因此多送任何 SCPI。
            "live_points": list(self.live_points),
        }
        payload["progress_percent"] = round(
            self.completed_points / self.total_points * 100 if self.total_points else 0, 1
        )
        return payload

    def is_cancel_requested(self) -> bool:
        # 暫停只會在 workflow 的點位邊界被檢查；上一點已 STOP 且 RF Off，禁止在 RF On 中途凍結。
        while self.pause_requested and not self._cancel_event.is_set():
            self.state = "paused"
            self.message = f"Paused safely after point {self.completed_points}/{self.total_points}"
            self._resume_event.wait(timeout=0.1)
        if not self._cancel_event.is_set() and self.state == "paused":
            self.state = "running"
            self.message = f"Resuming at point {self.completed_points + 1}/{self.total_points}"
        return self._cancel_event.is_set()

    def point_completed(self, count: int, point: dict[str, object] | None = None) -> None:
        self.completed_points = count
        self.message = f"Point {count}/{self.total_points}"
        if point is not None:
            self.live_points.append(point)


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
            if any(
                job.state in {"queued", "running", "paused", "stopping"}
                for job in self._jobs.values()
            ):
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
        if job.state not in {"queued", "running", "paused", "stopping"}:
            return job
        # 取消採 cooperative gate；實機接入時由 workflow 在點與點間做 STOP/RF Off。
        job.cancel_requested = True
        job.pause_requested = False
        job.state = "stopping"
        job._cancel_event.set()
        job._resume_event.set()
        return job

    def pause(self, job_id: str) -> SweepJob:
        job = self.get(job_id)
        if job.state not in {"queued", "running"}:
            return job
        # 只提出暫停要求；真正 PAUSED 由下一個 RF Off 點位邊界進入。
        job.pause_requested = True
        job.message = "Pause requested; waiting for the next RF-Off boundary"
        job._resume_event.clear()
        return job

    def resume(self, job_id: str) -> SweepJob:
        job = self.get(job_id)
        if job.state != "paused" and not job.pause_requested:
            return job
        job.pause_requested = False
        job.state = "running"
        job.message = f"Resuming at point {job.completed_points + 1}/{job.total_points}"
        job._resume_event.set()
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
            if job.is_cancel_requested():
                break
            captured.append(point)
            job.completed_points = index + 1
            job.message = f"Point {index + 1}/{job.total_points}"
            point_payload = asdict(point)
            point_payload.setdefault("point_index", index)
            job.live_points.append(point_payload)
            if index < len(points) - 1:
                time.sleep(dwell_s)
        artifacts = save(captured)
        return {
            "simulated": True,
            "points": [asdict(point) for point in captured],
            "artifacts": artifacts,
            "partial": len(captured) < len(points),
        }
