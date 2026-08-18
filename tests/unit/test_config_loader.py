from pathlib import Path

import pytest

from cmp180_evm.config.loader import (
    detect_config_kind,
    load_instrument_config,
    load_wlan_baseline_config,
)
from cmp180_evm.config.validators import validate_band_frequency
from cmp180_evm.utils.exceptions import ConfigValidationError

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = REPO_ROOT / "configs"


def test_detect_config_kind_instrument():
    assert detect_config_kind(CONFIGS_DIR / "instrument.example.yaml") == "instrument"


def test_detect_config_kind_wlan_baseline():
    assert detect_config_kind(CONFIGS_DIR / "wlan_baseline.example.yaml") == "wlan_baseline"


def test_load_instrument_config():
    config = load_instrument_config(CONFIGS_DIR / "instrument.example.yaml")
    assert config.instrument.resource.address == "TCPIP::192.168.200.50::5025::SOCKET"
    assert config.instrument.resource.options == "SelectVisa='socketio'"
    assert config.routing.generator_port == "RF1.1"
    assert config.routing.generator_port_confirmed is True
    assert config.routing.analyzer_port_confirmed is True
    assert config.instrument.session.reset_on_connect is False


def test_load_wlan_baseline_config():
    config = load_wlan_baseline_config(CONFIGS_DIR / "wlan_baseline.example.yaml")
    assert config.signal.band == "6_GHZ"
    assert config.signal.center_frequency_hz == 6105000000
    assert config.signal.bandwidth_hz == 320000000
    assert config.signal.coding == "LDPC"
    assert config.generator.arb_waveform_file is not None
    assert config.analyzer.trigger.source == "IF Power"
    assert config.measurement.burst_count == 10


def test_validate_band_frequency_ok():
    validate_band_frequency("6_GHZ", 6_105_000_000)


def test_validate_band_frequency_mismatch_raises():
    with pytest.raises(ConfigValidationError, match="does not match selected band"):
        validate_band_frequency("5_GHZ", 6_105_000_000)
