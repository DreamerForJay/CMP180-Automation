"""Parser for the CMP180 28-field OFDM SISO modulation response."""

from __future__ import annotations

import csv


RESULT_FIELDS = (
    "reliability", "out_of_tolerance_percent", "mcs_index", "modulation",
    "payload_symbols", "measured_symbols", "payload_bytes", "guard_interval",
    "spatial_streams", "space_time_streams", "burst_rate_percent",
    "power_backoff_db", "burst_power_dbm", "peak_power_dbm", "crest_factor_db",
    "evm_all_carriers_db", "evm_data_carriers_db", "evm_pilot_carriers_db",
    "frequency_error_hz", "clock_error_ppm", "iq_offset_db", "dc_power_dbm",
    "gain_imbalance_db", "quadrature_error_deg", "ltf_power_dbm",
    "data_power_dbm", "preamble_power_dbm", "common_phase_error_deg",
)


def parse_result(response: str) -> dict[str, str]:
    """Parse one aggregate response while preserving instrument text values."""
    values = next(csv.reader([response], skipinitialspace=True))
    if len(values) != len(RESULT_FIELDS):
        raise ValueError(f"Expected {len(RESULT_FIELDS)} fields, received {len(values)}")
    # 保留原始字串，避免 INV/NAN 等儀器 sentinel 被錯誤轉成數字零。
    return dict(zip(RESULT_FIELDS, values, strict=True))

