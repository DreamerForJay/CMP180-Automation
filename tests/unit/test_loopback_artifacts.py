import json

from cmp180_evm.loopback import LoopbackProfile, analyze_loopback
from cmp180_evm.results.loopback_artifacts import save_loopback_result


def test_loopback_artifacts_preserve_raw_and_profile(tmp_path):
    measurements = [{
        "repeat_index": 1,
        "timestamp": "2026-09-03T00:00:00+00:00",
        "valid": True,
        "evm_all_carriers_db": "-36.9",
        "burst_power_dbm": "-39.8",
        "frequency_error_hz": "-17",
        "raw": "0,raw,values",
        "invalid_reasons": [],
        "instrument_errors": [],
        "cleanup_errors": [],
    }]
    result = {
        "completed": True,
        "measurements": measurements,
        "analysis": analyze_loopback(measurements, LoopbackProfile(minimum_repeats=2)),
    }
    artifacts = save_loopback_result(result, tmp_path, simulated=True, metadata={})
    assert "0,raw,values" in (tmp_path / next(tmp_path.iterdir()).name / "raw" / "repeat_001_modulation_average.txt").read_text()
    assert json.loads(open(artifacts["json"], encoding="utf-8").read())["measurements"][0]["raw"] == "0,raw,values"
    assert json.loads(open(artifacts["metadata"], encoding="utf-8").read())["run_id"] == artifacts["run_id"]
