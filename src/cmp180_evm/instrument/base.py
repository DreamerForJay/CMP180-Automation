"""InstrumentSession protocol (SPEC.MD section 12.1).

Both the real CMP180 session (instrument/session.py) and the mock instrument
(instrument/mock_cmp180.py) implement this protocol, so workflow code can be
written once against `InstrumentSession` and run unchanged against either.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class InstrumentSession(Protocol):
    def connect(self) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def write(self, command: str) -> None:
        ...

    def query(self, command: str) -> str:
        ...

    def query_float(self, command: str) -> float:
        ...

    def query_int(self, command: str) -> int:
        ...

    def query_csv(self, command: str) -> list[str]:
        ...

    def wait_opc(self, timeout_s: float = 30.0) -> None:
        ...

    def clear_status(self) -> None:
        ...

    def drain_error_queue(self) -> list[str]:
        ...
