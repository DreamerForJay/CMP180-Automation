from pathlib import Path

from cmp180_evm.web.server import STATIC_DIR

STATIC = Path("src/cmp180_evm/web/static")


def test_original_workspace_is_the_served_frontend() -> None:
    assert STATIC_DIR.name == "static"
    assert (STATIC_DIR / "index.html").is_file()


def test_demo_exposes_advanced_pa_metrics_without_hardware_endpoint() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC / "app.js").read_text(encoding="utf-8")

    assert 'data-demo-tab="advancedPa"' in html
    assert 'id="advancedPaForm"' in html
    assert 'id="oip3Chart"' in html
    assert 'id="harmonicChart"' in html
    assert 'id="acpChart"' in html
    assert "/api/mock/pa-advanced" in javascript
    advanced_code = javascript.split("$('#advancedPaForm').onsubmit", 1)[1].split(
        "let latestAxis", 1
    )[0]
    assert "/api/hardware/" not in advanced_code


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
    # 單筆歷史紀錄與多筆比較共用唯讀圖表引擎，不應強迫至少勾選兩筆。
    assert "count<1||count>8" in javascript
    assert "analysisTraces.length<1" in javascript
    assert "analysisTraces.length<2" not in comparison_code


def test_loopback_page_exposes_live_trends_and_traceable_analysis() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC / "loopback.js").read_text(encoding="utf-8")
    assert 'data-tab="loopback"' in html
    assert 'id="loopbackCharts"' in html
    assert 'id="loopbackRows"' in html
    assert "/api/hardware/loopback-preview" in javascript
    assert "/api/jobs/hardware/loopback" in javascript
    assert "analysis.outliers" in javascript
    assert "renderLoopbackLive" in javascript
    # 面板宣稱 INVALID 與 IQR outlier 都會標成紅色；圖表必須真的標出 outlier 點。
    assert "loopback-outlier-dot" in javascript
    assert "loopback-outlier-dot" in (STATIC / "design-system.css").read_text(encoding="utf-8")
    assert "loopback-invalid" in javascript
    assert "preview.profile_lifecycle === 'approved'" in javascript
    assert 'id="runAllLoopbacks"' in html
    assert "/api/hardware/loopback-batch-preview" in javascript
    assert "/api/jobs/hardware/loopback-batch" in javascript


def test_all_operator_plan_reviews_follow_the_selected_language() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    app = (STATIC / "app.js").read_text(encoding="utf-8")
    plan_scripts = {
        name: (STATIC / name).read_text(encoding="utf-8")
        for name in (
            "hardware.js",
            "custom-plan.js",
            "gprf-power.js",
            "loopback.js",
            "campaign.js",
            "calibration.js",
        )
    }

    # 切換語言必須通知已顯示的 Preview 重繪，且不得靠重新送出 RF／preview 請求。
    assert "cmp180-language-change" in app
    for name, source in plan_scripts.items():
        assert "language === 'zh'" in source, name
    for name in ("hardware.js", "custom-plan.js", "gprf-power.js", "loopback.js", "campaign.js", "calibration.js"):
        assert "cmp180-language-change" in plan_scripts[name], name

    # 後端保留英文稽核內容；共用顯示層要翻譯安全拒絕原因，且跨頁沿用同一入口。
    assert "function localizePlanDetail" in plan_scripts["hardware.js"]
    assert "後端安全閘門以英文保存稽核原因" in plan_scripts["hardware.js"]
    assert "Generator 功率超出核准範圍" in plan_scripts["hardware.js"]
    assert "window.localizePlanDetail" in plan_scripts["loopback.js"]
    assert "window.localizePlanDetail" in plan_scripts["campaign.js"]

    # 各頁的靜態檢查步驟、按鈕與安全說明也必須由同一份語系字典控制。
    for key in (
        "hardwareSop3",
        "reviewSingle",
        "reviewPlan",
        "reviewGprf",
        "loopbackWarningHelp",
        "runAllLoopbacksHelp",
        "campaignRulesHelp",
        "campaignEvidence",
        "calibrationHelp",
        "calculateDraft",
    ):
        assert f'data-i18n="{key}"' in html
        assert f"{key}:" in app


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


def test_hardware_frequency_sweep_defaults_to_approved_wlan_section() -> None:
    plan = (STATIC / "custom-plan.js").read_text(encoding="utf-8")

    # 實機 frequency sweep 預設必須落在已核准 6 GHz/BW320 section，避免使用者一切換
    # 掃描軸就得到不可執行的非 WLAN 空隙計畫。
    assert "form.start.value = powerAxis ? -55 : 5925" in plan
    assert "form.stop.value = powerAxis ? -30 : 6125" in plan


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
    assert 'id="diagramShowcaseFrame"' in html
    assert "/diagrams/system-architecture.html?present=1" in html
    assert "diagramPlaybackUrl" in javascript
    assert 'src="/assets/cmp180-hero.png"' in html
    assert (STATIC / "assets" / "cmp180-hero.png").is_file()
    assert ".cmp180-visual" in design
    assert "signal-console" not in html
    # 首頁 CTA 只切換前端工作區，不得直接呼叫 RF API。
    navigation_code = javascript.split("document.querySelectorAll('[data-go-tab]')", 1)[
        1
    ].split("document.querySelectorAll('[data-measure-view]')", 1)[0]
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
    assert 'data-i18n="sweepSetup"' in html


