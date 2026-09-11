"""Parse user-defined sweep inputs through the non-bypassable workflow safety envelope."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from decimal import Decimal

from cmp180_evm.runtime import project_root
from cmp180_evm.utils.exceptions import SafetyGuardError
from cmp180_evm.web.capabilities import load_capability_profile
from cmp180_evm.workflow.frequency_sweep import (
    DIRECT_LOOPBACK_MAXIMUM_GENERATOR_POWER_DBM,
    FrequencySweepPlan,
)
from cmp180_evm.workflow.power_sweep import PowerSweepPlan
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan
from cmp180_evm.workflow.wlan_bands import (
    INSTRUMENT_MAXIMUM_FREQUENCY_HZ,
    INSTRUMENT_MINIMUM_FREQUENCY_HZ,
    describe_capability,
    reject_unsupported_plan,
)

# 只保護瀏覽器／伺服器不被誤填的極小 step 卡死，不是 RF 安全上限；
# 真正能送 RF 的點數仍由 FrequencySweepPlan／PowerSweepPlan 的硬性包絡把關。
MAXIMUM_PLANNING_PREVIEW_POINTS = 100_000
CAPABILITY_PROFILE_PATH = (
    project_root()
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
    band_supported: bool = True

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
            "rejection_help": _wlan_rejection_help(self.rejection_reason),
            "correct_range": _wlan_correct_range(),
            "capability": describe_capability(),
            "gate": "READY" if self.execution_allowed else "BLOCKED_BY_INSTRUMENT_LIMITS",
            # 非標準 WLAN band／頻寬組合仍可執行，但 CMP180 多半會回 INV；
            # 這裡只做提醒，不阻擋操作員蒐集資料。
            "band_supported": self.band_supported,
            "band_warning": None if self.band_supported else _BAND_WARNING,
        }


_BAND_WARNING = (
    "This frequency/bandwidth combination is outside the standard WLAN channel plan. "
    "The run is allowed, but the CMP180 will most likely return INV instead of a "
    "usable demodulation result."
)


def _wlan_correct_range() -> str:
    return (
        "Execution is limited only by what the instrument can physically accept: "
        "distinct generator/analyzer ports, center frequency 400 MHz..8 GHz, WLAN "
        "bandwidth 20/40/80/160/320 MHz, and dwell 0.01..10 s. Generator power is "
        "whatever the operator sets for the confirmed cabling and attenuation."
    )


def _wlan_rejection_help(reason: str | None) -> str | None:
    if not reason:
        return None
    text = reason.lower()
    if "port" in text:
        return "Generator and analyzer must use different RF ports."
    if "frequency" in text:
        return "Keep the center/sweep frequencies inside the CMP180 400 MHz..8 GHz tuning range."
    if "bandwidth" in text:
        return "Choose a bandwidth the CMP180 can demodulate: 20, 40, 80, 160, or 320 MHz."
    if "dwell" in text:
        return "Set dwell inside 0.01..10 s so each point has enough settling time."
    if "operator" in text:
        return "Confirm cabling and operator presence before the plan can transmit RF."
    if "point" in text or "step" in text:
        return "Increase the step size so the plan does not create an unusable number of points."
    return "Adjust the rejected field and run Review again; no RF is transmitted until the gate passes."


def _fingerprint(payload: dict[str, object]) -> tuple[str, str]:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12].upper()
    return digest, f"EXECUTE-CUSTOM-{digest}"


def _inclusive_points(start: float, stop: float, step: float) -> tuple[float, ...]:
    if step <= 0 or stop < start:
        raise ValueError("Sweep stop must follow start and step must be positive")
    # 十進位輸入不可用浮點整除計數，否則 1 / 0.1 會漏掉合法終點。
    first, last, increment = map(lambda value: Decimal(str(value)), (start, stop, step))
    count = int((last - first) // increment) + 1
    if count > MAXIMUM_PLANNING_PREVIEW_POINTS:
        raise ValueError(
            f"Planning preview exceeds {MAXIMUM_PLANNING_PREVIEW_POINTS} points"
        )
    return tuple(float(first + index * increment) for index in range(count))


def _requested_power_ceiling(data: dict[str, object], requested_dbm: float) -> float:
    """Return the effective ceiling of the supported WLAN execution path."""
    # WLAN 實機入口仍使用 -30 dBm 上限；預览必須提前擋下，操作員只能進一步縮小上限。
    declared = data.get("maximum_generator_power_dbm")
    if declared is None:
        return DIRECT_LOOPBACK_MAXIMUM_GENERATOR_POWER_DBM
    return min(float(declared), DIRECT_LOOPBACK_MAXIMUM_GENERATOR_POWER_DBM)



def _gate(
    plan: FrequencySweepPlan | PowerSweepPlan,
    *,
    frequencies_hz: tuple[float, ...],
    bandwidth_hz: float,
) -> tuple[bool, str | None, bool]:
    """Check only what the instrument can physically accept.

    Returns (execution_allowed, rejection_reason, band_supported). HIL／approved
    profile 證據不再參與判定；未經 HIL 的組合一樣可以實際量測。
    """
    try:
        # 規劃階段就呼叫實際執行時的同一份檢查，預覽才不會與執行結果不一致。
        # 這一層只涵蓋儀器物理限制：port 互斥、調諧範圍、可解調頻寬、dwell、
        # 以及呼叫端自行指定的功率上限。
        plan.frequencies() if isinstance(plan, FrequencySweepPlan) else plan.powers()
    except (SafetyGuardError, ValueError) as exc:
        return False, str(exc), True
    # 非標準 WLAN channel plan 不再阻擋執行，只回報提醒：CMP180 多半會回 INV，
    # 但操作員仍可自行決定要不要實際量一次來蒐集資料。
    band_supported = not reject_unsupported_plan(
        frequencies_hz=frequencies_hz, bandwidth_hz=bandwidth_hz
    )
    return True, None, band_supported


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
            _requested_power_ceiling(data, generator_power_dbm),
        )
        plan = FrequencySweepPlan(
            single=single,
            start_frequency_hz=start_hz,
            stop_frequency_hz=stop_hz,
            step_frequency_hz=step_hz,
            dwell_time_s=dwell_time_s,
        )
        execution_allowed, rejection_reason, band_supported = _gate(
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
            band_supported,
        )
    if axis == "power":
        center_frequency_hz = float(data.get("center_frequency_hz", 6_105_000_000))
        start_dbm = float(data["start_dbm"])
        stop_dbm = float(data["stop_dbm"])
        step_dbm = float(data["step_dbm"])
        points = _inclusive_points(start_dbm, stop_dbm, step_dbm)
        # 上限必須以宣告的 stop 為準（step 未整除時最後一點會低於 stop），
        # 否則計畫會被自己的上限擋下。
        power_ceiling = _requested_power_ceiling(data, stop_dbm)
        single = SingleMeasurementPlan(
            "RF1.1", "RF1.5", center_frequency_hz, bandwidth_hz,
            start_dbm, -20, 0, True,
            power_ceiling,
        )
        plan = PowerSweepPlan(
            single=single,
            start_power_dbm=start_dbm,
            stop_power_dbm=stop_dbm,
            step_power_dbm=step_dbm,
            dwell_time_s=dwell_time_s,
            minimum_power_dbm=start_dbm,
            maximum_power_dbm=power_ceiling,
        )
        execution_allowed, rejection_reason, band_supported = _gate(
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
            band_supported,
        )
    raise ValueError("Sweep axis must be 'frequency' or 'power'")


def build_custom_single_preview(data: dict[str, object]) -> CustomSweepPreview:
    """Validate one SingleShot against the installed CMP180 envelope only."""
    center_frequency_hz = float(data["center_frequency_hz"])
    bandwidth_hz = float(data.get("bandwidth_hz", 320_000_000))
    generator_power_dbm = float(data.get("generator_power_dbm", -40))
    profile = load_capability_profile(CAPABILITY_PROFILE_PATH)
    rejection_reason = None
    if not (
        INSTRUMENT_MINIMUM_FREQUENCY_HZ
        <= center_frequency_hz
        <= INSTRUMENT_MAXIMUM_FREQUENCY_HZ
    ):
        rejection_reason = "SingleShot frequency must stay within the CMP180 400 MHz–8 GHz range"
    elif bandwidth_hz not in profile.installed.analysis_bandwidths_hz:
        # 未安裝的頻寬送出去只會 SCPI 報錯，屬於儀器能力而非核准問題。
        rejection_reason = f"Bandwidth {bandwidth_hz / 1e6:g} MHz is not installed"
    # 預覽與 real_service 的 direct-loopback 上限一致，非有限數字也不得送入 SCPI。
    if not math.isfinite(generator_power_dbm) or generator_power_dbm > DIRECT_LOOPBACK_MAXIMUM_GENERATOR_POWER_DBM:
        rejection_reason = "WLAN generator power must be finite and must not exceed -30 dBm"
    fingerprint, confirmation = _fingerprint(
        {
            "axis": "single",
            "center_frequency_hz": center_frequency_hz,
            "bandwidth_hz": bandwidth_hz,
            "generator_power_dbm": generator_power_dbm,
        }
    )
    band_supported = not reject_unsupported_plan(
        frequencies_hz=(center_frequency_hz,), bandwidth_hz=bandwidth_hz
    )
    return CustomSweepPreview(
        axis="single",
        points=(center_frequency_hz,),
        dwell_time_s=0.1,
        bandwidth_hz=bandwidth_hz,
        generator_power_dbm=generator_power_dbm,
        center_frequency_hz=center_frequency_hz,
        plan_fingerprint=fingerprint,
        required_confirmation=confirmation,
        execution_allowed=rejection_reason is None,
        rejection_reason=rejection_reason,
        band_supported=band_supported,
    )
