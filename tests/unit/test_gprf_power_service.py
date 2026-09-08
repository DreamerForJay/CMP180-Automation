import json
from pathlib import Path

import pytest

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.web.gprf_service import (
    _drain_error_queue,
    _restore_baseband,
    _save_gprf_result,
    _select_cw_baseband,
    build_gprf_power_preview,
)

BBMODE_QUERY = "SOURce:GPRF:GEN:BBMode?"
ARB_QUERY = "SOURce:GPRF:GEN:ARB:FILE? ABSPath"
WLAN_ARB = '"/home/instrument/fw/data/waveform/WLAN/KV352_lib8.wv"'


class _BasebandConn:
    """Stateful stub tracking generator baseband mode and ARB selection."""

    def __init__(
        self,
        *,
        mode: str = "ARB",
        arb: str = WLAN_ARB,
        drop_arb_on_switch: bool = False,
        stuck_mode: str | None = None,
    ) -> None:
        self.mode = mode
        self.arb = arb
        self.drop_arb_on_switch = drop_arb_on_switch
        self.stuck_mode = stuck_mode
        self.writes: list[str] = []

    def query(self, command: str) -> str:
        if command == BBMODE_QUERY:
            return self.mode
        if command == ARB_QUERY:
            return self.arb
        if command == "*OPC?":
            return "1"
        if command == "SYST:ERR?":
            return '0,"No error"'
        raise AssertionError(f"unexpected query {command!r}")

    def write(self, command: str) -> None:
        self.writes.append(command)
        if command.startswith("SOURce:GPRF:GEN:BBMode "):
            requested = command.split(" ", 1)[1]
            # stuck_mode 模擬 setter 沒有真正生效的儀器行為。
            self.mode = self.stuck_mode or requested
            if requested == "CW" and self.drop_arb_on_switch:
                self.arb = '""'
            return
        if command.startswith('SOURce:GPRF:GEN:ARB:FILE "'):
            self.arb = '"' + command.split('"')[1] + '"'
            return
        raise AssertionError(f"unexpected write {command!r}")


class _StubConn:
    """Minimal stand-in exposing only the `query` method used by the drain helper."""

    def __init__(self, responses: list[str], *, fail_after: int | None = None) -> None:
        self.responses = list(responses)
        self.queries: list[str] = []
        self.fail_after = fail_after

    def query(self, command: str) -> str:
        self.queries.append(command)
        if self.fail_after is not None and len(self.queries) > self.fail_after:
            raise OSError("socket closed")
        if self.responses:
            return self.responses.pop(0)
        return '0,"No error"'


def _registry():
    return load_scpi_command_map(Path("configs/scpi_command_map.yaml"))


def test_gprf_frequency_preview_uses_instrument_range_not_wlan_sections():
    preview = build_gprf_power_preview(
        {
            "axis": "frequency",
            "start_hz": 400_000_000,
            "stop_hz": 8_000_000_000,
            "step_hz": 100_000_000,
            "power_dbm": -40,
            "dwell_ms": 200,
        }
    )

    assert preview.execution_allowed is True
    assert preview.public()["measurement_family"] == "GPRF_POWER"
    assert preview.public()["point_count"] == 77
    assert "not WLAN EVM" in preview.public()["disclaimer"]


def test_gprf_preview_blocks_outside_cmp180_planning_range():
    preview = build_gprf_power_preview(
        {
            "axis": "frequency",
            "start_hz": 300_000_000,
            "stop_hz": 500_000_000,
            "step_hz": 100_000_000,
            "power_dbm": -40,
            "dwell_ms": 200,
        }
    )

    assert preview.execution_allowed is False
    assert "400 MHz..8 GHz" in str(preview.rejection_reason)


def test_error_queue_drain_reports_empty_queue_without_extra_reads():
    conn = _StubConn(['0,"No error"'])

    assert _drain_error_queue(conn, _registry()) == []
    assert conn.queries == ["SYST:ERR?"]


