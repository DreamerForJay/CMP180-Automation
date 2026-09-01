"""Single source of truth for measurement validity and estimator confidence.

三層模型，不可互相取代：

1. Measurement validity  — 這個點的數字是否代表一次成功的量測。
2. Spec compliance       — 有效的數字是否通過限值（見 cmp180_evm.limits）。
3. Estimator confidence  — 個別欄位的估計器是否有足夠 symbol/PPDU 收斂。

「CMP180 有回傳數字」不等於「這個數字有物理意義」，因此第 3 層必須與第 1 層分開：
一個點可以是 valid（EVM/功率/頻率誤差都可信），同時 IQ 估計值不可信。
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

# 任一欄位無效即代表該點不可用於趨勢分析。
CRITICAL_RESULT_FIELDS = ("evm_all_carriers_db", "burst_power_dbm", "frequency_error_hz")

INVALID_RELIABILITY = "INVALID_RELIABILITY"
INVALID_EVM = "INVALID_EVM"
INVALID_POWER = "INVALID_POWER"
INVALID_FREQ_ERROR = "INVALID_FREQ_ERROR"

_FIELD_REASONS = {
    "evm_all_carriers_db": INVALID_EVM,
    "burst_power_dbm": INVALID_POWER,
    "frequency_error_hz": INVALID_FREQ_ERROR,
}

# 儀器內建 Help 對 IQ 類結果的 IEEE 指引：至少 20 個 PPDU，每個至少 16 個 data OFDM symbol。
# 低於此條件時 Gain Imbalance / Quadrature Error 的估計器不會收斂，數值不得當成 RF 結果。
MINIMUM_DATA_SYMBOLS_FOR_IQ_ESTIMATE = 16
MINIMUM_PPDUS_FOR_IQ_ESTIMATE = 20
IQ_ESTIMATE_FIELDS = ("gain_imbalance_db", "quadrature_error_deg")
INSUFFICIENT_SYMBOLS = "insufficient_symbols"
INSUFFICIENT_PPDUS = "insufficient_ppdus"


def _numeric(values: dict[str, object], field: str) -> float | None:
    """Return a finite float, or None for INV/NCAP/NAV/missing instrument sentinels."""
    try:
        number = float(values[field])  # type: ignore[arg-type]
    except (KeyError, TypeError, ValueError):
        return None
    return number if isfinite(number) else None


@dataclass(frozen=True)
class PointValidity:
    """Layer 1: whether this point represents a successful measurement."""

    valid: bool
    reasons: tuple[str, ...]

    def public(self) -> dict[str, object]:
        return {"valid": self.valid, "invalid_reasons": list(self.reasons)}


@dataclass(frozen=True)
class EstimatorConfidence:
    """Layer 3: whether per-field estimators had enough data to converge."""

    estimate_valid: bool
    reason: str | None
    measured_symbols: int | None
    statistic_count: int | None = None

    def public(self) -> dict[str, object]:
        return {
            "estimate_valid": self.estimate_valid,
            "reason": self.reason,
            "measured_symbols": self.measured_symbols,
            "required_symbols": MINIMUM_DATA_SYMBOLS_FOR_IQ_ESTIMATE,
            "required_ppdus": MINIMUM_PPDUS_FOR_IQ_ESTIMATE,
            "affected_fields": list(IQ_ESTIMATE_FIELDS),
        }


def evaluate_point_validity(values: dict[str, object]) -> PointValidity:
    """Return validity plus every reason the point failed, never a bare boolean."""
    reasons: list[str] = []
    # reliability 0 代表儀器認為量測成功；非 0 時即使欄位有數字也不可信。
    reliability = _numeric(values, "reliability")
    if reliability is None or reliability != 0:
        reasons.append(INVALID_RELIABILITY)
    for field in CRITICAL_RESULT_FIELDS:
        if _numeric(values, field) is None:
            reasons.append(_FIELD_REASONS[field])
    return PointValidity(not reasons, tuple(reasons))


def evaluate_estimator_confidence(
    values: dict[str, object],
    *,
    statistic_count: int | None = None,
) -> EstimatorConfidence:
    """Report whether the IQ estimators had enough symbols/PPDUs to be meaningful."""
    symbols = _numeric(values, "measured_symbols")
    measured_symbols = int(symbols) if symbols is not None else None
    if measured_symbols is None or measured_symbols < MINIMUM_DATA_SYMBOLS_FOR_IQ_ESTIMATE:
        return EstimatorConfidence(
            False, INSUFFICIENT_SYMBOLS, measured_symbols, statistic_count
        )
    if statistic_count is not None and statistic_count < MINIMUM_PPDUS_FOR_IQ_ESTIMATE:
        return EstimatorConfidence(False, INSUFFICIENT_PPDUS, measured_symbols, statistic_count)
    return EstimatorConfidence(True, None, measured_symbols, statistic_count)


def invalid_critical_fields(values: dict[str, object]) -> tuple[str, ...]:
    """Return input fields that require an immediate sweep stop."""
    invalid: list[str] = []
    # reliability 非 0 時即使 EVM／功率／頻率誤差為數字也不可繼續掃描；
    # 這裡必須與 evaluate_point_validity() 的 UI 判定共用同一語意。
    reliability = _numeric(values, "reliability")
    if reliability is None or reliability != 0:
        invalid.append("reliability")
    invalid.extend(
        field for field in CRITICAL_RESULT_FIELDS if _numeric(values, field) is None
    )
    return tuple(invalid)
