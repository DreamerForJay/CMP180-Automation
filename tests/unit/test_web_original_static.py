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
