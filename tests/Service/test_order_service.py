from datetime import datetime
from unittest.mock import ANY, MagicMock

import pytest

from src.DAO.addressDAO import AddressDAO
from src.DAO.bundleDAO import BundleDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.itemDAO import ItemDAO
from src.DAO.orderDAO import OrderDAO
from src.DAO.userDAO import UserDAO
from src.Model.abstract_bundle import AbstractBundle
from src.Model.address import Address
from src.Model.customer import Customer
from src.Model.driver import Driver
from src.Model.item import Item
from src.Model.order import Order
from src.Service.order_service import OrderService



@pytest.fixture
def mock_db_connector():
    """Provides a mock DBConnector."""
    return MagicMock(spec=DBConnector)


@pytest.fixture
def mock_item_dao():
    """Provides a mock ItemDAO."""
    return MagicMock(spec=ItemDAO)


@pytest.fixture
def mock_user_dao():
    """Provides a mock UserDAO."""
    return MagicMock(spec=UserDAO)


@pytest.fixture
def mock_address_dao():
    """Provides a mock AddressDAO."""
    return MagicMock(spec=AddressDAO)


@pytest.fixture
def mock_bundle_dao():
    """Provides a mock BundleDAO."""
    return MagicMock(spec=BundleDAO)


@pytest.fixture
def mock_order_dao():
    """Provides a mock OrderDAO."""
    return MagicMock(spec=OrderDAO)


@pytest.fixture
def service(mock_db_connector, mock_item_dao, mock_user_dao, mock_address_dao, mock_bundle_dao, mock_order_dao, mocker):
    """
    Provides an OrderService instance with all DAO dependencies mocked.
    """
    mocker.patch("src.Service.order_service.ItemDAO", return_value=mock_item_dao)
    mocker.patch("src.Service.order_service.UserDAO", return_value=mock_user_dao)
    mocker.patch("src.Service.order_service.AddressDAO", return_value=mock_address_dao)
    mocker.patch("src.Service.order_service.BundleDAO", return_value=mock_bundle_dao)
    mocker.patch("src.Service.order_service.OrderDAO", return_value=mock_order_dao)

    order_service = OrderService(db_connector=mock_db_connector)
    return order_service


@pytest.fixture
def sample_customer():
    """Provides a mock Customer."""
    return MagicMock(spec=Customer, id=1, name="Test Customer")


@pytest.fixture
def sample_address():
    """Provides a mock Address."""
    return MagicMock(spec=Address, id=10, street="123 Test St")


@pytest.fixture
def sample_item_1():
    """Provides a mock Item, available with stock."""
    item = MagicMock(spec=Item)
    item.id_item = 1
    item.name = "Burger"
    item.availability = True
    item.stock = 10
    item.price = 5.0
    return item


@pytest.fixture
def sample_item_2():
    """Provides a second mock Item, available with stock."""
    item = MagicMock(spec=Item)
    item.id_item = 2
    item.name = "Fries"
    item.availability = True
    item.stock = 5
    item.price = 2.0
    return item


@pytest.fixture
def sample_item_unavailable():
    """Provides a mock Item that is UNAVAILABLE."""
    item = MagicMock(spec=Item)
    item.id_item = 3
    item.name = "Milkshake"
    item.availability = False
    item.stock = 0
    item.price = 3.0
    return item


@pytest.fixture
def sample_bundle_1(sample_item_1, sample_item_2):
    """Provides a mock Bundle with available items."""
    bundle = MagicMock(spec=AbstractBundle)
    bundle.composition = [sample_item_1, sample_item_2]
    bundle.compute_price.return_value = 7.0
    bundle.name = "Menu 1"
    return bundle


@pytest.fixture
def sample_bundle_2(sample_item_1):
    """Provides a mock Bundle that uses the same item twice."""
    bundle = MagicMock(spec=AbstractBundle)
    bundle.composition = [sample_item_1, sample_item_1]
    bundle.compute_price.return_value = 10.0
    bundle.name = "Double Burger"
    return bundle


