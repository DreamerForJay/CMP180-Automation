from cmp180_evm.web.gprf_service import build_gprf_power_preview


def test_gprf_frequency_preview_uses_instrument_range_not_wlan_sections():
    preview = build_gprf_power_preview(
        {
            "axis": "frequency",
            "start_hz": 400_000_000,
            "stop_hz": 8_000_000_000,
            "step_hz": 100_000_000,
            "power_dbm": -40,
            "dwell_ms": 200,
        }
    )

    assert preview.execution_allowed is True
    assert preview.public()["measurement_family"] == "GPRF_POWER"
    assert preview.public()["point_count"] == 77
    assert "not WLAN EVM" in preview.public()["disclaimer"]


def test_gprf_preview_blocks_outside_cmp180_planning_range():
    preview = build_gprf_power_preview(
        {
            "axis": "frequency",
            "start_hz": 300_000_000,
            "stop_hz": 500_000_000,
            "step_hz": 100_000_000,
            "power_dbm": -40,
            "dwell_ms": 200,
        }
    )

    assert preview.execution_allowed is False
    assert "400 MHz..8 GHz" in str(preview.rejection_reason)
