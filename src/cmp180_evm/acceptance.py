"""Build a bilingual, evidence-backed V1 acceptance readiness report."""

from __future__ import annotations

import html
import json
import math
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from cmp180_evm.calibration import load_calibration_profile
from cmp180_evm.limits import load_limit_profile


@dataclass(frozen=True)
class AcceptanceGate:
    gate_id: str
    title_zh: str
    title_en: str
    status: str
    evidence: str


def _profile_gates(calibration_path: Path, limit_path: Path) -> list[AcceptanceGate]:
    calibration = load_calibration_profile(calibration_path)
    limits = load_limit_profile(limit_path)
    cal_ready = calibration.lifecycle == "approved" and not calibration.is_expired()
    limit_ready = limits.lifecycle == "approved"
    return [
        AcceptanceGate(
            "calibration",
            "校正 Profile 已核准且在有效期內",
            "Calibration Profile approved and current",
            "PASS" if cal_ready else "BLOCKED",
            (
                f"{calibration.profile_id} rev {calibration.revision}; "
                f"lifecycle={calibration.lifecycle}"
            ),
        ),
        AcceptanceGate(
            "limits",
            "Limit Profile 有規格來源與核准紀錄",
            "Limit Profile has specification source and approval",
            "PASS" if limit_ready else "BLOCKED",
            f"{limits.profile_id} rev {limits.revision}; lifecycle={limits.lifecycle}",
        ),
    ]


def _evidence_gate(evidence_dirs: tuple[Path, ...]) -> AcceptanceGate:
    valid_runs: list[str] = []
    problems: list[str] = []
    for run_dir in evidence_dirs:
        try:
            metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
            results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{run_dir.name}: {exc}")
            continue
        # Acceptance 只採完整實機 run；Mock、partial 或空結果不得補足 HIL 證據。
        if metadata.get("simulated") is True or metadata.get("status") != "complete" or not results:
            problems.append(f"{run_dir.name}: not a complete live-hardware run")
            continue
        points = results if isinstance(results, list) else [results]

        def valid_point(point: object) -> bool:
            if not isinstance(point, dict):
                return False
            if "valid" in point:
                return point.get("valid") is True
            # 舊版 SingleShot schema 沒有 valid 欄；只接受 reliability=0 且 EVM 為有限值。
            value = point.get("evm_all_carriers_db")
            if not isinstance(value, (int, float, str)):
                return False
            try:
                return int(point.get("reliability", -1)) == 0 and math.isfinite(float(value))
            except (TypeError, ValueError):
                return False

        if not all(valid_point(point) for point in points):
            problems.append(f"{run_dir.name}: contains invalid points")
            continue
        valid_runs.append(str(metadata.get("run_id") or run_dir.name))
    status = "PASS" if evidence_dirs and not problems else "BLOCKED"
    detail = f"valid runs: {', '.join(valid_runs) or 'none'}"
    if problems:
        detail += f"; issues: {' | '.join(problems)}"
    return AcceptanceGate(
        "hil_evidence",
        "指定 HIL artifacts 完整且所有點有效",
        "Selected HIL artifacts are complete with all points valid",
        status,
        detail,
    )


def build_v1_acceptance_report(
    calibration_path: Path,
    limit_path: Path,
    evidence_dirs: tuple[Path, ...],
    output_dir: Path,
) -> tuple[Path, Path]:
    """Write HTML and JSON readiness artifacts without contacting the instrument."""
    gates = _profile_gates(calibration_path, limit_path)
    gates.append(_evidence_gate(evidence_dirs))
    overall = "ACCEPTED" if all(gate.status == "PASS" for gate in gates) else "BLOCKED"
    generated_at = datetime.now(UTC).isoformat()
    payload = {
        "schema_version": 1,
        "generated_at": generated_at,
        "overall_status": overall,
        # 閘門全數通過代表「V1 交付可簽核」，不等於對 DUT 的正式 compliance 宣告。
        # 專案其他 artifacts 一律 compliance_claim=false，此處保持一致，
        # 避免這份報告被引用成合規證據；交付狀態請看 overall_status。
        "compliance_claim": False,
        "gates": [asdict(gate) for gate in gates],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "v1-acceptance.json"
    html_path = output_dir / "v1-acceptance.html"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    rows_zh = "".join(
        f"<tr><td>{html.escape(g.title_zh)}</td><td class='{g.status.lower()}'>{g.status}</td>"
        f"<td>{html.escape(g.evidence)}</td></tr>" for g in gates
    )
    rows_en = "".join(
        f"<tr><td>{html.escape(g.title_en)}</td><td class='{g.status.lower()}'>{g.status}</td>"
        f"<td>{html.escape(g.evidence)}</td></tr>" for g in gates
    )
    # 中文完整內容置前、英文完整內容置後；報告只讀現有 artifacts，不觸發 SCPI/RF。
    html_path.write_text(
        "<!doctype html><html lang='zh-Hant'><meta charset='utf-8'>"
        "<title>CMP180 V1 Acceptance</title><style>body{font:15px system-ui;margin:32px;"
        "color:#172033;background:#f4f7fb}main{max-width:1100px;margin:auto}section{background:#fff;"
        "padding:24px;margin:18px 0;border-radius:14px}table{border-collapse:collapse;width:100%}"
        "th,td{padding:10px;border-bottom:1px solid #dde4ec;text-align:left}.pass{color:#08785b;"
        "font-weight:800}.blocked{color:#b4233d;font-weight:800}</style><main>"
        f"<h1>CMP180 WLAN EVM V1 驗收報告</h1><p>總狀態：<strong>{overall}</strong></p>"
        "<p>此報告由既有 Profile 與實機 artifacts 離線產生，不會連線或控制儀器。"
        "BLOCKED 表示仍需負責人核准或補齊證據，不得宣稱正式 compliance PASS。</p>"
        f"<section><table><thead><tr><th>驗收閘門</th><th>狀態</th><th>證據</th></tr></thead>"
        f"<tbody>{rows_zh}</tbody></table></section>"
        f"<h1>CMP180 WLAN EVM V1 Acceptance Report</h1><p>Overall: <strong>{overall}</strong></p>"
        "<p>This report is generated offline from existing profiles and live-hardware artifacts; "
        "it does not connect to or control the instrument. BLOCKED means owner approval or "
        "evidence "
        "is still missing and no formal compliance PASS may be claimed.</p>"
        f"<section><table><thead><tr><th>Gate</th><th>Status</th><th>Evidence</th></tr></thead>"
        f"<tbody>{rows_en}</tbody></table></section><p>Generated: {html.escape(generated_at)}</p>"
        "</main></html>",
        encoding="utf-8",
    )
    return html_path, json_path
