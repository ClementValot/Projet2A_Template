from typing import Literal, Optional

from pydantic import BaseModel


class Item(BaseModel):
    """
    Represents an item that can be included in orders or bundles.

    Attributes:
        id_item (Optional[int]): Unique identifier of the item.
        name (str): Item name.
        item_type (str): Category of the item.
        price (float): Price of the item.
        description (Optional[str]): Optional description.
        stock (Optional[int]): Stock available.
        availability (Optional[bool]): If the item is available for sale.
    """

    id_item: Optional[int] = None
    name: str
    item_type: Literal["main", "starter", "drink", "side", "dessert"]
    price: float
    description: Optional[str] = None
    stock: Optional[int] = None
    availability: Optional[bool] = True
