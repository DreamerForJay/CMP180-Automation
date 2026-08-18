"""Mock CMP180 instrument (SPEC.MD section 26).

Implements the same InstrumentSession protocol as the real session so
workflow/CLI/GUI code can run against it unchanged when no hardware is
available. Only understands the fixed set of common SCPI commands
(*IDN?, *OPT?, *CLS, *OPC?, SYST:ERR?) plus whatever CMP180-specific commands
are passed to it as plain strings — it does not know the meaning of any
WLAN/generator command, it only records writes and returns canned responses.

Any data this produces is simulated and must be labeled as such wherever it
is displayed or saved (rule: "Mock results must be clearly labeled simulated").
"""

from cmp180_evm.scpi import common

SIMULATED_IDN = "Rohde&Schwarz,CMP180-MOCK,1234567,1.0.0.0"
SIMULATED_OPTIONS = "MOCK-OPT-1,MOCK-OPT-2"


class MockCmp180:
    simulated = True

    def __init__(self) -> None:
        self._connected = False
        self._error_queue: list[str] = []
        self.command_log: list[str] = []

    @property
    def connected(self) -> bool:
        return self._connected

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def verify_identity(self, expected_model_contains: str) -> str:
        idn = self.query(common.IDENTIFY)
        if expected_model_contains not in idn:
            from cmp180_evm.utils.exceptions import InstrumentIdentityError

            raise InstrumentIdentityError(expected_model_contains, idn)
        return idn

    def write(self, command: str) -> None:
        self._require_connected()
        self.command_log.append(command)

    def query(self, command: str) -> str:
        self._require_connected()
        self.command_log.append(command)

        if command == common.IDENTIFY:
            return SIMULATED_IDN
        if command == common.OPTIONS:
            return SIMULATED_OPTIONS
        if command == common.OPERATION_COMPLETE:
            return "1"
        if command == common.SYSTEM_ERROR:
            if self._error_queue:
                return self._error_queue.pop(0)
            return '+0,"No error"'

        return "0"

    def query_float(self, command: str) -> float:
        return float(self.query(command))

    def query_int(self, command: str) -> int:
        return int(float(self.query(command)))

    def query_csv(self, command: str) -> list[str]:
        return [token.strip() for token in self.query(command).split(",")]

    def wait_opc(self, timeout_s: float = 30.0) -> None:
        self._require_connected()

    def clear_status(self) -> None:
        self._require_connected()
        self._error_queue.clear()

    def drain_error_queue(self) -> list[str]:
        errors = list(self._error_queue)
        self._error_queue.clear()
        return errors

    def _require_connected(self) -> None:
        if not self._connected:
            raise RuntimeError("Mock instrument session is not connected. Call connect() first.")
