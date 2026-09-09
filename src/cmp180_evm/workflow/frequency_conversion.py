"""Frequency-converter (UDBox class) planning for CMP180 GPRF measurements.

A converter DUT breaks the assumption that the generator and the analyzer sit on
the same frequency. This module owns the single relation between IF, LO and RF so
callers never re-derive it, and reports which mixing products the CMP180 can
actually observe.
"""

from __future__ import annotations

from dataclasses import dataclass

# CMP180 tune 範圍；converter 的兩端都必須同時落在此範圍，否則儀器根本看不到訊號。
CMP180_MIN_FREQUENCY_HZ = 400_000_000.0
CMP180_MAX_FREQUENCY_HZ = 8_000_000_000.0

SIDEBANDS = ("high", "low")
DIRECTIONS = ("up", "down")


@dataclass(frozen=True)
class ConverterLimits:
    """DUT 端的調諧範圍。來源必須註記，不得由其他型號推定。"""

    if_min_hz: float
    if_max_hz: float
    rf_min_hz: float
    rf_max_hz: float
    lo_min_hz: float
    lo_max_hz: float
    source: str = ""

    def public(self) -> dict[str, object]:
        return {
            "if_min_hz": self.if_min_hz,
            "if_max_hz": self.if_max_hz,
            "rf_min_hz": self.rf_min_hz,
            "rf_max_hz": self.rf_max_hz,
            "lo_min_hz": self.lo_min_hz,
            "lo_max_hz": self.lo_max_hz,
            "source": self.source,
        }


# TMYTEK UD Box 0630 datasheet RF Specifications 表：RF 6–30 GHz、IF 1–8 GHz、LO 6–30 GHz。
# 功率上限不在此處：datasheet 只給 P1dB（線性度），沒有 absolute maximum rating，
# 因此 DUT 輸入上限必須由操作員在 request/profile 中明確提供。
UDBOX_0630_LIMITS = ConverterLimits(
    if_min_hz=1_000_000_000.0,
    if_max_hz=8_000_000_000.0,
    rf_min_hz=6_000_000_000.0,
    rf_max_hz=30_000_000_000.0,
    lo_min_hz=6_000_000_000.0,
    lo_max_hz=30_000_000_000.0,
    source="TMYTEK UD Box 0630 datasheet RF Specifications table; not hardware-verified",
)


def _is_observable(frequency_hz: float) -> bool:
    return CMP180_MIN_FREQUENCY_HZ <= frequency_hz <= CMP180_MAX_FREQUENCY_HZ


