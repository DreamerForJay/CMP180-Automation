"""Discover the CMP180 GPRF measurement routing and level commands.

這支腳本不發射 RF，也不寫入任何設定：它只對候選 query header 發問，每一條之後讀
`SYST:ERR?`，由儀器自己回答支援或不支援。

用途：`web/gprf_service.py` 目前只設定 GPRF measurement 的頻率，沒有設定量測端的
RF path 與位準。run `252bbbe39a` 因此在 Generator 送出 -40 dBm 時讀到 -80.8747 dBm
（約 41 dB 落差）。要修正必須先取得量測端 routing／expected power／external
attenuation 的正式命令出處。

候選字串依已驗證的 WLAN Analyzer 樹（`ROUTe:WLAN:MEAS:SPATh`、
`CONFigure:WLAN:MEAS:RFSettings:ENPower`／`EATTenuation`）的命名規律列出。這是
「詢問儀器接不接受」，不是把猜測當成已驗證結果：被拒絕的候選會記為 rejected，
不得寫進 `configs/scpi_command_map.yaml`。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from RsInstrument import RsInstrument

from cmp180_evm.scpi.registry import load_scpi_command_map

# 依已驗證的 WLAN Analyzer 樹命名規律列出；長短型各試一次，接受與否由儀器回答。
CANDIDATE_QUERIES: tuple[tuple[str, str], ...] = (
    ("measurement_frequency", "CONFigure:GPRF:MEASurement1:RFSettings:FREQuency?"),
    ("measurement_rf_path", "ROUTe:GPRF:MEASurement1:SPATh?"),
    ("measurement_rf_path_short", "ROUTe:GPRF:MEAS1:SPATh?"),
    ("measurement_rf_path_catalog", "CATalog:GPRF:MEASurement1:SPATh?"),
    ("measurement_expected_power", "CONFigure:GPRF:MEASurement1:RFSettings:ENPower?"),
    ("measurement_external_attenuation", "CONFigure:GPRF:MEASurement1:RFSettings:EATTenuation?"),
    ("measurement_user_margin", "CONFigure:GPRF:MEASurement1:RFSettings:UMARgin?"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", default="TCPIP::192.168.200.50::5025::SOCKET")
    parser.add_argument("--timeout-ms", type=int, default=15_000)
    parser.add_argument(
        "--command-map", type=Path, default=Path("configs/scpi_command_map.yaml")
    )
    return parser.parse_args()


def _drain_errors(instrument: RsInstrument, registry) -> list[str]:
    # error queue 必須讀到 `0,"No error"` 才算清空；設上限避免異常時無限迴圈。
    errors: list[str] = []
    for _ in range(50):
        response = instrument.query_str(registry.require("common.system_error")).strip()
        if response.startswith(("0,", "+0,")):
            break
        errors.append(response)
    return errors


def main() -> int:
    args = parse_args()
    registry = load_scpi_command_map(args.command_map)
    instrument: RsInstrument | None = None
    exit_code = 0
    try:
        instrument = RsInstrument(
            args.resource, id_query=False, reset=False, options="SelectVisa='socketio'"
        )
        instrument.visa_timeout = args.timeout_ms
        # 被拒絕的候選本身就是探索結果；關閉自動狀態例外，改用本腳本的 SYST:ERR? 輪詢。
        instrument.instrument_status_checking = False
        print(f"IDN: {instrument.query_str(registry.require('common.identify')).strip()}")

        # 安全前置：即使全程唯讀，仍要求 Generator RF 為 OFF 才進行探索。
        rf_state = instrument.query_str(registry.require("generator_query.state")).strip()
        if rf_state != "OFF":
            print(f"Refusing discovery while generator RF is {rf_state}.", file=sys.stderr)
            return 3
        _drain_errors(instrument, registry)

        results: list[dict[str, object]] = []
        for label, command in CANDIDATE_QUERIES:
            try:
                response = instrument.query_str(command).strip()
                errors = _drain_errors(instrument, registry)
            except Exception as exc:  # noqa: BLE001 - 記錄拒絕原因後繼續下一個候選
                response = ""
                errors = [f"{type(exc).__name__}: {exc}"]
                _drain_errors(instrument, registry)
            supported = not errors
            results.append(
                {
                    "label": label,
                    "command": command,
                    "supported": supported,
                    "response": response,
                    "errors": errors,
                }
            )
            print(f"{'PASS' if supported else 'FAIL'} {label:34} {response!r} errors={errors}")

        print(f"RESULTS: {json.dumps(results)}")
        print(
            "\nRecord every supported command (command + params/units + return fields + "
            "firmware + verification date + error-queue result) in "
            "docs/scpi-command-matrix.md before adding it to "
            "configs/scpi_command_map.yaml. A supported query does not by itself authorize "
            "writing the corresponding setter."
        )
    except Exception as exc:
        print(f"GPRF measurement discovery failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        exit_code = 3
    finally:
        if instrument is not None:
            try:
                final_rf = instrument.query_str(
                    registry.require("generator_query.state")
                ).strip()
                print(f"Final generator RF: {final_rf}")
                if final_rf != "OFF":
                    exit_code = 4
            except Exception as exc:
                print(f"Final RF readback failed: {type(exc).__name__}: {exc}", file=sys.stderr)
                exit_code = 4
            finally:
                instrument.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
