"""Draft RF result-limit profiles and deterministic point evaluation."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class LimitProfile:
    profile_id: str
    revision: str
    lifecycle: str
    description: str
    maximum_evm_db: float
    maximum_absolute_frequency_error_hz: float
    maximum_absolute_power_error_db: float

    def __post_init__(self) -> None:
        # Draft 與正式 profile 必須明確分流；未經核准的檔案不可產生 compliance PASS。
        if self.lifecycle not in {"draft", "approved"}:
            raise ValueError("Limit profile lifecycle must be 'draft' or 'approved'")
        if not self.profile_id.strip() or not self.revision.strip():
            raise ValueError("Limit profile ID and revision are required")
        if self.maximum_absolute_frequency_error_hz <= 0:
            raise ValueError("Frequency-error limit must be positive")
        if self.maximum_absolute_power_error_db <= 0:
            raise ValueError("Power-error limit must be positive")

    def snapshot(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class LimitEvaluation:
    overall_status: str
    evm_status: str
    frequency_error_status: str
    power_error_status: str
    evm_margin_db: float | None
    frequency_error_margin_hz: float | None
    power_error_margin_db: float | None


# 實機與模擬共用同一份 profile；任何路徑都不得自行複製一套 PASS/FAIL 判定。
# lifecycle 為 draft，因此結果只會標示 DRAFT_PASS／DRAFT_FAIL，不可當成 DUT compliance。
DRAFT_LOOPBACK_LIMIT_PROFILE = LimitProfile(
    profile_id="draft-eht-mcs11-bw320-loopback",
    revision="0.1-draft",
    lifecycle="draft",
    description="Development-only example; not DUT compliance",
    maximum_evm_db=-32.0,
    maximum_absolute_frequency_error_hz=1000.0,
    maximum_absolute_power_error_db=3.0,
)


def load_limit_profile(path: Path) -> LimitProfile:
    data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Limit profile must be a YAML object")
    return LimitProfile(**data)


def evaluate_limits(
    profile: LimitProfile,
    *,
    evm_db: float,
    frequency_error_hz: float,
    measured_power_dbm: float,
    expected_power_dbm: float,
) -> LimitEvaluation:
    values = (evm_db, frequency_error_hz, measured_power_dbm, expected_power_dbm)
    if not all(math.isfinite(value) for value in values):
        return LimitEvaluation("INVALID", "INVALID", "INVALID", "INVALID", None, None, None)

    evm_margin = profile.maximum_evm_db - evm_db
    frequency_margin = profile.maximum_absolute_frequency_error_hz - abs(frequency_error_hz)
    power_error = measured_power_dbm - expected_power_dbm
    power_margin = profile.maximum_absolute_power_error_db - abs(power_error)
    statuses = (
        "PASS" if evm_margin >= 0 else "FAIL",
        "PASS" if frequency_margin >= 0 else "FAIL",
        "PASS" if power_margin >= 0 else "FAIL",
    )
    passed = all(status == "PASS" for status in statuses)
    # Draft 結果只能稱為 DRAFT_PASS／DRAFT_FAIL，避免與正式 DUT compliance 混淆。
    prefix = "DRAFT_" if profile.lifecycle == "draft" else ""
    return LimitEvaluation(
        f"{prefix}{'PASS' if passed else 'FAIL'}",
        statuses[0],
        statuses[1],
        statuses[2],
        round(evm_margin, 6),
        round(frequency_margin, 6),
        round(power_margin, 6),
    )
