"""GPRF power sweep support for instrument capability checks.

This module intentionally uses the CMP180 GPRF generator/measurement apps, not
the WLAN TX EVM workflow. Results are RF power observations and must not be
presented as WLAN demodulation or compliance data.
"""

from __future__ import annotations

import csv
import html
import json
import math
import socket
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from cmp180_evm.results.visualization import write_pandas_matplotlib_plots
from cmp180_evm.scpi.registry import ScpiCommandRegistry, load_scpi_command_map
from cmp180_evm.web.jobs import SweepJob
from cmp180_evm.workflow.frequency_conversion import (
    ConversionPlan,
    ConverterLimits,
    build_converter_limits,
)
from cmp180_evm.workflow.rf_routes import parse_route

GPRF_MIN_FREQUENCY_HZ = 400_000_000.0
GPRF_MAX_FREQUENCY_HZ = 8_000_000_000.0
GPRF_MIN_POWER_DBM = -80.0
# CMP180 generator 最大輸出 +8 dBm（2026-09-09 由現場操作員提供的儀器規格；
# 尚未由 Remote Manual 條目覆核）。規劃上限必須貼齊儀器實際能力，否則會規劃出
# 儀器根本送不出來的功率點，在現場才失敗。
GPRF_MAX_POWER_DBM = 8.0
GPRF_MAX_POINTS = 401
GPRF_MIN_DWELL_MS = 50
GPRF_MAX_DWELL_MS = 5000
# GPRF power 量測需要連續波；突發 ARB 波形會被平均進閒置期而無法解讀。
GPRF_BASEBAND_MODE = "CW"
GPRF_MAX_PATH_COMPENSATION_DB = 120.0
GPRF_MIN_SAFE_LIMIT_DBM = -120.0
GPRF_MAX_SAFE_LIMIT_DBM = 30.0
GPRF_MIN_EXPECTED_POWER_DBM = -30.0
# Converter 類 DUT 是淨損耗，expected_dut_gain_db 必須允許負值，否則規劃階段就填不進去。
GPRF_MIN_DUT_GAIN_DB = -GPRF_MAX_PATH_COMPENSATION_DB
# DUT 輸入損傷上限與 sa_safe_limit_dbm 是兩件事：後者保護 CMP180，前者保護 DUT。
GPRF_MIN_DUT_MAX_INPUT_DBM = -120.0
GPRF_MAX_DUT_MAX_INPUT_DBM = 30.0


@dataclass(frozen=True)
class GprfPreview:
    axis: str
    points: tuple[float, ...]
    frequency_hz: float | None
    power_dbm: float | None
    dwell_ms: int
    execution_allowed: bool
    rejection_reason: str | None = None
    input_cable_loss_db: float = 0.0
    output_cable_loss_db: float = 0.0
    external_gain_db: float = 0.0
    external_attenuation_db: float = 0.0
    output_attenuator_db: float = 0.0
    expected_dut_gain_db: float = 0.0
    sa_safe_limit_dbm: float = 0.0
    dut_max_input_dbm: float | None = None
    # converter 為 None 時 generator 與 analyzer 同頻，維持既有 PA/loopback 行為。
    conversion: ConversionPlan | None = None
    converter_limits: ConverterLimits | None = None

    def point_frequencies_hz(self, value: float) -> tuple[float, float]:
        """Return (generator_hz, analyzer_hz) for one sweep point."""
        frequency_hz = value if self.axis == "frequency" else float(self.frequency_hz)
        if self.conversion is None:
            # 同頻 DUT（PA、直連 loopback）：兩端共用同一個頻率。
            return frequency_hz, frequency_hz
        plan = ConversionPlan.from_generator_frequency(
            generator_frequency_hz=frequency_hz,
            lo_frequency_hz=self.conversion.lo_frequency_hz,
            sideband=self.conversion.sideband,
            direction=self.conversion.direction,
        )
        return plan.generator_frequency_hz, plan.analyzer_frequency_hz

    def public(self) -> dict[str, object]:
        pin_start, pin_stop = _pin_range(
            self,
            start=float(self.points[0]) if self.axis == "power" and self.points else self.power_dbm,
            stop=float(self.points[-1]) if self.axis == "power" and self.points else self.power_dbm,
        )
        return {
            "measurement_family": "GPRF_POWER",
            "axis": self.axis,
            "points": self.points,
            "point_count": len(self.points),
            "frequency_hz": self.frequency_hz,
            "power_dbm": self.power_dbm,
            "dwell_ms": self.dwell_ms,
            "input_cable_loss_db": self.input_cable_loss_db,
            "output_cable_loss_db": self.output_cable_loss_db,
            "external_gain_db": self.external_gain_db,
            "external_attenuation_db": self.external_attenuation_db,
            "output_attenuator_db": self.output_attenuator_db,
            "expected_dut_gain_db": self.expected_dut_gain_db,
            "sa_safe_limit_dbm": self.sa_safe_limit_dbm,
            "dut_max_input_dbm": self.dut_max_input_dbm,
            "conversion": None if self.conversion is None else self.conversion.public(),
            "converter_limits": (
                None if self.converter_limits is None else self.converter_limits.public()
            ),
            "pin_start_dbm": pin_start,
            "pin_stop_dbm": pin_stop,
            "execution_allowed": self.execution_allowed,
            "rejection_reason": self.rejection_reason,
            "rejection_help": _gprf_rejection_help(self.rejection_reason),
            "correct_range": _gprf_correct_range(),
            "disclaimer": (
                "GPRF power sweep only; this is not WLAN EVM demodulation or a "
                "WLAN compliance claim."
            ),
        }


