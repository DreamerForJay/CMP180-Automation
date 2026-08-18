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


def test_unconfigured_wlan_command_raises():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    with pytest.raises(ScpiCommandNotConfiguredError, match="generator.set_power"):
        registry.require("generator.set_power")


def test_is_configured_false_for_unset_command():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    assert registry.is_configured("wlan_tx.initiate") is False
    assert registry.is_configured("common.identify") is True


def test_verified_wlan_queries_are_configured():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    assert registry.require("wlan_tx_query.standard") == "CONF:WLAN:MEAS:ISIG:STAN?"
    assert registry.require("wlan_tx_query.center_frequency").endswith("FREQ?")
    assert registry.require("wlan_tx_query.measurement_states").endswith("STAT:ALL?")


def test_verified_queries_do_not_enable_unverified_writes_or_results():
    registry = load_scpi_command_map(SCPI_MAP_PATH)
    assert registry.is_configured("wlan_tx.set_frequency") is False
    assert registry.is_configured("wlan_tx.initiate") is False
    assert registry.is_configured("results.evm_all_average") is False
