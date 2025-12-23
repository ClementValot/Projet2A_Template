import pytest
from pydantic_core import ValidationError

from src.Model.item import Item


def test_item_ok():
    it = Item(name="Burger", item_type="main", price=5.0)
    assert it.price == 5.0


def test_item_invalid_price():
    with pytest.raises(ValidationError):
        Item(name="Burger", item_type="main", price="five")


def test_item_invalid_type():
    with pytest.raises(ValidationError):
        Item(name="Burger", item_type="unknown_type", price=5.0)