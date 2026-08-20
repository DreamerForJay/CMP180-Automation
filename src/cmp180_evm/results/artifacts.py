"""Persist real or simulated CMP180 single-measurement artifacts."""

from __future__ import annotations

import csv
import html
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def save_single_result(
    values: dict[str, object],
    output_root: Path,
    *,
    test_name: str,
    simulated: bool,
    metadata: dict[str, object] | None = None,
) -> dict[str, str]:
    """Save one immutable result row plus metadata and raw response."""
    now = datetime.now(timezone.utc)
    run_id = uuid.uuid4().hex[:10]
    safe_name = "".join(char if char.isalnum() or char in "-_" else "_" for char in test_name)
    run_dir = output_root / f"{now.strftime('%Y%m%dT%H%M%SZ')}_{safe_name}_{run_id}"
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=False)

    # "raw"（average，向後相容）與 "raw_*"（current/min/max/std_dev 等其他
    # 已驗證統計查詢）都各自獨立保存，parser 或 schema 更新後仍可離線重現；
    # 兩者都從主要結果欄位中排除，不進 CSV/JSON row。
    normalized = {
        key: value
        for key, value in values.items()
        if key != "raw" and not key.startswith("raw_")
    }
    row = {
        "run_id": run_id,
        "timestamp": now.isoformat(),
        "simulated": simulated,
        **normalized,
    }
    raw_paths: dict[str, Path] = {}
    for key, value in values.items():
        if key == "raw":
            filename = "modulation_average.txt"
        elif key.startswith("raw_"):
            filename = f"modulation_{key[len('raw_'):]}.txt"
        else:
            continue
        path = raw_dir / filename
        path.write_text(str(value), encoding="utf-8")
        raw_paths[key] = path
    csv_path = run_dir / "results.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
    json_path = run_dir / "results.json"
    json_path.write_text(json.dumps(row, indent=2), encoding="utf-8")
    metadata_path = run_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "test_name": test_name,
                "created_at": now.isoformat(),
                "simulated": simulated,
                "status": "complete",
                **(metadata or {}),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    report_path = run_dir / "report.html"
    # HTML 使用已保存的 normalized row，不需重新連線 CMP180 即可開啟。
    # 儀器回應跨越信任邊界；HTML report 必須 escape，避免離線 XSS。
    cells = "".join(
        f"<tr><th>{html.escape(str(key))}</th><td>{html.escape(str(value))}</td></tr>"
        for key, value in row.items()
    )
    report_path.write_text(
        "<!doctype html><html lang='zh-Hant'><meta charset='utf-8'>"
        "<title>CMP180 SingleShot Report</title>"
        "<style>body{font:15px system-ui;margin:32px;color:#172033}"
        "table{border-collapse:collapse;width:100%;max-width:960px}"
        "th,td{padding:9px;border-bottom:1px solid #ddd;text-align:left}"
        "th{width:260px;background:#f4f7fb}</style>"
        f"<h1>CMP180 SingleShot Report</h1><p>Run ID: {html.escape(run_id)}</p>"
        f"<table>{cells}</table>",
        encoding="utf-8",
    )
    return {
        "run_id": run_id,
        "run_dir": str(run_dir.resolve()),
        "csv": str(csv_path.resolve()),
        "json": str(json_path.resolve()),
        "metadata": str(metadata_path.resolve()),
        "report": str(report_path.resolve()),
        **{key: str(path.resolve()) for key, path in raw_paths.items()},
    }
