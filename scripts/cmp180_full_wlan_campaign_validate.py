"""Run every installed EHT bandwidth over its valid 2.4/5/6 GHz WLAN sections."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from cmp180_evm.results.artifacts import save_frequency_sweep_result, save_single_result
from cmp180_evm.results.validity import invalid_critical_fields
from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.analyzer_setter_validation import ALLOWED_IDLE_MEASUREMENT_STATES
from cmp180_evm.workflow.cmp180_single_backend import Cmp180SingleMeasurementBackend
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan, run_single_measurement

if TYPE_CHECKING:
    from RsInstrument import RsInstrument

WAVEFORM_ROOT = "/home/instrument/fw/data/waveform/WLAN"


@dataclass(frozen=True)
class Section:
    band: str
    bandwidth_mhz: int
    frequencies_mhz: tuple[int, ...]
    waveform: str

    @property
    def key(self) -> str:
        return f"{self.band}-bw{self.bandwidth_mhz}"


def _range(start: int, stop: int, step: int) -> tuple[int, ...]:
    return tuple(range(start, stop + 1, step))


WAVEFORMS = {
    20: "KV352_lib8_WLAN_11be_EHT_MU_BW20_4xLTF_GI32_MCS11_LEN4096_LDPC.wv",
    40: "KV352_lib8_WLAN_11be_EHT_MU_BW40_4xLTF_GI32_MCS11_LEN4096_LDPC.wv",
    80: "KV352_lib8_WLAN_11be_EHT_MU_BW80_4xLTF_GI32_MCS11_LEN4096_LDPC.wv",
    160: "KV352_lib8_WLAN_11be_EHT_MU_BW160_4xLTF_GI32_MCS11_LEN4096_LDPC.wv",
    320: "KV352_lib8_WLAN_11be_EHT_MU_BW320-1_4xLTF_GI32_MCS11_LEN4096_LDPC.wv",
}

# 只使用標準 WLAN channel center；不把 400 MHz–8 GHz 的非 WLAN 空白區偽裝成 EVM 區段。
SECTIONS = (
    Section("2.4GHz", 20, _range(2412, 2472, 5), WAVEFORMS[20]),
    Section("2.4GHz", 40, (2422, 2442, 2462), WAVEFORMS[40]),
    Section(
        "5GHz",
        20,
        (5180, 5200, 5220, 5240, 5260, 5280, 5300, 5320, 5500, 5520, 5540,
         5560, 5580, 5600, 5620, 5640, 5660, 5680, 5700, 5720, 5745, 5765,
         5785, 5805, 5825),
        WAVEFORMS[20],
    ),
    Section(
        "5GHz",
        40,
        (5190, 5230, 5270, 5310, 5510, 5550, 5590, 5630, 5670, 5710, 5755, 5795),
        WAVEFORMS[40],
    ),
    Section("5GHz", 80, (5210, 5290, 5530, 5610, 5690, 5775), WAVEFORMS[80]),
    Section("5GHz", 160, (5250, 5570), WAVEFORMS[160]),
    Section("6GHz", 20, _range(5955, 7115, 20), WAVEFORMS[20]),
    Section("6GHz", 40, _range(5965, 7085, 40), WAVEFORMS[40]),
    Section("6GHz", 80, _range(5985, 7025, 80), WAVEFORMS[80]),
    Section("6GHz", 160, _range(6025, 6985, 160), WAVEFORMS[160]),
    Section("6GHz", 320, _range(6105, 6905, 160), WAVEFORMS[320]),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", default="TCPIP::192.168.200.50::5025::SOCKET")
    parser.add_argument("--command-map", type=Path, default=Path("configs/scpi_command_map.yaml"))
    parser.add_argument("--output-root", type=Path, default=Path("output"))
    parser.add_argument("--confirm-direct-cable", action="store_true")
    parser.add_argument("--confirm-no-attenuator", action="store_true")
    parser.add_argument("--confirm-operator-present", action="store_true")
    parser.add_argument("--confirm-full-wlan-campaign", action="store_true")
    parser.add_argument(
        "--section",
        action="append",
        choices=[section.key for section in SECTIONS],
        help="Run only the named section; repeat to resume selected failed sections.",
    )
    return parser.parse_args()


def selected_sections(names: list[str] | None) -> tuple[Section, ...]:
    """Return all sections by default, or the explicitly requested resume subset."""
    if not names:
        return SECTIONS
    requested = set(names)
    # argparse 已驗證 key；仍保留 SECTIONS 的固定順序，避免 resume 順序隨輸入漂移。
    return tuple(section for section in SECTIONS if section.key in requested)


def _plan(section: Section, frequency_mhz: int) -> SingleMeasurementPlan:
    return SingleMeasurementPlan(
        generator_port="RF1.1",
        analyzer_port="RF1.5",
        center_frequency_hz=frequency_mhz * 1_000_000.0,
        bandwidth_hz=section.bandwidth_mhz * 1_000_000.0,
        # 新 band／bandwidth 的第一輪固定 -45 dBm，低於已通過的 -40 dBm 黃金點。
        generator_power_dbm=-45.0,
        expected_nominal_power_dbm=-20.0,
        external_attenuation_db=0.0,
        operator_confirmed=True,
        maximum_generator_power_dbm=-30.0,
    )


def _query(instrument: RsInstrument, registry, name: str) -> str:
    return instrument.query_str(registry.require(name)).strip()


def _select_waveform(instrument: RsInstrument, registry, section: Section) -> str:
    rf = _query(instrument, registry, "generator_query.state")
    measurement = _query(instrument, registry, "wlan_tx_query.measurement_state")
    if rf != "OFF" or measurement not in ALLOWED_IDLE_MEASUREMENT_STATES:
        raise RuntimeError(f"Waveform switch requires RF OFF/idle, got {rf}/{measurement}")
    path = f"{WAVEFORM_ROOT}/{section.waveform}"
    # ARB 檔切換會改變 baseband 來源；每次等待 OPC、查錯並用絕對路徑讀回。
    instrument.write_str(registry.render("generator.set_arb_file", arb_file=path))
    instrument.query_str(registry.require("common.operation_complete"))
    error = _query(instrument, registry, "common.system_error")
    if not error.startswith(("0,", "+0,")):
        raise RuntimeError(f"Waveform select failed: {error}")
    selected = _query(instrument, registry, "generator_query.arb_file_absolute").strip('"')
    if selected != path:
        raise RuntimeError(f"Waveform readback mismatch: expected {path}, got {selected}")
    return selected


def _cleanup(instrument: RsInstrument, registry) -> tuple[str, str, list[str]]:
    try:
        instrument.write_str(registry.require("wlan_tx.stop"))
        instrument.query_str(registry.require("common.operation_complete"))
    except Exception:
        instrument.write_str(registry.require("wlan_tx.abort"))
    instrument.write_str(registry.require("generator.rf_off"))
    instrument.query_str(registry.require("common.operation_complete"))
    errors: list[str] = []
    for _ in range(50):
        error = _query(instrument, registry, "common.system_error")
        if error.startswith(("0,", "+0,")):
            break
        errors.append(error)
    return (
        _query(instrument, registry, "generator_query.state"),
        _query(instrument, registry, "wlan_tx_query.measurement_state"),
        errors,
    )


def _save_manifest(manifest: dict[str, object], output_root: Path) -> Path:
    output_dir = output_root / "full-wlan-campaign"
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "latest.json"
    # 每完成一區就覆寫 checkpoint；程序或對話中斷後仍能知道已完成哪些 RF-Off 點。
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return output


def main() -> int:
    # RsInstrument 只在真的要連上儀器時才載入。純解析邏輯（區段表、catalog 解析）
    # 必須能在沒有安裝 hardware extra 的環境被匯入，否則 CI 收集測試就會失敗。
    from RsInstrument import RsInstrument

    sys.stdout.reconfigure(line_buffering=True)
    args = parse_args()
    if not all((args.confirm_direct_cable, args.confirm_no_attenuator,
                args.confirm_operator_present, args.confirm_full_wlan_campaign)):
        print("Refusing live campaign without all four confirmations.", file=sys.stderr)
        return 2
    registry = load_scpi_command_map(args.command_map)
    active_sections = selected_sections(args.section)
    instrument: RsInstrument | None = None
    manifest: dict[str, object] = {
        "created_at": datetime.now(UTC).isoformat(),
        "section_count": len(active_sections),
        "requested_points": sum(len(section.frequencies_mhz) for section in active_sections),
        "sections": [],
    }
    failed = False
    try:
        instrument = RsInstrument(
            args.resource, id_query=False, reset=False, options="SelectVisa='socketio'"
        )
        instrument.visa_timeout = 60_000
        backend = Cmp180SingleMeasurementBackend(instrument, registry, timeout_s=30.0)
        print(f"IDN: {_query(instrument, registry, 'common.identify')}")
        # 接手前先 Stop／Abort／RF Off，避免外部 GUI 遺留 ON 讓第一區段直接失敗。
        initial_rf, initial_measurement, initial_errors = _cleanup(instrument, registry)
        if initial_rf != "OFF" or initial_errors:
            raise RuntimeError(
                f"Initial cleanup failed: rf={initial_rf}, measurement={initial_measurement}, "
                f"errors={initial_errors}"
            )
        for section_index, section in enumerate(active_sections, 1):
            record: dict[str, object] = {
                "key": section.key,
                "band": section.band,
                "bandwidth_mhz": section.bandwidth_mhz,
                "requested_frequencies_mhz": section.frequencies_mhz,
                "waveform": section.waveform,
                "status": "RUNNING",
            }
            manifest["sections"].append(record)
            try:
                selected = _select_waveform(instrument, registry, section)
                golden_mhz = section.frequencies_mhz[len(section.frequencies_mhz) // 2]
                print(
                    f"SECTION {section_index}/{len(active_sections)} {section.key}: "
                    f"golden {golden_mhz} MHz"
                )
                golden = run_single_measurement(backend, _plan(section, golden_mhz))
                invalid = invalid_critical_fields(golden.values)
                if invalid or golden.cleanup_errors or golden.instrument_errors:
                    raise RuntimeError(
                        f"golden invalid={invalid} instrument={golden.instrument_errors} "
                        f"cleanup={golden.cleanup_errors}"
                    )
                golden_artifacts = save_single_result(
                    golden.values,
                    args.output_root,
                    test_name=f"real-{section.key}-golden",
                    simulated=False,
                    metadata={"campaign": "full-wlan", "section": section.key,
                              "waveform": selected, "frequency_hz": golden_mhz * 1e6,
                              "bandwidth_hz": section.bandwidth_mhz * 1e6,
                              "generator_power_dbm": -45.0},
                )
                print(f"GOLDEN PASS {section.key} EVM={golden.values['evm_all_carriers_db']} dB")
                points: list[dict[str, object]] = []
                for point_index, frequency_mhz in enumerate(section.frequencies_mhz, 1):
                    result = run_single_measurement(backend, _plan(section, frequency_mhz))
                    invalid = invalid_critical_fields(result.values)
                    if invalid or result.cleanup_errors or result.instrument_errors:
                        raise RuntimeError(
                            f"{frequency_mhz} MHz invalid={invalid} "
                            f"instrument={result.instrument_errors} cleanup={result.cleanup_errors}"
                        )
                    points.append({"frequency_hz": frequency_mhz * 1e6, **result.values})
                    print(
                        f"POINT {section.key} {point_index}/{len(section.frequencies_mhz)} "
                        f"{frequency_mhz} MHz EVM={result.values['evm_all_carriers_db']} dB"
                    )
                artifacts = save_frequency_sweep_result(
                    points,
                    args.output_root,
                    requested_frequencies_hz=tuple(
                        value * 1e6 for value in section.frequencies_mhz
                    ),
                    completed=True,
                    failed_frequency_hz=None,
                    error=None,
                    metadata={"campaign": "full-wlan", "section": section.key,
                              "band": section.band, "bandwidth_hz": section.bandwidth_mhz * 1e6,
                              "waveform": selected, "generator_power_dbm": -45.0},
                )
                record.update(status="PASS", completed_points=len(points),
                              golden_artifacts=golden_artifacts, artifacts=artifacts)
                _save_manifest(manifest, args.output_root)
                print(f"SECTION PASS {section.key} {len(points)}/{len(points)}")
            except Exception as exc:  # noqa: BLE001 - 保留失敗區段並安全繼續下一區段
                failed = True
                record.update(status="FAIL", error=f"{type(exc).__name__}: {exc}")
                _save_manifest(manifest, args.output_root)
                print(f"SECTION FAIL {section.key}: {record['error']}", file=sys.stderr)
                _cleanup(instrument, registry)
        return 3 if failed else 0
    finally:
        if instrument is not None:
            try:
                rf, measurement, errors = _cleanup(instrument, registry)
                manifest.update(final_rf_state=rf, final_measurement_state=measurement,
                                final_instrument_errors=errors)
            finally:
                instrument.close()
        output = _save_manifest(manifest, args.output_root)
        print(f"MANIFEST {output.resolve()}")


if __name__ == "__main__":
    raise SystemExit(main())