def _gprf_correct_range() -> str:
    return (
        f"Frequency {GPRF_MIN_FREQUENCY_HZ / 1e6:.0f} MHz.."
        f"{GPRF_MAX_FREQUENCY_HZ / 1e9:.0f} GHz; generator power "
        f"{GPRF_MIN_POWER_DBM:g}..{GPRF_MAX_POWER_DBM:g} dBm; dwell "
        f"{GPRF_MIN_DWELL_MS}..{GPRF_MAX_DWELL_MS} ms; max {GPRF_MAX_POINTS} points."
    )


def _gprf_rejection_help(reason: str | None) -> str | None:
    if not reason:
        return None
    if "Frequency" in reason:
        return "Set every RF point inside the CMP180 GPRF planning range, then review again."
    if "power" in reason.lower():
        return "Reduce the generator level or sweep endpoints to the accepted GPRF power range."
    if "dwell" in reason.lower():
        return "Use a dwell time that is long enough for settling but inside the approved UI guard."
    return "Adjust the highlighted plan field and review again before enabling RF."


def _inclusive_points(start: float, stop: float, step: float) -> tuple[float, ...]:
    if step <= 0 or stop < start:
        raise ValueError("Stop must follow start and step must be positive")
    count = int((stop - start) // step) + 1
    if count > GPRF_MAX_POINTS:
        raise ValueError(f"GPRF preview exceeds {GPRF_MAX_POINTS} points")
    return tuple(round(start + index * step, 9) for index in range(count))


def _bounded_float(
    data: dict[str, object],
    name: str,
    default: float,
    *,
    minimum: float,
    maximum: float,
) -> float:
    value = float(data.get(name, default))
    if not minimum <= value <= maximum:
        raise ValueError(f"{name} must stay within {minimum:g}..{maximum:g}")
    return value


def _path_compensation(data: dict[str, object]) -> dict[str, float]:
    # PA 參考面補償只影響輸出 artifact 的 Pin/Pout/Gain，不放寬 RF 或儀器安全範圍。
    return {
        "input_cable_loss_db": _bounded_float(
            data,
            "input_cable_loss_db",
            0.0,
            minimum=0.0,
            maximum=GPRF_MAX_PATH_COMPENSATION_DB,
        ),
        "output_cable_loss_db": _bounded_float(
            data,
            "output_cable_loss_db",
            0.0,
            minimum=0.0,
            maximum=GPRF_MAX_PATH_COMPENSATION_DB,
        ),
        "external_gain_db": _bounded_float(
            data,
            "external_gain_db",
            0.0,
            minimum=0.0,
            maximum=GPRF_MAX_PATH_COMPENSATION_DB,
        ),
        "external_attenuation_db": _bounded_float(
            data,
            "external_attenuation_db",
            0.0,
            minimum=0.0,
            maximum=GPRF_MAX_PATH_COMPENSATION_DB,
        ),
        "output_attenuator_db": _bounded_float(
            data,
            "output_attenuator_db",
            float(data.get("external_attenuation_db", 0.0)),
            minimum=0.0,
            maximum=GPRF_MAX_PATH_COMPENSATION_DB,
        ),
        "expected_dut_gain_db": _bounded_float(
            data,
            "expected_dut_gain_db",
            0.0,
            minimum=GPRF_MIN_DUT_GAIN_DB,
            maximum=GPRF_MAX_PATH_COMPENSATION_DB,
        ),
        "sa_safe_limit_dbm": _bounded_float(
            data,
            "sa_safe_limit_dbm",
            0.0,
            minimum=GPRF_MIN_SAFE_LIMIT_DBM,
            maximum=GPRF_MAX_SAFE_LIMIT_DBM,
        ),
    }


def _pin_dbm(generator_power_dbm: float, external_gain_db: float, input_loss_db: float) -> float:
    return generator_power_dbm + external_gain_db - input_loss_db


def _pin_range(
    preview: GprfPreview,
    *,
    start: float | None,
    stop: float | None,
) -> tuple[float | None, float | None]:
    if start is None or stop is None:
        return None, None
    return (
        _pin_dbm(start, preview.external_gain_db, preview.input_cable_loss_db),
        _pin_dbm(stop, preview.external_gain_db, preview.input_cable_loss_db),
    )


def _dut_max_input_dbm(data: dict[str, object]) -> float | None:
    raw = data.get("dut_max_input_dbm")
    if raw is None or raw == "":
        return None
    value = float(raw)
    if not GPRF_MIN_DUT_MAX_INPUT_DBM <= value <= GPRF_MAX_DUT_MAX_INPUT_DBM:
        raise ValueError(
            f"dut_max_input_dbm must stay within {GPRF_MIN_DUT_MAX_INPUT_DBM:g}.."
            f"{GPRF_MAX_DUT_MAX_INPUT_DBM:g}"
        )
    return value


def _dut_input_rejection(
    *,
    max_generator_power_dbm: float,
    compensation: dict[str, float],
    dut_max_input_dbm: float | None,
) -> str | None:
    """Protect the DUT itself; sa_safe_limit_dbm only ever protects the CMP180 analyzer."""
    if dut_max_input_dbm is None:
        # 一旦宣告了 DUT 增益／損耗就代表路徑上有 DUT，必須同時說明它的輸入上限。
        if compensation["expected_dut_gain_db"] != 0.0:
            return (
                "dut_max_input_dbm is required once expected_dut_gain_db declares a DUT in the "
                "path; state the DUT input damage limit before planning RF"
            )
        return None
    pin_dbm = _pin_dbm(
        max_generator_power_dbm,
        compensation["external_gain_db"],
        compensation["input_cable_loss_db"],
    )
    if pin_dbm > dut_max_input_dbm:
        return (
            f"Worst-case DUT input {pin_dbm:g} dBm exceeds the declared DUT limit "
            f"{dut_max_input_dbm:g} dBm"
        )
    return None


def _conversion_request(
    data: dict[str, object],
) -> tuple[dict[str, object] | None, ConverterLimits | None]:
    raw = data.get("conversion")
    if not raw:
        return None, None
    if not isinstance(raw, dict):
        raise ValueError("GPRF conversion must be an object")
    settings = {
        "direction": str(raw.get("direction") or "up"),
        "sideband": str(raw.get("sideband") or "high"),
        "lo_frequency_hz": float(raw["lo_frequency_hz"]),
    }
    return settings, build_converter_limits(raw.get("limits"))


def _conversion_rejection(
    *,
    generator_frequencies_hz: tuple[float, ...],
    settings: dict[str, object],
    limits: ConverterLimits,
) -> str | None:
    # 每個掃描點都要重新解一次 IF/RF；只驗端點會漏掉中間落出 DUT 範圍的頻率。
    for generator_hz in generator_frequencies_hz:
        plan = ConversionPlan.from_generator_frequency(
            generator_frequency_hz=generator_hz,
            lo_frequency_hz=float(settings["lo_frequency_hz"]),
            sideband=str(settings["sideband"]),
            direction=str(settings["direction"]),
        )
        errors = plan.validate(limits)
        if errors:
            return "; ".join(errors)
    return None


def _representative_conversion(
    settings: dict[str, object] | None,
    generator_frequency_hz: float | None,
) -> ConversionPlan | None:
    if settings is None or generator_frequency_hz is None:
        return None
    return ConversionPlan.from_generator_frequency(
        generator_frequency_hz=generator_frequency_hz,
        lo_frequency_hz=float(settings["lo_frequency_hz"]),
        sideband=str(settings["sideband"]),
        direction=str(settings["direction"]),
    )


def build_gprf_power_preview(data: dict[str, object]) -> GprfPreview:
    axis = str(data.get("axis") or "frequency")
    dwell_ms = int(float(data.get("dwell_ms", 200)))
    if not GPRF_MIN_DWELL_MS <= dwell_ms <= GPRF_MAX_DWELL_MS:
        raise ValueError(f"GPRF dwell must stay within {GPRF_MIN_DWELL_MS}..{GPRF_MAX_DWELL_MS} ms")
    compensation = _path_compensation(data)
    dut_max_input_dbm = _dut_max_input_dbm(data)
    conversion_settings, converter_limits = _conversion_request(data)
    if axis == "frequency":
        start_hz = float(data["start_hz"])
        stop_hz = float(data["stop_hz"])
        step_hz = float(data["step_hz"])
        power_dbm = float(data.get("power_dbm", -40.0))
        points = _inclusive_points(start_hz, stop_hz, step_hz)
        reason = None
        if min(points) < GPRF_MIN_FREQUENCY_HZ or max(points) > GPRF_MAX_FREQUENCY_HZ:
            reason = "Frequency exceeds CMP180 GPRF planning range 400 MHz..8 GHz"
        elif not GPRF_MIN_POWER_DBM <= power_dbm <= GPRF_MAX_POWER_DBM:
            reason = (
                f"Generator power must stay within {GPRF_MIN_POWER_DBM:g}.."
                f"{GPRF_MAX_POWER_DBM:g} dBm"
            )
        elif conversion_settings is not None and converter_limits is not None:
            reason = _conversion_rejection(
                generator_frequencies_hz=points,
                settings=conversion_settings,
                limits=converter_limits,
            )
        if reason is None:
            reason = _dut_input_rejection(
                max_generator_power_dbm=power_dbm,
                compensation=compensation,
                dut_max_input_dbm=dut_max_input_dbm,
            )
        return GprfPreview(
            axis,
            points,
            None,
            power_dbm,
            dwell_ms,
            reason is None,
            reason,
            **compensation,
            dut_max_input_dbm=dut_max_input_dbm,
            conversion=_representative_conversion(conversion_settings, points[0] if points else None),
            converter_limits=converter_limits,
        )
    if axis == "power":
        frequency_hz = float(data["frequency_hz"])
        start_dbm = float(data["start_dbm"])
        stop_dbm = float(data["stop_dbm"])
        step_dbm = float(data["step_dbm"])
        points = _inclusive_points(start_dbm, stop_dbm, step_dbm)
        reason = None
        if not GPRF_MIN_FREQUENCY_HZ <= frequency_hz <= GPRF_MAX_FREQUENCY_HZ:
            reason = "Frequency exceeds CMP180 GPRF planning range 400 MHz..8 GHz"
        elif min(points) < GPRF_MIN_POWER_DBM or max(points) > GPRF_MAX_POWER_DBM:
            reason = (
                f"Power sweep exceeds {GPRF_MIN_POWER_DBM:g}.."
                f"{GPRF_MAX_POWER_DBM:g} dBm planning range"
            )
        elif conversion_settings is not None and converter_limits is not None:
            reason = _conversion_rejection(
                generator_frequencies_hz=(frequency_hz,),
                settings=conversion_settings,
                limits=converter_limits,
            )
        if reason is None:
            # Power sweep 的最壞情況是最高一點；DUT 保護必須用它，不是起始點。
            reason = _dut_input_rejection(
                max_generator_power_dbm=max(points),
                compensation=compensation,
                dut_max_input_dbm=dut_max_input_dbm,
            )
        return GprfPreview(
            axis,
            points,
            frequency_hz,
            None,
            dwell_ms,
            reason is None,
            reason,
            **compensation,
            dut_max_input_dbm=dut_max_input_dbm,
            conversion=_representative_conversion(conversion_settings, frequency_hz),
            converter_limits=converter_limits,
        )
    raise ValueError("GPRF axis must be 'frequency' or 'power'")


class GprfSocket:
    def __init__(self, registry: ScpiCommandRegistry) -> None:
        self.registry = registry
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10.0)

    def connect(self) -> None:
        self.sock.connect(("192.168.200.50", 5025))

    def close(self) -> None:
        self.sock.close()

    def write(self, command: str) -> None:
        self.sock.sendall((command.strip() + "\n").encode("utf-8"))

    def query(self, command: str) -> str:
        self.write(command)
        chunks: list[bytes] = []
        while True:
            chunk = self.sock.recv(4096)
            chunks.append(chunk)
            if chunk.endswith(b"\n") or not chunk:
                break
        return b"".join(chunks).decode("utf-8", errors="ignore").strip()


