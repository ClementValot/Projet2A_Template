from pydantic import BaseModel


class APIItem(BaseModel):
    """
    Item representation in the API
    """

    item_id: int
    orderable_id: int
    item_name: str
    item_price: float
    item_type: str
    item_stock: int
    is_in_menu: bool

    def __hash__(self):
        return hash(self.item_id)

    def __eq__(self, other):
        return isinstance(other, APIItem) and self.item_id == other.item_id

    def __repr__(self):
        return (
            f"item_name={self.item_name}, item_price={self.item_price}, item_type={self.item_type}"
        )

    @classmethod
    def from_item(cls, item):
        return cls(
            item_id=item.item_id,
            orderable_id=item.orderable_id,
            item_name=item.item_name,
            item_price=item.item_price,
            item_type=item.item_type,
            item_stock=item.item_stock,
            is_in_menu=item.is_in_menu,
        )
