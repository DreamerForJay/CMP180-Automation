import pytest

from cmp180_evm.instrument.mock_cmp180 import MockCmp180
from cmp180_evm.utils.exceptions import InstrumentIdentityError


def test_query_before_connect_raises():
    mock = MockCmp180()
    with pytest.raises(RuntimeError):
        mock.query("*IDN?")


def test_common_commands():
    mock = MockCmp180()
    mock.connect()
    assert ",CMP-MOCK," in mock.query("*IDN?")
    assert mock.query("*OPC?") == "1"
    assert mock.query("SYST:ERR?").startswith("+0")
    mock.disconnect()


def test_verify_identity_matches():
    mock = MockCmp180()
    mock.connect()
    idn = mock.verify_identity("CMP")
    assert ",CMP-MOCK," in idn


def test_verify_identity_mismatch_raises():
    mock = MockCmp180()
    mock.connect()
    with pytest.raises(InstrumentIdentityError):
        mock.verify_identity("FSW85")


def test_drain_error_queue_empty_by_default():
    mock = MockCmp180()
    mock.connect()
    assert mock.drain_error_queue() == []


def test_command_log_records_writes():
    mock = MockCmp180()
    mock.connect()
    mock.write("*CLS")
    assert "*CLS" in mock.command_log
