"""Safety-bounded frequency sweep built from verified SingleShot cycles."""

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

# HIL 前先把可變頻率 workflow 鎖在核准包絡；Plan 欄位不得用來放寬這些硬性限制。
VERIFIED_MINIMUM_FREQUENCY_HZ = 5_925_000_000.0
VERIFIED_MAXIMUM_FREQUENCY_HZ = 7_125_000_000.0
VERIFIED_MAXIMUM_SPAN_HZ = 200_000_000.0
VERIFIED_SWEEP_BANDWIDTH_HZ = 320_000_000.0
VERIFIED_MAXIMUM_GENERATOR_POWER_DBM = -40.0
VERIFIED_MAXIMUM_POINTS = 11


@dataclass(frozen=True)
class FrequencySweepPlan:
    single: SingleMeasurementPlan
    start_frequency_hz: float
    stop_frequency_hz: float
    step_frequency_hz: float
    dwell_time_s: float = 0.1
    maximum_points: int = 11
    minimum_frequency_hz: float = 5_925_000_000
    maximum_frequency_hz: float = 7_125_000_000
    maximum_span_hz: float = 200_000_000

    def frequencies(self) -> tuple[float, ...]:
        """Return an inclusive point list after all RF safety checks pass."""
        self.single.validate_safety()
        if self.single.generator_port != "RF1.1" or self.single.analyzer_port != "RF1.5":
            raise SafetyGuardError("Short sweep currently permits only RF1.1 to RF1.5.")
        if self.single.bandwidth_hz != VERIFIED_SWEEP_BANDWIDTH_HZ:
            raise SafetyGuardError(
                "Short sweep currently permits only the verified 320 MHz bandwidth."
            )
        if self.single.generator_power_dbm > VERIFIED_MAXIMUM_GENERATOR_POWER_DBM:
            raise SafetyGuardError("Short sweep generator power must not exceed -40 dBm.")
        if not 0.1 <= self.dwell_time_s <= 2.0:
            raise SafetyGuardError("Dwell time must be between 0.1 and 2.0 seconds.")
        if self.step_frequency_hz <= 0 or self.stop_frequency_hz < self.start_frequency_hz:
            raise SafetyGuardError("Sweep stop must follow start and step must be positive.")
        # 自訂上下限只能比硬性 6 GHz 包絡更窄，不能把未驗證頻率帶進實機 backend。
        effective_minimum = max(self.minimum_frequency_hz, VERIFIED_MINIMUM_FREQUENCY_HZ)
        effective_maximum = min(self.maximum_frequency_hz, VERIFIED_MAXIMUM_FREQUENCY_HZ)
        if not (
            effective_minimum
            <= self.start_frequency_hz
            <= self.stop_frequency_hz
            <= effective_maximum
        ):
            raise SafetyGuardError("Sweep frequencies exceed the approved 6 GHz lab range.")
        effective_maximum_span = min(self.maximum_span_hz, VERIFIED_MAXIMUM_SPAN_HZ)
        if self.stop_frequency_hz - self.start_frequency_hz > effective_maximum_span:
            raise SafetyGuardError("Short sweep span exceeds 200 MHz.")
        count = (
            int((self.stop_frequency_hz - self.start_frequency_hz) // self.step_frequency_hz) + 1
        )
        effective_maximum_points = min(self.maximum_points, VERIFIED_MAXIMUM_POINTS)
        if count > effective_maximum_points:
            raise SafetyGuardError(f"Short sweep exceeds {effective_maximum_points} points.")
        return tuple(
            self.start_frequency_hz + index * self.step_frequency_hz for index in range(count)
        )


@dataclass(frozen=True)
class FrequencySweepResult:
    requested_frequencies_hz: tuple[float, ...]
    points: tuple[SingleMeasurementResult, ...]
    completed: bool
    failed_frequency_hz: float | None = None
    error: str | None = None


def run_frequency_sweep(
    backend: MeasurementBackend,
    plan: FrequencySweepPlan,
    *,
    sleeper: Callable[[float], None] = time.sleep,
) -> FrequencySweepResult:
    """Run one cleanup-protected SingleShot per frequency and stop on first failure."""
    frequencies = plan.frequencies()
    results: list[SingleMeasurementResult] = []
    for index, frequency_hz in enumerate(frequencies):
        point_plan = replace(plan.single, center_frequency_hz=frequency_hz)
        try:
            # 每一點都走完整 SingleShot，確保點與點之間 STOP 且 RF Off。
            point_result = run_single_measurement(backend, point_plan)
            results.append(point_result)
        except Exception as exc:
            # 保留先前成功點，讓 CSV/JSON 可標示 partial run，而非遺失整批資料。
            return FrequencySweepResult(
                requested_frequencies_hz=frequencies,
                points=tuple(results),
                completed=False,
                failed_frequency_hz=frequency_hz,
                error=f"{type(exc).__name__}: {exc}",
            )
        if point_result.cleanup_errors or point_result.instrument_errors:
            # 清理或 error queue 異常代表儀器狀態不可信，禁止換到下一個頻點。
            return FrequencySweepResult(
                requested_frequencies_hz=frequencies,
                points=tuple(results),
                completed=False,
                failed_frequency_hz=frequency_hz,
                error=(
                    f"Point safety errors: instrument={point_result.instrument_errors}, "
                    f"cleanup={point_result.cleanup_errors}"
                ),
            )
        if index < len(frequencies) - 1:
            sleeper(plan.dwell_time_s)
    return FrequencySweepResult(frequencies, tuple(results), True)