@dataclass(frozen=True)
class ConversionPlan:
    """One IF/LO/RF triple plus the CMP180 port roles it implies."""

    direction: str
    sideband: str
    if_frequency_hz: float
    lo_frequency_hz: float

    def __post_init__(self) -> None:
        if self.direction not in DIRECTIONS:
            raise ValueError(f"Conversion direction must be one of {DIRECTIONS}")
        if self.sideband not in SIDEBANDS:
            raise ValueError(f"Conversion sideband must be one of {SIDEBANDS}")

    @classmethod
    def from_generator_frequency(
        cls,
        *,
        generator_frequency_hz: float,
        lo_frequency_hz: float,
        sideband: str,
        direction: str,
    ) -> ConversionPlan:
        """Build a plan from the frequency the CMP180 generator actually drives."""
        if direction not in DIRECTIONS:
            raise ValueError(f"Conversion direction must be one of {DIRECTIONS}")
        if sideband not in SIDEBANDS:
            raise ValueError(f"Conversion sideband must be one of {SIDEBANDS}")
        if direction == "up":
            # up-conversion：generator 直接驅動 IF port。
            if_frequency_hz = generator_frequency_hz
        elif sideband == "high":
            # down-conversion 掃的是 RF；由 RF 與 LO 反解 IF，維持單一頻率關係來源。
            if_frequency_hz = generator_frequency_hz - lo_frequency_hz
        else:
            if_frequency_hz = lo_frequency_hz - generator_frequency_hz
        return cls(
            direction=direction,
            sideband=sideband,
            if_frequency_hz=if_frequency_hz,
            lo_frequency_hz=lo_frequency_hz,
        )

    @property
    def rf_frequency_hz(self) -> float:
        # 高側 RF = LO + IF、低側 RF = LO − IF；兩者是同一顆混頻器的兩個乘積。
        if self.sideband == "high":
            return self.lo_frequency_hz + self.if_frequency_hz
        return self.lo_frequency_hz - self.if_frequency_hz

    @property
    def mirror_frequency_hz(self) -> float:
        # 另一個混頻乘積：up-conversion 時是不要的邊帶，down-conversion 時是鏡像輸入頻率。
        if self.sideband == "high":
            return self.lo_frequency_hz - self.if_frequency_hz
        return self.lo_frequency_hz + self.if_frequency_hz

    @property
    def generator_frequency_hz(self) -> float:
        # up：CMP180 送 IF、收 RF；down：CMP180 送 RF、收 IF。
        return self.if_frequency_hz if self.direction == "up" else self.rf_frequency_hz

    @property
    def analyzer_frequency_hz(self) -> float:
        return self.rf_frequency_hz if self.direction == "up" else self.if_frequency_hz

    def validate(self, limits: ConverterLimits) -> list[str]:
        """Collect every reason this triple cannot be measured, in operator wording."""
        errors: list[str] = []
        if self.if_frequency_hz <= 0 or self.rf_frequency_hz <= 0:
            # 低側注入且 LO ≤ IF 會算出零或負頻率，代表 LO 設定根本不成立。
            errors.append(
                "Conversion produces a non-positive frequency; check LO against IF for "
                f"{self.sideband}-side injection (IF {self.if_frequency_hz:.0f} Hz, "
                f"LO {self.lo_frequency_hz:.0f} Hz)"
            )
            return errors
        if not limits.if_min_hz <= self.if_frequency_hz <= limits.if_max_hz:
            errors.append(
                f"IF {self.if_frequency_hz / 1e6:.3f} MHz is outside the converter IF range "
                f"{limits.if_min_hz / 1e6:.0f}..{limits.if_max_hz / 1e6:.0f} MHz"
            )
        if not limits.rf_min_hz <= self.rf_frequency_hz <= limits.rf_max_hz:
            errors.append(
                f"RF {self.rf_frequency_hz / 1e6:.3f} MHz is outside the converter RF range "
                f"{limits.rf_min_hz / 1e6:.0f}..{limits.rf_max_hz / 1e6:.0f} MHz"
            )
        if not limits.lo_min_hz <= self.lo_frequency_hz <= limits.lo_max_hz:
            errors.append(
                f"LO {self.lo_frequency_hz / 1e6:.3f} MHz is outside the converter LO range "
                f"{limits.lo_min_hz / 1e6:.0f}..{limits.lo_max_hz / 1e6:.0f} MHz"
            )
        # CMP180 兩端都必須可調；否則規劃看起來合理但實機必然量到底噪。
        if not _is_observable(self.generator_frequency_hz):
            errors.append(
                f"Generator frequency {self.generator_frequency_hz / 1e6:.3f} MHz is outside the "
                "CMP180 400 MHz..8 GHz range"
            )
        if not _is_observable(self.analyzer_frequency_hz):
            errors.append(
                f"Analyzer frequency {self.analyzer_frequency_hz / 1e6:.3f} MHz is outside the "
                "CMP180 400 MHz..8 GHz range"
            )
        return errors

    def public(self) -> dict[str, object]:
        return {
            "direction": self.direction,
            "sideband": self.sideband,
            "if_frequency_hz": self.if_frequency_hz,
            "lo_frequency_hz": self.lo_frequency_hz,
            "rf_frequency_hz": self.rf_frequency_hz,
            "generator_frequency_hz": self.generator_frequency_hz,
            "analyzer_frequency_hz": self.analyzer_frequency_hz,
            "mirror_frequency_hz": self.mirror_frequency_hz,
            # 鏡像與 LO 洩漏若落在 CMP180 內就能免費觀測，落在外面只代表看不到、不是錯誤。
            "mirror_observable": _is_observable(self.mirror_frequency_hz),
            "lo_leakage_observable": _is_observable(self.lo_frequency_hz),
        }


def build_converter_limits(data: dict[str, object] | None) -> ConverterLimits:
    """Read DUT tuning limits from a request/config mapping, defaulting to UD Box 0630."""
    if not data:
        return UDBOX_0630_LIMITS
    return ConverterLimits(
        if_min_hz=float(data.get("if_min_hz", UDBOX_0630_LIMITS.if_min_hz)),
        if_max_hz=float(data.get("if_max_hz", UDBOX_0630_LIMITS.if_max_hz)),
        rf_min_hz=float(data.get("rf_min_hz", UDBOX_0630_LIMITS.rf_min_hz)),
        rf_max_hz=float(data.get("rf_max_hz", UDBOX_0630_LIMITS.rf_max_hz)),
        lo_min_hz=float(data.get("lo_min_hz", UDBOX_0630_LIMITS.lo_min_hz)),
        lo_max_hz=float(data.get("lo_max_hz", UDBOX_0630_LIMITS.lo_max_hz)),
        source=str(data.get("source") or UDBOX_0630_LIMITS.source),
    )
