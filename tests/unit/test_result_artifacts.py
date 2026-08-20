import csv
import json
from pathlib import Path

from cmp180_evm.results.artifacts import (
    save_frequency_sweep_result,
    save_power_sweep_result,
    save_single_result,
)


def test_real_single_artifacts_preserve_raw_and_simulation_label(tmp_path: Path):
    artifacts = save_single_result(
        {"raw": "1,2,3", "evm_all_carriers_db": "-36.2"},
        tmp_path,
        test_name="real-test",
        simulated=False,
        metadata={"frequency_hz": 6_105_000_000},
    )
    with open(artifacts["csv"], encoding="utf-8-sig", newline="") as handle:
        row = next(csv.DictReader(handle))
    payload = json.loads(Path(artifacts["json"]).read_text(encoding="utf-8"))
    metadata = json.loads(Path(artifacts["metadata"]).read_text(encoding="utf-8"))
    assert row["simulated"] == "False"
    assert payload["evm_all_carriers_db"] == "-36.2"
    assert metadata["frequency_hz"] == 6_105_000_000
    assert Path(artifacts["raw"]).read_text(encoding="utf-8") == "1,2,3"
    assert "CMP180 SingleShot Report" in Path(artifacts["report"]).read_text(
        encoding="utf-8"
    )


def test_multiple_raw_stats_are_saved_separately_and_excluded_from_row(tmp_path: Path):
    artifacts = save_single_result(
        {
            "raw": "avg-raw",
            "raw_current": "current-raw",
            "raw_minimum": "min-raw",
            "raw_maximum": "max-raw",
            "raw_std_dev": "stddev-raw",
            "evm_all_carriers_db": "-36.2",
            "current_evm_all_carriers_db": "-35.9",
        },
        tmp_path,
        test_name="multi-stat-test",
        simulated=False,
    )
    with open(artifacts["csv"], encoding="utf-8-sig", newline="") as handle:
        row = next(csv.DictReader(handle))
    # raw／raw_* 都不進入主要結果欄位。
    assert "raw" not in row and "raw_current" not in row
    assert row["evm_all_carriers_db"] == "-36.2"
    assert row["current_evm_all_carriers_db"] == "-35.9"
    raw_dir = Path(artifacts["run_dir"]) / "raw"
    assert (raw_dir / "modulation_average.txt").read_text(encoding="utf-8") == "avg-raw"
    assert (raw_dir / "modulation_current.txt").read_text(encoding="utf-8") == "current-raw"
    assert (raw_dir / "modulation_minimum.txt").read_text(encoding="utf-8") == "min-raw"
    assert (raw_dir / "modulation_maximum.txt").read_text(encoding="utf-8") == "max-raw"
    assert (raw_dir / "modulation_std_dev.txt").read_text(encoding="utf-8") == "stddev-raw"
    assert Path(artifacts["raw_current"]).read_text(encoding="utf-8") == "current-raw"


def test_html_report_escapes_instrument_controlled_values(tmp_path: Path):
    artifacts = save_single_result(
        {"evm_all_carriers_db": "<script>alert(1)</script>", "raw": "raw"},
        tmp_path,
        test_name="escape-test",
        simulated=False,
    )
    report = Path(artifacts["report"]).read_text(encoding="utf-8")
    assert "<script>alert(1)</script>" not in report
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in report


def test_frequency_sweep_artifacts_preserve_partial_points_and_raw(tmp_path: Path):
    artifacts = save_frequency_sweep_result(
        [
            {
                "frequency_hz": 6_085_000_000,
                "evm_all_carriers_db": -36.1,
                "raw": "average-raw",
                "raw_current": "current-raw",
            }
        ],
        tmp_path,
        requested_frequencies_hz=(6_085_000_000, 6_105_000_000, 6_125_000_000),
        completed=False,
        failed_frequency_hz=6_105_000_000,
        error="TimeoutError: point timeout",
    )
    metadata = json.loads(Path(artifacts["metadata"]).read_text(encoding="utf-8"))
    with open(artifacts["csv"], encoding="utf-8-sig", newline="") as handle:
        row = next(csv.DictReader(handle))
    assert metadata["status"] == "partial"
    assert metadata["completed_points"] == 1
    assert metadata["failed_frequency_hz"] == 6_105_000_000
    assert "raw" not in row and "raw_current" not in row
    assert row["simulated"] == "False"
    raw_dir = Path(artifacts["run_dir"]) / "raw"
    assert (raw_dir / "point_00_modulation_average.txt").read_text() == "average-raw"
    assert (raw_dir / "point_00_modulation_current.txt").read_text() == "current-raw"


def test_power_sweep_artifacts_preserve_partial_points_and_raw(tmp_path: Path):
    artifacts = save_power_sweep_result(
        [{"generator_power_dbm": -60.0, "evm_all_carriers_db": -34.0, "raw": "raw"}],
        tmp_path,
        requested_powers_dbm=(-60.0, -55.0, -50.0, -45.0, -40.0),
        completed=False,
        failed_power_dbm=-55.0,
        error="TimeoutError: point timeout",
    )
    metadata = json.loads(Path(artifacts["metadata"]).read_text(encoding="utf-8"))
    with open(artifacts["csv"], encoding="utf-8-sig", newline="") as handle:
        row = next(csv.DictReader(handle))
    assert metadata["status"] == "partial"
    assert metadata["failed_power_dbm"] == -55.0
    assert row["simulated"] == "False"
    assert "raw" not in row
    assert (Path(artifacts["run_dir"]) / "raw/point_00_modulation_average.txt").read_text() == "raw"
