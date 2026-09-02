"""Build the offline CMP180 V1 acceptance readiness report."""

from __future__ import annotations

import argparse
from pathlib import Path

from cmp180_evm.acceptance import build_v1_acceptance_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--calibration", type=Path, default=Path("configs/calibration.example.yaml")
    )
    parser.add_argument("--limits", type=Path, default=Path("configs/limits.example.yaml"))
    parser.add_argument("--evidence", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, default=Path("output/v1-acceptance"))
    args = parser.parse_args()
    html_path, json_path = build_v1_acceptance_report(
        args.calibration, args.limits, tuple(args.evidence), args.output
    )
    print(html_path.resolve())
    print(json_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
