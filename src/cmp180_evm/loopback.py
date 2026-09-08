"""Loopback baseline statistics and independent status evaluation."""

from __future__ import annotations

import math
import statistics
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

from cmp180_evm.results.validity import evaluate_point_validity
from cmp180_evm.workflow.single_measurement import (
    MeasurementBackend,
    SingleMeasurementPlan,
    run_single_measurement,
)

CORE_METRICS = ("evm_all_carriers_db", "burst_power_dbm", "frequency_error_hz")


@dataclass(frozen=True)
class LoopbackProfile:
    """Versioned thresholds; ``None`` means deliberately unspecified."""

    profile_id: str = "loopback-unspecified"
    revision: str = "0.1-draft"
    lifecycle: str = "draft"
    minimum_repeats: int = 5
    max_evm_std_db: float | None = None
    max_power_std_db: float | None = None
    max_freq_error_std_hz: float | None = None
    max_invalid_ratio: float | None = None
    expected_power_dbm: float | None = None
    allowed_power_error_db: float | None = None
    source_reference: str | None = None
    approved_by: str | None = None
    approved_at: str | None = None

    def __post_init__(self) -> None:
        # 未核准門檻不可升格為正式 RF baseline；approved 必須可追溯來源與簽核。
        if self.lifecycle not in {"draft", "approved"}:
            raise ValueError("Loopback profile lifecycle must be draft or approved")
        if not 2 <= self.minimum_repeats <= 1000:
            raise ValueError("minimum_repeats must be between 2 and 1000")
        if self.lifecycle == "approved" and not (
            self.source_reference and self.approved_by and self.approved_at
        ):
            raise ValueError("Approved loopback profile requires source and approval metadata")

    def snapshot(self) -> dict[str, object]:
        return asdict(self)


# 2026-09-03 Repeat=10 實機 HIL 通過後核准的單點 baseline；來源 artifact 保留完整
# raw repeat、IQR outlier 與 cleanup 證據，適用範圍仍由下方選擇器嚴格限制。
APPROVED_LOOPBACK_PROFILE = LoopbackProfile(
    profile_id="rf1.1-rf1.5-6105-bw320-loopback-v1",
    revision="1.0-approved",
    lifecycle="approved",
    minimum_repeats=10,
    max_evm_std_db=0.2,
    max_power_std_db=0.1,
    max_freq_error_std_hz=20.0,
    max_invalid_ratio=0.0,
    expected_power_dbm=-40.0,
    allowed_power_error_db=1.0,
    source_reference="output/20260903T101748Z_loopback-validation_865ca580c5",
    approved_by="RF/Test Owner",
    approved_at="2026-09-03",
)

# 代表點沿用已完成 section HIL 的合法中心頻率與安全低功率；每個案例仍需自己的
# Repeat=10 artifact，不能用單一頻點的證據跨頻段核准。
LOOPBACK_BATCH_CASES: tuple[tuple[str, int, int, int], ...] = (
    ("b24-bw20", 2_412_000_000, 20_000_000, -45),
    ("b24-bw40", 2_422_000_000, 40_000_000, -45),
    ("b5-bw20", 5_180_000_000, 20_000_000, -45),
    ("b5-bw40", 5_190_000_000, 40_000_000, -45),
    ("b5-bw80", 5_210_000_000, 80_000_000, -45),
    ("b5-bw160", 5_250_000_000, 160_000_000, -45),
    ("b6-bw20", 5_955_000_000, 20_000_000, -45),
    ("b6-bw40", 5_965_000_000, 40_000_000, -45),
    ("b6-bw80", 5_985_000_000, 80_000_000, -45),
    ("b6-bw160", 6_025_000_000, 160_000_000, -45),
    ("b6-bw320", 6_105_000_000, 320_000_000, -40),
)

_BATCH_APPROVAL_EVIDENCE = {
    "b24-bw20": "output/20260903T104127Z_loopback-validation_b5295954da",
    "b24-bw40": "output/20260903T104138Z_loopback-validation_695541f500",
    "b5-bw20": "output/20260903T104148Z_loopback-validation_4fd421fa05",
    "b5-bw40": "output/20260903T104158Z_loopback-validation_37294e1b0d",
    "b5-bw80": "output/20260903T104210Z_loopback-validation_ad5ec873db",
    "b5-bw160": "output/20260903T104227Z_loopback-validation_7b50078bd6",
    "b6-bw20": "output/20260903T104237Z_loopback-validation_281749d308",
    "b6-bw40": "output/20260903T104247Z_loopback-validation_e912550e50",
    "b6-bw80": "output/20260903T104259Z_loopback-validation_e43a50e7ab",
    "b6-bw160": "output/20260903T104316Z_loopback-validation_2323fc00fd",
}

