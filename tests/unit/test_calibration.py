from datetime import date
from pathlib import Path

import pytest

from cmp180_evm.calibration import CalibrationPoint, CalibrationProfile, load_calibration_profile


def profile() -> CalibrationProfile:
    return CalibrationProfile(
        profile_id="cal-1",
        revision="1",
        lifecycle="approved",
        route="RF1.1-RF1.5",
        calibrated_at=date(2026, 1, 1),
        expires_at=date(2026, 12, 31),
        equipment_reference="cable-1",
        points=(CalibrationPoint(6e9, 1.0), CalibrationPoint(7e9, 2.0)),
    )


def test_loss_interpolates_and_expected_input_subtracts_positive_loss():
    calibration = profile()
    assert calibration.loss_at(6.5e9) == 1.5
    assert calibration.expected_analyzer_input_dbm(-40, 6.5e9) == -41.5


def test_calibration_blocks_extrapolation():
    with pytest.raises(ValueError, match="extrapolation"):
        profile().loss_at(5.9e9)


def test_expiry_is_explicit_and_snapshot_is_serializable():
    calibration = profile()
    assert calibration.is_expired(date(2027, 1, 1)) is True
    assert calibration.snapshot()["calibrated_at"] == "2026-01-01"


def test_only_approved_current_profile_can_be_used_for_measurement():
    profile().require_approved_for_use(date(2026, 6, 1))
    draft = CalibrationProfile(
        "id", "1", "draft", "route", date(2026, 1, 1), date(2026, 12, 31), "ref",
        (CalibrationPoint(6e9, 1), CalibrationPoint(7e9, 1)),
    )
    with pytest.raises(ValueError, match="not approved"):
        draft.require_approved_for_use(date(2026, 6, 1))
    with pytest.raises(ValueError, match="expired"):
        profile().require_approved_for_use(date(2027, 1, 1))


def test_invalid_point_order_and_loss_are_rejected():
    with pytest.raises(ValueError, match="strictly increasing"):
        CalibrationProfile(
            "id", "1", "draft", "route", date.today(), date.today(), "ref",
            (CalibrationPoint(7e9, 1), CalibrationPoint(6e9, 1)),
        )
    with pytest.raises(ValueError, match="safety envelope"):
        CalibrationProfile(
            "id", "1", "draft", "route", date.today(), date.today(), "ref",
            (CalibrationPoint(6e9, -1), CalibrationPoint(7e9, 1)),
        )


def test_example_calibration_is_draft_and_covers_verified_frequency():
    calibration = load_calibration_profile(Path("configs/calibration.example.yaml"))
    assert calibration.lifecycle == "draft"
    assert calibration.loss_at(6_105_000_000) == 0


def test_loader_accepts_json_compatible_yaml_iso_date_strings(tmp_path):
    path = tmp_path / "draft.yaml"
    path.write_text(
        '{"profile_id":"p","revision":"1","lifecycle":"draft","route":"r",'
        '"calibrated_at":"2026-01-01","expires_at":"2026-12-31",'
        '"equipment_reference":"e","points":['
        '{"frequency_hz":6000000000,"loss_db":1},'
        '{"frequency_hz":6100000000,"loss_db":1.1}]}',
        encoding="utf-8",
    )
    assert load_calibration_profile(path).expires_at == date(2026, 12, 31)
