import pytest
from pydantic_core import ValidationError

from src.Model.address import Address


def test_address_ok():
    addr = Address(city="Rennes", postal_code=35000, street_name="Rue X", street_number=12)

    assert addr.city == "Rennes"
    assert addr.postal_code == 35000
    assert addr.street_number == 12


def test_address_invalid_street_number():
    with pytest.raises(ValidationError):
        Address(city="Rennes", postal_code=35000, street_name="Rue X", street_number={"bad": "type"})
