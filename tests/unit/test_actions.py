from pathlib import Path

from cmp180_evm import actions

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = REPO_ROOT / "configs"


def test_validate_config_instrument_ok():
    result = actions.validate_config(CONFIGS_DIR / "instrument.example.yaml")
    assert result.ok
    assert result.kind == "instrument"


def test_validate_config_wlan_baseline_ok():
    result = actions.validate_config(CONFIGS_DIR / "wlan_baseline.example.yaml")
    assert result.ok
    assert result.kind == "wlan_baseline"


def test_validate_config_missing_file():
    result = actions.validate_config(CONFIGS_DIR / "does_not_exist.yaml")
    assert not result.ok


def test_dry_run_steps_never_touches_instrument():
    steps = actions.dry_run_steps(
        CONFIGS_DIR / "instrument.example.yaml",
        CONFIGS_DIR / "wlan_baseline.example.yaml",
    )
    assert steps[0].startswith("[DRY RUN]")
    assert any("RF1.1" in step for step in steps)
    assert any("RF1.5" in step for step in steps)
    assert steps[-1] == "RF OFF"


def test_connection_with_mock_succeeds():
    result = actions.test_connection(CONFIGS_DIR / "instrument.example.yaml", use_mock=True)
    assert result.ok
    assert result.idn is not None and "CMP180" in result.idn
    assert result.errors == []
