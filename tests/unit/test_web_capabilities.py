from pathlib import Path

import pytest
from pydantic import ValidationError

from cmp180_evm.web.capabilities import InstrumentCapabilityProfile, load_capability_profile


def test_example_separates_catalog_from_rf_execution_profile():
    profile = load_capability_profile(Path("configs/instrument_capabilities.example.yaml"))
    public = profile.public()
    assert public["catalog"]["frequency_min_hz"] == 400_000_000
    assert public["approved_profile"]["frequency_min_hz"] == 2_412_000_000
    assert public["approved_profile"]["frequency_max_hz"] == 7_125_000_000
    assert public["approved_profile"]["maximum_span_hz"] == 1_200_000_000
    assert public["approved_profile"]["generator_power_max_dbm"] == -30
    assert public["approved_profile"]["maximum_points"] == 59
    assert len(public["approved_profile"]["sections"]) == 11
    assert public["catalog_grants_execution"] is False
    assert public["rf_execution_source"] == "approved_profile"
    assert len(public["verified_hil"]["sections"]) == 11
    assert public["verified_hil"]["bandwidths_hz"] == [
        20_000_000,
        40_000_000,
        80_000_000,
        160_000_000,
        320_000_000,
    ]


def test_unapproved_profile_cannot_be_loaded_for_execution():
    payload = load_capability_profile(
        Path("configs/instrument_capabilities.example.yaml")
    ).model_dump()
    payload["approved_profile"]["lifecycle"] = "draft"
    with pytest.raises(ValidationError, match="lifecycle: approved"):
        InstrumentCapabilityProfile.model_validate(payload)
