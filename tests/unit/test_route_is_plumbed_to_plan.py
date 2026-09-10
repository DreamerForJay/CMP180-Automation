"""Regression tests: the confirmed route must reach the plan, not just the UI text."""

import json

import pytest

from cmp180_evm.web.hil_campaign import HilCampaignStore, _route_executable
from cmp180_evm.web.real_service import DEFAULT_ROUTE, _ports_from_request


def test_route_from_request_selects_the_analyzer_port():
    """接線換到 RF1.6 時 plan 必須跟著換，否則 analyzer 仍停在 RF1.5 收不到訊號。"""
    assert _ports_from_request({"cable_confirmation": "RF1.1-RF1.6"}) == ("RF1.1", "RF1.6")
    assert _ports_from_request({"cable_confirmation": " rf1.1 → rf2.8 "}) == ("RF1.1", "RF2.8")


def test_missing_route_falls_back_to_the_hil_verified_default():
    assert _ports_from_request({}) == tuple(DEFAULT_ROUTE.split("-"))


def test_route_without_hil_evidence_is_executable():
    allowed, reason = _route_executable("RF1.1-RF1.6")
    assert allowed is True
    assert reason == ""


def test_generator_side_route_is_refused_with_the_real_reason():
    """訊息必須說出真正原因（切不過去），不能只寫模糊的『未驗證』。"""
    allowed, reason = _route_executable("RF1.2-RF1.5")
    assert allowed is False
    assert "cannot be selected remotely" in reason


@pytest.mark.parametrize("route", ["RF1.1-RF1.1", "RF1.1-RF9.9"])
def test_physically_impossible_routes_stay_blocked(route):
    allowed, _ = _route_executable(route)
    assert allowed is False


def test_campaign_no_longer_generates_permanently_blocked_route_cases(tmp_path):
    """自動產生的案例必須都是真的跑得起來的，否則就是永遠不會消失的假待辦。"""
    store = HilCampaignStore(tmp_path / "state.json")
    cases = store.reset()["cases"]
    route_cases = [case for case in cases if case["category"] == "route"]
    assert route_cases, "route cases should still exist"
    for case in route_cases:
        allowed, reason = _route_executable(case["route"])
        assert allowed, f'{case["case_id"]} can never run: {reason}'
    # 同 port 與 generator 端換 port 的假案例都不應再被產生。
    labels = {case["route"] for case in route_cases}
    assert "RF1.1-RF1.1" not in labels
    assert not any(route.split("-")[0] != "RF1.1" for route in labels)


def test_prepare_marks_executable_route_cases_ready(tmp_path):
    store = HilCampaignStore(tmp_path / "state.json")
    store.reset()
    prepared = store.prepare()
    ready = [
        case for case in prepared["cases"]
        if case["category"] == "route" and case["state"] == "ready"
    ]
    assert ready, "route cases must become READY so the campaign can gather evidence"
    saved = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    assert saved["cases"]
