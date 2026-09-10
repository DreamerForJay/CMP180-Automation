"""Canonical constellation data model and hardware-neutral I/Q parsing."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from enum import StrEnum


class SourceKind(StrEnum):
    MOCK = "mock"
    STORED = "stored"
    HARDWARE = "hardware"


class HilStatus(StrEnum):
    NOT_RUN = "NOT_RUN"
    HIL_PENDING = "HIL_PENDING"
    VERIFIED = "VERIFIED"


@dataclass(frozen=True)
class IQSample:
    symbol_index: int
    i: float | None
    q: float | None
    valid: bool


@dataclass(frozen=True)
class ConstellationPoint:
    symbol_index: int
    i: float | None
    q: float | None
    ideal_i: float | None
    ideal_q: float | None
    evm: float | None
    valid: bool
    normalized_i: float | None = None
    normalized_q: float | None = None
    stream_index: int = 0
    subcarrier_index: int | None = None
    symbol_type: str = "data"


@dataclass(frozen=True)
class ConstellationMetadata:
    modulation: str
    sample_count: int
    valid_count: int
    source: SourceKind
    simulated: bool
    hil_status: HilStatus
    normalization: str = "unit-average-symbol-power"
    impairments: dict[str, float] = field(default_factory=dict)
    provenance: tuple[str, ...] = ("DERIVED",)


@dataclass(frozen=True)
class ConstellationDataset:
    metadata: ConstellationMetadata
    points: tuple[ConstellationPoint, ...]
    ideal_points: tuple[tuple[float, float], ...]
    analysis: dict[str, object]

    def public(self) -> dict[str, object]:
        return {
            "metadata": {
                **asdict(self.metadata),
                "source": self.metadata.source.value,
                "hil_status": self.metadata.hil_status.value,
            },
            "points": [asdict(point) for point in self.points],
            "ideal_points": [
                {"i": ideal_i, "q": ideal_q} for ideal_i, ideal_q in self.ideal_points
            ],
            "analysis": self.analysis,
        }


def _finite_number(value: object) -> float | None:
    if not isinstance(value, (str, bytes, bytearray, int, float)):
        raise ValueError(f"Malformed numeric I/Q value: {value!r}")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Malformed numeric I/Q value: {value!r}") from exc
    # NaN／Inf 代表原始點無效；保留 invalid，不可悄悄改成 0。
    return number if math.isfinite(number) else None


def parse_interleaved_iq(values: Iterable[object]) -> tuple[IQSample, ...]:
    """Parse known interleaved I0,Q0,I1,Q1 input without assuming CMP180 format."""
    raw = list(values)
    if not raw:
        raise ValueError("Interleaved I/Q input is empty")
    if len(raw) % 2:
        raise ValueError("Interleaved I/Q input must contain an even number of values")
    samples: list[IQSample] = []
    for index in range(0, len(raw), 2):
        i_value = _finite_number(raw[index])
        q_value = _finite_number(raw[index + 1])
        samples.append(
            IQSample(
                symbol_index=index // 2,
                i=i_value,
                q=q_value,
                valid=i_value is not None and q_value is not None,
            )
        )
    return tuple(samples)
