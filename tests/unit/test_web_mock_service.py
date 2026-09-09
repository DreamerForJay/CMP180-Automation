import csv
import json
from pathlib import Path

import pytest

from cmp180_evm.web.mock_service import (
    build_frequency_points,
    build_power_points,
    save_mock_run,
    simulate_point,
)
from cmp180_evm.web.server import (
    Cmp180WebHandler,
    ExclusiveThreadingHTTPServer,
    list_run_history,
    validate_cable_route,
    validate_custom_hardware_startup,
    validate_hardware_bind,
)


def test_web_server_disables_address_reuse_to_prevent_stale_duplicate_instances():
    assert ExclusiveThreadingHTTPServer.allow_reuse_address is False


def test_run_history_is_newest_first_and_exposes_only_safe_artifact_urls(tmp_path):
    older = tmp_path / "older_run"
    newer = tmp_path / "newer_run"
    older.mkdir()
    newer.mkdir()
    (older / "metadata.json").write_text(
        json.dumps({"run_id": "old", "created_at": "2026-08-20T01:00:00+00:00", "simulated": True}),
        encoding="utf-8",
    )
    (newer / "metadata.json").write_text(
        json.dumps(
            {
                "run_id": "new",
                "created_at": "2026-08-20T02:00:00+00:00",
                "simulated": False,
                "status": "partial",
                "completed_points": 2,
            }
        ),
        encoding="utf-8",
    )
    (newer / "report.html").write_text("ok", encoding="utf-8")

    runs = list_run_history(tmp_path)

    assert [run["run_id"] for run in runs] == ["new", "old"]
    assert runs[0]["artifact_urls"] == {
        "metadata": "/artifacts/newer_run/metadata.json",
        "report": "/artifacts/newer_run/report.html",
    }
    assert "run_dir" not in runs[0]


def test_run_history_skips_corrupt_metadata(tmp_path):
    broken = tmp_path / "broken"
    broken.mkdir()
    (broken / "metadata.json").write_text("not-json", encoding="utf-8")
    assert list_run_history(tmp_path) == []


def test_frequency_points_are_inclusive_and_bounded():
    assert build_frequency_points(5_925e6, 5_965e6, 20e6) == [5_925e6, 5_945e6, 5_965e6]
    with pytest.raises(ValueError, match="11-point"):
        build_frequency_points(1, 12, 1)


def test_power_points_are_inclusive_and_bounded():
    assert build_power_points(-50, -40, 5) == [-50, -45, -40]
    with pytest.raises(ValueError, match="11-point"):
        build_power_points(-12, -1, 1)


def test_simulation_is_deterministic_and_labeled():
    first = simulate_point(6_105e6, 320e6, -40)
    second = simulate_point(6_105e6, 320e6, -40)
    assert first == second
    assert first.valid is True
    assert first.generator_power_dbm == -40


def test_simulated_evm_varies_with_power_at_fixed_frequency():
    # Power vs EVM 圖表要有意義，功率越高（越接近 -40 dBm 上限）EVM 應該越差。
    lower_power = simulate_point(6_105e6, 320e6, -60)
    higher_power = simulate_point(6_105e6, 320e6, -40)
    assert higher_power.evm_all_db > lower_power.evm_all_db


def test_mock_artifacts_include_csv_json_and_html(tmp_path):
    point = simulate_point(6_105e6, 320e6, -40)
    artifacts = save_mock_run([point], tmp_path, "unit-test")
    with open(artifacts["csv"], encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    payload = json.loads(open(artifacts["json"], encoding="utf-8").read())
    metadata = json.loads(open(artifacts["run_dir"] + "/metadata.json", encoding="utf-8").read())
    assert len(rows) == 1
    assert payload["simulated"] is True
    assert rows[0]["limit_status"] == "DRAFT_PASS"
    assert metadata["limit_profile"]["lifecycle"] == "draft"
    assert metadata["compliance_claim"] is False
    assert metadata["created_at"] == payload["created_at"]
    assert metadata["completed_points"] == 1
    assert metadata["source"] == "web-demo"
    assert "SIMULATED" in open(artifacts["report"], encoding="utf-8").read()
    assert Path(artifacts["matplotlib_evm_all_carriers_db"]).is_file()
    assert Path(artifacts["matplotlib_burst_power_dbm"]).is_file()


def test_run_history_recovers_legacy_demo_timestamp_without_rewriting_artifacts(tmp_path):
    run = tmp_path / "legacy-demo"
    run.mkdir()
    metadata_path = run / "metadata.json"
    metadata_path.write_text(
        json.dumps({"run_id": "legacy", "point_count": 3, "simulated": True}),
        encoding="utf-8",
    )
    (run / "results.json").write_text(
        json.dumps({"created_at": "2026-08-25T08:00:00+00:00", "points": []}),
        encoding="utf-8",
    )

    result = list_run_history(tmp_path)[0]

    assert result["created_at"] == "2026-08-25T08:00:00+00:00"
    assert result["completed_points"] == 3
    assert "created_at" not in json.loads(metadata_path.read_text(encoding="utf-8"))


def test_web_hardware_endpoint_is_enabled_for_local_workstation_by_default():
    # 啟動服務本身不會送 RF；每個執行 request 仍需通過接線與安全檢查。
    assert Cmp180WebHandler.hardware_enabled is True
    assert Cmp180WebHandler.custom_hardware_enabled is True


def test_cable_route_accepts_verified_variants_and_blocks_custom_route():
    assert validate_cable_route(" RF1.1 → RF1.5 ") == "RF1.1-RF1.5"
    with pytest.raises(ValueError, match="not hardware-verified"):
        validate_cable_route("RF1.2-RF1.6")


def test_hardware_mode_must_not_bind_to_network_interfaces():
    validate_hardware_bind("127.0.0.1", True)
    validate_hardware_bind("0.0.0.0", False)
    with pytest.raises(ValueError, match="loopback"):
        validate_hardware_bind("0.0.0.0", True)


def test_custom_hardware_requires_hardware_control_and_loopback():
    validate_custom_hardware_startup("127.0.0.1", True, True)
    with pytest.raises(ValueError, match="requires hardware control"):
        validate_custom_hardware_startup("127.0.0.1", False, True)
    with pytest.raises(ValueError, match="loopback"):
        validate_custom_hardware_startup("0.0.0.0", True, True)


def test_output_location_is_project_relative_and_hides_absolute_path(tmp_path):
    run_dir = tmp_path / "20260820T000000Z_demo_abc123"
    artifacts = {"run_dir": str(run_dir), "run_id": "abc123"}
    location = Cmp180WebHandler._output_location(artifacts)
    assert location == "output/20260820T000000Z_demo_abc123/"
    assert str(tmp_path) not in location
