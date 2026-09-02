import json
from pathlib import Path

from cmp180_evm.acceptance import build_v1_acceptance_report


def test_draft_profiles_keep_v1_acceptance_blocked(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "metadata.json").write_text(
        json.dumps({"run_id": "real-1", "simulated": False, "status": "complete"}),
        encoding="utf-8",
    )
    (run_dir / "results.json").write_text(
        json.dumps([{"valid": True}]), encoding="utf-8"
    )

    html_path, json_path = build_v1_acceptance_report(
        Path("configs/calibration.example.yaml"),
        Path("configs/limits.example.yaml"),
        (run_dir,),
        tmp_path / "acceptance",
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["overall_status"] == "BLOCKED"
    assert payload["compliance_claim"] is False
    assert {gate["gate_id"]: gate["status"] for gate in payload["gates"]} == {
        "calibration": "BLOCKED",
        "limits": "BLOCKED",
        "hil_evidence": "PASS",
    }
    report = html_path.read_text(encoding="utf-8")
    assert report.index("V1 驗收報告") < report.index("V1 Acceptance Report")


def test_mock_or_invalid_evidence_never_passes_hil_gate(tmp_path: Path) -> None:
    run_dir = tmp_path / "mock"
    run_dir.mkdir()
    (run_dir / "metadata.json").write_text(
        json.dumps({"run_id": "mock-1", "simulated": True, "status": "complete"}),
        encoding="utf-8",
    )
    (run_dir / "results.json").write_text(json.dumps([{"valid": True}]), encoding="utf-8")
    _, json_path = build_v1_acceptance_report(
        Path("configs/calibration.example.yaml"),
        Path("configs/limits.example.yaml"),
        (run_dir,),
        tmp_path / "acceptance",
    )
    gates = json.loads(json_path.read_text(encoding="utf-8"))["gates"]
    assert next(gate for gate in gates if gate["gate_id"] == "hil_evidence")["status"] == "BLOCKED"


def _approved_profiles(tmp_path: Path) -> tuple[Path, Path]:
    """Write owner-approved calibration/limit profiles for the accepted path."""
    calibration = tmp_path / "calibration.yaml"
    calibration.write_text(
        "profile_id: \"rf1.1-rf1.5-direct-cable\"\n"
        "revision: \"1.0\"\n"
        "lifecycle: \"approved\"\n"
        "route: \"RF1.1-RF1.5\"\n"
        "calibrated_at: 2026-09-01\n"
        "expires_at: 2027-12-31\n"
        "equipment_reference: \"cable SN-TEST\"\n"
        "source_evidence: \"output/test-evidence\"\n"
        "approved_by: \"rf-owner\"\n"
        "approved_at: 2026-09-01\n"
        "points:\n"
        "  - frequency_hz: 5925000000\n"
        "    loss_db: 0.3\n"
        "  - frequency_hz: 7125000000\n"
        "    loss_db: 0.4\n",
        encoding="utf-8",
    )
    limits = tmp_path / "limits.yaml"
    limits.write_text(
        "profile_id: \"eht-mcs11-bw320-loopback\"\n"
        "revision: \"1.0\"\n"
        "lifecycle: \"approved\"\n"
        "description: \"Owner-approved profile\"\n"
        "maximum_evm_db: -32.0\n"
        "maximum_absolute_frequency_error_hz: 1000.0\n"
        "maximum_absolute_power_error_db: 3.0\n"
        "source_reference: \"internal RF specification\"\n"
        "approved_by: \"rf-owner\"\n"
        "approved_at: 2026-09-01\n",
        encoding="utf-8",
    )
    return calibration, limits


def test_approved_profiles_with_valid_evidence_reach_accepted(tmp_path: Path) -> None:
    calibration, limits = _approved_profiles(tmp_path)
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "metadata.json").write_text(
        json.dumps({"run_id": "real-1", "simulated": False, "status": "complete"}),
        encoding="utf-8",
    )
    (run_dir / "results.json").write_text(json.dumps([{"valid": True}]), encoding="utf-8")

    _, json_path = build_v1_acceptance_report(
        calibration, limits, (run_dir,), tmp_path / "acceptance"
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["overall_status"] == "ACCEPTED"
    # 驗收通過仍不得自稱 compliance；那是 RF owner 對 DUT 的宣告，不是本工具的輸出。
    assert payload["compliance_claim"] is False
    assert all(gate["status"] == "PASS" for gate in payload["gates"])


def test_legacy_singleshot_schema_is_accepted_when_reliability_is_zero(tmp_path: Path) -> None:
    calibration, limits = _approved_profiles(tmp_path)
    run_dir = tmp_path / "legacy"
    run_dir.mkdir()
    (run_dir / "metadata.json").write_text(
        json.dumps({"run_id": "legacy-1", "simulated": False, "status": "complete"}),
        encoding="utf-8",
    )
    # 舊版 SingleShot artifacts 是單一 dict 且沒有 valid 欄位。
    (run_dir / "results.json").write_text(
        json.dumps({"reliability": 0, "evm_all_carriers_db": -36.8}), encoding="utf-8"
    )

    _, json_path = build_v1_acceptance_report(
        calibration, limits, (run_dir,), tmp_path / "acceptance"
    )

    gates = json.loads(json_path.read_text(encoding="utf-8"))["gates"]
    assert next(g for g in gates if g["gate_id"] == "hil_evidence")["status"] == "PASS"


def test_legacy_singleshot_with_nonzero_reliability_is_blocked(tmp_path: Path) -> None:
    calibration, limits = _approved_profiles(tmp_path)
    run_dir = tmp_path / "legacy-bad"
    run_dir.mkdir()
    (run_dir / "metadata.json").write_text(
        json.dumps({"run_id": "legacy-2", "simulated": False, "status": "complete"}),
        encoding="utf-8",
    )
    (run_dir / "results.json").write_text(
        json.dumps({"reliability": 3, "evm_all_carriers_db": -36.8}), encoding="utf-8"
    )

    _, json_path = build_v1_acceptance_report(
        calibration, limits, (run_dir,), tmp_path / "acceptance"
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["overall_status"] == "BLOCKED"
