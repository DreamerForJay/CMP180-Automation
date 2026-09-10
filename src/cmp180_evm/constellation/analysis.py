"""Derived RF metrics for standardized constellation datasets."""

from __future__ import annotations

import math
from statistics import fmean

from .models import ConstellationPoint


def _metric(value: float | int | None, unit: str, provenance: list[str]) -> dict[str, object]:
    return {"value": value, "unit": unit, "provenance": provenance}


def analyze_constellation(
    points: tuple[ConstellationPoint, ...], *, simulated: bool
) -> dict[str, object]:
    """Analyze finite valid points; insufficient fields stay null rather than becoming zero."""
    valid = [
        point
        for point in points
        if point.valid
        and point.i is not None
        and point.q is not None
        and point.ideal_i is not None
        and point.ideal_q is not None
    ]
    provenance = ["SIMULATED", "DERIVED"] if simulated else ["DERIVED"]
    if not valid:
        return {
            "status": "insufficient_data",
            "provenance": provenance,
            "point_count": len(points),
            "valid_count": 0,
            "invalid_count": len(points),
        }

    i_values: list[float] = []
    q_values: list[float] = []
    ideal_values: list[tuple[float, float]] = []
    for point in valid:
        # 上方 valid 篩選已排除缺值；assert 同時讓型別與演算法邊界保持一致。
        assert point.i is not None and point.q is not None
        assert point.ideal_i is not None and point.ideal_q is not None
        i_values.append(point.i)
        q_values.append(point.q)
        ideal_values.append((point.ideal_i, point.ideal_q))
    errors = [
        math.hypot(i_value - ideal_i, q_value - ideal_q)
        for i_value, q_value, (ideal_i, ideal_q) in zip(
            i_values, q_values, ideal_values, strict=True
        )
    ]
    i_rms = math.sqrt(fmean(value * value for value in i_values))
    q_rms = math.sqrt(fmean(value * value for value in q_values))
    rms_evm = math.sqrt(fmean(error * error for error in errors))
    peak_evm = max(errors)
    gain_imbalance_db = 20 * math.log10(i_rms / q_rms) if i_rms > 0 and q_rms > 0 else None

    phase_terms = []
    for i_value, q_value, (ideal_i, ideal_q) in zip(
        i_values, q_values, ideal_values, strict=True
    ):
        measured = complex(i_value, q_value)
        ideal = complex(ideal_i, ideal_q)
        if abs(measured) > 0 and abs(ideal) > 0:
            phase_terms.append(math.atan2((measured * ideal.conjugate()).imag, (measured * ideal.conjugate()).real))
    phase_error_deg = math.degrees(fmean(phase_terms)) if phase_terms else None

    return {
        "status": "complete",
        "provenance": provenance,
        "point_count": len(points),
        "valid_count": len(valid),
        "invalid_count": len(points) - len(valid),
        "rms_evm_percent": _metric(rms_evm * 100, "%", provenance),
        "rms_evm_db": _metric(20 * math.log10(rms_evm) if rms_evm > 0 else None, "dB", provenance),
        "peak_evm_percent": _metric(peak_evm * 100, "%", provenance),
        "i_mean": _metric(fmean(i_values), "normalized", provenance),
        "q_mean": _metric(fmean(q_values), "normalized", provenance),
        "i_rms": _metric(i_rms, "normalized", provenance),
        "q_rms": _metric(q_rms, "normalized", provenance),
        "iq_gain_imbalance_db": _metric(gain_imbalance_db, "dB", provenance),
        "estimated_phase_error_deg": _metric(phase_error_deg, "deg", provenance),
    }
