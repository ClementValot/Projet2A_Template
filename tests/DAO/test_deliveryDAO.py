from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from unittest.mock import MagicMock

import pytest

from src.DAO.DBConnector import DBConnector
from src.DAO.deliveryDAO import DeliveryDAO
from src.DAO.orderDAO import OrderDAO
from src.DAO.userDAO import UserDAO
from src.Model.address import Address
from src.Model.customer import Customer
from src.Model.delivery import Delivery
from src.Model.driver import Driver
from src.Model.item import Item
from src.Model.order import Order


class MockDBConnector(DBConnector):
    def __init__(self):
        self.deliveries = [
            {
                "id_delivery": 1,
                "id_driver": 10,
                "status": "in_progress",
                "delivery_time": None,
            },
            {
                "id_delivery": 2,
                "id_driver": 10,
                "status": "in_progress",
                "delivery_time": datetime(2023, 1, 1, 12, 0, 0),
            },
        ]
        self.delivery_orders = {1: [100, 101], 2: [102]}
        self.next_id = 3

    def sql_query(
        self,
        query: str,
        data: Optional[Union[tuple, list, dict]] = None,
        return_type: Optional[Union[Literal["one"], Literal["all"], None]] = "one",
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], bool, None]:
        q = " ".join(query.lower().split())

        if "simulate_db_error" in q:
            raise Exception("Simulated Database Error")

        if "select * from delivery where id_delivery" in q and return_type == "one":
            if isinstance(data, dict):
                did = data.get("id_delivery")
                for d in self.deliveries:
                    if d["id_delivery"] == did:
                        return d.copy()
            return None

        if "select id_order from delivery_order" in q and return_type == "all":
            if isinstance(data, dict):
                did = data.get("id_delivery")
                order_ids = self.delivery_orders.get(did, [])
                return [{"id_order": oid} for oid in order_ids]
            return []

        if "select * from delivery" in q and return_type == "all":
            if "where" not in q:
                return [d.copy() for d in self.deliveries]

        if "select * from delivery" in q and "where id_driver" in q and "status = 'in_progress'" in q:
            driver_id = data.get("driver_id")
            return [d.copy() for d in self.deliveries if d["id_driver"] == driver_id and d["status"] == "in_progress"]

        if "insert into delivery" in q and "returning" in q:
            new_id = self.next_id
            self.next_id += 1
            new_delivery = {
                "id_delivery": new_id,
                "id_driver": data.get("id_driver"),
                "status": data.get("status"),
                "delivery_time": data.get("delivery_time"),
            }
            self.deliveries.append(new_delivery)
            self.delivery_orders[new_id] = []
            return new_delivery

        if "insert into delivery_order" in q:
            did = data.get("id_delivery")
            oid = data.get("id_order")
            if did in self.delivery_orders:
                self.delivery_orders[did].append(oid)
            else:
                self.delivery_orders[did] = [oid]
            return None

        if "update delivery" in q:
            did = data.get("id_delivery")
            for d in self.deliveries:
                if d["id_delivery"] == did:
                    d.update({k: v for k, v in data.items() if k in d})
                    return {"id_delivery": did}
            return None

        if "delete from delivery_order" in q:
            did = data.get("id_delivery")
            if did in self.delivery_orders:
                del self.delivery_orders[did]
            return None

        if "delete from delivery" in q and "returning" in q:
            did = data.get("id_delivery")
            initial_len = len(self.deliveries)
            self.deliveries = [d for d in self.deliveries if d["id_delivery"] != did]
            if len(self.deliveries) < initial_len:
                return {"id_delivery": did}
            return None

        return None


@pytest.fixture
def mock_db_connector():
    return MockDBConnector()


@pytest.fixture
def mock_user_dao():
    dao = MagicMock(spec=UserDAO)
    driver = Driver(
        id_user=10,
        username="driver_john",
        hash_password="hashed_secret",
        salt="random_salt",
        name="John Driver",
        phone_number="0123456789",
        vehicle_type="scooter",
        availability=True,
    )
    dao.find_user_by_id.return_value = driver
    return dao


@pytest.fixture
def mock_order_dao():
    dao = MagicMock(spec=OrderDAO)

    def side_effect_find_order(oid):
        customer = Customer(
            id_user=50,
            username="cust_jane",
            hash_password="pw",
            salt="salt",
            name="Jane Doe",
            phone_number="0987654321",
        )
        address = Address(
            id_address=1, city="Paris", postal_code=75001, street_name="Rue de Rivoli", street_number="10"
        )
        item = Item(
            id_item=1, name="Pizza", price=15.0, item_type="main", description="Yummy", stock=10, availability=True
        )

        return Order(
            id_order=oid,
            status="pending",
            total_price=50.0,
            customer=customer,
            address=address,
            items=[item],
            bundle=None,
        )

    dao.find_order_by_id.side_effect = side_effect_find_order
    return dao