@pytest.fixture
def sample_bundle_unavailable(sample_item_1, sample_item_unavailable):
    """Provides a mock Bundle with one unavailable item."""
    bundle = MagicMock(spec=AbstractBundle)
    bundle.composition = [sample_item_1, sample_item_unavailable]
    bundle.compute_price.return_value = 8.0
    bundle.name = "Broken Menu"
    return bundle


@pytest.fixture
def sample_order_pending(sample_customer, sample_address):
    """Provides a mock 'pending' Order, starting empty."""
    order = MagicMock(spec=Order)
    order.id = 501
    order.customer = sample_customer
    order.address = sample_address
    order.status = "pending"
    order.items = []
    order.price = 0.0
    return order


@pytest.fixture
def sample_order_pending_with_items(sample_customer, sample_address, sample_item_1, sample_item_2):
    """Provides a 'pending' order that already contains items (from bundle 1)."""
    order = MagicMock(spec=Order)
    order.id = 503
    order.customer = sample_customer
    order.address = sample_address
    order.status = "pending"
    order.items = [sample_item_1, sample_item_2]
    order.price = 7.0
    return order


@pytest.fixture
def sample_order_validated(sample_customer, sample_address, sample_item_1):
    """Provides a mock 'validated' Order."""
    order = MagicMock(spec=Order)
    order.id = 502
    order.customer = sample_customer
    order.address = sample_address
    order.status = "validated"
    order.items = [sample_item_1]
    return order



def test_create_order_success(
    service: OrderService,
    mock_user_dao: MagicMock,
    mock_address_dao: MagicMock,
    mock_order_dao: MagicMock,
    sample_customer: Customer,
    sample_address: Address,
    mocker,
):
    """Tests successful creation of a new, empty order."""
    mock_user_dao.find_user_by_id.return_value = sample_customer
    mock_address_dao.find_address_by_id.return_value = sample_address
    mock_created_order = MagicMock(spec=Order, id=1)
    mock_order_dao.add_order.return_value = mock_created_order
    mock_now = datetime(2025, 1, 1, 12, 0)
    mocker.patch("src.Service.order_service.datetime").now.return_value = mock_now

    result = service.create_order(customer_id=1, address_id=10)

    mock_user_dao.find_user_by_id.assert_called_once_with(1)
    mock_address_dao.find_address_by_id.assert_called_once_with(10)
    mock_order_dao.add_order.assert_called_once_with(ANY)

    called_order = mock_order_dao.add_order.call_args[0][0]
    assert isinstance(called_order, Order)
    assert called_order.customer == sample_customer
    assert called_order.address == sample_address
    assert called_order.status == "pending"
    assert called_order.items == []
    assert called_order.order_date == mock_now
    assert result == mock_created_order


def test_create_order_customer_not_found(service: OrderService, mock_user_dao: MagicMock):
    """Tests that a ValueError is raised if the customer is not found."""
    mock_user_dao.find_user_by_id.return_value = None
    with pytest.raises(ValueError, match="No valid customer found with ID 99"):
        service.create_order(customer_id=99, address_id=10)


def test_create_order_user_not_customer(service: OrderService, mock_user_dao: MagicMock):
    """Tests that a ValueError is raised if the user is not a Customer instance."""
    not_a_customer = MagicMock(spec=Driver)
    mock_user_dao.find_user_by_id.return_value = not_a_customer
    with pytest.raises(ValueError, match="No valid customer found with ID 2"):
        service.create_order(customer_id=2, address_id=10)


def test_create_order_address_not_found(
    service: OrderService, mock_user_dao: MagicMock, mock_address_dao: MagicMock, sample_customer: Customer
):
    """Tests that a ValueError is raised if the address is not found."""
    mock_user_dao.find_user_by_id.return_value = sample_customer
    mock_address_dao.find_address_by_id.return_value = None
    with pytest.raises(ValueError, match="No address found with ID 99"):
        service.create_order(customer_id=1, address_id=99)


