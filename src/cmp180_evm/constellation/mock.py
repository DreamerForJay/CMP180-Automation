"""Deterministic mock constellation generator with configurable impairments."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .analysis import analyze_constellation
from .models import (
    ConstellationDataset,
    ConstellationMetadata,
    ConstellationPoint,
    HilStatus,
    SourceKind,
)

SUPPORTED_MODULATIONS = {
    "BPSK": 2,
    "QPSK": 4,
    "16-QAM": 16,
    "64-QAM": 64,
    "256-QAM": 256,
    "1024-QAM": 1024,
    "4096-QAM": 4096,
}


@dataclass(frozen=True)
class MockConstellationConfig:
    modulation: str = "256-QAM"
    point_count: int = 1024
    noise_db: float = 32.0
    phase_deg: float = 0.0
    quadrature_error_deg: float = 0.0
    gain_imbalance_db: float = 0.0
    dc_i: float = 0.0
    dc_q: float = 0.0
    frequency_offset_hz: float = 0.0
    symbol_rate_hz: float = 1_000_000.0
    amplitude_scale: float = 1.0
    invalid_rate: float = 0.0
    seed: int = 180

    def validate(self) -> None:
        modulation = self.modulation.upper()
        if modulation not in SUPPORTED_MODULATIONS:
            raise ValueError(f"Unsupported modulation: {self.modulation}")
        if not 1 <= self.point_count <= 20_000:
            raise ValueError("point_count must be between 1 and 20000")
        if self.symbol_rate_hz <= 0:
            raise ValueError("symbol_rate_hz must be positive")
        if self.amplitude_scale <= 0:
            raise ValueError("amplitude_scale must be positive")
        if not 0 <= self.invalid_rate < 1:
            raise ValueError("invalid_rate must be between 0 and 1")


def ideal_constellation(modulation: str) -> tuple[tuple[float, float], ...]:
    """Return unit-average-power BPSK or square-QAM reference points."""
    name = modulation.upper()
    if name not in SUPPORTED_MODULATIONS:
        raise ValueError(f"Unsupported modulation: {modulation}")
    order = SUPPORTED_MODULATIONS[name]
    if order == 2:
        return ((-1.0, 0.0), (1.0, 0.0))
    side = math.isqrt(order)
    if side * side != order:
        raise ValueError(f"Modulation order must form square QAM: {order}")
    levels = tuple(range(-(side - 1), side, 2))
    # 方形 QAM 的平均 symbol energy 為 2/3*(M-1)，據此正規化成 1。
    scale = math.sqrt((2.0 / 3.0) * (order - 1))
    return tuple((i / scale, q / scale) for q in levels for i in levels)


def _normalize(points: list[tuple[float, float] | None]) -> list[tuple[float, float] | None]:
    finite = [point for point in points if point is not None]
    if not finite:
        return [None for _ in points]
    rms = math.sqrt(sum(i * i + q * q for i, q in finite) / len(finite))
    if rms == 0:
        return [None if point is None else point for point in points]
    return [None if point is None else (point[0] / rms, point[1] / rms) for point in points]


def generate_mock_constellation(config: MockConstellationConfig) -> ConstellationDataset:
    """Generate reproducible simulated points; this path never opens an instrument session."""
    config.validate()
    references = ideal_constellation(config.modulation)
    rng = random.Random(config.seed)
    snr_linear = 10 ** (config.noise_db / 10)
    noise_sigma = math.sqrt((1 / snr_linear) / 2) if snr_linear > 0 else 0.0
    phase_offset = math.radians(config.phase_deg)
    quadrature_error = math.radians(config.quadrature_error_deg)
    i_gain = 10 ** (config.gain_imbalance_db / 40)
    q_gain = 10 ** (-config.gain_imbalance_db / 40)
    measured: list[tuple[float, float] | None] = []
    selected: list[tuple[float, float]] = []

    for index in range(config.point_count):
        ideal_i, ideal_q = references[rng.randrange(len(references))]
        selected.append((ideal_i, ideal_q))
        if rng.random() < config.invalid_rate:
            measured.append(None)
            continue
        # Gain／quadrature error 先作用於正交軸，再加上 common phase 與頻偏旋轉。
        i_value = ideal_i * i_gain
        q_value = (ideal_q * math.cos(quadrature_error) + ideal_i * math.sin(quadrature_error)) * q_gain
        phase = phase_offset + 2 * math.pi * config.frequency_offset_hz * index / config.symbol_rate_hz
        rotated_i = i_value * math.cos(phase) - q_value * math.sin(phase)
        rotated_q = i_value * math.sin(phase) + q_value * math.cos(phase)
        measured.append(
            (
                config.amplitude_scale * rotated_i + config.dc_i + rng.gauss(0, noise_sigma),
                config.amplitude_scale * rotated_q + config.dc_q + rng.gauss(0, noise_sigma),
            )
        )

    normalized = _normalize(measured)
    points: list[ConstellationPoint] = []
    for index, (ideal_i, ideal_q) in enumerate(selected):
        raw = measured[index]
        normalized_point = normalized[index]
        valid = raw is not None and normalized_point is not None
        error = math.hypot(raw[0] - ideal_i, raw[1] - ideal_q) if raw is not None else None
        points.append(
            ConstellationPoint(
                symbol_index=index,
                i=raw[0] if raw else None,
                q=raw[1] if raw else None,
                normalized_i=normalized_point[0] if normalized_point else None,
                normalized_q=normalized_point[1] if normalized_point else None,
                ideal_i=ideal_i,
                ideal_q=ideal_q,
                evm=error,
                valid=valid,
            )
        )

    point_tuple = tuple(points)
    metadata = ConstellationMetadata(
        modulation=config.modulation.upper(),
        sample_count=len(points),
        valid_count=sum(point.valid for point in points),
        source=SourceKind.MOCK,
        simulated=True,
        hil_status=HilStatus.HIL_PENDING,
        impairments={
            "noise_db": config.noise_db,
            "phase_deg": config.phase_deg,
            "quadrature_error_deg": config.quadrature_error_deg,
            "gain_imbalance_db": config.gain_imbalance_db,
            "dc_i": config.dc_i,
            "dc_q": config.dc_q,
            "frequency_offset_hz": config.frequency_offset_hz,
            "symbol_rate_hz": config.symbol_rate_hz,
            "amplitude_scale": config.amplitude_scale,
            "invalid_rate": config.invalid_rate,
        },
        provenance=("SIMULATED", "DERIVED"),
    )
    return ConstellationDataset(
        metadata=metadata,
        points=point_tuple,
        ideal_points=references,
        analysis=analyze_constellation(point_tuple, simulated=True),
    )
