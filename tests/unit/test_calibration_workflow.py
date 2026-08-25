from datetime import date

import pytest

from cmp180_evm.calibration_workflow import CalibrationReading, build_draft_profile


def build(readings):
    return build_draft_profile(
        tuple(readings),
        profile_id="route-cal",
        revision="0.1",
        route="RF1.1-RF1.5",
        calibrated_at=date(2026, 8, 25),
        expires_at=date(2026, 11, 25),
        equipment_reference="cable:C01;receiver:P01",
    )


def test_readings_create_draft_positive_loss_profile():
    profile = build(
        [
            CalibrationReading(6_085_000_000, -40, -40.8),
            CalibrationReading(6_125_000_000, -40, -40.9),
        ]
    )
    assert profile.lifecycle == "draft"
    assert profile.points[0].loss_db == pytest.approx(0.8)
    with pytest.raises(ValueError, match="not approved"):
        profile.require_approved_for_use()


def test_negative_or_excessive_calculated_loss_is_blocked():
    with pytest.raises(ValueError, match="outside 0..30"):
        build(
            [
                CalibrationReading(6_085_000_000, -40, -39),
                CalibrationReading(6_125_000_000, -40, -40.9),
            ]
        )
    with pytest.raises(ValueError, match="outside 0..30"):
        build(
            [
                CalibrationReading(6_085_000_000, 0, -31),
                CalibrationReading(6_125_000_000, 0, -1),
            ]
        )
