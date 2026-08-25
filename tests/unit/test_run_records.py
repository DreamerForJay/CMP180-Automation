import json

import pytest

from cmp180_evm.web.run_records import load_run_record, move_run_to_trash, resolve_run_dir


def make_run(output_root, name="run_one", run_id="abc123"):
    run_dir = output_root / name
    run_dir.mkdir()
    (run_dir / "metadata.json").write_text(
        json.dumps({"run_id": run_id, "frequency_hz": 6_105_000_000}), encoding="utf-8"
    )
    (run_dir / "results.json").write_text(json.dumps([{"evm": -36.0}]), encoding="utf-8")
    return run_dir


def test_load_run_returns_settings_results_and_legacy_waveform_state(tmp_path):
    make_run(tmp_path)
    record = load_run_record(tmp_path, "run_one")
    assert record["metadata"]["frequency_hz"] == 6_105_000_000
    assert record["results"] == [{"evm": -36.0}]
    assert record["waveform_recorded"] is False
    assert record["output_location"] == "output/run_one/"


def test_resolve_run_blocks_traversal_and_non_run_directories(tmp_path):
    make_run(tmp_path)
    with pytest.raises(ValueError, match="Invalid run key"):
        resolve_run_dir(tmp_path, "../run_one")
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ValueError, match="no metadata"):
        resolve_run_dir(tmp_path, "empty")


def test_trash_requires_exact_run_id_and_preserves_run_for_recovery(tmp_path):
    run_dir = make_run(tmp_path)
    with pytest.raises(ValueError, match="does not match"):
        move_run_to_trash(tmp_path, "run_one", "wrong")
    result = move_run_to_trash(tmp_path, "run_one", "abc123")
    assert result["status"] == "trashed"
    assert not run_dir.exists()
    assert (tmp_path / ".trash" / result["trash_key"] / "metadata.json").is_file()
