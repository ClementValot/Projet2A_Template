from typing import Optional, Literal

from pydantic import ConfigDict

from src.Model.abstract_user import AbstractUser


class Driver(AbstractUser):
    """
    Represents a driver responsible for deliveries.

    Attributes:
        name (str): Driver’s name.
        phone_number (str): Contact phone number.
        vehicle_type (str): Type of vehicle (car, bike, scooter…).
        availability (bool): Whether the driver is available.
    """

    name: str
    phone_number: Optional[str] = None
    vehicle_type: Literal["car", "bike", "scooter"]
    availability: bool

    model_config = ConfigDict(from_attributes=True)
