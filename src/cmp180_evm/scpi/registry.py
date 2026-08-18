"""Central registry of CMP180 SCPI commands.

This is the ONLY place SCPI command strings are allowed to live (SPEC.MD
section 10). Workflow, CLI, and instrument code must look commands up here via
`ScpiCommandRegistry.require(...)` rather than embedding SCPI strings inline.

Every generator/wlan_tx/results command starts out as `None` and stays that
way until it has been captured and verified during SCPI discovery (see
SPEC.MD section 11) and recorded in configs/scpi_command_map.yaml. Calling
`require()` on an unconfigured command raises ScpiCommandNotConfiguredError
instead of silently returning None or guessing a plausible-looking command.
"""

from pathlib import Path

import yaml
from pydantic import BaseModel

from cmp180_evm.scpi import common
from cmp180_evm.utils.exceptions import ScpiCommandNotConfiguredError


class CommonCommands(BaseModel):
    identify: str = common.IDENTIFY
    options: str = common.OPTIONS
    clear_status: str = common.CLEAR_STATUS
    operation_complete: str = common.OPERATION_COMPLETE
    system_error: str = common.SYSTEM_ERROR


class GeneratorCommands(BaseModel):
    set_frequency: str | None = None
    set_power: str | None = None
    rf_on: str | None = None
    rf_off: str | None = None


class WlanTxCommands(BaseModel):
    set_frequency: str | None = None
    set_band: str | None = None
    set_expected_power: str | None = None
    set_external_attenuation: str | None = None
    adjust_level: str | None = None
    clear_statistics: str | None = None
    initiate: str | None = None
    abort: str | None = None


class ResultCommands(BaseModel):
    burst_power_current: str | None = None
    burst_power_average: str | None = None
    evm_all_current: str | None = None
    evm_all_average: str | None = None
    evm_all_max: str | None = None
    evm_all_std_dev: str | None = None
    evm_data_average: str | None = None
    evm_pilot_average: str | None = None
    frequency_error_average: str | None = None
    symbol_clock_error_average: str | None = None


class ScpiCommandRegistry(BaseModel):
    common: CommonCommands = CommonCommands()
    generator: GeneratorCommands = GeneratorCommands()
    wlan_tx: WlanTxCommands = WlanTxCommands()
    results: ResultCommands = ResultCommands()

    def require(self, dotted_name: str) -> str:
        """Look up e.g. "generator.set_power" and raise if it is not configured yet."""
        section_name, _, field_name = dotted_name.partition(".")
        section = getattr(self, section_name, None)
        value = getattr(section, field_name, None) if section is not None else None
        if value is None:
            raise ScpiCommandNotConfiguredError(dotted_name)
        return value

    def is_configured(self, dotted_name: str) -> bool:
        try:
            self.require(dotted_name)
        except ScpiCommandNotConfiguredError:
            return False
        return True


def load_scpi_command_map(path: Path) -> ScpiCommandRegistry:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return ScpiCommandRegistry.model_validate(data)
