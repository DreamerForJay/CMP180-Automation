"""Deterministic mock measurements and offline run artifacts."""

from __future__ import annotations

import csv
import json
import math
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class MockPoint:
    point_index: int
    frequency_hz: float
    bandwidth_hz: float
    generator_power_dbm: float
    evm_all_db: float
    evm_data_db: float
    evm_pilot_db: float
    burst_power_dbm: float
    frequency_error_hz: float
    clock_error_ppm: float
    valid: bool
    limit_status: str


def build_frequency_points(
    start_hz: float,
    stop_hz: float,
    step_hz: float,
) -> list[float]:
    """Build an inclusive frequency list without floating-point accumulation."""
    if start_hz <= 0 or stop_hz < start_hz or step_hz <= 0:
        raise ValueError("Invalid frequency range or step")
    count = int(math.floor((stop_hz - start_hz) / step_hz)) + 1
    if count > 1001:
        raise ValueError("Sweep exceeds the 1001-point GUI safety limit")
    return [start_hz + index * step_hz for index in range(count)]


def simulate_point(
    frequency_hz: float,
    bandwidth_hz: float,
    generator_power_dbm: float,
    point_index: int = 0,
) -> MockPoint:
    """Return stable simulated values; never represent them as hardware data."""
    # 使用固定公式而非亂數，讓測試、CSV 與圖表每次都能重現。
    phase = frequency_hz / 100_000_000.0
    evm_all = -36.0 + 1.8 * math.sin(phase)
    evm_data = evm_all + 0.35
    evm_pilot = evm_all - 0.55
    burst_power = generator_power_dbm - 0.45 + 0.12 * math.cos(phase)
    frequency_error = 7.5 * math.sin(phase * 0.7)
    clock_error = 0.18 * math.cos(phase * 0.4)
    return MockPoint(
        point_index=point_index,
        frequency_hz=frequency_hz,
        bandwidth_hz=bandwidth_hz,
        generator_power_dbm=generator_power_dbm,
        evm_all_db=round(evm_all, 4),
        evm_data_db=round(evm_data, 4),
        evm_pilot_db=round(evm_pilot, 4),
        burst_power_dbm=round(burst_power, 4),
        frequency_error_hz=round(frequency_error, 4),
        clock_error_ppm=round(clock_error, 6),
        valid=True,
        limit_status="PASS" if evm_all <= -32.0 else "FAIL",
    )


def save_mock_run(
    points: list[MockPoint],
    output_root: Path,
    test_name: str,
) -> dict[str, str]:
    """Persist normalized mock CSV/JSON and a self-contained HTML report."""
    now = datetime.now(timezone.utc)
    run_id = uuid.uuid4().hex[:10]
    safe_name = "".join(char if char.isalnum() or char in "-_" else "_" for char in test_name)
    run_dir = output_root / f"{now.strftime('%Y%m%dT%H%M%SZ')}_{safe_name}_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=False)
    rows = [asdict(point) for point in points]

    # CSV schema 固定使用英文，避免介面語言切換破壞後續分析流程。
    csv_path = run_dir / "results.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    json_path = run_dir / "results.json"
    json_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "simulated": True,
                "created_at": now.isoformat(),
                "points": rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    metadata_path = run_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "test_name": test_name,
                "status": "complete",
                "simulated": True,
                "point_count": len(points),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    report_path = run_dir / "report.html"
    report_path.write_text(_build_html_report(run_id, rows), encoding="utf-8")
    return {
        "run_id": run_id,
        "run_dir": str(run_dir.resolve()),
        "csv": str(csv_path.resolve()),
        "json": str(json_path.resolve()),
        "report": str(report_path.resolve()),
    }


def _build_html_report(run_id: str, rows: list[dict[str, object]]) -> str:
    encoded = json.dumps(rows).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="zh-Hant"><meta charset="utf-8"><title>CMP180 Mock Report</title>
<style>body{{font:15px system-ui;margin:32px;color:#172033}}table{{border-collapse:collapse;width:100%}}
th,td{{padding:8px;border-bottom:1px solid #ddd;text-align:right}}th:first-child,td:first-child{{text-align:left}}
.badge{{background:#fff3cd;padding:8px 12px;border-radius:8px}}</style>
<h1>CMP180 WLAN EVM Mock Report</h1><p class="badge">SIMULATED / 模擬資料</p>
<p>Run ID: {run_id}</p><table id="results"></table>
<script>const rows={encoded};const keys=['point_index','frequency_hz','evm_all_db','burst_power_dbm','frequency_error_hz','limit_status'];
document.querySelector('#results').innerHTML='<tr>'+keys.map(k=>`<th>${{k}}</th>`).join('')+'</tr>'+rows.map(r=>'<tr>'+keys.map(k=>`<td>${{r[k]}}</td>`).join('')+'</tr>').join('');</script></html>"""
