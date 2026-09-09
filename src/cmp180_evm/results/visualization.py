"""Offline SVG charts and HTML reports for saved CMP180 CSV artifacts."""

from __future__ import annotations

import csv
import html
import math
import os
from pathlib import Path

METRICS = (
    ("evm_all_carriers_db", "EVM All", "dB"),
    ("burst_power_dbm", "Burst Power", "dBm"),
    ("pin_dbm", "PA Pin", "dBm"),
    ("pout_dbm", "PA Pout", "dBm"),
    ("gain_db", "PA Gain", "dB"),
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
            number = float(value)
            if math.isfinite(number):
                return number
        except ValueError:
            continue
    return None


def _row_valid(row: dict[str, object]) -> bool:
    # 舊 CSV 可能沒有 valid；明確 INVALID 或 false 一律排除，保留原始列供追溯。
    flag = str(row.get("valid", "true")).strip().lower()
    return flag in {"true", "1", "1.0"} and str(row.get("limit_status", "")).upper() != "INVALID"


def _axis(rows: list[dict[str, str]]) -> tuple[str, str, float]:
    frequency_values = {_number(row, "frequency_hz") for row in rows}
    power_values = {_number(row, "generator_power_dbm") for row in rows}
    frequency_values.discard(None)
    power_values.discard(None)
    # 同時有頻率與功率時，用有變化的欄位當 X 軸；避免功率掃描被誤畫成單點頻率圖。
    if len(power_values) > len(frequency_values):
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
        (_number(row, axis_field), _number(row, *(aliases.get(metric, (metric,)))))
        if _row_valid(row) else (None, None) for row in rows
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
    width, height, left_pad, right_pad, top_pad, bottom_pad = 1080, 540, 96, 42, 66, 82

    def px(value: float) -> float:
        return left_pad + (value - xmin) / xspan * (width - left_pad - right_pad)

    def py(value: float) -> float:
        return height - bottom_pad - (value - ymin) / (ymax - ymin) * (
            height - top_pad - bottom_pad
        )

    grid = []
    for index in range(6):
        gy = top_pad + index * (height - top_pad - bottom_pad) / 5
        label = ymax - index * (ymax - ymin) / 5
        grid.append(
            f'<line x1="{left_pad}" y1="{gy:.1f}" x2="{width - right_pad}" '
            f'y2="{gy:.1f}" stroke="#dbe4ef"/>'
            '<text x="84" y="{:.1f}" fill="#526173" font-size="13" '
            'text-anchor="end">{:.3g}</text>'.format(gy + 5, label)
        )
    for index in range(6):
        gx = left_pad + index * (width - left_pad - right_pad) / 5
        label = xmin + index * (xmax - xmin) / 5
        grid.append(
            f'<line x1="{gx:.1f}" y1="{top_pad}" x2="{gx:.1f}" '
            f'y2="{height - bottom_pad}" stroke="#dbe4ef" stroke-dasharray="4 6" '
            'opacity=".75"/>'
            f'<text x="{gx:.1f}" y="{height - bottom_pad + 28}" fill="#526173" '
            f'font-size="13" text-anchor="middle">{label:.6g}</text>'
        )
    # 無效點切斷曲線，避免跨過缺失資料造成連續有效的錯覺。
    segments: list[list[str]] = [[]]
    for x, y in samples:
        if x is None or y is None:
            segments.append([])
        else:
            segments[-1].append(f"{px(x * axis_scale):.1f},{py(y):.1f}")
    lines = "".join(
        f'<polyline points="{" ".join(segment)}" fill="none" stroke="#0f766e" stroke-width="3"/>'
        for segment in segments if segment
    )
    dots = "".join(
        f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="5" fill="#0ea5a8">'
        f"<title>x={x:.6g}, {html.escape(title)}={y:.6g} {html.escape(unit)}</title></circle>"
        for x, y in zip(xs, ys, strict=True)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        'role="img" style="background:#ffffff;border-radius:14px">'
        f"<title>{html.escape(title)}</title>{''.join(grid)}"
        f'{lines}{dots}'
        f'<text x="{width / 2}" y="34" text-anchor="middle" font-size="20" '
        f'font-family="system-ui" fill="#172033">{html.escape(title)} ({html.escape(unit)})</text>'
        f'<text x="{width / 2}" y="{height - 18}" text-anchor="middle" font-size="15" '
        f'font-family="system-ui" fill="#526173">{html.escape(axis_label)}</text>'
        f'<text x="24" y="{top_pad + (height - top_pad - bottom_pad) / 2}" '
        f'text-anchor="middle" font-size="15" font-family="system-ui" fill="#526173" '
        f'transform="rotate(-90 24 {top_pad + (height - top_pad - bottom_pad) / 2})">'
        f'{html.escape(title)} ({html.escape(unit)})</text></svg>'
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


def write_pandas_matplotlib_plots(
    csv_path: Path, output_dir: Path | None = None
) -> list[Path]:
    """Create presentation-ready PNG charts using Pandas and Matplotlib."""
    # 實驗室帳號的使用者家目錄可能禁止寫入；把 font cache 留在該 Run 的可寫目錄。
    cache_dir = csv_path.parent / ".matplotlib-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache_dir))
    try:
        import matplotlib
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError(
            "Pandas/Matplotlib reporting requires the project reporting dependencies"
        ) from exc

    # 離線／CI 報告不需要 GUI；固定 Agg 避免 Windows session 或 headless runner 卡住。
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    frame = pd.read_csv(csv_path, encoding="utf-8-sig", na_values=["INV", ""])
    if frame.empty:
        raise ValueError("Results CSV contains no measurement rows")
    destination = output_dir or csv_path.parent / "plots-matplotlib"
    destination.mkdir(parents=True, exist_ok=True)
    frequency_unique = (
        pd.to_numeric(frame["frequency_hz"], errors="coerce").dropna().nunique()
        if "frequency_hz" in frame
        else 0
    )
    power_unique = (
        pd.to_numeric(frame["generator_power_dbm"], errors="coerce").dropna().nunique()
        if "generator_power_dbm" in frame
        else 0
    )
    # 功率掃描會同時保存固定頻率與變動功率；選唯一值較多者作為趨勢 X 軸。
    if power_unique > frequency_unique:
        axis = pd.to_numeric(frame["generator_power_dbm"], errors="coerce")
        axis_label = "Generator Power (dBm)"
    else:
        if "frequency_hz" not in frame:
            raise ValueError("Results CSV has no supported sweep axis")
        # 儀器 artifact 保存 Hz；顯示時轉 MHz，原始 CSV 不被改寫。
        axis = pd.to_numeric(frame["frequency_hz"], errors="coerce") / 1e6
        axis_label = "Frequency (MHz)"

    aliases = {"evm_all_carriers_db": "evm_all_db", "clock_error_ppm": "clock_error"}
    created: list[Path] = []
    for metric, title, unit in METRICS:
        source = metric if metric in frame else aliases.get(metric)
        if source is None or source not in frame:
            continue
        values = pd.to_numeric(frame[source], errors="coerce")
        # 有數值不代表量測有效；用 NaN 切斷 INVALID 點前後的線段。
        validity = frame.apply(lambda row: _row_valid(row.to_dict()), axis=1)
        valid = axis.map(math.isfinite) & values.map(math.isfinite) & validity
        if not valid.any():
            continue
        figure, plot = plt.subplots(
            figsize=(10.8, 5.4),
            constrained_layout=True,
            facecolor="#ffffff",
        )
        plot.set_facecolor("#ffffff")
        plot.plot(axis, values.where(valid), marker="o", linewidth=2.6, color="#0f766e")
        plot.set_title(f"{title} ({unit})")
        plot.set_xlabel(axis_label)
        plot.set_ylabel(f"{title} ({unit})")
        plot.grid(True, color="#dbe4ef", alpha=0.9)
        plot.tick_params(colors="#172033", labelsize=9)
        plot.title.set_color("#172033")
        plot.xaxis.label.set_color("#172033")
        plot.yaxis.label.set_color("#172033")
        for spine in plot.spines.values():
            spine.set_color("#94a3b8")
        path = destination / f"{metric}.png"
        # 白底輸出可在深色 Web 容器與簡報中保持可讀，不依賴瀏覽器背景色。
        figure.savefig(
            path,
            dpi=160,
            facecolor=figure.get_facecolor(),
            metadata={"Software": "CMP180 EVM Automation"},
        )
        plt.close(figure)
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
