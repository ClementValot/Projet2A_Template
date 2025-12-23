from typing import Optional

from pydantic import BaseModel


class Address(BaseModel):
    """
    Address of a customer for a delivery.

    Attributes:
        id_address (Optional[int]): Unique identifier for the address.
        city (str): Name of the city.
        postal_code (int): Postal code of the city.
        street_name (str): Name of the street.
        street_number (Optional[str | int]): Street number if exists.
    """

    id_address: Optional[int] = None
    city: str
    postal_code: int
    street_name: str
    street_number: Optional[str | int] = None
