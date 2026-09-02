"""Inventory every CMP180 ARB waveform in the selected waveform directory.

這是 query-only 工具：先確認 Generator RF OFF 與 WLAN measurement idle，再讀取
目前 ARB 檔案的絕對路徑，最後用 CMP180 內建 Help 確認的 mass-memory catalog
命令一次列出同一目錄的所有 `.wv`。若外部狀態在盤點期間意外轉為 RF ON，finally
會執行 Stop／Abort／RF Off，避免把儀器留在不安全狀態。
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

from RsInstrument import RsInstrument

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.workflow.analyzer_setter_validation import ALLOWED_IDLE_MEASUREMENT_STATES

_BANDWIDTH_PATTERN = re.compile(r"(?:^|_)BW(20|40|80|160|320)(?:[-_]|\.)", re.IGNORECASE)


def parse_catalog_response(response: str) -> list[dict[str, object]]:
    """Parse MMEMory:CATalog? output into file records."""
    fields = next(csv.reader([response], skipinitialspace=True))
    records: list[dict[str, object]] = []
    # 前兩欄是已用與剩餘容量；後續每欄才是一個檔案／目錄紀錄。
    for field in fields[2:]:
        parts = field.split(",")
        if len(parts) < 3:
            continue
        name, item_type, size_text = parts[:3]
        try:
            size_bytes = int(size_text)
        except ValueError:
            size_bytes = 0
        match = _BANDWIDTH_PATTERN.search(name)
        records.append(
            {
                "name": name,
                "type": item_type,
                "size_bytes": size_bytes,
                "bandwidth_mhz": int(match.group(1)) if match else None,
            }
        )
    return records


def _parent_pattern(path: str) -> str:
    normalized = path.strip().strip('"').replace("\\", "/")
    parent, separator, _ = normalized.rpartition("/")
    if not separator:
        raise ValueError(f"Selected ARB path has no directory: {path!r}")
    # 萬用字元只盤點同一個 waveform 目錄，不遞迴觸碰其他儀器檔案。
    return f"{parent}/*.wv"


def _drain_errors(instrument: RsInstrument, registry) -> list[str]:
    errors: list[str] = []
    for _ in range(50):
        response = instrument.query_str(registry.require("common.system_error")).strip()
        if response.startswith(("0,", "+0,")):
            return errors
        errors.append(response)
    raise RuntimeError("CMP180 error queue did not terminate")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", default="TCPIP::192.168.200.50::5025::SOCKET")
    parser.add_argument("--command-map", type=Path, default=Path("configs/scpi_command_map.yaml"))
    parser.add_argument("--output-root", type=Path, default=Path("output/waveform-catalog"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = load_scpi_command_map(args.command_map)
    instrument: RsInstrument | None = None
    try:
        instrument = RsInstrument(
            args.resource, id_query=False, reset=False, options="SelectVisa='socketio'"
        )
        instrument.visa_timeout = 15_000
        rf_state = instrument.query_str(registry.require("generator_query.state")).strip()
        measurement_state = instrument.query_str(
            registry.require("wlan_tx_query.measurement_state")
        ).strip()
        if rf_state != "OFF" or measurement_state not in ALLOWED_IDLE_MEASUREMENT_STATES:
            raise RuntimeError(
                f"Refusing inventory while rf={rf_state}, measurement={measurement_state}"
            )
        selected = instrument.query_str(
            registry.require("generator_query.arb_file_absolute")
        ).strip()
        pattern = _parent_pattern(selected)
        aliases = instrument.query_str(registry.require("mass_memory_query.aliases")).strip()
        catalog_raw = instrument.query_str(
            registry.render("mass_memory_query.catalog", path_pattern=pattern)
        ).strip()
        errors = _drain_errors(instrument, registry)
        if errors:
            raise RuntimeError(f"CMP180 catalog query errors: {errors}")
        waveforms = [
            item for item in parse_catalog_response(catalog_raw)
            if str(item["name"]).lower().endswith(".wv")
        ]
        payload = {
            "created_at": datetime.now(UTC).isoformat(),
            "selected_arb_file": selected.strip('"'),
            "catalog_pattern": pattern,
            "aliases_raw": aliases,
            "waveform_count": len(waveforms),
            "bandwidths_mhz": sorted(
                {item["bandwidth_mhz"] for item in waveforms if item["bandwidth_mhz"]}
            ),
            "waveforms": waveforms,
            "final_rf_state": rf_state,
            "final_measurement_state": measurement_state,
            "instrument_errors": errors,
        }
        args.output_root.mkdir(parents=True, exist_ok=True)
        output = args.output_root / "latest.json"
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print(f"Saved: {output.resolve()}")
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI 必須把完整儀器失敗原因交給操作員
        print(f"Waveform inventory failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 3
    finally:
        if instrument is not None:
            try:
                final_rf = instrument.query_str(
                    registry.require("generator_query.state")
                ).strip()
                if final_rf != "OFF":
                    # 外部控制若在 query-only 期間打開 RF，仍以人身／硬體安全優先清理。
                    instrument.write_str(registry.require("wlan_tx.stop"))
                    instrument.write_str(registry.require("wlan_tx.abort"))
                    instrument.write_str(registry.require("generator.rf_off"))
                    instrument.query_str(registry.require("common.operation_complete"))
            finally:
                instrument.close()


if __name__ == "__main__":
    raise SystemExit(main())
