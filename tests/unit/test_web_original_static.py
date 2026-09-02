from pathlib import Path

from cmp180_evm.web.server import STATIC_DIR


STATIC = Path("src/cmp180_evm/web/static")


def test_original_workspace_is_the_served_frontend() -> None:
    assert STATIC_DIR.name == "static"
    assert (STATIC_DIR / "index.html").is_file()


def test_original_workspace_supports_read_only_run_comparison() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC / "app.js").read_text(encoding="utf-8")

    assert "compareSelectedButton" in html
    assert "traceList" in html
    assert "normalizeHistoricalPoints" in javascript
    assert "drawAnalysisChart" in javascript
    # 歷史分析只能呼叫既有唯讀 Run API，不得觸發任何 RF job endpoint。
    comparison_code = javascript.split("async function compareSelectedRuns", 1)[1].split(
        "function renderComparisonControls", 1
    )[0]
    assert "/api/runs/" in comparison_code
    assert "/api/jobs/" not in comparison_code


def test_workspace_navigation_history_and_theme_regressions() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC / "app.js").read_text(encoding="utf-8")
    design = (STATIC / "design-system.css").read_text(encoding="utf-8")

    assert 'id="pageTitle"' in html
    assert "activateTopTab" in javascript
    assert "main > .panel" in javascript
    assert "loadRunHistory();" in javascript
    # 不可用 observer 重寫列內容，否則每次 textContent mutation 都可能再次觸發。
    assert "new MutationObserver" not in javascript
    assert ':root[data-theme="light"]' in design
    assert '.sop-steps li::before{content:none' in design


def test_runs_filters_inline_details_and_rf_trace_controls() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC / "app.js").read_text(encoding="utf-8")
    design = (STATIC / "design-system.css").read_text(encoding="utf-8")

    for control_id in (
        "runSearch",
        "runDateFilter",
        "runSourceFilter",
        "runStatusFilter",
        "runSort",
    ):
        assert f'id="{control_id}"' in html
    assert "filteredRuns" in javascript
    assert "data-detail-row" in javascript
    assert "window.open(url" in javascript
    assert "open-folder" not in javascript
    assert "data-trace-line" in javascript
    assert "data-trace-point" in javascript
    assert "data-trace-solo" in javascript
    assert "compatibilityWarnings" in javascript
    # 子頁預設隱藏，只顯示 active，避免實機與示範表單堆疊。
    assert ".measurement-view,.demo-panel{display:none}" in design


def test_frequency_unit_switch_is_one_click_not_a_dropdown() -> None:
    """操作員要求單鍵切換 MHz／GHz，不可退回需要展開的下拉選單。"""
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    plan = (STATIC / "custom-plan.js").read_text(encoding="utf-8")

    for field in ("start_unit", "stop_unit", "step_unit", "center_unit"):
        assert f'data-unit-for="{field}"' in html
        # 單位值仍需進入 FormData，但選擇介面必須是按鈕而非 <select>。
        assert f'<input type="hidden" name="{field}" value="MHz">' in html
        assert f'<select name="{field}"' not in html
    assert "[data-unit-for]" in plan
    assert "addEventListener('click'" in plan


def test_web_preflight_and_chart_hover_are_operator_visible() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC / "app.js").read_text(encoding="utf-8")
    hardware = (STATIC / "hardware.js").read_text(encoding="utf-8")

    assert "instrument-block-board" not in html
    assert 'id="blockRunButton"' not in html
    assert "chart-hover-tooltip" in javascript
    assert "data-chart-point" in javascript
    # 摘要改為即時反映使用者輸入的計畫，不再是寫死的固定 profile 對照表。
    assert "hardwareProfileSummary" in hardware
    assert "updateHardwareSummary" in hardware
    assert "即將送出真實 RF" in hardware
    assert "confirm(" in hardware
    assert "reviewAndExecuteCustomHardwarePlan" in hardware
    assert "/api/jobs/hardware/${action}-sweep" not in hardware
    assert "不會改跑固定" in (STATIC / "custom-plan.js").read_text(encoding="utf-8")
    # 積木 Run 必須轉送既有受保護表單，不可直接呼叫 RF endpoint。
    assert "積木介面已移除" in javascript
    assert '<input name="axis" type="hidden"' in html
    assert 'name="start_unit"' in html
    assert 'name="center_unit"' in html
    assert 'id="liveMeasurementChart"' in html
    assert "renderLiveMeasurement" in javascript


