import pytest

from cmp180_evm.workflow.rf_routes import normalize_route, parse_route, validate_route

INSTALLED = ["RF1.1", "RF1.2", "RF1.5", "RF2.1"]
APPROVED = ["RF1.1-RF1.5"]


def check(value):
    return validate_route(value, approved_routes=APPROVED, installed_ports=INSTALLED)


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


def test_installed_but_unapproved_route_still_blocks_rf():
    # RF1.2 存在於儀器上，但該路徑未完成 HIL，仍不得送 RF。
    with pytest.raises(ValueError, match="not hardware-verified"):
        check("RF1.1-RF1.2")


def test_adding_a_verified_route_to_the_profile_unlocks_it():
    """新增一條已完成 HIL 的 route 只需改 capability profile，不必改程式。"""
    unlocked = validate_route(
        "RF1.2-RF2.1",
        approved_routes=["RF1.1-RF1.5", "RF1.2-RF2.1"],
        installed_ports=INSTALLED,
    )
    assert unlocked.generator_port == "RF1.2"
    assert unlocked.analyzer_port == "RF2.1"
