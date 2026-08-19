"""Controlled low-power Generator RF On/Off pulse validation."""

from __future__ import annotations

from dataclasses import dataclass

from cmp180_evm.scpi.registry import ScpiCommandRegistry
from cmp180_evm.workflow.analyzer_setter_validation import (
    ALLOWED_IDLE_MEASUREMENT_STATES,
)
from cmp180_evm.workflow.generator_setter_validation import ScpiIo


@dataclass(frozen=True)
class RfStateValidation:
    frequency_hz: float
    power_dbm: float
    on_state: str
    final_state: str
    on_error: str
    off_error: str


def _query(io: ScpiIo, command: str) -> str:
    return io.query_str(command).strip()


def _require_no_error(error: str, context: str) -> None:
    if not error.startswith("0,"):
        raise RuntimeError(f"{context}: CMP180 error queue returned {error}")


def validate_low_power_rf_pulse(
    io: ScpiIo,
    registry: ScpiCommandRegistry,
    *,
    operator_confirmed_direct_cable: bool,
    maximum_power_dbm: float = -40.0,
) -> RfStateValidation:
    """Enable RF briefly and always force RF off in finally."""
    if not operator_confirmed_direct_cable:
        raise RuntimeError("Operator must confirm the RF1.1 to RF1.5 direct cable")

    state_query = registry.require("generator_query.state")
    measurement_state_query = registry.require("wlan_tx_query.measurement_state")
    error_query = registry.require("common.system_error")
    opc_query = registry.require("common.operation_complete")
    rf_on = registry.require("generator.rf_on")
    rf_off = registry.require("generator.rf_off")

    initial_state = _query(io, state_query)
    measurement_state = _query(io, measurement_state_query)
    frequency_hz = float(_query(io, registry.require("generator_query.frequency")))
    power_dbm = float(_query(io, registry.require("generator_query.level")))
    if initial_state != "OFF":
        raise RuntimeError(f"Refusing RF pulse because initial RF state is {initial_state}")
    if measurement_state not in ALLOWED_IDLE_MEASUREMENT_STATES:
        raise RuntimeError(f"Refusing RF pulse because measurement is {measurement_state}")
    if power_dbm > maximum_power_dbm:
        raise RuntimeError(
            f"Refusing RF pulse because {power_dbm} dBm exceeds {maximum_power_dbm} dBm"
        )
    _require_no_error(_query(io, error_query), "Before RF pulse")

    on_attempted = False
    on_state = "UNKNOWN"
    on_error = "not queried"
    off_error = "not queried"
    try:
        # RF On 後只做同步、查錯與狀態 read-back，不啟動 Analyzer measurement。
        on_attempted = True
        io.write_str(rf_on)
        _query(io, opc_query)
        on_error = _query(io, error_query)
        _require_no_error(on_error, "After RF On")
        on_state = _query(io, state_query)
        if on_state != "ON":
            raise RuntimeError(f"RF On readback was {on_state}")
    finally:
        if on_attempted:
            # 即使 RF On、OPC、error query 或 read-back 失敗，也必須送 RF Off。
            io.write_str(rf_off)
            _query(io, opc_query)
            off_error = _query(io, error_query)
        final_state = _query(io, state_query)

    _require_no_error(off_error, "After RF Off")
    if final_state != "OFF":
        raise RuntimeError(f"Unsafe final RF state: {final_state}")
    return RfStateValidation(
        frequency_hz,
        power_dbm,
        on_state,
        final_state,
        on_error,
        off_error,
    )

