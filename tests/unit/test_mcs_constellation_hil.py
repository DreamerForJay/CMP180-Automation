"""實機入口的離線安全與格式測試，不連線 CMP180。"""

import pytest

from scripts.cmp180_mcs_constellation_validate import enabled_flags, final_cleanup, parse_trace


def test_separate_arrays_do_not_pair_reliability_as_iq():
    result = parse_trace("0,1,-1", "0,0.5,-0.5")
    assert result["valid"]
    assert result["points"][0] == {"index": 0, "i": 1, "q": 0.5, "valid": True}


@pytest.mark.parametrize("raw_i,raw_q", [("0,1,2", "0,1"), ("0", "0")])
def test_malformed_trace_is_rejected(raw_i, raw_q):
    with pytest.raises(ValueError):
        parse_trace(raw_i, raw_q)


@pytest.mark.parametrize("token", ["INV", "NaN", "inf", "9.91E37"])
def test_invalid_values_are_never_zero(token):
    result = parse_trace(f"0,{token}", "0,1")
    assert not result["valid"]
    assert result["points"][0]["i"] is None


def test_nonzero_reliability_invalidates_numeric_points():
    assert not parse_trace("1,0.5", "0,0.5")["valid"]


def test_enable_preserves_other_results():
    assert enabled_flags("ON,OFF,ON,OFF,ON,OFF,OFF,ON,OFF") == "ON,OFF,ON,OFF,ON,ON,OFF,ON,OFF"
    with pytest.raises(ValueError):
        enabled_flags("ON,OFF")


def test_stop_and_abort_failure_still_attempt_rf_off():
    class BrokenStop:
        rf_off_called = False

        def stop_measurement(self):
            raise RuntimeError("stop failed")

        def _write_checked(self, command):
            raise RuntimeError("abort failed")

        def rf_off(self):
            self.rf_off_called = True

        def _query(self, command):
            return "OFF"

        def drain_error_queue(self):
            return []

    backend = BrokenStop()
    result = final_cleanup(backend)
    assert backend.rf_off_called
    assert len(result["cleanup_errors"]) == 2
