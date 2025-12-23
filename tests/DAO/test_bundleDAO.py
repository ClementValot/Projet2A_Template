from collections import Counter
from typing import Any, Dict, List, Literal, Optional, Union

import pytest

from src.DAO.bundleDAO import BundleDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.itemDAO import ItemDAO
from src.Model.discounted_bundle import DiscountedBundle
from src.Model.item import Item
from src.Model.predefined_bundle import PredefinedBundle


class MockDBConnector(DBConnector):
    def __init__(self):
        self.bundles = [
            {
                "id_bundle": 1,
                "name": "Banh mi Menu",
                "description": "Banh mi + Drink + Dessert",
                "bundle_type": "predefined",
                "price": 17.0,
                "discount": None,
                "required_item_types": None,
            },
            {
                "id_bundle": 2,
                "name": "Burger Menu",
                "description": "Burger + Fries + Drink",
                "bundle_type": "predefined",
                "price": 16.0,
                "discount": None,
                "required_item_types": None,
            },
            {
                "id_bundle": 3,
                "name": "Promo for couple",
                "description": "Buy 2 main, get 10% off",
                "bundle_type": "discount",
                "price": None,
                "discount": 0.1,
                "required_item_types": ["main", "main"],
            },
            {
                "id_bundle": 5,
                "name": "Complete bundle",
                "description": None,
                "bundle_type": "discount",
                "price": None,
                "discount": 0.2,
                "required_item_types": ["starter", "main", "dessert"],
            },
        ]

        self.bundle_items = [
            {"id_bundle": 1, "id_item": 101},
            {"id_bundle": 1, "id_item": 102},
            {"id_bundle": 1, "id_item": 103},
            {"id_bundle": 2, "id_item": 201},
            {"id_bundle": 2, "id_item": 202},
        ]
        self.next_id = 12

    def sql_query(
        self,
        query: str,
        data: Optional[Union[tuple, list, dict]] = None,
        return_type: Optional[Union[Literal["one"], Literal["all"], None]] = "one",
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], bool, None]:
        q = " ".join(query.lower().split())

        if "simulate_db_error" in q:
            raise Exception("Simulated Database Error")

        if "select * from bundle where id_bundle" in q and return_type == "one":
            if isinstance(data, dict):
                bid = data.get("bundle_id")
                for b in self.bundles:
                    if b["id_bundle"] == bid:
                        return b.copy()
            return None

        if "select i.* from item i join bundle_item bi" in q and return_type == "all":
            if isinstance(data, dict):
                bid = data.get("bundle_id")
                item_ids = [bi["id_item"] for bi in self.bundle_items if bi["id_bundle"] == bid]
                return [{"id_item": iid, "name": f"Item {iid}", "price": 5.0} for iid in item_ids]
            return []

        if "select item_type, quantity_required from bundle_required_item" in q:
            if isinstance(data, dict):
                bid = data.get("bundle_id")
                for b in self.bundles:
                    if b["id_bundle"] == bid:
                        types = b.get("required_item_types") or []
                        counts = Counter(types)
                        return [{"item_type": t, "quantity_required": c} for t, c in counts.items()]
            return []

        if "select id_bundle from bundle" in q and return_type == "all":
            return [{"id_bundle": b["id_bundle"]} for b in self.bundles]

        if "insert into bundle" in q and "returning" in q:
            if not isinstance(data, dict):
                return None

            new_id = self.next_id
            self.next_id += 1

            bundle_type = "predefined"
            if "discount" in q and "discount" in data:
                if "'discount'" in q:
                    bundle_type = "discount"
                elif "'single_item'" in q:
                    bundle_type = "single_item"

            new_bundle = {
                "id_bundle": new_id,
                "name": data["name"],
                "description": data["description"],
                "bundle_type": bundle_type,
                "price": data.get("price"),
                "discount": data.get("discount"),
                "required_item_types": [],
            }
            self.bundles.append(new_bundle)
            return new_bundle

        if "insert into bundle_item" in q:
            if isinstance(data, dict):
                self.bundle_items.append({"id_bundle": data["id_bundle"], "id_item": data["id_item"]})
            return None

        if "insert into bundle_required_item" in q:
            if isinstance(data, dict):
                bid = data.get("id_bundle")
                item_type = data.get("item_type")
                qty = data.get("quantity_required")
                for b in self.bundles:
                    if b["id_bundle"] == bid:
                        if b["required_item_types"] is None:
                            b["required_item_types"] = []
                        b["required_item_types"].extend([item_type] * qty)
            return None

        if "update bundle" in q:
            if isinstance(data, dict):
                bid = data.get("id_bundle")
                for b in self.bundles:
                    if b["id_bundle"] == bid:
                        b.update({k: v for k, v in data.items() if k in b})
                        return True
            return None

        if "delete from bundle_item" in q:
            if isinstance(data, dict):
                bid = data.get("bundle_id") or data.get("id_bundle")
                self.bundle_items = [bi for bi in self.bundle_items if bi["id_bundle"] != bid]
                return True
            return None

        if "delete from bundle_required_item" in q:
            if isinstance(data, dict):
                bid = data.get("bundle_id") or data.get("id_bundle")
                for b in self.bundles:
                    if b["id_bundle"] == bid:
                        b["required_item_types"] = []
                return True
            return None

        if "delete from bundle" in q:
            if isinstance(data, dict):
                bid = data.get("bundle_id")
                self.bundles = [b for b in self.bundles if b["id_bundle"] != bid]
                return True
            return None

        return None


