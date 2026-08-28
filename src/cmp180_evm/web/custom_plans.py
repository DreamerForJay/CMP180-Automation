"""Parse user-defined sweep inputs through the non-bypassable workflow safety envelope."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from cmp180_evm.utils.exceptions import SafetyGuardError

from cmp180_evm.workflow.frequency_sweep import FrequencySweepPlan
from cmp180_evm.workflow.power_sweep import PowerSweepPlan
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan


@dataclass(frozen=True)
class CustomSweepPreview:
    axis: str
    points: tuple[float, ...]
    dwell_time_s: float
    bandwidth_hz: float
    generator_power_dbm: float | None
    center_frequency_hz: float | None
    plan_fingerprint: str
    required_confirmation: str
    execution_allowed: bool = False

    def public(self) -> dict[str, object]:
        return {
            "axis": self.axis,
            "points": self.points,
            "point_count": len(self.points),
            "dwell_ms": round(self.dwell_time_s * 1000),
            "bandwidth_hz": self.bandwidth_hz,
            "generator_power_dbm": self.generator_power_dbm,
            "center_frequency_hz": self.center_frequency_hz,
            "plan_fingerprint": self.plan_fingerprint,
            "required_confirmation": self.required_confirmation,
            "execution_allowed": self.execution_allowed,
            "gate": (
                "APPROVED_PROFILE_READY"
                if self.execution_allowed
                else "PLANNING_ONLY_REQUIRES_APPROVED_PROFILE"
            ),
        }


def _fingerprint(payload: dict[str, object]) -> tuple[str, str]:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12].upper()
    return digest, f"EXECUTE-CUSTOM-{digest}"


# 只保護瀏覽器／伺服器不被誤填的極小 step 卡死，不是 RF 安全上限；
# 真正能送 RF 的點數仍由 FrequencySweepPlan／PowerSweepPlan 的硬性包絡把關。
MAXIMUM_PLANNING_PREVIEW_POINTS = 100_000


def _inclusive_points(start: float, stop: float, step: float) -> tuple[float, ...]:
    if step <= 0 or stop < start:
        raise ValueError("Sweep stop must follow start and step must be positive")
    count = int((stop - start) // step) + 1
    if count > MAXIMUM_PLANNING_PREVIEW_POINTS:
        raise ValueError(
            f"Planning preview exceeds {MAXIMUM_PLANNING_PREVIEW_POINTS} points"
        )
    return tuple(start + index * step for index in range(count))


def build_custom_sweep_preview(data: dict[str, object]) -> CustomSweepPreview:
    axis = str(data.get("axis") or "")
    bandwidth_hz = float(data.get("bandwidth_hz", 320_000_000))
    dwell_time_s = float(data.get("dwell_ms", 100)) / 1000
    if bandwidth_hz not in {20e6, 40e6, 80e6, 160e6, 320e6}:
        raise ValueError("WLAN bandwidth must be 20, 40, 80, 160, or 320 MHz")
    if not 0.01 <= dwell_time_s <= 10:
        raise ValueError("Planning dwell must be between 10 and 10000 ms")
    if axis == "frequency":
        generator_power_dbm = float(data.get("generator_power_dbm", -40))
        start_hz = float(data["start_hz"])
        stop_hz = float(data["stop_hz"])
        step_hz = float(data["step_hz"])
        if not 400e6 <= start_hz <= stop_hz <= 8e9:
            raise ValueError("CMP180 planning frequency must stay within 400 MHz..8 GHz")
        points = _inclusive_points(start_hz, stop_hz, step_hz)
        single = SingleMeasurementPlan(
            "RF1.1", "RF1.5", start_hz, bandwidth_hz,
            generator_power_dbm, -20, 0, True, -40,
        )
        plan = FrequencySweepPlan(
            single=single,
            start_frequency_hz=start_hz,
            stop_frequency_hz=stop_hz,
            step_frequency_hz=step_hz,
            dwell_time_s=dwell_time_s,
        )
        try:
            plan.frequencies()
            execution_allowed = True
        except (SafetyGuardError, ValueError):
            # 型錄範圍可先建立計畫；只有已核准且通過 HIL 的子集合可以送入 RF workflow。
            execution_allowed = False
        fingerprint, confirmation = _fingerprint(
            {
                "axis": axis,
                "points": points,
                "dwell_time_s": dwell_time_s,
                "bandwidth_hz": bandwidth_hz,
                "generator_power_dbm": generator_power_dbm,
            }
        )
        return CustomSweepPreview(
            axis,
            points,
            dwell_time_s,
            bandwidth_hz,
            generator_power_dbm,
            None,
            fingerprint,
            confirmation,
            execution_allowed,
        )
    if axis == "power":
        center_frequency_hz = float(data.get("center_frequency_hz", 6_105_000_000))
        if not 400e6 <= center_frequency_hz <= 8e9:
            raise ValueError("CMP180 planning frequency must stay within 400 MHz..8 GHz")
        start_dbm = float(data["start_dbm"])
        stop_dbm = float(data["stop_dbm"])
        step_dbm = float(data["step_dbm"])
        points = _inclusive_points(start_dbm, stop_dbm, step_dbm)
        single = SingleMeasurementPlan(
            "RF1.1", "RF1.5", center_frequency_hz, bandwidth_hz,
            start_dbm, -20, 0, True, -40,
        )
        plan = PowerSweepPlan(
            single=single,
            start_power_dbm=start_dbm,
            stop_power_dbm=stop_dbm,
            step_power_dbm=step_dbm,
            dwell_time_s=dwell_time_s,
        )
        try:
            plan.powers()
            execution_allowed = True
        except (SafetyGuardError, ValueError):
            execution_allowed = False
        fingerprint, confirmation = _fingerprint(
            {
                "axis": axis,
                "points": points,
                "dwell_time_s": dwell_time_s,
                "bandwidth_hz": bandwidth_hz,
                "center_frequency_hz": center_frequency_hz,
            }
        )
        return CustomSweepPreview(
            axis,
            points,
            dwell_time_s,
            bandwidth_hz,
            None,
            center_frequency_hz,
            fingerprint,
            confirmation,
            execution_allowed,
        )
    raise ValueError("Sweep axis must be 'frequency' or 'power'")

