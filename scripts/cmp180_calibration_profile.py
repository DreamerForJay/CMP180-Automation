"""Create a review-only CMP180 path-loss calibration profile from CSV readings."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import yaml

from cmp180_evm.calibration_workflow import build_draft_profile, load_calibration_readings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readings", type=Path, help="CSV containing reference-plane readings")
    parser.add_argument("--output", type=Path, required=True, help="Draft YAML output path")
    parser.add_argument("--profile-id", required=True)
    parser.add_argument("--revision", default="0.1-draft")
    parser.add_argument("--route", required=True)
    parser.add_argument("--calibrated-at", type=date.fromisoformat, required=True)
    parser.add_argument("--expires-at", type=date.fromisoformat, required=True)
    parser.add_argument("--equipment-reference", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    profile = build_draft_profile(
        load_calibration_readings(args.readings),
        profile_id=args.profile_id,
        revision=args.revision,
        route=args.route,
        calibrated_at=args.calibrated_at,
        expires_at=args.expires_at,
        equipment_reference=args.equipment_reference,
    )
    # 腳本永遠輸出 draft；核准必須經 RF/test owner 審查，不由量測程式自行升級。
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(profile.snapshot(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Draft calibration profile: {args.output}")
    print("Measurement use: BLOCKED until RF/test-owner approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

