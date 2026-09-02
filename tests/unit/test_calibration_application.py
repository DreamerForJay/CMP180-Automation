from dataclasses import replace
from datetime import date

import pytest

from cmp180_evm.calibration import CalibrationPoint, CalibrationProfile
from cmp180_evm.workflow.calibration_application import (
    resolve_calibration,
    uncalibrated_metadata,
)

TODAY = date(2026, 9, 1)


def profile(**overrides) -> CalibrationProfile:
    values = {
        "profile_id": "rf1.1-rf1.5-6ghz",
        "revision": "1.0",
        "lifecycle": "approved",
        "route": "RF1.1-RF1.5",
        "calibrated_at": date(2026, 8, 1),
        "expires_at": date(2027, 8, 1),
        "equipment_reference": "cable:C01; power-meter:P01",
        "source_evidence": "calibration-certificate:CERT-001",
        "approved_by": "RF Owner",
        "approved_at": date(2026, 8, 2),
        "points": (
            CalibrationPoint(5_925_000_000, 2.0),
            CalibrationPoint(7_125_000_000, 4.0),
        ),
    }
    values.update(overrides)
    return CalibrationProfile(**values)


def resolve(profile_value, **overrides):
    kwargs = {
        "route": "RF1.1-RF1.5",
        "frequencies_hz": (6_105_000_000.0,),
        "on_date": TODAY,
    }
    kwargs.update(overrides)
    return resolve_calibration(profile_value, **kwargs)


def test_no_profile_means_no_correction_and_unchanged_behaviour():
    assert resolve(None) is None
    metadata = uncalibrated_metadata("no profile supplied")
    assert metadata["calibration_applied"] is False
    assert metadata["calibration_reason"] == "no profile supplied"


def test_approved_profile_interpolates_loss_at_the_measured_frequency():
    application = resolve(profile())
    assert application is not None
    # 5925 MHz→2 dB、7125 MHz→4 dB，6525 MHz 恰為中點。
    assert application.loss_for(6_525_000_000) == pytest.approx(3.0)
    assert application.loss_for(5_925_000_000) == pytest.approx(2.0)


def test_draft_profile_cannot_correct_a_measurement():
    with pytest.raises(ValueError, match="not approved"):
        resolve(profile(lifecycle="draft"))


def test_expired_profile_cannot_correct_a_measurement():
    with pytest.raises(ValueError, match="expired"):
        resolve(profile(expires_at=date(2026, 8, 15)))


def test_profile_for_a_different_route_is_refused():
    with pytest.raises(ValueError, match="covers route"):
        resolve(profile(route="RF1.2-RF2.1"))


def test_frequency_outside_the_calibrated_range_blocks_extrapolation():
    with pytest.raises(ValueError, match="extrapolation is blocked"):
        resolve(profile(), frequencies_hz=(5_500_000_000.0,))


def test_every_sweep_frequency_must_be_covered_not_just_the_first():
    with pytest.raises(ValueError, match="extrapolation is blocked"):
        resolve(profile(), frequencies_hz=(6_105_000_000.0, 7_500_000_000.0))


def test_applied_metadata_records_provenance_for_audit():
    metadata = resolve(profile()).metadata()
    assert metadata["calibration_applied"] is True
    assert metadata["calibration_profile_id"] == "rf1.1-rf1.5-6ghz"
    assert metadata["calibration_revision"] == "1.0"
    assert metadata["calibration_equipment_reference"] == "cable:C01; power-meter:P01"
    # 修正必須套用在 external attenuation，不可改動已驗證的 ranging 值。
    assert metadata["calibration_correction_target"] == "analyzer_external_attenuation_db"


def test_route_text_variants_still_match_the_profile():
    assert resolve(profile(), route="rf1.1 → rf1.5") is not None


def test_loss_is_applied_per_frequency_across_a_sweep():
    """掃描每點的 path loss 不同，必須逐點取值而非整批套同一個數字。"""
    application = resolve(
        profile(), frequencies_hz=(5_925_000_000.0, 6_525_000_000.0, 7_125_000_000.0)
    )
    losses = [
        application.loss_for(value)
        for value in (5_925_000_000, 6_525_000_000, 7_125_000_000)
    ]
    assert losses == pytest.approx([2.0, 3.0, 4.0])


def test_profile_rejects_loss_outside_the_safety_envelope():
    # calibration.py 的 0..30 dB 包絡仍然有效，避免明顯錯誤的校正值被套用。
    with pytest.raises(ValueError, match="0..30 dB safety envelope"):
        profile(points=(CalibrationPoint(5_925_000_000, 2.0), CalibrationPoint(7_125_000_000, 45.0)))


def test_replace_keeps_frozen_profile_immutable():
    original = profile()
    modified = replace(original, revision="1.1")
    assert original.revision == "1.0" and modified.revision == "1.1"


def test_config_path_resolution_blocks_traversal(tmp_path, monkeypatch):
    """校正檔路徑來自請求，必須擋下 ../ 穿越，只允許 configs/ 內的檔案。"""
    from cmp180_evm.web import server as web_server

    monkeypatch.setattr(web_server, "PROJECT_ROOT", tmp_path)
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "cal.yaml").write_text("points: []", encoding="utf-8")
    (tmp_path / "secret.yaml").write_text("nope", encoding="utf-8")

    resolver = web_server.Cmp180WebHandler._resolve_config_path

    assert resolver(None, "cal.yaml").name == "cal.yaml"
    for attempt in ("../secret.yaml", "../../etc/passwd"):
        with pytest.raises(ValueError):
            resolver(None, attempt)
