from pathlib import Path

import pytest

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.measurement_lifecycle_validation import (
    validate_measurement_lifecycle,
)

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = load_scpi_command_map(ROOT / "configs" / "scpi_command_map.yaml")


class FakeIo:
    def __init__(self, generator_state: str = "OFF", measurement_state: str = "RDY"):
        self.generator_state = generator_state
        self.measurement_state = measurement_state
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
        raise AssertionError(f"Unexpected query: {command}")

    def write_str(self, command: str) -> None:
        self.writes.append(command)
        if command == REGISTRY.require("wlan_tx.initiate"):
            self.measurement_state = "RUN"
        elif command in {
            REGISTRY.require("wlan_tx.stop"),
            REGISTRY.require("wlan_tx.abort"),
        }:
            self.measurement_state = "RDY"


def test_validates_stop_and_abort_cycles_with_generator_off():
    io = FakeIo()
    result = validate_measurement_lifecycle(io, REGISTRY)
    assert [event.action for event in result.events] == [
        "initiate_for_stop",
        "stop",
        "initiate_for_abort",
        "abort",
    ]
    assert result.final_state == "RDY"
    assert result.final_generator_state == "OFF"


@pytest.mark.parametrize(
    ("generator", "measurement", "message"),
    (("ON", "RDY", "Generator RF is ON"), ("OFF", "RUN", "measurement is RUN")),
)
def test_refuses_unsafe_initial_state(generator: str, measurement: str, message: str):
    io = FakeIo(generator, measurement)
    with pytest.raises(RuntimeError, match=message):
        validate_measurement_lifecycle(io, REGISTRY)
    assert io.writes == []