def test_product_home_is_safe_bilingual_navigation() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC / "app.js").read_text(encoding="utf-8")
    design = (STATIC / "design-system.css").read_text(encoding="utf-8")

    assert 'id="home"' in html
    assert 'data-tab="home"' in html
    assert 'data-go-tab="measurement"' in html
    assert "homeCopy" in javascript
    assert "activeTopTab='home'" in javascript
    assert ".product-home" in design
    # 首頁 CTA 只切換前端工作區，不得直接呼叫 RF API。
    navigation_code = javascript.split("document.querySelectorAll('[data-go-tab]')", 1)[1].split("document.querySelectorAll('[data-measure-view]')", 1)[0]
    assert "/api/" not in navigation_code


def test_operator_guide_uses_copyable_project_commands() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    design = (STATIC / "design-system.css").read_text(encoding="utf-8")

    assert 'id="quickGuideTitle"' in html
    assert "Set-Location" in html
    assert ".\\.venv\\Scripts\\Activate.ps1" in html
    # PowerShell 的提示符不是指令；複製區不可再把 `PS` 一併送入終端。
    assert "<em>PS</em>" not in html
    assert ".workspace-head{display:none}" in design
    assert "掃描設定 / Sweep Setup" in html


def test_hardware_tabs_and_stable_chart_interactions() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC / "app.js").read_text(encoding="utf-8")
    hardware = (STATIC / "hardware.js").read_text(encoding="utf-8")

    for action in ("single", "frequency", "power"):
        assert f'data-hardware-action="{action}"' in html
    assert 'data-hardware-action="gprf"' in html
    assert 'id="gprfPowerForm"' in html
    assert "reviewAndExecuteGprfPowerPlan" in (STATIC / "gprf-power.js").read_text(
        encoding="utf-8"
    )
    assert 'id="hardwareProfileSummary"' in html
    assert 'class="sop-steps measurement-sop"' in html
    assert 'id="planCheckText"' in html
    assert 'id="hardwareSweepSetup"' in html
    assert "selectHardwareAction" in hardware
    assert "WLAN Frequency Sweep：先 Review" in hardware
    assert "GPRF Power：可掃儀器調諧能力" in hardware
    # 圖表平移必須限制在固定畫布內，且不得造成 Y 軸跟著游標漂移。
    assert "Math.min(900-chartView.width" in javascript
    assert "chartView.y=0" in javascript
    assert "chart-crosshair" in javascript


def test_hil_campaign_is_persistent_and_operator_driven() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    campaign = (STATIC / "campaign.js").read_text(encoding="utf-8")
    assert 'data-tab="campaign"' in html
    assert 'id="campaignRows"' in html
    assert 'id="campaignOperatorHint"' in html
    assert 'id="campaignOperator"' in html
    assert 'id="campaignRoute"' in html
    assert 'class="table-wrap campaign-table-wrap"' in html
    assert 'class="campaign-col-priority"' in html
    assert 'class="campaign-col-evidence"' in html
    assert "RF1.1 Generator output" in html
    assert "/api/hil-campaign/prepare" in campaign
    assert "/api/hil-campaign/cases/" in campaign
    assert "/api/jobs/" in campaign
    assert "campaign-detail" in campaign
    assert "priorityForCase" in campaign
    assert "sortedCampaignCases" in campaign
    assert "campaignCaseOrder" in campaign
    assert "connectionInstruction" in campaign


def test_operator_guide_covers_clone_cli_and_artifacts() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")

    assert "git clone" in html
    assert "DreamerForJay/CMP180-Automation.git" in html
    assert "validate-config" in html
    assert "test-connection" in html
    assert "scripts\\plot_results.py" in html
    assert "scripts\\build_report.py" in html
