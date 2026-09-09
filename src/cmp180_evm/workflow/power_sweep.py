"""Power sweep built from cleanup-protected SingleShot cycles."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, replace
from decimal import Decimal

from cmp180_evm.results.validity import (
    invalid_critical_fields as _invalid_critical_fields,
)
from cmp180_evm.utils.exceptions import SafetyGuardError
from cmp180_evm.workflow.frequency_sweep import (
    CMP180_MAXIMUM_FREQUENCY_HZ,
    CMP180_MINIMUM_FREQUENCY_HZ,
    DIRECT_LOOPBACK_MAXIMUM_GENERATOR_POWER_DBM,
    MAXIMUM_SWEEP_POINTS,
    SUPPORTED_WLAN_BANDWIDTHS_HZ,
)
from cmp180_evm.workflow.single_measurement import (
    MeasurementBackend,
    SingleMeasurementPlan,
    SingleMeasurementResult,
    run_single_measurement,
)

# 功率下限以儀器常用低功率掃描保守值開放；上限仍由 direct-loopback input protection 控制。
CMP180_PLANNING_MINIMUM_POWER_DBM = -100.0




@dataclass(frozen=True)
class PowerSweepPlan:
    single: SingleMeasurementPlan
    start_power_dbm: float
    stop_power_dbm: float
    step_power_dbm: float
    dwell_time_s: float = 0.1
    maximum_points: int = MAXIMUM_SWEEP_POINTS
    minimum_power_dbm: float = CMP180_PLANNING_MINIMUM_POWER_DBM
    maximum_power_dbm: float = DIRECT_LOOPBACK_MAXIMUM_GENERATOR_POWER_DBM

    def powers(self) -> tuple[float, ...]:
        """Return an inclusive power-level list after RF planning checks pass."""
        self.single.validate_safety()
        if self.single.generator_port == self.single.analyzer_port:
            raise SafetyGuardError("Generator and analyzer ports must be different.")
        if not CMP180_MINIMUM_FREQUENCY_HZ <= self.single.center_frequency_hz <= CMP180_MAXIMUM_FREQUENCY_HZ:
            raise SafetyGuardError("Center frequency exceeds the CMP180 400 MHz..8 GHz range.")
        if self.single.bandwidth_hz not in SUPPORTED_WLAN_BANDWIDTHS_HZ:
            raise SafetyGuardError("WLAN bandwidth must be 20, 40, 80, 160, or 320 MHz.")
        if not 0.01 <= self.dwell_time_s <= 10.0:
            raise SafetyGuardError("Dwell time must be between 0.01 and 10.0 seconds.")
        if self.step_power_dbm <= 0 or self.stop_power_dbm < self.start_power_dbm:
            raise SafetyGuardError("Sweep stop must follow start and step must be positive.")
        # 功率上限由呼叫端依實際接線、衰減器與 DUT 宣告；不再硬寫保守值擋住實際量測。
        effective_maximum = self.maximum_power_dbm
        if not (
            self.minimum_power_dbm <= self.start_power_dbm <= self.stop_power_dbm <= effective_maximum
        ):
            raise SafetyGuardError(
                f"Sweep power must stay within {self.minimum_power_dbm}..{effective_maximum} dBm."
            )
        # 以十進位計數，保留可整除終點且不補入未整除的 stop。
        first, last, increment = (Decimal(str(value)) for value in (self.start_power_dbm, self.stop_power_dbm, self.step_power_dbm))
        count = int((last - first) // increment) + 1
        # 防止極小 step 造成超大 job；這是軟體資源防呆，不是 CMP180 能力限制。
        if count > self.maximum_points:
            raise SafetyGuardError(f"Power sweep exceeds {self.maximum_points} points.")
        return tuple(float(first + index * increment) for index in range(count))


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
    should_cancel: Callable[[], bool] = lambda: False,
    on_point_complete: Callable[[int, SingleMeasurementResult], None] = lambda _i, _r: None,
) -> PowerSweepResult:
    """Run one cleanup-protected SingleShot per power level and stop on first failure."""
    powers = plan.powers()
    results: list[SingleMeasurementResult] = []
    for index, power_dbm in enumerate(powers):
        if should_cancel():
            # 取消只在點與點之間生效，確保不會在 RF On 中途硬切狀態。
            return PowerSweepResult(powers, tuple(results), False, error="Cancelled")
        # expected nominal power 必須維持呼叫端設定值，不可跟隨 generator 功率。
        # 2026-08-28 實機驗收證實：-55 dBm 搭配 expected -55 dBm 會讓 28 個欄位全部
        # 回傳 INV；同樣 -55 dBm 搭配已驗證的 expected -20 dBm 則可量到有效結果。
        point_plan = replace(plan.single, generator_power_dbm=power_dbm)
        try:
            # 每個功率點完整走 configure/RF On/INIT/FETCh/STOP/RF Off。
            point_result = run_single_measurement(backend, point_plan)
            results.append(point_result)
            on_point_complete(index + 1, point_result)
        except Exception as exc:
            # 保留 partial run，避免失敗後看不到已量到的點。
            return PowerSweepResult(
                requested_powers_dbm=powers,
                points=tuple(results),
                completed=False,
                failed_power_dbm=power_dbm,
                error=f"{type(exc).__name__}: {exc}",
            )
        if point_result.cleanup_errors or point_result.instrument_errors:
            # 儀器回報錯誤或 cleanup 失敗時，不繼續送下一個 RF 點。
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
        invalid_fields = _invalid_critical_fields(point_result.values)
        if invalid_fields:
            # INVALID 點必須中斷掃描，不可和正常點相連造成趨勢誤判。
            return PowerSweepResult(
                requested_powers_dbm=powers,
                points=tuple(results),
                completed=False,
                failed_power_dbm=power_dbm,
                error=f"Invalid critical result fields: {', '.join(invalid_fields)}",
            )
        if index < len(powers) - 1:
            sleeper(plan.dwell_time_s)
    return PowerSweepResult(powers, tuple(results), True)
