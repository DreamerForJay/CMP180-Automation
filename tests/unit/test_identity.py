import pytest

from cmp180_evm.instrument.base import validate_idn_model
from cmp180_evm.utils.exceptions import InstrumentIdentityError


def test_cmp180_real_idn_uses_cmp_model_token():
    idn = "Rohde&Schwarz,CMP,1201.0002k18/102502,6.0.50.23"
    assert validate_idn_model(idn, "CMP") == idn


def test_mock_hyphenated_model_is_accepted():
    idn = "Rohde&Schwarz,CMP-MOCK,serial,1.0"
    assert validate_idn_model(idn, "CMP") == idn


def test_model_name_elsewhere_in_idn_is_not_accepted():
    with pytest.raises(InstrumentIdentityError):
        validate_idn_model("Vendor,FSW,CMP-in-serial,1.0", "CMP")


def test_malformed_idn_is_rejected():
    with pytest.raises(InstrumentIdentityError):
        validate_idn_model("unexpected-response", "CMP")
