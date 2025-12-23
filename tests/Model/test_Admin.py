from datetime import date

import pytest
from pydantic_core import ValidationError

from src.Model.address import Address
from src.Model.admin import Admin
from src.Model.customer import Customer
from src.Model.order import Order


def test_admin_ok():
    cust = Customer(
        id_user=1,
        username="john",
        hash_password="h",
        salt="s",
        sign_up_date=date.today(),
    )

    addr = Address(city="Rennes", postal_code=35000, street_name="Rue X", street_number=7)

    order = Order(
        id_order=1,
        customer=cust,
        address=addr,
        items=[],
        status="pending",
    )

    admin = Admin(
        id_user=1,
        username="admin",
        hash_password="h",
        salt="s",
        adress=addr,
        queue=[order],
    )

    assert admin.id_user == 1
    assert admin.username == "admin"
    assert len(admin.queue) == 1
    assert admin.queue[0].status == "pending"


def test_admin_invalid_id():
    with pytest.raises(ValidationError):
        Admin(
            id_user="x",
            username="admin",
            hash_password="h",
            salt="s",
            adress=None,
            queue=[],
        )
