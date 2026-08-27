"""Offline SVG charts and HTML reports for saved CMP180 CSV artifacts."""

from __future__ import annotations

import csv
import html
from pathlib import Path

METRICS = (
    ("evm_all_carriers_db", "EVM All", "dB"),
    ("burst_power_dbm", "Burst Power", "dBm"),
    ("frequency_error_hz", "Frequency Error", "Hz"),
    ("clock_error_ppm", "Clock Error", "ppm"),
)


def load_result_rows(csv_path: Path) -> list[dict[str, str]]:
    """Load saved result rows without contacting the instrument."""
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("Results CSV contains no measurement rows")
    return rows


def _number(row: dict[str, str], *names: str) -> float | None:
    for name in names:
        value = row.get(name)
        if value in (None, "", "INV"):
            continue
        try:
            return float(value)
        except ValueError:
            continue
    return None


def _axis(rows: list[dict[str, str]]) -> tuple[str, str, float]:
    if any(_number(row, "generator_power_dbm") is not None for row in rows) and not any(
        _number(row, "frequency_hz") is not None for row in rows
    ):
        return "generator_power_dbm", "Generator Power (dBm)", 1.0
    return "frequency_hz", "Frequency (MHz)", 1e-6


def render_metric_svg(rows: list[dict[str, str]], metric: str, title: str, unit: str) -> str:
    """Render one dependency-free SVG chart from normalized or legacy field names."""
    axis_field, axis_label, axis_scale = _axis(rows)
    aliases = {
        "evm_all_carriers_db": ("evm_all_carriers_db", "evm_all_db"),
        "clock_error_ppm": ("clock_error_ppm", "clock_error"),
    }
    samples = [
        (_number(row, axis_field), _number(row, *(aliases.get(metric, (metric,))))) for row in rows
    ]
    valid = [(x, y) for x, y in samples if x is not None and y is not None]
    if not valid:
        raise ValueError(f"No numeric values available for {metric}")
    xs = [x * axis_scale for x, _ in valid]
    ys = [y for _, y in valid]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    # 單點或同值資料仍保留可見尺度，避免除以零與圖形貼邊。
    xspan = xmax - xmin or 1.0
    ymargin = max((ymax - ymin) * 0.15, 0.5)
    ymin, ymax = ymin - ymargin, ymax + ymargin
    width, height, pad = 960, 420, 64

    def px(value: float) -> float:
        return pad + (value - xmin) / xspan * (width - 2 * pad)

    def py(value: float) -> float:
        return height - pad - (value - ymin) / (ymax - ymin) * (height - 2 * pad)

    grid = []
    for index in range(5):
        gy = pad + index * (height - 2 * pad) / 4
        label = ymax - index * (ymax - ymin) / 4
        grid.append(
            f'<line x1="{pad}" y1="{gy:.1f}" x2="{width - pad}" y2="{gy:.1f}" '
            'stroke="#dbe4ef"/><text x="8" y="{:.1f}" fill="#526173" '
            'font-size="13">{:.3g}</text>'.format(gy + 5, label)
        )
    points = " ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in zip(xs, ys, strict=True))
    dots = "".join(
        f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="5" fill="#0ea5a8">'
        f"<title>x={x:.6g}, {html.escape(title)}={y:.6g} {html.escape(unit)}</title></circle>"
        for x, y in zip(xs, ys, strict=True)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        'role="img" style="background:#fff;border-radius:14px">'
        f"<title>{html.escape(title)}</title>{''.join(grid)}"
        f'<polyline points="{points}" fill="none" stroke="#0f766e" stroke-width="3"/>{dots}'
        f'<text x="{width / 2}" y="28" text-anchor="middle" font-size="19" '
        f'font-family="system-ui" fill="#172033">{html.escape(title)} ({html.escape(unit)})</text>'
        f'<text x="{width / 2}" y="408" text-anchor="middle" font-size="14" '
        f'font-family="system-ui" fill="#526173">{html.escape(axis_label)}</text></svg>'
    )


def write_plots(csv_path: Path, output_dir: Path | None = None) -> list[Path]:
    """Write every available standard metric as SVG and return created paths."""
    rows = load_result_rows(csv_path)
    destination = output_dir or csv_path.parent / "plots"
    destination.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for metric, title, unit in METRICS:
        try:
            svg = render_metric_svg(rows, metric, title, unit)
        except ValueError:
            continue
        path = destination / f"{metric}.svg"
        path.write_text(svg, encoding="utf-8")
        created.append(path)
    if not created:
        raise ValueError("Results CSV has no supported numeric metrics")
    return created


def build_offline_report(run_dir: Path) -> Path:
    """Rebuild a self-contained bilingual HTML report from saved CSV only."""
    csv_path = run_dir / "results.csv"
    rows = load_result_rows(csv_path)
    charts = [path.read_text(encoding="utf-8") for path in write_plots(csv_path)]
    headers = list(rows[0])
    table_head = "".join(f"<th>{html.escape(name)}</th>" for name in headers)
    table_body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(row.get(name, ''))}</td>" for name in headers) + "</tr>"
        for row in rows
    )
    report = run_dir / "report.html"
    # 報告嵌入 SVG 與已 escape 的 CSV；搬移整個 run 時仍可離線開啟。
    report.write_text(
        "<!doctype html><html lang='zh-Hant'><meta charset='utf-8'>"
        "<title>CMP180 離線量測報告 / Offline Measurement Report</title>"
        "<style>body{font:15px system-ui;margin:32px;color:#172033;background:#f4f7fb}"
        "main{max-width:1180px;margin:auto}section{background:#fff;padding:24px;margin:18px 0;"
        "border-radius:16px}svg{width:100%;height:auto}table{border-collapse:collapse;width:100%}"
        "th,td{padding:8px;border-bottom:1px solid #dde4ec;text-align:left;white-space:nowrap}"
        ".table{overflow:auto}</style><main>"
        "<h1>CMP180 離線量測報告</h1><p>由保存的 CSV 產生，不會連線或控制儀器。</p>"
        "<h2>圖表 / Charts</h2>"
        + "".join(f"<section>{chart}</section>" for chart in charts)
        + f"<section class='table'><h2>原始表格 / Saved Data</h2><table><thead><tr>{table_head}"
        f"</tr></thead><tbody>{table_body}</tbody></table></section></main>",
        encoding="utf-8",
    )
    return report
