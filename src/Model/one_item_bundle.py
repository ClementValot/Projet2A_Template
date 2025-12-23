from typing import List

from pydantic import Field

from src.Model.abstract_bundle import AbstractBundle
from src.Model.item import Item


class OneItemBundle(AbstractBundle):
    """
    A bundle to wrap a single item and use bundle logic.

    Attributes:
        composition (list[Item]): one item in a list for bundle logic.
    """
    composition: List[Item] = Field(default_factory=list)

    def compute_price(self) -> float:
        """Price is the single item price."""
        if not self.composition:
            return 0.0
        return sum(item.price for item in self.composition)
