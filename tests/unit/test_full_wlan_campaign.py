from scripts.cmp180_full_wlan_campaign_validate import SECTIONS, WAVEFORMS, selected_sections


def test_campaign_covers_every_installed_bandwidth_and_valid_band_pair():
    assert set(WAVEFORMS) == {20, 40, 80, 160, 320}
    assert len(SECTIONS) == 11
    assert {(section.band, section.bandwidth_mhz) for section in SECTIONS} == {
        ("2.4GHz", 20), ("2.4GHz", 40),
        ("5GHz", 20), ("5GHz", 40), ("5GHz", 80), ("5GHz", 160),
        ("6GHz", 20), ("6GHz", 40), ("6GHz", 80), ("6GHz", 160), ("6GHz", 320),
    }


def test_campaign_uses_low_power_and_bounded_channel_centers():
    total_points = sum(len(section.frequencies_mhz) for section in SECTIONS)
    assert total_points == 176
    assert min(SECTIONS[0].frequencies_mhz) == 2412
    assert max(SECTIONS[-1].frequencies_mhz) == 6905


def test_resume_selects_only_requested_sections_in_campaign_order():
    sections = selected_sections(["6GHz-bw320", "2.4GHz-bw20"])
    assert [section.key for section in sections] == ["2.4GHz-bw20", "6GHz-bw320"]
