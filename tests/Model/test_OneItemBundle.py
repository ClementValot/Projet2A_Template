from src.Model.item import Item
from src.Model.one_item_bundle import OneItemBundle


def test_one_item_bundle_price_ok():
    item = Item(name="A", item_type="main", price=10)
    bundle = OneItemBundle(name="Single", composition=[item])

    assert bundle.compute_price() == 10


def test_one_item_bundle_empty():
    bundle = OneItemBundle(name="Empty")
    assert bundle.compute_price() == 0.0