"""IEEE-488.2 / SCPI common commands.

These five commands are standard across virtually all SCPI instruments and are
the ONLY commands this project is allowed to assume without discovery evidence
(SPEC.MD section 32, item 11). Every CMP180-specific command (generator, WLAN
TX measurement, results, ...) must come from configs/scpi_command_map.yaml and
must never be hardcoded here.
"""

IDENTIFY = "*IDN?"
OPTIONS = "*OPT?"
CLEAR_STATUS = "*CLS"
OPERATION_COMPLETE = "*OPC?"
SYSTEM_ERROR = "SYST:ERR?"

NO_ERROR_PREFIXES = ("+0,", "0,")
