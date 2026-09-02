"""GPRF power sweep support for instrument capability checks.

This module intentionally uses the CMP180 GPRF generator/measurement apps, not
the WLAN TX EVM workflow. Results are RF power observations and must not be
presented as WLAN demodulation or compliance data.
"""

from __future__ import annotations

import csv
import html
import json
import socket
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from cmp180_evm.scpi.registry import ScpiCommandRegistry, load_scpi_command_map
from cmp180_evm.web.jobs import SweepJob

GPRF_MIN_FREQUENCY_HZ = 400_000_000.0
GPRF_MAX_FREQUENCY_HZ = 8_000_000_000.0
GPRF_MIN_POWER_DBM = -80.0
GPRF_MAX_POWER_DBM = 20.0
GPRF_MAX_POINTS = 401
GPRF_MIN_DWELL_MS = 50
GPRF_MAX_DWELL_MS = 5000


@dataclass(frozen=True)
class GprfPreview:
    axis: str
    points: tuple[float, ...]
    frequency_hz: float | None
    power_dbm: float | None
    dwell_ms: int
    execution_allowed: bool
    rejection_reason: str | None = None

    def public(self) -> dict[str, object]:
        return {
            "measurement_family": "GPRF_POWER",
            "axis": self.axis,
            "points": self.points,
            "point_count": len(self.points),
            "frequency_hz": self.frequency_hz,
            "power_dbm": self.power_dbm,
            "dwell_ms": self.dwell_ms,
            "execution_allowed": self.execution_allowed,
            "rejection_reason": self.rejection_reason,
            "disclaimer": (
                "GPRF power sweep only; this is not WLAN EVM demodulation or a "
                "WLAN compliance claim."
            ),
        }


def _inclusive_points(start: float, stop: float, step: float) -> tuple[float, ...]:
    if step <= 0 or stop < start:
        raise ValueError("Stop must follow start and step must be positive")
    count = int((stop - start) // step) + 1
    if count > GPRF_MAX_POINTS:
        raise ValueError(f"GPRF preview exceeds {GPRF_MAX_POINTS} points")
    return tuple(round(start + index * step, 9) for index in range(count))


def build_gprf_power_preview(data: dict[str, object]) -> GprfPreview:
    axis = str(data.get("axis") or "frequency")
    dwell_ms = int(float(data.get("dwell_ms", 200)))
    if not GPRF_MIN_DWELL_MS <= dwell_ms <= GPRF_MAX_DWELL_MS:
        raise ValueError(f"GPRF dwell must stay within {GPRF_MIN_DWELL_MS}..{GPRF_MAX_DWELL_MS} ms")
    if axis == "frequency":
        start_hz = float(data["start_hz"])
        stop_hz = float(data["stop_hz"])
        step_hz = float(data["step_hz"])
        power_dbm = float(data.get("power_dbm", -40.0))
        points = _inclusive_points(start_hz, stop_hz, step_hz)
        reason = None
        if min(points) < GPRF_MIN_FREQUENCY_HZ or max(points) > GPRF_MAX_FREQUENCY_HZ:
            reason = "Frequency exceeds CMP180 GPRF planning range 400 MHz..8 GHz"
        elif not GPRF_MIN_POWER_DBM <= power_dbm <= GPRF_MAX_POWER_DBM:
            reason = (
                f"Generator power must stay within {GPRF_MIN_POWER_DBM:g}.."
                f"{GPRF_MAX_POWER_DBM:g} dBm"
            )
        return GprfPreview(axis, points, None, power_dbm, dwell_ms, reason is None, reason)
    if axis == "power":
        frequency_hz = float(data["frequency_hz"])
        start_dbm = float(data["start_dbm"])
        stop_dbm = float(data["stop_dbm"])
        step_dbm = float(data["step_dbm"])
        points = _inclusive_points(start_dbm, stop_dbm, step_dbm)
        reason = None
        if not GPRF_MIN_FREQUENCY_HZ <= frequency_hz <= GPRF_MAX_FREQUENCY_HZ:
            reason = "Frequency exceeds CMP180 GPRF planning range 400 MHz..8 GHz"
        elif min(points) < GPRF_MIN_POWER_DBM or max(points) > GPRF_MAX_POWER_DBM:
            reason = (
                f"Power sweep exceeds {GPRF_MIN_POWER_DBM:g}.."
                f"{GPRF_MAX_POWER_DBM:g} dBm planning range"
            )
        return GprfPreview(axis, points, frequency_hz, None, dwell_ms, reason is None, reason)
    raise ValueError("GPRF axis must be 'frequency' or 'power'")


class GprfSocket:
    def __init__(self, registry: ScpiCommandRegistry) -> None:
        self.registry = registry
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10.0)

    def connect(self) -> None:
        self.sock.connect(("192.168.200.50", 5025))

    def close(self) -> None:
        self.sock.close()

    def write(self, command: str) -> None:
        self.sock.sendall((command.strip() + "\n").encode("utf-8"))

    def query(self, command: str) -> str:
        self.write(command)
        chunks: list[bytes] = []
        while True:
            chunk = self.sock.recv(4096)
            chunks.append(chunk)
            if chunk.endswith(b"\n") or not chunk:
                break
        return b"".join(chunks).decode("utf-8", errors="ignore").strip()