def test_create_order_dao_failure(
    service: OrderService,
    mock_user_dao: MagicMock,
    mock_address_dao: MagicMock,
    mock_order_dao: MagicMock,
    sample_customer: Customer,
    sample_address: Address,
):
    """Tests that an Exception is raised if the DAO fails to add the order."""
    mock_user_dao.find_user_by_id.return_value = sample_customer
    mock_address_dao.find_address_by_id.return_value = sample_address
    mock_order_dao.add_order.return_value = None

    with pytest.raises(Exception, match="Failed to create the order in the database."):
        service.create_order(customer_id=1, address_id=10)


def test_cancel_order_success(service: OrderService, mock_order_dao: MagicMock, sample_order_pending: Order):
    """Tests successful cancellation (deletion) of an order."""
    mock_order_dao.find_order_by_id.return_value = sample_order_pending
    mock_order_dao.delete_order.return_value = True

    result = service.cancel_order(order_id=501)

    mock_order_dao.find_order_by_id.assert_called_once_with(501)
    mock_order_dao.delete_order.assert_called_once_with(501)
    assert result is True


def test_cancel_order_not_found(service: OrderService, mock_order_dao: MagicMock):
    """Tests that a ValueError is raised if the order to cancel is not found."""
    mock_order_dao.find_order_by_id.return_value = None

    with pytest.raises(ValueError, match="No order found with ID 99."):
        service.cancel_order(order_id=99)
    mock_order_dao.delete_order.assert_not_called()


def test_cancel_order_dao_failure(service: OrderService, mock_order_dao: MagicMock, sample_order_pending: Order):
    """Tests a failure in the DAO layer during deletion."""
    mock_order_dao.find_order_by_id.return_value = sample_order_pending
    mock_order_dao.delete_order.return_value = False

    result = service.cancel_order(order_id=501)

    mock_order_dao.find_order_by_id.assert_called_once_with(501)
    mock_order_dao.delete_order.assert_called_once_with(501)
    assert result is False


def test_add_bundle_to_order_success(
    service: OrderService,
    mock_order_dao: MagicMock,
    sample_order_pending: Order,
    sample_bundle_1: AbstractBundle,
    sample_item_1: Item,
    sample_item_2: Item,
):
    """
    Tests adding a bundle with all available items to an order using the bundle object.
    """
    mock_order_dao.find_order_by_id.return_value = sample_order_pending
    mock_order_dao.update_order.return_value = sample_order_pending
    mock_order_dao.find_order_by_id.side_effect = [sample_order_pending, sample_order_pending]

    assert len(sample_order_pending.items) == 0
    assert sample_order_pending.price == 0.0

    result = service.add_bundle_to_order(order_id=501, bundle=sample_bundle_1)

    assert len(sample_order_pending.items) == 2
    assert sample_order_pending.items[0] == sample_item_1
    assert sample_order_pending.items[1] == sample_item_2
    assert sample_order_pending.price == 7.0
    mock_order_dao.update_order.assert_called_once_with(sample_order_pending)
    assert result == sample_order_pending


def test_add_bundle_to_order_item_not_available(
    service: OrderService,
    mock_order_dao: MagicMock,
    sample_order_pending: Order,
    sample_bundle_unavailable: AbstractBundle,
):
    """
    Tests that a ValueError is raised if one item in the bundle is unavailable.
    """
    mock_order_dao.find_order_by_id.return_value = sample_order_pending

    with pytest.raises(ValueError, match="unavailable because items \\['Milkshake'\\] are not available"):
        service.add_bundle_to_order(order_id=501, bundle=sample_bundle_unavailable)

    mock_order_dao.update_order.assert_not_called()
    assert len(sample_order_pending.items) == 0


