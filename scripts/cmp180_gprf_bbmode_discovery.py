"""Discover whether the CMP180 GPRF generator accepts a CW baseband mode.

這支腳本不發射 RF：它只在 Generator RF 為 OFF 時寫入 baseband mode 候選、讀回結果、
檢查 error queue，最後還原原始 mode 與原始 ARB waveform。

用途：GPRF power sweep 的目的是量測 WLAN 涵蓋不到的範圍（400 MHz–8 GHz 掃頻、線損
校正、port 頻率響應）。目前產生器播放突發 WLAN ARB 波形，功率計會把閒置期一起平均，
量到的值比 burst power 低約 15.8 dB，無法用於位準或線損結論。改用 CW 才能得到可直接
解讀的功率值。

風險控制：切離 ARB 可能清除已選的 waveform，而 WLAN campaign 依賴該 waveform。因此
本腳本在探索前記錄 `SOURce:GPRF:GEN:BBMode?` 與 `SOURce:GPRF:GEN:ARB:FILE? ABSPath`，
結束時一律還原並逐項 read-back 驗證；還原失敗會以非零 exit code 明確報錯。

只探索 `CW` 與 `ARB` 兩個值：目標是確立 CW 出處，不必要地切換其他 baseband 模式只會
增加狀態漂移風險。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from RsInstrument import RsInstrument

from cmp180_evm.scpi.registry import load_scpi_command_map

# 只探索本次需要的兩個值；接受與否完全由儀器回答。
CANDIDATE_BASEBAND_MODES = ("CW", "ARB")

BBMODE_QUERY = "SOURce:GPRF:GEN:BBMode?"
BBMODE_SETTER = "SOURce:GPRF:GEN:BBMode {mode}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", default="TCPIP::192.168.200.50::5025::SOCKET")
    parser.add_argument("--timeout-ms", type=int, default=15_000)
    parser.add_argument(
        "--command-map", type=Path, default=Path("configs/scpi_command_map.yaml")
    )
    parser.add_argument("--confirm-operator-present", action="store_true")
    parser.add_argument(
        "--confirm-generator-config-write",
        action="store_true",
        help="Acknowledge that the generator baseband mode is written and restored (no RF).",
    )
    return parser.parse_args()


def _drain_errors(instrument: RsInstrument, registry) -> list[str]:
    errors: list[str] = []
    for _ in range(50):
        response = instrument.query_str(registry.require("common.system_error")).strip()
        if response.startswith(("0,", "+0,")):
            break
        errors.append(response)
    return errors


def main() -> int:
    args = parse_args()
    if not (args.confirm_operator_present and args.confirm_generator_config_write):
        print("Refusing baseband mode discovery without both confirmations.", file=sys.stderr)
        return 2

    registry = load_scpi_command_map(args.command_map)
    instrument: RsInstrument | None = None
    exit_code = 0
    original_mode: str | None = None
    original_arb: str | None = None
    try:
        instrument = RsInstrument(
            args.resource, id_query=False, reset=False, options="SelectVisa='socketio'"
        )
        instrument.visa_timeout = args.timeout_ms
        # 被拒絕的候選本身就是探索結果；改用本腳本的 SYST:ERR? 輪詢判斷成敗。
        instrument.instrument_status_checking = False
        print(f"IDN: {instrument.query_str(registry.require('common.identify')).strip()}")

        # 安全前置：Generator 必須 OFF 才寫入任何設定。
        rf_state = instrument.query_str(registry.require("generator_query.state")).strip()
        if rf_state != "OFF":
            print(f"Refusing discovery while generator RF is {rf_state}.", file=sys.stderr)
            return 3

        original_mode = instrument.query_str(BBMODE_QUERY).strip()
        original_arb = instrument.query_str(
            registry.require("generator_query.arb_file_absolute")
        ).strip()
        print(f"Original baseband mode: {original_mode}")
        print(f"Original ARB file: {original_arb}")
        _drain_errors(instrument, registry)

        results: list[dict[str, object]] = []
        for candidate in CANDIDATE_BASEBAND_MODES:
            try:
                instrument.write_str(BBMODE_SETTER.format(mode=candidate))
                instrument.query_str(registry.require("common.operation_complete"))
                errors = _drain_errors(instrument, registry)
            except Exception as exc:  # noqa: BLE001 - 記錄拒絕原因後繼續下一個候選
                errors = [f"{type(exc).__name__}: {exc}"]
                _drain_errors(instrument, registry)
            readback = instrument.query_str(BBMODE_QUERY).strip()
            accepted = not errors
            results.append(
                {
                    "candidate": candidate,
                    "accepted": accepted,
                    "readback": readback,
                    "errors": errors,
                }
            )
            print(f"{candidate:>5} -> accepted={accepted} readback={readback!r} errors={errors}")
        print(f"RESULTS: {json.dumps(results)}")
    except Exception as exc:
        print(f"Baseband mode discovery failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        exit_code = 3
    finally:
        if instrument is not None:
            try:
                # 一律還原原始 baseband mode 與 ARB waveform：WLAN campaign 依賴該 waveform。
                if original_mode:
                    instrument.write_str(BBMODE_SETTER.format(mode=original_mode))
                    instrument.query_str(registry.require("common.operation_complete"))
                    restored_mode = instrument.query_str(BBMODE_QUERY).strip()
                    print(f"Restored baseband mode: {restored_mode}")
                    if restored_mode != original_mode:
                        print("Baseband mode restore mismatch", file=sys.stderr)
                        exit_code = 4
                if original_arb:
                    restored_arb = instrument.query_str(
                        registry.require("generator_query.arb_file_absolute")
                    ).strip()
                    if restored_arb != original_arb:
                        # 切換 baseband 可能清除選取；用已驗證的 setter 重新指定同一個檔案。
                        print(f"ARB selection changed to {restored_arb}; reselecting original.")
                        instrument.write_str(
                            registry.render(
                                "generator.set_arb_file", arb_file=original_arb.strip('"')
                            )
                        )
                        instrument.query_str(registry.require("common.operation_complete"))
                        restored_arb = instrument.query_str(
                            registry.require("generator_query.arb_file_absolute")
                        ).strip()
                    print(f"Restored ARB file: {restored_arb}")
                    if restored_arb != original_arb:
                        print("ARB restore mismatch", file=sys.stderr)
                        exit_code = 4
                errors = _drain_errors(instrument, registry)
                final_rf = instrument.query_str(
                    registry.require("generator_query.state")
                ).strip()
                print(f"Final generator RF: {final_rf} (restore errors={errors})")
                if final_rf != "OFF" or errors:
                    exit_code = 4
            except Exception as exc:
                print(f"Restore failed: {type(exc).__name__}: {exc}", file=sys.stderr)
                exit_code = 4
            finally:
                instrument.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