def _drain_error_queue(
    conn: GprfSocket,
    registry: ScpiCommandRegistry,
    *,
    limit: int = 20,
) -> list[str]:
    """Read `SYST:ERR?` until the instrument reports an empty queue."""
    # SCPI error queue 必須讀到 `0,"No error"` 才算清空；設上限避免儀器異常時無限迴圈。
    entries: list[str] = []
    command = registry.require("common.system_error")
    for _ in range(limit):
        try:
            response = conn.query(command).strip()
        except Exception as exc:  # 讀取失敗本身就是證據，不可靜默吞掉
            entries.append(f"ERROR_QUEUE_READ_FAILED: {exc}")
            break
        if not response or response.startswith("0,"):
            break
        entries.append(response)
    return entries


def _select_cw_baseband(conn: GprfSocket, registry: ScpiCommandRegistry) -> tuple[str, str]:
    """Switch the generator to CW; returns the original (baseband mode, ARB file)."""
    # GPRF power 量測必須用 CW：突發 WLAN ARB 波形會讓功率計把閒置期一起平均，
    # 實測比 WLAN analyzer 的 burst power 低約 15.8 dB。切換只可在 RF OFF 時進行。
    original_mode = conn.query(registry.require("generator_query.baseband_mode")).strip()
    original_arb = conn.query(registry.require("generator_query.arb_file_absolute")).strip()
    if original_mode != GPRF_BASEBAND_MODE:
        conn.write(registry.render("generator.set_baseband_mode", mode=GPRF_BASEBAND_MODE))
        conn.query(registry.require("common.operation_complete"))
        errors = _drain_error_queue(conn, registry)
        if errors:
            raise RuntimeError(f"Switching the generator to CW reported {errors}")
        readback = conn.query(registry.require("generator_query.baseband_mode")).strip()
        if readback != GPRF_BASEBAND_MODE:
            raise RuntimeError(f"Generator baseband mode readback {readback!r} is not CW")
    return original_mode, original_arb