def test_add_bundle_to_order_order_not_found(
    service: OrderService, mock_order_dao: MagicMock, sample_bundle_1: AbstractBundle
):
    """Tests adding a bundle when the order is not found."""
    mock_order_dao.find_order_by_id.return_value = None
    with pytest.raises(ValueError, match="No order found with ID 99."):
        service.add_bundle_to_order(order_id=99, bundle=sample_bundle_1)


def test_add_bundle_to_order_not_pending(
    service: OrderService, mock_order_dao: MagicMock, sample_order_validated: Order, sample_bundle_1: AbstractBundle
):
    """Tests adding a bundle to an already validated order."""
    mock_order_dao.find_order_by_id.return_value = sample_order_validated
    with pytest.raises(ValueError, match="Cannot modify an order with status 'validated'."):
        service.add_bundle_to_order(order_id=502, bundle=sample_bundle_1)


def test_add_bundle_to_order_dao_failure(
    service: OrderService,
    mock_order_dao: MagicMock,
    sample_order_pending: Order,
    sample_bundle_1: AbstractBundle,
):
    """
    Tests an exception if the order update fails after adding the bundle.
    """
    mock_order_dao.find_order_by_id.return_value = sample_order_pending
    mock_order_dao.update_order.return_value = None

    with pytest.raises(Exception, match="Failed to update the order."):
        service.add_bundle_to_order(order_id=501, bundle=sample_bundle_1)

    assert len(sample_order_pending.items) == 2
    mock_order_dao.update_order.assert_called_once()


def test_validate_order_success_simple(
    service: OrderService,
    mock_order_dao: MagicMock,
    mock_item_dao: MagicMock,
    sample_order_pending_with_items: Order,
    sample_item_1: Item,
    sample_item_2: Item,
):
    """Tests successful validation of an order, checking stock reduction."""
    sample_item_1.stock = 10
    sample_item_2.stock = 5
    sample_order_pending_with_items.status = "pending"

    mock_order_dao.find_order_by_id.return_value = sample_order_pending_with_items
    mock_item_dao.find_item_by_id.side_effect = (
        lambda id: sample_item_1 if id == 1 else (sample_item_2 if id == 2 else None)
    )

    mock_item_dao.update_item.return_value = True
    mock_order_dao.update_order.return_value = True

    result = service.validate_order(order_id=503)

    assert sample_item_1.stock == 9
    assert sample_item_2.stock == 4
    assert mock_item_dao.update_item.call_count == 2
    assert sample_order_pending_with_items.status == "validated"
    mock_order_dao.update_order.assert_called_once_with(sample_order_pending_with_items)
    assert result == sample_order_pending_with_items


def test_validate_order_success_complex_stock(
    service: OrderService,
    mock_order_dao: MagicMock,
    mock_item_dao: MagicMock,
    sample_item_1: Item,
    sample_item_2: Item,
):
    """Tests validation with multiple bundles and duplicate items."""
    sample_item_1.stock = 10
    sample_item_2.stock = 5

    complex_order = MagicMock(
        spec=Order, id=504, status="pending", items=[sample_item_1, sample_item_2, sample_item_1, sample_item_1]
    )

    mock_order_dao.find_order_by_id.return_value = complex_order
    mock_item_dao.find_item_by_id.side_effect = (
        lambda id: sample_item_1 if id == 1 else (sample_item_2 if id == 2 else None)
    )
    mock_item_dao.update_item.return_value = True
    mock_order_dao.update_order.return_value = True

    service.validate_order(order_id=504)

    assert sample_item_1.stock == 7
    assert sample_item_2.stock == 4
    assert complex_order.status == "validated"


