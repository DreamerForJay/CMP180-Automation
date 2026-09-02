from pathlib import Path

import pytest

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.gprf_measurement_validation import (
    validate_gprf_measurement_setters,
)

RF_PATH_QUERY = "ROUTe:GPRF:MEASurement1:SPATh?"
ENPOWER_QUERY = "CONFigure:GPRF:MEASurement1:RFSettings:ENPower?"
EATTENUATION_QUERY = "CONFigure:GPRF:MEASurement1:RFSettings:EATTenuation?"


class FakeIo:
    """Mock CMP180 that echoes written GPRF routing/level values back on query."""

    def __init__(
        self,
        *,
        rf_state: str = "OFF",
        rf_path: str = '"RF1.6"',
        expected_power: str = "0.000000E+00",
        external_attenuation: str = "0.000000E+00",
        errors: list[str] | None = None,
        readback_override: dict[str, str] | None = None,
    ) -> None:
        self.rf_state = rf_state
        self.values = {
            RF_PATH_QUERY: rf_path,
            ENPOWER_QUERY: expected_power,
            EATTENUATION_QUERY: external_attenuation,
        }
        self.errors = list(errors or [])
        self.readback_override = readback_override or {}
        self.read_counts: dict[str, int] = {}
        self.writes: list[str] = []

    def query_str(self, command: str) -> str:
        if command == "SOURce:GPRF:GEN:STATe?":
            return self.rf_state
        if command == "SYST:ERR?":
            return self.errors.pop(0) if self.errors else '0,"No error"'
        if command == "*OPC?":
            return "1"
        if command in self.values:
            # 第一次讀是原值，之後才套用 override，用來模擬 setter 沒有真正生效。
            self.read_counts[command] = self.read_counts.get(command, 0) + 1
            override = self.readback_override.get(command)
            if override is not None and self.read_counts[command] > 1:
                return override
            return self.values[command]
        raise AssertionError(f"unexpected query {command!r}")

    def write_str(self, command: str) -> None:
        self.writes.append(command)
        for query, prefix in (
            (RF_PATH_QUERY, "ROUTe:GPRF:MEASurement1:SPATh "),
            (ENPOWER_QUERY, "CONFigure:GPRF:MEASurement1:RFSettings:ENPower "),
            (EATTENUATION_QUERY, "CONFigure:GPRF:MEASurement1:RFSettings:EATTenuation "),
        ):
            if command.startswith(prefix):
                self.values[query] = command[len(prefix) :]
                return
        raise AssertionError(f"unexpected write {command!r}")


def _registry():
    return load_scpi_command_map(Path("configs/scpi_command_map.yaml"))


def test_same_value_write_back_passes_and_leaves_rf_off():
    io = FakeIo()

    result = validate_gprf_measurement_setters(io, _registry())

    assert result.initial_rf_state == "OFF"
    assert result.final_rf_state == "OFF"
    assert [check.name for check in result.checks] == [
        "rf_path",
        "expected_power",
        "external_attenuation",
    ]
    # rf_path 必須連引號一起寫回，與 wlan_tx.set_rf_path 慣例相同。
    assert io.writes[0] == 'ROUTe:GPRF:MEASurement1:SPATh "RF1.6"'


def test_validation_refuses_to_write_while_rf_is_on():
    io = FakeIo(rf_state="ON")

    with pytest.raises(RuntimeError, match="Generator RF is ON"):
        validate_gprf_measurement_setters(io, _registry())

    assert io.writes == []


def test_validation_fails_when_error_queue_is_not_empty_after_setter():
    io = FakeIo(errors=['0,"No error"', '-113,"Undefined header"'])

    with pytest.raises(RuntimeError, match="After rf_path setter"):
        validate_gprf_measurement_setters(io, _registry())


def test_validation_fails_when_readback_does_not_match():
    io = FakeIo(readback_override={RF_PATH_QUERY: '"RF1.8"'})

    with pytest.raises(RuntimeError, match="rf_path readback mismatch"):
        validate_gprf_measurement_setters(io, _registry())
