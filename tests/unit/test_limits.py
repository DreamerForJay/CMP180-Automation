import math
from pathlib import Path

import pytest

from cmp180_evm.limits import LimitProfile, evaluate_limits, load_limit_profile


def profile(lifecycle: str = "draft") -> LimitProfile:
    return LimitProfile(
        profile_id="example",
        revision="0.1",
        lifecycle=lifecycle,
        description="test",
        maximum_evm_db=-32.0,
        maximum_absolute_frequency_error_hz=1000.0,
        maximum_absolute_power_error_db=3.0,
    )


def test_draft_profile_never_returns_unqualified_compliance_pass():
    result = evaluate_limits(
        profile(),
        evm_db=-36.0,
        frequency_error_hz=10.0,
        measured_power_dbm=-40.5,
        expected_power_dbm=-40.0,
    )
    assert result.overall_status == "DRAFT_PASS"
    assert result.evm_margin_db == 4.0


def test_any_failed_metric_fails_the_draft_profile():
    result = evaluate_limits(
        profile(),
        evm_db=-30.0,
        frequency_error_hz=10.0,
        measured_power_dbm=-40.0,
        expected_power_dbm=-40.0,
    )
    assert result.overall_status == "DRAFT_FAIL"
    assert result.evm_status == "FAIL"


def test_non_finite_metric_is_invalid_not_pass():
    result = evaluate_limits(
        profile(),
        evm_db=math.nan,
        frequency_error_hz=0.0,
        measured_power_dbm=-40.0,
        expected_power_dbm=-40.0,
    )
    assert result.overall_status == "INVALID"
    assert result.evm_margin_db is None


def test_profile_rejects_unrecognized_lifecycle():
    with pytest.raises(ValueError, match="lifecycle"):
        profile("production")


def test_example_profile_is_explicitly_draft():
    loaded = load_limit_profile(Path("configs/limits.example.yaml"))
    assert loaded.lifecycle == "draft"
    assert "draft" in loaded.profile_id
