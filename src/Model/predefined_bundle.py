from src.Model.abstract_bundle import AbstractBundle
from src.Model.item import Item


class PredefinedBundle(AbstractBundle):
    """
    A bundle with a predefined price and a fixed list of items.

    Attributes:
        composition (list[Item]): Items contained in the bundle.
        price (float): Predefined total price.
    """

    composition: list[Item]
    price: float

    def compute_price(self) -> float:
        """Price is predefined for this bundle."""
        return self.price

    def compute_description(self) -> str:
        """Return descriptions of all items in the bundle."""
        descriptions = []
        for item in self.composition:
            if item.description:
                descriptions.append(f"{item.name}: {item.description}")
            else:
                descriptions.append(f"{item.name}")
        return ", ".join(descriptions)
