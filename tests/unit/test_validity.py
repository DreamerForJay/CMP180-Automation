import pytest

from cmp180_evm.results.validity import (
    INSUFFICIENT_PPDUS,
    INSUFFICIENT_SYMBOLS,
    INVALID_EVM,
    INVALID_FREQ_ERROR,
    INVALID_POWER,
    INVALID_RELIABILITY,
    MINIMUM_DATA_SYMBOLS_FOR_IQ_ESTIMATE,
    evaluate_estimator_confidence,
    evaluate_point_validity,
    invalid_critical_fields,
)


def good_values(**overrides):
    values = {
        "reliability": "0",
        "evm_all_carriers_db": "-36.59215",
        "burst_power_dbm": "-40.04724",
        "frequency_error_hz": "-18.83229",
        "measured_symbols": str(MINIMUM_DATA_SYMBOLS_FOR_IQ_ESTIMATE),
    }
    values.update(overrides)
    return values


def test_valid_point_reports_no_reasons():
    validity = evaluate_point_validity(good_values())
    assert validity.valid is True
    assert validity.reasons == ()
    assert validity.public() == {"valid": True, "invalid_reasons": []}


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"reliability": "6"}, INVALID_RELIABILITY),
        ({"evm_all_carriers_db": "INV"}, INVALID_EVM),
        ({"burst_power_dbm": "NCAP"}, INVALID_POWER),
        ({"frequency_error_hz": "NAV"}, INVALID_FREQ_ERROR),
    ],
)
def test_each_failure_mode_is_reported_by_name(overrides, reason):
    validity = evaluate_point_validity(good_values(**overrides))
    assert validity.valid is False
    assert reason in validity.reasons


def test_multiple_failures_are_all_preserved_not_collapsed_to_boolean():
    validity = evaluate_point_validity(
        good_values(reliability="4", evm_all_carriers_db="INV", burst_power_dbm="INV")
    )
    assert set(validity.reasons) == {INVALID_RELIABILITY, INVALID_EVM, INVALID_POWER}


def test_reliability_alone_invalidates_a_point_with_numeric_fields():
    # 舊行為只看三個欄位是否有限值，reliability 非 0 仍被視為有效。
    values = good_values(reliability="6")
    assert invalid_critical_fields(values) == ("reliability",)
    assert evaluate_point_validity(values).valid is False


def test_estimator_is_untrusted_below_the_documented_symbol_minimum():
    confidence = evaluate_estimator_confidence(good_values(measured_symbols="2"))
    assert confidence.estimate_valid is False
    assert confidence.reason == INSUFFICIENT_SYMBOLS
    assert confidence.measured_symbols == 2
    assert confidence.public()["affected_fields"] == [
        "gain_imbalance_db",
        "quadrature_error_deg",
    ]


def test_estimator_is_trusted_only_with_enough_symbols_and_ppdus():
    assert evaluate_estimator_confidence(good_values()).estimate_valid is True
    low_ppdu = evaluate_estimator_confidence(good_values(), statistic_count=10)
    assert low_ppdu.estimate_valid is False
    assert low_ppdu.reason == INSUFFICIENT_PPDUS
    assert evaluate_estimator_confidence(good_values(), statistic_count=20).estimate_valid is True
