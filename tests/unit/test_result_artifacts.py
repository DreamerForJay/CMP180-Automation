import csv
import json
from pathlib import Path

from cmp180_evm.results.artifacts import save_single_result


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
