import sys
from types import SimpleNamespace

from cmp180_evm.instrument.session import Cmp180Session


class FakeRsInstrument:
    last_instance = None

    def __init__(self, resource, *, id_query, reset, options):
        self.resource = resource
        self.id_query = id_query
        self.reset = reset
        self.options = options
        self.visa_timeout = None
        self.writes = []
        self.closed = False
        FakeRsInstrument.last_instance = self

    def write_str(self, command):
        self.writes.append(command)

    def query_str(self, command):
        responses = {
            "*IDN?": "Rohde&Schwarz,CMP,serial,6.0.50.23",
            "*OPC?": "1",
            "SYST:ERR?": '0,"No error"',
        }
        return responses[command]

    def close(self):
        self.closed = True


def test_rsinstrument_socket_adapter(monkeypatch):
    monkeypatch.setitem(
        sys.modules,
        "RsInstrument",
        SimpleNamespace(RsInstrument=FakeRsInstrument),
    )
    session = Cmp180Session(
        "TCPIP::192.168.200.50::5025::SOCKET",
        options="SelectVisa='socketio'",
        timeout_ms=12345,
        check_error_after_write=False,
    )

    session.connect()
    fake = FakeRsInstrument.last_instance

    assert fake.resource == "TCPIP::192.168.200.50::5025::SOCKET"
    assert fake.options == "SelectVisa='socketio'"
    assert fake.id_query is False
    assert fake.reset is False
    assert fake.visa_timeout == 12345
    assert fake.writes == ["*CLS"]
    assert session.verify_identity("CMP") == "Rohde&Schwarz,CMP,serial,6.0.50.23"
    assert session.drain_error_queue() == []

    session.disconnect()
    assert fake.closed is True
    assert session.connected is False
