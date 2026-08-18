class Cmp180Error(Exception):
    """Base class for all cmp180_evm errors."""


class ScpiCommandNotConfiguredError(Cmp180Error):
    """Raised when a required SCPI command is not present in scpi_command_map.yaml."""

    def __init__(self, command_name: str) -> None:
        self.command_name = command_name
        super().__init__(
            f"SCPI command '{command_name}' is not configured. "
            "Run SCPI discovery and update scpi_command_map.yaml."
        )


class InstrumentIdentityError(Cmp180Error):
    """Raised when the connected instrument's *IDN? does not match the expected CMP180."""

    def __init__(self, expected_model_contains: str, actual_idn: str) -> None:
        self.expected_model_contains = expected_model_contains
        self.actual_idn = actual_idn
        super().__init__(
            f"Expected instrument model '{expected_model_contains}' but received:\n"
            f"{actual_idn}"
        )


class ConfigValidationError(Cmp180Error):
    """Raised when a loaded configuration fails domain-level validation."""


class SafetyGuardError(Cmp180Error):
    """Raised when an RF-affecting action is attempted without passing required safety checks."""
