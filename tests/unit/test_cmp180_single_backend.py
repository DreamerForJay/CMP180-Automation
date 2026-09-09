from pathlib import Path

import pytest

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.cmp180_single_backend import (
    Cmp180SingleMeasurementBackend,
    waveform_for_bandwidth,
)
from cmp180_evm.workflow.single_measurement import (
    SingleMeasurementPlan,
    run_single_measurement,
)

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = load_scpi_command_map(ROOT / "configs" / "scpi_command_map.yaml")


class FakeCmp180:
    def __init__(self, *, malformed_result: bool = False):
        self.rf_state = "OFF"
        self.arb_state = "OFF"
        self.measurement_state = "RDY"
        self.measurement_queries = 0
        self.malformed_result = malformed_result
        self.writes: list[str] = []
        self.arb_file = waveform_for_bandwidth(320_000_000)

    def write_str(self, command: str) -> None:
        self.writes.append(command)
        if command == REGISTRY.require("generator.rf_on"):
            self.rf_state = "ON"
        elif command == REGISTRY.require("generator.arb_rf_on"):
            self.arb_state = "ON"
        elif command == REGISTRY.require("generator.rf_off"):
            self.rf_state = "OFF"
        elif command == REGISTRY.require("generator.arb_rf_off"):
            self.arb_state = "OFF"
        elif command == REGISTRY.require("wlan_tx.initiate"):
            self.measurement_state = "RUN"
            self.measurement_queries = 0
        elif command in {REGISTRY.require("wlan_tx.stop"), REGISTRY.require("wlan_tx.abort")}:
            self.measurement_state = "RDY"
        elif command.startswith('SOURce:GPRF:GEN:ARB:FILE "'):
            # 模擬 ABSPath readback，確認 backend 真的依頻寬切換 waveform。
            self.arb_file = command.split('"', 2)[1]

    def query_str(self, command: str) -> str:
        values = {
            REGISTRY.require("generator_query.state"): self.rf_state,
            REGISTRY.require("generator_query.arb_state"): self.arb_state,
            REGISTRY.require("generator_query.arb_repetition"): "CONT",
            REGISTRY.require("generator_query.frequency"): "6.105E9",
            REGISTRY.require("generator_query.level"): "-40",
            REGISTRY.require("generator_query.arb_file_absolute"): f'"{self.arb_file}"',
            REGISTRY.require("wlan_tx_query.rf_path"): '"RF1.5"',
            REGISTRY.require("wlan_tx_query.standard"): "EHT",
            REGISTRY.require("wlan_tx_query.band"): "B6GH",
            REGISTRY.require("wlan_tx_query.bandwidth"): "BW32",
            REGISTRY.require("wlan_tx_query.center_frequency"): "6.105E9",
            REGISTRY.require("wlan_tx_query.external_attenuation"): "0",
            REGISTRY.require("wlan_tx_query.expected_nominal_power"): "-20",
            REGISTRY.require("wlan_tx_query.trigger_threshold"): "-45",
            REGISTRY.require("wlan_tx_query.trigger_source"): '"IF Power"',
            REGISTRY.require("wlan_tx_query.repetition"): "SING",
            REGISTRY.require("wlan_tx_query.modulation_statistic_count"): "10",
            REGISTRY.require("common.operation_complete"): "1",
            REGISTRY.require("common.system_error"): '0,"No error"',
        }
        if command == REGISTRY.require("wlan_tx_query.measurement_state"):
            if self.measurement_state == "RUN":
                self.measurement_queries += 1
                if self.measurement_queries >= 2:
                    self.measurement_state = "RDY"
            return self.measurement_state
        stat_offsets = {
            REGISTRY.require("results.modulation_average"): 0,
            REGISTRY.require("results.modulation_current"): 100,
            REGISTRY.require("results.modulation_minimum"): 200,
            REGISTRY.require("results.modulation_maximum"): 300,
            REGISTRY.require("results.modulation_std_dev"): 400,
        }
        if command in stat_offsets:
            if self.malformed_result:
                return "1,2"
            offset = stat_offsets[command]
            return ",".join(str(offset + index) for index in range(1, 29))
        if command in values:
            return values[command]
        raise AssertionError(f"Unexpected query: {command}")


def plan() -> SingleMeasurementPlan:
    return SingleMeasurementPlan(
        generator_port="RF1.1",
        analyzer_port="RF1.5",
        center_frequency_hz=6_105_000_000,
        bandwidth_hz=320_000_000,
        generator_power_dbm=-40,
        expected_nominal_power_dbm=-20,
        external_attenuation_db=0,
        operator_confirmed=True,
        maximum_generator_power_dbm=-40,
    )


