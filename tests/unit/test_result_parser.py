import pytest

from cmp180_evm.results.ofdm_siso import RESULT_FIELDS, parse_result


def test_parse_result_maps_all_28_fields():
    response = ",".join(str(index) for index in range(1, 29))
    result = parse_result(response)
    assert tuple(result) == RESULT_FIELDS
    assert result["burst_power_dbm"] == "13"
    assert result["evm_all_carriers_db"] == "16"
    assert result["common_phase_error_deg"] == "28"


def test_parse_result_rejects_wrong_field_count():
    with pytest.raises(ValueError, match="Expected 28 fields"):
        parse_result("1,2,3")
