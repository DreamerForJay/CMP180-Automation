from pathlib import Path

import pytest

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.utils.exceptions import ScpiCommandNotConfiguredError

REPO_ROOT = Path(__file__).resolve().parents[2]
SCPI_MAP_PATH = REPO_ROOT / "configs" / "scpi_command_map.yaml"


def test_common_commands_are_fixed():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    assert registry.common.identify == "*IDN?"
    assert registry.common.system_error == "SYST:ERR?"
    assert registry.require("common.identify") == "*IDN?"


def test_unconfigured_result_command_raises():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    with pytest.raises(ScpiCommandNotConfiguredError, match="results.evm_all_average"):
        registry.require("results.evm_all_average")


def test_is_configured_false_for_unset_command():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    assert registry.is_configured("wlan_tx.adjust_level") is False
    assert registry.is_configured("common.identify") is True


def test_verified_wlan_queries_are_configured():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    assert registry.require("wlan_tx_query.standard") == "CONF:WLAN:MEAS:ISIG:STAN?"
    assert registry.require("wlan_tx_query.center_frequency").endswith("FREQ?")
    assert registry.require("wlan_tx_query.measurement_states").endswith("STAT:ALL?")


def test_help_confirmed_generator_queries_are_configured():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    assert registry.require("generator_query.frequency").endswith("FREQuency?")
    assert registry.require("generator_query.level").endswith("LEVel?")
    assert registry.require("generator_query.state").endswith("STATe?")
    assert registry.require("generator_query.rf_path").endswith("SPATh?")


def test_help_confirmed_generator_setters_render_named_values():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    assert registry.render("generator.set_frequency", frequency_hz=6_105_000_000).endswith(
        "FREQuency 6105000000"
    )
    assert registry.render("generator.set_power", power_dbm=-40).endswith("LEVel -40")
    assert registry.require("generator.rf_on").endswith("STATe ON")
    assert registry.require("generator.rf_off").endswith("STATe OFF")


def test_help_confirmed_analyzer_setters_render_named_values():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    assert registry.render("wlan_tx.set_rf_path", rf_path='"RF1.5"').endswith(
        'SPATh "RF1.5"'
    )
    assert registry.render("wlan_tx.set_bandwidth", bandwidth="BW320").endswith(
        "BWIDth BW320"
    )
    assert registry.render("wlan_tx.set_frequency", frequency_hz="6.105E9").endswith(
        "FREQuency 6.105E9"
    )


def test_help_confirmed_measurement_lifecycle_commands_are_configured():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    assert registry.require("wlan_tx.initiate").startswith("INITiate:")
    assert registry.require("wlan_tx.stop").startswith("STOP:")
    assert registry.require("wlan_tx.abort").startswith("ABORt:")


def test_verified_setters_do_not_enable_lifecycle_rf_or_unverified_results():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    assert registry.is_configured("wlan_tx.set_frequency") is True
    assert registry.is_configured("wlan_tx.initiate") is True
    assert registry.is_configured("generator.rf_on") is True
    assert registry.is_configured("results.evm_all_average") is False


def test_modulation_aggregate_result_queries_are_configured():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    assert registry.require("results.modulation_current").endswith("MOD:CURR?")
    assert registry.require("results.modulation_average").endswith("MOD:AVER?")