class MockItemDAO(ItemDAO):
    def __init__(self):
        super().__init__(db_connector=MockDBConnector())

    def find_item_by_id(self, item_id: int) -> Optional[Item]:
        return Item(id_item=item_id, name=f"Mock Item {item_id}", price=5.0, item_type="main")


@pytest.fixture
def mock_db_connector():
    return MockDBConnector()


@pytest.fixture
def mock_item_dao():
    return MockItemDAO()


@pytest.fixture
def bundle_dao(mock_db_connector, mock_item_dao) -> BundleDAO:
    return BundleDAO(db_connector=mock_db_connector, item_dao=mock_item_dao)


def test_find_bundle_by_id_predefined(bundle_dao: BundleDAO):
    bundle = bundle_dao.find_bundle_by_id(1)

    assert isinstance(bundle, PredefinedBundle)
    assert bundle.id_bundle == 1
    assert bundle.name == "Banh mi Menu"
    assert bundle.price == 17.0
    assert len(bundle.composition) == 3


def test_find_bundle_by_id_discounted(bundle_dao: BundleDAO):
    bundle = bundle_dao.find_bundle_by_id(3)

    assert isinstance(bundle, DiscountedBundle)
    assert bundle.id_bundle == 3
    assert bundle.name == "Promo for couple"
    assert bundle.discount == 0.1
    assert bundle.required_item_types == ["main", "main"]


def test_find_bundle_by_id_discounted_complex(bundle_dao: BundleDAO):
    bundle = bundle_dao.find_bundle_by_id(5)

    assert isinstance(bundle, DiscountedBundle)
    assert bundle.name == "Complete bundle"
    assert bundle.discount == 0.2
    assert "starter" in bundle.required_item_types
    assert "dessert" in bundle.required_item_types


def test_find_bundle_by_id_not_found(bundle_dao: BundleDAO):
    bundle = bundle_dao.find_bundle_by_id(999)
    assert bundle is None


def test_find_all_bundles(bundle_dao: BundleDAO):
    bundles = bundle_dao.find_all_bundles()

    assert len(bundles) == 4
    names = [b.name for b in bundles]
    assert "Banh mi Menu" in names
    assert "Promo for couple" in names


def test_add_predefined_bundle(bundle_dao: BundleDAO):
    item1 = Item(id_item=301, name="Tofu Salad", price=12.0, item_type="starter")
    new_bundle = PredefinedBundle(name="Vegan Special", description="Healthy choice", price=15.0, composition=[item1])

    created = bundle_dao.add_predefined_bundle(new_bundle)

    assert created is not None
    assert created.id_bundle == 12
    assert created.name == "Vegan Special"
    assert created.price == 15.0


def test_add_discounted_bundle(bundle_dao: BundleDAO):
    new_bundle = DiscountedBundle(
        name="Mega Family Pack",
        description="For 4 people",
        discount=0.28,
        required_item_types=["main", "main", "main", "main"],
    )

    created = bundle_dao.add_discounted_bundle(new_bundle)

    assert created is not None
    assert created.id_bundle == 12
    assert created.discount == 0.28


def test_update_bundle_predefined(bundle_dao: BundleDAO):
    item_mock = Item(id_item=101, name="Banh Mi", price=5.0, item_type="main")
    bundle_to_update = PredefinedBundle(
        id_bundle=1, name="Banh mi Menu V2", description="Updated Description", price=18.5, composition=[item_mock]
    )

    success = bundle_dao.update_bundle(bundle_to_update)
    assert success is True

    updated = bundle_dao.find_bundle_by_id(1)
    assert updated.name == "Banh mi Menu V2"
    assert updated.price == 18.5


def test_update_bundle_discounted(bundle_dao: BundleDAO):
    bundle_to_update = DiscountedBundle(
        id_bundle=3,
        name="Promo for couple",
        description="Buy 2 main, get 15% off",
        discount=0.15,
        required_item_types=["main", "main"],
    )

    success = bundle_dao.update_bundle(bundle_to_update)
    assert success is True

    updated = bundle_dao.find_bundle_by_id(3)
    assert updated.discount == 0.15


def test_delete_bundle(bundle_dao: BundleDAO, mock_db_connector):
    success = bundle_dao.delete_bundle(2)

    assert success is True
    assert not any(b["id_bundle"] == 2 for b in mock_db_connector.bundles)


def test_find_bundle_error(bundle_dao: BundleDAO, mock_db_connector):
    mock_db_connector.sql_query = lambda q, d, rt: exec('raise Exception("DB Error")')
    assert bundle_dao.find_bundle_by_id(1) is None


def test_add_bundle_error(bundle_dao: BundleDAO, mock_db_connector):
    mock_db_connector.sql_query = lambda q, d, rt: exec('raise Exception("DB Error")')
    new_bundle = DiscountedBundle(name="Fail", description="", discount=0.1, required_item_types=[])
    assert bundle_dao.add_discounted_bundle(new_bundle) is None


def test_update_bundle_error(bundle_dao: BundleDAO, mock_db_connector):
    mock_db_connector.sql_query = lambda q, d, rt: exec('raise Exception("DB Error")')
    bundle = DiscountedBundle(id_bundle=3, name="Fail", description="", discount=0.1, required_item_types=[])
    assert bundle_dao.update_bundle(bundle) is False


def test_delete_bundle_error(bundle_dao: BundleDAO, mock_db_connector):
    mock_db_connector.sql_query = lambda q, d, rt: exec('raise Exception("DB Error")')
    assert bundle_dao.delete_bundle(1) is False
