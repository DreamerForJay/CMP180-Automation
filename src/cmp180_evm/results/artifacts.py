"""Persist real or simulated CMP180 single-measurement artifacts."""

from __future__ import annotations

import csv
import html
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from cmp180_evm.results.visualization import write_pandas_matplotlib_plots


def _matplotlib_artifacts(csv_path: Path) -> dict[str, str]:
    """Generate Web-visible Pandas/Matplotlib PNG artifacts for one saved CSV."""
    # PNG 一律由已落盤 CSV 產生，不重新連線儀器；這讓畫面、離線分析與稽核使用同一份資料。
    try:
        paths = write_pandas_matplotlib_plots(csv_path)
    except ValueError:
        # 舊版或最低欄位測試可能沒有頻率／功率軸；報告衍生失敗不得破壞原始 artifact 保存。
        return {}
    return {f"matplotlib_{path.stem}": str(path.resolve()) for path in paths}


def save_single_result(
    values: dict[str, object],
    output_root: Path,
    *,
    test_name: str,
    simulated: bool,
    metadata: dict[str, object] | None = None,
) -> dict[str, str]:
    """Save one immutable result row plus metadata and raw response."""
    now = datetime.now(UTC)
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
    measurement_metadata = metadata or {}
    # 單點儀器回傳本身沒有掃描軸；把已執行的設定寫回結果列，PNG 才能明確標示頻率座標。
    for key in ("frequency_hz", "bandwidth_hz", "generator_power_dbm"):
        if key in measurement_metadata:
            normalized.setdefault(key, measurement_metadata[key])
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
                **measurement_metadata,
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
        **_matplotlib_artifacts(csv_path),
        **{key: str(path.resolve()) for key, path in raw_paths.items()},
    }


def save_frequency_sweep_result(
    points: list[dict[str, object]],
    output_root: Path,
    *,
    requested_frequencies_hz: tuple[float, ...],
    completed: bool,
    failed_frequency_hz: float | None,
    error: str | None,
    metadata: dict[str, object] | None = None,
) -> dict[str, str]:
    """Persist completed or partial frequency-sweep results without instrument access."""
    now = datetime.now(UTC)
    run_id = uuid.uuid4().hex[:10]
    run_dir = output_root / f"{now.strftime('%Y%m%dT%H%M%SZ')}_real-frequency-sweep_{run_id}"
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=False)

    rows: list[dict[str, object]] = []
    for point_index, point in enumerate(points):
        # 原始 SCPI 回應分點保存，避免混入主要 CSV，也保留日後重新解析的依據。
        normalized: dict[str, object] = {}
        for key, value in point.items():
            if key == "raw" or key.startswith("raw_"):
                suffix = "average" if key == "raw" else key.removeprefix("raw_")
                (raw_dir / f"point_{point_index:02d}_modulation_{suffix}.txt").write_text(
                    str(value), encoding="utf-8"
                )
            else:
                normalized[key] = value
        rows.append(
            {
                "run_id": run_id,
                "timestamp": now.isoformat(),
                "simulated": False,
                "point_index": point_index,
                **normalized,
            }
        )

    csv_path = run_dir / "results.csv"
    fieldnames = (
        list(rows[0])
        if rows
        else ["run_id", "timestamp", "simulated", "point_index", "frequency_hz"]
    )
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    json_path = run_dir / "results.json"
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    metadata_path = run_dir / "metadata.json"
    metadata_payload = {
        "run_id": run_id,
        "test_name": "real-frequency-sweep",
        "created_at": now.isoformat(),
        "simulated": False,
        "status": "complete" if completed else "partial",
        "requested_frequencies_hz": requested_frequencies_hz,
        "completed_points": len(rows),
        "failed_frequency_hz": failed_frequency_hz,
        "error": error,
        **(metadata or {}),
    }
    metadata_path.write_text(json.dumps(metadata_payload, indent=2), encoding="utf-8")

    # 報告只讀取已落盤資料；所有儀器回傳值先 escape，避免 HTML 注入。
    headers = "".join(f"<th>{html.escape(str(name))}</th>" for name in fieldnames)
    body = "".join(
        "<tr>"
        + "".join(f"<td>{html.escape(str(row.get(name, '')))}</td>" for name in fieldnames)
        + "</tr>"
        for row in rows
    )
    report_path = run_dir / "report.html"
    report_path.write_text(
        "<!doctype html><html lang='zh-Hant'><meta charset='utf-8'>"
        "<title>CMP180 Frequency Sweep Report</title>"
        "<style>body{font:14px system-ui;margin:32px;color:#172033}"
        "table{border-collapse:collapse;width:100%;overflow:auto}"
        "th,td{padding:8px;border-bottom:1px solid #ddd;text-align:left;white-space:nowrap}"
        "th{background:#f4f7fb}</style>"
        f"<h1>CMP180 Frequency Sweep Report</h1><p>Status: {metadata_payload['status']}</p>"
        f"<table><thead><tr>{headers}</tr></thead><tbody>{body}</tbody></table>",
        encoding="utf-8",
    )
    return {
        "run_id": run_id,
        "run_dir": str(run_dir.resolve()),
        "csv": str(csv_path.resolve()),
        "json": str(json_path.resolve()),
        "metadata": str(metadata_path.resolve()),
        "report": str(report_path.resolve()),
        **_matplotlib_artifacts(csv_path),
    }


