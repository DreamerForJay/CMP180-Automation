"""Safe adapter contract for external path-loss calibration instruments."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Protocol

from cmp180_evm.calibration_workflow import CalibrationReading

CALIBRATION_MINIMUM_FREQUENCY_HZ = 5_925_000_000.0
CALIBRATION_MAXIMUM_FREQUENCY_HZ = 7_125_000_000.0
CALIBRATION_MAXIMUM_POINTS = 11
CALIBRATION_MINIMUM_SOURCE_POWER_DBM = -80.0
CALIBRATION_MAXIMUM_SOURCE_POWER_DBM = -40.0


class CalibrationInstrumentAdapter(Protocol):
    adapter_id: str
    simulated: bool

    def connect(self) -> None: ...

    def identify(self) -> str: ...

    def measure(self, frequency_hz: float, source_power_dbm: float) -> float: ...

    def output_off(self) -> None: ...

    def close(self) -> None: ...


@dataclass(frozen=True)
class AdapterDescriptor:
    adapter_id: str
    label: str
    simulated: bool
    available: bool
    reason: str


@dataclass(frozen=True)
class CalibrationCaptureResult:
    adapter_id: str
    identity: str
    simulated: bool
    readings: tuple[CalibrationReading, ...]
    final_output_state: str

    def public(self) -> dict[str, object]:
        return {
            "adapter_id": self.adapter_id,
            "identity": self.identity,
            "simulated": self.simulated,
            "readings": [asdict(reading) for reading in self.readings],
            "final_output_state": self.final_output_state,
        }


class MockReferenceAdapter:
    """Deterministic software adapter for UI and cleanup acceptance only."""

    adapter_id = "mock-reference"
    simulated = True

    def __init__(self) -> None:
        self.connected = False
        self.output_enabled = False

    def connect(self) -> None:
        self.connected = True

    def identify(self) -> str:
        if not self.connected:
            raise RuntimeError("Adapter is not connected")
        return "SIMULATED,REFERENCE-ADAPTER,NO-HARDWARE"

    def measure(self, frequency_hz: float, source_power_dbm: float) -> float:
        if not self.connected:
            raise RuntimeError("Adapter is not connected")
        self.output_enabled = True
        # 僅產生可重現的示範 loss；不得用於正式校正或 compliance。
        loss_db = 0.8 + (frequency_hz - 6_085_000_000) / 1_000_000_000
        return round(source_power_dbm - loss_db, 6)

    def output_off(self) -> None:
        self.output_enabled = False

    def close(self) -> None:
        self.connected = False


def list_calibration_adapters() -> tuple[AdapterDescriptor, ...]:
    return (
        AdapterDescriptor(
            "mock-reference",
            "Simulation reference adapter",
            True,
            True,
            "Software-only validation; no instrument or RF",
        ),
        AdapterDescriptor(
            "external-scpi",
            "External SCPI calibration instrument",
            False,
            False,
            "Model, resource address, official SCPI, and safety limits are not configured",
        ),
    )


def create_calibration_adapter(adapter_id: str) -> CalibrationInstrumentAdapter:
    if adapter_id == "mock-reference":
        return MockReferenceAdapter()
    raise ValueError(f"Calibration adapter {adapter_id!r} is unavailable")


def capture_calibration_readings(
    adapter: CalibrationInstrumentAdapter,
    frequencies_hz: tuple[float, ...],
    source_power_dbm: float,
) -> CalibrationCaptureResult:
    if not 2 <= len(frequencies_hz) <= CALIBRATION_MAXIMUM_POINTS:
        raise ValueError("Calibration capture requires 2..11 frequency points")
    if tuple(sorted(set(frequencies_hz))) != frequencies_hz:
        raise ValueError("Calibration frequencies must be unique and strictly increasing")
    if not all(
        CALIBRATION_MINIMUM_FREQUENCY_HZ
        <= frequency_hz
        <= CALIBRATION_MAXIMUM_FREQUENCY_HZ
        for frequency_hz in frequencies_hz
    ):
        raise ValueError("Calibration frequencies exceed the approved 6 GHz range")
    if not (
        CALIBRATION_MINIMUM_SOURCE_POWER_DBM
        <= source_power_dbm
        <= CALIBRATION_MAXIMUM_SOURCE_POWER_DBM
    ):
        raise ValueError("Calibration source power must stay within -80..-40 dBm")

    identity = "UNKNOWN"
    readings: list[CalibrationReading] = []
    adapter.connect()
    try:
        identity = adapter.identify()
        for frequency_hz in frequencies_hz:
            receiver_dbm = adapter.measure(frequency_hz, source_power_dbm)
            readings.append(CalibrationReading(frequency_hz, source_power_dbm, receiver_dbm))
    finally:
        # 真實 adapter 即使量測、逾時或取消失敗，也必須先關輸出再關 session。
        try:
            adapter.output_off()
        finally:
            adapter.close()
    return CalibrationCaptureResult(
        adapter.adapter_id,
        identity,
        adapter.simulated,
        tuple(readings),
        "OFF",
    )
