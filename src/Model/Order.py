from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Union

from pydantic import BaseModel

from .Bundle import Bundle
from .Item import Item


class OrderState(Enum):
    PENDING = 0
    PAID = 1
    PREPARED = 2
    DELIVERING = 3
    DELIVERED = 4
    CANCELLED = 5


class Order(BaseModel):
    """
    Represents a customer's order.

    Attributes
    ----------
        id_order (int): Unique identifier of the order.
        client_id (int): ID of the client.
        state (int, optional): Order status (0 = pending, 1 = paid, 2 = prepared,
                                3 = delivery, 4 = delivered, 5 = cancelled).
        items (Dict[Bundle | Item, int]): List of items and bundles in the order.
        date (date): Date of the order.
        time (time): Time of the order.
    """

    order_id: int
    order_customer_id: int
    order_state: OrderState = OrderState.PENDING
    order_created_at: datetime
    order_paid_at: Optional[datetime] = None
    order_orderables: Dict[Union[Bundle, Item], int]

    @property
    def order_price(self) -> float:
        """
        Calculate the price of the order (price of the item times its amount in the order)
        Return
        ------
        float:
            The total price of the order
        """
        total_price = 0.0
        for orderable, qty in self.order_orderables.items():
            total_price += orderable.price * qty

        return total_price

    @property
    def is_paid(self) -> bool:
        return self.order_state.value >= OrderState.PAID.value

    @property
    def is_prepared(self) -> bool:
        return self.order_state.value >= OrderState.PREPARED.value

    @property
    def is_delivered(self) -> bool:
        return self.order_state == OrderState.DELIVERED
