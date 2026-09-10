"""Deterministic mock measurements and offline run artifacts."""

from __future__ import annotations

import csv
import json
import math
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from cmp180_evm.limits import DRAFT_LOOPBACK_LIMIT_PROFILE, evaluate_limits
from cmp180_evm.results.visualization import write_pandas_matplotlib_plots

MAXIMUM_DEMO_SWEEP_POINTS = 1001
# Profile 現在集中定義於 cmp180_evm.limits，實機與模擬共用；此處僅保留既有匯入名稱。
DEMO_LIMIT_PROFILE = DRAFT_LOOPBACK_LIMIT_PROFILE


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
    pin_dbm: float
    pout_dbm: float
    gain_db: float
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
    # Demo 不套用 RF 安全掃描限制；此上限只避免瀏覽器或 CSV 產生過大的模擬資料。
    if count > MAXIMUM_DEMO_SWEEP_POINTS:
        raise ValueError(f"Sweep exceeds the {MAXIMUM_DEMO_SWEEP_POINTS}-point GUI limit")
    return [start_hz + index * step_hz for index in range(count)]


def build_power_points(
    start_dbm: float,
    stop_dbm: float,
    step_dbm: float,
) -> list[float]:
    """Build an inclusive power-level list without floating-point accumulation."""
    if step_dbm <= 0 or stop_dbm < start_dbm:
        raise ValueError("Invalid power range or step")
    count = int(math.floor((stop_dbm - start_dbm) / step_dbm)) + 1
    # Demo 不套用 RF 安全掃描限制；此上限只避免瀏覽器或 CSV 產生過大的模擬資料。
    if count > MAXIMUM_DEMO_SWEEP_POINTS:
        raise ValueError(f"Sweep exceeds the {MAXIMUM_DEMO_SWEEP_POINTS}-point GUI limit")
    return [start_dbm + index * step_dbm for index in range(count)]


def simulate_point(
    frequency_hz: float,
    bandwidth_hz: float,
    generator_power_dbm: float,
    point_index: int = 0,
) -> MockPoint:
    """Return stable simulated values; never represent them as hardware data."""
    # 使用固定公式而非亂數，讓測試、CSV 與圖表每次都能重現。
    phase = frequency_hz / 100_000_000.0
    # Demo PA model 只用來產生可教學的 Gain compression/P1dB 曲線，不代表實機 DUT。
    pin_dbm = generator_power_dbm
    compression_db = max(0.0, (pin_dbm + 10.0) * 0.2)
    gain_db = 20.0 - compression_db
    pout_dbm = pin_dbm + gain_db
    # 示範用 EVM 隨功率提高而變差；不使用 -40 dBm 安全上限概念。
    evm_all = -36.0 + 1.8 * math.sin(phase) + 0.04 * (generator_power_dbm + 60.0)
    evm_data = evm_all + 0.35
    evm_pilot = evm_all - 0.55
    burst_power = generator_power_dbm - 0.45 + 0.12 * math.cos(phase)
    frequency_error = 7.5 * math.sin(phase * 0.7)
    clock_error = 0.18 * math.cos(phase * 0.4)
    limit_result = evaluate_limits(
        DEMO_LIMIT_PROFILE,
        evm_db=evm_all,
        frequency_error_hz=frequency_error,
        measured_power_dbm=burst_power,
        expected_power_dbm=generator_power_dbm,
    )
    return MockPoint(
        point_index=point_index,
        frequency_hz=frequency_hz,
        bandwidth_hz=bandwidth_hz,
        generator_power_dbm=generator_power_dbm,
        evm_all_db=round(evm_all, 4),
        evm_data_db=round(evm_data, 4),
        evm_pilot_db=round(evm_pilot, 4),
        burst_power_dbm=round(burst_power, 4),
        pin_dbm=round(pin_dbm, 4),
        pout_dbm=round(pout_dbm, 4),
        gain_db=round(gain_db, 4),
        frequency_error_hz=round(frequency_error, 4),
        clock_error_ppm=round(clock_error, 6),
        valid=True,
        limit_status=limit_result.overall_status,
    )


