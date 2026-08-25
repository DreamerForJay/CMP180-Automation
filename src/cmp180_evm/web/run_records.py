"""Safe local run-record loading, folder opening, and recoverable trash operations."""

from __future__ import annotations

import json
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path


def resolve_run_dir(output_root: Path, run_key: str) -> Path:
    """Resolve one direct output child without accepting arbitrary paths."""
    if not run_key or Path(run_key).name != run_key or run_key in {".", "..", ".trash"}:
        raise ValueError("Invalid run key")
    root = output_root.resolve()
    candidate = (root / run_key).resolve()
    # 只允許 output/ 的直接子目錄，避免以 ../、symlink 或絕對路徑操作其他資料。
    if candidate.parent != root or not candidate.is_dir():
        raise FileNotFoundError("Run record not found")
    if not (candidate / "metadata.json").is_file():
        raise ValueError("Run record has no metadata")
    return candidate


def load_run_record(output_root: Path, run_key: str) -> dict[str, object]:
    run_dir = resolve_run_dir(output_root, run_key)
    metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    results_path = run_dir / "results.json"
    results = (
        json.loads(results_path.read_text(encoding="utf-8")) if results_path.is_file() else None
    )
    waveform = metadata.get("arb_waveform_file") or metadata.get("waveform_file")
    raw_dir = run_dir / "raw"
    raw_files = sorted(path.name for path in raw_dir.glob("*.txt")) if raw_dir.is_dir() else []
    return {
        "run_key": run_key,
        "output_location": f"output/{run_key}/",
        "metadata": metadata,
        "results": results,
        "waveform_reference": waveform,
        "waveform_recorded": waveform is not None,
        "raw_files": raw_files,
    }


def move_run_to_trash(output_root: Path, run_key: str, confirmed_run_id: str) -> dict[str, str]:
    run_dir = resolve_run_dir(output_root, run_key)
    metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    actual_run_id = str(metadata.get("run_id") or "")
    if not actual_run_id or confirmed_run_id != actual_run_id:
        raise ValueError("Run ID confirmation does not match")
    trash_root = output_root.resolve() / ".trash"
    trash_root.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    destination = trash_root / f"{stamp}_{run_dir.name}"
    # 使用 move 保留完整 artifacts，可由管理者手動復原；不做永久刪除。
    shutil.move(str(run_dir), str(destination))
    return {"status": "trashed", "run_id": actual_run_id, "trash_key": destination.name}


def open_run_folder(output_root: Path, run_key: str) -> None:
    run_dir = resolve_run_dir(output_root, run_key)
    if os.name != "nt":
        raise OSError("Open folder is supported only on the local Windows workstation")
    # os.startfile 只接收上方已驗證的 output 直接子目錄，不接受 request 提供的任意路徑。
    os.startfile(run_dir)  # type: ignore[attr-defined]
