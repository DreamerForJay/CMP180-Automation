"""Generate offline SVG charts from a saved CMP180 results.csv."""

from __future__ import annotations

import argparse
from pathlib import Path

from cmp180_evm.results.visualization import write_plots


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    for path in write_plots(args.csv_path, args.output_dir):
        print(path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