@pytest.fixture
def delivery_dao(mock_db_connector, mock_user_dao, mock_order_dao) -> DeliveryDAO:
    return DeliveryDAO(db_connector=mock_db_connector, user_dao=mock_user_dao, order_dao=mock_order_dao)


def test_find_delivery_by_id_existing(delivery_dao: DeliveryDAO):
    delivery = delivery_dao.find_delivery_by_id(1)

    assert delivery is not None
    assert isinstance(delivery, Delivery)
    assert delivery.id_delivery == 1
    assert delivery.status == "in_progress"

    assert delivery.driver is not None
    assert delivery.driver.id_user == 10
    assert delivery.driver.vehicle_type == "scooter"

    assert len(delivery.orders) == 2
    assert delivery.orders[0].id_order == 100
    assert delivery.orders[1].id_order == 101


def test_find_delivery_by_id_not_found(delivery_dao: DeliveryDAO):
    delivery = delivery_dao.find_delivery_by_id(999)
    assert delivery is None


def test_find_all_deliveries(delivery_dao: DeliveryDAO):
    deliveries = delivery_dao.find_all_deliveries()

    assert len(deliveries) == 2
    assert deliveries[0].id_delivery == 1
    assert deliveries[1].id_delivery == 2
    assert deliveries[1].driver.id_user == 10
    assert len(deliveries[1].orders) == 1


def test_find_in_progress_deliveries_by_driver(delivery_dao: DeliveryDAO):
    deliveries = delivery_dao.find_in_progress_deliveries_by_driver(10)

    assert len(deliveries) == 2
    assert deliveries[1].id_delivery == 2
    assert deliveries[1].status == "in_progress"


def test_add_delivery_success(delivery_dao: DeliveryDAO, mocker):
    driver = Driver(
        id_user=10,
        username="driver_john",
        hash_password="hashed_secret",
        salt="random_salt",
        name="John",
        phone_number="0123456789",
        vehicle_type="bike",
        availability=True,
    )

    customer = Customer(id_user=50, username="cust", hash_password="pw", salt="s", name="C", phone_number="1")
    address = Address(city="P", postal_code=1, street_name="S")
    item = Item(name="I", price=1.0, item_type="main")

    order1 = Order(id_order=200, status="pending", total_price=10.0, customer=customer, address=address, items=[item])

    new_delivery = Delivery(driver=driver, orders=[order1], status="in_progress", delivery_time=None)

    created_delivery = delivery_dao.add_delivery(new_delivery)

    assert created_delivery is not None
    assert created_delivery.id_delivery == 3
    assert created_delivery.status == "in_progress"
    assert len(created_delivery.orders) == 1
    assert created_delivery.orders[0].id_order == 200


def test_update_delivery_success(delivery_dao: DeliveryDAO):
    delivery = delivery_dao.find_delivery_by_id(1)
    assert delivery is not None

    delivery.status = "delivered"
    delivery.delivery_time = datetime.now()

    result = delivery_dao.update_delivery(delivery)

    assert result is True

    updated_delivery = delivery_dao.find_delivery_by_id(1)
    assert updated_delivery.status == "delivered"
    assert updated_delivery.delivery_time is not None


def test_delete_delivery_success(delivery_dao: DeliveryDAO):
    result = delivery_dao.delete_delivery(1)

    assert result is True
    assert delivery_dao.find_delivery_by_id(1) is None


def test_delete_delivery_not_found(delivery_dao: DeliveryDAO):
    result = delivery_dao.delete_delivery(999)
    assert result is False


def test_find_delivery_error(delivery_dao: DeliveryDAO, mock_db_connector):
    mock_db_connector.sql_query = lambda q, d, rt: exec('raise Exception("DB Error")')
    assert delivery_dao.find_delivery_by_id(1) is None


def test_find_all_deliveries_error(delivery_dao: DeliveryDAO, mock_db_connector):
    mock_db_connector.sql_query = lambda q, d, rt: exec('raise Exception("DB Error")')
    assert delivery_dao.find_all_deliveries() == []


def test_add_delivery_error(delivery_dao: DeliveryDAO, mock_db_connector):
    mock_db_connector.sql_query = lambda q, d, rt: exec('raise Exception("DB Error")')
    driver = Driver(
        id_user=10,
        username="u",
        hash_password="p",
        salt="s",
        name="d",
        phone_number="0",
        vehicle_type="car",
        availability=True,
    )
    delivery = Delivery(driver=driver, orders=[], status="in_progress")

    assert delivery_dao.add_delivery(delivery) is None


def test_update_delivery_error(delivery_dao: DeliveryDAO, mock_db_connector):
    driver = Driver(
        id_user=10,
        username="u",
        hash_password="p",
        salt="s",
        name="d",
        phone_number="0",
        vehicle_type="car",
        availability=True,
    )
    delivery = Delivery(id_delivery=1, driver=driver, orders=[], status="in_progress")

    mock_db_connector.sql_query = lambda q, d, rt: exec('raise Exception("DB Error")')
    assert delivery_dao.update_delivery(delivery) is False
