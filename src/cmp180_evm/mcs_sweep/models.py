"""MCS sweep 的標準資料模型與 hardware-independent 輸入驗證。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum


class MCSDataSource(StrEnum):
    MOCK = "mock"
    STORED = "stored"
    HARDWARE = "hardware"


class MCSHilStatus(StrEnum):
    NOT_RUN = "NOT_RUN"
    HIL_PENDING = "HIL_PENDING"
    VERIFIED = "VERIFIED"


@dataclass(frozen=True)
class MCSDefinition:
    mcs_index: int
    modulation: str
    coding_rate: str


# IEEE 802.11 EHT baseline；只描述 modulation/coding，不宣稱 CMP180 waveform mapping 已驗證。
EHT_MCS_DEFINITIONS: dict[int, MCSDefinition] = {
    0: MCSDefinition(0, "BPSK", "1/2"),
    1: MCSDefinition(1, "QPSK", "1/2"),
    2: MCSDefinition(2, "QPSK", "3/4"),
    3: MCSDefinition(3, "16-QAM", "1/2"),
    4: MCSDefinition(4, "16-QAM", "3/4"),
    5: MCSDefinition(5, "64-QAM", "2/3"),
    6: MCSDefinition(6, "64-QAM", "3/4"),
    7: MCSDefinition(7, "64-QAM", "5/6"),
    8: MCSDefinition(8, "256-QAM", "3/4"),
    9: MCSDefinition(9, "256-QAM", "5/6"),
    10: MCSDefinition(10, "1024-QAM", "3/4"),
    11: MCSDefinition(11, "1024-QAM", "5/6"),
    12: MCSDefinition(12, "4096-QAM", "3/4"),
    13: MCSDefinition(13, "4096-QAM", "5/6"),
}


@dataclass(frozen=True)
class MCSSweepPoint:
    mcs_index: int
    modulation: str
    coding_rate: str
    bandwidth_mhz: float
    frequency_hz: float
    evm_db: float | None
    power_dbm: float | None
    frequency_error_hz: float | None
    reliability: int | None
    valid: bool
    provenance: tuple[str, ...] = ("DERIVED",)


@dataclass(frozen=True)
class MCSSweepMetadata:
    standard: str
    selected_mcs: tuple[int, ...]
    point_count: int
    valid_count: int
    source: MCSDataSource
    simulated: bool
    hil_status: MCSHilStatus
    hardware_support: str = "HIL_PENDING"
    compliance_limits: str = "NOT_DEFINED"


@dataclass(frozen=True)
class MCSSweepDataset:
    metadata: MCSSweepMetadata
    points: tuple[MCSSweepPoint, ...]

    def public(self) -> dict[str, object]:
        metadata = asdict(self.metadata)
        metadata["source"] = self.metadata.source.value
        metadata["hil_status"] = self.metadata.hil_status.value
        return {"metadata": metadata, "points": [asdict(point) for point in self.points]}


def validate_mcs_list(values: list[int] | tuple[int, ...]) -> tuple[int, ...]:
    """保留使用者指定順序；拒絕空值、重複與 EHT baseline 外索引。"""
    if not values:
        raise ValueError("MCS list must not be empty")
    selected = tuple(values)
    if len(set(selected)) != len(selected):
        raise ValueError("MCS list must not contain duplicates")
    unknown = [value for value in selected if value not in EHT_MCS_DEFINITIONS]
    if unknown:
        raise ValueError(f"Unsupported EHT MCS index: {unknown}")
    return selected


def parse_mcs_list(value: str) -> tuple[int, ...]:
    """解析逗號分隔的任意 selected list，不強制連續範圍。"""
    tokens = [token.strip() for token in value.split(",") if token.strip()]
    if not tokens:
        raise ValueError("MCS list must not be empty")
    try:
        selected = [int(token) for token in tokens]
    except ValueError as exc:
        raise ValueError("MCS list must contain integers separated by commas") from exc
    return validate_mcs_list(selected)
