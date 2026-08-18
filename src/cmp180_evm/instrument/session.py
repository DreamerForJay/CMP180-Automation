"""Real CMP180 instrument session through RsInstrument (SPEC.MD section 12).

RsInstrument is an optional dependency (`pip install .[hardware]`) and is only
imported when `connect()` is actually called, so the rest of the project
(config validation, dry-run, mock-based tests) works without it installed.

This module intentionally does NOT know about WLAN/generator SCPI commands —
it only implements the generic read/write/query primitives from
`InstrumentSession`. CMP180-specific commands are looked up by callers via
`ScpiCommandRegistry` and passed in as plain strings.
"""

import time

from cmp180_evm.scpi import common
from cmp180_evm.utils.exceptions import InstrumentIdentityError
from cmp180_evm.utils.logging import get_scpi_logger


class Cmp180Session:
    def __init__(
        self,
        resource_address: str,
        *,
        options: str = "SelectVisa='socketio'",
        timeout_ms: int = 10000,
        opc_timeout_ms: int = 30000,
        query_delay_ms: int = 0,
        clear_status_on_connect: bool = False,
        check_error_after_write: bool = True,
        mask_sensitive_data: bool = True,
    ) -> None:
        self.resource_address = resource_address
        self.options = options
        self.timeout_ms = timeout_ms
        self.opc_timeout_ms = opc_timeout_ms
        self.query_delay_ms = query_delay_ms
        self.clear_status_on_connect = clear_status_on_connect
        self.check_error_after_write = check_error_after_write
        self.mask_sensitive_data = mask_sensitive_data

        self._instrument = None
        self._logger = get_scpi_logger()

    @property
    def connected(self) -> bool:
        return self._instrument is not None

    def connect(self) -> None:
        try:
            from RsInstrument import RsInstrument
        except ImportError as exc:
            raise RuntimeError(
                "RsInstrument is required for a real instrument connection. "
                "Install it with: pip install .[hardware]"
            ) from exc

        self._instrument = RsInstrument(
            self.resource_address,
            id_query=False,
            reset=False,
            options=self.options,
        )
        self._instrument.visa_timeout = self.timeout_ms

        if self.clear_status_on_connect:
            self.clear_status()

    def disconnect(self) -> None:
        if self._instrument is not None:
            self._instrument.close()
            self._instrument = None

    def verify_identity(self, expected_model_contains: str) -> str:
        idn = self.query(common.IDENTIFY)
        if expected_model_contains not in idn:
            raise InstrumentIdentityError(expected_model_contains, idn)
        return idn

    def write(self, command: str) -> None:
        self._require_connected()
        self._logger.debug("TX %s", command)
        self._instrument.write_str(command)
        if self.query_delay_ms:
            time.sleep(self.query_delay_ms / 1000)
        if self.check_error_after_write:
            errors = self.drain_error_queue()
            if errors:
                self._logger.warning("SYST:ERR? after '%s': %s", command, errors)

    def query(self, command: str) -> str:
        self._require_connected()
        self._logger.debug("TX %s", command)
        start = time.monotonic()
        response = self._instrument.query_str(command).strip()
        elapsed_ms = (time.monotonic() - start) * 1000
        self._logger.debug("RX %s", response)
        self._logger.debug("ELAPSED %.1f ms", elapsed_ms)
        return response

    def query_float(self, command: str) -> float:
        return float(self.query(command))

    def query_int(self, command: str) -> int:
        return int(float(self.query(command)))

    def query_csv(self, command: str) -> list[str]:
        return [token.strip() for token in self.query(command).split(",")]

    def wait_opc(self, timeout_s: float | None = None) -> None:
        timeout_s = self.opc_timeout_ms / 1000 if timeout_s is None else timeout_s
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            if self.query(common.OPERATION_COMPLETE) == "1":
                return
        raise TimeoutError(f"*OPC? did not return within {timeout_s:.1f}s")

    def clear_status(self) -> None:
        self._require_connected()
        self._logger.debug("TX %s", common.CLEAR_STATUS)
        self._instrument.write_str(common.CLEAR_STATUS)

    def drain_error_queue(self) -> list[str]:
        errors: list[str] = []
        for _ in range(50):
            response = self.query(common.SYSTEM_ERROR)
            if response.startswith(common.NO_ERROR_PREFIXES):
                break
            errors.append(response)
        return errors

    def _require_connected(self) -> None:
        if self._instrument is None:
            raise RuntimeError("Instrument session is not connected. Call connect() first.")
