import pytest
from pydantic_core import ValidationError

from src.Model.Address import Address


def test_address_constructor_ok():
    ensai = Address(
        address_id=1,
        address_number=51,
        address_street="Rue Blaise Pascal",
        address_city="Bruz",
        address_postal_code=35170,
        address_country="France",
    )

    assert isinstance(ensai, Address)
    assert ensai.address_id == 1
    assert ensai.address_number == 51
    assert ensai.address_street == "Rue Blaise Pascal"
    assert ensai.address_city == "Bruz"
    assert ensai.address_postal_code == 35170
    assert ensai.address_country == "France"


def test_address_constructor_throws_on_incorrect_input():
    with pytest.raises(ValidationError) as exception_info:
        Address(
            address_number="fifty-one",
            address_street="Rue Blaise Pascal",
            address_city="Bruz",
            address_postal_code=35170,
            address_country="France",
        )
    assert "number" in str(
        exception_info.value
    ) and "Input should be a valid integer, unable to parse string as an integer" in str(
        exception_info.value
    )


def test_get_attributes():
    ensai = Address(
        address_id=1,
        address_number=51,
        address_street="Rue Blaise Pascal",
        address_city="Bruz",
        address_postal_code=35170,
        address_country="France",
    )

    attributes = ensai.get_attributes()

    expected_attributes = {
        "address_id": 1,
        "address_number": 51,
        "address_street": "Rue Blaise Pascal",
        "address_city": "Bruz",
        "address_postal_code": 35170,
        "address_country": "France",
    }

    assert attributes == expected_attributes
    assert isinstance(attributes, dict)


def test_str_representation():
    ensai = Address(
        address_id=1,
        address_number=51,
        address_street="Rue Blaise Pascal",
        address_city="Bruz",
        address_postal_code=35170,
        address_country="France",
    )

    str_repr = str(ensai)
    expected_str = "51 Rue Blaise Pascal, 35170 Bruz, France"

    assert str_repr == expected_str
