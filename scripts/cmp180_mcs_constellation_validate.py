"""固定安全 loopback 的 MCS 0–13 與同次量測星座圖實機驗證。"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from cmp180_evm.results.validity import evaluate_point_validity
from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.cmp180_single_backend import Cmp180SingleMeasurementBackend
from cmp180_evm.workflow.single_measurement import SingleMeasurementPlan, run_single_measurement


def parse_trace(raw_i: str, raw_q: str) -> dict:
    """Parse separate CMP180 amplitude arrays, each prefixed by reliability."""
    channels = [next(csv.reader([raw])) for raw in (raw_i, raw_q)]
    if any(len(channel) < 2 for channel in channels):
        raise ValueError("I/Q trace has no amplitudes")
    if len(channels[0]) != len(channels[1]) or len(channels[0]) > 2081:
        raise ValueError("I/Q length mismatch or OFDM trace exceeds 2080 points")

    def finite(token: str):
        try:
            value = float(token)
        except ValueError:
            return None
        # INV／NaN／溢位 sentinel 不補零；保留原回應供後續診斷。
        return value if math.isfinite(value) and abs(value) <= 2 else None

    reliability = [channel[0].strip() for channel in channels]
    reliable = all(value in {"0", "+0"} for value in reliability)
    points = []
    for index, (i_token, q_token) in enumerate(zip(channels[0][1:], channels[1][1:], strict=True)):
        i_value, q_value = finite(i_token), finite(q_token)
        points.append({"index": index, "i": i_value, "q": q_value,
                       "valid": reliable and i_value is not None and q_value is not None})
    return {"reliability": reliability, "points": points,
            "valid": all(point["valid"] for point in points),
            "normalization": "CMP180 native amplitudes; no rescaling",
            "symbol_type": "unspecified by trace response"}


def enabled_flags(raw: str) -> str:
    flags = [value.strip().upper() for value in raw.split(",")]
    # ALL 的第六欄才是 IQConst，其他結果開關保持原值，拒絕未知欄位格式。
    if len(flags) not in (8, 9) or any(flag not in {"ON", "OFF", "0", "1"} for flag in flags):
        raise ValueError(f"Unknown result flags: {raw}")
    flags[5] = "ON"
    return ",".join(flags)


def waveform_candidates(catalog: dict) -> dict[int, str]:
    selected = catalog["selected_arb_file"]
    parent = selected.rsplit("/", 1)[0]
    names = {item["name"] for item in catalog["waveforms"]}
    result = {}
    for mcs in range(14):
        name = f"KV352_lib8_WLAN_11be_EHT_MU_BW320-1_4xLTF_GI32_MCS{mcs}_LEN4096_LDPC.wv"
        if name not in names:
            raise ValueError(f"Missing catalog waveform for MCS {mcs}")
        result[mcs] = f"{parent}/{name}"
    return result


class CampaignBackend(Cmp180SingleMeasurementBackend):
    def __init__(self, io, registry, waveform: str):
        super().__init__(io, registry, timeout_s=60)
        self.waveform = waveform

    def configure(self, plan):
        super().configure(plan)
        # 共用 backend 先選 MCS11；RF 開啟前再切至本點波形，不能在 configure 前切換。
        if self._query("generator_query.state") != "OFF":
            raise RuntimeError("RF changed during configuration")
        self._write_checked("generator.set_arb_file", arb_file=self.waveform)
        self._require_readback("generator_query.arb_file_absolute", self.waveform)
        self.selected_arb_file = self.waveform


def final_cleanup(backend) -> dict:
    errors = []
    # Stop 或 Abort 失敗都不得跳過 RF Off；各步獨立清理並保存失敗資訊。
    try:
        backend.stop_measurement()
    except Exception as exc:
        errors.append(f"stop: {exc}")
        try:
            backend._write_checked("wlan_tx.abort")
        except Exception as abort_exc:
            errors.append(f"abort: {abort_exc}")
    try:
        backend.rf_off()
    except Exception as exc:
        errors.append(f"rf_off: {exc}")
    state = {"cleanup_errors": errors}
    for key, command in (("rf", "generator_query.state"),
                         ("measurement", "wlan_tx_query.measurement_state")):
        try:
            state[key] = backend._query(command)
        except Exception as exc:
            errors.append(f"{key}: {exc}")
    try:
        state["instrument_errors"] = backend.drain_error_queue()
    except Exception as exc:
        errors.append(f"error_queue: {exc}")
    return state


def save_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=Path("output/mcs-constellation-hil"))
    parser.add_argument("--confirm-direct-cable", action="store_true")
    parser.add_argument("--confirm-operator-present", action="store_true")
    parser.add_argument("--confirm-rf11-only", action="store_true")
    args = parser.parse_args()
    if not (args.confirm_direct_cable and args.confirm_operator_present and args.confirm_rf11_only):
        parser.error("RF1.1 to RF1.5 direct cable, no DUT/attenuator, and operator required")
    candidates = waveform_candidates(json.loads(args.catalog.read_text(encoding="utf-8")))
    registry = load_scpi_command_map(Path("configs/scpi_command_map.yaml"))
    # 固定安全條件，不開放任意頻率／功率或路徑覆寫。
    plan = SingleMeasurementPlan("RF1.1", "RF1.5", 6_105_000_000, 320_000_000,
                                 -40, -20, 0, True, -40)
    run_dir = args.output_root / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir.mkdir(parents=True, exist_ok=False)
    manifest = {"source": "hardware", "simulated": False, "compliance_claim": False,
                "plan": asdict(plan), "created_at": datetime.now(UTC).isoformat(),
                "status": "RUNNING", "points": [], "catalog": str(args.catalog)}
    from RsInstrument import RsInstrument

    io = None
    backend = None
    original = {}
    try:
        io = RsInstrument("TCPIP::192.168.200.50::5025::SOCKET", id_query=False,
                          reset=False, options="SelectVisa='socketio'")
        io.visa_timeout = 15000
        backend = CampaignBackend(io, registry, candidates[11])
        identity = backend._query("common.identify").split(",")
        if len(identity) < 4 or "CMP" not in identity[1]:
            raise RuntimeError("Unexpected instrument identity")
        # 證據僅保存機型與韌體，避免散播序號或選配授權資訊。
        manifest["instrument"] = {"model": identity[1], "firmware": identity[3]}
        for key, command in (("rf", "generator_query.state"),
                             ("measurement", "wlan_tx_query.measurement_state"),
                             ("route", "generator_query.rf_path"),
                             ("states", "generator_query.states")):
            original[key] = backend._query(command)
        manifest["initial"] = original
        if original["rf"] != "OFF" or original["measurement"] not in {"OFF", "RDY"}:
            raise RuntimeError("Instrument must be RF OFF and measurement idle")
        # SPATh 回傳 routing 群組，不代表八埠皆啟用；獨立以 GUI 確認只有 RF1.1 勾選。
        manifest["rf11_only_gui_confirmed"] = args.confirm_rf11_only
        if original["route"].strip('" ') not in {"RF1.1", "RF1.1-RF1.8"}:
            raise RuntimeError(f"Unexpected generator route: {original['route']}")
        if backend.drain_error_queue():
            raise RuntimeError("Initial instrument error queue was not empty")
        original["waveform"] = backend._query("generator_query.arb_file_absolute").strip('"')
        original["result_flags"] = backend._query("wlan_tx_query.result_configuration")
        backend._write_checked("wlan_tx.set_results", flags=enabled_flags(original["result_flags"]))
        flags = backend._query("wlan_tx_query.result_configuration")
        if flags.split(",")[5].strip() not in {"ON", "1"}:
            raise RuntimeError("IQ constellation result enable readback failed")
        manifest["enabled_result_flags"] = flags
        # 先跑已知 MCS11 黃金點，再逐點掃其餘 13 點；每點都是新的 INIT→RDY→FETCh。
        for mcs in [11] + [index for index in range(14) if index != 11]:
            backend.waveform = candidates[mcs]
            record = {"requested_mcs": mcs, "waveform": candidates[mcs], "status": "RUNNING"}
            manifest["points"].append(record)
            save_json(run_dir / "manifest.json", manifest)
            result = run_single_measurement(backend, plan)
            record.update({"values": result.values, "phases": [phase.value for phase in result.phases],
                           "cleanup_errors": result.cleanup_errors, "instrument_errors": result.instrument_errors})
            save_json(run_dir / "manifest.json", manifest)
            if result.cleanup_errors or result.instrument_errors:
                raise RuntimeError(f"MCS {mcs}: instrument/cleanup error")
            validity = evaluate_point_validity(result.values)
            if not validity.valid or float(result.values["mcs_index"]) != mcs:
                raise RuntimeError(f"MCS {mcs}: invalid result or decoded MCS mismatch")
            record["measurement_valid"] = True
            record["final_rf"] = backend._query("generator_query.state")
            record["final_measurement"] = backend._query("wlan_tx_query.measurement_state")
            if record["final_rf"] != "OFF" or record["final_measurement"] != "RDY":
                raise RuntimeError("Unsafe post-measurement state")
            # RF 關閉且量測完成後讀同次 stored trace，不會另啟動量測或混入下一個 MCS。
            raw_i = backend._query("results.constellation_i")
            raw_q = backend._query("results.constellation_q")
            trace = {"raw_i": raw_i, "raw_q": raw_q, "source": "hardware", "simulated": False}
            save_json(run_dir / f"mcs-{mcs:02d}-iq.json", trace)
            trace_errors = backend.drain_error_queue()
            if trace_errors:
                record["trace_errors"] = trace_errors
                raise RuntimeError(f"Trace query failed: {trace_errors}")
            try:
                trace.update(parse_trace(raw_i, raw_q))
            except ValueError as exc:
                trace.update({"valid": False, "parse_error": str(exc)})
            save_json(run_dir / f"mcs-{mcs:02d}-iq.json", trace)
            record.update({"constellation_valid": trace["valid"], "status": "COMPLETE",
                           "constellation_file": f"mcs-{mcs:02d}-iq.json"})
            save_json(run_dir / "manifest.json", manifest)
            print(f"MCS {mcs}: EVM={result.values['evm_all_carriers_db']} dB; IQ valid={trace['valid']}; RF OFF", flush=True)
        manifest["status"] = "COMPLETE"
    except (Exception, KeyboardInterrupt) as exc:
        manifest.update({"status": "FAILED", "error": f"{type(exc).__name__}: {exc}"})
        print(manifest["error"], flush=True)
    finally:
        if backend is not None:
            state = final_cleanup(backend)
            manifest["final"] = state
            if state.get("rf") == "OFF" and state.get("measurement") in {"OFF", "RDY"}:
                for key, command, argument in (("waveform", "generator.set_arb_file", "arb_file"),
                                                ("result_flags", "wlan_tx.set_results", "flags")):
                    if key in original:
                        try:
                            backend._write_checked(command, **{argument: original[key]})
                            query = "generator_query.arb_file_absolute" if key == "waveform" else "wlan_tx_query.result_configuration"
                            backend._require_readback(query, original[key])
                        except Exception as exc:
                            state["cleanup_errors"].append(f"restore {key}: {exc}")
            if state.get("rf") != "OFF" or state.get("measurement") not in {"OFF", "RDY"} or state["cleanup_errors"] or state.get("instrument_errors"):
                manifest["status"] = "FAILED"
        if io is not None:
            io.close()
        save_json(run_dir / "manifest.json", manifest)
        print(f"Saved: {run_dir.resolve()}; status={manifest['status']}", flush=True)
    return 0 if manifest["status"] == "COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