def test_error_queue_drain_collects_entries_until_queue_is_empty():
    conn = _StubConn(
        [
            '-113,"Undefined header"',
            '-222,"Data out of range"',
            '0,"No error"',
        ]
    )

    entries = _drain_error_queue(conn, _registry())

    assert entries == ['-113,"Undefined header"', '-222,"Data out of range"']
    assert len(conn.queries) == 3


def test_error_queue_drain_records_read_failure_as_evidence():
    conn = _StubConn(['-113,"Undefined header"'], fail_after=1)

    entries = _drain_error_queue(conn, _registry())

    assert entries[0] == '-113,"Undefined header"'
    assert entries[1].startswith("ERROR_QUEUE_READ_FAILED:")


def test_error_queue_drain_stops_at_limit_when_instrument_never_clears():
    conn = _StubConn(['-113,"Undefined header"'] * 50)

    entries = _drain_error_queue(conn, _registry(), limit=5)

    assert len(entries) == 5
    assert len(conn.queries) == 5


def test_cw_selection_switches_generator_and_reports_original_state():
    conn = _BasebandConn()

    original_mode, original_arb = _select_cw_baseband(conn, _registry())

    assert (original_mode, original_arb) == ("ARB", WLAN_ARB)
    assert conn.mode == "CW"
    assert conn.writes == ["SOURce:GPRF:GEN:BBMode CW"]


def test_cw_selection_does_not_write_when_generator_is_already_cw():
    conn = _BasebandConn(mode="CW")

    original_mode, _ = _select_cw_baseband(conn, _registry())

    assert original_mode == "CW"
    assert conn.writes == []


def test_cw_selection_fails_when_readback_is_not_cw():
    conn = _BasebandConn(stuck_mode="ARB")

    with pytest.raises(RuntimeError, match="is not CW"):
        _select_cw_baseband(conn, _registry())


def test_restore_puts_back_arb_mode_and_keeps_existing_waveform():
    conn = _BasebandConn(mode="CW", arb=WLAN_ARB)

    problems = _restore_baseband(conn, _registry(), "ARB", WLAN_ARB)

    assert problems == []
    assert conn.mode == "ARB"
    # waveform 未被清掉時不應重複寫入 ARB 檔案。
    assert conn.writes == ["SOURce:GPRF:GEN:BBMode ARB"]


def test_restore_reselects_waveform_when_switching_cleared_it():
    conn = _BasebandConn(drop_arb_on_switch=True)
    _select_cw_baseband(conn, _registry())
    assert conn.arb == '""'

    problems = _restore_baseband(conn, _registry(), "ARB", WLAN_ARB)

    assert problems == []
    assert conn.arb == WLAN_ARB


def test_restore_reports_mismatch_when_baseband_mode_will_not_return():
    conn = _BasebandConn(mode="CW", stuck_mode="CW")

    problems = _restore_baseband(conn, _registry(), "ARB", WLAN_ARB)

    assert problems and problems[0].startswith("BASEBAND_MODE_RESTORE_MISMATCH")


def test_gprf_artifacts_record_completed_point_count(tmp_path: Path):
    artifacts = _save_gprf_result(
        points=[
            {
                "point_index": 0,
                "frequency_hz": 4_000_000_000,
                "generator_power_dbm": -40,
                "expected_power_dbm": -40,
                "burst_power_dbm": -40.1,
                "valid": True,
            },
            {
                "point_index": 1,
                "frequency_hz": 4_100_000_000,
                "generator_power_dbm": -40,
                "expected_power_dbm": -40,
                "burst_power_dbm": -39.9,
                "valid": True,
            },
        ],
        output_root=tmp_path,
        metadata={"sweep_axis": "frequency"},
    )

    metadata = json.loads(Path(artifacts["metadata"]).read_text(encoding="utf-8"))

    assert metadata["completed_points"] == 2
    assert metadata["point_count"] == 2
    # GPRF 使用獨立保存流程，也必須同步產生靜態 PNG，避免結果頁只剩互動 SVG。
    assert Path(artifacts["matplotlib_burst_power_dbm"]).is_file()
