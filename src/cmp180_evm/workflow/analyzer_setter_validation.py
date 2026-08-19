"""Controlled same-value WLAN analyzer setter validation."""

from __future__ import annotations

from dataclasses import dataclass

from cmp180_evm.scpi.registry import ScpiCommandRegistry
from cmp180_evm.workflow.generator_setter_validation import ScpiIo


# CMP180 的 OFF 與 RDY 都是不在擷取中的 idle 狀態；其餘狀態一律拒絕寫入。
ALLOWED_IDLE_MEASUREMENT_STATES = frozenset({"OFF", "RDY"})


@dataclass(frozen=True)
class AnalyzerSetterCheck:
    name: str
    original: str
    readback: str
    error: str


@dataclass(frozen=True)
class AnalyzerSetterValidation:
    initial_generator_state: str
    final_generator_state: str
    initial_measurement_state: str
    final_measurement_state: str
    checks: tuple[AnalyzerSetterCheck, ...]


def _query(io: ScpiIo, command: str) -> str:
    return io.query_str(command).strip()


def _require_no_error(error: str, context: str) -> None:
    if not error.startswith("0,"):
        raise RuntimeError(f"{context}: CMP180 error queue returned {error}")


def _equivalent(original: str, readback: str) -> bool:
    """Compare numeric SCPI values numerically and enums/routes textually."""
    try:
        left = float(original)
        right = float(readback)
    except ValueError:
        # 路徑與 enum 可能帶引號；比較時只移除外層引號與空白。
        return original.strip('" ') == readback.strip('" ')
    tolerance = max(abs(left) * 1e-9, 1e-9)
    return abs(left - right) <= tolerance


def validate_analyzer_same_value_setters(
    io: ScpiIo,
    registry: ScpiCommandRegistry,
) -> AnalyzerSetterValidation:
    """Write back current analyzer settings while Generator and measurement are off."""
    generator_state_query = registry.require("generator_query.state")
    measurement_state_query = registry.require("wlan_tx_query.measurement_state")
    error_query = registry.require("common.system_error")

    # Analyzer setter 前同時鎖住兩個危險狀態：Generator RF 與 WLAN measurement。
    initial_generator_state = _query(io, generator_state_query)
    initial_measurement_state = _query(io, measurement_state_query)
    if initial_generator_state != "OFF":
        raise RuntimeError(
            f"Refusing analyzer setter validation because Generator RF is {initial_generator_state}"
        )
    if initial_measurement_state not in ALLOWED_IDLE_MEASUREMENT_STATES:
        raise RuntimeError(
            "Refusing analyzer setter validation because WLAN measurement is "
            f"{initial_measurement_state}"
        )

    _require_no_error(_query(io, error_query), "Before analyzer setter validation")
    definitions = (
        ("rf_path", "wlan_tx.set_rf_path", "wlan_tx_query.rf_path", "rf_path"),
        (
            "bandwidth",
            "wlan_tx.set_bandwidth",
            "wlan_tx_query.bandwidth",
            "bandwidth",
        ),
        (
            "frequency",
            "wlan_tx.set_frequency",
            "wlan_tx_query.center_frequency",
            "frequency_hz",
        ),
        (
            "external_attenuation",
            "wlan_tx.set_external_attenuation",
            "wlan_tx_query.external_attenuation",
            "external_attenuation_db",
        ),
        (
            "expected_power",
            "wlan_tx.set_expected_power",
            "wlan_tx_query.expected_nominal_power",
            "expected_power_dbm",
        ),
    )
    originals = {
        name: _query(io, registry.require(query_name))
        for name, _, query_name, _ in definitions
    }
    checks: list[AnalyzerSetterCheck] = []

    try:
        # 每一項只寫回現值，並立刻同步、查錯及 read-back，方便定位單一命令。
        for name, setter_name, query_name, placeholder in definitions:
            original = originals[name]
            io.write_str(registry.render(setter_name, **{placeholder: original}))
            _query(io, registry.require("common.operation_complete"))
            error = _query(io, error_query)
            _require_no_error(error, f"After analyzer {name} setter")
            readback = _query(io, registry.require(query_name))
            if not _equivalent(original, readback):
                raise RuntimeError(
                    f"Analyzer {name} readback mismatch: wrote {original}, received {readback}"
                )
            checks.append(AnalyzerSetterCheck(name, original, readback, error))
    finally:
        # 任何例外路徑都重新讀取兩個狀態，確保沒有意外啟動 RF 或量測。
        final_measurement_state = _query(io, measurement_state_query)
        final_generator_state = _query(io, generator_state_query)

    if (
        final_generator_state != "OFF"
        or final_measurement_state not in ALLOWED_IDLE_MEASUREMENT_STATES
    ):
        raise RuntimeError(
            "Unsafe final state: Generator "
            f"{final_generator_state}, measurement {final_measurement_state}"
        )
    return AnalyzerSetterValidation(
        initial_generator_state,
        final_generator_state,
        initial_measurement_state,
        final_measurement_state,
        tuple(checks),
    )
