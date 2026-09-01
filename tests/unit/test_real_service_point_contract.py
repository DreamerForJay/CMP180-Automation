"""Contract tests for the hardware point payload, using a real 2026-08-28 response."""

from dataclasses import replace

from cmp180_evm.limits import DRAFT_LOOPBACK_LIMIT_PROFILE
from cmp180_evm.results.ofdm_siso import parse_result
from cmp180_evm.web.real_service import _web_point

# 取自 output/20260828T072935Z_real-frequency-sweep_f0e961bf77 的 point_00 average raw response。
REAL_RESPONSE = (
    "0,0.000000E+00,11,1KQ56,2,2,5106,GI32,1,1,NCAP,-1.185631E+01,-4.004724E+01,"
    "-2.904303E+01,1.100419E+01,-3.659215E+01,-3.657895E+01,-3.748849E+01,"
    "-1.883229E+01,-6.377444E-02,-7.253366E+01,-1.125808E+02,6.790724E+00,"
    "2.914752E+00,-4.030440E+01,-3.999815E+01,-4.007365E+01,NAV"
)


def build_point(**kwargs):
    return _web_point(0, 5_925_000_000.0, parse_result(REAL_RESPONSE), "frequency", **kwargs)


def test_hardware_point_exposes_measured_limit_and_margin():
    point = build_point()
    assert point["measured_evm_db"] == -36.59215
    assert point["spec_limit_db"] == DRAFT_LOOPBACK_LIMIT_PROFILE.maximum_evm_db
    # margin = limit - measured；-32.0 - (-36.59215) = +4.59215，正值代表優於限值。
    assert point["margin_db"] == 4.59215
    assert point["limit_status"] == "DRAFT_PASS"


def test_evm_comparison_direction_against_a_stricter_mcs11_limit():
    """EVM dB 越負越好：-36 dB 通過 -35 dB limit，-33.4 dB 不通過。"""
    strict = replace(DRAFT_LOOPBACK_LIMIT_PROFILE, maximum_evm_db=-35.0)

    passing = _web_point(0, 5_925_000_000.0, parse_result(REAL_RESPONSE), "frequency", profile=strict)
    assert passing["measured_evm_db"] == -36.59215
    assert passing["margin_db"] == 1.59215
    assert passing["limit_status"] == "DRAFT_PASS"

    # 修好「沒有套 limit」的缺陷，不代表這批 -33.4 dB 會變成 PASS——它是真正的 FAIL。
    failing_response = REAL_RESPONSE.replace("-3.659215E+01", "-3.340000E+01")
    failing = _web_point(
        0, 5_925_000_000.0, parse_result(failing_response), "frequency", profile=strict
    )
    assert failing["measured_evm_db"] == -33.4
    assert failing["margin_db"] == -1.6
    assert failing["limit_status"] == "DRAFT_FAIL"


def test_reliability_failure_marks_point_invalid_with_reason():
    unreliable = "6," + REAL_RESPONSE.split(",", 1)[1]
    point = _web_point(0, 5_925_000_000.0, parse_result(unreliable), "frequency")
    assert point["valid"] is False
    assert "INVALID_RELIABILITY" in point["invalid_reasons"]
    assert point["limit_status"] == "INVALID"
    assert point["margin_db"] is None


def test_iq_estimates_are_withheld_when_symbol_count_is_insufficient():
    # 這筆實機資料 measured_symbols=2，遠低於文件要求的 16，估計器未收斂。
    point = build_point()
    assert point["gain_imbalance_db"] is None
    assert point["quadrature_error_deg"] is None
    assert point["estimator"]["estimate_valid"] is False
    assert point["estimator"]["reason"] == "insufficient_symbols"
    assert point["estimator"]["measured_symbols"] == 2


def test_iq_estimates_are_returned_once_symbol_count_is_sufficient():
    sufficient = parse_result(REAL_RESPONSE) | {"measured_symbols": "32"}
    point = _web_point(0, 5_925_000_000.0, sufficient, "frequency")
    assert point["gain_imbalance_db"] == 6.790724
    assert point["quadrature_error_deg"] == 2.914752
    assert point["estimator"]["estimate_valid"] is True


def test_instrument_out_of_tolerance_stays_separate_from_app_verdict():
    point = build_point()
    assert point["instrument_out_of_tolerance_percent"] == 0.0
    # 儀器判定與 app spec 判定是兩個獨立欄位，不可互相覆蓋。
    assert point["limit_status"] == "DRAFT_PASS"
