"""Validate WLAN measurement start/stop/abort while Generator RF is off."""

from __future__ import annotations

from dataclasses import dataclass

from cmp180_evm.scpi.registry import ScpiCommandRegistry
from cmp180_evm.workflow.analyzer_setter_validation import (
    ALLOWED_IDLE_MEASUREMENT_STATES,
)
from cmp180_evm.workflow.generator_setter_validation import ScpiIo


@dataclass(frozen=True)
class LifecycleEvent:
    action: str
    state: str
    error: str


@dataclass(frozen=True)
class LifecycleValidation:
    initial_state: str
    final_state: str
    final_generator_state: str
    events: tuple[LifecycleEvent, ...]


def _query(io: ScpiIo, command: str) -> str:
    return io.query_str(command).strip()


def _require_no_error(error: str, context: str) -> None:
    if not error.startswith("0,"):
        raise RuntimeError(f"{context}: CMP180 error queue returned {error}")


def validate_measurement_lifecycle(
    io: ScpiIo,
    registry: ScpiCommandRegistry,
) -> LifecycleValidation:
    """Exercise INIT/STOP and INIT/ABORT without ever enabling Generator RF."""
    generator_state_query = registry.require("generator_query.state")
    measurement_state_query = registry.require("wlan_tx_query.measurement_state")
    error_query = registry.require("common.system_error")
    opc_query = registry.require("common.operation_complete")
    initiate = registry.require("wlan_tx.initiate")
    stop = registry.require("wlan_tx.stop")
    abort = registry.require("wlan_tx.abort")

    # 生命週期驗證只允許 Analyzer 動作；Generator RF 必須保持 OFF。
    initial_generator_state = _query(io, generator_state_query)
    initial_state = _query(io, measurement_state_query)
    if initial_generator_state != "OFF":
        raise RuntimeError(
            f"Refusing lifecycle validation because Generator RF is {initial_generator_state}"
        )
    if initial_state not in ALLOWED_IDLE_MEASUREMENT_STATES:
        raise RuntimeError(
            f"Refusing lifecycle validation because measurement is {initial_state}"
        )
    _require_no_error(_query(io, error_query), "Before lifecycle validation")

    events: list[LifecycleEvent] = []
    active = False
    try:
        # 第一循環驗證正常停止路徑：INITiate -> STOP。
        io.write_str(initiate)
        active = True
        _query(io, opc_query)
        error = _query(io, error_query)
        _require_no_error(error, "After INITiate for STOP")
        events.append(LifecycleEvent("initiate_for_stop", _query(io, measurement_state_query), error))

        io.write_str(stop)
        active = False
        _query(io, opc_query)
        error = _query(io, error_query)
        _require_no_error(error, "After STOP")
        stopped_state = _query(io, measurement_state_query)
        if stopped_state not in ALLOWED_IDLE_MEASUREMENT_STATES:
            raise RuntimeError(f"STOP did not return to idle state: {stopped_state}")
        events.append(LifecycleEvent("stop", stopped_state, error))

        # 第二循環驗證錯誤／取消時使用的中止路徑：INITiate -> ABORt。
        io.write_str(initiate)
        active = True
        _query(io, opc_query)
        error = _query(io, error_query)
        _require_no_error(error, "After INITiate for ABORt")
        events.append(LifecycleEvent("initiate_for_abort", _query(io, measurement_state_query), error))

        io.write_str(abort)
        active = False
        _query(io, opc_query)
        error = _query(io, error_query)
        _require_no_error(error, "After ABORt")
        aborted_state = _query(io, measurement_state_query)
        if aborted_state not in ALLOWED_IDLE_MEASUREMENT_STATES:
            raise RuntimeError(f"ABORt did not return to idle state: {aborted_state}")
        events.append(LifecycleEvent("abort", aborted_state, error))
    finally:
        if active:
            # 任一步驟失敗時先 STOP；STOP 本身失敗才以 ABORt 作為後備清理。
            try:
                io.write_str(stop)
                _query(io, opc_query)
            except Exception:
                io.write_str(abort)
                _query(io, opc_query)
        final_state = _query(io, measurement_state_query)
        final_generator_state = _query(io, generator_state_query)

    if final_state not in ALLOWED_IDLE_MEASUREMENT_STATES:
        raise RuntimeError(f"Unsafe final measurement state: {final_state}")
    if final_generator_state != "OFF":
        raise RuntimeError(f"Generator RF changed unexpectedly to {final_generator_state}")
    return LifecycleValidation(initial_state, final_state, final_generator_state, tuple(events))

