"""Typed configuration models (SPEC.MD section 8).

These mirror configs/instrument.example.yaml and configs/wlan_baseline.example.yaml
field-for-field. Field-level constraints (types, required-ness) are enforced by
pydantic here; cross-field domain rules (e.g. band vs. frequency consistency,
"generator port must be confirmed before RF ON") live in config/validators.py
instead, since they need more context than a single field can express.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ResourceConfig(BaseModel):
    type: Literal["rsinstrument"] = "rsinstrument"
    address: str
    options: str = "SelectVisa='socketio'"


class ConnectionConfig(BaseModel):
    timeout_ms: int = 10000
    opc_timeout_ms: int = 30000
    query_delay_ms: int = 0
    retry_count: int = 3
    retry_interval_ms: int = 1000


class IdentityConfig(BaseModel):
    expected_manufacturer: str = "Rohde&Schwarz"
    expected_model_contains: str = "CMP180"


class SessionConfig(BaseModel):
    reset_on_connect: bool = False
    clear_status_on_connect: bool = True
    check_error_after_write: bool = True
    close_on_finish: bool = True


class InstrumentLoggingConfig(BaseModel):
    scpi_enabled: bool = True
    scpi_log_file: str = "logs/scpi.log"
    mask_sensitive_data: bool = True


class InstrumentSettings(BaseModel):
    name: str
    resource: ResourceConfig
    connection: ConnectionConfig = ConnectionConfig()
    identity: IdentityConfig = IdentityConfig()
    session: SessionConfig = SessionConfig()
    logging: InstrumentLoggingConfig = InstrumentLoggingConfig()


class RoutingConfig(BaseModel):
    generator_port: str
    analyzer_port: str
    generator_port_confirmed: bool = False
    analyzer_port_confirmed: bool = False
    path_description: str | None = None
    external_attenuation_db: float = 0.0
    require_manual_confirmation_before_rf_on: bool = True


class InstrumentConfig(BaseModel):
    """Top-level model for configs/instrument.yaml (instrument + routing sections)."""

    instrument: InstrumentSettings
    routing: RoutingConfig


class TestInfo(BaseModel):
    id: str
    description: str | None = None


class SignalConfig(BaseModel):
    standard: str
    burst_type: str | None = None

    band: str
    center_frequency_hz: float

    bandwidth_hz: float | None = None
    channel: int | None = None

    mcs_index: int | None = None
    modulation: str | None = None

    spatial_streams: int | None = None
    space_time_streams: int | None = None

    guard_interval_us: float | None = None
    ltf_size: str | None = None
    coding: str | None = None
    payload_length_bytes: int | None = None


class GeneratorSignalConfig(BaseModel):
    """GPRF Gen 1 in this project plays a pre-built ARB waveform file rather than
    generating WLAN parameters live via SCPI (confirmed from the CMsquares GUI:
    Baseband Mode = ARB). `arb_waveform_file` is the actual signal source of
    truth — the `signal.*` fields above should match what's encoded in its
    filename, not the other way around."""

    enabled: bool = True
    output_power_dbm: float
    rf_on_at_start: bool = False
    arb_waveform_file: str | None = None


class AnalyzerTriggerConfig(BaseModel):
    source: str = "IF Power"
    threshold_db: float = -30.0
    offset_us: float = 0.0
    min_gap_us: float = 5.0
    slope: str = "RisingEdge"
    timeout_ms: float = 1000.0


class AnalyzerConfig(BaseModel):
    expected_nominal_power_dbm: float
    external_attenuation_db: float = 0.0
    user_margin_db: float = 3.0
    modulation_filter: str = "ALL"
    iq_swap: bool = False
    trigger: AnalyzerTriggerConfig = AnalyzerTriggerConfig()


class MeasurementConfig(BaseModel):
    mode: str = "multi_evaluation"
    burst_count: int = 20
    timeout_s: float = 30
    clear_statistics_before_run: bool = True
    adjust_level_before_run: bool = True
    # "continuous" is what the CMsquares GUI baseline currently uses for live
    # monitoring; automated single-point measurements should use "single" (run
    # exactly `burst_count` bursts, then stop) — confirm the right Repetition/
    # Stop Condition combination during SCPI discovery before relying on this.
    repetition: str = "single"


class OutputConfig(BaseModel):
    save_csv: bool = True
    save_json: bool = True
    save_screenshots: bool = False
    generate_plots: bool = True
    generate_html_report: bool = True


class WlanBaselineConfig(BaseModel):
    """Top-level model for configs/wlan_baseline.yaml."""

    test: TestInfo
    signal: SignalConfig
    generator: GeneratorSignalConfig
    analyzer: AnalyzerConfig
    measurement: MeasurementConfig = MeasurementConfig()
    output: OutputConfig = OutputConfig()


class SafetyConfig(BaseModel):
    generator_power_min_dbm: float = -60.0
    generator_power_max_dbm: float = -10.0
    analyzer_input_soft_limit_dbm: float = -5.0
    require_port_confirmation: bool = True
    require_attenuation_confirmation: bool = True
    force_rf_off_on_exception: bool = True


class BandRule(BaseModel):
    min_hz: float
    max_hz: float


class BandRulesConfig(BaseModel):
    """Provisional band frequency ranges (SPEC.MD section 19).

    These IEEE-standard 2.4/5/6 GHz splits are broad industry conventions, not
    a CMP180-specific fact — treat as provisional until confirmed by a mentor
    or internal spec before relying on them for a real pass/fail decision.
    """

    bands: dict[str, BandRule] = Field(
        default_factory=lambda: {
            "2_4_GHZ": BandRule(min_hz=2_400_000_000, max_hz=2_500_000_000),
            "5_GHZ": BandRule(min_hz=5_000_000_000, max_hz=5_925_000_000),
            "6_GHZ": BandRule(min_hz=5_925_000_000, max_hz=7_125_000_000),
        }
    )
