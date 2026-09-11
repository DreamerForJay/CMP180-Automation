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
    set_arb_file: str | None = None
    rf_on: str | None = None
    rf_off: str | None = None
    arb_rf_on: str | None = None
    arb_rf_off: str | None = None
    arb_set_repetition: str | None = None
    set_baseband_mode: str | None = None


class GeneratorQueryCommands(BaseModel):
    frequency: str
    level: str
    peak_power: str
    state: str
    arb_state: str
    arb_repetition: str
    states: str
    rf_path: str
    arb_file_absolute: str
    baseband_mode: str | None = None


class MassMemoryQueryCommands(BaseModel):
    aliases: str | None = None
    catalog: str | None = None


class WlanTxCommands(BaseModel):
    # 星座圖計算開關會改變結果集合；HIL 工具必須保存並恢復原設定。
    set_results: str | None = None
    set_rf_path: str | None = None
    set_frequency: str | None = None
    set_bandwidth: str | None = None
    set_standard: str | None = None
    set_band: str | None = None
    set_trigger_threshold: str | None = None
    set_trigger_source: str | None = None
    set_repetition: str | None = None
    set_modulation_statistic_count: str | None = None
    set_expected_power: str | None = None
    set_external_attenuation: str | None = None
    adjust_level: str | None = None
    clear_statistics: str | None = None
    initiate: str | None = None
    stop: str | None = None
    abort: str | None = None


class WlanTxQueryCommands(BaseModel):
    result_configuration: str | None = None
    standard: str
    bandwidth: str
    rf_path_catalog: str
    rf_path: str
    rf_path_count: str
    external_attenuation: str
    expected_nominal_power: str
    band: str
    center_frequency: str
    channels: str
    trigger_source_catalog: str
    trigger_source: str
    trigger_threshold: str
    trigger_offset: str
    trigger_min_gap: str
    trigger_slope: str
    trigger_timeout: str
    repetition: str
    modulation_statistic_count: str
    measurement_state: str
    measurement_states: str


class GprfMeasurementCommands(BaseModel):
    set_frequency: str | None = None
    initiate_power: str | None = None
    stop_power: str | None = None
    set_rf_path: str | None = None
    set_expected_power: str | None = None
    set_external_attenuation: str | None = None


class GprfMeasurementQueryCommands(BaseModel):
    power_current: str | None = None
    frequency: str | None = None
    rf_path: str | None = None
    rf_path_catalog: str | None = None
    expected_power: str | None = None
    external_attenuation: str | None = None


class ResultCommands(BaseModel):
    # CMP180 Help 確認 I/Q 分開回傳，首欄各自為 reliability。
    constellation_i: str | None = None
    constellation_q: str | None = None
    modulation_current: str | None = None
    modulation_average: str | None = None
    modulation_minimum: str | None = None
    modulation_maximum: str | None = None
    modulation_std_dev: str | None = None


class ScpiCommandRegistry(BaseModel):
    common: CommonCommands = CommonCommands()
    generator: GeneratorCommands = GeneratorCommands()
    generator_query: GeneratorQueryCommands
    mass_memory_query: MassMemoryQueryCommands = MassMemoryQueryCommands()
    wlan_tx: WlanTxCommands = WlanTxCommands()
    wlan_tx_query: WlanTxQueryCommands
    gprf_measurement: GprfMeasurementCommands = GprfMeasurementCommands()
    gprf_measurement_query: GprfMeasurementQueryCommands = GprfMeasurementQueryCommands()
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

    def render(self, dotted_name: str, **values: float | int | str) -> str:
        """Render a verified command template with explicit named values."""
        return self.require(dotted_name).format(**values)


def load_scpi_command_map(path: Path) -> ScpiCommandRegistry:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return ScpiCommandRegistry.model_validate(data)
