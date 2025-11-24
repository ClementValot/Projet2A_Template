from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Delivery(BaseModel):
    """
    Represents a delivery assignment for an order.

    Attributes
    ----------
        delivery_order_id (int): Unique identifier of the order to be delivered.
        delivery_driver_id (int): Unique identifier of the driver assigned to the delivery.
        delivery_state (int, optional): Delivery status
            (0 = pending, 1 = being delivered, 2 = delivered)
    """

    delivery_order_id: int
    delivery_driver_id: int
    delivery_created_at: datetime
    delivery_state: Optional[int] = None
