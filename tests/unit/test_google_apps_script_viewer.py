from pathlib import Path


ROOT = Path("deploy/google-apps-script")


def test_apps_script_viewer_has_required_web_app_files() -> None:
    for filename in ("Code.gs", "Index.html", "Stylesheet.html", "JavaScript.html", "appsscript.json"):
        assert (ROOT / filename).is_file()
    assert "function doGet()" in (ROOT / "Code.gs").read_text(encoding="utf-8")


def test_cloud_viewer_is_read_only_and_has_historical_comparison() -> None:
    page = (ROOT / "Index.html").read_text(encoding="utf-8")
    javascript = (ROOT / "JavaScript.html").read_text(encoding="utf-8")
    combined = page + javascript

    assert "READ ONLY" in page
    assert 'type="file"' in page
    assert "evm_all_db" in combined
    assert "frequency_error_hz" in combined
    # 雲端分享版不得包含實機控制或公司內網儀器端點。
    assert "192.168.200.50" not in combined
    assert "/api/jobs/" not in combined
    assert "enable-hardware" not in combined
