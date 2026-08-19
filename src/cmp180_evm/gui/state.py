"""Persisted GUI state (last-used config paths + mock checkbox).

Deliberately Tk-free so it is unit-testable without a display or a
tk.Tk() instance. gui/app.py is the only caller.
"""

import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class GuiState:
    instrument_config_path: str
    wlan_config_path: str
    use_mock: bool = True


def default_state_path() -> Path:
    """Mirrors gui/app.py's _default_configs_dir() convention.

    Frozen (.exe): state file lives next to the exe, alongside configs/,
    consistent with the existing "ship editable stuff next to the exe"
    pattern. Source mode: the repo working tree is not a reliable
    writable/user-scoped location (may be read-only, is git-tracked), so
    use %APPDATA% instead, with a non-Windows fallback purely so
    tests/dev machines don't crash.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "gui_state.json"
    appdata = os.getenv("APPDATA")
    base = Path(appdata) if appdata else Path.home() / ".config"
    return base / "cmp180-evm" / "gui_state.json"


def load_state(path: Path, defaults: GuiState) -> GuiState:
    """Never raises. Missing file, unreadable file, corrupt/partial JSON
    all fall back to `defaults` (today's hardcoded example-config paths)."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return GuiState(
            instrument_config_path=str(
                raw.get("instrument_config_path", defaults.instrument_config_path)
            ),
            wlan_config_path=str(raw.get("wlan_config_path", defaults.wlan_config_path)),
            use_mock=bool(raw.get("use_mock", defaults.use_mock)),
        )
    except (FileNotFoundError, OSError, json.JSONDecodeError, TypeError, ValueError, AttributeError):
        return defaults


def save_state(path: Path, state: GuiState) -> None:
    """Best-effort. A persistence failure must never crash the GUI."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")
    except OSError:
        pass
