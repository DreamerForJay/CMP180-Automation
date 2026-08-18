from pathlib import Path

from cmp180_evm.gui import state as gui_state

DEFAULTS = gui_state.GuiState(
    instrument_config_path="configs/instrument.example.yaml",
    wlan_config_path="configs/wlan_baseline.example.yaml",
    use_mock=True,
)


def test_save_then_load_round_trip(tmp_path: Path):
    path = tmp_path / "gui_state.json"
    saved = gui_state.GuiState(
        instrument_config_path="C:/foo/instrument.yaml",
        wlan_config_path="C:/foo/wlan.yaml",
        use_mock=False,
    )
    gui_state.save_state(path, saved)

    loaded = gui_state.load_state(path, DEFAULTS)

    assert loaded == saved


def test_load_missing_file_returns_defaults(tmp_path: Path):
    path = tmp_path / "does_not_exist.json"

    loaded = gui_state.load_state(path, DEFAULTS)

    assert loaded == DEFAULTS


def test_load_corrupt_json_returns_defaults(tmp_path: Path):
    path = tmp_path / "gui_state.json"
    path.write_text("{not valid json", encoding="utf-8")

    loaded = gui_state.load_state(path, DEFAULTS)

    assert loaded == DEFAULTS


def test_load_non_object_json_returns_defaults(tmp_path: Path):
    path = tmp_path / "gui_state.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")

    loaded = gui_state.load_state(path, DEFAULTS)

    assert loaded == DEFAULTS


def test_load_partial_json_fills_in_defaults(tmp_path: Path):
    path = tmp_path / "gui_state.json"
    path.write_text('{"instrument_config_path": "C:/only/instrument.yaml"}', encoding="utf-8")

    loaded = gui_state.load_state(path, DEFAULTS)

    assert loaded.instrument_config_path == "C:/only/instrument.yaml"
    assert loaded.wlan_config_path == DEFAULTS.wlan_config_path
    assert loaded.use_mock == DEFAULTS.use_mock


def test_save_creates_parent_directories(tmp_path: Path):
    path = tmp_path / "nested" / "dir" / "gui_state.json"

    gui_state.save_state(path, DEFAULTS)

    assert path.exists()
    assert gui_state.load_state(path, DEFAULTS) == DEFAULTS


def test_default_state_path_frozen_uses_exe_directory(monkeypatch, tmp_path: Path):
    fake_exe = tmp_path / "dist" / "CMP180-EVM-GUI.exe"
    fake_exe.parent.mkdir(parents=True)
    fake_exe.touch()
    monkeypatch.setattr("sys.frozen", True, raising=False)
    monkeypatch.setattr("sys.executable", str(fake_exe))

    path = gui_state.default_state_path()

    assert path == fake_exe.resolve().parent / "gui_state.json"


def test_default_state_path_source_uses_appdata(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("sys.frozen", False, raising=False)
    monkeypatch.setenv("APPDATA", str(tmp_path))

    path = gui_state.default_state_path()

    assert path == tmp_path / "cmp180-evm" / "gui_state.json"


def test_default_state_path_source_without_appdata_falls_back_to_home(monkeypatch):
    monkeypatch.setattr("sys.frozen", False, raising=False)
    monkeypatch.delenv("APPDATA", raising=False)

    path = gui_state.default_state_path()

    assert path == Path.home() / ".config" / "cmp180-evm" / "gui_state.json"