# 每個核准 profile 僅引用自身 Repeat=10 HIL；320 MHz 保留最早核准的 source evidence。
APPROVED_LOOPBACK_PROFILES: dict[str, tuple[float, float, float, LoopbackProfile]] = {}
for _case_id, _frequency_hz, _bandwidth_hz, _power_dbm in LOOPBACK_BATCH_CASES[:-1]:
    APPROVED_LOOPBACK_PROFILES[_case_id] = (
        float(_frequency_hz),
        float(_bandwidth_hz),
        float(_power_dbm),
        LoopbackProfile(
            profile_id=f"rf1.1-rf1.5-{_case_id}-loopback-v1",
            revision="1.0-approved",
            lifecycle="approved",
            minimum_repeats=10,
            max_evm_std_db=0.2,
            max_power_std_db=0.1,
            max_freq_error_std_hz=20.0,
            max_invalid_ratio=0.0,
            expected_power_dbm=float(_power_dbm),
            allowed_power_error_db=1.0,
            source_reference=_BATCH_APPROVAL_EVIDENCE[_case_id],
            approved_by="RF/Test Owner",
            approved_at="2026-09-03",
        ),
    )
APPROVED_LOOPBACK_PROFILES["b6-bw320"] = (
    6_105_000_000.0,
    320_000_000.0,
    -40.0,
    APPROVED_LOOPBACK_PROFILE,
)


def loopback_batch_requests() -> list[dict[str, object]]:
    """Build isolated Repeat=10 requests for every approved WLAN section."""
    requests: list[dict[str, object]] = []
    for case_id, frequency_hz, bandwidth_hz, power_dbm_int in LOOPBACK_BATCH_CASES:
        power_dbm = float(power_dbm_int)
        requests.append(
            {
                "batch_case_id": case_id,
                "profile_id": f"{case_id}-loopback-draft",
                "profile_revision": "0.1-draft",
                "center_frequency_hz": frequency_hz,
                "bandwidth_hz": bandwidth_hz,
                "generator_power_dbm": power_dbm,
                "repeat_count": 10,
                "minimum_repeats": 10,
                "max_evm_std_db": 0.2,
                "max_power_std_db": 0.1,
                "max_freq_error_std_hz": 20.0,
                "max_invalid_ratio": 0.0,
                "expected_power_dbm": power_dbm,
                "allowed_power_error_db": 1.0,
                "cable_confirmation": "RF1.1-RF1.5",
                "direct_cable_no_attenuator": True,
                "operator_present": True,
            }
        )
    return requests


def _numeric(request: dict[str, object], name: str) -> float | None:
    value = request.get(name)
    return float(value) if isinstance(value, (int, float, str)) else None


def _integer(request: dict[str, object], name: str, default: int) -> int:
    value = request.get(name, default)
    return int(value) if isinstance(value, (int, float, str)) else default


def select_loopback_profile(request: dict[str, object]) -> LoopbackProfile:
    """Select the approved fixed baseline or preserve an editable draft profile."""
    # Approved 僅適用已完成 HIL 的精確 RF 條件；任一可編輯值偏離時降回 draft，
    # 避免使用者輸入被錯誤包裝成 owner-approved baseline。
    route_matches = str(request.get("cable_confirmation", "")) == "RF1.1-RF1.5"
    repeats_sufficient = _integer(request, "repeat_count", 0) >= 10
    for frequency_hz, bandwidth_hz, power_dbm, profile in APPROVED_LOOPBACK_PROFILES.values():
        approved_values = {
            "center_frequency_hz": frequency_hz,
            "bandwidth_hz": bandwidth_hz,
            "generator_power_dbm": power_dbm,
            "max_evm_std_db": profile.max_evm_std_db,
            "max_power_std_db": profile.max_power_std_db,
            "max_freq_error_std_hz": profile.max_freq_error_std_hz,
            "max_invalid_ratio": profile.max_invalid_ratio,
            "expected_power_dbm": profile.expected_power_dbm,
            "allowed_power_error_db": profile.allowed_power_error_db,
        }
        exact_match = all(
            _numeric(request, name) == expected
            for name, expected in approved_values.items()
        )
        if exact_match and route_matches and repeats_sufficient:
            return profile
    return LoopbackProfile(
        profile_id=str(request.get("profile_id") or "web-loopback-draft"),
        revision=str(request.get("profile_revision") or "0.1-draft"),
        lifecycle="draft",
        minimum_repeats=_integer(request, "minimum_repeats", 5),
        max_evm_std_db=_numeric(request, "max_evm_std_db"),
        max_power_std_db=_numeric(request, "max_power_std_db"),
        max_freq_error_std_hz=_numeric(request, "max_freq_error_std_hz"),
        max_invalid_ratio=_numeric(request, "max_invalid_ratio"),
        expected_power_dbm=_numeric(request, "expected_power_dbm"),
        allowed_power_error_db=_numeric(request, "allowed_power_error_db"),
    )