def _restore_baseband(
    conn: GprfSocket,
    registry: ScpiCommandRegistry,
    original_mode: str,
    original_arb: str | None,
) -> list[str]:
    """Restore the generator baseband mode and ARB selection; returns any mismatches."""
    # WLAN campaign 依賴原本選取的 ARB waveform，收尾必須還原並逐項 read-back 確認。
    problems: list[str] = []
    if original_mode and original_mode != GPRF_BASEBAND_MODE:
        conn.write(registry.render("generator.set_baseband_mode", mode=original_mode))
        conn.query(registry.require("common.operation_complete"))
        readback = conn.query(registry.require("generator_query.baseband_mode")).strip()
        if readback != original_mode:
            problems.append(
                f"BASEBAND_MODE_RESTORE_MISMATCH: expected {original_mode}, got {readback}"
            )
    if original_arb:
        restored = conn.query(registry.require("generator_query.arb_file_absolute")).strip()
        if restored != original_arb:
            # 切換 baseband 可能清除選取；用已驗證的 setter 重新指定同一個檔案。
            conn.write(
                registry.render("generator.set_arb_file", arb_file=original_arb.strip('"'))
            )
            conn.query(registry.require("common.operation_complete"))
            restored = conn.query(registry.require("generator_query.arb_file_absolute")).strip()
        if restored != original_arb:
            problems.append(f"ARB_RESTORE_MISMATCH: expected {original_arb}, got {restored}")
    return problems


