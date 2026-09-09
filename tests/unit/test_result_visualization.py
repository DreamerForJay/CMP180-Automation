import csv
from pathlib import Path

import pytest

from cmp180_evm.results.visualization import (
    build_offline_report,
    write_pandas_matplotlib_plots,
    write_plots,
)


def _fixture(run_dir: Path) -> Path:
    csv_path = run_dir / "results.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "frequency_hz",
                "evm_all_carriers_db",
                "burst_power_dbm",
                "frequency_error_hz",
                "clock_error_ppm",
            ],
        )
        writer.writeheader()
        writer.writerows(
            [
                {
                    "frequency_hz": 6_085_000_000,
                    "evm_all_carriers_db": -36.1,
                    "burst_power_dbm": -40.5,
                    "frequency_error_hz": -8.0,
                    "clock_error_ppm": 0.1,
                },
                {
                    "frequency_hz": 6_105_000_000,
                    "evm_all_carriers_db": -35.9,
                    "burst_power_dbm": -40.4,
                    "frequency_error_hz": -6.0,
                    "clock_error_ppm": 0.2,
                },
            ]
        )
    return csv_path


def _power_sweep_fixture(run_dir: Path) -> Path:
    csv_path = run_dir / "results.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "frequency_hz",
                "generator_power_dbm",
                "evm_all_carriers_db",
                "burst_power_dbm",
                "frequency_error_hz",
                "clock_error_ppm",
            ],
        )
        writer.writeheader()
        writer.writerows(
            [
                {
                    "frequency_hz": 6_105_000_000,
                    "generator_power_dbm": power,
                    "evm_all_carriers_db": -35.5 + index * 0.1,
                    "burst_power_dbm": power - 0.4,
                    "frequency_error_hz": -5.0 + index,
                    "clock_error_ppm": 0.1,
                }
                for index, power in enumerate((-55, -50, -45, -40))
            ]
        )
    return csv_path


def test_offline_visualization_creates_standard_svg_charts(tmp_path: Path) -> None:
    paths = write_plots(_fixture(tmp_path))
    assert len(paths) == 4
    assert all("<svg" in path.read_text(encoding="utf-8") for path in paths)
    assert "Frequency (MHz)" in paths[0].read_text(encoding="utf-8")


def test_offline_report_embeds_charts_and_escapes_saved_data(tmp_path: Path) -> None:
    csv_path = _fixture(tmp_path)
    with csv_path.open("a", encoding="utf-8", newline="") as handle:
        handle.write('6106000000,"<script>alert(1)</script>",-40,-5,0.2\n')
    report = build_offline_report(tmp_path).read_text(encoding="utf-8")
    assert "CMP180 離線量測報告" in report
    assert "<svg" in report
    assert "<script>alert(1)</script>" not in report
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in report


def test_pandas_matplotlib_visualization_creates_png_charts(tmp_path: Path) -> None:
    pytest.importorskip("pandas")
    pytest.importorskip("matplotlib")
    paths = write_pandas_matplotlib_plots(_fixture(tmp_path))
    assert len(paths) == 4
    assert all(path.read_bytes().startswith(b"\x89PNG") for path in paths)


def test_visualization_uses_power_axis_when_power_varies(tmp_path: Path) -> None:
    pytest.importorskip("pandas")
    pytest.importorskip("matplotlib")
    csv_path = _power_sweep_fixture(tmp_path)
    svg = write_plots(csv_path)[0].read_text(encoding="utf-8")
    png_paths = write_pandas_matplotlib_plots(csv_path)

    assert "Generator Power (dBm)" in svg
    assert len(png_paths) == 4
    assert all(path.read_bytes().startswith(b"\x89PNG") for path in png_paths)