@dataclass(frozen=True)
class MetricStatistics:
    count: int
    mean: float | None
    minimum: float | None
    maximum: float | None
    std_dev: float | None
    value_range: float | None
    max_absolute: float | None

    def public(self) -> dict[str, object]:
        return asdict(self)


def _finite(value: object) -> float | None:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def metric_statistics(values: list[float]) -> MetricStatistics:
    """Calculate repeat statistics using sample standard deviation (ddof=1)."""
    if not values:
        return MetricStatistics(0, None, None, None, None, None, None)
    low, high = min(values), max(values)
    return MetricStatistics(
        len(values),
        statistics.fmean(values),
        low,
        high,
        statistics.stdev(values) if len(values) >= 2 else None,
        high - low,
        max(abs(value) for value in values),
    )


def _quartile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def iqr_outliers(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Flag per-metric IQR outliers without removing or rewriting raw rows."""
    observations: list[dict[str, object]] = []
    for metric in CORE_METRICS:
        samples = [
            (int(row["repeat_index"]), number)
            for row in rows
            if row.get("valid") is True and (number := _finite(row.get(metric))) is not None
        ]
        # IQR 對極小樣本不具足夠辨識力；少於四筆明確不做 outlier 宣稱。
        if len(samples) < 4:
            continue
        numbers = [number for _, number in samples]
        q1, q3 = _quartile(numbers, 0.25), _quartile(numbers, 0.75)
        spread = q3 - q1
        lower, upper = q1 - 1.5 * spread, q3 + 1.5 * spread
        for repeat_index, number in samples:
            if number < lower or number > upper:
                observations.append(
                    {
                        "repeat_index": repeat_index,
                        "metric": metric,
                        "value": number,
                        "method": "IQR_1.5",
                        "lower_fence": lower,
                        "upper_fence": upper,
                    }
                )
    return observations


def analyze_loopback(
    rows: list[dict[str, object]], profile: LoopbackProfile
) -> dict[str, object]:
    """Separate measurement validity, stability, and RF reasonableness."""
    valid_rows = [row for row in rows if row.get("valid") is True]
    stats = {
        metric: metric_statistics(
            [number for row in valid_rows if (number := _finite(row.get(metric))) is not None]
        ).public()
        for metric in CORE_METRICS
    }
    invalid_count = len(rows) - len(valid_rows)
    valid_rate = len(valid_rows) / len(rows) if rows else 0.0
    outliers = iqr_outliers(rows)

    checks: dict[str, str] = {}
    thresholds = {
        "evm_std": (stats["evm_all_carriers_db"]["std_dev"], profile.max_evm_std_db),
        "power_std": (stats["burst_power_dbm"]["std_dev"], profile.max_power_std_db),
        "freq_error_std": (
            stats["frequency_error_hz"]["std_dev"],
            profile.max_freq_error_std_hz,
        ),
        "invalid_ratio": (1.0 - valid_rate, profile.max_invalid_ratio),
    }
    for name, (actual, limit) in thresholds.items():
        checks[name] = (
            "NOT_EVALUATED"
            if actual is None or limit is None
            else "PASS"
            if float(actual) <= limit
            else "FAIL"
        )
    enough_repeats = len(rows) >= profile.minimum_repeats
    evaluated = [status for status in checks.values() if status != "NOT_EVALUATED"]
    stability = (
        "FAIL"
        if "FAIL" in evaluated
        else "PASS"
        if enough_repeats and len(evaluated) == len(checks)
        else "NOT_EVALUATED"
    )

    expected = profile.expected_power_dbm
    measured = stats["burst_power_dbm"]["mean"]
    power_error = None if expected is None or measured is None else float(measured) - expected
    if power_error is None or profile.allowed_power_error_db is None:
        reasonableness = "NOT_EVALUATED"
    else:
        passed = abs(power_error) <= profile.allowed_power_error_db
        prefix = "" if profile.lifecycle == "approved" else "DRAFT_"
        reasonableness = f"{prefix}{'PASS' if passed else 'FAIL'}"

    validity = "PASS" if enough_repeats and invalid_count == 0 else "FAIL"
    # 證據不足只有在沒有任何實質失敗時才成立。validity 與 stability 不需要 RF baseline
    # 即可判定，因此必須優先於 UNVERIFIED，否則 draft profile 會遮蔽真實硬體異常。
    insufficient_evidence = (
        not enough_repeats
        or stability == "NOT_EVALUATED"
        or reasonableness == "NOT_EVALUATED"
        or reasonableness.startswith("DRAFT_")
    )
    if invalid_count and validity == "FAIL":
        overall = "LOOPBACK_INVALID"
    elif stability == "FAIL":
        overall = "LOOPBACK_UNSTABLE"
    elif reasonableness == "FAIL":
        # 只有 approved profile 會產生無前綴 FAIL；draft 門檻不得宣告正式 RF 異常。
        overall = "LOOPBACK_RF_ABNORMAL"
    elif insufficient_evidence:
        overall = "LOOPBACK_UNVERIFIED"
    else:
        overall = "LOOPBACK_READY"
    return {
        "repeat_count": len(rows),
        "valid_count": len(valid_rows),
        "invalid_count": invalid_count,
        "valid_rate": valid_rate,
        "statistics": stats,
        "outliers": outliers,
        "outlier_count": len({item["repeat_index"] for item in outliers}),
        "stability_checks": checks,
        "stability_status": stability,
        "reasonableness_status": reasonableness,
        "validity_status": validity,
        "expected_power_dbm": expected,
        "mean_power_error_db": power_error,
        "overall_status": overall,
        "profile": profile.snapshot(),
        "statistics_convention": "sample_std_dev_ddof_1",
    }


def run_loopback_repeats(
    backend: MeasurementBackend,
    plan: SingleMeasurementPlan,
    repeat_count: int,
    *,
    profile: LoopbackProfile | None = None,
    should_cancel: Callable[[], bool] = lambda: False,
    on_repeat_complete: Callable[[int, dict[str, object]], None] = lambda _i, _r: None,
) -> dict[str, object]:
    """Run independent SingleShot cycles and retain invalid measurements."""
    if not 2 <= repeat_count <= 1000:
        raise ValueError("repeat_count must be between 2 and 1000")
    rows: list[dict[str, object]] = []
    aborted_reason: str | None = None
    for repeat_index in range(1, repeat_count + 1):
        if should_cancel():
            aborted_reason = "Cancelled"
            break
        result = run_single_measurement(backend, plan)
        # 每一筆時間在該次 cleanup 完成後擷取，不能用 artifact 落盤時間代替量測時間。
        validity = evaluate_point_validity(result.values)
        row = {
            "repeat_index": repeat_index,
            "timestamp": datetime.now(UTC).isoformat(),
            "frequency_hz": plan.center_frequency_hz,
            "bandwidth_hz": plan.bandwidth_hz,
            "generator_power_dbm": plan.generator_power_dbm,
            **result.values,
            **validity.public(),
            "instrument_errors": list(result.instrument_errors),
            "cleanup_errors": list(result.cleanup_errors),
        }
        rows.append(row)
        on_repeat_complete(repeat_index, row)
        # INVALID 是 baseline 的觀察值而非立即中止條件；安全 cleanup/SCPI error 才停止後續 RF。
        if result.cleanup_errors or result.instrument_errors:
            aborted_reason = "Instrument or cleanup error"
            break
    analysis = analyze_loopback(rows, profile or LoopbackProfile())
    return {
        "requested_repeats": repeat_count,
        "completed": len(rows) == repeat_count and aborted_reason is None,
        "aborted_reason": aborted_reason,
        "measurements": rows,
        "analysis": analysis,
    }
