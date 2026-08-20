import csv
import json

import pytest

from cmp180_evm.web.mock_service import (
    build_frequency_points,
    build_power_points,
    save_mock_run,
    simulate_point,
)
from cmp180_evm.web.server import (
    Cmp180WebHandler,
    validate_cable_route,
    validate_hardware_bind,
)


def test_frequency_points_are_inclusive_and_bounded():
    assert build_frequency_points(5_925e6, 5_965e6, 20e6) == [5_925e6, 5_945e6, 5_965e6]
    with pytest.raises(ValueError, match="11-point"):
        build_frequency_points(1, 12, 1)


def test_power_points_are_inclusive_and_bounded():
    assert build_power_points(-50, -40, 5) == [-50, -45, -40]
    with pytest.raises(ValueError, match="11-point"):
        build_power_points(-12, -1, 1)


def test_simulation_is_deterministic_and_labeled():
    first = simulate_point(6_105e6, 320e6, -40)
    second = simulate_point(6_105e6, 320e6, -40)
    assert first == second
    assert first.valid is True
    assert first.generator_power_dbm == -40


def test_simulated_evm_varies_with_power_at_fixed_frequency():
    # Power vs EVM 圖表要有意義，功率越高（越接近 -40 dBm 上限）EVM 應該越差。
    lower_power = simulate_point(6_105e6, 320e6, -60)
    higher_power = simulate_point(6_105e6, 320e6, -40)
    assert higher_power.evm_all_db > lower_power.evm_all_db


def test_mock_artifacts_include_csv_json_and_html(tmp_path):
    point = simulate_point(6_105e6, 320e6, -40)
    artifacts = save_mock_run([point], tmp_path, "unit-test")
    with open(artifacts["csv"], encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    payload = json.loads(open(artifacts["json"], encoding="utf-8").read())
    assert len(rows) == 1
    assert payload["simulated"] is True
    assert "SIMULATED" in open(artifacts["report"], encoding="utf-8").read()


def test_web_hardware_endpoint_is_locked_by_default():
    # 只有明確 --enable-hardware 啟動時，server.main 才能改變此旗標。
    assert Cmp180WebHandler.hardware_enabled is False


def test_cable_route_accepts_verified_variants_and_blocks_custom_route():
    assert validate_cable_route(" RF1.1 → RF1.5 ") == "RF1.1-RF1.5"
    with pytest.raises(ValueError, match="not hardware-verified"):
        validate_cable_route("RF1.2-RF1.6")


def test_hardware_mode_must_not_bind_to_network_interfaces():
    validate_hardware_bind("127.0.0.1", True)
    validate_hardware_bind("0.0.0.0", False)
    with pytest.raises(ValueError, match="loopback"):
        validate_hardware_bind("0.0.0.0", True)