def _drain_error_queue(conn: GprfSocket, registry: ScpiCommandRegistry, *, limit: int = 20) -> list[str]:
    """Read `SYST:ERR?` until the instrument reports an empty queue."""
    # SCPI error queue 必須讀到 `0,"No error"` 才算清空；設上限避免儀器異常時無限迴圈。
    entries: list[str] = []
    command = registry.require("common.system_error")
    for _ in range(limit):
        try:
            response = conn.query(command).strip()
        except Exception as exc:  # 讀取失敗本身就是證據，不可靜默吞掉
            entries.append(f"ERROR_QUEUE_READ_FAILED: {exc}")
            break
        if not response or response.startswith("0,"):
            break
        entries.append(response)
    return entries


def _parse_power(response: str) -> tuple[int, float | None]:
    try:
        parts = response.strip().split(",")
        reliability = int(float(parts[0]))
        value = float(parts[1]) if len(parts) > 1 else None
        return reliability, value
    except (IndexError, ValueError):
        return -1, None


def _save_gprf_result(
    points: list[dict[str, object]],
    output_root: Path,
    metadata: dict[str, object],
) -> dict[str, str]:
    now = datetime.now(UTC)
    run_id = uuid.uuid4().hex[:10]
    run_dir = output_root / f"{now.strftime('%Y%m%dT%H%M%SZ')}_gprf-power-sweep_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=False)
    csv_path = run_dir / "results.csv"
    fieldnames = list(points[0]) if points else ["point_index", "status"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(points)
    json_path = run_dir / "results.json"
    json_path.write_text(json.dumps(points, indent=2), encoding="utf-8")
    metadata_path = run_dir / "metadata.json"
    payload = {
        "run_id": run_id,
        "test_name": "gprf-power-sweep",
        "created_at": now.isoformat(),
        "simulated": False,
        "status": "complete",
        "source": "web_gprf_power_sweep",
        "measurement_family": "GPRF_POWER",
        "compliance_claim": False,
        **metadata,
    }
    metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    headers = "".join(f"<th>{html.escape(str(name))}</th>" for name in fieldnames)
    rows = "".join(
        "<tr>"
        + "".join(
            f"<td>{html.escape(str(row.get(name, '')))}</td>" for name in fieldnames
        )
        + "</tr>"
        for row in points
    )
    report_path = run_dir / "report.html"
    report_path.write_text(
        "<!doctype html><html lang='zh-Hant'><meta charset='utf-8'>"
        "<title>CMP180 GPRF Power Sweep</title>"
        "<style>body{font:14px system-ui;margin:32px;color:#172033}"
        "table{border-collapse:collapse;width:100%}"
        "th,td{padding:8px;border-bottom:1px solid #ddd;text-align:left}"
        "th{background:#f4f7fb}</style>"
        "<h1>CMP180 GPRF Power Sweep</h1>"
        "<p>GPRF power only; not WLAN EVM demodulation or compliance.</p>"
        f"<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>",
        encoding="utf-8",
    )
    return {
        "run_id": run_id,
        "run_dir": str(run_dir.resolve()),
        "csv": str(csv_path.resolve()),
        "json": str(json_path.resolve()),
        "metadata": str(metadata_path.resolve()),
        "report": str(report_path.resolve()),
    }


def run_gprf_power_sweep(
    job: SweepJob,
    *,
    request: dict[str, object],
    output_root: Path,
) -> dict[str, object]:
    preview = build_gprf_power_preview(request)
    if not preview.execution_allowed:
        raise ValueError(preview.rejection_reason or "GPRF plan is blocked")
    registry = load_scpi_command_map(Path("configs/scpi_command_map.yaml"))
    conn = GprfSocket(registry)
    rows: list[dict[str, object]] = []
    # 回傳 dict 持有同一個 list 參考，因此 finally 內補上的收尾錯誤仍會被呼叫端看到。
    cleanup_errors: list[str] = []
    try:
        conn.connect()
        conn.write(registry.require("common.clear_status"))
        # GPRF 模式會開真實 RF；每個設定點都在 job 邊界檢查取消，finally 仍會關 RF。
        for index, value in enumerate(preview.points):
            if job.is_cancel_requested():
                break
            frequency_hz = value if preview.axis == "frequency" else float(preview.frequency_hz)
            power_dbm = float(preview.power_dbm) if preview.axis == "frequency" else value
            conn.write(registry.render("generator.set_frequency", frequency_hz=frequency_hz))
            conn.write(registry.render("gprf_measurement.set_frequency", frequency_hz=frequency_hz))
            conn.write(registry.render("generator.set_power", power_dbm=power_dbm))
            conn.write(registry.require("generator.rf_on"))
            time.sleep(preview.dwell_ms / 1000)
            conn.write(registry.require("gprf_measurement.initiate_power"))
            time.sleep(preview.dwell_ms / 1000)
            raw = conn.query(registry.require("gprf_measurement_query.power_current"))
            reliability, measured = _parse_power(raw)
            # 每點都讀 error queue：儀器已回報錯誤時不得標記為有效量測，避免假 PASS。
            point_errors = _drain_error_queue(conn, registry)
            if point_errors:
                status = "SCPI_ERROR"
            elif reliability != 0:
                status = f"RELIABILITY_{reliability}"
            else:
                status = "OK"
            valid = reliability == 0 and measured is not None and not point_errors
            row = {
                "point_index": index,
                "frequency_hz": frequency_hz,
                "generator_power_dbm": power_dbm,
                "measured_power_dbm": measured,
                "evm_all_db": None,
                "evm_data_db": None,
                "evm_pilot_db": None,
                "burst_power_dbm": measured,
                "frequency_error_hz": None,
                "valid": valid,
                "limit_status": "MEASURED" if valid else "INVALID",
                "reliability": reliability,
                "raw_power_current": raw,
                "error_queue": "; ".join(point_errors),
                "status": status,
                "measurement_family": "GPRF_POWER",
            }
            rows.append(row)
            job.point_completed(index + 1, row)
        artifacts = _save_gprf_result(
            rows,
            output_root,
            {
                "axis": preview.axis,
                "requested_points": preview.points,
                "dwell_ms": preview.dwell_ms,
            },
        )
        return {
            "simulated": False,
            "sweep_axis": preview.axis,
            "measurement_family": "GPRF_POWER",
            "points": rows,
            "artifacts": artifacts,
            "cleanup_errors": cleanup_errors,
            "compliance_claim": False,
        }
    finally:
        # GPRF cleanup 只碰 GPRF power lifecycle 與 generator RF state，不碰 WLAN state tree。
        try:
            conn.write(registry.require("gprf_measurement.stop_power"))
        except Exception:
            pass
        try:
            conn.write(registry.require("generator.rf_off"))
        finally:
            # 收尾後再讀一次 error queue 留存證據；讀取失敗不得遮蔽原始錯誤，也不得跳過 close。
            try:
                cleanup_errors.extend(_drain_error_queue(conn, registry))
            except Exception:
                pass
            conn.close()
