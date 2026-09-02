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
        "start_hz": 5_925_000_000,
        "stop_hz": 6_125_000_000,
        "step_hz": 20_000_000,
        "bandwidth_hz": 320_000_000,
        "generator_power_dbm": -45,
        "dwell_ms": 100,
    }
    preview = build_custom_sweep_preview(base)
    assert preview.execution_allowed is True
    assert preview.points[0] == 5_925_000_000
    assert preview.points[-1] == 6_125_000_000
    assert preview.public()["point_count"] == 11

    for change in (
        {"generator_power_dbm": -29},
        {"dwell_ms": 5},
        # 6 GHz band 以外的頻率必須在規劃階段就被擋下，而不是送到 CMP180 才失敗。
        {"start_hz": 5_085_000_000},
        # 320 MHz 以上超出此 band 的通道頻寬能力。
        {"bandwidth_hz": 640_000_000},
    ):
        rejected = build_custom_sweep_preview(base | change)
        assert rejected.execution_allowed is False
        assert rejected.public()["rejection_reason"]


def test_preview_allows_full_catalog_range_but_rejects_runaway_point_counts():
    # 頻率規劃可涵蓋整個 CMP180 型錄範圍；這個上限只防止誤填極小 step 讓瀏覽器/
    # 伺服器卡死，不是 RF 安全包絡（RF 安全仍由 FrequencySweepPlan 把關）。
    preview = build_custom_sweep_preview(
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
    # 儀器 RF 能力涵蓋 400 MHz–8 GHz，所以計畫可以建立並預覽；但有效 WLAN 量測
    # 受 band 限制，因此不可執行，且必須說明原因。
    assert preview.execution_allowed is False
    assert "WLAN band" in (preview.rejection_reason or "")
    assert len(preview.public()["capability"]["valid_wlan_ranges_hz"]) == 3
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


def test_power_preview_accepts_bounded_values_and_blocks_out_of_band_frequency():
    preview = build_custom_sweep_preview(
        {
            "axis": "power",
            "center_frequency_hz": 6_105_000_000,
            "start_dbm": -55,
            "stop_dbm": -35,
            "step_dbm": 3,
            "bandwidth_hz": 320_000_000,
            "dwell_ms": 500,
        }
    )
    assert preview.points == (-55, -52, -49, -46, -43, -40, -37)
    assert preview.execution_allowed is True
    assert build_custom_sweep_preview(
            {
                "axis": "power",
                "center_frequency_hz": 8_100_000_000,
                "start_dbm": -55,
                "stop_dbm": -40,
                "step_dbm": 5,
                "bandwidth_hz": 320_000_000,
                "dwell_ms": 100,
            }
        ).execution_allowed is False
