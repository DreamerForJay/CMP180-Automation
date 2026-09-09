"""High-level actions used by the CLI (cli.py).

Kept separate from cli.py so it stays a thin presentation layer over these
functions, and so the config-validation/dry-run/connection-test logic stays
usable from other front ends (e.g. the Web GUI) without duplicating it.
"""

from dataclasses import dataclass, field
from pathlib import Path

from cmp180_evm.config.loader import (
    detect_config_kind,
    load_instrument_config,
    load_wlan_baseline_config,
)
from cmp180_evm.config.models import InstrumentConfig, WlanBaselineConfig
from cmp180_evm.config.validators import validate_band_frequency
from cmp180_evm.instrument.mock_cmp180 import MockCmp180
from cmp180_evm.instrument.session import Cmp180Session
from cmp180_evm.scpi import common
from cmp180_evm.utils.exceptions import Cmp180Error
from cmp180_evm.utils.retry import RetryPolicy, run_with_bounded_retry


@dataclass
class ValidationResult:
    ok: bool
    kind: str | None = None
    messages: list[str] = field(default_factory=list)


def validate_config(path: Path) -> ValidationResult:
    """Load a YAML config and run both pydantic field validation and the
    cross-field domain checks that pydantic alone can't express."""
    try:
        kind = detect_config_kind(path)
    except (FileNotFoundError, ValueError) as exc:
        return ValidationResult(ok=False, messages=[str(exc)])

    try:
        if kind == "instrument":
            config = load_instrument_config(path)
            messages = _describe_instrument_config(config)
        else:
            config = load_wlan_baseline_config(path)
            messages = _describe_wlan_baseline_config(config)
            validate_band_frequency(config.signal.band, config.signal.center_frequency_hz)
    except Cmp180Error as exc:
        return ValidationResult(ok=False, kind=kind, messages=[str(exc)])
    except Exception as exc:  # pydantic ValidationError and friends
        return ValidationResult(ok=False, kind=kind, messages=[str(exc)])

    return ValidationResult(ok=True, kind=kind, messages=messages)


def _describe_instrument_config(config: InstrumentConfig) -> list[str]:
    """Human-readable "Label: value" lines, in this exact format so front
    ends (CLI text, GUI summary table) can split on the first ": " to render
    a label/value pair without guessing at Python attribute names."""
    return [
        f"Instrument name: {config.instrument.name}",
        f"Resource address: {config.instrument.resource.address}",
        f"Generator port: {config.routing.generator_port} "
        f"({'confirmed' if config.routing.generator_port_confirmed else 'NOT CONFIRMED'})",
        f"Analyzer port: {config.routing.analyzer_port} "
        f"({'confirmed' if config.routing.analyzer_port_confirmed else 'NOT CONFIRMED'})",
    ]


def _describe_wlan_baseline_config(config: WlanBaselineConfig) -> list[str]:
    return [
        f"Test ID: {config.test.id}",
        f"Band: {config.signal.band}",
        f"Center frequency: {config.signal.center_frequency_hz / 1e6:.1f} MHz",
        f"Generator output power: {config.generator.output_power_dbm} dBm",
        f"Analyzer expected power: {config.analyzer.expected_nominal_power_dbm} dBm",
        f"Burst count: {config.measurement.burst_count}",
    ]


def dry_run_steps(instrument_config_path: Path, wlan_config_path: Path) -> list[str]:
    """Describe what a real run would do, without sending any SCPI writes
    (SPEC.MD section 25)."""
    instrument = load_instrument_config(instrument_config_path)
    baseline = load_wlan_baseline_config(wlan_config_path)

    steps = [
        "[DRY RUN] no SCPI commands will be sent",
        f"Connect to {instrument.instrument.resource.address}",
        f"Confirm generator port {instrument.routing.generator_port} "
        f"(confirmed={instrument.routing.generator_port_confirmed})",
        f"Confirm analyzer port {instrument.routing.analyzer_port} "
        f"(confirmed={instrument.routing.analyzer_port_confirmed})",
        f"Set frequency {baseline.signal.center_frequency_hz / 1e6:.1f} MHz",
        f"Set generator power {baseline.generator.output_power_dbm} dBm",
        f"Set analyzer expected power {baseline.analyzer.expected_nominal_power_dbm} dBm",
    ]
    if baseline.measurement.adjust_level_before_run:
        steps.append("Adjust level")
    if baseline.measurement.clear_statistics_before_run:
        steps.append("Clear statistics")
    steps.append(f"Measure {baseline.measurement.burst_count} bursts")
    steps.append("Query EVM / Burst Power / Frequency Error")
    if baseline.output.save_csv or baseline.output.save_json:
        steps.append("Save output (CSV/JSON)")
    if baseline.output.generate_plots:
        steps.append("Generate plots")
    if baseline.output.generate_html_report:
        steps.append("Generate HTML report")
    steps.append("RF OFF")
    return steps


@dataclass
class ConnectionResult:
    ok: bool
    idn: str | None = None
    options: str | None = None
    errors: list[str] = field(default_factory=list)
    message: str = ""


def test_connection(instrument_config_path: Path, use_mock: bool) -> ConnectionResult:
    """Connect, verify *IDN?, read *OPT?, drain the error queue, disconnect.

    Mirrors SPEC.MD section 12.2. Never sends any WLAN/generator command —
    only the fixed IEEE-488.2 common commands.
    """
    config = load_instrument_config(instrument_config_path)

    session: Cmp180Session | MockCmp180
    if use_mock:
        session = MockCmp180()
    else:
        session = Cmp180Session(
            resource_address=config.instrument.resource.address,
            options=config.instrument.resource.options,
            timeout_ms=config.instrument.connection.timeout_ms,
            opc_timeout_ms=config.instrument.connection.opc_timeout_ms,
            query_delay_ms=config.instrument.connection.query_delay_ms,
            clear_status_on_connect=config.instrument.session.clear_status_on_connect,
            check_error_after_write=config.instrument.session.check_error_after_write,
            mask_sensitive_data=config.instrument.logging.mask_sensitive_data,
        )

    def attempt_connection(attempt: int) -> ConnectionResult:
        session.connect()
        idn = session.verify_identity(config.instrument.identity.expected_model_contains)
        options = session.query(common.OPTIONS)
        errors = session.drain_error_queue()
        return ConnectionResult(
            ok=True,
            idn=idn,
            options=options,
            errors=errors,
            message=(
                "Connected successfully"
                + (" (mock)" if use_mock else "")
                + (f" after {attempt} attempts" if attempt > 1 else "")
            ),
        )

    def cleanup_failed_attempt(attempt: int, exc: BaseException) -> None:
        del attempt, exc
        # 連線診斷不送 RF；重試前仍關閉可能半開的 session，避免資源鎖殘留。
        session.disconnect()

    try:
        policy = RetryPolicy(
            retry_count=0 if use_mock else config.instrument.connection.retry_count,
            retry_interval_ms=config.instrument.connection.retry_interval_ms,
        )
        return run_with_bounded_retry(
            attempt_connection,
            policy=policy,
            cleanup=cleanup_failed_attempt,
        )
    except Cmp180Error as exc:
        return ConnectionResult(ok=False, message=str(exc))
    except Exception as exc:
        return ConnectionResult(ok=False, message=f"Connection failed: {exc}")
    finally:
        try:
            session.disconnect()
        except Exception:
            pass
