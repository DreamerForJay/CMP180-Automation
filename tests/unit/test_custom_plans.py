import pytest

from cmp180_evm.web.custom_plans import (
    MAXIMUM_PLANNING_PREVIEW_POINTS,
    build_custom_single_preview,
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


def test_single_preview_uses_web_values_and_flags_non_standard_channels():
    preview = build_custom_single_preview(
        {
            "center_frequency_hz": 6_105_000_000,
            "bandwidth_hz": 320_000_000,
            "generator_power_dbm": -45,
        }
    )
    assert preview.points == (6_105_000_000,)
    assert preview.generator_power_dbm == -45
    assert preview.execution_allowed is True
    assert preview.band_supported is True
    assert preview.required_confirmation.startswith("EXECUTE-CUSTOM-")

    # 預覽不可承諾執行端會拒絕的 WLAN 功率。
    high_power = build_custom_single_preview(
        {
            "center_frequency_hz": 6_105_000_000,
            "bandwidth_hz": 320_000_000,
            "generator_power_dbm": -29,
        }
    )
    assert high_power.execution_allowed is False

    # 非標準 WLAN channel plan 只提醒不阻擋；CMP180 可能回 INV，但操作員仍可蒐集資料。
    exploratory = build_custom_single_preview(
        {
            "center_frequency_hz": 400_000_000,
            "bandwidth_hz": 320_000_000,
            "generator_power_dbm": -45,
        }
    )
    assert exploratory.execution_allowed is True
    assert exploratory.band_supported is False
    assert exploratory.public()["gate"] == "READY"
    assert exploratory.public()["band_warning"]


@pytest.mark.parametrize("frequency_hz", [399_999_999, 8_000_000_001])
def test_single_preview_rejects_frequency_outside_cmp180_envelope(frequency_hz):
    preview = build_custom_single_preview(
        {
            "center_frequency_hz": frequency_hz,
            "bandwidth_hz": 20_000_000,
            "generator_power_dbm": -45,
        }
    )
    assert preview.execution_allowed is False
    assert "400 MHz" in (preview.rejection_reason or "")


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


def test_preview_only_blocks_what_the_instrument_cannot_accept():
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

    # 這些以前會被 approved profile 擋下，現在都必須能實際量測。
    for change in (
        # 跨越 5 GHz／6 GHz 的非標準組合只提醒，不再擋下。
        {"start_hz": 5_085_000_000},
        # span 與點數不再受 approved profile 收斂。
        {"stop_hz": 7_125_000_000},
    ):
        allowed = build_custom_sweep_preview(base | change)
        assert allowed.execution_allowed is True, change

    # 儀器物理上做不到的仍必須擋下：dwell 過短、CMP180 無法解調的頻寬。
    for change, fragment in (
        ({"dwell_ms": 5}, "Dwell time"),
        ({"bandwidth_hz": 640_000_000}, "bandwidth"),
    ):
        rejected = build_custom_sweep_preview(base | change)
        assert rejected.execution_allowed is False, change
        assert fragment.lower() in (rejected.rejection_reason or "").lower()


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
    # 涵蓋整個調諧範圍的計畫可以執行；跨越非 WLAN 頻段只會標示 band_supported=False，
    # 由操作員自行判斷是否值得跑（多半會得到 INV）。
    assert preview.execution_allowed is True
    assert preview.band_supported is False
    assert preview.public()["band_warning"]
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


def test_power_preview_runs_full_requested_range_and_respects_tuning_limits():
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

    # 保留要求的點供操作員檢視，但超過實際 WLAN 上限時禁止執行。
    high = build_custom_sweep_preview(
        {
            "axis": "power",
            "center_frequency_hz": 6_105_000_000,
            "start_dbm": -40,
            "stop_dbm": -10,
            "step_dbm": 10,
            "bandwidth_hz": 320_000_000,
            "dwell_ms": 200,
        }
    )
    assert high.execution_allowed is False
    assert high.points == (-40, -30, -20, -10)

    # 超出 CMP180 400 MHz–8 GHz 調諧範圍仍必須擋下。
    out_of_range = build_custom_sweep_preview(
        {
            "axis": "power",
            "center_frequency_hz": 8_100_000_000,
            "start_dbm": -55,
            "stop_dbm": -40,
            "step_dbm": 5,
            "bandwidth_hz": 320_000_000,
            "dwell_ms": 100,
        }
    )
    assert out_of_range.execution_allowed is False
