from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional, Union
from unittest.mock import MagicMock

import pytest

from src.DAO.addressDAO import AddressDAO
from src.DAO.bundleDAO import BundleDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.itemDAO import ItemDAO
from src.DAO.orderDAO import OrderDAO
from src.DAO.userDAO import UserDAO
from src.Model.address import Address
from src.Model.customer import Customer
from src.Model.item import Item
from src.Model.order import Order


class MockDBConnector:
    def __init__(self):
        self.orders = [
            {
                "id_order": 101,
                "id_user": 1,
                "status": "pending",
                "price": 45.99,
                "id_address": 10,
                "order_date": datetime(2025, 1, 15),
            },
            {
                "id_order": 102,
                "id_user": 1,
                "status": "delivered",
                "price": 12.50,
                "id_address": 10,
                "order_date": datetime(2025, 1, 16),
            },
            {
                "id_order": 103,
                "id_user": 2,
                "status": "in_progress",
                "price": 99.00,
                "id_address": 20,
                "order_date": datetime(2025, 1, 17),
            },
            {
                "id_order": 104,
                "id_user": 2,
                "status": "delivered",
                "price": 150.00,
                "id_address": 20,
                "order_date": datetime(2025, 1, 18),
            },
        ]
        self.order_items = [
            {"id_order": 101, "id_item": 1001},
            {"id_order": 101, "id_item": 1002},
            {"id_order": 102, "id_item": 1003},
            {"id_order": 104, "id_item": 2001},
        ]
        self.next_id_order = 105
        self.raise_exception = False
        self.last_query_data = None

    def sql_query(
        self,
        query: str,
        data: Optional[Union[tuple, list, dict]] = None,
        return_type: Union[Literal["one"], Literal["all"], None] = "one",
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        q = " ".join(query.lower().split())
        self.last_query_data = data

        if self.raise_exception:
            if "select" in q or "insert" in q or "update" in q or "delete" in q:
                raise Exception("Simulated DB Error")

        if q.startswith('select * from "order"'):
            if "where id_order" in q:
                id_order = data.get("id_order")
                return next((o for o in self.orders if o["id_order"] == id_order), None)
            elif "where id_user" in q:
                id_user = data.get("id_user")
                results = [o for o in self.orders if o["id_user"] == id_user]
                return results if return_type == "all" else (results[0] if results else None)
            else:
                return self.orders if return_type == "all" else (self.orders[0] if self.orders else None)

        if q.startswith("select i.* from item i join order_item oi on i.id_item = oi.id_item where oi.id_order"):
            id_order = data.get("id_order")
            item_ids = [oi["id_item"] for oi in self.order_items if oi["id_order"] == id_order]
            return (
                [{"id_item": item_id} for item_id in item_ids]
                if return_type == "all"
                else ([{"id_item": item_ids[0]}] if item_ids else None)
            )

        if q.startswith('insert into "order"'):
            new_order = {
                "id_order": self.next_id_order,
                "id_user": data["id_user"],
                "status": data["status"],
                "price": data["price"],
                "id_address": data["id_address"],
                "order_date": data["order_date"],
            }
            self.orders.append(new_order)
            self.next_id_order += 1
            return new_order

        if q.startswith("insert into order_item"):
            self.order_items.append(data)
            return None

        if q.startswith('update "order"'):
            id_order = data.get("id_order")
            for order in self.orders:
                if order["id_order"] == id_order:
                    order.update(
                        {
                            "id_user": data["id_user"],
                            "status": data["status"],
                            "price": data["price"],
                            "id_address": data["id_address"],
                            "order_date": data["order_date"],
                        }
                    )
                    return {"id_order": id_order}
            return None

        if q.startswith("delete from order_item"):
            id_order = data.get("id_order")
            self.order_items = [oi for oi in self.order_items if oi["id_order"] != id_order]
            return None

        if q.startswith("delete from delivery_order"):
            return None

        if q.startswith('delete from "order"'):
            id_order = data.get("id_order")
            initial_count = len(self.orders)
            self.orders = [o for o in self.orders if o["id_order"] != id_order]
            if len(self.orders) < initial_count:
                return {"id_order": id_order}
            return None

        return None


MOCK_USERS = {
    1: Customer(
        id_user=1,
        username="john_doe",
        hash_password="aa453f466c612b04de2e62b5501c264e462b06bac3ce18dc4bf7ad38e2d17bdf",
        salt="9a7fc02853c99c560238517027351d7deb7efeb2097686bd565c59bdaf059af6",
        sign_up_date=date(2024, 1, 15),
        name="John Doe",
        phone_number="0601020304",
    ),
    2: Customer(
        id_user=2,
        username="jane_smith",
        hash_password="9faef269131b1838ab8e95af580e7c109e1de4448ba0282bdf06f19726ff55ea",
        salt="776e37cc088064e6aef5cd504181f07e83ab5e495e724a5a492f0b495cec3e1c",
        sign_up_date=date(2024, 2, 20),
        name="Jane Smith",
        phone_number="0612345678",
    ),
}
MOCK_ADDRESSES = {
    10: Address(id_address=10, city="Paris", postal_code=75001, street_name="Rivoli Street", street_number=10),
    20: Address(id_address=20, city="Lyon", postal_code=69001, street_name="Republic Street", street_number=25),
}
MOCK_ITEMS_BUNDLES = {
    1001: Item(id_item=1001, name="Item1", price=10.0, item_type="main", stock=1),
    1002: Item(id_item=1002, name="Item2", price=15.0, item_type="main", stock=1),
    1003: Item(id_item=1003, name="Item3", price=12.50, item_type="main", stock=1),
    2001: Item(id_item=2001, name="Mega Discount (as Item)", price=150.0, item_type="main", stock=1),
}


@pytest.fixture
def mock_db_connector_impl() -> MockDBConnector:
    return MockDBConnector()


@pytest.fixture
def mock_db(mock_db_connector_impl) -> MagicMock:
    mock = MagicMock(spec=DBConnector)
    mock.sql_query.side_effect = mock_db_connector_impl.sql_query
    return mock


@pytest.fixture
def mock_user_dao() -> MagicMock:
    mock = MagicMock(spec=UserDAO)
    mock.find_user_by_id.side_effect = lambda id: MOCK_USERS.get(id, None)
    return mock


@pytest.fixture
def mock_address_dao() -> MagicMock:
    mock = MagicMock(spec=AddressDAO)
    mock.find_address_by_id.side_effect = lambda id: MOCK_ADDRESSES.get(id, None)
    return mock


@pytest.fixture
def mock_item_dao() -> MagicMock:
    mock = MagicMock(spec=ItemDAO)
    mock.find_item_by_id.side_effect = lambda id: MOCK_ITEMS_BUNDLES.get(id, None)
    return mock


@pytest.fixture
def mock_bundle_dao() -> MagicMock:
    return MagicMock(spec=BundleDAO)


@pytest.fixture
def order_dao(mock_db: MagicMock, mock_item_dao, mock_user_dao, mock_address_dao, mock_bundle_dao) -> OrderDAO:
    return OrderDAO(
        db_connector=mock_db,
        item_dao=mock_item_dao,
        user_dao=mock_user_dao,
        address_dao=mock_address_dao,
        bundle_dao=mock_bundle_dao,
    )


def test_find_order_by_id_nominal(order_dao: OrderDAO):
    order = order_dao.find_order_by_id(101)
    assert order is not None
    assert order.id_order == 101
    assert order.status == "pending"
    assert len(order.items) == 2
    assert isinstance(order.customer, Customer)
    assert isinstance(order.address, Address)


def test_find_order_with_bundle(order_dao: OrderDAO):
    order = order_dao.find_order_by_id(104)
    assert order is not None
    assert order.id_order == 104
    assert len(order.items) == 1
    assert isinstance(order.items[0], Item)
    assert order.items[0].id_item == 2001


def test_find_order_by_id_not_found(order_dao: OrderDAO):
    order = order_dao.find_order_by_id(999)
    assert order is None


def test_find_all_orders(order_dao: OrderDAO):
    orders = order_dao.find_all_orders()
    assert len(orders) == 4
    assert orders[0].id_order == 101
    assert orders[3].id_order == 104


def test_find_orders_by_customer(order_dao: OrderDAO):
    orders = order_dao.find_orders_by_customer(1)
    assert len(orders) == 2
    assert all(o.customer.id_user == 1 for o in orders)


def test_find_orders_by_customer_no_orders(order_dao: OrderDAO):
    orders = order_dao.find_orders_by_customer(99)
    assert orders == []


def test_add_order_nominal(order_dao: OrderDAO, mock_db_connector_impl: MockDBConnector):
    new_order_data = Order(
        customer=MOCK_USERS[1],
        address=MOCK_ADDRESSES[10],
        items=[MOCK_ITEMS_BUNDLES[1001]],
        status="pending",
        price=10.0,
        order_date=datetime.now().replace(microsecond=0),
    )

    initial_order_count = len(mock_db_connector_impl.orders)
    added_order = order_dao.add_order(new_order_data)

    assert added_order is not None
    assert added_order.id_order == mock_db_connector_impl.next_id_order - 1
    assert len(mock_db_connector_impl.orders) == initial_order_count + 1
    assert added_order.status == "pending"


def test_update_order_nominal(order_dao: OrderDAO, mock_db_connector_impl: MockDBConnector):
    order_to_update = order_dao.find_order_by_id(101)

    order_to_update.status = "delivered"
    order_to_update.price = 50.00
    order_to_update.items = [MOCK_ITEMS_BUNDLES[1003]]

    success = order_dao.update_order(order_to_update)
    assert success is True

    updated_order = order_dao.find_order_by_id(101)
    assert updated_order.status == "delivered"
    assert updated_order.price == 50.00
    assert len(updated_order.items) == 1
    assert updated_order.items[0].id_item == 1003

    item_links = [oi for oi in mock_db_connector_impl.order_items if oi["id_order"] == 101]
    assert len(item_links) == 1
    assert item_links[0]["id_item"] == 1003


def test_delete_order_nominal(order_dao: OrderDAO, mock_db_connector_impl: MockDBConnector):
    initial_order_count = len(mock_db_connector_impl.orders)

    success = order_dao.delete_order(101)
    assert success is True

    assert len(mock_db_connector_impl.orders) == initial_order_count - 1
    assert order_dao.find_order_by_id(101) is None

    assert len([oi for oi in mock_db_connector_impl.order_items if oi["id_order"] == 101]) == 0


def test_find_order_by_id_db_error(order_dao: OrderDAO, mock_db: MagicMock):
    mock_db.sql_query.side_effect = Exception("Simulated DB Error")
    order = order_dao.find_order_by_id(101)
    assert order is None
    mock_db.sql_query.side_effect = None


def test_find_all_orders_db_error(order_dao: OrderDAO, mock_db: MagicMock):
    mock_db.sql_query.side_effect = Exception("Simulated DB Error")
    orders = order_dao.find_all_orders()
    assert orders == []
    mock_db.sql_query.side_effect = None


def test_find_orders_by_customer_db_error(order_dao: OrderDAO, mock_db: MagicMock):
    mock_db.sql_query.side_effect = Exception("Simulated DB Error")
    orders = order_dao.find_orders_by_customer(1)
    assert orders == []
    mock_db.sql_query.side_effect = None


def test_add_order_db_error(order_dao: OrderDAO, mock_db: MagicMock):
    mock_db.sql_query.side_effect = Exception("Simulated DB Error")
    new_order_data = Order(
        customer=MOCK_USERS[1],
        address=MOCK_ADDRESSES[10],
        items=[MOCK_ITEMS_BUNDLES[1001]],
        status="pending",
        price=10.0,
        order_date=datetime.now().replace(microsecond=0),
    )
    added_order = order_dao.add_order(new_order_data)
    assert added_order is None
    mock_db.sql_query.side_effect = None


def test_update_order_db_error(order_dao: OrderDAO, mock_db: MagicMock):
    order_to_update = order_dao.find_order_by_id(101)
    mock_db.sql_query.side_effect = Exception("Simulated DB Error")
    success = order_dao.update_order(order_to_update)
    assert success is False
    mock_db.sql_query.side_effect = None


def test_delete_order_db_error(order_dao: OrderDAO, mock_db: MagicMock):
    mock_db.sql_query.side_effect = Exception("Simulated DB Error")
    success = order_dao.delete_order(101)
    assert success is False
    mock_db.sql_query.side_effect = None