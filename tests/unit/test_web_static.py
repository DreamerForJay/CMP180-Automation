from pathlib import Path


STATIC_ROOT = Path("src/cmp180_evm/web/static")


def test_operator_guide_and_design_system_are_loaded():
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
    assert '/design-system.css?v=console3' in html
    assert 'id="guide"' in html
    assert 'data-copy-target="cmd-demo"' in html
    assert "--enable-hardware" in html
    assert "RF HOLD" in html


def test_console_design_system_has_required_responsive_and_accessibility_rules():
    css = (STATIC_ROOT / "design-system.css").read_text(encoding="utf-8")
    assert "width:min(1680px" in css
    assert "@media(max-width:1100px)" in css
    assert "@media(max-width:720px)" in css
    assert "prefers-reduced-motion" in css
    assert ":focus-visible" in css
