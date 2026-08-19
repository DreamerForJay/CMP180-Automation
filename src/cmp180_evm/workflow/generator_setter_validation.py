"""Controlled same-value Generator setter validation with RF required off."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from cmp180_evm.scpi.registry import ScpiCommandRegistry


class ScpiIo(Protocol):
    def query_str(self, command: str) -> str: ...

    def write_str(self, command: str) -> None: ...


@dataclass(frozen=True)
class SetterCheck:
    name: str
    original: float
    readback: float
    error: str


@dataclass(frozen=True)
class GeneratorSetterValidation:
    initial_rf_state: str
    final_rf_state: str
    checks: tuple[SetterCheck, ...]


def _query(io: ScpiIo, command: str) -> str:
    return io.query_str(command).strip()


def _require_no_error(error: str, context: str) -> None:
    if not error.startswith("0,"):
        raise RuntimeError(f"{context}: CMP180 error queue returned {error}")


def validate_same_value_setters(
    io: ScpiIo,
    registry: ScpiCommandRegistry,
) -> GeneratorSetterValidation:
    """Write back current frequency/level only; never enables or initiates RF."""
    # 寫入前強制確認 RF Off；此工具刻意沒有 RF On 指令可用。
    state_query = registry.require("generator_query.state")
    error_query = registry.require("common.system_error")
    initial_state = _query(io, state_query)
    if initial_state != "OFF":
        raise RuntimeError(f"Refusing setter validation because Generator RF is {initial_state}")

    initial_error = _query(io, error_query)
    _require_no_error(initial_error, "Before setter validation")
    frequency = float(_query(io, registry.require("generator_query.frequency")))
    power = float(_query(io, registry.require("generator_query.level")))
    checks: list[SetterCheck] = []

    try:
        # 只寫回剛從儀器讀到的原值，避免驗證 setter 時改變 RF 條件。
        for name, original, setter_name, query_name, placeholder in (
            (
                "frequency",
                frequency,
                "generator.set_frequency",
                "generator_query.frequency",
                "frequency_hz",
            ),
            (
                "power",
                power,
                "generator.set_power",
                "generator_query.level",
                "power_dbm",
            ),
        ):
            io.write_str(registry.render(setter_name, **{placeholder: original}))
            _query(io, registry.require("common.operation_complete"))
            error = _query(io, error_query)
            _require_no_error(error, f"After {name} setter")
            readback = float(_query(io, registry.require(query_name)))
            tolerance = max(abs(original) * 1e-9, 1e-9)
            if abs(readback - original) > tolerance:
                raise RuntimeError(
                    f"{name} readback mismatch: wrote {original}, received {readback}"
                )
            checks.append(SetterCheck(name, original, readback, error))
    finally:
        # 即使 setter 或 read-back 失敗，也要留下最後 RF 狀態證據。
        final_state = _query(io, state_query)

    if final_state != "OFF":
        raise RuntimeError(f"Generator RF changed unexpectedly to {final_state}")
    return GeneratorSetterValidation(initial_state, final_state, tuple(checks))
