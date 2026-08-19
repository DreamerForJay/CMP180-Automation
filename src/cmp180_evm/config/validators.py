"""Cross-field domain validation that a single pydantic model can't express on its own."""

from cmp180_evm.config.models import BandRulesConfig, RoutingConfig, SafetyConfig
from cmp180_evm.utils.exceptions import ConfigValidationError, SafetyGuardError


def validate_band_frequency(
    band: str,
    frequency_hz: float,
    band_rules: BandRulesConfig | None = None,
) -> None:
    """Reject the "Band = 5 GHz, Frequency = 6105 MHz" kind of mismatch seen in
    the CMsquares GUI (SPEC.MD section 19) before it reaches the instrument."""
    band_rules = band_rules or BandRulesConfig()
    rule = band_rules.bands.get(band)
    if rule is None:
        raise ConfigValidationError(
            f"Unknown band '{band}'. Known bands: {sorted(band_rules.bands)}"
        )
    if not (rule.min_hz <= frequency_hz <= rule.max_hz):
        suggested = next(
            (
                name
                for name, r in band_rules.bands.items()
                if r.min_hz <= frequency_hz <= r.max_hz
            ),
            None,
        )
        message = (
            f"Configuration error: {frequency_hz / 1e6:.0f} MHz does not match selected band {band}."
        )
        if suggested:
            message += f" Suggested band: {suggested}."
        raise ConfigValidationError(message)


def validate_generator_power(power_dbm: float, safety: SafetyConfig | None = None) -> None:
    safety = safety or SafetyConfig()
    if not (safety.generator_power_min_dbm <= power_dbm <= safety.generator_power_max_dbm):
        raise SafetyGuardError(
            f"Generator power {power_dbm} dBm is outside the configured safe range "
            f"[{safety.generator_power_min_dbm}, {safety.generator_power_max_dbm}] dBm."
        )


def validate_rf_on_preconditions(routing: RoutingConfig, safety: SafetyConfig | None = None) -> None:
    """RF ON pre-flight checks (SPEC.MD section 16.1). Must pass before any RF-enabling
    SCPI write is issued — callers are expected to invoke this and let the
    SafetyGuardError propagate rather than catching it and continuing."""
    safety = safety or SafetyConfig()

    if safety.require_port_confirmation and not routing.generator_port_confirmed:
        raise SafetyGuardError(
            f"Generator port '{routing.generator_port}' is not confirmed "
            "(routing.generator_port_confirmed=false). Confirm it via SCPI discovery "
            "before enabling RF."
        )
    if safety.require_port_confirmation and not routing.analyzer_port_confirmed:
        raise SafetyGuardError(
            f"Analyzer port '{routing.analyzer_port}' is not confirmed "
            "(routing.analyzer_port_confirmed=false). Confirm it before enabling RF."
        )
    if safety.require_attenuation_confirmation and routing.external_attenuation_db is None:
        raise SafetyGuardError("External attenuation is not set (routing.external_attenuation_db).")
