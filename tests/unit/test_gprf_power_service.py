from pathlib import Path

from cmp180_evm.scpi.registry import load_scpi_command_map
from cmp180_evm.web.gprf_service import _drain_error_queue, build_gprf_power_preview


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
