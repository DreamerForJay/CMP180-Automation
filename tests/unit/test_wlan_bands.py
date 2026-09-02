from dataclasses import replace

import pytest

from cmp180_evm.workflow import wlan_bands
from cmp180_evm.workflow.wlan_bands import (
    WLAN_BANDS,
    band_for_frequency,
    describe_capability,
    executable_band_for,
    reject_unsupported_plan,
)


def test_band_lookup_matches_each_wlan_band():
    assert band_for_frequency(2_450_000_000).key == "2.4GHz"
    assert band_for_frequency(5_500_000_000).key == "5GHz"
    assert band_for_frequency(6_105_000_000).key == "6GHz"
    # 儀器可調諧但不屬於任何 WLAN band 的頻率。
    assert band_for_frequency(400_000_000) is None


def test_band_setters_verified_on_hardware_2026_09_01():
    """enum 由 scripts/cmp180_band_discovery.py 在韌體 6.0.50.23 實機取得。"""
    assert executable_band_for(2_450_000_000).band_enum == "B24GHz"
    assert executable_band_for(5_500_000_000).band_enum == "B5GHz"
    assert executable_band_for(6_105_000_000).band_enum == "B6GHz"


def test_band_without_a_verified_enum_is_still_refused(monkeypatch):
    unverified = replace(WLAN_BANDS["5GHz"], band_enum=None, band_readback=None)
    monkeypatch.setitem(wlan_bands.WLAN_BANDS, "5GHz", unverified)
    with pytest.raises(ValueError, match="not hardware-verified"):
        executable_band_for(5_500_000_000)


def test_hil_approved_24ghz_section_is_authorized():
    """band setter 與 section HIL 兩者完成後，approved profile 才授權。"""
    from cmp180_evm.web.custom_plans import build_custom_sweep_preview

    preview = build_custom_sweep_preview(
        {
            "axis": "frequency",
            "start_hz": 2_412_000_000,
            "stop_hz": 2_462_000_000,
            "step_hz": 20_000_000,
            "bandwidth_hz": 20_000_000,
            "generator_power_dbm": -40,
            "dwell_ms": 100,
        }
    )
    assert executable_band_for(2_412_000_000).band_enum == "B24GHz"
    assert preview.execution_allowed is True


def test_frequency_outside_every_band_is_refused():
    with pytest.raises(ValueError, match="outside every supported WLAN band"):
        executable_band_for(400_000_000)


def test_verified_six_ghz_plan_is_accepted():
    assert (
        reject_unsupported_plan(
            frequencies_hz=(5_925_000_000, 6_125_000_000), bandwidth_hz=320_000_000
        )
        is None
    )


@pytest.mark.parametrize(
    ("frequencies_hz", "bandwidth_hz", "expected"),
    [
        ((400_000_000,), 320_000_000, "outside every supported WLAN band"),
        ((2_450_000_000,), 80_000_000, "exceeds the 2.4 GHz band maximum"),
        # 單次掃描只載入一個 ARB waveform，跨 band 必須拆批。
        ((5_500_000_000, 6_105_000_000), 160_000_000, "multiple WLAN bands"),
        ((6_105_000_000,), 640_000_000, "exceeds the 6 GHz band maximum"),
    ],
)
def test_unsupported_plans_are_rejected_with_a_reason(frequencies_hz, bandwidth_hz, expected):
    reason = reject_unsupported_plan(
        frequencies_hz=frequencies_hz, bandwidth_hz=bandwidth_hz
    )
    assert reason is not None and expected in reason


def test_capability_separates_instrument_range_from_valid_wlan_range():
    capability = describe_capability()
    assert capability["instrument_rf_range_hz"] == [400_000_000.0, 8_000_000_000.0]
    assert capability["valid_wlan_ranges_hz"] == [
        [2_400_000_000.0, 2_500_000_000.0],
        [5_150_000_000.0, 5_895_000_000.0],
        [5_925_000_000.0, 7_125_000_000.0],
    ]
    # 只有完成 HIL 的 band 才會出現在 verified 清單。
    assert capability["verified_bands"] == ["2.4GHz", "5GHz", "6GHz"]


def test_filling_in_a_verified_enum_unlocks_that_band():
    """band_enum 通過實機驗證填入後，該 band 即自動可設定，不需再改其他程式。"""
    assert executable_band_for(5_500_000_000).band_enum == "B5GHz"
    assert (
        reject_unsupported_plan(frequencies_hz=(5_500_000_000,), bandwidth_hz=160_000_000)
        is None
    )
    # 5 GHz 仍不支援 320 MHz 通道。
    reason = reject_unsupported_plan(
        frequencies_hz=(5_500_000_000,), bandwidth_hz=320_000_000
    )
    assert reason is not None and "exceeds the 5 GHz band maximum" in reason
