"""Generate offline SVG charts from a saved CMP180 results.csv."""

from __future__ import annotations

import argparse
from pathlib import Path

from cmp180_evm.results.visualization import write_pandas_matplotlib_plots, write_plots


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--engine",
        choices=("svg", "pandas-matplotlib", "both"),
        default="svg",
        help="Keep the dependency-free SVG path or create Pandas/Matplotlib PNG charts.",
    )
    args = parser.parse_args()
    paths: list[Path] = []
    if args.engine in {"svg", "both"}:
        paths.extend(write_plots(args.csv_path, args.output_dir))
    if args.engine in {"pandas-matplotlib", "both"}:
        paths.extend(write_pandas_matplotlib_plots(args.csv_path, args.output_dir))
    for path in paths:
        print(path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
