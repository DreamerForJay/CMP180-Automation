from cmp180_evm.loopback import (
    APPROVED_LOOPBACK_PROFILE,
    LOOPBACK_BATCH_CASES,
    LoopbackProfile,
    analyze_loopback,
    loopback_batch_requests,
    run_loopback_repeats,
    select_loopback_profile,
)
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan


class RepeatBackend:
    def __init__(self, evm_values):
        self.evm_values = iter(evm_values)
        self.initiates = 0
        self.rf_offs = 0

    def configure(self, plan): pass
    def rf_on(self): pass
    def initiate_single(self): self.initiates += 1
    def wait_ready(self): pass
    def fetch_result(self):
        return {
            "reliability": "0",
            "evm_all_carriers_db": str(next(self.evm_values)),
            "burst_power_dbm": "-39.8",
            "frequency_error_hz": "-17.0",
            "raw": "raw-response",
        }
    def stop_measurement(self): pass
    def rf_off(self): self.rf_offs += 1
    def drain_error_queue(self): return []


def plan():
    return SingleMeasurementPlan(
        "RF1.1", "RF1.5", 6_105_000_000, 320_000_000, -40, -20, 0, True
    )


def test_repeat_workflow_executes_real_independent_cycles():
    backend = RepeatBackend([-36.9] * 5)
    result = run_loopback_repeats(backend, plan(), 5)
    assert backend.initiates == 5
    assert backend.rf_offs == 5
    assert [row["repeat_index"] for row in result["measurements"]] == [1, 2, 3, 4, 5]
    assert len({row["timestamp"] for row in result["measurements"]}) >= 1


def test_statistics_use_sample_standard_deviation_and_identify_outlier():
    rows = [
        {
            "repeat_index": index + 1,
            "valid": True,
            "evm_all_carriers_db": value,
            "burst_power_dbm": -39.8,
            "frequency_error_hz": -17.0,
        }
        for index, value in enumerate([-36.9, -37.0, -36.8, -36.9, -27.1, -36.9])
    ]
    result = analyze_loopback(rows, LoopbackProfile())
    assert result["statistics"]["evm_all_carriers_db"]["count"] == 6
    assert result["statistics_convention"] == "sample_std_dev_ddof_1"
    assert any(item["repeat_index"] == 5 for item in result["outliers"])


def test_stable_but_wrong_power_is_not_ready():
    rows = [
        {
            "repeat_index": index + 1,
            "valid": True,
            "evm_all_carriers_db": -36.9,
            "burst_power_dbm": -60.0,
            "frequency_error_hz": -17.0,
        }
        for index in range(5)
    ]
    profile = LoopbackProfile(
        max_evm_std_db=0.2,
        max_power_std_db=0.2,
        max_freq_error_std_hz=20,
        max_invalid_ratio=0,
        expected_power_dbm=-40,
        allowed_power_error_db=1,
    )
    result = analyze_loopback(rows, profile)
    assert result["stability_status"] == "PASS"
    assert result["reasonableness_status"] == "DRAFT_FAIL"
    assert result["overall_status"] == "LOOPBACK_UNVERIFIED"


def test_approved_profile_can_produce_ready():
    rows = [
        {
            "repeat_index": index + 1,
            "valid": True,
            "evm_all_carriers_db": -36.9,
            "burst_power_dbm": -39.8,
            "frequency_error_hz": -17.0,
        }
        for index in range(5)
    ]
    profile = LoopbackProfile(
        lifecycle="approved",
        max_evm_std_db=0.2,
        max_power_std_db=0.2,
        max_freq_error_std_hz=20,
        max_invalid_ratio=0,
        expected_power_dbm=-40,
        allowed_power_error_db=1,
        source_reference="internal baseline",
        approved_by="RF owner",
        approved_at="2026-09-03",
    )
    assert analyze_loopback(rows, profile)["overall_status"] == "LOOPBACK_READY"


def test_invalid_measurements_outrank_unverified_under_a_draft_profile():
    rows = [
        {
            "repeat_index": index + 1,
            "valid": False,
            "invalid_reasons": ["reliability != 0"],
            "evm_all_carriers_db": None,
            "burst_power_dbm": None,
            "frequency_error_hz": None,
        }
        for index in range(5)
    ]
    result = analyze_loopback(rows, LoopbackProfile())
    assert result["validity_status"] == "FAIL"
    assert result["overall_status"] == "LOOPBACK_INVALID"


def test_unstable_outranks_unverified_when_no_rf_baseline_exists():
    rows = [
        {
            "repeat_index": index + 1,
            "valid": True,
            "evm_all_carriers_db": value,
            "burst_power_dbm": -39.8,
            "frequency_error_hz": -17.0,
        }
        for index, value in enumerate([-36.9, -30.1, -41.2, -33.0, -38.7])
    ]
    profile = LoopbackProfile(
        max_evm_std_db=0.2,
        max_power_std_db=0.2,
        max_freq_error_std_hz=20,
        max_invalid_ratio=0,
    )
    result = analyze_loopback(rows, profile)
    assert result["stability_status"] == "FAIL"
    assert result["reasonableness_status"] == "NOT_EVALUATED"
    assert result["overall_status"] == "LOOPBACK_UNSTABLE"


def test_insufficient_repeats_stay_unverified_not_invalid():
    rows = [
        {
            "repeat_index": index + 1,
            "valid": True,
            "evm_all_carriers_db": -36.9,
            "burst_power_dbm": -39.8,
            "frequency_error_hz": -17.0,
        }
        for index in range(3)
    ]
    result = analyze_loopback(rows, LoopbackProfile(minimum_repeats=5))
    assert result["overall_status"] == "LOOPBACK_UNVERIFIED"


def test_repeat_10_hil_point_selects_traceable_approved_profile():
    request = {
        "center_frequency_hz": 6_105_000_000,
        "bandwidth_hz": 320_000_000,
        "generator_power_dbm": -40,
        "repeat_count": 10,
        "max_evm_std_db": 0.2,
        "max_power_std_db": 0.1,
        "max_freq_error_std_hz": 20,
        "max_invalid_ratio": 0,
        "expected_power_dbm": -40,
        "allowed_power_error_db": 1,
        "cable_confirmation": "RF1.1-RF1.5",
    }
    assert select_loopback_profile(request) == APPROVED_LOOPBACK_PROFILE


def test_changed_loopback_condition_falls_back_to_draft():
    request = {
        "center_frequency_hz": 6_105_000_000,
        "bandwidth_hz": 320_000_000,
        "generator_power_dbm": -40,
        "repeat_count": 10,
        "max_evm_std_db": 0.2,
        "max_power_std_db": 0.1,
        "max_freq_error_std_hz": 21,
        "max_invalid_ratio": 0,
        "expected_power_dbm": -40,
        "allowed_power_error_db": 1,
        "cable_confirmation": "RF1.1-RF1.5",
    }
    assert select_loopback_profile(request).lifecycle == "draft"


def test_batch_builds_all_wlan_sections_as_isolated_repeat_10_requests():
    requests = loopback_batch_requests()
    assert len(requests) == len(LOOPBACK_BATCH_CASES) == 11
    assert len({request["profile_id"] for request in requests}) == 11
    assert all(request["repeat_count"] == 10 for request in requests)
    assert all(request["cable_confirmation"] == "RF1.1-RF1.5" for request in requests)
    assert requests[-1]["center_frequency_hz"] == 6_105_000_000
    assert all(select_loopback_profile(request).lifecycle == "approved" for request in requests)
    assert len({select_loopback_profile(request).source_reference for request in requests}) == 11
