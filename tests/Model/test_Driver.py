import pytest
from pydantic_core import ValidationError

from src.Model.driver import Driver


def test_driver_ok():
    d = Driver(
        id_user=1,
        username="driver",
        hash_password="h",
        salt="s",
        name="Bob",
        phone_number="06000000",
        vehicle_type="bike",
        availability=True,
    )

    assert d.vehicle_type == "bike"
    assert d.availability is True


def test_driver_invalid_availability():
    with pytest.raises(ValidationError):
        Driver(
            id_user=1,
            username="driver",
            hash_password="h",
            salt="s",
            name="Bob",
            phone_number="06000000",
            vehicle_type="car",
            availability="indeed",
        )


def test_driver_invalid_vehicle_type():
    with pytest.raises(ValidationError):
        Driver(
            id_user=1,
            username="driver",
            hash_password="h",
            salt="s",
            name="Bob",
            phone_number="06000000",
            vehicle_type="truck",
            availability=True,
        )