def test_complete_backend_fetches_new_result_and_cleans_up():
    io = FakeCmp180()
    backend = Cmp180SingleMeasurementBackend(io, REGISTRY, poll_interval_s=0)
    result = run_single_measurement(backend, plan())
    # average 沿用無前綴欄位名稱（向後相容）；其餘 4 組統計各自加前綴保存。
    assert result.values["evm_all_carriers_db"] == "16"
    assert result.values["current_evm_all_carriers_db"] == "116"
    assert result.values["min_evm_all_carriers_db"] == "216"
    assert result.values["max_evm_all_carriers_db"] == "316"
    assert result.values["stddev_evm_all_carriers_db"] == "416"
    assert result.values["raw"].startswith("1,2,")
    assert result.values["raw_current"].startswith("101,102,")
    assert result.values["raw_minimum"].startswith("201,202,")
    assert result.values["raw_maximum"].startswith("301,302,")
    assert result.values["raw_std_dev"].startswith("401,402,")
    assert backend.last_measurement_states[-1] == "RDY"
    assert io.rf_state == "OFF"
    assert REGISTRY.require("generator.rf_on") in io.writes
    assert REGISTRY.render(
        "generator.set_arb_file", arb_file=waveform_for_bandwidth(320_000_000)
    ) in io.writes
    assert REGISTRY.require("wlan_tx.stop") in io.writes
    assert REGISTRY.render("wlan_tx.set_repetition", repetition="SINGleshot") in io.writes
    assert (
        REGISTRY.render("wlan_tx.set_modulation_statistic_count", count=10) in io.writes
    )
    assert io.writes[-1] == REGISTRY.require("generator.rf_off")


def test_catalog_edge_single_uses_verified_b6_measurement_template():
    io = FakeCmp180()
    original_query = io.query_str

    def query_catalog_edge(command: str) -> str:
        if command in {
            REGISTRY.require("generator_query.frequency"),
            REGISTRY.require("wlan_tx_query.center_frequency"),
        }:
            return "4.0E8"
        return original_query(command)

    io.query_str = query_catalog_edge  # type: ignore[method-assign]
    edge_plan = SingleMeasurementPlan(
        generator_port="RF1.1",
        analyzer_port="RF1.5",
        center_frequency_hz=400_000_000,
        bandwidth_hz=320_000_000,
        generator_power_dbm=-40,
        expected_nominal_power_dbm=-20,
        external_attenuation_db=0,
        operator_confirmed=True,
        maximum_generator_power_dbm=-40,
    )
    backend = Cmp180SingleMeasurementBackend(io, REGISTRY, poll_interval_s=0)
    result = run_single_measurement(backend, edge_plan)
    # 非 WLAN section 只借用已驗證的 EHT/B6G 解調 template，RF 頻率仍是 400 MHz。
    assert result.cleanup_errors == ()
    assert backend.selected_wlan_band_readback == "B6GH"
    assert REGISTRY.render("generator.set_frequency", frequency_hz=400_000_000) in io.writes
    assert REGISTRY.render("wlan_tx.set_frequency", frequency_hz=400_000_000) in io.writes


@pytest.mark.parametrize("bandwidth_hz", [20e6, 40e6, 80e6, 160e6, 320e6])
def test_each_approved_bandwidth_has_a_matching_hil_waveform(bandwidth_hz):
    path = waveform_for_bandwidth(bandwidth_hz)
    assert f"BW{int(bandwidth_hz / 1e6)}" in path
    assert path.endswith("_LDPC.wv")


def test_malformed_result_still_stops_and_turns_rf_off():
    io = FakeCmp180(malformed_result=True)
    backend = Cmp180SingleMeasurementBackend(io, REGISTRY, poll_interval_s=0)
    with pytest.raises(ValueError, match="Expected 28 fields"):
        run_single_measurement(backend, plan())
    assert io.rf_state == "OFF"
    assert io.writes[-2:] == [
        REGISTRY.require("wlan_tx.stop"),
        REGISTRY.require("generator.rf_off"),
    ]


def test_unknown_rf_on_state_is_reported_and_rf_is_turned_off():
    io = FakeCmp180()
    original_write = io.write_str

    def write_with_adjusting_state(command: str) -> None:
        original_write(command)
        if command == REGISTRY.require("generator.rf_on"):
            io.rf_state = "ADJ"

    io.write_str = write_with_adjusting_state  # type: ignore[method-assign]
    backend = Cmp180SingleMeasurementBackend(io, REGISTRY, poll_interval_s=0)
    with pytest.raises(RuntimeError, match="'ADJ'"):
        run_single_measurement(backend, plan())
    assert io.rf_state == "OFF"
