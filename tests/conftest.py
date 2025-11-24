from datetime import datetime

import pytest
from dotenv import load_dotenv

from src.DAO.AddressDAO import AddressDAO
from src.DAO.AdminDAO import AdminDAO
from src.DAO.BundleDAO import BundleDAO
from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.DeliveryDAO import DeliveryDAO
from src.DAO.DriverDAO import DriverDAO
from src.DAO.ItemDAO import ItemDAO
from src.DAO.OrderableDAO import OrderableDAO
from src.DAO.OrderDAO import OrderDAO
from src.Service.AddressService import AddressService
from src.Service.BundleService import BundleService
from src.Service.CustomerService import CustomerService
from src.Service.DriverService import DriverService
from src.Service.GoogleMapService import GoogleMapService
from src.Service.ItemService import ItemService
from src.Service.MenuService import MenuService
from src.Service.OrderService import OrderService
from src.Service.UserService import UserService

load_dotenv()


@pytest.fixture(scope="session")
def db_connector_test():
    return DBConnector(test=True)


@pytest.fixture(scope="function")
def clean_database(db_connector_test):
    tables = [
        "Deliveries",
        "Order_contents",
        "Bundle_Items",
        "Bundles",
        "Items",
        "Orderables",
        "Orders",
        "Customers",
        "Drivers",
        "Admins",
        "Addresses",
    ]

    for table in tables:
        db_connector_test.sql_query(
            f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE", return_type="none"
        )

    yield db_connector_test


@pytest.fixture
def orderable_dao(db_connector_test):
    return OrderableDAO(db_connector_test)


@pytest.fixture
def item_dao(db_connector_test, orderable_dao):
    return ItemDAO(db_connector_test, orderable_dao)


@pytest.fixture
def bundle_dao(db_connector_test, orderable_dao, item_dao):
    return BundleDAO(db_connector_test, orderable_dao, item_dao)


@pytest.fixture
def order_dao(db_connector_test, orderable_dao, item_dao, bundle_dao):
    return OrderDAO(db_connector_test, orderable_dao, item_dao, bundle_dao)


@pytest.fixture
def address_dao(db_connector_test):
    return AddressDAO(db_connector_test)


@pytest.fixture
def admin_dao(db_connector_test):
    return AdminDAO(db_connector_test)


@pytest.fixture
def customer_dao(db_connector_test, address_dao):
    return CustomerDAO(db_connector_test, address_dao)


@pytest.fixture
def driver_dao(db_connector_test):
    return DriverDAO(db_connector_test)


@pytest.fixture
def delivery_dao(db_connector_test):
    return DeliveryDAO(db_connector_test)


@pytest.fixture
def user_service(customer_dao, driver_dao, admin_dao):
    return UserService(customer_dao, driver_dao, admin_dao)


@pytest.fixture
def item_service(item_dao, order_dao):
    return ItemService(item_dao, order_dao)


@pytest.fixture
def bundle_service(bundle_dao):
    return BundleService(bundle_dao)


@pytest.fixture
def order_service(order_dao, orderable_dao, item_dao, bundle_dao):
    return OrderService(order_dao, orderable_dao, item_dao, bundle_dao)


@pytest.fixture
def driver_service(delivery_dao, driver_dao, user_service, order_dao):
    return DriverService(delivery_dao, driver_dao, order_dao, user_service)


@pytest.fixture
def google_map_service():
    return GoogleMapService()


@pytest.fixture
def address_service(address_dao, google_map_service):
    return AddressService(address_dao, google_map_service)


@pytest.fixture
def menu_service(orderable_dao, item_dao, bundle_dao):
    return MenuService(orderable_dao, item_dao, bundle_dao)


@pytest.fixture
def customer_service(customer_dao, address_service, user_service):
    return CustomerService(customer_dao, address_service, user_service)


@pytest.fixture
def sample_address(address_dao, clean_database):
    address = address_dao.create_address(
        7,
        "Contour Antoine de Saint-Exupéry",
        "Bruz",
        35170,
        "France",
    )
    return address


@pytest.fixture
def sample_customer(customer_dao, sample_address, clean_database):
    customer = customer_dao.create_customer(
        first_name="Jean",
        last_name="Dupont",
        phone="+33612345678",
        mail="jean.dupont@email.com",
        password_hash="hashed_password_123",
        salt="random_salt_456",
        address_id=sample_address.address_id,
    )
    return customer


@pytest.fixture
def sample_driver(driver_dao, clean_database):
    driver = driver_dao.create_driver("Lewis", "Hamilton", "0707", "hash", "salt")
    return driver


@pytest.fixture
def sample_order(order_dao, sample_customer, clean_database):
    return order_dao.create_order(sample_customer.id)


@pytest.fixture
def sample_item_data():
    return {
        "item_name": "Galette-Saucisse",
        "item_price": 4.5,
        "item_type": "Main course",
        "item_description": "La fameuse galette-saucisse de l'EJR",
        "item_stock": 50,
        "is_in_menu": True,
    }


@pytest.fixture
def sample_item(item_dao, clean_database, sample_item_data):
    return item_dao.create_item(**sample_item_data)


@pytest.fixture
def multiple_items(item_dao, clean_database):
    items = []

    item1 = item_dao.create_item(
        item_name="Galette-Saucisse",
        item_price=4.5,
        item_type="Main course",
        item_description="La fameuse galette-saucisse de l'EJR",
        item_stock=50,
        is_in_menu=True,
    )
    items.append(item1)

    item2 = item_dao.create_item(
        item_name="Coca-Cola 33cl",
        item_price=0.5,
        item_type="Drink",
        item_description="Canette de Coca-Cola",
        item_stock=100,
        is_in_menu=True,
    )
    items.append(item2)

    item3 = item_dao.create_item(
        item_name="Tiramisu",
        item_price=2.0,
        item_type="Dessert",
        item_description="Tiramisu-holic",
        item_stock=30,
        is_in_menu=True,
    )
    items.append(item3)

    return items


@pytest.fixture
def sample_bundle(multiple_items, bundle_dao, clean_database):
    bundle_items = {item: 1 for item in multiple_items[:2]}
    bundle = bundle_dao.create_bundle(
        "Menu",
        15,
        "Plat + Boisson",
        datetime(2024, 10, 9, 12, 30, 0),
        datetime(2026, 10, 9, 12, 30, 0),
        bundle_items,
        is_in_menu=True,
    )
    return bundle


@pytest.fixture
def sample_empty_order(order_dao, clean_database, sample_customer):
    return order_dao.create_order(sample_customer.id)


@pytest.fixture
def sample_order_full(multiple_items, sample_bundle, order_dao, clean_database, sample_customer):
    order = order_dao.create_order(sample_customer.id)

    order_dao.add_orderable_to_order(order.order_id, sample_bundle.orderable_id)
    order = order_dao.add_orderable_to_order(order.order_id, multiple_items[2].orderable_id)
    return order


@pytest.fixture
def sample_admin(admin_dao, clean_database):
    return admin_dao.create_admin("admin", "Aucune", "Idee", "V@lidPassw0rd", "salt")
