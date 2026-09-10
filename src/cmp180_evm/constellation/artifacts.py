"""Persist auditable mock/stored constellation artifacts without instrument access."""

from __future__ import annotations

import csv
import json
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .models import ConstellationDataset


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-") or "constellation"


def save_constellation_artifacts(
    dataset: ConstellationDataset, output_root: Path, test_name: str = "constellation-mock"
) -> dict[str, str]:
    """Save CSV, JSON, SVG, PNG, and metadata with explicit source/HIL labels."""
    timestamp = datetime.now(UTC)
    run_id = uuid.uuid4().hex[:10]
    run_dir = output_root / f"{timestamp:%Y%m%dT%H%M%SZ}_{_safe_name(test_name)}_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=False)
    public = dataset.public()
    point_rows = cast(list[dict[str, object]], public["points"])
    metadata_public = cast(dict[str, object], public["metadata"])

    csv_path = run_dir / "constellation.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        fieldnames = [
            "symbol_index",
            "i",
            "q",
            "normalized_i",
            "normalized_q",
            "ideal_i",
            "ideal_q",
            "evm",
            "valid",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows({key: point[key] for key in fieldnames} for point in point_rows)

    json_path = run_dir / "constellation.json"
    json_path.write_text(json.dumps(public, ensure_ascii=False, indent=2), encoding="utf-8")

    metadata = {
        **metadata_public,
        "run_id": run_id,
        "test_name": test_name,
        "created_at": timestamp.isoformat(),
        "status": "complete",
        "measurement_type": "constellation",
        "hardware_support": "HIL_PENDING",
        "compliance_claim": False,
        "artifact_schema": "constellation-v1",
    }
    metadata_path = run_dir / "constellation_metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    figure, axis = plt.subplots(figsize=(8, 8), constrained_layout=True)
    valid = [point for point in dataset.points if point.valid and point.i is not None and point.q is not None]
    invalid = [point for point in dataset.points if not point.valid]
    plot_i: list[float] = []
    plot_q: list[float] = []
    for point in valid:
        # invalid 點不補零；只有已確認有限的座標能進入 scatter。
        assert point.i is not None and point.q is not None
        plot_i.append(point.i)
        plot_q.append(point.q)
    axis.scatter(plot_i, plot_q, s=9, alpha=0.55, label="Measured / SIMULATED")
    axis.scatter(
        [point[0] for point in dataset.ideal_points],
        [point[1] for point in dataset.ideal_points],
        marker="+",
        s=38,
        linewidths=1.2,
        label="Ideal reference",
    )
    if invalid:
        # invalid 沒有可畫的座標，只在圖例保留數量，避免把缺值偽造成原點。
        axis.scatter([], [], marker="x", color="#d1495b", label=f"Invalid ({len(invalid)})")
    axis.set_aspect("equal", adjustable="box")
    axis.set_xlabel("I")
    axis.set_ylabel("Q")
    axis.set_title(f"{dataset.metadata.modulation} Constellation — SOFTWARE / MOCK VERIFIED")
    axis.grid(True, alpha=0.25)
    axis.legend(loc="best")
    svg_path = run_dir / "constellation.svg"
    png_path = run_dir / "constellation.png"
    figure.savefig(svg_path, format="svg")
    figure.savefig(png_path, format="png", dpi=180)
    plt.close(figure)

    return {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "csv": str(csv_path),
        "json": str(json_path),
        "svg": str(svg_path),
        "png": str(png_path),
        "metadata": str(metadata_path),
    }
