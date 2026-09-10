"""保存可稽核的 MCS sweep Mock／stored artifacts。"""

from __future__ import annotations

import csv
import json
import re
import uuid
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .models import MCSSweepDataset


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-") or "mcs-sweep"


def save_mcs_sweep_artifacts(
    dataset: MCSSweepDataset, output_root: Path, test_name: str = "mcs-sweep-mock"
) -> dict[str, str]:
    """輸出 CSV、JSON、SVG、PNG 與 metadata；不產生 PASS／FAIL compliance 判定。"""
    timestamp = datetime.now(UTC)
    run_id = uuid.uuid4().hex[:10]
    run_dir = output_root / f"{timestamp:%Y%m%dT%H%M%SZ}_{_safe_name(test_name)}_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=False)
    payload = dataset.public()

    csv_path = run_dir / "mcs_sweep.csv"
    fieldnames = [
        "mcs_index",
        "modulation",
        "coding_rate",
        "bandwidth_mhz",
        "frequency_hz",
        "evm_db",
        "power_dbm",
        "frequency_error_hz",
        "reliability",
        "valid",
        "provenance",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for point in dataset.points:
            row = asdict(point)
            row["provenance"] = ";".join(point.provenance)
            writer.writerow(row)

    json_path = run_dir / "mcs_sweep.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    metadata = {
        **asdict(dataset.metadata),
        "source": dataset.metadata.source.value,
        "hil_status": dataset.metadata.hil_status.value,
        "run_id": run_id,
        "test_name": test_name,
        "created_at": timestamp.isoformat(),
        "measurement_type": "mcs_sweep",
        "status": "complete",
        "compliance_claim": False,
        "artifact_schema": "mcs-sweep-v1",
    }
    metadata_path = run_dir / "mcs_sweep_metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    valid = [point for point in dataset.points if point.valid and point.evm_db is not None]
    valid_mcs: list[int] = []
    valid_evm: list[float] = []
    for point in valid:
        # valid 篩選已排除缺值；invalid 不補 0，避免圖表製造假量測點。
        assert point.evm_db is not None
        valid_mcs.append(point.mcs_index)
        valid_evm.append(point.evm_db)
    figure, axis = plt.subplots(figsize=(9, 5.5), constrained_layout=True)
    axis.plot(
        valid_mcs,
        valid_evm,
        marker="o",
        linewidth=1.6,
        label="EVM / SIMULATED",
    )
    invalid = [point.mcs_index for point in dataset.points if not point.valid]
    if invalid:
        # invalid 沒有 EVM 座標，只在圖例列出索引，不偽造為 0 dB。
        axis.scatter([], [], marker="x", color="#d1495b", label=f"Invalid MCS {invalid}")
    axis.set_xlabel("MCS index")
    axis.set_ylabel("EVM (dB)")
    axis.set_title("EHT MCS Sweep — SOFTWARE / MOCK VERIFIED")
    axis.set_xticks(list(dataset.metadata.selected_mcs))
    axis.grid(True, alpha=0.25)
    axis.legend(loc="best")
    svg_path = run_dir / "mcs_sweep.svg"
    png_path = run_dir / "mcs_sweep.png"
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
