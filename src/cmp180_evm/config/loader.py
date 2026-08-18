from pathlib import Path
from typing import Any

import yaml

from cmp180_evm.config.models import InstrumentConfig, WlanBaselineConfig


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def load_instrument_config(path: Path) -> InstrumentConfig:
    return InstrumentConfig.model_validate(load_yaml(path))


def load_wlan_baseline_config(path: Path) -> WlanBaselineConfig:
    return WlanBaselineConfig.model_validate(load_yaml(path))


def detect_config_kind(path: Path) -> str:
    """Guess which model a YAML file matches, for CLI commands that accept either."""
    data = load_yaml(path)
    if "instrument" in data and "routing" in data:
        return "instrument"
    if "signal" in data and "test" in data:
        return "wlan_baseline"
    raise ValueError(
        f"Could not determine config kind for {path}: "
        "expected top-level 'instrument'+'routing' or 'test'+'signal' keys."
    )
