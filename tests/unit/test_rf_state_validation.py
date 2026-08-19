from pathlib import Path

import pytest

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.rf_state_validation import validate_low_power_rf_pulse

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = load_scpi_command_map(ROOT / "configs" / "scpi_command_map.yaml")


class FakeIo:
    def __init__(self, power: float = -40.0):
        self.rf_state = "OFF"
        self.measurement_state = "OFF"
        self.power = power
        self.writes: list[str] = []

    def query_str(self, command: str) -> str:
        if command == REGISTRY.require("generator_query.state"):
            return self.rf_state
        if command == REGISTRY.require("wlan_tx_query.measurement_state"):
            return self.measurement_state
        if command == REGISTRY.require("generator_query.frequency"):
            return "6.105E9"
        if command == REGISTRY.require("generator_query.level"):
            return str(self.power)
        if command == REGISTRY.require("common.operation_complete"):
            return "1"
        if command == REGISTRY.require("common.system_error"):
            return '0,"No error"'
        raise AssertionError(command)

    def write_str(self, command: str) -> None:
        self.writes.append(command)
        if command == REGISTRY.require("generator.rf_on"):
            self.rf_state = "ON"
        elif command == REGISTRY.require("generator.rf_off"):
            self.rf_state = "OFF"


def test_low_power_pulse_turns_on_then_always_off():
    io = FakeIo()
    result = validate_low_power_rf_pulse(
        io, REGISTRY, operator_confirmed_direct_cable=True
    )
    assert result.on_state == "ON"
    assert result.final_state == "OFF"
    assert io.writes == [
        REGISTRY.require("generator.rf_on"),
        REGISTRY.require("generator.rf_off"),
    ]


@pytest.mark.parametrize(
    ("confirmed", "power", "message"),
    ((False, -40.0, "confirm"), (True, -39.0, "exceeds")),
)
def test_refuses_missing_confirmation_or_excess_power(
    confirmed: bool, power: float, message: str
):
    io = FakeIo(power)
    with pytest.raises(RuntimeError, match=message):
        validate_low_power_rf_pulse(
            io, REGISTRY, operator_confirmed_direct_cable=confirmed
        )
    assert io.writes == []
