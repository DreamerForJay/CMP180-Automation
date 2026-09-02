"""Versioned RF path-loss calibration profiles with bounded interpolation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class CalibrationPoint:
    frequency_hz: float
    loss_db: float


@dataclass(frozen=True)
class CalibrationProfile:
    profile_id: str
    revision: str
    lifecycle: str
    route: str
    calibrated_at: date
    expires_at: date
    equipment_reference: str
    points: tuple[CalibrationPoint, ...]
    source_evidence: str | None = None
    approved_by: str | None = None
    approved_at: date | None = None

    def __post_init__(self) -> None:
        if self.lifecycle not in {"draft", "approved"}:
            raise ValueError("Calibration lifecycle must be 'draft' or 'approved'")
        if self.expires_at < self.calibrated_at:
            raise ValueError("Calibration expiry cannot precede calibration date")
        if len(self.points) < 2:
            raise ValueError("Calibration requires at least two frequency points")
        frequencies = [point.frequency_hz for point in self.points]
        if frequencies != sorted(frequencies) or len(frequencies) != len(set(frequencies)):
            raise ValueError("Calibration frequencies must be unique and strictly increasing")
        if any(point.frequency_hz <= 0 or not 0 <= point.loss_db <= 30 for point in self.points):
            raise ValueError("Calibration points exceed the 0..30 dB safety envelope")
        if self.lifecycle == "approved":
            # 正式修正會改變量測參考面；核准者與原始證據缺一不可，禁止只改 lifecycle。
            if not self.source_evidence or not self.approved_by or self.approved_at is None:
                raise ValueError(
                    "Approved calibration requires source_evidence, approved_by, and approved_at"
                )
            if "draft" in self.equipment_reference.lower():
                raise ValueError("Approved calibration cannot use a draft equipment reference")

    def loss_at(self, frequency_hz: float) -> float:
        """Linearly interpolate in-range loss; extrapolation is intentionally blocked."""
        if (
            frequency_hz < self.points[0].frequency_hz
            or frequency_hz > self.points[-1].frequency_hz
        ):
            raise ValueError("Frequency is outside the calibrated range; extrapolation is blocked")
        for left, right in zip(self.points, self.points[1:]):
            if frequency_hz == left.frequency_hz:
                return left.loss_db
            if left.frequency_hz <= frequency_hz <= right.frequency_hz:
                ratio = (frequency_hz - left.frequency_hz) / (
                    right.frequency_hz - left.frequency_hz
                )
                return round(left.loss_db + ratio * (right.loss_db - left.loss_db), 6)
        return self.points[-1].loss_db

    def expected_analyzer_input_dbm(self, source_power_dbm: float, frequency_hz: float) -> float:
        # 被動路徑 loss 為正值；Analyzer 預期輸入 = Source power - path loss。
        return round(source_power_dbm - self.loss_at(frequency_hz), 6)

    def is_expired(self, on_date: date | None = None) -> bool:
        return (on_date or date.today()) > self.expires_at

    def require_approved_for_use(self, on_date: date | None = None) -> None:
        """Block measurement correction unless the profile is approved and current."""
        # Draft 僅供建置與審查，不得讓 0 dB 佔位值成為正式量測修正。
        if self.lifecycle != "approved":
            raise ValueError("Calibration profile is not approved for measurement use")
        if self.is_expired(on_date):
            raise ValueError("Calibration profile is expired")

    def snapshot(self) -> dict[str, object]:
        payload = asdict(self)
        payload["calibrated_at"] = self.calibrated_at.isoformat()
        payload["expires_at"] = self.expires_at.isoformat()
        return payload


def load_calibration_profile(path: Path) -> CalibrationProfile:
    data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("points"), list):
        raise ValueError("Calibration profile must contain a points list")
    points = tuple(CalibrationPoint(**point) for point in data.pop("points"))
    # YAML parser 可能回傳 date，JSON-compatible YAML 則回傳 ISO 字串；統一成 date。
    for field in ("calibrated_at", "expires_at", "approved_at"):
        if isinstance(data.get(field), str):
            data[field] = date.fromisoformat(data[field])
    return CalibrationProfile(points=points, **data)
