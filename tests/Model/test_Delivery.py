from datetime import datetime

import pytest
from pydantic_core import ValidationError

from src.Model.address import Address
from src.Model.customer import Customer
from src.Model.delivery import Delivery
from src.Model.driver import Driver
from src.Model.item import Item
from src.Model.order import Order


def test_delivery_constructor_ok():
    customer = Customer(
        id_user=1,
        username="john_doe",
        hash_password="secure",
        salt="xx",
        phone_number="0606060606",
    )

    driver = Driver(
        id_user=2,
        username="driver_1",
        hash_password="strong_pwd",
        salt="yy",
        name="Jean Dupont",
        phone_number="0610101010",
        vehicle_type="bike",
        availability=True,
    )

    address = Address(
        city="Rennes",
        postal_code=35000,
        street_name="Rue de la Galette",
        street_number=12,
    )

    item = Item(
        name="Galette",
        item_type="main",
        price=5.0,
    )

    order = Order(
        id_order=1,
        customer=customer,
        address=address,
        items=[item],
        status="pending",
    )

    delivery = Delivery(
        id_delivery=1,
        driver=driver,
        orders=[order],
        status="in_progress",
        delivery_time=datetime(2025, 1, 2),
    )

    assert delivery.id_delivery == 1
    assert delivery.driver.name == "Jean Dupont"
    assert delivery.orders[0].customer.username == "john_doe"
    assert delivery.status == "in_progress"
    assert isinstance(delivery.delivery_time, datetime)


def test_delivery_invalid_driver_type_raises_validationerror():
    customer = Customer(
        id_user=1,
        username="john_doe",
        hash_password="secure",
        salt="xx",
    )

    address = Address(
        city="Rennes",
        postal_code=35000,
        street_name="Rue de la Galette",
        street_number=12,
    )

    order = Order(
        id_order=1,
        customer=customer,
        address=address,
        items=[],
        status="pending",
    )

    with pytest.raises(ValidationError):
        Delivery(
            id_delivery=1,
            driver="invalid_driver",
            orders=[order],
            status="in_progress",
            delivery_time=datetime(2025, 1, 2),
        )


def test_delivery_invalid_status_raises_validationerror():
    customer = Customer(
        id_user=1,
        username="john_doe",
        hash_password="secure",
        salt="xx",
    )

    driver = Driver(
        id_user=2,
        username="driver_1",
        hash_password="strong_pwd",
        salt="yy",
        name="Jean Dupont",
        vehicle_type="bike",
        availability=True,
    )

    address = Address(
        city="Rennes",
        postal_code=35000,
        street_name="Rue de la Galette",
        street_number=12,
    )

    order = Order(
        id_order=1,
        customer=customer,
        address=address,
        items=[],
        status="pending",
    )

    with pytest.raises(ValidationError):
        Delivery(
            id_delivery=1,
            driver=driver,
            orders=[order],
            status="archived",
            delivery_time=datetime(2025, 1, 2),
        )