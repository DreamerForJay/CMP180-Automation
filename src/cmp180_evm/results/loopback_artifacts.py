"""Traceable CSV/JSON artifacts for loopback baseline verification."""

from __future__ import annotations

import csv
import html
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path


def save_loopback_result(
    result: dict[str, object],
    output_root: Path,
    *,
    simulated: bool,
    metadata: dict[str, object],
) -> dict[str, str]:
    """Persist every repeat, raw response, statistics, and profile snapshot."""
    now = datetime.now(UTC)
    run_id = uuid.uuid4().hex[:10]
    run_dir = output_root / f"{now.strftime('%Y%m%dT%H%M%SZ')}_loopback-validation_{run_id}"
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=False)
    measurements = list(result.get("measurements", []))
    rows: list[dict[str, object]] = []
    for measurement in measurements:
        row = dict(measurement)
        repeat_index = int(row["repeat_index"])
        for key in list(row):
            if key == "raw" or key.startswith("raw_"):
                suffix = "average" if key == "raw" else key.removeprefix("raw_")
                # Raw SCPI 永久保留且不塞進 CSV，避免 sentinel 或逗號破壞正規化欄位。
                (raw_dir / f"repeat_{repeat_index:03d}_modulation_{suffix}.txt").write_text(
                    str(row.pop(key)), encoding="utf-8"
                )
        for key in ("invalid_reasons", "instrument_errors", "cleanup_errors"):
            row[key] = json.dumps(row.get(key, []), ensure_ascii=False)
        rows.append(row)

    csv_path = run_dir / "raw_measurements.csv"
    fieldnames = list(rows[0]) if rows else ["repeat_index", "timestamp"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    raw_json_path = run_dir / "raw_measurements.json"
    raw_json_path.write_text(json.dumps(measurements, indent=2), encoding="utf-8")
    validation_path = run_dir / "validation_result.json"
    validation_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    profile_path = run_dir / "profile_snapshot.json"
    analysis = dict(result.get("analysis", {}))
    profile_path.write_text(json.dumps(analysis.get("profile", {}), indent=2), encoding="utf-8")
    metadata_path = run_dir / "metadata.json"
    metadata_payload = {
        "run_id": run_id,
        "test_name": "loopback-validation",
        "created_at": now.isoformat(),
        "simulated": simulated,
        "status": "complete" if result.get("completed") else "partial",
        "completed_points": len(measurements),
        "overall_status": analysis.get("overall_status"),
        **metadata,
    }
    metadata_path.write_text(json.dumps(metadata_payload, indent=2), encoding="utf-8")

    # 報告完整呈現三層判定；所有量測文字先 escape，避免 raw instrument data 注入 HTML。
    stats = analysis.get("statistics", {})
    summary = "".join(
        f"<tr><th>{html.escape(str(name))}</th><td>{html.escape(str(value))}</td></tr>"
        for name, value in {
            "Overall": analysis.get("overall_status"),
            "Validity": analysis.get("validity_status"),
            "Stability": analysis.get("stability_status"),
            "Reasonableness": analysis.get("reasonableness_status"),
            "Valid": f"{analysis.get('valid_count')}/{analysis.get('repeat_count')}",
            "Outliers": analysis.get("outlier_count"),
            "Statistics": stats,
        }.items()
    )
    report_path = run_dir / "report.html"
    report_path.write_text(
        "<!doctype html><html lang='zh-Hant'><meta charset='utf-8'>"
        "<title>Loopback Validation</title><style>body{font:14px system-ui;margin:32px}"
        "table{border-collapse:collapse;width:100%}th,td{padding:8px;border-bottom:1px solid #ddd;"
        "text-align:left;vertical-align:top}th{width:220px;background:#f4f7fb}</style>"
        f"<h1>Loopback Validation / 回送基線驗證</h1><p>Run ID: {html.escape(run_id)}</p>"
        f"<table>{summary}</table></html>",
        encoding="utf-8",
    )
    return {
        "run_id": run_id,
        "run_dir": str(run_dir.resolve()),
        "csv": str(csv_path.resolve()),
        "json": str(validation_path.resolve()),
        "raw_json": str(raw_json_path.resolve()),
        "profile": str(profile_path.resolve()),
        "metadata": str(metadata_path.resolve()),
        "report": str(report_path.resolve()),
    }
