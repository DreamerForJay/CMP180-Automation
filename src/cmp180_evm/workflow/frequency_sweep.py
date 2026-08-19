"""Safety-bounded frequency sweep built from verified SingleShot cycles."""

from __future__ import annotations

import time
from dataclasses import dataclass, field, replace
from typing import Callable

from cmp180_evm.utils.exceptions import SafetyGuardError
from cmp180_evm.workflow.single_measurement import (
    MeasurementBackend,
    SingleMeasurementPlan,
    SingleMeasurementResult,
    run_single_measurement,
)


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
        if self.single.generator_power_dbm > -40.0:
            raise SafetyGuardError("Short sweep generator power must not exceed -40 dBm.")
        if not 0.1 <= self.dwell_time_s <= 2.0:
            raise SafetyGuardError("Dwell time must be between 0.1 and 2.0 seconds.")
        if self.step_frequency_hz <= 0 or self.stop_frequency_hz < self.start_frequency_hz:
            raise SafetyGuardError("Sweep stop must follow start and step must be positive.")
        if not (
            self.minimum_frequency_hz <= self.start_frequency_hz
            and self.stop_frequency_hz <= self.maximum_frequency_hz
        ):
            raise SafetyGuardError("Sweep frequencies exceed the approved 6 GHz lab range.")
        if self.stop_frequency_hz - self.start_frequency_hz > self.maximum_span_hz:
            raise SafetyGuardError("Short sweep span exceeds 200 MHz.")
        count = int((self.stop_frequency_hz - self.start_frequency_hz) // self.step_frequency_hz) + 1
        if count > self.maximum_points:
            raise SafetyGuardError(f"Short sweep exceeds {self.maximum_points} points.")
        return tuple(self.start_frequency_hz + index * self.step_frequency_hz for index in range(count))


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
            results.append(run_single_measurement(backend, point_plan))
        except Exception as exc:
            # 保留先前成功點，讓 CSV/JSON 可標示 partial run，而非遺失整批資料。
            return FrequencySweepResult(
                requested_frequencies_hz=frequencies,
                points=tuple(results),
                completed=False,
                failed_frequency_hz=frequency_hz,
                error=f"{type(exc).__name__}: {exc}",
            )
        if index < len(frequencies) - 1:
            sleeper(plan.dwell_time_s)
    return FrequencySweepResult(frequencies, tuple(results), True)
