"""WLAN band capability table separating instrument RF range from valid sweep range.

儀器 RF 能力（400 MHz–8 GHz）與「有效 WLAN 掃描範圍」是兩件事：後者由
Standard + Band + Channel Bandwidth + ARB waveform 共同決定。同一個 320 MHz
11be waveform 無法掃過整個 400 MHz–8 GHz——2.4 GHz 整個頻段的總寬度就小於 320 MHz。

因此不合法的組合必須在規劃階段就被擋下，而不是送到 CMP180 之後才失敗。
"""

from __future__ import annotations

from dataclasses import dataclass

# 儀器本身的 RF 調諧範圍；僅供 UI 顯示能力上限，不代表可取得有效 WLAN 量測。
INSTRUMENT_MINIMUM_FREQUENCY_HZ = 400_000_000.0
INSTRUMENT_MAXIMUM_FREQUENCY_HZ = 8_000_000_000.0


@dataclass(frozen=True)
class WlanBand:
    key: str
    name: str
    minimum_frequency_hz: float
    maximum_frequency_hz: float
    maximum_bandwidth_hz: float
    # 只有經實機驗證的 band 才填寫 SCPI enum；未驗證者保持 None，不得臆測。
    band_enum: str | None
    band_readback: str | None

    def covers(self, frequency_hz: float) -> bool:
        return self.minimum_frequency_hz <= frequency_hz <= self.maximum_frequency_hz


WLAN_BANDS: dict[str, WlanBand] = {
    # enum/readback 由 scripts/cmp180_band_discovery.py 於 2026-09-01 在韌體 6.0.50.23
    # 實機驗證（全程 RF OFF）。band setter 可用不代表該 band 已可掃描：仍需該 band 專屬
    # 的 ARB waveform 與完整 HIL，並由 approved profile 授權後才會送 RF。
    "2.4GHz": WlanBand(
        "2.4GHz", "2.4 GHz", 2_400_000_000.0, 2_500_000_000.0, 40_000_000.0, "B24GHz", "B24G"
    ),
    "5GHz": WlanBand(
        "5GHz", "5 GHz", 5_150_000_000.0, 5_895_000_000.0, 160_000_000.0, "B5GHz", "B5GH"
    ),
    "6GHz": WlanBand(
        "6GHz", "6 GHz", 5_925_000_000.0, 7_125_000_000.0, 320_000_000.0, "B6GHz", "B6GH"
    ),
}

def describe_capability() -> dict[str, object]:
    """Expose instrument RF capability and the separate valid WLAN band ranges."""
    return {
        "instrument_rf_range_hz": [
            INSTRUMENT_MINIMUM_FREQUENCY_HZ,
            INSTRUMENT_MAXIMUM_FREQUENCY_HZ,
        ],
        "configured_band": "dynamic per sweep",
        # 分段回傳才能保留 2.4／5／6 GHz 間的空隙，不可用單一 min/max 誤導操作員。
        "valid_wlan_ranges_hz": [
            [band.minimum_frequency_hz, band.maximum_frequency_hz]
            for band in WLAN_BANDS.values()
        ],
        "maximum_bandwidth_hz": max(
            band.maximum_bandwidth_hz for band in WLAN_BANDS.values()
        ),
        "verified_bands": [band.key for band in WLAN_BANDS.values() if band.band_enum],
    }


def band_for_frequency(frequency_hz: float) -> WlanBand | None:
    """Return the WLAN band containing this frequency, or None if no band covers it."""
    for band in WLAN_BANDS.values():
        if band.covers(frequency_hz):
            return band
    return None


def executable_band_for(frequency_hz: float) -> WlanBand:
    """Return the band to configure, refusing any band whose SCPI enum is unverified."""
    band = band_for_frequency(frequency_hz)
    if band is None:
        raise ValueError(
            f"{frequency_hz / 1e6:.0f} MHz is outside every supported WLAN band"
        )
    if band.band_enum is None:
        # 未經實機驗證的 band enum 一律不得送出；先完成 scripts/cmp180_band_discovery.py。
        raise ValueError(
            f"The {band.name} WLAN band setter is not hardware-verified yet"
        )
    return band


def reject_unsupported_plan(
    *, frequencies_hz: tuple[float, ...], bandwidth_hz: float
) -> str | None:
    """Return why this plan cannot produce a valid WLAN measurement, or None if it can."""
    bands = {band_for_frequency(value) for value in frequencies_hz}
    if None in bands:
        missing = next(value for value in frequencies_hz if band_for_frequency(value) is None)
        return (
            f"{missing / 1e6:.0f} MHz is outside every supported WLAN band; the instrument "
            f"tunes {INSTRUMENT_MINIMUM_FREQUENCY_HZ / 1e6:.0f}–"
            f"{INSTRUMENT_MAXIMUM_FREQUENCY_HZ / 1e9:.0f} GHz but WLAN measurement needs a band"
        )
    if len(bands) > 1:
        # 單次掃描只載入一個 ARB waveform，跨 band 必須拆成不同批次。
        names = ", ".join(sorted(band.name for band in bands if band))
        return f"Sweep spans multiple WLAN bands ({names}); run one band per sweep"
    band = next(iter(bands))
    assert band is not None
    if band.band_enum is None:
        return (
            f"The {band.name} WLAN band is not hardware-verified yet; run "
            "scripts/cmp180_band_discovery.py and record the enum before sweeping there"
        )
    if bandwidth_hz > band.maximum_bandwidth_hz:
        return (
            f"{bandwidth_hz / 1e6:.0f} MHz bandwidth exceeds the {band.name} band maximum "
            f"of {band.maximum_bandwidth_hz / 1e6:.0f} MHz"
        )
    return None
