import pytest

from cmp180_evm.workflow.frequency_conversion import (
    UDBOX_0630_LIMITS,
    ConversionPlan,
    ConverterLimits,
    build_converter_limits,
)


def _plan(**overrides) -> ConversionPlan:
    payload = {
        "direction": "up",
        "sideband": "high",
        "if_frequency_hz": 1_000_000_000.0,
        "lo_frequency_hz": 6_000_000_000.0,
    }
    payload.update(overrides)
    return ConversionPlan(**payload)


def test_high_side_up_conversion_splits_generator_and_analyzer_frequencies():
    plan = _plan()
    assert plan.rf_frequency_hz == 7_000_000_000.0
    # up-conversion：generator 停在 IF、analyzer 停在 RF，兩者不得相同。
    assert plan.generator_frequency_hz == 1_000_000_000.0
    assert plan.analyzer_frequency_hz == 7_000_000_000.0
    assert plan.generator_frequency_hz != plan.analyzer_frequency_hz


def test_high_side_plan_reports_observable_mirror_and_lo_leakage():
    plan = _plan()
    public = plan.public()
    assert public["mirror_frequency_hz"] == 5_000_000_000.0
    assert public["mirror_observable"] is True
    assert public["lo_leakage_observable"] is True


def test_udbox_0630_reference_plan_passes_validation():
    assert _plan().validate(UDBOX_0630_LIMITS) == []


def test_down_conversion_solves_if_from_the_swept_rf_frequency():
    plan = ConversionPlan.from_generator_frequency(
        generator_frequency_hz=7_000_000_000.0,
        lo_frequency_hz=6_000_000_000.0,
        sideband="high",
        direction="down",
    )
    assert plan.if_frequency_hz == 1_000_000_000.0
    # down-conversion：generator 送 RF、analyzer 收 IF，角色與 up 相反。
    assert plan.generator_frequency_hz == 7_000_000_000.0
    assert plan.analyzer_frequency_hz == 1_000_000_000.0


def test_low_side_injection_below_converter_rf_minimum_is_rejected():
    plan = _plan(sideband="low", lo_frequency_hz=7_000_000_000.0)
    assert plan.rf_frequency_hz == 6_000_000_000.0
    assert plan.validate(UDBOX_0630_LIMITS) == []
    # LO 再低一點 RF 就掉出 UDBox 的 6 GHz 下限。
    too_low = _plan(sideband="low", lo_frequency_hz=6_500_000_000.0)
    reasons = too_low.validate(UDBOX_0630_LIMITS)
    assert any("converter RF range" in reason for reason in reasons)


def test_rf_above_cmp180_range_is_rejected_even_when_converter_supports_it():
    plan = _plan(lo_frequency_hz=8_000_000_000.0)
    # RF 9 GHz 在 UDBox 範圍內，但 CMP180 analyzer 調不到。
    assert plan.rf_frequency_hz == 9_000_000_000.0
    reasons = plan.validate(UDBOX_0630_LIMITS)
    assert any("Analyzer frequency" in reason for reason in reasons)
    assert not any("converter RF range" in reason for reason in reasons)


def test_low_side_lo_below_if_reports_non_positive_frequency():
    plan = _plan(sideband="low", lo_frequency_hz=500_000_000.0)
    reasons = plan.validate(UDBOX_0630_LIMITS)
    assert len(reasons) == 1
    assert "non-positive frequency" in reasons[0]


def test_if_outside_converter_range_is_reported_separately():
    plan = _plan(if_frequency_hz=500_000_000.0, lo_frequency_hz=6_000_000_000.0)
    reasons = plan.validate(UDBOX_0630_LIMITS)
    assert any("converter IF range" in reason for reason in reasons)


def test_invalid_direction_or_sideband_is_rejected_at_construction():
    with pytest.raises(ValueError, match="direction"):
        _plan(direction="sideways")
    with pytest.raises(ValueError, match="sideband"):
        _plan(sideband="middle")


def test_converter_limits_default_to_udbox_and_accept_overrides():
    assert build_converter_limits(None) == UDBOX_0630_LIMITS
    custom = build_converter_limits({"if_min_hz": 2_000_000_000.0})
    assert isinstance(custom, ConverterLimits)
    assert custom.if_min_hz == 2_000_000_000.0
    # 未覆寫的欄位維持 UD Box 0630 預設，避免部分設定造成靜默的空範圍。
    assert custom.rf_max_hz == UDBOX_0630_LIMITS.rf_max_hz