def analyze_mock_p1db(points: list[MockPoint]) -> dict[str, object]:
    rows = [asdict(point) for point in points]
    valid = [
        point
        for point in rows
        if point.get("valid") is True
        and isinstance(point.get("pin_dbm"), (int, float))
        and isinstance(point.get("pout_dbm"), (int, float))
        and isinstance(point.get("gain_db"), (int, float))
    ]
    valid.sort(key=lambda point: float(point["pin_dbm"]))
    if len(valid) < 2:
        return {"status": "insufficient_points", "small_signal_gain_db": None}
    baseline_count = max(1, min(3, len(valid)))
    # 低 Pin 前三點作為小訊號增益，讓 demo P1dB 與實機 GPRF 分析規則一致。
    small_signal_gain = sum(float(point["gain_db"]) for point in valid[:baseline_count]) / baseline_count
    target_gain = small_signal_gain - 1.0
    max_pin_point = max(valid, key=lambda point: float(point["pin_dbm"]))
    max_compression = max(small_signal_gain - float(point["gain_db"]) for point in valid)
    previous = valid[0]
    for point in valid[1:]:
        previous_gain = float(previous["gain_db"])
        current_gain = float(point["gain_db"])
        if previous_gain >= target_gain >= current_gain:
            span = previous_gain - current_gain
            ratio = 0.0 if span == 0 else (previous_gain - target_gain) / span
            pin = float(previous["pin_dbm"]) + ratio * (
                float(point["pin_dbm"]) - float(previous["pin_dbm"])
            )
            pout = float(previous["pout_dbm"]) + ratio * (
                float(point["pout_dbm"]) - float(previous["pout_dbm"])
            )
            return {
                "status": "found",
                "small_signal_gain_db": small_signal_gain,
                "target_gain_db": target_gain,
                "ip1db_dbm": pin,
                "op1db_dbm": pout,
                "max_compression_db": max_compression,
                "max_measured_pin_dbm": float(max_pin_point["pin_dbm"]),
                "max_measured_pout_dbm": float(max_pin_point["pout_dbm"]),
            }
        previous = point
    return {
        "status": "not_found",
        "small_signal_gain_db": small_signal_gain,
        "target_gain_db": target_gain,
        "max_compression_db": max_compression,
        "max_measured_pin_dbm": float(max_pin_point["pin_dbm"]),
        "max_measured_pout_dbm": float(max_pin_point["pout_dbm"]),
    }


