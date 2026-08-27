"""Layered CMP180 capability model for Web planning and RF authorization."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class RangeLayer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frequency_min_hz: float
    frequency_max_hz: float

    @model_validator(mode="after")
    def validate_range(self) -> RangeLayer:
        if self.frequency_min_hz >= self.frequency_max_hz:
            raise ValueError("frequency_min_hz must be below frequency_max_hz")
        return self


class CatalogCapabilities(RangeLayer):
    maximum_analysis_bandwidth_hz: float
    analyzer_count: int = Field(ge=1)
    generator_count: int = Field(ge=1)
    rf_port_count: int = Field(ge=1)
    supports_list_mode: bool


class InstalledCapabilities(RangeLayer):
    analysis_bandwidths_hz: list[float]
    analyzer_count: int = Field(ge=1)
    generator_count: int = Field(ge=1)
    rf_ports: list[str]


class ApprovedProfile(RangeLayer):
    profile_id: str
    lifecycle: str
    maximum_span_hz: float
    bandwidths_hz: list[float]
    generator_power_min_dbm: float
    generator_power_max_dbm: float
    dwell_min_ms: int
    dwell_max_ms: int
    maximum_points: int = Field(ge=1)
    routes: list[str]

    @model_validator(mode="after")
    def validate_envelope(self) -> ApprovedProfile:
        if self.lifecycle != "approved":
            raise ValueError("RF execution profile must have lifecycle: approved")
        if self.generator_power_min_dbm > self.generator_power_max_dbm:
            raise ValueError("generator power minimum must not exceed maximum")
        if self.dwell_min_ms > self.dwell_max_ms:
            raise ValueError("dwell minimum must not exceed maximum")
        return self


class VerifiedHil(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frequencies_hz: list[float]
    bandwidths_hz: list[float]
    generator_powers_dbm: list[float]
    dwell_ms: list[int]
    routes: list[str]


class InstrumentCapabilityProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    instrument_model: str
    catalog: CatalogCapabilities
    installed: InstalledCapabilities
    approved_profile: ApprovedProfile
    verified_hil: VerifiedHil

    def public(self) -> dict[str, Any]:
        payload = self.model_dump()
        # UI 必須明確區分型錄、已安裝、核准與 HIL，禁止將型錄上限標成可執行。
        payload["layers"] = ["catalog", "installed", "approved_profile", "verified_hil"]
        payload["rf_execution_source"] = "approved_profile"
        payload["catalog_grants_execution"] = False
        return payload


def load_capability_profile(path: Path) -> InstrumentCapabilityProfile:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return InstrumentCapabilityProfile.model_validate(data)
