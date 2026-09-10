from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pytest

from cmp180_evm.constellation import (
    CMP180ConstellationSource,
    MockConstellationConfig,
    generate_mock_constellation,
    ideal_constellation,
    parse_interleaved_iq,
    save_constellation_artifacts,
)


@pytest.mark.parametrize(
    ("modulation", "order"),
    [
        ("BPSK", 2),
        ("QPSK", 4),
        ("16-QAM", 16),
        ("64-QAM", 64),
        ("256-QAM", 256),
        ("1024-QAM", 1024),
        ("4096-QAM", 4096),
    ],
)
def test_ideal_constellation_has_expected_order_and_unit_average_power(
    modulation: str, order: int
) -> None:
    points = ideal_constellation(modulation)

    assert len(points) == order
    assert len(set(points)) == order
    assert sum(i * i + q * q for i, q in points) / order == pytest.approx(1.0)


def test_interleaved_parser_preserves_invalid_values_as_none() -> None:
    samples = parse_interleaved_iq([1, -1, float("nan"), 0.5, 0.2, float("inf")])

    assert samples[0].valid is True
    assert samples[1].valid is False
    assert samples[1].i is None
    assert samples[1].q == 0.5
    assert samples[2].valid is False
    assert samples[2].q is None


@pytest.mark.parametrize("values", [[], [1, 2, 3]])
def test_interleaved_parser_rejects_empty_or_odd_length(values: list[object]) -> None:
    with pytest.raises(ValueError):
        parse_interleaved_iq(values)


def test_interleaved_parser_rejects_malformed_numeric_input() -> None:
    with pytest.raises(ValueError, match="Malformed numeric"):
        parse_interleaved_iq(["not-a-number", 1])


def test_noise_injection_increases_rms_evm() -> None:
    clean = generate_mock_constellation(
        MockConstellationConfig(modulation="64-QAM", point_count=2000, noise_db=60, seed=7)
    )
    noisy = generate_mock_constellation(
        MockConstellationConfig(modulation="64-QAM", point_count=2000, noise_db=15, seed=7)
    )

    assert noisy.analysis["rms_evm_percent"]["value"] > clean.analysis["rms_evm_percent"]["value"]


def test_mock_impairments_are_deterministic_and_visible() -> None:
    config = MockConstellationConfig(
        modulation="QPSK",
        point_count=512,
        noise_db=80,
        phase_deg=8,
        quadrature_error_deg=2,
        gain_imbalance_db=1,
        dc_i=0.02,
        dc_q=-0.03,
        frequency_offset_hz=10,
        symbol_rate_hz=1_000_000,
        amplitude_scale=1.05,
        seed=9,
    )
    first = generate_mock_constellation(config)
    second = generate_mock_constellation(config)

    assert first.points == second.points
    assert first.metadata.simulated is True
    assert first.metadata.source.value == "mock"
    assert first.metadata.hil_status.value == "HIL_PENDING"
    # Quadrature error 與累積 frequency offset 也會進入整體 phase estimate。
    assert 8 < first.analysis["estimated_phase_error_deg"]["value"] < 12
    assert abs(first.analysis["iq_gain_imbalance_db"]["value"]) > 0.5


def test_invalid_mock_points_are_filtered_from_analysis_without_becoming_zero() -> None:
    dataset = generate_mock_constellation(
        MockConstellationConfig(point_count=1000, invalid_rate=0.2, seed=180)
    )
    invalid = [point for point in dataset.points if not point.valid]

    assert invalid
    assert all(point.i is None and point.q is None and point.evm is None for point in invalid)
    assert dataset.analysis["valid_count"] == dataset.metadata.valid_count
    assert dataset.analysis["invalid_count"] == len(invalid)


def test_constellation_public_payload_supports_raw_normalized_and_ideal_points() -> None:
    payload = generate_mock_constellation(
        MockConstellationConfig(modulation="16-QAM", point_count=32, seed=2)
    ).public()

    assert payload["metadata"]["simulated"] is True
    assert payload["metadata"]["hil_status"] == "HIL_PENDING"
    assert len(payload["ideal_points"]) == 16
    assert {"symbol_index", "i", "q", "normalized_i", "normalized_q", "ideal_i", "ideal_q", "evm", "valid"} <= set(payload["points"][0])
    assert payload["analysis"]["rms_evm_percent"]["provenance"] == ["SIMULATED", "DERIVED"]


def test_constellation_artifacts_have_exact_formats_and_metadata(tmp_path: Path) -> None:
    dataset = generate_mock_constellation(
        MockConstellationConfig(modulation="256-QAM", point_count=128, invalid_rate=0.05)
    )
    artifacts = save_constellation_artifacts(dataset, tmp_path, "export test")

    expected = {"csv", "json", "svg", "png", "metadata"}
    assert expected <= artifacts.keys()
    for key in expected:
        assert Path(artifacts[key]).is_file()
        assert Path(artifacts[key]).stat().st_size > 0
    assert Path(artifacts["csv"]).name == "constellation.csv"
    assert Path(artifacts["json"]).name == "constellation.json"
    assert Path(artifacts["svg"]).name == "constellation.svg"
    assert Path(artifacts["png"]).name == "constellation.png"
    assert Path(artifacts["metadata"]).name == "constellation_metadata.json"

    rows = list(csv.DictReader(Path(artifacts["csv"]).open(encoding="utf-8-sig")))
    assert len(rows) == 128
    assert {"i", "q", "normalized_i", "normalized_q", "valid"} <= rows[0].keys()
    metadata = json.loads(Path(artifacts["metadata"]).read_text(encoding="utf-8"))
    assert metadata["source"] == "mock"
    assert metadata["simulated"] is True
    assert metadata["hil_status"] == "HIL_PENDING"
    assert metadata["compliance_claim"] is False
    assert Path(artifacts["png"]).read_bytes().startswith(b"\x89PNG")
    assert "<svg" in Path(artifacts["svg"]).read_text(encoding="utf-8")


def test_cmp180_source_is_explicitly_unimplemented() -> None:
    source = CMP180ConstellationSource()

    assert source.hardware_support == "HIL_PENDING"
    with pytest.raises(NotImplementedError, match="no verified SCPI"):
        source.acquire()


def test_frequency_offset_changes_later_symbols() -> None:
    baseline = generate_mock_constellation(
        MockConstellationConfig(modulation="BPSK", point_count=20, noise_db=100, seed=3)
    )
    offset = generate_mock_constellation(
        MockConstellationConfig(
            modulation="BPSK",
            point_count=20,
            noise_db=100,
            frequency_offset_hz=10_000,
            symbol_rate_hz=1_000_000,
            seed=3,
        )
    )

    assert math.isclose(baseline.points[0].i, offset.points[0].i, abs_tol=1e-6)
    assert not math.isclose(baseline.points[-1].q, offset.points[-1].q, abs_tol=1e-3)
