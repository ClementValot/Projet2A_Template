from datetime import datetime

import pytest
from pydantic_core import ValidationError

from src.Model.address import Address
from src.Model.customer import Customer
from src.Model.item import Item
from src.Model.order import Order


def test_order_ok():
    cust = Customer(
        id_user=1,
        username="u",
        hash_password="h",
        salt="s",
    )

    addr = Address(city="Paris", postal_code=75000, street_name="Rue Y", street_number=10)

    item = Item(name="A", item_type="main", price=3.0)

    order = Order(
        customer=cust,
        address=addr,
        items=[item],
        status="pending",
    )

    assert order.status == "pending"
    assert order.items[0].price == 3.0
    assert isinstance(order.order_date, datetime)


def test_order_invalid_status():
    cust = Customer(
        id_user=1,
        username="u",
        hash_password="h",
        salt="s",
    )

    addr = Address(city="Paris", postal_code=75000, street_name="Rue Y", street_number=10)

    with pytest.raises(ValidationError):
        Order(
            customer=cust,
            address=addr,
            items=[],
            status="cancelled",
        )