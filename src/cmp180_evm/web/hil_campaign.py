"""Persistent, operator-driven HIL campaign planning and evidence tracking."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from cmp180_evm.web.custom_plans import build_custom_sweep_preview


DEFAULT_CASES: tuple[dict[str, object], ...] = (
    {"case_id": "b24-bw20", "category": "bandwidth", "label": "2.4 GHz / 20 MHz", "route": "RF1.1-RF1.5", "request": {"axis": "frequency", "start_hz": 2_412_000_000, "stop_hz": 2_472_000_000, "step_hz": 30_000_000, "bandwidth_hz": 20_000_000, "generator_power_dbm": -45, "dwell_ms": 100}},
    {"case_id": "b24-bw40", "category": "bandwidth", "label": "2.4 GHz / 40 MHz", "route": "RF1.1-RF1.5", "request": {"axis": "frequency", "start_hz": 2_422_000_000, "stop_hz": 2_462_000_000, "step_hz": 20_000_000, "bandwidth_hz": 40_000_000, "generator_power_dbm": -45, "dwell_ms": 100}},
    {"case_id": "b5-bw20", "category": "bandwidth", "label": "5 GHz / 20 MHz", "route": "RF1.1-RF1.5", "request": {"axis": "frequency", "start_hz": 5_180_000_000, "stop_hz": 5_805_000_000, "step_hz": 312_500_000, "bandwidth_hz": 20_000_000, "generator_power_dbm": -45, "dwell_ms": 100}},
    {"case_id": "b5-bw40", "category": "bandwidth", "label": "5 GHz / 40 MHz", "route": "RF1.1-RF1.5", "request": {"axis": "frequency", "start_hz": 5_190_000_000, "stop_hz": 5_795_000_000, "step_hz": 302_500_000, "bandwidth_hz": 40_000_000, "generator_power_dbm": -45, "dwell_ms": 100}},
    {"case_id": "b5-bw80", "category": "bandwidth", "label": "5 GHz / 80 MHz", "route": "RF1.1-RF1.5", "request": {"axis": "frequency", "start_hz": 5_210_000_000, "stop_hz": 5_775_000_000, "step_hz": 282_500_000, "bandwidth_hz": 80_000_000, "generator_power_dbm": -45, "dwell_ms": 100}},
    {"case_id": "b5-bw160", "category": "bandwidth", "label": "5 GHz / 160 MHz", "route": "RF1.1-RF1.5", "request": {"axis": "frequency", "start_hz": 5_250_000_000, "stop_hz": 5_570_000_000, "step_hz": 320_000_000, "bandwidth_hz": 160_000_000, "generator_power_dbm": -45, "dwell_ms": 100}},
    {"case_id": "b6-bw20", "category": "bandwidth", "label": "6 GHz / 20 MHz", "route": "RF1.1-RF1.5", "request": {"axis": "frequency", "start_hz": 5_935_000_000, "stop_hz": 7_115_000_000, "step_hz": 590_000_000, "bandwidth_hz": 20_000_000, "generator_power_dbm": -45, "dwell_ms": 100}},
    {"case_id": "b6-bw40", "category": "bandwidth", "label": "6 GHz / 40 MHz", "route": "RF1.1-RF1.5", "request": {"axis": "frequency", "start_hz": 5_945_000_000, "stop_hz": 7_105_000_000, "step_hz": 580_000_000, "bandwidth_hz": 40_000_000, "generator_power_dbm": -45, "dwell_ms": 100}},
    {"case_id": "b6-bw80", "category": "bandwidth", "label": "6 GHz / 80 MHz", "route": "RF1.1-RF1.5", "request": {"axis": "frequency", "start_hz": 5_965_000_000, "stop_hz": 7_085_000_000, "step_hz": 560_000_000, "bandwidth_hz": 80_000_000, "generator_power_dbm": -45, "dwell_ms": 100}},
    {"case_id": "b6-bw160", "category": "bandwidth", "label": "6 GHz / 160 MHz", "route": "RF1.1-RF1.5", "request": {"axis": "frequency", "start_hz": 6_005_000_000, "stop_hz": 7_045_000_000, "step_hz": 520_000_000, "bandwidth_hz": 160_000_000, "generator_power_dbm": -45, "dwell_ms": 100}},
    {"case_id": "b6-bw320", "category": "baseline", "label": "6 GHz / 320 MHz known-good baseline", "route": "RF1.1-RF1.5", "request": {"axis": "frequency", "start_hz": 6_085_000_000, "stop_hz": 6_125_000_000, "step_hz": 20_000_000, "bandwidth_hz": 320_000_000, "generator_power_dbm": -40, "dwell_ms": 100}},
    {"case_id": "b6-power", "category": "power", "label": "6 GHz power reference (-40 to -30 dBm)", "route": "RF1.1-RF1.5", "requires": "b6-bw320", "request": {"axis": "power", "center_frequency_hz": 6_105_000_000, "start_dbm": -40, "stop_dbm": -30, "step_dbm": 5, "bandwidth_hz": 320_000_000, "dwell_ms": 100}},
)

REFERENCE_REQUEST = {"axis": "frequency", "start_hz": 6_105_000_000, "stop_hz": 6_105_000_000, "step_hz": 20_000_000, "bandwidth_hz": 320_000_000, "generator_power_dbm": -45, "dwell_ms": 100}


class HilCampaignStore:
    """Persist campaign progress so browser operation survives chat/server restarts."""

    def __init__(self, state_path: Path):
        self.state_path = state_path
        self._lock = Lock()
        if self.state_path.is_file():
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
            changed = False
            for case in state.get("cases", []):
                if case.get("state") == "running":
                    # Server 重啟後舊 thread 不存在；轉為 interrupted，禁止假裝仍在送 RF。
                    case["state"] = "interrupted"
                    case["reason"] = "Server restarted; prepare this case before rerun"
                    changed = True
            if changed:
                self._save_unlocked(state)

    def _default(self) -> dict[str, object]:
        cases = []
        for template in DEFAULT_CASES:
            case = deepcopy(template)
            case.update({"state": "pending", "reason": "", "job_id": None, "artifacts": {}})
            cases.append(case)
        ports = [f"RF{bank}.{index}" for bank in (1, 2) for index in range(1, 9)]
        for port in ports:
            if port != "RF1.5":
                cases.append({"case_id": f"route-rf11-{port.lower().replace('.', '')}", "category": "route", "label": f"RF1.1 → {port}", "route": f"RF1.1-{port}", "request": deepcopy(REFERENCE_REQUEST), "state": "pending", "reason": "", "job_id": None, "artifacts": {}})
        for port in ports:
            if port not in {"RF1.1", "RF1.5"}:
                cases.append({"case_id": f"route-{port.lower().replace('.', '')}-rf15", "category": "route", "label": f"{port} → RF1.5", "route": f"{port}-RF1.5", "request": deepcopy(REFERENCE_REQUEST), "state": "pending", "reason": "", "job_id": None, "artifacts": {}})
        cases.extend((
            {"case_id": "analysis-bw500", "category": "analysis", "label": "500 MHz analysis bandwidth", "route": "RF1.1-RF1.5", "request": {**deepcopy(REFERENCE_REQUEST), "bandwidth_hz": 500_000_000}, "state": "pending", "reason": "", "job_id": None, "artifacts": {}},
            {"case_id": "dual-vsa-vsg", "category": "parallel", "label": "Dual VSA/VSG parallel", "route": "TWO-INDEPENDENT-ROUTES", "request": None, "state": "pending", "reason": "", "job_id": None, "artifacts": {}},
            {"case_id": "waveform-len32768", "category": "waveform", "label": "LEN ≥ 32768 convergence", "route": "RF1.1-RF1.5", "request": None, "state": "pending", "reason": "", "job_id": None, "artifacts": {}},
        ))
        return {"schema_version": 1, "updated_at": self._now(), "cases": cases}

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def load(self) -> dict[str, object]:
        with self._lock:
            if not self.state_path.is_file():
                return self._save_unlocked(self._default())
            return json.loads(self.state_path.read_text(encoding="utf-8"))

    def reset(self) -> dict[str, object]:
        with self._lock:
            return self._save_unlocked(self._default())

    def prepare(self) -> dict[str, object]:
        state = self.load()
        changed = False
        templates = {item["case_id"]: item for item in DEFAULT_CASES}
        for case in state["cases"]:
            template = templates.get(case["case_id"])
            if template:
                # 更新內建案例定義但保留執行狀態／歷史證據，避免舊 state 永遠沿用錯誤點位。
                for key in ("category", "label", "route", "request", "requires"):
                    if key in template:
                        case[key] = deepcopy(template[key])
                    else:
                        case.pop(key, None)
                changed = True
            if case["state"] in {"complete", "running", "failed"}:
                continue
            if not isinstance(case.get("request"), dict):
                case["state"] = "blocked"
                case["reason"] = "Dedicated verified backend/SCPI registry entry is not available"
                changed = True
                continue
            preview = build_custom_sweep_preview(case["request"])
            case["preview"] = preview.public()
            route_allowed = case["route"] == "RF1.1-RF1.5"
            requirement = case.get("requires")
            requirement_complete = not requirement or any(
                item["case_id"] == requirement and item["state"] == "complete"
                for item in state["cases"]
            )
            case["state"] = (
                "ready"
                if preview.execution_allowed and route_allowed and requirement_complete
                else "blocked"
            )
            case["reason"] = (
                preview.rejection_reason
                or ("Route backend/profile is not verified" if not route_allowed else "")
                or (f"Requires successful case {requirement}" if not requirement_complete else "")
            )
            changed = True
        return self.save(state) if changed else state

    def case(self, case_id: str) -> dict[str, object]:
        state = self.load()
        for case in state["cases"]:
            if case["case_id"] == case_id:
                return case
        raise KeyError("HIL campaign case not found")

    def update_case(self, case_id: str, **updates: object) -> dict[str, object]:
        with self._lock:
            state = self._load_unlocked()
            for case in state["cases"]:
                if case["case_id"] == case_id:
                    case.update(updates)
                    self._save_unlocked(state)
                    return case
            raise KeyError("HIL campaign case not found")

    def retry(self, case_id: str) -> dict[str, object]:
        """Archive the failed attempt and return the case to pending for explicit recheck."""
        with self._lock:
            state = self._load_unlocked()
            for case in state["cases"]:
                if case["case_id"] != case_id:
                    continue
                if case["state"] not in {"failed", "interrupted"}:
                    raise ValueError("Only failed or interrupted cases can be retried")
                attempts = list(case.get("attempts") or [])
                attempts.append({"reason": case.get("reason"), "artifacts": case.get("artifacts")})
                case.update({"state": "pending", "reason": "", "job_id": None, "artifacts": {}, "attempts": attempts})
                return self._save_unlocked(state)
            raise KeyError("HIL campaign case not found")

    def save(self, state: dict[str, object]) -> dict[str, object]:
        with self._lock:
            return self._save_unlocked(state)

    def _load_unlocked(self) -> dict[str, object]:
        return (
            json.loads(self.state_path.read_text(encoding="utf-8"))
            if self.state_path.is_file()
            else self._default()
        )

    def _save_unlocked(self, state: dict[str, object]) -> dict[str, object]:
        state["updated_at"] = self._now()
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.state_path.with_suffix(".tmp")
        # 先寫暫存再 replace，避免斷電或中止留下半份 JSON，讓下一次可安全續跑。
        temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.state_path)
        return state
