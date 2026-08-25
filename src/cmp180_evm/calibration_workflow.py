"""Device-independent path-loss calibration calculation and draft-profile creation."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from cmp180_evm.calibration import CalibrationPoint, CalibrationProfile


@dataclass(frozen=True)
class CalibrationReading:
    frequency_hz: float
    source_reference_dbm: float
    receiver_reading_dbm: float

    @property
    def loss_db(self) -> float:
        # 所有讀值先統一為儀器參考面 dBm；被動路徑損耗 = 發射參考 - 接收讀值。
        return round(self.source_reference_dbm - self.receiver_reading_dbm, 6)


def load_calibration_readings(path: Path) -> tuple[CalibrationReading, ...]:
    """Load reference-plane readings from a CSV exported by an instrument adapter."""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = tuple(
            CalibrationReading(
                frequency_hz=float(row["frequency_hz"]),
                source_reference_dbm=float(row["source_reference_dbm"]),
                receiver_reading_dbm=float(row["receiver_reading_dbm"]),
            )
            for row in csv.DictReader(handle)
        )
    if len(rows) < 2:
        raise ValueError("Calibration CSV requires at least two readings")
    return rows


def build_draft_profile(
    readings: tuple[CalibrationReading, ...],
    *,
    profile_id: str,
    revision: str,
    route: str,
    calibrated_at: date,
    expires_at: date,
    equipment_reference: str,
) -> CalibrationProfile:
    """Convert measured readings into a review-only draft profile."""
    points: list[CalibrationPoint] = []
    for reading in readings:
        loss_db = reading.loss_db
        # 負值通常代表參考面、線材方向或儀器 offset 錯誤，禁止用 abs() 掩蓋問題。
        if not 0 <= loss_db <= 30:
            raise ValueError(
                f"Calculated loss {loss_db:g} dB at {reading.frequency_hz:g} Hz is outside 0..30 dB"
            )
        points.append(CalibrationPoint(reading.frequency_hz, loss_db))
    return CalibrationProfile(
        profile_id=profile_id,
        revision=revision,
        lifecycle="draft",
        route=route,
        calibrated_at=calibrated_at,
        expires_at=expires_at,
        equipment_reference=equipment_reference,
        points=tuple(points),
    )

