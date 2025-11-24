from datetime import datetime
from typing import Dict

from pydantic import BaseModel

from .APIItem import APIItem


class APIBundle(BaseModel):
    """
    Bundle representation in the API
    """
    bundle_id: int
    orderable_id: int
    bundle_name: str
    bundle_reduction: int
    bundle_availability_start_date: datetime
    bundle_availability_end_date: datetime
    bundle_items: Dict[APIItem, int]
    is_in_menu: bool

    def __hash__(self):
        return hash((self.bundle_name, self.bundle_description))

    def __eq__(self, other):
        return (
            isinstance(other, APIBundle)
            and self.bundle_name == other.bundle_name
            and self.bundle_description == other.bundle_description
            and self.bundle_items == other.bundle_items
        )

    def __repr__(self):
        return (
            f"bundle_name={self.bundle_name}, "
            f"bundle_description={self.bundle_description}, "
            f"bundle_items={self.bundle_items} "
        )

    @classmethod
    def from_bundle(cls, bundle):
        bundle_items_dict = {}
        for item, quantity in bundle.bundle_items.items():
            bundle_items_dict[str(item.item_id)] = quantity

        return cls(
            bundle_id=bundle.bundle_id,
            orderable_id=bundle.orderable_id,
            bundle_name=bundle.bundle_name,
            bundle_reduction=bundle.bundle_reduction,
            bundle_availability_start_date=bundle.bundle_availability_start_date,
            bundle_availability_end_date=bundle.bundle_availability_end_date,
            bundle_items=bundle_items_dict,
            is_in_menu=bundle.is_in_menu,
        )