def test_validate_order_stock_to_zero(
    service: OrderService,
    mock_order_dao: MagicMock,
    mock_item_dao: MagicMock,
    sample_order_pending_with_items: Order,
    sample_item_1: Item,
    sample_item_2: Item,
):
    """Tests that item availability is set to False when stock hits 0."""
    sample_item_1.stock = 1
    sample_item_1.availability = True
    sample_item_2.stock = 1
    sample_item_2.availability = True
    sample_order_pending_with_items.status = "pending"

    mock_order_dao.find_order_by_id.return_value = sample_order_pending_with_items
    mock_item_dao.find_item_by_id.side_effect = (
        lambda id: sample_item_1 if id == 1 else (sample_item_2 if id == 2 else None)
    )
    mock_item_dao.update_item.return_value = True
    mock_order_dao.update_order.return_value = True

    service.validate_order(order_id=503)

    assert sample_item_1.stock == 0
    assert sample_item_1.availability is False
    assert sample_item_2.stock == 0
    assert sample_item_2.availability is False


def test_validate_order_not_enough_stock(
    service: OrderService,
    mock_order_dao: MagicMock,
    mock_item_dao: MagicMock,
    sample_order_pending_with_items: Order,
    sample_item_1: Item,
    sample_item_2: Item,
):
    """Tests that a ValueError is raised if stock is insufficient."""
    sample_item_1.stock = 10
    sample_item_2.stock = 0
    sample_order_pending_with_items.status = "pending"

    mock_order_dao.find_order_by_id.return_value = sample_order_pending_with_items
    mock_item_dao.find_item_by_id.side_effect = (
        lambda id: sample_item_1 if id == 1 else (sample_item_2 if id == 2 else None)
    )

    with pytest.raises(ValueError, match="Not enough stock for item 'Fries'. Needed: 1, Available: 0."):
        service.validate_order(order_id=503)

    mock_item_dao.update_item.assert_not_called()
    mock_order_dao.update_order.assert_not_called()


def test_validate_order_item_not_found_in_db(
    service: OrderService,
    mock_order_dao: MagicMock,
    mock_item_dao: MagicMock,
    sample_order_pending_with_items: Order,
    sample_item_1: Item,
):
    """Tests that an Exception is raised if a required item no longer exists."""
    sample_order_pending_with_items.status = "pending"
    mock_order_dao.find_order_by_id.return_value = sample_order_pending_with_items
    mock_item_dao.find_item_by_id.side_effect = lambda id: sample_item_1 if id == 1 else None

    with pytest.raises(Exception, match="Item ID 2 required for order no longer exists."):
        service.validate_order(order_id=503)

    mock_item_dao.update_item.assert_not_called()
    mock_order_dao.update_order.assert_not_called()


def test_validate_order_not_found(service: OrderService, mock_order_dao: MagicMock):
    """Tests validation on a non-existent order."""
    mock_order_dao.find_order_by_id.return_value = None
    with pytest.raises(ValueError, match="No order found with ID 99."):
        service.validate_order(order_id=99)


def test_validate_order_not_pending(service: OrderService, mock_order_dao: MagicMock, sample_order_validated: Order):
    """Tests validation on an already validated order."""
    mock_order_dao.find_order_by_id.return_value = sample_order_validated
    with pytest.raises(ValueError, match="Only 'pending' orders can be validated. Current status: 'validated'."):
        service.validate_order(order_id=502)


def test_validate_order_empty_order(service: OrderService, mock_order_dao: MagicMock, sample_order_pending: Order):
    """Tests validation on an order with no items."""
    mock_order_dao.find_order_by_id.return_value = sample_order_pending
    with pytest.raises(ValueError, match="Cannot validate an empty order."):
        service.validate_order(order_id=501)


def test_validate_order_item_update_fails(
    service: OrderService,
    mock_order_dao: MagicMock,
    mock_item_dao: MagicMock,
    sample_order_pending_with_items: Order,
    sample_item_1: Item,
    sample_item_2: Item,
):
    """Tests that an Exception is raised if item stock update fails."""
    sample_item_1.stock = 10
    sample_item_2.stock = 5
    sample_order_pending_with_items.status = "pending"
    mock_order_dao.find_order_by_id.return_value = sample_order_pending_with_items
    mock_item_dao.find_item_by_id.side_effect = (
        lambda id: sample_item_1 if id == 1 else (sample_item_2 if id == 2 else None)
    )
    mock_item_dao.update_item.side_effect = [True, False]

    with pytest.raises(Exception, match="Failed to update stock for item 2."):
        service.validate_order(order_id=503)

    mock_order_dao.update_order.assert_not_called()