def _parse_power(response: str) -> tuple[int, float | None]:
    try:
        parts = response.strip().split(",")
        reliability = int(float(parts[0]))
        value = float(parts[1]) if len(parts) > 1 else None
        # 缺值與非有限數不是有效功率；讓呼叫端停止升功率，不能以 OK 繼續掃描。
        if value is None or not math.isfinite(value):
            return -1, None
        return reliability, value
    except (IndexError, ValueError, OverflowError):
        return -1, None


def _pout_dbm(
    measured_power_dbm: float | None,
    output_loss_db: float,
    attenuation_db: float,
) -> float | None:
    if measured_power_dbm is None:
        return None
    return measured_power_dbm + output_loss_db + attenuation_db


def _point_pa_metrics(
    *,
    generator_power_dbm: float,
    measured_power_dbm: float | None,
    preview: GprfPreview,
) -> dict[str, float | None]:
    # Pin/Pout 以 DUT 參考面計算；這是 PA 圖表用欄位，不回寫儀器 expected power。
    pin_dbm = _pin_dbm(
        generator_power_dbm,
        preview.external_gain_db,
        preview.input_cable_loss_db,
    )
    pout_dbm = _pout_dbm(
        measured_power_dbm,
        preview.output_cable_loss_db,
        preview.output_attenuator_db,
    )
    return {
        "pin_dbm": pin_dbm,
        "pout_dbm": pout_dbm,
        "gain_db": None if pout_dbm is None else pout_dbm - pin_dbm,
    }


def _should_stop_after_gprf_point(status: str) -> bool:
    # SCPI/ranging/SA limit 異常代表量測條件已不可信；PA sweep 必須在 RF Off 邊界停止。
    return status != "OK"


def _expected_analyzer_power_dbm(generator_power_dbm: float, preview: GprfPreview) -> float:
    # CMP180 ENPower 是 RF1.5 量測端 ranging，不是 DUT Pout；實體輸出衰減只進安全估算。
    estimated_input = (
        generator_power_dbm
        + preview.external_gain_db
        - preview.input_cable_loss_db
        + preview.expected_dut_gain_db
        - preview.output_cable_loss_db
        - preview.output_attenuator_db
    )
    return max(estimated_input, GPRF_MIN_EXPECTED_POWER_DBM)


def _analyze_p1db(points: list[dict[str, object]], *, small_signal_points: int = 3) -> dict[str, object]:
    valid = [
        point
        for point in points
        if point.get("valid") is True
        and isinstance(point.get("pin_dbm"), (int, float))
        and isinstance(point.get("pout_dbm"), (int, float))
        and isinstance(point.get("gain_db"), (int, float))
        # 離線匯入也可能含 NaN/Inf；不得污染基準或 P1dB 插值。
        and all(math.isfinite(float(point[key])) for key in ("pin_dbm", "pout_dbm", "gain_db"))
    ]
    valid.sort(key=lambda point: float(point["pin_dbm"]))
    if len(valid) < 2:
        return {"status": "insufficient_points", "small_signal_gain_db": None}
    # 小訊號增益用最低 Pin 的前幾點平均；避免單點雜訊直接決定 P1dB 門檻。
    baseline_count = max(1, min(small_signal_points, len(valid)))
    small_signal_gain = sum(float(point["gain_db"]) for point in valid[:baseline_count]) / baseline_count
    target_gain = small_signal_gain - 1.0
    compressions = [small_signal_gain - float(point["gain_db"]) for point in valid]
    max_compression = max(compressions)
    max_pin_point = max(valid, key=lambda point: float(point["pin_dbm"]))
    # 壓縮後 Pout 可能回落；最大輸出與最大輸入必須分別搜尋。
    max_pout = max(float(point["pout_dbm"]) for point in valid)
    previous = valid[0]
    for point in valid[1:]:
        previous_gain = float(previous["gain_db"])
        current_gain = float(point["gain_db"])
        if previous_gain >= target_gain >= current_gain:
            span = previous_gain - current_gain
            ratio = 0.0 if span == 0 else (previous_gain - target_gain) / span
            pin = float(previous["pin_dbm"]) + ratio * (
                float(point["pin_dbm"]) - float(previous["pin_dbm"])
            )
            pout = float(previous["pout_dbm"]) + ratio * (
                float(point["pout_dbm"]) - float(previous["pout_dbm"])
            )
            return {
                "status": "found",
                "small_signal_gain_db": small_signal_gain,
                "target_gain_db": target_gain,
                "ip1db_dbm": pin,
                "op1db_dbm": pout,
                "max_compression_db": max_compression,
                "max_measured_pin_dbm": float(max_pin_point["pin_dbm"]),
                "max_measured_pout_dbm": max_pout,
            }
        previous = point
    return {
        "status": "not_found",
        "small_signal_gain_db": small_signal_gain,
        "target_gain_db": target_gain,
        "max_compression_db": max_compression,
        "max_measured_pin_dbm": float(max_pin_point["pin_dbm"]),
        "max_measured_pout_dbm": max_pout,
    }


