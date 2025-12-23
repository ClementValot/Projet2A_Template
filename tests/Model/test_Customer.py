from datetime import date

import pytest
from pydantic_core import ValidationError

from src.Model.customer import Customer


def test_customer_constructor_ok():
    c = Customer(
        id_user=1,
        username="alice",
        hash_password="hashed_pwd",
        salt="xyz",
        sign_up_date=date(2025, 1, 1),
        phone_number="0600000000",
        name="Alice Dupont",
    )

    assert c.id_user == 1
    assert c.username == "alice"
    assert c.phone_number == "0600000000"
    assert c.sign_up_date == date(2025, 1, 1)


def test_customer_invalid_id_raises():
    with pytest.raises(ValidationError):
        Customer(
            id_user="wrong",
            username="bob",
            hash_password="pwd",
            salt="s",
            sign_up_date=date(2025, 1, 2),
        )
