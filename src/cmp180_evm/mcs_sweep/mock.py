"""可重現的 EHT MCS sweep synthetic dataset。"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .models import (
    EHT_MCS_DEFINITIONS,
    MCSDataSource,
    MCSHilStatus,
    MCSSweepDataset,
    MCSSweepMetadata,
    MCSSweepPoint,
    validate_mcs_list,
)


@dataclass(frozen=True)
class MockMCSSweepConfig:
    selected_mcs: tuple[int, ...] = tuple(range(12))
    bandwidth_mhz: float = 320.0
    frequency_hz: float = 6_105_000_000.0
    nominal_power_dbm: float = -20.0
    evm_jitter_db: float = 0.35
    power_jitter_db: float = 0.08
    frequency_error_std_hz: float = 25.0
    invalid_rate: float = 0.0
    seed: int = 180

    def __post_init__(self) -> None:
        validate_mcs_list(self.selected_mcs)
        # 頻率使用 Hz、頻寬使用 MHz；先擋下非有限或非正值，避免單位錯誤流入 artifact。
        finite_positive = (self.bandwidth_mhz, self.frequency_hz)
        if not all(math.isfinite(value) and value > 0 for value in finite_positive):
            raise ValueError("Bandwidth and frequency must be finite positive values")
        if not math.isfinite(self.nominal_power_dbm):
            raise ValueError("Nominal power must be finite")
        if not 0 <= self.invalid_rate < 1:
            raise ValueError("Invalid rate must be in [0, 1)")
        if min(self.evm_jitter_db, self.power_jitter_db, self.frequency_error_std_hz) < 0:
            raise ValueError("Mock jitter values must be non-negative")


def generate_mock_mcs_sweep(config: MockMCSSweepConfig) -> MCSSweepDataset:
    """產生趨勢合理但不含 compliance limit 的 synthetic MCS sweep。"""
    selected = validate_mcs_list(config.selected_mcs)
    rng = random.Random(config.seed)
    points: list[MCSSweepPoint] = []
    for mcs_index in selected:
        definition = EHT_MCS_DEFINITIONS[mcs_index]
        invalid = rng.random() < config.invalid_rate
        # 高 MCS 對 impairment 更敏感；此曲線只供軟體驗證，不是標準限值。
        evm_db = -38.0 + 1.18 * mcs_index + rng.gauss(0.0, config.evm_jitter_db)
        power_dbm = config.nominal_power_dbm - 0.025 * mcs_index + rng.gauss(0.0, config.power_jitter_db)
        frequency_error_hz = rng.gauss(0.0, config.frequency_error_std_hz)
        points.append(
            MCSSweepPoint(
                mcs_index=mcs_index,
                modulation=definition.modulation,
                coding_rate=definition.coding_rate,
                bandwidth_mhz=config.bandwidth_mhz,
                frequency_hz=config.frequency_hz,
                evm_db=None if invalid else evm_db,
                power_dbm=None if invalid else power_dbm,
                frequency_error_hz=None if invalid else frequency_error_hz,
                reliability=None if invalid else 0,
                valid=not invalid,
                provenance=("SIMULATED", "DERIVED"),
            )
        )
    valid_count = sum(point.valid for point in points)
    return MCSSweepDataset(
        metadata=MCSSweepMetadata(
            standard="IEEE 802.11be EHT baseline",
            selected_mcs=selected,
            point_count=len(points),
            valid_count=valid_count,
            source=MCSDataSource.MOCK,
            simulated=True,
            hil_status=MCSHilStatus.HIL_PENDING,
        ),
        points=tuple(points),
    )
