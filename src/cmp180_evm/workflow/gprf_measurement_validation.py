"""Controlled same-value GPRF measurement setter validation with RF required off.

GPRF measurement 的 routing 與位準原本從未由 workflow 寫入，導致量測端可能停在
與接線不符的 port（run `252bbbe39a` 實測為 `"RF1.6"`，實際接線為 RF1.5）。本模組
只把剛讀到的原值寫回，用來確立 setter 出處，不改變任何 RF 條件。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from cmp180_evm.scpi.registry import ScpiCommandRegistry


class ScpiIo(Protocol):
    def query_str(self, command: str) -> str: ...

    def write_str(self, command: str) -> None: ...


@dataclass(frozen=True)
class GprfSetterCheck:
    name: str
    original: str
    readback: str
    error: str


@dataclass(frozen=True)
class GprfMeasurementSetterValidation:
    initial_rf_state: str
    final_rf_state: str
    checks: tuple[GprfSetterCheck, ...]


def _query(io: ScpiIo, command: str) -> str:
    return io.query_str(command).strip()


def _require_no_error(error: str, context: str) -> None:
    if not error.startswith(("0,", "+0,")):
        raise RuntimeError(f"{context}: CMP180 error queue returned {error}")


def _values_match(name: str, original: str, readback: str) -> bool:
    # rf_path 是帶引號字串，必須完全相同；位準是浮點數，允許儀器格式化誤差。
    if name == "rf_path":
        return readback == original
    try:
        original_value = float(original)
        readback_value = float(readback)
    except ValueError:
        return readback == original
    tolerance = max(abs(original_value) * 1e-9, 1e-9)
    return abs(readback_value - original_value) <= tolerance


def validate_gprf_measurement_setters(
    io: ScpiIo,
    registry: ScpiCommandRegistry,
) -> GprfMeasurementSetterValidation:
    """Write back the current GPRF measurement routing/level; never enables RF."""
    # 寫入前強制確認 Generator RF Off；此工具刻意沒有 RF On 指令可用。
    state_query = registry.require("generator_query.state")
    error_query = registry.require("common.system_error")
    initial_state = _query(io, state_query)
    if initial_state != "OFF":
        raise RuntimeError(
            f"Refusing GPRF setter validation because Generator RF is {initial_state}"
        )

    _require_no_error(_query(io, error_query), "Before GPRF setter validation")

    definitions = (
        (
            "rf_path",
            "gprf_measurement.set_rf_path",
            "gprf_measurement_query.rf_path",
            "rf_path",
        ),
        (
            "expected_power",
            "gprf_measurement.set_expected_power",
            "gprf_measurement_query.expected_power",
            "expected_power_dbm",
        ),
        (
            "external_attenuation",
            "gprf_measurement.set_external_attenuation",
            "gprf_measurement_query.external_attenuation",
            "external_attenuation_db",
        ),
    )

    checks: list[GprfSetterCheck] = []
    try:
        for name, setter_name, query_name, placeholder in definitions:
            # 只寫回剛讀到的原值，驗證 setter 時不改變量測條件。
            original = _query(io, registry.require(query_name))
            io.write_str(registry.render(setter_name, **{placeholder: original}))
            _query(io, registry.require("common.operation_complete"))
            error = _query(io, error_query)
            _require_no_error(error, f"After {name} setter")
            readback = _query(io, registry.require(query_name))
            if not _values_match(name, original, readback):
                raise RuntimeError(
                    f"{name} readback mismatch: wrote {original}, received {readback}"
                )
            checks.append(GprfSetterCheck(name, original, readback, error))
    finally:
        # 即使 setter 或 read-back 失敗，也要留下最後 RF 狀態證據。
        final_state = _query(io, state_query)

    if final_state != "OFF":
        raise RuntimeError(f"Generator RF changed unexpectedly to {final_state}")
    return GprfMeasurementSetterValidation(initial_state, final_state, tuple(checks))
