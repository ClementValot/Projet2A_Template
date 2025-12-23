from datetime import date
from typing import Optional

from pydantic import ConfigDict, Field

from src.Model.abstract_user import AbstractUser


class Customer(AbstractUser):
    """
    Inherits from AbstractUser to model Customers.

    Attributes:
        name(str): Civil name of the customer.
        sign_up_date(Optional[datetime]): Date of last authentification.
        phone_number(Optional[str]): Phone number of the Admin.
        model_config(ConfigDict): TypedDict for configuring Pydantic behaviour.
    """

    name: str = ""
    sign_up_date: date = Field(default_factory=date.today)
    phone_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
