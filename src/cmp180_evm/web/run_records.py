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


def rename_run_record(output_root: Path, run_key: str, display_name: str) -> dict[str, str]:
    """Save an operator-facing display name without renaming the evidence directory."""
    run_dir = resolve_run_dir(output_root, run_key)
    normalized = " ".join(display_name.split())
    if not normalized or len(normalized) > 120 or any(ord(char) < 32 for char in normalized):
        raise ValueError("Display name must contain 1 to 120 printable characters")
    metadata_path = run_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise ValueError("Run record metadata must be an object")
    # 顯示名稱只改 metadata，不改 run 目錄或 run_id，讓既有 artifact URL 與量測證據保持可追溯。
    metadata["display_name"] = normalized
    metadata["display_name_updated_at"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"status": "renamed", "run_key": run_key, "display_name": normalized}


def open_run_folder(output_root: Path, run_key: str) -> None:
    run_dir = resolve_run_dir(output_root, run_key)
    if os.name != "nt":
        raise OSError("Open folder is supported only on the local Windows workstation")
    # os.startfile 只接收上方已驗證的 output 直接子目錄，不接受 request 提供的任意路徑。
    os.startfile(run_dir)  # type: ignore[attr-defined]
