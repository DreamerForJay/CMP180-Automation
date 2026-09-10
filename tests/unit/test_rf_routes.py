import pytest

from cmp180_evm.workflow.rf_routes import (
    normalize_route,
    parse_route,
    route_is_hil_verified,
    validate_route,
)

INSTALLED = ["RF1.1", "RF1.2", "RF1.5", "RF1.6", "RF2.1"]
# Generator 輸出無法遠端切換，只有 workspace 既有的 RF1.1 驅動得動。
COMMANDABLE_GENERATOR = ["RF1.1"]
HIL_VERIFIED = ["RF1.1-RF1.5"]


def check(value):
    return validate_route(
        value,
        installed_ports=INSTALLED,
        commandable_generator_ports=COMMANDABLE_GENERATOR,
    )


def test_operator_text_variants_normalize_to_one_canonical_route():
    for value in ("rf1.1-rf1.5", " RF1.1 - RF1.5 ", "RF1.1→RF1.5"):
        assert normalize_route(value) == "RF1.1-RF1.5"
        assert check(value).label == "RF1.1-RF1.5"


def test_route_splits_into_generator_and_analyzer_ports():
    route = parse_route("RF1.1-RF1.5")
    assert route.generator_port == "RF1.1"
    assert route.analyzer_port == "RF1.5"


@pytest.mark.parametrize("value", ["", None, "   "])
def test_empty_route_is_refused(value):
    with pytest.raises(ValueError, match="Select or enter a cable route"):
        check(value)


@pytest.mark.parametrize("value", ["RF1.1", "RF1.1-RF1.5-RF2.1", "RF1.1-"])
def test_malformed_route_is_refused(value):
    with pytest.raises(ValueError, match="GENERATOR-ANALYZER form"):
        check(value)


def test_same_port_for_generator_and_analyzer_is_refused():
    with pytest.raises(ValueError, match="must be different"):
        check("RF1.1-RF1.1")


def test_port_absent_from_this_instrument_is_refused():
    with pytest.raises(ValueError, match="Port RF2.8 is not present"):
        check("RF1.1-RF2.8")


def test_analyzer_port_without_hil_evidence_still_executes():
    """Analyzer 端可由 ROUTe:WLAN:MEAS:SPATh 切換，未做過 HIL 也必須跑得起來蒐證。"""
    route = check("RF1.1-RF1.6")
    assert route.generator_port == "RF1.1"
    assert route.analyzer_port == "RF1.6"
    # 執行不受阻，但證據等級仍必須誠實標示。
    assert route_is_hil_verified(route.label, HIL_VERIFIED) is False


def test_generator_port_that_cannot_be_switched_remotely_is_refused():
    """沒有已驗證的 generator RF path setter，輸出切不過去，硬送只會量到空氣。"""
    with pytest.raises(ValueError, match="cannot be selected remotely"):
        check("RF1.2-RF1.5")


def test_calibration_style_check_skips_the_generator_capability_gate():
    """校正不送 RF，只需要 port 存在且兩端不同。"""
    route = validate_route("RF1.2-RF1.5", installed_ports=INSTALLED)
    assert route.label == "RF1.2-RF1.5"


def test_hil_verification_is_a_label_not_a_gate():
    assert route_is_hil_verified(" rf1.1 → rf1.5 ", HIL_VERIFIED) is True
    assert route_is_hil_verified("RF1.1-RF1.6", HIL_VERIFIED) is False