def simulate_advanced_pa(
    frequency_hz: float,
    input_power_dbm: float,
    tone_spacing_hz: float,
    channel_bandwidth_hz: float,
) -> dict[str, object]:
    """Build deterministic OIP3, harmonic, and adjacent-channel demo data."""
    if frequency_hz <= 0 or tone_spacing_hz <= 0 or channel_bandwidth_hz <= 0:
        raise ValueError("Frequency, tone spacing, and channel bandwidth must be positive")

    # 這些係數只建立可重現的教學頻譜，不代表任何實機 DUT 規格或量測結果。
    compression_db = max(0.0, (input_power_dbm + 10.0) * 0.2)
    gain_db = 20.0 - compression_db
    tone_output_dbm = input_power_dbm + gain_db - 3.0
    oip3_dbm = 35.0 - max(0.0, compression_db - 1.0) * 0.5
    im3_dbm = 3.0 * tone_output_dbm - 2.0 * oip3_dbm
    im3_dbc = tone_output_dbm - im3_dbm
    harmonic_fundamental_dbm = input_power_dbm + gain_db
    h2_dbc = 32.0 - min(compression_db, 8.0) * 0.5
    h3_dbc = 45.0 - min(compression_db, 8.0) * 0.8
    aclr_lower_db = 36.0 - min(compression_db, 8.0) * 1.2
    aclr_upper_db = aclr_lower_db - 0.8
    channel_power_dbm = harmonic_fundamental_dbm

    # 雙音 IM3 位於兩個 tone 外側各一個 tone spacing；頻率欄位統一使用 Hz。
    half_spacing = tone_spacing_hz / 2.0
    two_tone = [
        {"frequency_hz": frequency_hz - 1.5 * tone_spacing_hz, "power_dbm": im3_dbm, "label": "IM3 lower"},
        {"frequency_hz": frequency_hz - half_spacing, "power_dbm": tone_output_dbm, "label": "Tone 1"},
        {"frequency_hz": frequency_hz + half_spacing, "power_dbm": tone_output_dbm, "label": "Tone 2"},
        {"frequency_hz": frequency_hz + 1.5 * tone_spacing_hz, "power_dbm": im3_dbm - 0.6, "label": "IM3 upper"},
    ]
    harmonics = [
        {"order": 1, "frequency_hz": frequency_hz, "power_dbm": harmonic_fundamental_dbm, "relative_dbc": 0.0},
        {"order": 2, "frequency_hz": frequency_hz * 2.0, "power_dbm": harmonic_fundamental_dbm - h2_dbc, "relative_dbc": -h2_dbc},
        {"order": 3, "frequency_hz": frequency_hz * 3.0, "power_dbm": harmonic_fundamental_dbm - h3_dbc, "relative_dbc": -h3_dbc},
    ]
    acp_channels = [
        {"channel": "Lower adjacent", "offset_hz": -channel_bandwidth_hz, "power_dbm": channel_power_dbm - aclr_lower_db},
        {"channel": "Main", "offset_hz": 0.0, "power_dbm": channel_power_dbm},
        {"channel": "Upper adjacent", "offset_hz": channel_bandwidth_hz, "power_dbm": channel_power_dbm - aclr_upper_db},
    ]
    return {
        "simulated": True,
        "measurement_family": "PA_ADVANCED_DEMO",
        "inputs": {
            "frequency_hz": frequency_hz,
            "input_power_dbm": input_power_dbm,
            "tone_spacing_hz": tone_spacing_hz,
            "channel_bandwidth_hz": channel_bandwidth_hz,
        },
        "metrics": {
            "gain_db": round(gain_db, 3),
            "tone_output_dbm": round(tone_output_dbm, 3),
            "oip3_dbm": round(oip3_dbm, 3),
            "im3_dbm": round(im3_dbm, 3),
            "im3_dbc": round(im3_dbc, 3),
            "h2_dbc": round(h2_dbc, 3),
            "h3_dbc": round(h3_dbc, 3),
            "acp_lower_dbm": round(channel_power_dbm - aclr_lower_db, 3),
            "acp_upper_dbm": round(channel_power_dbm - aclr_upper_db, 3),
            "aclr_lower_db": round(aclr_lower_db, 3),
            "aclr_upper_db": round(aclr_upper_db, 3),
        },
        "two_tone": two_tone,
        "harmonics": harmonics,
        "acp_channels": acp_channels,
    }


def save_advanced_pa_run(
    result: dict[str, object], output_root: Path, test_name: str
) -> dict[str, str]:
    """Persist an advanced PA demo as JSON, CSV, metadata, and HTML."""
    now = datetime.now(UTC)
    run_id = uuid.uuid4().hex[:10]
    safe_name = "".join(char if char.isalnum() or char in "-_" else "_" for char in test_name)
    run_dir = output_root / f"{now.strftime('%Y%m%dT%H%M%SZ')}_{safe_name or 'pa-advanced'}_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=False)
    payload = {**result, "run_id": run_id, "created_at": now.isoformat()}

    rows: list[dict[str, object]] = []
    for point in cast(list[dict[str, object]], result["two_tone"]):
        rows.append({"measurement": "OIP3", **point})
    for point in cast(list[dict[str, object]], result["harmonics"]):
        rows.append({"measurement": "HARMONIC", **point})
    for point in cast(list[dict[str, object]], result["acp_channels"]):
        rows.append({"measurement": "ACP", **point})
    fieldnames = sorted({key for row in rows for key in row})
    csv_path = run_dir / "results.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    json_path = run_dir / "results.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    metadata_path = run_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "test_name": test_name,
                "created_at": now.isoformat(),
                "status": "complete",
                "simulated": True,
                "source": "web-demo-pa-advanced",
                "measurement_family": "PA_ADVANCED_DEMO",
                "point_count": len(rows),
                "completed_points": len(rows),
                "compliance_claim": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    report_path = run_dir / "report.html"
    encoded = json.dumps(payload).replace("</", "<\\/")
    report_path.write_text(
        f"""<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>PA Advanced Demo</title>
<style>body{{font:15px system-ui;margin:32px;color:#172033}}pre{{padding:18px;background:#f3f6fa;overflow:auto}}.badge{{background:#fff3cd;padding:8px 12px}}</style>
<h1>PA 進階指標示範</h1><p class="badge">SIMULATED / 模擬資料，不代表實機 DUT</p><pre id="result"></pre>
<script>document.querySelector('#result').textContent=JSON.stringify({encoded},null,2)</script></html>""",
        encoding="utf-8",
    )
    return {
        "run_id": run_id,
        "run_dir": str(run_dir.resolve()),
        "csv": str(csv_path.resolve()),
        "json": str(json_path.resolve()),
        "report": str(report_path.resolve()),
    }


