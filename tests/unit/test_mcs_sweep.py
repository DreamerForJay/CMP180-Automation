from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from cmp180_evm.mcs_sweep import (
    EHT_MCS_DEFINITIONS,
    CMP180MCSSweepSource,
    MockMCSSweepConfig,
    generate_mock_mcs_sweep,
    parse_mcs_list,
    save_mcs_sweep_artifacts,
    validate_mcs_list,
)


def test_eht_baseline_defines_mcs_zero_through_thirteen() -> None:
    assert set(EHT_MCS_DEFINITIONS) == set(range(14))
    assert EHT_MCS_DEFINITIONS[11].modulation == "1024-QAM"
    assert EHT_MCS_DEFINITIONS[13].modulation == "4096-QAM"


def test_selected_mcs_list_preserves_non_contiguous_order() -> None:
    assert parse_mcs_list("0, 3, 5, 7, 9, 11") == (0, 3, 5, 7, 9, 11)


@pytest.mark.parametrize("value", ["", "0,x,3", "0,0,1", "14"])
def test_invalid_mcs_list_is_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        parse_mcs_list(value)


def test_validate_mcs_list_rejects_empty_sequence() -> None:
    with pytest.raises(ValueError):
        validate_mcs_list([])


def test_mock_sweep_is_deterministic_and_explicitly_simulated() -> None:
    config = MockMCSSweepConfig(selected_mcs=(0, 3, 7, 11, 13), seed=91)
    first = generate_mock_mcs_sweep(config)
    second = generate_mock_mcs_sweep(config)

    assert first == second
    assert first.metadata.source.value == "mock"
    assert first.metadata.simulated is True
    assert first.metadata.hil_status.value == "HIL_PENDING"
    assert first.metadata.compliance_limits == "NOT_DEFINED"
    assert all(point.provenance == ("SIMULATED", "DERIVED") for point in first.points)


def test_mock_evm_trend_is_more_sensitive_at_high_mcs() -> None:
    dataset = generate_mock_mcs_sweep(
        MockMCSSweepConfig(selected_mcs=(0, 3, 7, 11, 13), evm_jitter_db=0, seed=1)
    )
    evm_values = [point.evm_db for point in dataset.points]

    assert all(value is not None for value in evm_values)
    assert evm_values == sorted(evm_values)


def test_invalid_mock_point_keeps_measurements_null() -> None:
    dataset = generate_mock_mcs_sweep(
        MockMCSSweepConfig(selected_mcs=(0, 1, 2), invalid_rate=0.999, seed=4)
    )

    assert dataset.metadata.valid_count == 0
    assert all(not point.valid for point in dataset.points)
    assert all(point.evm_db is None and point.power_dbm is None for point in dataset.points)


def test_mock_config_rejects_invalid_units_or_rates() -> None:
    with pytest.raises(ValueError):
        MockMCSSweepConfig(frequency_hz=0)
    with pytest.raises(ValueError):
        MockMCSSweepConfig(invalid_rate=1)
    with pytest.raises(ValueError):
        MockMCSSweepConfig(evm_jitter_db=-1)


def test_public_payload_has_required_fields() -> None:
    payload = generate_mock_mcs_sweep(
        MockMCSSweepConfig(selected_mcs=(0, 11), seed=5)
    ).public()
    point = payload["points"][0]

    assert payload["metadata"]["hardware_support"] == "HIL_PENDING"
    assert {
        "mcs_index",
        "modulation",
        "coding_rate",
        "bandwidth_mhz",
        "frequency_hz",
        "evm_db",
        "power_dbm",
        "frequency_error_hz",
        "reliability",
        "valid",
    } <= set(point)


def test_mcs_artifacts_are_complete_and_do_not_claim_compliance(tmp_path: Path) -> None:
    dataset = generate_mock_mcs_sweep(
        MockMCSSweepConfig(selected_mcs=(0, 3, 5, 7, 9, 11), seed=6)
    )
    artifacts = save_mcs_sweep_artifacts(dataset, tmp_path)

    assert {"csv", "json", "svg", "png", "metadata"} <= artifacts.keys()
    assert Path(artifacts["png"]).read_bytes().startswith(b"\x89PNG")
    assert "<svg" in Path(artifacts["svg"]).read_text(encoding="utf-8")
    rows = list(csv.DictReader(Path(artifacts["csv"]).open(encoding="utf-8-sig")))
    assert [int(row["mcs_index"]) for row in rows] == [0, 3, 5, 7, 9, 11]
    metadata = json.loads(Path(artifacts["metadata"]).read_text(encoding="utf-8"))
    assert metadata["source"] == "mock"
    assert metadata["hil_status"] == "HIL_PENDING"
    assert metadata["compliance_claim"] is False


def test_cmp180_mcs_source_is_explicitly_hil_pending() -> None:
    source = CMP180MCSSweepSource()

    assert source.hardware_support == "HIL_PENDING"
    with pytest.raises(NotImplementedError, match="no verified waveform/SCPI mapping"):
        source.acquire()
