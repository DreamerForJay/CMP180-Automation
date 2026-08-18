"""InstrumentSession protocol (SPEC.MD section 12.1).

Both the real CMP180 session (instrument/session.py) and the mock instrument
(instrument/mock_cmp180.py) implement this protocol, so workflow code can be
written once against `InstrumentSession` and run unchanged against either.
"""

from typing import Protocol, runtime_checkable

from cmp180_evm.utils.exceptions import InstrumentIdentityError


def validate_idn_model(idn: str, expected_model: str) -> str:
    """Validate the model field of an IEEE-488.2 identification response.

    The CMP180 identifies its model as ``CMP``. Mock variants may append a
    hyphenated suffix, but a match elsewhere in the IDN response is rejected.
    """
    fields = [field.strip() for field in idn.split(",")]
    if len(fields) < 2:
        raise InstrumentIdentityError(expected_model, idn)

    actual_model = fields[1].upper()
    expected = expected_model.strip().upper()
    if actual_model != expected and not actual_model.startswith(f"{expected}-"):
        raise InstrumentIdentityError(expected_model, idn)
    return idn


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
