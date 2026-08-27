"""Rebuild a self-contained offline report from a saved CMP180 run directory."""

from __future__ import annotations

import argparse
from pathlib import Path

from cmp180_evm.results.visualization import build_offline_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    print(build_offline_report(args.run_dir).resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
