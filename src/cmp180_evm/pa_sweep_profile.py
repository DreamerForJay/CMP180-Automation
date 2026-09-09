"""Approved PA power-sweep profile validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class PaSweepProfile:
    profile_id: str
    revision: str
    lifecycle: str
    route: str
    frequency_hz: float
    start_dbm: float
    stop_dbm: float
    step_db: float
    dwell_ms: int
    expected_dut_gain_db: float
    input_cable_loss_db: float
    output_cable_loss_db: float
    output_attenuator_db: float
    measurement_external_attenuation_db: float
    sa_safe_limit_dbm: float
    approved_by: str
    approved_at: date
    source_evidence: str

    def max_safe_generator_power_dbm(
        self,
        *,
        expected_dut_gain_db: float | None = None,
        output_cable_loss_db: float | None = None,
        output_attenuator_db: float | None = None,
    ) -> float:
        gain = self.expected_dut_gain_db if expected_dut_gain_db is None else expected_dut_gain_db
        loss = self.output_cable_loss_db if output_cable_loss_db is None else output_cable_loss_db
        attenuator = (
            self.output_attenuator_db if output_attenuator_db is None else output_attenuator_db
        )
        # 由 RF1.5 safe limit 反推可送出的最高 Generator power；現場 fixture 不同時會改變此值。
        return self.sa_safe_limit_dbm - gain + loss + attenuator

    def worst_case_rf_input_dbm(
        self,
        *,
        stop_dbm: float | None = None,
        expected_dut_gain_db: float | None = None,
        output_cable_loss_db: float | None = None,
        output_attenuator_db: float | None = None,
    ) -> float:
        stop = self.stop_dbm if stop_dbm is None else stop_dbm
        gain = self.expected_dut_gain_db if expected_dut_gain_db is None else expected_dut_gain_db
        loss = self.output_cable_loss_db if output_cable_loss_db is None else output_cable_loss_db
        attenuator = (
            self.output_attenuator_db if output_attenuator_db is None else output_attenuator_db
        )
        # RF1.5 輸入保護用最壞點估算；不得用離線 Pout 補償值放寬此限制。
        return stop + gain - loss - attenuator

    def measurement_request(
        self,
        *,
        dut_id: str = "",
        expected_dut_gain_db: float | None = None,
        output_attenuator_db: float | None = None,
        input_cable_loss_db: float | None = None,
        output_cable_loss_db: float | None = None,
    ) -> dict[str, object]:
        gain = self.expected_dut_gain_db if expected_dut_gain_db is None else expected_dut_gain_db
        input_loss = self.input_cable_loss_db if input_cable_loss_db is None else input_cable_loss_db
        output_loss = (
            self.output_cable_loss_db if output_cable_loss_db is None else output_cable_loss_db
        )
        attenuator = (
            self.output_attenuator_db if output_attenuator_db is None else output_attenuator_db
        )
        safe_stop = min(
            self.stop_dbm,
            self.max_safe_generator_power_dbm(
                expected_dut_gain_db=gain,
                output_cable_loss_db=output_loss,
                output_attenuator_db=attenuator,
            ),
        )
        if safe_stop < self.start_dbm:
            raise ValueError(
                "PA sweep has no safe points for the current fixture: "
                f"safe_stop={safe_stop:g} dBm, start={self.start_dbm:g} dBm"
            )
        # 實體 attenuator 與儀器 EATT 分開：前者只用於 Pout/Gain，後者才寫入 CMP180。
        return {
            "axis": "power",
            "frequency_hz": self.frequency_hz,
            "start_dbm": self.start_dbm,
            "stop_dbm": safe_stop,
            "profile_stop_dbm": self.stop_dbm,
            "step_dbm": self.step_db,
            "dwell_ms": self.dwell_ms,
            "cable_confirmation": self.route,
            "input_cable_loss_db": input_loss,
            "output_cable_loss_db": output_loss,
            "external_gain_db": 0.0,
            "expected_dut_gain_db": gain,
            "output_attenuator_db": attenuator,
            "external_attenuation_db": self.measurement_external_attenuation_db,
            "sa_safe_limit_dbm": self.sa_safe_limit_dbm,
            "profile_id": self.profile_id,
            "profile_revision": self.revision,
            "dut_id": dut_id,
            "safe_stop_clipped": safe_stop < self.stop_dbm,
            "worst_case_rf_input_dbm": self.worst_case_rf_input_dbm(
                stop_dbm=safe_stop,
                expected_dut_gain_db=gain,
                output_cable_loss_db=output_loss,
                output_attenuator_db=attenuator,
            ),
        }


def _require_number(data: dict[str, Any], name: str) -> float:
    try:
        return float(data[name])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"PA sweep profile requires numeric {name}") from exc


def load_pa_sweep_profile(path: Path) -> PaSweepProfile:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("PA sweep profile must be a YAML object")
    profile = PaSweepProfile(
        profile_id=str(payload["profile_id"]),
        revision=str(payload["revision"]),
        lifecycle=str(payload["lifecycle"]),
        route=str(payload["route"]),
        frequency_hz=_require_number(payload, "frequency_hz"),
        start_dbm=_require_number(payload, "start_dbm"),
        stop_dbm=_require_number(payload, "stop_dbm"),
        step_db=_require_number(payload, "step_db"),
        dwell_ms=int(_require_number(payload, "dwell_ms")),
        expected_dut_gain_db=_require_number(payload, "expected_dut_gain_db"),
        input_cable_loss_db=_require_number(payload, "input_cable_loss_db"),
        output_cable_loss_db=_require_number(payload, "output_cable_loss_db"),
        output_attenuator_db=_require_number(payload, "output_attenuator_db"),
        measurement_external_attenuation_db=_require_number(
            payload, "measurement_external_attenuation_db"
        ),
        sa_safe_limit_dbm=_require_number(payload, "sa_safe_limit_dbm"),
        approved_by=str(payload.get("approved_by") or ""),
        approved_at=date.fromisoformat(str(payload["approved_at"])),
        source_evidence=str(payload.get("source_evidence") or ""),
    )
    if profile.lifecycle != "approved":
        raise ValueError("PA sweep profile must be approved before RF use")
    if not profile.approved_by or not profile.source_evidence:
        raise ValueError("Approved PA sweep profile requires approved_by and source_evidence")
    if profile.route != "RF1.1-RF1.5":
        raise ValueError("Only RF1.1-RF1.5 is approved for this PA sweep profile")
    if profile.step_db <= 0 or profile.stop_dbm < profile.start_dbm:
        raise ValueError("PA sweep stop must follow start and step must be positive")
    if not 50 <= profile.dwell_ms <= 5000:
        raise ValueError("PA sweep dwell_ms must stay within 50..5000")
    if profile.output_attenuator_db < 0 or profile.measurement_external_attenuation_db < 0:
        raise ValueError("PA sweep attenuation values cannot be negative")
    if profile.max_safe_generator_power_dbm() < profile.start_dbm:
        raise ValueError("PA sweep profile has no safe points with its default fixture")
    return profile
