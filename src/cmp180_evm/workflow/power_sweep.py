"""Safety-bounded power sweep built from verified SingleShot cycles.

Mirrors workflow/frequency_sweep.py exactly, but varies generator power at a
fixed frequency instead of varying frequency at a fixed power. This backs
the Web GUI's mock Power Sweep tab only — there is no hardware execution
path yet, matching frequency sweep's own HIL-pending status.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, replace

from cmp180_evm.utils.exceptions import SafetyGuardError
from cmp180_evm.workflow.single_measurement import (
    MeasurementBackend,
    SingleMeasurementPlan,
    SingleMeasurementResult,
    run_single_measurement,
)

# 這些常數是目前唯一允許進入 HIL 的實機安全包絡；呼叫端參數只能縮小範圍，不能放寬。
VERIFIED_POWER_SWEEP_FREQUENCY_HZ = 6_105_000_000.0
VERIFIED_POWER_SWEEP_BANDWIDTH_HZ = 320_000_000.0
VERIFIED_MINIMUM_POWER_DBM = -60.0
VERIFIED_MAXIMUM_POWER_DBM = -40.0
VERIFIED_MAXIMUM_POINTS = 11


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
        if self.single.center_frequency_hz != VERIFIED_POWER_SWEEP_FREQUENCY_HZ:
            raise SafetyGuardError(
                "Power sweep currently permits only the verified 6105 MHz profile."
            )
        if self.single.bandwidth_hz != VERIFIED_POWER_SWEEP_BANDWIDTH_HZ:
            raise SafetyGuardError(
                "Power sweep currently permits only the verified 320 MHz bandwidth."
            )
        if not 0.1 <= self.dwell_time_s <= 2.0:
            raise SafetyGuardError("Dwell time must be between 0.1 and 2.0 seconds.")
        if self.step_power_dbm <= 0 or self.stop_power_dbm < self.start_power_dbm:
            raise SafetyGuardError("Sweep stop must follow start and step must be positive.")
        # 同時套用硬性包絡與呼叫端較嚴格的限制，避免以自訂欄位繞過 -60 至 -40 dBm。
        effective_minimum = max(self.minimum_power_dbm, VERIFIED_MINIMUM_POWER_DBM)
        effective_maximum = min(self.maximum_power_dbm, VERIFIED_MAXIMUM_POWER_DBM)
        if not (
            effective_minimum <= self.start_power_dbm <= self.stop_power_dbm <= effective_maximum
        ):
            raise SafetyGuardError(
                f"Sweep power must stay within {effective_minimum}..{effective_maximum} dBm."
            )
        count = int((self.stop_power_dbm - self.start_power_dbm) // self.step_power_dbm) + 1
        effective_maximum_points = min(self.maximum_points, VERIFIED_MAXIMUM_POINTS)
        if count > effective_maximum_points:
            raise SafetyGuardError(f"Power sweep exceeds {effective_maximum_points} points.")
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
            point_result = run_single_measurement(backend, point_plan)
            results.append(point_result)
        except Exception as exc:
            # 保留先前成功點，讓 CSV/JSON 可標示 partial run，而非遺失整批資料。
            return PowerSweepResult(
                requested_powers_dbm=powers,
                points=tuple(results),
                completed=False,
                failed_power_dbm=power_dbm,
                error=f"{type(exc).__name__}: {exc}",
            )
        if point_result.cleanup_errors or point_result.instrument_errors:
            # 清理或 error queue 異常代表儀器狀態不可信，禁止提高到下一個功率點。
            return PowerSweepResult(
                requested_powers_dbm=powers,
                points=tuple(results),
                completed=False,
                failed_power_dbm=power_dbm,
                error=(
                    f"Point safety errors: instrument={point_result.instrument_errors}, "
                    f"cleanup={point_result.cleanup_errors}"
                ),
            )
        if index < len(powers) - 1:
            sleeper(plan.dwell_time_s)
    return PowerSweepResult(powers, tuple(results), True)
