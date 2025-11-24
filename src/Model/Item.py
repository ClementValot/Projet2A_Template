from typing import Literal

from pydantic import Field

from .Orderable import Orderable


class Item(Orderable):
    """
    Represents an item/product in the system.

    Attributes
    ----------
        id_item (int): Unique identifier for the item.
        product_id (int): Identifier of the item as an orderable
        name (str): Name of the item.
        price (float): Price of the item (>= 0).
        item_type (str): Category or type of item.
        description (str): Description of the item.
        stock (int): Current stock quantity (>= 0).
    """

    item_id: int
    orderable_id: int
    item_name: str
    item_price: float = Field(gt=0, description="[Item] Price must be > 0.")
    item_type: Literal["Starter", "Main course", "Dessert", "Side dish", "Drink"]
    item_description: str
    item_stock: int = Field(ge=0, description="[Item] Stock must be >= 0.")

    def __init__(self, **args):
        args["orderable_type"] = "item"
        super().__init__(**args)
        self.is_in_menu = True if self.is_in_menu and self.check_availability() else False

    def __hash__(self) -> int:
        return hash(self.orderable_id)

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        return self.orderable_id == other.orderable_id

    def check_availability(self) -> bool:
        """
        Check that stock are available and that item is in the menu

        Return
        ------
        bool:
            True if all the conditions are met
        """
        return self.item_stock > 0

    def check_stock(self, quantity: int) -> bool:
        """
        Checks if an item is available and if there is enough of it to be added
        to an order

        Parameters
        ----------
        quantity : int
            Quantity to be added to the order

        Returns
        -------
        bool
            True if the item is avaliable (both in stock and stock>0) and
            the quanity to be ordered is <= to the stock,
            False otherwise
        """
        return self.item_stock - quantity >= 0

    @property
    def price(self) -> float:
        return self.item_price
