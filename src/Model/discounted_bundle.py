from typing import List, Optional

from pydantic import Field

from src.Model.abstract_bundle import AbstractBundle
from src.Model.item import Item


class DiscountedBundle(AbstractBundle):
    """
    A bundle whose price is computed with a discount applied.

    Attributes:
        required_item_types (list[str]): Types of items required in the bundle.
        discount (float): Discount applied to the total price.
        composition (list[Item]): Items included in the bundle.
    """

    required_item_types: List[str]
    discount: float
    composition: Optional[List[Item]] = Field(default_factory=list)

    def compute_price(self) -> float:
        """Sum the price of all items and apply discount."""
        total = sum(item.price for item in self.composition)
        return total * (1 - self.discount)
