import pytest

from cmp180_evm.web.custom_plans import (
    MAXIMUM_PLANNING_PREVIEW_POINTS,
    build_custom_sweep_preview,
)


def test_frequency_preview_marks_approved_user_inputs_executable():
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
    assert preview.public()["execution_allowed"] is True
    assert preview.required_confirmation.startswith("EXECUTE-CUSTOM-")


def test_plan_fingerprint_is_stable_and_changes_with_any_rf_parameter():
    base = {
        "axis": "frequency",
        "start_hz": 6_085_000_000,
        "stop_hz": 6_125_000_000,
        "step_hz": 20_000_000,
        "bandwidth_hz": 320_000_000,
        "generator_power_dbm": -45,
        "dwell_ms": 100,
    }
    first = build_custom_sweep_preview(base)
    assert build_custom_sweep_preview(dict(base)).plan_fingerprint == first.plan_fingerprint
    changed = build_custom_sweep_preview(base | {"generator_power_dbm": -46})
    assert changed.plan_fingerprint != first.plan_fingerprint


def test_preview_accepts_catalog_planning_but_keeps_unapproved_rf_locked():
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
        assert build_custom_sweep_preview(base | change).execution_allowed is False


def test_preview_allows_full_catalog_range_but_rejects_runaway_point_counts():
    # 頻率規劃可涵蓋整個 CMP180 型錄範圍；這個上限只防止誤填極小 step 讓瀏覽器/
    # 伺服器卡死，不是 RF 安全包絡（RF 安全仍由 FrequencySweepPlan 把關）。
    build_custom_sweep_preview(
        {
            "axis": "frequency",
            "start_hz": 400_000_000,
            "stop_hz": 8_000_000_000,
            "step_hz": 100_000,
            "bandwidth_hz": 320_000_000,
            "generator_power_dbm": -40,
            "dwell_ms": 100,
        }
    )
    assert MAXIMUM_PLANNING_PREVIEW_POINTS < 7_600_000_000 / 1_000
    with pytest.raises(ValueError, match="exceeds"):
        build_custom_sweep_preview(
            {
                "axis": "frequency",
                "start_hz": 400_000_000,
                "stop_hz": 8_000_000_000,
                "step_hz": 1_000,
                "bandwidth_hz": 320_000_000,
                "generator_power_dbm": -40,
                "dwell_ms": 100,
            }
        )


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
    assert build_custom_sweep_preview(
            {
                "axis": "power",
                "center_frequency_hz": 6_100_000_000,
                "start_dbm": -55,
                "stop_dbm": -40,
                "step_dbm": 5,
                "bandwidth_hz": 320_000_000,
                "dwell_ms": 100,
            }
        ).execution_allowed is False
