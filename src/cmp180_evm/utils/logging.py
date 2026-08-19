import logging
from pathlib import Path

APPLICATION_LOGGER_NAME = "cmp180_evm.application"
SCPI_LOGGER_NAME = "cmp180_evm.scpi"


def setup_logging(log_dir: Path, scpi_enabled: bool = True) -> None:
    """Configure the application and SCPI loggers to write into log_dir.

    Safe to call multiple times; existing handlers are cleared first so
    repeated calls (e.g. across CLI invocations in tests) don't duplicate output.
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    app_logger = logging.getLogger(APPLICATION_LOGGER_NAME)
    app_logger.handlers.clear()
    app_logger.setLevel(logging.INFO)
    app_handler = logging.FileHandler(log_dir / "application.log", encoding="utf-8")
    app_handler.setFormatter(formatter)
    app_logger.addHandler(app_handler)
    app_logger.propagate = False

    scpi_logger = logging.getLogger(SCPI_LOGGER_NAME)
    scpi_logger.handlers.clear()
    scpi_logger.setLevel(logging.DEBUG if scpi_enabled else logging.CRITICAL + 1)
    scpi_handler = logging.FileHandler(log_dir / "scpi.log", encoding="utf-8")
    scpi_handler.setFormatter(formatter)
    scpi_logger.addHandler(scpi_handler)
    scpi_logger.propagate = False


def get_application_logger() -> logging.Logger:
    return logging.getLogger(APPLICATION_LOGGER_NAME)


def get_scpi_logger() -> logging.Logger:
    return logging.getLogger(SCPI_LOGGER_NAME)
