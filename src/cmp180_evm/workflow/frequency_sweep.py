"""Frequency sweep built from cleanup-protected SingleShot cycles."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, replace
from decimal import Decimal

from cmp180_evm.results.validity import (
    invalid_critical_fields as _invalid_critical_fields,
)
from cmp180_evm.utils.exceptions import SafetyGuardError
from cmp180_evm.workflow.single_measurement import (
    MeasurementBackend,
    SingleMeasurementPlan,
    SingleMeasurementResult,
    run_single_measurement,
)

# 掃描規劃採 CMP180 WLAN 測試可規劃的型錄頻率範圍；逐點是否真的可量測，
# 仍由 SCPI readback、measurement state 與 error queue 決定。
CMP180_MINIMUM_FREQUENCY_HZ = 400_000_000.0
CMP180_MAXIMUM_FREQUENCY_HZ = 8_000_000_000.0
SUPPORTED_WLAN_BANDWIDTHS_HZ = {
    20_000_000.0,
    40_000_000.0,
    80_000_000.0,
    160_000_000.0,
    320_000_000.0,
}
# 直接 loopback 無外部衰減器時保留輸入保護上限；這不是頻率掃描範圍限制。
DIRECT_LOOPBACK_MAXIMUM_GENERATOR_POWER_DBM = -30.0
MAXIMUM_SWEEP_POINTS = 100_000




@dataclass(frozen=True)
class FrequencySweepPlan:
    single: SingleMeasurementPlan
    start_frequency_hz: float
    stop_frequency_hz: float
    step_frequency_hz: float
    dwell_time_s: float = 0.1
    maximum_points: int = MAXIMUM_SWEEP_POINTS
    minimum_frequency_hz: float = CMP180_MINIMUM_FREQUENCY_HZ
    maximum_frequency_hz: float = CMP180_MAXIMUM_FREQUENCY_HZ
    maximum_span_hz: float | None = None

    def frequencies(self) -> tuple[float, ...]:
        """Return an inclusive point list after RF planning checks pass."""
        self.single.validate_safety()
        if self.single.generator_port == self.single.analyzer_port:
            raise SafetyGuardError("Generator and analyzer ports must be different.")
        if self.single.bandwidth_hz not in SUPPORTED_WLAN_BANDWIDTHS_HZ:
            raise SafetyGuardError("WLAN bandwidth must be 20, 40, 80, 160, or 320 MHz.")
        # 功率上限已由 single.validate_safety() 依 plan 自帶的 maximum_generator_power_dbm
        # 檢查；呼叫端依實際接線宣告上限，這裡不再另外硬寫保守值。
        if not 0.01 <= self.dwell_time_s <= 10.0:
            raise SafetyGuardError("Dwell time must be between 0.01 and 10.0 seconds.")
        if self.step_frequency_hz <= 0 or self.stop_frequency_hz < self.start_frequency_hz:
            raise SafetyGuardError("Sweep stop must follow start and step must be positive.")
        # 呼叫端可以用 capability/profile 縮小範圍，但不能超出 CMP180 型錄規劃範圍。
        effective_minimum = max(self.minimum_frequency_hz, CMP180_MINIMUM_FREQUENCY_HZ)
        effective_maximum = min(self.maximum_frequency_hz, CMP180_MAXIMUM_FREQUENCY_HZ)
        if not (
            effective_minimum
            <= self.start_frequency_hz
            <= self.stop_frequency_hz
            <= effective_maximum
        ):
            raise SafetyGuardError("Sweep frequencies exceed the CMP180 400 MHz..8 GHz range.")
        if (
            self.maximum_span_hz is not None
            and self.stop_frequency_hz - self.start_frequency_hz > self.maximum_span_hz
        ):
            raise SafetyGuardError(f"Sweep span exceeds {self.maximum_span_hz} Hz.")
        # 以十進位計數，保留可整除終點且不補入未整除的 stop。
        first, last, increment = (Decimal(str(value)) for value in (self.start_frequency_hz, self.stop_frequency_hz, self.step_frequency_hz))
        count = int((last - first) // increment) + 1
        # 軟體仍保留很高的防呆上限，避免極小 step 讓 Web job 或瀏覽器記憶體爆掉。
        if count > self.maximum_points:
            raise SafetyGuardError(f"Sweep exceeds {self.maximum_points} points.")
        return tuple(
            float(first + index * increment) for index in range(count)
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
    should_cancel: Callable[[], bool] = lambda: False,
    on_point_complete: Callable[[int, SingleMeasurementResult], None] = lambda _i, _r: None,
    external_attenuation_for: Callable[[float], float] | None = None,
) -> FrequencySweepResult:
    """Run one cleanup-protected SingleShot per frequency and stop on first failure.

    ``external_attenuation_for`` supplies the approved path loss for each frequency so
    results refer to the DUT reference plane. Omitting it keeps the plan's own value.
    """
    frequencies = plan.frequencies()
    results: list[SingleMeasurementResult] = []
    for index, frequency_hz in enumerate(frequencies):
        if should_cancel():
            # 取消只在點與點之間生效；單點內仍由 SingleShot 的 finally 關閉 RF。
            return FrequencySweepResult(frequencies, tuple(results), False, error="Cancelled")
        # Path loss 隨頻率變化，因此每點各自套用已核准的 external attenuation。
        overrides: dict[str, float] = {"center_frequency_hz": frequency_hz}
        if external_attenuation_for is not None:
            overrides["external_attenuation_db"] = external_attenuation_for(frequency_hz)
        point_plan = replace(plan.single, **overrides)
        try:
            # 每個頻點都是完整 SingleShot，確保每點結束都會 STOP 與 RF Off。
            point_result = run_single_measurement(backend, point_plan)
            results.append(point_result)
            on_point_complete(index + 1, point_result)
        except Exception as exc:
            # 失敗時保留已完成點，讓 CSV/JSON 能追溯 partial run。
            return FrequencySweepResult(
                requested_frequencies_hz=frequencies,
                points=tuple(results),
                completed=False,
                failed_frequency_hz=frequency_hz,
                error=f"{type(exc).__name__}: {exc}",
            )
        if point_result.cleanup_errors or point_result.instrument_errors:
            # 儀器 error queue 或 cleanup 異常代表此點不可再往後掃。
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
        invalid_fields = _invalid_critical_fields(point_result.values)
        if invalid_fields:
            # INV/null 不與正常點連線；立即停止，避免把無效量測當趨勢。
            return FrequencySweepResult(
                requested_frequencies_hz=frequencies,
                points=tuple(results),
                completed=False,
                failed_frequency_hz=frequency_hz,
                error=f"Invalid critical result fields: {', '.join(invalid_fields)}",
            )
        if index < len(frequencies) - 1:
            sleeper(plan.dwell_time_s)
    return FrequencySweepResult(frequencies, tuple(results), True)
