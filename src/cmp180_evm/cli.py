import argparse
import sys
from pathlib import Path

from cmp180_evm import actions


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cmp180_evm")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_config = subparsers.add_parser(
        "validate-config", help="Validate a config YAML file (instrument or WLAN baseline)."
    )
    validate_config.add_argument("config", help="Path to the YAML config file.")
    validate_config.set_defaults(func=_cmd_validate_config)

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