def save_power_sweep_result(
    points: list[dict[str, object]],
    output_root: Path,
    *,
    requested_powers_dbm: tuple[float, ...],
    completed: bool,
    failed_power_dbm: float | None,
    error: str | None,
    metadata: dict[str, object] | None = None,
) -> dict[str, str]:
    """Persist completed or partial power-sweep results without instrument access."""
    now = datetime.now(UTC)
    run_id = uuid.uuid4().hex[:10]
    run_dir = output_root / f"{now.strftime('%Y%m%dT%H%M%SZ')}_real-power-sweep_{run_id}"
    raw_dir = run_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=False)

    rows: list[dict[str, object]] = []
    for point_index, point in enumerate(points):
        normalized: dict[str, object] = {}
        for key, value in point.items():
            if key == "raw" or key.startswith("raw_"):
                # 原始 SCPI 回應逐功率點保存，避免混入主要 CSV。
                suffix = "average" if key == "raw" else key.removeprefix("raw_")
                (raw_dir / f"point_{point_index:02d}_modulation_{suffix}.txt").write_text(
                    str(value), encoding="utf-8"
                )
            else:
                normalized[key] = value
        rows.append(
            {
                "run_id": run_id,
                "timestamp": now.isoformat(),
                "simulated": False,
                "point_index": point_index,
                **normalized,
            }
        )

    csv_path = run_dir / "results.csv"
    fieldnames = (
        list(rows[0])
        if rows
        else ["run_id", "timestamp", "simulated", "point_index", "generator_power_dbm"]
    )
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    json_path = run_dir / "results.json"
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    metadata_path = run_dir / "metadata.json"
    metadata_payload = {
        "run_id": run_id,
        "test_name": "real-power-sweep",
        "created_at": now.isoformat(),
        "simulated": False,
        "status": "complete" if completed else "partial",
        "requested_powers_dbm": requested_powers_dbm,
        "completed_points": len(rows),
        "failed_power_dbm": failed_power_dbm,
        "error": error,
        **(metadata or {}),
    }
    metadata_path.write_text(json.dumps(metadata_payload, indent=2), encoding="utf-8")

    # HTML 僅呈現已保存的正規化資料，且 escape 所有儀器控制值。
    headers = "".join(f"<th>{html.escape(str(name))}</th>" for name in fieldnames)
    body = "".join(
        "<tr>"
        + "".join(f"<td>{html.escape(str(row.get(name, '')))}</td>" for name in fieldnames)
        + "</tr>"
        for row in rows
    )
    report_path = run_dir / "report.html"
    report_path.write_text(
        "<!doctype html><html lang='zh-Hant'><meta charset='utf-8'>"
        "<title>CMP180 Power Sweep Report</title>"
        "<style>body{font:14px system-ui;margin:32px;color:#172033}"
        "table{border-collapse:collapse;width:100%;overflow:auto}"
        "th,td{padding:8px;border-bottom:1px solid #ddd;text-align:left;white-space:nowrap}"
        "th{background:#f4f7fb}</style>"
        f"<h1>CMP180 Power Sweep Report</h1><p>Status: {metadata_payload['status']}</p>"
        f"<table><thead><tr>{headers}</tr></thead><tbody>{body}</tbody></table>",
        encoding="utf-8",
    )
    return {
        "run_id": run_id,
        "run_dir": str(run_dir.resolve()),
        "csv": str(csv_path.resolve()),
        "json": str(json_path.resolve()),
        "metadata": str(metadata_path.resolve()),
        "report": str(report_path.resolve()),
        **_matplotlib_artifacts(csv_path),
    }
