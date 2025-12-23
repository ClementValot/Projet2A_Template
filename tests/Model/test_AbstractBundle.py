import pytest
from pydantic_core import ValidationError

from src.Model.abstract_bundle import AbstractBundle


class DummyBundle(AbstractBundle):
    price: float = 0.0

    def compute_price(self) -> float:
        return self.price


def test_dummy_bundle_ok():
    bundle = DummyBundle(id_bundle=1, name="Pack", price=9.99)
    assert bundle.id_bundle == 1
    assert bundle.name == "Pack"
    assert bundle.price == 9.99


def test_dummy_bundle_invalid_id():
    with pytest.raises(ValidationError):
        DummyBundle(id_bundle="abc", name="Test", price=5.0)
