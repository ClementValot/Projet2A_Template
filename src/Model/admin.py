from typing import Optional

from pydantic import ConfigDict

from src.Model.abstract_user import AbstractUser
from src.Model.address import Address
from src.Model.order import Order


class Admin(AbstractUser):
    """
    Inherits from AbstractUser to model Admin Users.

    Attributes:
        name(str): Civil name of the admin.
        adress(Optional[Address]): Address of EJR or other.
        queue(list[Order]) : List of the orders to be done.
        phone_number(Optional[str]): Phone number of the Admin
    """

    name: str = ""
    adress: Optional[Address] = None
    queue: list[Order] = []
    phone_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
