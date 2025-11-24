from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel

from .Order import Order, OrderState


class APIOrder(BaseModel):
    """
    Order representation in the API
    """
    order_id: int
    order_customer_id: int
    order_state: OrderState
    order_price: float
    order_created_at: datetime
    order_paid_at: Optional[datetime]
    order_orderables: Dict[str, int]

    @classmethod
    def from_order(cls, order: Order):
        orderables = {}
        for orderable, qty in order.order_orderables.items():
            orderables[str(orderable.orderable_id)] = qty

        return cls(
            order_id=order.order_id,
            order_customer_id=order.order_customer_id,
            order_state=order.order_state,
            order_price=round(order.order_price, 2),
            order_orderables=orderables,
            order_created_at=order.order_created_at,
            order_paid_at=order.order_paid_at,
        )