def save_mock_run(
    points: list[MockPoint],
    output_root: Path,
    test_name: str,
) -> dict[str, str]:
    """Persist normalized mock CSV/JSON and a self-contained HTML report."""
    now = datetime.now(UTC)
    run_id = uuid.uuid4().hex[:10]
    safe_name = "".join(char if char.isalnum() or char in "-_" else "_" for char in test_name)
    run_dir = output_root / f"{now.strftime('%Y%m%dT%H%M%SZ')}_{safe_name}_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=False)
    rows = [asdict(point) for point in points]
    p1db = analyze_mock_p1db(points)

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
                "p1db": p1db,
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
                "created_at": now.isoformat(),
                "status": "complete",
                "simulated": True,
                "point_count": len(points),
                "completed_points": len(points),
                "source": "web-demo",
                "limit_profile": DEMO_LIMIT_PROFILE.snapshot(),
                "compliance_claim": False,
                "p1db": p1db,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    report_path = run_dir / "report.html"
    report_path.write_text(_build_html_report(run_id, rows), encoding="utf-8")
    # Web Demo 也從保存後的 CSV 產生正式 PNG，確保示範與實機走同一條報告鏈。
    matplotlib_artifacts = {
        f"matplotlib_{path.stem}": str(path.resolve())
        for path in write_pandas_matplotlib_plots(csv_path)
    }
    return {
        "run_id": run_id,
        "run_dir": str(run_dir.resolve()),
        "csv": str(csv_path.resolve()),
        "json": str(json_path.resolve()),
        "report": str(report_path.resolve()),
        **matplotlib_artifacts,
    }


def _build_html_report(run_id: str, rows: list[dict[str, object]]) -> str:
    encoded = json.dumps(rows).replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="zh-Hant"><meta charset="utf-8"><title>CMP180 Mock Report</title>
<style>
body{{font:15px system-ui;margin:32px;color:#172033}}
table{{border-collapse:collapse;width:100%}}
th,td{{padding:8px;border-bottom:1px solid #ddd;text-align:right}}
th:first-child,td:first-child{{text-align:left}}
.badge{{background:#fff3cd;padding:8px 12px;border-radius:8px}}</style>
<h1>CMP180 WLAN EVM Mock Report</h1><p class="badge">SIMULATED / 模擬資料</p>
<p class="badge">DRAFT LIMITS / 非正式限制，不代表 DUT compliance</p>
<p>Run ID: {run_id}</p><table id="results"></table>
<script>
const rows={encoded};
const keys=['point_index','frequency_hz','generator_power_dbm','pin_dbm','pout_dbm','gain_db','evm_all_db','burst_power_dbm',
  'frequency_error_hz','limit_status'];
document.querySelector('#results').innerHTML='<tr>'+
  keys.map(k=>`<th>${{k}}</th>`).join('')+'</tr>'+
  rows.map(r=>'<tr>'+keys.map(k=>`<td>${{r[k]}}</td>`).join('')+'</tr>').join('');
</script></html>"""
