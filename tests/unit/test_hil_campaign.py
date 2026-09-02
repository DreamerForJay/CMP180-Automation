import json
from pathlib import Path

from cmp180_evm.web.hil_campaign import HilCampaignStore


def test_campaign_prepare_separates_ready_from_blocked(tmp_path: Path) -> None:
    store = HilCampaignStore(tmp_path / "state.json")
    state = store.prepare()
    by_id = {case["case_id"]: case for case in state["cases"]}
    assert by_id["b6-bw320"]["state"] == "ready"
    assert by_id["b6-power"]["state"] == "blocked"
    assert "Requires successful case" in by_id["b6-power"]["reason"]
    assert by_id["b24-bw20"]["state"] == "ready"
    assert by_id["b6-bw20"]["state"] == "ready"


def test_campaign_progress_persists_and_reset_preserves_external_artifacts(tmp_path: Path) -> None:
    state_path = tmp_path / "campaign" / "state.json"
    store = HilCampaignStore(state_path)
    store.prepare()
    store.update_case("b6-bw320", state="complete", artifacts={"run_dir": "output/run-1"})
    reloaded = HilCampaignStore(state_path).load()
    case = next(item for item in reloaded["cases"] if item["case_id"] == "b6-bw320")
    assert case["state"] == "complete"
    assert case["artifacts"]["run_dir"] == "output/run-1"
    reset = store.reset()
    reset_case = next(item for item in reset["cases"] if item["case_id"] == "b6-bw320")
    assert reset_case["state"] == "pending"
    assert json.loads(state_path.read_text(encoding="utf-8"))["schema_version"] == 1


def test_server_restart_marks_inflight_case_interrupted(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    store = HilCampaignStore(state_path)
    store.prepare()
    store.update_case("b6-bw320", state="running", job_id="old-job")
    recovered = HilCampaignStore(state_path).load()
    case = next(item for item in recovered["cases"] if item["case_id"] == "b6-bw320")
    assert case["state"] == "interrupted"
    assert "Server restarted" in case["reason"]


def test_prepare_preserves_failure_and_retry_uses_known_good_baseline(tmp_path: Path) -> None:
    store = HilCampaignStore(tmp_path / "state.json")
    store.prepare()
    store.update_case("b6-bw320", state="failed", reason="INV", artifacts={"run_dir": "old"})
    prepared = store.prepare()
    failed = next(item for item in prepared["cases"] if item["case_id"] == "b6-bw320")
    assert failed["state"] == "failed"
    assert failed["request"]["start_hz"] == 6_085_000_000
    retried = store.retry("b6-bw320")
    assert next(item for item in retried["cases"] if item["case_id"] == "b6-bw320")["state"] == "pending"
    ready = store.prepare()
    baseline = next(item for item in ready["cases"] if item["case_id"] == "b6-bw320")
    power = next(item for item in ready["cases"] if item["case_id"] == "b6-power")
    assert baseline["state"] == "ready"
    assert baseline["request"]["generator_power_dbm"] == -40
    assert power["state"] == "blocked"
    assert "Requires successful case" in power["reason"]
