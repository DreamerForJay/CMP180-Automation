from pathlib import Path


STATIC_V2 = Path("src/cmp180_evm/web/static_v2")


def test_v2_uses_one_stylesheet_and_one_application_script():
    html = (STATIC_V2 / "index.html").read_text(encoding="utf-8")
    assert html.count('rel="stylesheet"') == 1
    assert html.count("<script") == 1
    assert 'href="/app.css?v=1"' in html
    assert 'src="/app.js?v=1"' in html


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