def _save_gprf_result(
    points: list[dict[str, object]],
    output_root: Path,
    metadata: dict[str, object],
) -> dict[str, str]:
    now = datetime.now(UTC)
    run_id = uuid.uuid4().hex[:10]
    run_dir = output_root / f"{now.strftime('%Y%m%dT%H%M%SZ')}_gprf-power-sweep_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=False)
    csv_path = run_dir / "results.csv"
    fieldnames = list(points[0]) if points else ["point_index", "status"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(points)
    json_path = run_dir / "results.json"
    json_path.write_text(json.dumps(points, indent=2), encoding="utf-8")
    metadata_path = run_dir / "metadata.json"
    payload = {
        "run_id": run_id,
        "test_name": "gprf-power-sweep",
        "created_at": now.isoformat(),
        "simulated": False,
        "status": "complete",
        # Run History 只讀 metadata 摘要；GPRF 沒有 EVM completed counter，
        # 因此在保存時直接寫入點數，避免畫面誤顯示 0 點。
        "completed_points": len(points),
        "point_count": len(points),
        "source": "web_gprf_power_sweep",
        "measurement_family": "GPRF_POWER",
        "compliance_claim": False,
        **metadata,
    }
    metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    headers = "".join(f"<th>{html.escape(str(name))}</th>" for name in fieldnames)
    rows = "".join(
        "<tr>"
        + "".join(
            f"<td>{html.escape(str(row.get(name, '')))}</td>" for name in fieldnames
        )
        + "</tr>"
        for row in points
    )
    report_path = run_dir / "report.html"
    report_path.write_text(
        "<!doctype html><html lang='zh-Hant'><meta charset='utf-8'>"
        "<title>CMP180 GPRF Power Sweep</title>"
        "<style>body{font:14px system-ui;margin:32px;color:#172033}"
        "table{border-collapse:collapse;width:100%}"
        "th,td{padding:8px;border-bottom:1px solid #ddd;text-align:left}"
        "th{background:#f4f7fb}</style>"
        "<h1>CMP180 GPRF Power Sweep</h1>"
        "<p>GPRF power only; not WLAN EVM demodulation or compliance.</p>"
        f"<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>",
        encoding="utf-8",
    )
    # GPRF 結果走獨立保存流程；這裡補上與 WLAN artifacts 相同的 Pandas/Matplotlib PNG，
    # 讓「結果與圖表」不會因 workflow 不同而缺少靜態報告圖。
    matplotlib_artifacts = {
        f"matplotlib_{path.stem}": str(path.resolve())
        for path in write_pandas_matplotlib_plots(csv_path)
    }
    return {
        "run_id": run_id,
        "run_dir": str(run_dir.resolve()),
        "csv": str(csv_path.resolve()),
        "json": str(json_path.resolve()),
        "metadata": str(metadata_path.resolve()),
        "report": str(report_path.resolve()),
        **matplotlib_artifacts,
    }


def run_gprf_power_sweep(
    job: SweepJob,
    *,
    request: dict[str, object],
    output_root: Path,
) -> dict[str, object]:
    preview = build_gprf_power_preview(request)
    if not preview.execution_allowed:
        raise ValueError(preview.rejection_reason or "GPRF plan is blocked")
    registry = load_scpi_command_map(Path("configs/scpi_command_map.yaml"))
    conn = GprfSocket(registry)
    rows: list[dict[str, object]] = []
    # 回傳結果在 finally 完成後才交付；收尾讀回與保存結果必須同步。
    cleanup_errors: list[str] = []
    artifacts: dict[str, str] | None = None
    result: dict[str, object] = {}
    original_baseband_mode: str | None = None
    original_arb_file: str | None = None
    stopped_reason: str | None = None
    try:
        conn.connect()
        conn.write(registry.require("common.clear_status"))
        # 先切 CW 再設定 routing／位準，全部都在 RF Off 下完成。
        original_baseband_mode, original_arb_file = _select_cw_baseband(conn, registry)
        # 量測端 routing 與位準必須在 RF Off 時先寫入並 read-back：run 252bbbe39a 因為
        # GPRF measurement 停在未接線的 RF1.6，才會在送出 -40 dBm 時讀到雜訊底 -80.87 dBm。
        route = parse_route(request.get("cable_confirmation"))
        external_attenuation_db = preview.external_attenuation_db
        conn.write(
            registry.render("gprf_measurement.set_rf_path", rf_path=f'"{route.analyzer_port}"')
        )
        conn.write(
            registry.render(
                "gprf_measurement.set_external_attenuation",
                external_attenuation_db=external_attenuation_db,
            )
        )
        conn.query(registry.require("common.operation_complete"))
        setup_errors = _drain_error_queue(conn, registry)
        if setup_errors:
            raise RuntimeError(f"GPRF measurement setup reported {setup_errors}")
        rf_path_readback = conn.query(registry.require("gprf_measurement_query.rf_path")).strip()
        if rf_path_readback.strip('"').upper() != route.analyzer_port:
            raise RuntimeError(
                f"GPRF measurement RF path readback {rf_path_readback!r} does not match the "
                f"confirmed cable route analyzer port {route.analyzer_port}"
            )
        # GPRF 模式會開真實 RF；每個設定點都在 job 邊界檢查取消，finally 仍會關 RF。
        for index, value in enumerate(preview.points):
            if job.is_cancel_requested():
                break
            generator_frequency_hz, analyzer_frequency_hz = preview.point_frequencies_hz(value)
            # frequency_hz 沿用 generator 端，維持既有 artifact 與圖表的掃描軸語意。
            frequency_hz = generator_frequency_hz
            power_dbm = float(preview.power_dbm) if preview.axis == "frequency" else value
            expected_power_dbm = _expected_analyzer_power_dbm(power_dbm, preview)
            # Converter DUT 的輸入與輸出不同頻；兩端寫同一個頻率只會讓 analyzer 停在底噪。
            conn.write(
                registry.render("generator.set_frequency", frequency_hz=generator_frequency_hz)
            )
            conn.write(
                registry.render(
                    "gprf_measurement.set_frequency", frequency_hz=analyzer_frequency_hz
                )
            )
            conn.write(registry.render("generator.set_power", power_dbm=power_dbm))
            # expected nominal power 決定 RF1.5 ranging；PA profile 需用預估輸入且避開儀器下限。
            conn.write(
                registry.render(
                    "gprf_measurement.set_expected_power", expected_power_dbm=expected_power_dbm
                )
            )
            conn.write(registry.require("generator.rf_on"))
            time.sleep(preview.dwell_ms / 1000)
            conn.write(registry.require("gprf_measurement.initiate_power"))
            time.sleep(preview.dwell_ms / 1000)
            raw = conn.query(registry.require("gprf_measurement_query.power_current"))
            # 每點量測完立即收尾：先停量測再關 RF，讓下一點的設定同樣在 RF Off 下完成。
            conn.write(registry.require("gprf_measurement.stop_power"))
            conn.write(registry.require("generator.rf_off"))
            reliability, measured = _parse_power(raw)
            pa_metrics = _point_pa_metrics(
                generator_power_dbm=power_dbm,
                measured_power_dbm=measured,
                preview=preview,
            )
            # 每點都讀 error queue（涵蓋量測與收尾）：儀器已回報錯誤時不得標記為有效量測。
            point_errors = _drain_error_queue(conn, registry)
            if point_errors:
                status = "SCPI_ERROR"
            elif reliability != 0:
                status = f"RELIABILITY_{reliability}"
            elif measured is not None and measured > preview.sa_safe_limit_dbm:
                status = "SA_LIMIT"
            else:
                status = "OK"
            valid = (
                reliability == 0
                and measured is not None
                and measured <= preview.sa_safe_limit_dbm
                and not point_errors
            )
            row = {
                "point_index": index,
                "frequency_hz": frequency_hz,
                "generator_frequency_hz": generator_frequency_hz,
                "analyzer_frequency_hz": analyzer_frequency_hz,
                "generator_power_dbm": power_dbm,
                "analyzer_port": route.analyzer_port,
                "expected_power_dbm": expected_power_dbm,
                "external_attenuation_db": external_attenuation_db,
                "output_attenuator_db": preview.output_attenuator_db,
                "expected_dut_gain_db": preview.expected_dut_gain_db,
                "input_cable_loss_db": preview.input_cable_loss_db,
                "output_cable_loss_db": preview.output_cable_loss_db,
                "external_gain_db": preview.external_gain_db,
                "sa_safe_limit_dbm": preview.sa_safe_limit_dbm,
                "pin_dbm": pa_metrics["pin_dbm"],
                "pout_dbm": pa_metrics["pout_dbm"],
                "gain_db": pa_metrics["gain_db"],
                "baseband_mode": GPRF_BASEBAND_MODE,
                "measured_power_dbm": measured,
                "evm_all_db": None,
                "evm_data_db": None,
                "evm_pilot_db": None,
                "burst_power_dbm": measured,
                "frequency_error_hz": None,
                "valid": valid,
                "limit_status": "MEASURED" if valid else "INVALID",
                "reliability": reliability,
                "raw_power_current": raw,
                "error_queue": "; ".join(point_errors),
                "status": status,
                "measurement_family": "GPRF_POWER",
            }
            rows.append(row)
            job.point_completed(index + 1, row)
            if _should_stop_after_gprf_point(status):
                stopped_reason = status
                break
        p1db = _analyze_p1db(rows) if preview.axis == "power" else {"status": "frequency_sweep"}
        completed = len(rows) == len(preview.points) and stopped_reason is None
        artifacts = _save_gprf_result(
            rows,
            output_root,
            {
                "status": "complete" if completed else "partial",
                "axis": preview.axis,
                "requested_points": preview.points,
                "completed_requested_points": len(rows),
                "stopped_reason": stopped_reason,
                "dwell_ms": preview.dwell_ms,
                "cable_route": route.label,
                "analyzer_port": route.analyzer_port,
                "external_attenuation_db": external_attenuation_db,
                "output_attenuator_db": preview.output_attenuator_db,
                "expected_dut_gain_db": preview.expected_dut_gain_db,
                "input_cable_loss_db": preview.input_cable_loss_db,
                "output_cable_loss_db": preview.output_cable_loss_db,
                "external_gain_db": preview.external_gain_db,
                "sa_safe_limit_dbm": preview.sa_safe_limit_dbm,
                "dut_max_input_dbm": preview.dut_max_input_dbm,
                # Converter 的 LO／sideband 決定了 analyzer 停在哪裡，必須隨 artifact 留存。
                "conversion": None if preview.conversion is None else preview.conversion.public(),
                "converter_limits": (
                    None if preview.converter_limits is None else preview.converter_limits.public()
                ),
                "p1db": p1db,
                "baseband_mode": GPRF_BASEBAND_MODE,
                "original_baseband_mode": original_baseband_mode,
                "restored_baseband_mode": None,
                "cleanup_pending": True,
            },
        )
        result = {
            "simulated": False,
            "sweep_axis": preview.axis,
            "measurement_family": "GPRF_POWER",
            "points": rows,
            "p1db": p1db,
            "artifacts": artifacts,
            "cleanup_errors": cleanup_errors,
            "partial": not completed,
            "stopped_reason": stopped_reason,
            "compliance_claim": False,
        }
        return result
    finally:
        # GPRF cleanup 只碰 GPRF power lifecycle 與 generator RF state，不碰 WLAN state tree。
        try:
            conn.write(registry.require("gprf_measurement.stop_power"))
        except Exception as exc:
            cleanup_errors.append(f"STOP_FAILED: {exc}")
        try:
            conn.write(registry.require("generator.rf_off"))
        except Exception as exc:
            cleanup_errors.append(f"RF_OFF_FAILED: {exc}")
        finally:
            # RF 關閉後才還原 baseband；還原失敗必須留成證據，不得靜默吞掉。
            try:
                if original_baseband_mode is not None:
                    cleanup_errors.extend(
                        _restore_baseband(
                            conn, registry, original_baseband_mode, original_arb_file
                        )
                    )
            except Exception as exc:
                cleanup_errors.append(f"BASEBAND_RESTORE_FAILED: {exc}")
            # 必須讀回實際狀態；原始 mode 只是還原目標，不能預先宣稱還原成功。
            final_cleanup: dict[str, object] = {
                "final_rf_state": None,
                "restored_baseband_mode": None,
                "measurement_stop_attempted": True,
                # Registry 尚無已驗證 GPRF state query，不能把 STOP 寫入當成狀態讀回。
                "final_measurement_state": None,
                "measurement_state_verified": False,
                "cleanup_errors": cleanup_errors,
            }
            for key, command in (
                ("final_rf_state", "generator_query.state"),
                ("restored_baseband_mode", "generator_query.baseband_mode"),
            ):
                try:
                    final_cleanup[key] = conn.query(registry.require(command)).strip().strip('"')
                except Exception as exc:
                    cleanup_errors.append(f"{key.upper()}_QUERY_FAILED: {exc}")
            if final_cleanup["final_rf_state"] != "OFF":
                cleanup_errors.append("FINAL_RF_OFF_NOT_CONFIRMED")
            # 收尾後再讀一次 error queue 留存證據；讀取失敗不得遮蔽原始錯誤，也不得跳過 close。
            try:
                cleanup_errors.extend(_drain_error_queue(conn, registry))
            except Exception as exc:
                cleanup_errors.append(f"ERROR_QUEUE_QUERY_FAILED: {exc}")
            try:
                conn.close()
            except Exception as exc:
                cleanup_errors.append(f"CONNECTION_CLOSE_FAILED: {exc}")
            result["final_cleanup"] = final_cleanup
            if cleanup_errors:
                result["partial"] = True
                result["stopped_reason"] = "CLEANUP_ERROR"
            if artifacts is not None:
                # 先前保存的資料仍保留；僅在收尾完成後原子更新 metadata 的最終安全證據。
                metadata_path = Path(artifacts["metadata"])
                payload = json.loads(metadata_path.read_text(encoding="utf-8"))
                payload.update(final_cleanup)
                payload["final_cleanup"] = final_cleanup
                payload["cleanup_pending"] = False
                if cleanup_errors:
                    payload["status"] = "partial"
                    payload["stopped_reason"] = "CLEANUP_ERROR"
                temporary = metadata_path.with_suffix(".json.tmp")
                temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
                temporary.replace(metadata_path)
