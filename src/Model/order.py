from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from src.Model.address import Address
from src.Model.customer import Customer
from src.Model.item import Item


class Order(BaseModel):
    """
    Represents an order placed by a customer.

    Attributes:
        id_order (Optional[int]): Unique identifier.
        customer (Customer): Customer who placed the order.
        address (Address): Delivery address.
        items (list[Item]): Items included in the order.
        price (Optional[float]): Total order price.
        status (str): Order status.
        order_date (datetime): Creation timestamp (defaults to now).
    """

    id_order: Optional[int] = None
    customer: Customer
    address: Address
    items: list[Item]
    price: Optional[float] = None
    status: Literal["in_progress", "validated", "pending", "delivered"]
    order_date: datetime = Field(default_factory=datetime.now)
