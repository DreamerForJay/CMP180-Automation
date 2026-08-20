"""Safety-bounded power sweep built from verified SingleShot cycles.

Mirrors workflow/frequency_sweep.py exactly, but varies generator power at a
fixed frequency instead of varying frequency at a fixed power. This backs
the Web GUI's mock Power Sweep tab only — there is no hardware execution
path yet, matching frequency sweep's own HIL-pending status.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, replace
from typing import Callable

from cmp180_evm.utils.exceptions import SafetyGuardError
from cmp180_evm.workflow.single_measurement import (
    MeasurementBackend,
    SingleMeasurementPlan,
    SingleMeasurementResult,
    run_single_measurement,
)


@dataclass(frozen=True)
class PowerSweepPlan:
    single: SingleMeasurementPlan
    start_power_dbm: float
    stop_power_dbm: float
    step_power_dbm: float
    dwell_time_s: float = 0.1
    maximum_points: int = 11
    minimum_power_dbm: float = -60.0
    maximum_power_dbm: float = -40.0

    def powers(self) -> tuple[float, ...]:
        """Return an inclusive power-level list after all RF safety checks pass."""
        self.single.validate_safety()
        if self.single.generator_port != "RF1.1" or self.single.analyzer_port != "RF1.5":
            raise SafetyGuardError("Power sweep currently permits only RF1.1 to RF1.5.")
        if not 0.1 <= self.dwell_time_s <= 2.0:
            raise SafetyGuardError("Dwell time must be between 0.1 and 2.0 seconds.")
        if self.step_power_dbm <= 0 or self.stop_power_dbm < self.start_power_dbm:
            raise SafetyGuardError("Sweep stop must follow start and step must be positive.")
        if not (
            self.minimum_power_dbm <= self.start_power_dbm
            and self.stop_power_dbm <= self.maximum_power_dbm
        ):
            raise SafetyGuardError(
                f"Sweep power must stay within {self.minimum_power_dbm}..{self.maximum_power_dbm} dBm."
            )
        count = int((self.stop_power_dbm - self.start_power_dbm) // self.step_power_dbm) + 1
        if count > self.maximum_points:
            raise SafetyGuardError(f"Power sweep exceeds {self.maximum_points} points.")
        return tuple(self.start_power_dbm + index * self.step_power_dbm for index in range(count))


@dataclass(frozen=True)
class PowerSweepResult:
    requested_powers_dbm: tuple[float, ...]
    points: tuple[SingleMeasurementResult, ...]
    completed: bool
    failed_power_dbm: float | None = None
    error: str | None = None


def run_power_sweep(
    backend: MeasurementBackend,
    plan: PowerSweepPlan,
    *,
    sleeper: Callable[[float], None] = time.sleep,
) -> PowerSweepResult:
    """Run one cleanup-protected SingleShot per power level and stop on first failure."""
    powers = plan.powers()
    results: list[SingleMeasurementResult] = []
    for index, power_dbm in enumerate(powers):
        point_plan = replace(plan.single, generator_power_dbm=power_dbm)
        try:
            # 每一點都走完整 SingleShot，確保點與點之間 STOP 且 RF Off。
            results.append(run_single_measurement(backend, point_plan))
        except Exception as exc:
            # 保留先前成功點，讓 CSV/JSON 可標示 partial run，而非遺失整批資料。
            return PowerSweepResult(
                requested_powers_dbm=powers,
                points=tuple(results),
                completed=False,
                failed_power_dbm=power_dbm,
                error=f"{type(exc).__name__}: {exc}",
            )
        if index < len(powers) - 1:
            sleeper(plan.dwell_time_s)
    return PowerSweepResult(powers, tuple(results), True)
