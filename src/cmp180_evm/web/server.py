"""Dependency-free local HTTP server for the responsive CMP180 GUI."""

from __future__ import annotations

import argparse
import ipaddress
import json
import mimetypes
import socket
from dataclasses import asdict
from datetime import date, datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from cmp180_evm.calibration import load_calibration_profile
from cmp180_evm.calibration_adapters import (
    capture_calibration_readings,
    create_calibration_adapter,
    list_calibration_adapters,
)
from cmp180_evm.calibration_workflow import CalibrationReading, build_draft_profile
from cmp180_evm.loopback import loopback_batch_requests, select_loopback_profile
from cmp180_evm.web.capabilities import load_capability_profile
from cmp180_evm.web.custom_plans import (
    build_custom_single_preview,
    build_custom_sweep_preview,
)
from cmp180_evm.web.gprf_service import build_gprf_power_preview
from cmp180_evm.web.hil_campaign import HilCampaignStore
from cmp180_evm.web.jobs import JobManager
from cmp180_evm.web.mock_service import (
    DEMO_LIMIT_PROFILE,
    analyze_mock_p1db,
    build_frequency_points,
    build_power_points,
    save_mock_run,
    simulate_point,
)
from cmp180_evm.web.run_records import load_run_record, move_run_to_trash, open_run_folder
from cmp180_evm.workflow.rf_routes import validate_route

# 原版橫向量測工作區已由操作員確認較符合實驗室流程；新版分析能力回填此介面。
STATIC_DIR = Path(__file__).with_name("static")
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DIAGRAM_ROUTES = {
    "/diagrams/system-architecture.html": (
        PROJECT_ROOT / "docs" / "diagrams" / "system-architecture.html"
    ),
    "/diagrams/single-measurement-lifecycle.html": (
        PROJECT_ROOT / "docs" / "diagrams" / "single-measurement-lifecycle.html"
    ),
}
LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}
JOB_MANAGER = JobManager()
CAPABILITY_PROFILE_PATH = PROJECT_ROOT / "configs" / "instrument_capabilities.example.yaml"
HIL_CAMPAIGN = HilCampaignStore(PROJECT_ROOT / "output" / "hil-campaign" / "state.json")


