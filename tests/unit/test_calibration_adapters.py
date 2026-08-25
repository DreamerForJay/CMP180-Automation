import pytest

from cmp180_evm.calibration_adapters import (
    MockReferenceAdapter,
    capture_calibration_readings,
    list_calibration_adapters,
)


def test_registry_exposes_mock_and_blocks_unconfigured_real_adapter():
    descriptors = {item.adapter_id: item for item in list_calibration_adapters()}
    assert descriptors["mock-reference"].available is True
    assert descriptors["mock-reference"].simulated is True
    assert descriptors["external-scpi"].available is False


def test_mock_capture_returns_readings_and_finishes_output_off():
    adapter = MockReferenceAdapter()
    result = capture_calibration_readings(
        adapter, (6_085_000_000, 6_105_000_000, 6_125_000_000), -40
    )
    assert result.simulated is True
    assert result.final_output_state == "OFF"
    assert result.readings[0].loss_db == pytest.approx(0.8)
    assert adapter.output_enabled is False
    assert adapter.connected is False


def test_capture_cleanup_runs_when_measurement_fails():
    class FailingAdapter(MockReferenceAdapter):
        def measure(self, frequency_hz, source_power_dbm):
            self.output_enabled = True
            raise RuntimeError("capture failed")

    adapter = FailingAdapter()
    with pytest.raises(RuntimeError, match="capture failed"):
        capture_calibration_readings(adapter, (6_085_000_000, 6_125_000_000), -40)
    assert adapter.output_enabled is False
    assert adapter.connected is False


def test_capture_hard_limits_cannot_be_bypassed():
    adapter = MockReferenceAdapter()
    with pytest.raises(ValueError, match="-80..-40"):
        capture_calibration_readings(adapter, (6_085_000_000, 6_125_000_000), -39)
    with pytest.raises(ValueError, match="6 GHz"):
        capture_calibration_readings(adapter, (5_800_000_000, 6_125_000_000), -40)
