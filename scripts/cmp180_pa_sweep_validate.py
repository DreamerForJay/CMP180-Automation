"""Run an approved CMP180 GPRF PA power-sweep profile."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cmp180_evm.pa_sweep_profile import load_pa_sweep_profile
from cmp180_evm.web.gprf_service import build_gprf_power_preview, run_gprf_power_sweep
from cmp180_evm.web.jobs import SweepJob


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=Path("configs/pa_sweep.example.yaml"))
    parser.add_argument("--dut-id", required=True)
    parser.add_argument("--output-root", type=Path, default=Path("output"))
    parser.add_argument("--expected-dut-gain-db", type=float)
    parser.add_argument("--output-attenuator-db", type=float, default=0.0)
    parser.add_argument("--input-cable-loss-db", type=float)
    parser.add_argument("--output-cable-loss-db", type=float)
    parser.add_argument("--confirm-direct-cable", action="store_true")
    parser.add_argument("--confirm-operator-present", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not (args.confirm_direct_cable and args.confirm_operator_present):
        print("Refusing PA sweep without cable and operator confirmations.", file=sys.stderr)
        return 2

    profile = load_pa_sweep_profile(args.profile)
    request = profile.measurement_request(
        dut_id=args.dut_id,
        expected_dut_gain_db=args.expected_dut_gain_db,
        output_attenuator_db=args.output_attenuator_db,
        input_cable_loss_db=args.input_cable_loss_db,
        output_cable_loss_db=args.output_cable_loss_db,
    )
    request.update(
        {
            "operator_present": True,
            "direct_cable_no_attenuator": False,
            "gprf_confirmation": "GPRF-POWER-NOT-WLAN-EVM",
        }
    )
    preview = build_gprf_power_preview(request)
    # Preview 是最後一道軟體 gate；真正 RF 仍在 run_gprf_power_sweep 逐點收尾。
    print(f"Profile: {profile.profile_id} rev {profile.revision}")
    print(f"DUT: {args.dut_id}")
    print(f"Points: {len(preview.points)}")
    print(f"Requested profile stop: {request['profile_stop_dbm']:g} dBm")
    print(f"Effective safe stop: {request['stop_dbm']:g} dBm")
    print(f"Safe stop clipped: {request['safe_stop_clipped']}")
    print(f"Expected DUT gain: {request['expected_dut_gain_db']:g} dB")
    print(f"Output attenuator: {request['output_attenuator_db']:g} dB")
    print(f"Worst-case RF1.5 input: {request['worst_case_rf_input_dbm']:g} dBm")
    print(f"SA safe limit: {profile.sa_safe_limit_dbm:g} dBm")
    job = SweepJob("pa-sweep-cli", "hardware-pa-power-sweep", len(preview.points))
    result = run_gprf_power_sweep(job, request=request, output_root=args.output_root)
    print(f"Completed points: {len(result['points'])}/{len(preview.points)}")
    print(f"P1dB: {json.dumps(result['p1db'])}")
    print(f"Partial: {result.get('partial')}")
    print(f"Stopped reason: {result.get('stopped_reason')}")
    print(f"Artifacts: {json.dumps(result['artifacts'])}")
    print(f"Cleanup errors: {json.dumps(result['cleanup_errors'])}")
    return 3 if result.get("partial") else 0


if __name__ == "__main__":
    raise SystemExit(main())