def test_hardware_tabs_and_stable_chart_interactions() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC / "app.js").read_text(encoding="utf-8")
    hardware = (STATIC / "hardware.js").read_text(encoding="utf-8")
    design = (STATIC / "design-system.css").read_text(encoding="utf-8")

    for action in ("single", "frequency", "power"):
        assert f'data-hardware-action="{action}"' in html
    assert 'data-hardware-action="gprf"' in html
    assert 'id="gprfPowerForm"' in html
    assert "reviewAndExecuteGprfPowerPlan" in (STATIC / "gprf-power.js").read_text(
        encoding="utf-8"
    )
    assert 'id="hardwareProfileSummary"' in html
    assert 'id="singlePlanForm"' in html
    assert "/api/hardware/single-plan-preview" in hardware
    assert "...singlePlanPayload" in hardware
    assert 'class="sop-steps measurement-sop"' in html
    assert 'id="planCheckText"' in html
    assert 'id="hardwareSweepSetup"' in html
    assert "selectHardwareAction" in hardware
    assert "WLAN EVM Frequency Sweep: review first" in hardware
    assert "GPRF: RF power only" in hardware
    # 圖表平移必須限制在固定畫布內，且不得造成 Y 軸跟著游標漂移。
    assert "chartFrame.width-width" in javascript
    assert "chartView.y=0" in javascript
    assert "chart-crosshair" in javascript
    assert "chartAxisMarkup" in javascript
    assert "xTicks=xmin===xmax?1:6" in javascript
    assert 'id="matplotlibGallery"' in html
    assert 'id="matplotlibMetric"' in html
    assert "renderMatplotlibGallery" in javascript
    assert "matplotlib-active-plot" in design


def test_gprf_power_chart_has_flatness_analysis_and_contrast() -> None:
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC / "app.js").read_text(encoding="utf-8")
    hardware = (STATIC / "hardware.js").read_text(encoding="utf-8")
    design = (STATIC / "design-system.css").read_text(encoding="utf-8")

    assert 'data-i18n="measurementTab"' in html
    assert 'data-i18n="calibrationTab"' in html
    assert "measurementTab:'Measure'" in javascript
    assert "calibrationTab:'Calibration'" in javascript
    assert 'value="power_error_db"' in html
    assert 'name="input_cable_loss_db"' in html
    assert 'name="output_cable_loss_db"' in html
    assert 'name="external_gain_db"' in html
    assert 'name="expected_dut_gain_db"' in html
    assert 'name="output_attenuator_db"' in html
    assert 'id="loadPaProfileButton"' in html
    # 靜態資源版本必須跟著 profile UI 修正提升，避免現場瀏覽器沿用舊摘要與安全文案。
    assert 'src="/app.js?v=console17"' in html
    assert 'src="/hardware.js?v=single-range9"' in html
    assert 'src="/gprf-power.js?v=5"' in html
    assert 'value="0" min="0" max="120" step="0.01" required><b>dB</b></div><small class="field-help">實體衰減器' in html
    gprf = (STATIC / "gprf-power.js").read_text(encoding="utf-8")
    assert "function loadApprovedPaProfile" in gprf
    assert "stopWithoutAttenuator: -25" in gprf
    assert "window.loadApprovedPaProfile" in gprf
    # Loader 填值後必須刷新摘要；GPRF 文案允許已登錄的 fixture 衰減器。
    assert gprf.count("updateHardwareSummary();") >= 3
    assert "safetyCheckHelpGprf:'目前只核准 RF1.1 → RF1.5。確認線材、衰減器與轉接件都已登錄於計畫" in javascript
    assert 'translations[language].safetyCheckHelpGprf' in hardware
    assert 'name="sa_safe_limit_dbm"' in html
    assert "external_attenuation_db: 0" in gprf
    assert 'value="gain_db"' in html
    assert 'value="pout_dbm"' in html
    assert "<th>Power Error (dB)</th>" in html
    assert "powerFlatnessStats" in javascript
    assert "p1dbMetrics" in javascript
    assert "Max Compression" in javascript
    assert "expected_power_dbm:expectedPower" in javascript
    assert "pin_dbm:pin" in javascript
    assert "pout_dbm:pout" in javascript
    assert "gain_db:gain" in javascript
    assert "formatMeasured(point.power_error_db,3)" in javascript
    assert "Power Error 是 GPRF flatness" in javascript
    assert "Peak-to-Peak Ripple" in javascript
    assert "Expected error 0 dB" in javascript
    assert "Expected = Generator Power" in javascript
    assert "Pexpected = Pgenerator" in javascript
    assert "expected-power-line" in javascript
    assert 'id="gprfModeTitle"' in html
    assert "metricAxisLabel" in javascript
    assert "Generator Power':'Frequency" in javascript
    assert 'class="axis-title"' in javascript
    assert ".plot-line{fill:none;stroke:#1e88ff" in design
    assert "[data-theme=\"light\"] .plot-line{stroke:#0877ff" in design


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
