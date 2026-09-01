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
from cmp180_evm.workflow.wlan_bands import executable_band_for

BANDWIDTH_ENUMS = {
    20_000_000: "BW20",
    40_000_000: "BW40",
    80_000_000: "BW80",
    160_000_000: "BW16",
    320_000_000: "BW32",
}

VERIFIED_WLAN_STANDARD = "EHTofdm"
VERIFIED_WLAN_STANDARD_READBACK = "EHT"
VERIFIED_WLAN_BAND = "B6GHz"
VERIFIED_WLAN_BAND_READBACK = "B6GH"
# -40 dBm 直連短封包在預設 -30 dB threshold 曾觸發逾時；-45 dB 仍在 Help 規定的 -50..0 dB 範圍。
VERIFIED_TRIGGER_THRESHOLD_DB = -45.0
VERIFIED_TRIGGER_SOURCE = "IF Power"
VERIFIED_REPETITION = "SINGleshot"
VERIFIED_REPETITION_READBACK = "SING"
VERIFIED_MODULATION_STATISTIC_COUNT = 10


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
        self.last_measurement_states: list[str] = []

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
            raise RuntimeError(
                f"Measurement must be idle before configuration: {measurement_state}"
            )
        bandwidth = BANDWIDTH_ENUMS.get(int(plan.bandwidth_hz))
        if bandwidth is None:
            raise ValueError(f"Unsupported WLAN bandwidth: {plan.bandwidth_hz}")

        # 這些 setter 已逐項通過實機同值驗證；每一項仍獨立 OPC 與查錯。
        self._write_checked("generator.set_frequency", frequency_hz=plan.center_frequency_hz)
        self._write_checked("generator.set_power", power_dbm=plan.generator_power_dbm)
        # 儀器重啟後可能回到 LOFD/B24G，必須在頻寬與頻率前恢復 EHT/6 GHz。
        self._write_checked("wlan_tx.set_standard", standard=VERIFIED_WLAN_STANDARD)
        # Band 依中心頻率選取，不再寫死 6 GHz；未驗證 enum 的 band 會在此拒絕。
        band = executable_band_for(plan.center_frequency_hz)
        if plan.bandwidth_hz > band.maximum_bandwidth_hz:
            raise ValueError(
                f"{plan.bandwidth_hz / 1e6:.0f} MHz exceeds the {band.name} band maximum"
            )
        self._write_checked("wlan_tx.set_band", band=band.band_enum)
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
        self._write_checked(
            "wlan_tx.set_trigger_threshold",
            threshold_db=VERIFIED_TRIGGER_THRESHOLD_DB,
        )
        # lib8/GI32 實機 HIL 使用 IF Power；Restart Marker 曾造成 RDY,ADJ,INV。
        self._write_checked(
            "wlan_tx.set_trigger_source", source=f'"{VERIFIED_TRIGGER_SOURCE}"'
        )
        # Continuous + Stop Condition None 會讓 INIT 永遠維持 RUN；遠端固定條件
        # 量測依 CMP180 WebHelp 強制 SingleShot，並明確設定每次 10 個 interval。
        self._write_checked("wlan_tx.set_repetition", repetition=VERIFIED_REPETITION)
        self._write_checked(
            "wlan_tx.set_modulation_statistic_count",
            count=VERIFIED_MODULATION_STATISTIC_COUNT,
        )
        # 所有 setter 完成後逐項 read-back，避免在錯誤設定下繼續 RF On。
        self._require_readback("generator_query.frequency", plan.center_frequency_hz)
        self._require_readback("generator_query.level", plan.generator_power_dbm)
        self._require_readback("wlan_tx_query.standard", VERIFIED_WLAN_STANDARD_READBACK)
        self._require_readback("wlan_tx_query.band", band.band_readback)
        self._require_readback("wlan_tx_query.rf_path", plan.analyzer_port)
        self._require_readback("wlan_tx_query.bandwidth", bandwidth)
        self._require_readback("wlan_tx_query.center_frequency", plan.center_frequency_hz)
        self._require_readback(
            "wlan_tx_query.external_attenuation", plan.external_attenuation_db
        )
        self._require_readback(
            "wlan_tx_query.expected_nominal_power", plan.expected_nominal_power_dbm
        )
        self._require_readback(
            "wlan_tx_query.trigger_threshold", VERIFIED_TRIGGER_THRESHOLD_DB
        )
        self._require_readback("wlan_tx_query.trigger_source", VERIFIED_TRIGGER_SOURCE)
        self._require_readback("wlan_tx_query.repetition", VERIFIED_REPETITION_READBACK)
        self._require_readback(
            "wlan_tx_query.modulation_statistic_count",
            VERIFIED_MODULATION_STATISTIC_COUNT,
        )

    def rf_on(self) -> None:
        # 此 profile 是 GPRF Baseband ARB，不是 ARB Sequencer；狀態樹不可混用。
        self._write_checked("generator.rf_on")
        actual_state = self._query("generator_query.state")
        if actual_state != "ON":
            # 狀態 token 是安全判定證據；失敗訊息必須保留實機回值，不能只寫模糊 failed。
            raise RuntimeError(f"Generator RF On readback failed: {actual_state!r}")

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
                # 保存狀態轉換供 artifact 稽核；這不會額外送出 SCPI 或改變儀器狀態。
                self.last_measurement_states = observed.copy()
                return
            if state in {"INV", "OFF"}:
                self.last_measurement_states = observed.copy()
                raise RuntimeError(f"Measurement entered {state}; observed={observed}")
            time.sleep(self.poll_interval_s)
        self.last_measurement_states = observed.copy()
        raise TimeoutError(f"Measurement did not reach RDY; observed={observed}")

    # 5 組已個別驗證過的聚合統計查詢；average 沿用無前綴欄位名稱以維持既有
    # CSV/GUI/real_service.py 相容性，其餘統計加前綴避免欄位衝突。
    RESULT_STATS: tuple[tuple[str, str, str], ...] = (
        ("", "raw", "results.modulation_average"),
        ("current_", "raw_current", "results.modulation_current"),
        ("min_", "raw_minimum", "results.modulation_minimum"),
        ("max_", "raw_maximum", "results.modulation_maximum"),
        ("stddev_", "raw_std_dev", "results.modulation_std_dev"),
    )

    def fetch_result(self) -> dict[str, object]:
        # INITiate 已完成後才使用 FETCh，避免讀到前一次 stale result。
        merged: dict[str, object] = {}
        for field_prefix, raw_key, registry_name in self.RESULT_STATS:
            raw_response = self._query(registry_name)
            parsed = parse_result(raw_response)
            merged[raw_key] = raw_response
            merged.update({f"{field_prefix}{field}": value for field, value in parsed.items()})
        self.raw_result = str(merged["raw"])
        return merged

    def stop_measurement(self) -> None:
        self._write_checked("wlan_tx.stop")

    def rf_off(self) -> None:
        # 此 profile 使用 Baseband ARB；ARB Sequencer 是另一個 state tree。
        # 混送 Sequencer Off 會造成 workspace/profile 漂移，因此只關通用 Generator。
        self._write_checked("generator.rf_off")
        rf_state = self._query("generator_query.state")
        if rf_state != "OFF":
            raise RuntimeError(f"Generator RF Off readback failed: rf={rf_state!r}")

    def drain_error_queue(self) -> list[str]:
        errors: list[str] = []
        for _ in range(50):
            response = self._query("common.system_error")
            if response.startswith("0,") or response.startswith("+0,"):
                return errors
            errors.append(response)
        raise RuntimeError("CMP180 error queue did not terminate")