class ExclusiveThreadingHTTPServer(ThreadingHTTPServer):
    """Reject a second local server instead of splitting requests across stale versions."""

    allow_reuse_address = False

    def server_bind(self) -> None:
        # Windows 的 SO_REUSEADDR 可能讓多個開發 server 同時監聽同一 port；使用 exclusive
        # bind，啟動第二份時立即失敗，避免新版靜態頁打到舊版 API。
        exclusive = getattr(socket, "SO_EXCLUSIVEADDRUSE", None)
        if exclusive is not None:
            self.socket.setsockopt(socket.SOL_SOCKET, exclusive, 1)
        super().server_bind()


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
            # Matplotlib PNG 是 results.csv 的衍生證據；存在時一併列入歷史 Run，不重新量測。
            plot_dir = run_dir / "plots-matplotlib"
            if plot_dir.is_dir():
                artifacts.update(
                    {
                        f"matplotlib_{path.stem}": (
                            f"/artifacts/{run_dir.name}/plots-matplotlib/{path.name}"
                        )
                        for path in sorted(plot_dir.glob("*.png"))
                    }
                )
            created_at = str(metadata.get("created_at") or "")
            if not created_at and (run_dir / "results.json").is_file():
                # 舊版 Demo metadata 未保存時間；只讀 results.json 補回排序，不修改歷史 artifact。
                legacy_results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
                if isinstance(legacy_results, dict):
                    created_at = str(legacy_results.get("created_at") or "")
            # 無效時間保留顯示，但排序降到最後；單一損壞 run 不應讓整頁失效。
            try:
                sort_time = datetime.fromisoformat(created_at.replace("Z", "+00:00")).timestamp()
            except ValueError:
                sort_time = 0.0
            results_path = run_dir / "results.json"
            result_payload: object = None
            if results_path.is_file():
                result_payload = json.loads(results_path.read_text(encoding="utf-8"))
            result_points = (
                result_payload
                if isinstance(result_payload, list)
                else result_payload.get("points", [])
                if isinstance(result_payload, dict)
                else []
            )
            # EVM dB 越接近 0 越差，因此 Worst EVM 取有效數值的最大值，不使用一般升降語意。
            evm_values = [
                float(point.get("evm_all_db"))
                for point in result_points
                if isinstance(point, dict)
                and isinstance(point.get("evm_all_db"), (int, float))
            ]
            frequency_values = [
                float(point.get("frequency_hz"))
                for point in result_points
                if isinstance(point, dict)
                and isinstance(point.get("frequency_hz"), (int, float))
            ]
            power_values = [
                float(point.get("generator_power_dbm"))
                for point in result_points
                if isinstance(point, dict)
                and isinstance(point.get("generator_power_dbm"), (int, float))
            ]
            runs.append(
                {
                    "run_id": str(metadata.get("run_id") or run_dir.name),
                    "run_key": run_dir.name,
                    "test_name": str(metadata.get("test_name") or "measurement"),
                    "created_at": created_at,
                    "simulated": bool(metadata.get("simulated", True)),
                    "status": str(metadata.get("status") or "complete"),
                    "completed_points": int(
                        metadata.get("completed_points") or metadata.get("point_count") or 0
                    ),
                    "source": str(metadata.get("source") or "unknown"),
                    "measurement_type": str(
                        metadata.get("measurement_type")
                        or metadata.get("sweep_axis")
                        or metadata.get("test_type")
                        or "unknown"
                    ),
                    "operator": str(metadata.get("operator") or metadata.get("operator_id") or ""),
                    "dut": str(metadata.get("dut") or metadata.get("dut_id") or ""),
                    "notes": str(metadata.get("notes") or metadata.get("comment") or ""),
                    "bandwidth_hz": metadata.get("bandwidth_hz"),
                    "route": str(metadata.get("route") or metadata.get("cable_route") or ""),
                    "calibration_profile": str(
                        metadata.get("calibration_profile_id")
                        or metadata.get("calibration_profile")
                        or ""
                    ),
                    "frequency_hz": frequency_values[0] if frequency_values else None,
                    "generator_power_dbm": power_values[0] if power_values else None,
                    "worst_evm_db": max(evm_values) if evm_values else None,
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
    # 核准清單改由 capability profile 驅動：新增一條已完成 HIL 的 route 只需改
    # approved_profile.routes，不必改程式；未列入者仍一律拒絕開啟 RF。
    profile = load_capability_profile(CAPABILITY_PROFILE_PATH)
    return validate_route(
        value,
        approved_routes=profile.approved_profile.routes,
        installed_ports=profile.installed.rf_ports,
    ).label


def validate_hardware_bind(host: str, hardware_enabled: bool) -> None:
    """Prevent the unauthenticated hardware endpoint from leaving loopback."""
    # 目前 Web 尚未有登入與角色權限；實機 RF 控制只能供本機操作員使用。
    if hardware_enabled and host.strip().lower() not in LOOPBACK_HOSTS:
        raise ValueError(
            "Hardware mode may bind only to loopback until authentication is implemented"
        )


def validate_custom_hardware_startup(
    host: str, hardware_enabled: bool, custom_hardware_enabled: bool
) -> None:
    """Require hardware control and a loopback bind for custom RF execution."""
    if custom_hardware_enabled and not hardware_enabled:
        raise ValueError("Custom hardware execution requires hardware control")
    validate_hardware_bind(host, hardware_enabled or custom_hardware_enabled)


class Cmp180WebHandler(SimpleHTTPRequestHandler):
    """Serve static GUI assets and explicitly scoped mock endpoints."""

    # 本機工作站預設提供實機控制；真正 RF 仍必須通過每次 request 的路徑與安全檢查。
    hardware_enabled = True
    custom_hardware_enabled = True

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

    def _resolve_config_path(self, requested: str) -> Path:
        """Resolve a request-supplied config file strictly inside configs/."""
        # 路徑來自請求，屬於不可信輸入；解析後必須仍位於 configs/ 才允許讀取。
        config_root = (PROJECT_ROOT / "configs").resolve()
        candidate = (config_root / requested).resolve()
        if candidate != config_root and config_root not in candidate.parents:
            raise ValueError("Config path must stay inside configs/")
        if not candidate.is_file():
            raise ValueError(f"Config file not found: {requested}")
        return candidate

    def _is_local_client(self) -> bool:
        """Return whether this request originates from the local workstation."""
        try:
            return ipaddress.ip_address(self.client_address[0]).is_loopback
        except ValueError:
            return False

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        parsed_path = parsed.path
        if parsed_path in DIAGRAM_ROUTES:
            # 首頁只可嵌入兩份受控架構圖；不接受 request 組合任意 docs 路徑。
            candidate = DIAGRAM_ROUTES[parsed_path]
            if not candidate.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            body = candidate.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed_path == "/api/calibration/adapters":
            self._json_response(
                {"adapters": [asdict(adapter) for adapter in list_calibration_adapters()]}
            )
            return
        if parsed_path == "/api/capabilities":
            # 此端點只公開能力分層，不會查詢儀器、送 SCPI 或授予 RF 權限。
            self._json_response(load_capability_profile(CAPABILITY_PROFILE_PATH).public())
            return
        if parsed_path == "/api/hil-campaign":
            # Campaign 狀態來自本機 JSON；查詢頁面不連線儀器，也不送出 SCPI。
            self._json_response(HIL_CAMPAIGN.load())
            return
        if parsed_path == "/api/runs":
            self._json_response({"runs": list_run_history(PROJECT_ROOT / "output")})
            return
        if parsed_path.startswith("/api/runs/"):
            run_key = unquote(parsed_path.removeprefix("/api/runs/"))
            try:
                self._json_response(load_run_record(PROJECT_ROOT / "output", run_key))
            except FileNotFoundError as exc:
                self._json_response({"error": str(exc)}, HTTPStatus.NOT_FOUND)
            except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                self._json_response({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        if parsed_path.startswith("/api/jobs/"):
            job_id = parsed_path.removeprefix("/api/jobs/")
            try:
                payload = JOB_MANAGER.get(job_id).public()
                result = payload.get("result")
                if isinstance(result, dict) and isinstance(result.get("artifacts"), dict):
                    # 只回傳 output/ 下的受控 URL，不把本機絕對路徑當成瀏覽器連結。
                    result["artifact_urls"] = self._artifact_urls(result["artifacts"])
                    result["output_location"] = self._output_location(result["artifacts"])
                    # 實機與模擬都套用同一份 draft profile，並且都明確標示非 compliance；
                    # 先前只有模擬結果附帶 profile，導致實機頁面無法顯示 PASS/FAIL。
                    result["limit_profile"] = DEMO_LIMIT_PROFILE.snapshot()
                    result["compliance_claim"] = False
                self._json_response(payload)
            except KeyError as exc:
                self._json_response({"error": str(exc)}, HTTPStatus.NOT_FOUND)
            return
        if parsed_path == "/api/status":
            mode = (
                "custom-hardware"
                if self.custom_hardware_enabled
                else "hardware"
                if self.hardware_enabled
                else "mock"
            )
            self._json_response(
                {
                    "app": "CMP180 WLAN EVM Automation",
                    "mode": mode,
                    "hardware_enabled": self.hardware_enabled,
                    "custom_hardware_enabled": self.custom_hardware_enabled,
                    "capability": (
                        "custom-frequency-and-power-sweep"
                        if self.custom_hardware_enabled
                        else "fixed-hardware-profiles"
                        if self.hardware_enabled
                        else "mock-single-frequency-sweep-and-power-sweep"
                    ),
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

    @staticmethod
    def _output_location(artifacts: dict[str, str]) -> str:
        # 顯示專案相對位置即可；絕對路徑可能包含員工帳號或公司目錄資訊。
        return f"output/{Path(artifacts['run_dir']).name}/"

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            if path.startswith("/api/jobs/") and path.endswith("/pause"):
                job_id = path.removeprefix("/api/jobs/").removesuffix("/pause")
                # Pause 只設 cooperative gate；worker 會在 STOP／RF Off 的點位邊界停住。
                self._json_response(JOB_MANAGER.pause(job_id).public())
                return
            if path.startswith("/api/jobs/") and path.endswith("/resume"):
                job_id = path.removeprefix("/api/jobs/").removesuffix("/resume")
                self._json_response(JOB_MANAGER.resume(job_id).public())
                return
            if path.startswith("/api/jobs/") and path.endswith("/cancel"):
                job_id = path.removeprefix("/api/jobs/").removesuffix("/cancel")
                self._json_response(JOB_MANAGER.cancel(job_id).public())
                return
            data = self._read_json()
            if path == "/api/hil-campaign/prepare":
                # Prepare 只套用現行 safety/profile gate，blocked case 不會進 RF workflow。
                self._json_response(HIL_CAMPAIGN.prepare())
                return
            if path == "/api/hil-campaign/reset":
                self._json_response(HIL_CAMPAIGN.reset())
                return
            if path.startswith("/api/hil-campaign/cases/") and path.endswith("/retry"):
                case_id = unquote(
                    path.removeprefix("/api/hil-campaign/cases/").removesuffix("/retry")
                )
                HIL_CAMPAIGN.retry(case_id)
                self._json_response(HIL_CAMPAIGN.prepare())
                return
            if path.startswith("/api/hil-campaign/cases/") and path.endswith("/start"):
                if not self.hardware_enabled or not self.custom_hardware_enabled:
                    self._json_response(
                        {"error": "Hardware campaign execution is locked at server startup"},
                        HTTPStatus.FORBIDDEN,
                    )
                    return
                if data.get("operator_present") is not True:
                    raise ValueError("Operator presence confirmation is required")
                if data.get("route_connected") is not True:
                    raise ValueError("Current route connection confirmation is required")
                case_id = unquote(
                    path.removeprefix("/api/hil-campaign/cases/").removesuffix("/start")
                )
                case = HIL_CAMPAIGN.case(case_id)
                preview = build_custom_sweep_preview(case["request"])
                if not preview.execution_allowed:
                    HIL_CAMPAIGN.update_case(
                        case_id, state="blocked", reason=preview.rejection_reason or "Blocked"
                    )
                    self._json_response(
                        {"error": preview.rejection_reason or "Campaign case is blocked"},
                        HTTPStatus.FORBIDDEN,
                    )
                    return
                validate_cable_route(case["route"])
                from cmp180_evm.web.real_service import run_custom_real_sweep

                execution_request = dict(case["request"])

                def campaign_worker(active_job):
                    try:
                        result = run_custom_real_sweep(
                            active_job,
                            request=execution_request,
                            output_root=PROJECT_ROOT / "output",
                        )
                        failed = result.get("measurement_failed") is True
                        HIL_CAMPAIGN.update_case(
                            case_id,
                            state="failed" if failed else "complete",
                            reason=str(result.get("error") or ""),
                            artifacts=result.get("artifacts") or {},
                        )
                        return result
                    except Exception as exc:
                        # 例外 cleanup 由 real_service finally 執行；此處另存失敗以便重啟後續跑。
                        HIL_CAMPAIGN.update_case(
                            case_id,
                            state="failed",
                            reason=f"{type(exc).__name__}: {exc}",
                        )
                        raise

                job = JOB_MANAGER.start(
                    f"hil-campaign-{case_id}", len(preview.points), campaign_worker
                )
                HIL_CAMPAIGN.update_case(
                    case_id, state="running", reason="", job_id=job.job_id
                )
                self._json_response(job.public(), HTTPStatus.ACCEPTED)
                return
            if path == "/api/calibration/capture":
                adapter_id = str(data.get("adapter_id") or "")
                adapter = create_calibration_adapter(adapter_id)
                # 模擬擷取也必須由 UI 明確標示，避免示範讀值混入正式 Profile。
                if adapter.simulated and data.get("allow_simulated") is not True:
                    raise ValueError("Simulated capture requires explicit acknowledgement")
                frequencies_raw = data.get("frequencies_hz")
                if not isinstance(frequencies_raw, list):
                    raise ValueError("frequencies_hz must be a list")
                result = capture_calibration_readings(
                    adapter,
                    tuple(float(value) for value in frequencies_raw),
                    float(data.get("source_power_dbm", -40)),
                )
                self._json_response(result.public())
                return
            if path == "/api/hardware/custom-plan-preview":
                # 預覽只建立安全點位，不連線儀器、不送 SCPI，也不開 RF。
                preview = build_custom_sweep_preview(data)
                self._json_response(preview.public())
                return
            if path == "/api/hardware/single-plan-preview":
                # 單點預覽只做型別與 approved profile 檢查，不建立儀器 session，也不送 RF。
                self._json_response(build_custom_single_preview(data).public())
                return
            if path == "/api/hardware/loopback-preview":
                # Loopback 預覽沿用 SingleShot RF gate，另外限制重複次數以避免誤送過長測試。
                preview = build_custom_single_preview(data)
                repeats = int(data.get("repeat_count", 5))
                if not 2 <= repeats <= 100:
                    raise ValueError("Loopback repeat count must be between 2 and 100")
                payload = preview.public()
                loopback_profile = select_loopback_profile(data)
                payload.update(
                    repeat_count=repeats,
                    total_measurements=repeats,
                    profile_lifecycle=loopback_profile.lifecycle,
                    loopback_profile=loopback_profile.snapshot(),
                )
                self._json_response(payload)
                return
            if path == "/api/hardware/loopback-batch-preview":
                # 一鍵批次仍逐案通過正式 SingleShot profile gate；預覽本身不送 SCPI。
                cases = []
                for request in loopback_batch_requests():
                    preview = build_custom_single_preview(request)
                    cases.append(
                        {
                            "case_id": request["batch_case_id"],
                            "frequency_hz": request["center_frequency_hz"],
                            "bandwidth_hz": request["bandwidth_hz"],
                            "generator_power_dbm": request["generator_power_dbm"],
                            "execution_allowed": preview.execution_allowed,
                            "rejection_reason": preview.rejection_reason,
                        }
                    )
                self._json_response(
                    {
                        "cases": cases,
                        "case_count": len(cases),
                        "repeat_count_per_case": 10,
                        "total_measurements": len(cases) * 10,
                        "execution_allowed": all(case["execution_allowed"] for case in cases),
                        "required_confirmation": "LOOPBACK-BATCH-11X10-RF1.1-RF1.5",
                    }
                )
                return
            if path == "/api/hardware/gprf-power-preview":
                # GPRF 預覽只檢查 CMP180 tune/power 規劃範圍；它不是 WLAN EVM 授權。
                self._json_response(build_gprf_power_preview(data).public())
                return
            if path == "/api/jobs/hardware/gprf-power-sweep":
                if not self.hardware_enabled:
                    self._json_response(
                        {"error": "Hardware mode is locked at server startup"},
                        HTTPStatus.FORBIDDEN,
                    )
                    return
                validate_cable_route(data.get("cable_confirmation"))
                if data.get("operator_present") is not True:
                    raise ValueError("Operator presence confirmation is required")
                if data.get("gprf_confirmation") != "GPRF-POWER-NOT-WLAN-EVM":
                    raise ValueError("GPRF confirmation is required")
                preview = build_gprf_power_preview(data)
                if not preview.execution_allowed:
                    self._json_response(
                        {"error": preview.rejection_reason or "GPRF plan is blocked"},
                        HTTPStatus.FORBIDDEN,
                    )
                    return
                from cmp180_evm.web.gprf_service import run_gprf_power_sweep

                # GPRF 是獨立能力檢查 workflow；背景 thread 收到 request copy 後
                # 不再讀 handler 狀態。
                execution_request = dict(data)
                job = JOB_MANAGER.start(
                    f"hardware-gprf-{preview.axis}-power-sweep",
                    len(preview.points),
                    lambda active_job: run_gprf_power_sweep(
                        active_job,
                        request=execution_request,
                        output_root=PROJECT_ROOT / "output",
                    ),
                )
                self._json_response(job.public(), HTTPStatus.ACCEPTED)
                return
            if path == "/api/jobs/hardware/custom-sweep":
                if not self.hardware_enabled or not self.custom_hardware_enabled:
                    self._json_response(
                        {"error": "Custom hardware execution is locked at server startup"},
                        HTTPStatus.FORBIDDEN,
                    )
                    return
                validate_cable_route(data.get("cable_confirmation"))
                if data.get("operator_present") is not True:
                    raise ValueError("Operator presence confirmation is required")
                if data.get("direct_cable_no_attenuator") is not True:
                    raise ValueError("Direct-cable/no-attenuator confirmation is required")
                preview = build_custom_sweep_preview(data)
                if not preview.execution_allowed:
                    self._json_response(
                        {
                            "error": (
                                "Plan is within the CMP180 planning range but cannot enter the "
                                f"current RF workflow: {preview.rejection_reason}"
                            )
                        },
                        HTTPStatus.FORBIDDEN,
                    )
                    return
                if data.get("execution_confirmation") != preview.required_confirmation:
                    raise ValueError("Custom plan confirmation does not match revalidated plan")
                from cmp180_evm.web.real_service import run_custom_real_sweep

                # 複製 request，避免背景 thread 讀到 handler 後續變動的 request 物件。
                execution_request = dict(data)
                # 校正為選用；未指定時完全維持未修正行為。Draft／過期／路徑不符或
                # 頻率超出校正範圍，都會在此拋錯而不是靜默送出未修正的量測。
                calibration_profile = None
                requested_profile = data.get("calibration_profile_path")
                if requested_profile:
                    calibration_profile = load_calibration_profile(
                        self._resolve_config_path(str(requested_profile))
                    )
                job = JOB_MANAGER.start(
                    f"hardware-custom-{preview.axis}-sweep",
                    len(preview.points),
                    lambda active_job: run_custom_real_sweep(
                        active_job,
                        request=execution_request,
                        output_root=PROJECT_ROOT / "output",
                        calibration_profile=calibration_profile,
                    ),
                )
                self._json_response(job.public(), HTTPStatus.ACCEPTED)
                return
            if path == "/api/jobs/hardware/loopback":
                if not self.hardware_enabled or not self.custom_hardware_enabled:
                    self._json_response(
                        {"error": "Loopback hardware execution is locked at server startup"},
                        HTTPStatus.FORBIDDEN,
                    )
                    return
                validate_cable_route(data.get("cable_confirmation"))
                if data.get("operator_present") is not True:
                    raise ValueError("Operator presence confirmation is required")
                if data.get("direct_cable_no_attenuator") is not True:
                    raise ValueError("Direct-cable/no-attenuator confirmation is required")
                preview = build_custom_single_preview(data)
                repeats = int(data.get("repeat_count", 5))
                if not 2 <= repeats <= 100:
                    raise ValueError("Loopback repeat count must be between 2 and 100")
                if not preview.execution_allowed:
                    self._json_response(
                        {"error": preview.rejection_reason or "Loopback plan is blocked"},
                        HTTPStatus.FORBIDDEN,
                    )
                    return
                if data.get("execution_confirmation") != preview.required_confirmation:
                    raise ValueError("Loopback confirmation does not match revalidated plan")
                from cmp180_evm.web.real_service import run_real_loopback_validation

                execution_request = dict(data)
                job = JOB_MANAGER.start(
                    "hardware-loopback-validation",
                    repeats,
                    lambda active_job: run_real_loopback_validation(
                        active_job,
                        request=execution_request,
                        output_root=PROJECT_ROOT / "output",
                    ),
                )
                self._json_response(job.public(), HTTPStatus.ACCEPTED)
                return
            if path == "/api/jobs/hardware/loopback-batch":
                if not self.hardware_enabled or not self.custom_hardware_enabled:
                    self._json_response(
                        {"error": "Loopback hardware execution is locked at server startup"},
                        HTTPStatus.FORBIDDEN,
                    )
                    return
                validate_cable_route(data.get("cable_confirmation"))
                if data.get("operator_present") is not True:
                    raise ValueError("Operator presence confirmation is required")
                if data.get("direct_cable_no_attenuator") is not True:
                    raise ValueError("Direct-cable/no-attenuator confirmation is required")
                if data.get("execution_confirmation") != "LOOPBACK-BATCH-11X10-RF1.1-RF1.5":
                    raise ValueError("Loopback batch confirmation is required")
                requests = loopback_batch_requests()
                for request in requests:
                    preview = build_custom_single_preview(request)
                    if not preview.execution_allowed:
                        self._json_response(
                            {
                                "error": (
                                    f"{request['batch_case_id']} is blocked: "
                                    f"{preview.rejection_reason}"
                                )
                            },
                            HTTPStatus.FORBIDDEN,
                        )
                        return
                from cmp180_evm.web.real_service import run_real_loopback_batch

                # 單一 Job 依序執行 11×10；任何案例的 SCPI/cleanup error 都停止後續案例。
                job = JOB_MANAGER.start(
                    "hardware-loopback-batch-validation",
                    len(requests) * 10,
                    lambda active_job: run_real_loopback_batch(
                        active_job,
                        output_root=PROJECT_ROOT / "output",
                    ),
                )
                self._json_response(job.public(), HTTPStatus.ACCEPTED)
                return
            if path == "/api/calibration/draft-preview":
                raw_readings = data.get("readings")
                if not isinstance(raw_readings, list):
                    raise ValueError("Calibration readings must be a list")
                readings = tuple(
                    CalibrationReading(
                        float(item["frequency_hz"]),
                        float(item["source_reference_dbm"]),
                        float(item["receiver_reading_dbm"]),
                    )
                    for item in raw_readings
                    if isinstance(item, dict)
                )
                if len(readings) != len(raw_readings):
                    raise ValueError("Every calibration reading must be an object")
                profile = build_draft_profile(
                    readings,
                    profile_id=str(data["profile_id"]),
                    revision=str(data.get("revision") or "0.1-draft"),
                    route=validate_cable_route(data.get("route")),
                    calibrated_at=date.fromisoformat(str(data["calibrated_at"])),
                    expires_at=date.fromisoformat(str(data["expires_at"])),
                    equipment_reference=str(data["equipment_reference"]),
                )
                self._json_response(
                    {
                        "profile": profile.snapshot(),
                        "measurement_use": "BLOCKED_DRAFT_REQUIRES_OWNER_APPROVAL",
                    }
                )
                return
            if path.startswith("/api/runs/") and path.endswith("/open-folder"):
                # 開啟 Explorer 是工作站副作用；內網遠端請求不得觸發本機 GUI。
                if not self._is_local_client():
                    self._json_response(
                        {"error": "Open folder is available only from the local workstation"},
                        HTTPStatus.FORBIDDEN,
                    )
                    return
                run_key = unquote(path.removeprefix("/api/runs/").removesuffix("/open-folder"))
                open_run_folder(PROJECT_ROOT / "output", run_key)
                self._json_response({"status": "opened"})
                return
            if path.startswith("/api/runs/") and path.endswith("/trash"):
                # 移至 .trash 雖可復原，仍屬檔案狀態變更，只允許本機操作員執行。
                if not self._is_local_client():
                    self._json_response(
                        {"error": "Trash is available only from the local workstation"},
                        HTTPStatus.FORBIDDEN,
                    )
                    return
                run_key = unquote(path.removeprefix("/api/runs/").removesuffix("/trash"))
                result = move_run_to_trash(
                    PROJECT_ROOT / "output", run_key, str(data.get("confirm_run_id") or "")
                )
                self._json_response(result)
                return
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
                if data.get("direct_cable_no_attenuator") is not True:
                    raise ValueError("Direct-cable/no-attenuator confirmation is required")
                preview = build_custom_single_preview(data)
                if not preview.execution_allowed:
                    self._json_response(
                        {"error": preview.rejection_reason or "SingleShot plan is blocked"},
                        HTTPStatus.FORBIDDEN,
                    )
                    return
                if data.get("execution_confirmation") != preview.required_confirmation:
                    raise ValueError("SingleShot confirmation does not match revalidated plan")
                # 延遲 import，Mock-only server 不載入或接觸硬體套件。
                from cmp180_evm.web.real_service import run_custom_real_single

                payload = run_custom_real_single(
                    request=data,
                    output_root=PROJECT_ROOT / "output",
                )
                payload["artifact_urls"] = self._artifact_urls(payload["artifacts"])
                payload["output_location"] = self._output_location(payload["artifacts"])
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
                "p1db": analyze_mock_p1db(points),
                "artifacts": artifacts,
                "artifact_urls": self._artifact_urls(artifacts),
                "output_location": self._output_location(artifacts),
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
        "--demo-only",
        action="store_true",
        help="Disable all real-hardware endpoints and run with demonstration data only.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    hardware_enabled = not args.demo_only
    custom_hardware_enabled = not args.demo_only
    validate_custom_hardware_startup(args.host, hardware_enabled, custom_hardware_enabled)
    Cmp180WebHandler.hardware_enabled = hardware_enabled
    Cmp180WebHandler.custom_hardware_enabled = custom_hardware_enabled
    server = ExclusiveThreadingHTTPServer((args.host, args.port), Cmp180WebHandler)
    print(f"CMP180 Web GUI: http://{args.host}:{args.port}")
    print(
        "Mode: hardware endpoint enabled (custom enabled)."
        if custom_hardware_enabled
        else "Mode: hardware endpoint enabled (fixed profiles only)."
        if hardware_enabled
        else "Mode: MOCK only; real-hardware controls are locked."
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
