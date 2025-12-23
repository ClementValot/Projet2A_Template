from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel

from src.Model.driver import Driver
from src.Model.order import Order


class Delivery(BaseModel):
    """
    Delivery to be done by a Driver.

    Attributes:
        id_delivery (Optional[int]): Unique identifier for the delivery.
        driver(Optional[Driver]): Driver assigned to the delivery.
        orders(list[Order]): Orders that are part of the delivery.
        status(str) : Indicates if the Delivery is pending, assignated to a Driver or accomplished.
        delivery_time(Optional[datetime]): Time of the Delivery end.
    """

    id_delivery: Optional[int] = None
    driver: Optional[Driver]
    orders: list[Order]
    status: Literal["delivered", "in_progress"]
    delivery_time: Optional[datetime] = None
