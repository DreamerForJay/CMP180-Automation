import argparse
import sys
from pathlib import Path

from cmp180_evm import actions
from cmp180_evm.calibration import load_calibration_profile
from cmp180_evm.limits import load_limit_profile
from cmp180_evm.pa_sweep_profile import load_pa_sweep_profile


def _cmd_validate_config(args: argparse.Namespace) -> int:
    result = actions.validate_config(Path(args.config))
    if result.ok:
        print(f"OK ({result.kind})")
        for message in result.messages:
            print(f"  {message}")
        return 0

    print("INVALID")
    for message in result.messages:
        print(f"  {message}")
    return 1


def _cmd_dry_run(args: argparse.Namespace) -> int:
    steps = actions.dry_run_steps(Path(args.instrument_config), Path(args.config))
    for step in steps:
        print(step)
    return 0


def _cmd_test_connection(args: argparse.Namespace) -> int:
    result = actions.test_connection(Path(args.instrument_config), use_mock=args.mock)
    if not result.ok:
        print(f"FAILED: {result.message}")
        return 1

    print(result.message)
    print(f"  IDN: {result.idn}")
    print(f"  OPT: {result.options}")
    if result.errors:
        print(f"  Errors in queue: {result.errors}")
    else:
        print("  Error queue: empty")
    return 0


def _cmd_validate_calibration(args: argparse.Namespace) -> int:
    try:
        profile = load_calibration_profile(Path(args.config))
    except (OSError, TypeError, ValueError) as exc:
        print(f"INVALID: {exc}")
        return 1
    print("OK (calibration)")
    print(f"  Profile: {profile.profile_id} rev {profile.revision}")
    print(f"  Lifecycle: {profile.lifecycle}")
    print(f"  Route: {profile.route}")
    print(f"  Range: {profile.points[0].frequency_hz:g}..{profile.points[-1].frequency_hz:g} Hz")
    print(f"  Expires: {profile.expires_at.isoformat()}")
    if profile.lifecycle != "approved":
        print("  Measurement use: BLOCKED (profile is not approved)")
    elif profile.is_expired():
        print("  Measurement use: BLOCKED (profile is expired)")
    else:
        print("  Measurement use: ALLOWED")
    return 0


def _cmd_validate_limits(args: argparse.Namespace) -> int:
    try:
        profile = load_limit_profile(Path(args.config))
    except (OSError, TypeError, ValueError) as exc:
        print(f"INVALID: {exc}")
        return 1
    print("OK (limits)")
    print(f"  Profile: {profile.profile_id} rev {profile.revision}")
    print(f"  Lifecycle: {profile.lifecycle}")
    # Draft 門檻只可做流程預覽；正式 PASS/FAIL 必須有來源與核准欄位。
    print(f"  Compliance use: {'ALLOWED' if profile.lifecycle == 'approved' else 'BLOCKED'}")
    return 0


def _cmd_validate_pa_sweep(args: argparse.Namespace) -> int:
    try:
        profile = load_pa_sweep_profile(Path(args.config))
    except (OSError, TypeError, ValueError) as exc:
        print(f"INVALID: {exc}")
        return 1
    print("OK (pa_sweep)")
    print(f"  Profile: {profile.profile_id} rev {profile.revision}")
    print(f"  Route: {profile.route}")
    print(f"  Frequency: {profile.frequency_hz:g} Hz")
    print(f"  Power: {profile.start_dbm:g}..{profile.stop_dbm:g} dBm step {profile.step_db:g} dB")
    request = profile.measurement_request()
    print(f"  Default fixture output attenuator: {profile.output_attenuator_db:g} dB")
    print(f"  Default effective stop: {request['stop_dbm']:g} dBm")
    print(f"  Measurement EATT: {profile.measurement_external_attenuation_db:g} dB")
    # 最壞 RF1.5 power 是硬體保護判斷，不是離線 Pout 或 DUT 規格宣稱。
    print(f"  Worst-case RF1.5 input: {request['worst_case_rf_input_dbm']:g} dBm")
    print(f"  SA safe limit: {profile.sa_safe_limit_dbm:g} dBm")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cmp180_evm")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_config = subparsers.add_parser(
        "validate-config", help="Validate a config YAML file (instrument or WLAN baseline)."
    )
    validate_config.add_argument("config", help="Path to the YAML config file.")
    validate_config.set_defaults(func=_cmd_validate_config)

    validate_calibration = subparsers.add_parser(
        "validate-calibration", help="Validate a path-loss calibration profile."
    )
    validate_calibration.add_argument("config", help="Path to the calibration YAML file.")
    validate_calibration.set_defaults(func=_cmd_validate_calibration)

    validate_limits = subparsers.add_parser(
        "validate-limits", help="Validate an EVM result-limit profile."
    )
    validate_limits.add_argument("config", help="Path to the limit-profile YAML file.")
    validate_limits.set_defaults(func=_cmd_validate_limits)

    validate_pa_sweep = subparsers.add_parser(
        "validate-pa-sweep", help="Validate an approved PA power-sweep profile."
    )
    validate_pa_sweep.add_argument("config", help="Path to the PA sweep YAML file.")
    validate_pa_sweep.set_defaults(func=_cmd_validate_pa_sweep)

    dry_run = subparsers.add_parser(
        "dry-run", help="Print the planned steps for a run without sending any SCPI writes."
    )
    dry_run.add_argument("--config", required=True, help="Path to the WLAN baseline/sweep config.")
    dry_run.add_argument(
        "--instrument-config",
        default="configs/instrument.example.yaml",
        help="Path to the instrument/routing config.",
    )
    dry_run.set_defaults(func=_cmd_dry_run)

    test_connection = subparsers.add_parser(
        "test-connection", help="Connect to the instrument and verify *IDN?/*OPT?."
    )
    test_connection.add_argument(
        "--instrument-config",
        default="configs/instrument.example.yaml",
        help="Path to the instrument/routing config.",
    )
    test_connection.add_argument(
        "--mock", action="store_true", help="Use the mock instrument instead of a real connection."
    )
    test_connection.set_defaults(func=_cmd_test_connection)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
