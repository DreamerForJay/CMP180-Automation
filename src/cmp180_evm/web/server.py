"""Dependency-free local HTTP server for the responsive CMP180 GUI."""

from __future__ import annotations

import argparse
import json
import mimetypes
from datetime import datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from cmp180_evm.web.jobs import JobManager
from cmp180_evm.web.mock_service import (
    DEMO_LIMIT_PROFILE,
    build_frequency_points,
    build_power_points,
    save_mock_run,
    simulate_point,
)

STATIC_DIR = Path(__file__).with_name("static")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
VERIFIED_CABLE_ROUTE = "RF1.1-RF1.5"
LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}
JOB_MANAGER = JobManager()


def list_run_history(output_root: Path, limit: int = 50) -> list[dict[str, object]]:
    """Return safe, newest-first summaries for locally saved measurement runs."""
    bounded_limit = max(1, min(limit, 200))
    if not output_root.is_dir():
        return []
    runs: list[dict[str, object]] = []
    for metadata_path in output_root.glob("*/metadata.json"):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if not isinstance(metadata, dict):
                continue
            run_dir = metadata_path.parent
            # 歷史 API 僅回傳白名單欄位與 output/ 相對 URL，避免洩漏本機路徑或原始 SCPI。
            artifacts = {
                name: f"/artifacts/{run_dir.name}/{filename}"
                for name, filename in {
                    "csv": "results.csv",
                    "json": "results.json",
                    "metadata": "metadata.json",
                    "report": "report.html",
                }.items()
                if (run_dir / filename).is_file()
            }
            created_at = str(metadata.get("created_at") or "")
            # 無效時間保留顯示，但排序降到最後；單一損壞 run 不應讓整頁失效。
            try:
                sort_time = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()
            except ValueError:
                sort_time = 0.0
            runs.append(
                {
                    "run_id": str(metadata.get("run_id") or run_dir.name),
                    "test_name": str(metadata.get("test_name") or "measurement"),
                    "created_at": created_at,
                    "simulated": bool(metadata.get("simulated", True)),
                    "status": str(metadata.get("status") or "complete"),
                    "completed_points": int(metadata.get("completed_points") or 0),
                    "source": str(metadata.get("source") or "unknown"),
                    "artifact_urls": artifacts,
                    "_sort_time": sort_time,
                }
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            continue
    runs.sort(key=lambda item: float(item.pop("_sort_time")), reverse=True)
    return runs[:bounded_limit]


def validate_cable_route(value: object) -> str:
    """Normalize a user-entered route and allow only hardware-verified wiring."""
    normalized = str(value or "").strip().upper().replace("→", "-").replace(" ", "")
    if not normalized:
        raise ValueError("Select or enter a cable route")
    # 自訂文字可供介面輸入，但未完成 routing／功率安全驗證前不得開啟 RF。
    if normalized != VERIFIED_CABLE_ROUTE:
        raise ValueError(
            f"Cable route {normalized!r} is not hardware-verified; RF output is blocked"
        )
    return normalized


def validate_hardware_bind(host: str, hardware_enabled: bool) -> None:
    """Prevent the unauthenticated hardware endpoint from leaving loopback."""
    # 目前 Web 尚未有登入與角色權限；實機 RF 控制只能供本機操作員使用。
    if hardware_enabled and host.strip().lower() not in LOOPBACK_HOSTS:
        raise ValueError(
            "Hardware mode may bind only to loopback until authentication is implemented"
        )


class Cmp180WebHandler(SimpleHTTPRequestHandler):
    """Serve static GUI assets and explicitly scoped mock endpoints."""

    hardware_enabled = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def _json_response(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 64_000:
            raise ValueError("Invalid request body size")
        value = json.loads(self.rfile.read(length))
        if not isinstance(value, dict):
            raise ValueError("JSON body must be an object")
        return value

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        parsed_path = parsed.path
        if parsed_path == "/api/runs":
            self._json_response({"runs": list_run_history(PROJECT_ROOT / "output")})
            return
        if parsed_path.startswith("/api/jobs/"):
            job_id = parsed_path.removeprefix("/api/jobs/")
            try:
                payload = JOB_MANAGER.get(job_id).public()
                result = payload.get("result")
                if isinstance(result, dict) and isinstance(result.get("artifacts"), dict):
                    # 只回傳 output/ 下的受控 URL，不把本機絕對路徑當成瀏覽器連結。
                    result["artifact_urls"] = self._artifact_urls(result["artifacts"])
                    if result.get("simulated") is True:
                        result["limit_profile"] = DEMO_LIMIT_PROFILE.snapshot()
                        result["compliance_claim"] = False
                self._json_response(payload)
            except KeyError as exc:
                self._json_response({"error": str(exc)}, HTTPStatus.NOT_FOUND)
            return
        if parsed_path == "/api/status":
            self._json_response(
                {
                    "app": "CMP180 WLAN EVM Automation",
                    "mode": "mock",
                    "hardware_enabled": self.hardware_enabled,
                    "capability": "mock-single-frequency-sweep-and-power-sweep",
                }
            )
            return
        if parsed_path.startswith("/artifacts/"):
            relative = Path(unquote(parsed_path.removeprefix("/artifacts/")))
            output_root = (PROJECT_ROOT / "output").resolve()
            candidate = (output_root / relative).resolve()
            # 僅允許 output/ 內檔案，阻止 ../ 讀取專案或系統其他路徑。
            if output_root not in candidate.parents or not candidate.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            body = candidate.read_bytes()
            self.send_response(HTTPStatus.OK)
            content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
            self.send_header(
                "Content-Type",
                content_type,
            )
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Content-Disposition", f'inline; filename="{candidate.name}"')
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    @staticmethod
    def _artifact_urls(artifacts: dict[str, str]) -> dict[str, str]:
        run_name = Path(artifacts["run_dir"]).name
        run_dir = Path(artifacts["run_dir"])
        return {
            key: f"/artifacts/{run_name}/{Path(path).relative_to(run_dir).as_posix()}"
            for key, path in artifacts.items()
            if key not in {"run_id", "run_dir"} and Path(path).is_file()
        }

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            if path.startswith("/api/jobs/") and path.endswith("/cancel"):
                job_id = path.removeprefix("/api/jobs/").removesuffix("/cancel")
                self._json_response(JOB_MANAGER.cancel(job_id).public())
                return
            data = self._read_json()
            if path in {"/api/jobs/hardware/frequency-sweep", "/api/jobs/hardware/power-sweep"}:
                if not self.hardware_enabled:
                    self._json_response({"error": "Hardware mode is locked"}, HTTPStatus.FORBIDDEN)
                    return
                validate_cable_route(data.get("cable_confirmation"))
                if data.get("operator_present") is not True:
                    raise ValueError("Operator presence confirmation is required")
                axis = "frequency" if "frequency" in path else "power"
                expected_confirmation = "6085-6125MHz" if axis == "frequency" else "-55--40dBm"
                if data.get("sweep_confirmation") != expected_confirmation:
                    raise ValueError("Fixed hardware sweep profile confirmation is required")
                from cmp180_evm.web.real_service import run_verified_real_sweep

                total_points = 3 if axis == "frequency" else 4
                job = JOB_MANAGER.start(
                    f"hardware-{axis}-sweep",
                    total_points,
                    lambda active_job: run_verified_real_sweep(
                        active_job, axis=axis, output_root=PROJECT_ROOT / "output"
                    ),
                )
                self._json_response(job.public(), HTTPStatus.ACCEPTED)
                return
            # 決定結果圖表 X 軸：頻率或功率掃描才不是 "frequency"（單點沿用預設）。
            sweep_axis = "frequency"
            if path == "/api/mock/single":
                points = [
                    simulate_point(
                        float(data["frequency_hz"]),
                        float(data["bandwidth_hz"]),
                        float(data["generator_power_dbm"]),
                    )
                ]
                artifacts = save_mock_run(
                    points, PROJECT_ROOT / "output", str(data.get("test_name", "mock-single"))
                )
            elif path in {"/api/mock/sweep", "/api/jobs/mock/frequency-sweep"}:
                frequencies = build_frequency_points(
                    float(data["start_hz"]),
                    float(data["stop_hz"]),
                    float(data["step_hz"]),
                )
                points = [
                    simulate_point(
                        frequency,
                        float(data["bandwidth_hz"]),
                        float(data["generator_power_dbm"]),
                        index,
                    )
                    for index, frequency in enumerate(frequencies)
                ]
                if path.startswith("/api/jobs/"):
                    job = JOB_MANAGER.start(
                        "mock-frequency-sweep",
                        len(points),
                        lambda active_job: JobManager.run_mock_points(
                            active_job,
                            points,
                            lambda captured: save_mock_run(
                                captured,
                                PROJECT_ROOT / "output",
                                str(data.get("test_name", "mock-sweep")),
                            ),
                            float(data.get("dwell_ms", 100)) / 1000,
                        ),
                    )
                    self._json_response(job.public(), HTTPStatus.ACCEPTED)
                    return
                artifacts = save_mock_run(
                    points,
                    PROJECT_ROOT / "output",
                    str(data.get("test_name", "mock-sweep")),
                )
            elif path in {"/api/mock/power-sweep", "/api/jobs/mock/power-sweep"}:
                sweep_axis = "power"
                powers = build_power_points(
                    float(data["start_dbm"]),
                    float(data["stop_dbm"]),
                    float(data["step_dbm"]),
                )
                points = [
                    simulate_point(
                        float(data["frequency_hz"]),
                        float(data["bandwidth_hz"]),
                        power_dbm,
                        index,
                    )
                    for index, power_dbm in enumerate(powers)
                ]
                if path.startswith("/api/jobs/"):
                    job = JOB_MANAGER.start(
                        "mock-power-sweep",
                        len(points),
                        lambda active_job: JobManager.run_mock_points(
                            active_job,
                            points,
                            lambda captured: save_mock_run(
                                captured,
                                PROJECT_ROOT / "output",
                                str(data.get("test_name", "mock-power-sweep")),
                            ),
                            float(data.get("dwell_ms", 100)) / 1000,
                        ),
                    )
                    self._json_response(job.public(), HTTPStatus.ACCEPTED)
                    return
                artifacts = save_mock_run(
                    points,
                    PROJECT_ROOT / "output",
                    str(data.get("test_name", "mock-power-sweep")),
                )
            elif path == "/api/hardware/single":
                if not self.hardware_enabled:
                    self._json_response(
                        {"error": "Hardware mode is locked at server startup"},
                        HTTPStatus.FORBIDDEN,
                    )
                    return
                validate_cable_route(data.get("cable_confirmation"))
                if data.get("operator_present") is not True:
                    self._json_response(
                        {"error": "Operator presence confirmation is required"},
                        HTTPStatus.BAD_REQUEST,
                    )
                    return
                # 延遲 import，Mock-only server 不載入或接觸硬體套件。
                from cmp180_evm.web.real_service import run_verified_real_single

                payload = run_verified_real_single(output_root=PROJECT_ROOT / "output")
                payload["artifact_urls"] = self._artifact_urls(payload["artifacts"])
                self._json_response(payload)
                return
            else:
                self._json_response({"error": "Not found"}, HTTPStatus.NOT_FOUND)
                return
        except (KeyError, TypeError, ValueError, OSError) as exc:
            self._json_response({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:
            # 實機錯誤回傳一般化訊息；完整細節保留在本機 server log。
            self.log_error("Hardware request failed: %s", exc)
            self._json_response(
                {"error": f"Hardware measurement failed: {type(exc).__name__}: {exc}"},
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            return

        # API 明確標示 simulated，避免 Mock 結果被誤認成實機量測。
        self._json_response(
            {
                "simulated": True,
                "limit_profile": DEMO_LIMIT_PROFILE.snapshot(),
                "compliance_claim": False,
                "sweep_axis": sweep_axis,
                "points": [point.__dict__ for point in points],
                "artifacts": artifacts,
                "artifact_urls": self._artifact_urls(artifacts),
            }
        )

    def log_message(self, format: str, *args: object) -> None:
        # 保留簡潔的 HTTP audit log，不輸出 request body 或公司敏感資料。
        super().log_message(format, *args)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--enable-hardware",
        action="store_true",
        help="Enable the guarded fixed-profile real SingleShot endpoint.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validate_hardware_bind(args.host, args.enable_hardware)
    Cmp180WebHandler.hardware_enabled = args.enable_hardware
    server = ThreadingHTTPServer((args.host, args.port), Cmp180WebHandler)
    print(f"CMP180 Web GUI: http://{args.host}:{args.port}")
    print(
        "Mode: hardware endpoint enabled (guarded)."
        if args.enable_hardware
        else "Mode: MOCK only; real-hardware controls are locked."
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