def test_validate_order_status_update_fails(
    service: OrderService,
    mock_order_dao: MagicMock,
    mock_item_dao: MagicMock,
    sample_order_pending_with_items: Order,
    sample_item_1: Item,
    sample_item_2: Item,
):
    """Tests exception if stock updates but order status update fails."""
    sample_item_1.stock = 10
    sample_item_2.stock = 5
    sample_order_pending_with_items.status = "pending"
    mock_order_dao.find_order_by_id.return_value = sample_order_pending_with_items
    mock_item_dao.find_item_by_id.side_effect = (
        lambda id: sample_item_1 if id == 1 else (sample_item_2 if id == 2 else None)
    )
    mock_item_dao.update_item.return_value = True
    mock_order_dao.update_order.return_value = None

    with pytest.raises(Exception, match="Stock was updated, but failed to validate the order status."):
        service.validate_order(order_id=503)

    assert mock_item_dao.update_item.call_count == 2
    assert sample_order_pending_with_items.status == "validated"
    mock_order_dao.update_order.assert_called_once()


def test_get_order_details_success(service: OrderService, mock_order_dao: MagicMock, sample_order_validated: Order):
    """Tests retrieving details for a single order."""
    mock_order_dao.find_order_by_id.return_value = sample_order_validated

    result = service.get_order_details(order_id=502)

    assert result == sample_order_validated
    mock_order_dao.find_order_by_id.assert_called_once_with(502)


def test_get_order_details_not_found(service: OrderService, mock_order_dao: MagicMock):
    """Tests retrieving a non-existent order."""
    mock_order_dao.find_order_by_id.return_value = None
    with pytest.raises(ValueError, match="No order found with ID 99."):
        service.get_order_details(order_id=99)


def test_list_orders_for_customer_success(
    service: OrderService,
    mock_user_dao: MagicMock,
    mock_order_dao: MagicMock,
    sample_customer: Customer,
    sample_order_validated: Order,
    sample_order_pending: Order,
):
    """Tests retrieving the order history for a customer."""
    mock_user_dao.find_user_by_id.return_value = sample_customer
    order_list = [sample_order_validated, sample_order_pending]
    mock_order_dao.find_orders_by_customer.return_value = order_list

    result = service.list_orders_for_customer(customer_id=1)

    assert result == order_list
    mock_user_dao.find_user_by_id.assert_called_once_with(1)
    mock_order_dao.find_orders_by_customer.assert_called_once_with(1)


def test_list_orders_for_customer_no_orders(
    service: OrderService, mock_user_dao: MagicMock, mock_order_dao: MagicMock, sample_customer: Customer
):
    """Tests retrieving history for a customer with zero orders."""
    mock_user_dao.find_user_by_id.return_value = sample_customer
    mock_order_dao.find_orders_by_customer.return_value = []

    result = service.list_orders_for_customer(customer_id=1)

    assert result == []
    mock_order_dao.find_orders_by_customer.assert_called_once_with(1)


def test_list_orders_for_customer_not_found(service: OrderService, mock_user_dao: MagicMock):
    """Tests listing orders for a non-existent customer."""
    mock_user_dao.find_user_by_id.return_value = None
    with pytest.raises(ValueError, match="No valid customer found with ID 99"):
        service.list_orders_for_customer(customer_id=99)


def test_list_orders_for_customer_user_not_customer(service: OrderService, mock_user_dao: MagicMock):
    """Tests listing orders for a user ID that is not a customer."""
    not_a_customer = MagicMock(spec=Driver)
    mock_user_dao.find_user_by_id.return_value = not_a_customer
    with pytest.raises(ValueError, match="No valid customer found with ID 99"):
        service.list_orders_for_customer(customer_id=99)
