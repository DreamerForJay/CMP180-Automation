from pathlib import Path


STATIC_V2 = Path("src/cmp180_evm/web/static_v2")


def test_v2_uses_one_stylesheet_and_one_application_script():
    html = (STATIC_V2 / "index.html").read_text(encoding="utf-8")
    assert html.count('rel="stylesheet"') == 1
    assert html.count("<script") == 1
    assert 'href="/app.css?v=3"' in html
    assert 'src="/app.js?v=3"' in html


def test_v2_contains_measurement_workflow_and_rf_hold_guidance():
    html = (STATIC_V2 / "index.html").read_text(encoding="utf-8")
    assert 'id="planForm"' in html
    assert 'data-axis="single"' in html
    assert 'data-axis="frequency"' in html
    assert 'data-axis="power"' in html
    assert "--enable-hardware" in html
    assert "RF 暫停" in html


def test_v2_has_mobile_navigation_and_reduced_motion_rules():
    css = (STATIC_V2 / "app.css").read_text(encoding="utf-8")
    assert "@media(max-width:1050px)" in css
    assert "@media(max-width:720px)" in css
    assert "prefers-reduced-motion" in css
    assert "focus-visible" in css


def test_v2_exposes_traceable_run_output_and_recoverable_record_actions():
    html = (STATIC_V2 / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC_V2 / "app.js").read_text(encoding="utf-8")
    assert 'id="resultTimestamp"' in html
    assert 'id="resultOutput"' in html
    assert 'id="runDialog"' in html
    assert 'id="trashRunId"' in html
    assert "/open-folder" in javascript
    assert "/trash" in javascript
    assert "output/.trash" in javascript


def test_v2_is_an_rf_workstation_without_a_repeated_global_measurement_hero():
    html = (STATIC_V2 / "index.html").read_text(encoding="utf-8")
    javascript = (STATIC_V2 / "app.js").read_text(encoding="utf-8")
    assert "建立量測計畫" not in html
    assert 'id="themeButton"' in html
    assert 'id="runSearch"' in html
    assert 'id="runSort"' in html
    assert 'id="compareRuns"' in html
    assert 'id="chartMetric"' in html
    assert 'id="traceList"' in html
    assert "localStorage.setItem('cmp180-theme'" in javascript
    assert "drawTraces" in javascript
    assert "chartZoom" in javascript
    assert "chartCursors" in javascript
    assert 'id="calibrationForm"' in html
    assert "/api/calibration/draft-preview" in javascript
