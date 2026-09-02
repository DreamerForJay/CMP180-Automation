"""Parse user-defined sweep inputs through the non-bypassable workflow safety envelope."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from cmp180_evm.utils.exceptions import SafetyGuardError
from cmp180_evm.web.capabilities import load_capability_profile

from cmp180_evm.workflow.frequency_sweep import (
    DIRECT_LOOPBACK_MAXIMUM_GENERATOR_POWER_DBM,
    FrequencySweepPlan,
)
from cmp180_evm.workflow.power_sweep import PowerSweepPlan
from cmp180_evm.workflow.wlan_bands import describe_capability, reject_unsupported_plan
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan

# 只保護瀏覽器／伺服器不被誤填的極小 step 卡死，不是 RF 安全上限；
# 真正能送 RF 的點數仍由 FrequencySweepPlan／PowerSweepPlan 的硬性包絡把關。
MAXIMUM_PLANNING_PREVIEW_POINTS = 100_000
CAPABILITY_PROFILE_PATH = (
    Path(__file__).resolve().parents[3]
    / "configs"
    / "instrument_capabilities.example.yaml"
)


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
    rejection_reason: str | None = None

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
            # 被擋下時一定要說明原因，操作員才知道要調整哪個參數。
            "rejection_reason": self.rejection_reason,
            "capability": describe_capability(),
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


def _inclusive_points(start: float, stop: float, step: float) -> tuple[float, ...]:
    if step <= 0 or stop < start:
        raise ValueError("Sweep stop must follow start and step must be positive")
    count = int((stop - start) // step) + 1
    if count > MAXIMUM_PLANNING_PREVIEW_POINTS:
        raise ValueError(
            f"Planning preview exceeds {MAXIMUM_PLANNING_PREVIEW_POINTS} points"
        )
    return tuple(start + index * step for index in range(count))


def _gate(
    plan: FrequencySweepPlan | PowerSweepPlan,
    *,
    frequencies_hz: tuple[float, ...],
    bandwidth_hz: float,
) -> tuple[bool, str | None]:
    """Run the workflow safety envelope and report why execution is blocked."""
    try:
        # 規劃階段就呼叫真正的安全檢查，預覽結果才不會與實際執行不一致。
        plan.frequencies() if isinstance(plan, FrequencySweepPlan) else plan.powers()
    except (SafetyGuardError, ValueError) as exc:
        # 型錄範圍可先建立計畫；只有通過安全包絡的組合可以送入 RF workflow。
        return False, str(exc)
    # 儀器 RF 能力涵蓋 400 MHz–8 GHz，但有效 WLAN 量測還受 band 與 waveform 限制；
    # 不合法組合必須在此擋下，而不是送到 CMP180 之後才在 readback 失敗。
    unsupported = reject_unsupported_plan(
        frequencies_hz=frequencies_hz, bandwidth_hz=bandwidth_hz
    )
    if unsupported:
        return False, unsupported
    # Catalog 只允許建立計畫；真正送 RF 前仍必須逐欄套用已留存 HIL 證據的 profile。
    approved = load_capability_profile(CAPABILITY_PROFILE_PATH).approved_profile
    route = f"{plan.single.generator_port}-{plan.single.analyzer_port}"
    if route not in approved.routes:
        return False, f"Route {route} is not included in approved profile {approved.profile_id}"
    # band/bandwidth section 才是 RF 授權單位，避免用 2.4–7.1 GHz 外框誤放行中間空隙。
    section = next(
        (
            item
            for item in approved.sections
            if item.bandwidth_hz == bandwidth_hz
            and all(item.frequency_min_hz <= value <= item.frequency_max_hz for value in frequencies_hz)
        ),
        None,
    )
    if section is None:
        return False, (
            f"Frequency/bandwidth combination is outside the approved WLAN sections "
            f"for {bandwidth_hz / 1e6:.0f} MHz"
        )
    if max(frequencies_hz) - min(frequencies_hz) > approved.maximum_span_hz:
        return False, f"Sweep span exceeds approved {approved.maximum_span_hz / 1e6:.0f} MHz"
    if bandwidth_hz not in approved.bandwidths_hz:
        return False, f"Bandwidth {bandwidth_hz / 1e6:.0f} MHz is not HIL-approved"
    powers = (
        (plan.single.generator_power_dbm,)
        if isinstance(plan, FrequencySweepPlan)
        else plan.powers()
    )
    if not all(
        approved.generator_power_min_dbm <= value <= approved.generator_power_max_dbm
        for value in powers
    ):
        return False, (
            f"Generator power is outside approved {approved.generator_power_min_dbm:g}–"
            f"{approved.generator_power_max_dbm:g} dBm"
        )
    dwell_ms = plan.dwell_time_s * 1000
    if not approved.dwell_min_ms <= dwell_ms <= approved.dwell_max_ms:
        return False, (
            f"Dwell must stay within approved {approved.dwell_min_ms}–"
            f"{approved.dwell_max_ms} ms"
        )
    point_count = len(frequencies_hz if isinstance(plan, FrequencySweepPlan) else powers)
    if point_count > approved.maximum_points:
        return False, f"Plan exceeds the approved {approved.maximum_points}-point campaign size"
    if point_count > section.maximum_points:
        return False, f"Plan exceeds the approved {section.maximum_points}-point size for {section.key}"
    return True, None


def build_custom_sweep_preview(data: dict[str, object]) -> CustomSweepPreview:
    axis = str(data.get("axis") or "")
    bandwidth_hz = float(data.get("bandwidth_hz", 320_000_000))
    dwell_time_s = float(data.get("dwell_ms", 100)) / 1000
    if axis == "frequency":
        generator_power_dbm = float(data.get("generator_power_dbm", -40))
        start_hz = float(data["start_hz"])
        stop_hz = float(data["stop_hz"])
        step_hz = float(data["step_hz"])
        points = _inclusive_points(start_hz, stop_hz, step_hz)
        single = SingleMeasurementPlan(
            "RF1.1", "RF1.5", start_hz, bandwidth_hz,
            generator_power_dbm, -20, 0, True,
            DIRECT_LOOPBACK_MAXIMUM_GENERATOR_POWER_DBM,
        )
        plan = FrequencySweepPlan(
            single=single,
            start_frequency_hz=start_hz,
            stop_frequency_hz=stop_hz,
            step_frequency_hz=step_hz,
            dwell_time_s=dwell_time_s,
        )
        execution_allowed, rejection_reason = _gate(
            plan, frequencies_hz=points, bandwidth_hz=bandwidth_hz
        )
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
            rejection_reason,
        )
    if axis == "power":
        center_frequency_hz = float(data.get("center_frequency_hz", 6_105_000_000))
        start_dbm = float(data["start_dbm"])
        stop_dbm = float(data["stop_dbm"])
        step_dbm = float(data["step_dbm"])
        points = _inclusive_points(start_dbm, stop_dbm, step_dbm)
        single = SingleMeasurementPlan(
            "RF1.1", "RF1.5", center_frequency_hz, bandwidth_hz,
            start_dbm, -20, 0, True,
            DIRECT_LOOPBACK_MAXIMUM_GENERATOR_POWER_DBM,
        )
        plan = PowerSweepPlan(
            single=single,
            start_power_dbm=start_dbm,
            stop_power_dbm=stop_dbm,
            step_power_dbm=step_dbm,
            dwell_time_s=dwell_time_s,
        )
        execution_allowed, rejection_reason = _gate(
            plan, frequencies_hz=(center_frequency_hz,), bandwidth_hz=bandwidth_hz
        )
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
            rejection_reason,
        )
    raise ValueError("Sweep axis must be 'frequency' or 'power'")
