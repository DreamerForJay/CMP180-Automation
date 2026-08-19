from pathlib import Path

import pytest

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.analyzer_setter_validation import (
    validate_analyzer_same_value_setters,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = load_scpi_command_map(REPO_ROOT / "configs" / "scpi_command_map.yaml")


class FakeIo:
    def __init__(self, generator_state: str = "OFF", measurement_state: str = "OFF"):
        self.generator_state = generator_state
        self.measurement_state = measurement_state
        self.values = {
            "wlan_tx_query.rf_path": '"RF1.5"',
            "wlan_tx_query.bandwidth": "BW320",
            "wlan_tx_query.center_frequency": "6.105000E+09",
            "wlan_tx_query.external_attenuation": "0.000000E+00",
            "wlan_tx_query.expected_nominal_power": "-2.000000E+01",
        }
        self.writes: list[str] = []

    def query_str(self, command: str) -> str:
        if command == REGISTRY.require("generator_query.state"):
            return self.generator_state
        if command == REGISTRY.require("wlan_tx_query.measurement_state"):
            return self.measurement_state
        if command == REGISTRY.require("common.system_error"):
            return '0,"No error"'
        if command == REGISTRY.require("common.operation_complete"):
            return "1"
        for name, value in self.values.items():
            if command == REGISTRY.require(name):
                return value
        raise AssertionError(f"Unexpected query: {command}")

    def write_str(self, command: str) -> None:
        self.writes.append(command)


def test_writes_five_current_values_and_keeps_both_states_off():
    io = FakeIo()
    result = validate_analyzer_same_value_setters(io, REGISTRY)
    assert len(result.checks) == 5
    assert result.initial_generator_state == result.final_generator_state == "OFF"
    assert result.initial_measurement_state == result.final_measurement_state == "OFF"
    assert len(io.writes) == 5


def test_accepts_ready_as_idle_measurement_state():
    io = FakeIo(measurement_state="RDY")
    result = validate_analyzer_same_value_setters(io, REGISTRY)
    assert result.initial_measurement_state == result.final_measurement_state == "RDY"
    assert len(io.writes) == 5


@pytest.mark.parametrize(
    ("generator_state", "measurement_state", "message"),
    (("ON", "OFF", "Generator RF is ON"), ("OFF", "RUN", "measurement is RUN")),
)
def test_refuses_non_idle_state_without_writing(
    generator_state: str,
    measurement_state: str,
    message: str,
):
    io = FakeIo(generator_state, measurement_state)
    with pytest.raises(RuntimeError, match=message):
        validate_analyzer_same_value_setters(io, REGISTRY)
    assert io.writes == []
