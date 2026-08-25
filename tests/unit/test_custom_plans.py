import pytest

from cmp180_evm.utils.exceptions import SafetyGuardError
from cmp180_evm.web.custom_plans import build_custom_sweep_preview


def test_frequency_preview_accepts_bounded_user_inputs_but_keeps_rf_locked():
    preview = build_custom_sweep_preview(
        {
            "axis": "frequency",
            "start_hz": 6_085_000_000,
            "stop_hz": 6_125_000_000,
            "step_hz": 10_000_000,
            "bandwidth_hz": 320_000_000,
            "generator_power_dbm": -45,
            "dwell_ms": 200,
        }
    )
    assert preview.points == (
        6_085_000_000,
        6_095_000_000,
        6_105_000_000,
        6_115_000_000,
        6_125_000_000,
    )
    assert preview.public()["execution_allowed"] is False


def test_preview_reuses_hard_bandwidth_power_span_point_and_dwell_guards():
    base = {
        "axis": "frequency",
        "start_hz": 6_085_000_000,
        "stop_hz": 6_125_000_000,
        "step_hz": 20_000_000,
        "bandwidth_hz": 320_000_000,
        "generator_power_dbm": -40,
        "dwell_ms": 100,
    }
    for change in (
        {"bandwidth_hz": 160_000_000},
        {"generator_power_dbm": -39},
        {"dwell_ms": 50},
        {"stop_hz": 6_305_000_000},
        {"step_hz": 1_000_000},
    ):
        with pytest.raises(SafetyGuardError):
            build_custom_sweep_preview(base | change)


def test_power_preview_accepts_bounded_values_and_blocks_wrong_frequency():
    preview = build_custom_sweep_preview(
        {
            "axis": "power",
            "center_frequency_hz": 6_105_000_000,
            "start_dbm": -55,
            "stop_dbm": -40,
            "step_dbm": 3,
            "bandwidth_hz": 320_000_000,
            "dwell_ms": 500,
        }
    )
    assert preview.points == (-55, -52, -49, -46, -43, -40)
    with pytest.raises(SafetyGuardError, match="6105"):
        build_custom_sweep_preview(
            {
                "axis": "power",
                "center_frequency_hz": 6_100_000_000,
                "start_dbm": -55,
                "stop_dbm": -40,
                "step_dbm": 5,
                "bandwidth_hz": 320_000_000,
                "dwell_ms": 100,
            }
        )
