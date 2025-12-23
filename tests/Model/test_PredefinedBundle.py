import pytest
from pydantic_core import ValidationError

from src.Model.item import Item
from src.Model.predefined_bundle import PredefinedBundle


def test_predefined_bundle_ok():
    item1 = Item(name="Galette", item_type="main", price=4.5, description="Sarrasin complète")
    item2 = Item(name="Cidre", item_type="drink", price=3.0)

    bundle = PredefinedBundle(
        id_bundle=10,
        name="Menu Breton",
        composition=[item1, item2],
        price=6.0,
    )

    assert bundle.id_bundle == 10
    assert bundle.name == "Menu Breton"
    assert bundle.price == 6.0
    assert len(bundle.composition) == 2


def test_predefined_bundle_invalid_price():
    item = Item(name="Galette", item_type="main", price=4.5)

    with pytest.raises(ValidationError):
        PredefinedBundle(
            id_bundle=10,
            name="Menu Breton",
            composition=[item],
            price="six euros",
        )


def test_predefined_bundle_description():
    item1 = Item(name="Galette", item_type="main", price=4.5, description="Complète")
    item2 = Item(name="Cidre", item_type="drink", price=3.0)

    bundle = PredefinedBundle(
        id_bundle=1,
        name="Menu",
        composition=[item1, item2],
        price=7.0,
    )

    assert bundle.compute_description() == "Galette: Complète, Cidre"
