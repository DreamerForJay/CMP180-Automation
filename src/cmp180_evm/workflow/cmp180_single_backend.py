"""Real CMP180 backend for the verified WLAN single-measurement workflow."""

from __future__ import annotations

import time

from cmp180_evm.results.ofdm_siso import parse_result
from cmp180_evm.scpi.registry import ScpiCommandRegistry
from cmp180_evm.workflow.analyzer_setter_validation import (
    ALLOWED_IDLE_MEASUREMENT_STATES,
)
from cmp180_evm.workflow.generator_setter_validation import ScpiIo
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan


BANDWIDTH_ENUMS = {
    20_000_000: "BW20",
    40_000_000: "BW40",
    80_000_000: "BW80",
    160_000_000: "BW16",
    320_000_000: "BW32",
}


class Cmp180SingleMeasurementBackend:
    """Combine only commands already verified individually on this CMP180."""

    def __init__(
        self,
        io: ScpiIo,
        registry: ScpiCommandRegistry,
        *,
        timeout_s: float = 15.0,
        poll_interval_s: float = 0.1,
    ) -> None:
        self.io = io
        self.registry = registry
        self.timeout_s = timeout_s
        self.poll_interval_s = poll_interval_s
        self.raw_result: str | None = None

    def _query(self, name: str) -> str:
        return self.io.query_str(self.registry.require(name)).strip()

    def _write_checked(self, name: str, **values: float | str) -> None:
        command = self.registry.render(name, **values) if values else self.registry.require(name)
        self.io.write_str(command)
        self._query("common.operation_complete")
        error = self._query("common.system_error")
        if not error.startswith("0,"):
            raise RuntimeError(f"{name}: CMP180 returned {error}")

    def _require_readback(self, name: str, expected: float | str) -> None:
        actual = self._query(name)
        try:
            left = float(expected)
            right = float(actual)
        except ValueError:
            matches = str(expected).strip('" ') == actual.strip('" ')
        else:
            matches = abs(left - right) <= max(abs(left) * 1e-9, 1e-9)
        if not matches:
            raise RuntimeError(f"{name} readback mismatch: expected {expected}, got {actual}")

    def configure(self, plan: SingleMeasurementPlan) -> None:
        # 完整流程開始前再次確認 RF 與 Analyzer 都不在執行狀態。
        if self._query("generator_query.state") != "OFF":
            raise RuntimeError("Generator RF must be OFF before configuration")
        measurement_state = self._query("wlan_tx_query.measurement_state")
        if measurement_state not in ALLOWED_IDLE_MEASUREMENT_STATES:
            raise RuntimeError(f"Measurement must be idle before configuration: {measurement_state}")
        bandwidth = BANDWIDTH_ENUMS.get(int(plan.bandwidth_hz))
        if bandwidth is None:
            raise ValueError(f"Unsupported WLAN bandwidth: {plan.bandwidth_hz}")

        # 這些 setter 已逐項通過實機同值驗證；每一項仍獨立 OPC 與查錯。
        self._write_checked("generator.set_frequency", frequency_hz=plan.center_frequency_hz)
        self._write_checked("generator.set_power", power_dbm=plan.generator_power_dbm)
        self._write_checked("wlan_tx.set_rf_path", rf_path=f'"{plan.analyzer_port}"')
        self._write_checked("wlan_tx.set_bandwidth", bandwidth=bandwidth)
        self._write_checked("wlan_tx.set_frequency", frequency_hz=plan.center_frequency_hz)
        self._write_checked(
            "wlan_tx.set_external_attenuation",
            external_attenuation_db=plan.external_attenuation_db,
        )
        self._write_checked(
            "wlan_tx.set_expected_power",
            expected_power_dbm=plan.expected_nominal_power_dbm,
        )
        # 所有 setter 完成後逐項 read-back，避免在錯誤設定下繼續 RF On。
        self._require_readback("generator_query.frequency", plan.center_frequency_hz)
        self._require_readback("generator_query.level", plan.generator_power_dbm)
        self._require_readback("wlan_tx_query.rf_path", plan.analyzer_port)
        self._require_readback("wlan_tx_query.bandwidth", bandwidth)
        self._require_readback("wlan_tx_query.center_frequency", plan.center_frequency_hz)
        self._require_readback(
            "wlan_tx_query.external_attenuation", plan.external_attenuation_db
        )
        self._require_readback(
            "wlan_tx_query.expected_nominal_power", plan.expected_nominal_power_dbm
        )

    def rf_on(self) -> None:
        self._write_checked("generator.rf_on")
        if self._query("generator_query.state") != "ON":
            raise RuntimeError("Generator RF On readback failed")

    def initiate_single(self) -> None:
        self._write_checked("wlan_tx.initiate")

    def wait_ready(self) -> None:
        deadline = time.monotonic() + self.timeout_s
        observed: list[str] = []
        while time.monotonic() < deadline:
            state = self._query("wlan_tx_query.measurement_state")
            if not observed or state != observed[-1]:
                observed.append(state)
            if state == "RDY":
                return
            if state in {"INV", "OFF"}:
                raise RuntimeError(f"Measurement entered {state}; observed={observed}")
            time.sleep(self.poll_interval_s)
        raise TimeoutError(f"Measurement did not reach RDY; observed={observed}")

    def fetch_result(self) -> dict[str, object]:
        # INITiate 已完成後才使用 FETCh，避免讀到前一次 stale result。
        self.raw_result = self._query("results.modulation_average")
        values = parse_result(self.raw_result)
        return {"raw": self.raw_result, **values}

    def stop_measurement(self) -> None:
        self._write_checked("wlan_tx.stop")

    def rf_off(self) -> None:
        self._write_checked("generator.rf_off")
        if self._query("generator_query.state") != "OFF":
            raise RuntimeError("Generator RF Off readback failed")

    def drain_error_queue(self) -> list[str]:
        errors: list[str] = []
        for _ in range(50):
            response = self._query("common.system_error")
            if response.startswith("0,") or response.startswith("+0,"):
                return errors
            errors.append(response)
        raise RuntimeError("CMP180 error queue did not terminate")
