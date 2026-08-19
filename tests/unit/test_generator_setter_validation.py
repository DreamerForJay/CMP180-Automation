from pathlib import Path

import pytest

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.generator_setter_validation import validate_same_value_setters

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = load_scpi_command_map(REPO_ROOT / "configs" / "scpi_command_map.yaml")


class FakeIo:
    def __init__(self, state: str = "OFF", error: str = '0,"No error"'):
        self.state = state
        self.error = error
        self.frequency = 6_105_000_000.0
        self.power = -40.0
        self.writes: list[str] = []

    def query_str(self, command: str) -> str:
        if command == REGISTRY.require("generator_query.state"):
            return self.state
        if command == REGISTRY.require("generator_query.frequency"):
            return str(self.frequency)
        if command == REGISTRY.require("generator_query.level"):
            return str(self.power)
        if command == REGISTRY.require("common.system_error"):
            return self.error
        if command == REGISTRY.require("common.operation_complete"):
            return "1"
        raise AssertionError(f"Unexpected query: {command}")

    def write_str(self, command: str) -> None:
        self.writes.append(command)


def test_writes_only_current_values_and_keeps_rf_off():
    io = FakeIo()
    result = validate_same_value_setters(io, REGISTRY)
    assert result.initial_rf_state == result.final_rf_state == "OFF"
    assert len(result.checks) == 2
    assert io.writes == [
        REGISTRY.render("generator.set_frequency", frequency_hz=io.frequency),
        REGISTRY.render("generator.set_power", power_dbm=io.power),
    ]


def test_refuses_any_non_off_rf_state_without_writing():
    io = FakeIo(state="ON")
    with pytest.raises(RuntimeError, match="RF is ON"):
        validate_same_value_setters(io, REGISTRY)
    assert io.writes == []


def test_stops_after_error_queue_failure():
    io = FakeIo(error='-100,"Command error"')
    with pytest.raises(RuntimeError, match="Before setter validation"):
        validate_same_value_setters(io, REGISTRY)
    assert io.writes == []
