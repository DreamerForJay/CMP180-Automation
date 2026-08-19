"""Safety-first orchestration for one WLAN measurement.

The workflow is transport-independent. A future SCPI backend will implement
the protocol only after every write command has been verified on the CMP180.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol, runtime_checkable

from cmp180_evm.utils.exceptions import SafetyGuardError


class MeasurementPhase(StrEnum):
    VALIDATING = "validating"
    CONFIGURING = "configuring"
    RF_ON = "rf_on"
    MEASURING = "measuring"
    FETCHING = "fetching"
    CLEANING_UP = "cleaning_up"
    COMPLETE = "complete"


@dataclass(frozen=True)
class SingleMeasurementPlan:
    generator_port: str
    analyzer_port: str
    center_frequency_hz: float
    bandwidth_hz: float
    generator_power_dbm: float
    expected_nominal_power_dbm: float
    external_attenuation_db: float
    operator_confirmed: bool = False
    maximum_generator_power_dbm: float = -30.0

    def validate_safety(self) -> None:
        if not self.operator_confirmed:
            raise SafetyGuardError("Live RF measurement requires operator confirmation.")
        if self.generator_port == self.analyzer_port:
            raise SafetyGuardError("Generator and analyzer ports must be different.")
        if self.center_frequency_hz <= 0 or self.bandwidth_hz <= 0:
            raise SafetyGuardError("Frequency and bandwidth must be positive.")
        if self.generator_power_dbm > self.maximum_generator_power_dbm:
            raise SafetyGuardError(
                f"Generator power {self.generator_power_dbm} dBm exceeds the "
                f"approved limit {self.maximum_generator_power_dbm} dBm."
            )


@runtime_checkable
class MeasurementBackend(Protocol):
    def configure(self, plan: SingleMeasurementPlan) -> None: ...
    def rf_on(self) -> None: ...
    def initiate_single(self) -> None: ...
    def wait_ready(self) -> None: ...
    def fetch_result(self) -> dict[str, object]: ...
    def stop_measurement(self) -> None: ...
    def rf_off(self) -> None: ...
    def drain_error_queue(self) -> list[str]: ...


@dataclass(frozen=True)
class SingleMeasurementResult:
    values: dict[str, object]
    instrument_errors: list[str]
    phases: tuple[MeasurementPhase, ...]
    cleanup_errors: tuple[str, ...] = field(default_factory=tuple)


def run_single_measurement(
    backend: MeasurementBackend,
    plan: SingleMeasurementPlan,
) -> SingleMeasurementResult:
    """Run one measurement and always attempt stop plus RF off."""
    phases: list[MeasurementPhase] = [MeasurementPhase.VALIDATING]
    cleanup_errors: list[str] = []
    measurement_started = False
    rf_enabled = False
    values: dict[str, object] = {}
    instrument_errors: list[str] = []

    plan.validate_safety()
    try:
        phases.append(MeasurementPhase.CONFIGURING)
        backend.configure(plan)
        rf_enabled = True
        backend.rf_on()
        phases.append(MeasurementPhase.RF_ON)
        measurement_started = True
        backend.initiate_single()
        phases.append(MeasurementPhase.MEASURING)
        backend.wait_ready()
        phases.append(MeasurementPhase.FETCHING)
        values = backend.fetch_result()
        instrument_errors = backend.drain_error_queue()
    finally:
        phases.append(MeasurementPhase.CLEANING_UP)
        if measurement_started:
            try:
                backend.stop_measurement()
            except Exception as exc:  # cleanup must continue to RF off
                cleanup_errors.append(f"stop_measurement: {type(exc).__name__}: {exc}")
        if rf_enabled:
            try:
                backend.rf_off()
            except Exception as exc:
                cleanup_errors.append(f"rf_off: {type(exc).__name__}: {exc}")

    phases.append(MeasurementPhase.COMPLETE)
    return SingleMeasurementResult(
        values=values,
        instrument_errors=instrument_errors,
        phases=tuple(phases),
        cleanup_errors=tuple(cleanup_errors),
    )
