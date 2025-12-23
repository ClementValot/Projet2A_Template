from unittest.mock import ANY, MagicMock, patch

import pytest

from src.DAO.addressDAO import AddressDAO
from src.DAO.bundleDAO import BundleDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.deliveryDAO import DeliveryDAO
from src.DAO.itemDAO import ItemDAO
from src.DAO.orderDAO import OrderDAO
from src.DAO.userDAO import UserDAO
from src.Model.delivery import Delivery
from src.Model.order import Order
from src.Service.admin_order_service import AdminOrderService


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
def mock_delivery_dao():
    """Provides a mock DeliveryDAO."""
    return MagicMock(spec=DeliveryDAO)



@pytest.fixture
def service(
    mock_db_connector,
    mock_item_dao,
    mock_user_dao,
    mock_address_dao,
    mock_bundle_dao,
    mock_order_dao,
    mock_delivery_dao,
    mocker,
):
    """
    Provides an AdminOrderService instance with mocked DAOs.
    Injects delivery_dao manually as it is called but not initialized in the service.
    """
    mocker.patch("src.Service.admin_order_service.ItemDAO", return_value=mock_item_dao)
    mocker.patch("src.Service.admin_order_service.UserDAO", return_value=mock_user_dao)
    mocker.patch("src.Service.admin_order_service.AddressDAO", return_value=mock_address_dao)
    mocker.patch("src.Service.admin_order_service.BundleDAO", return_value=mock_bundle_dao)
    mocker.patch("src.Service.admin_order_service.OrderDAO", return_value=mock_order_dao)

    admin_service = AdminOrderService(db_connector=mock_db_connector)

    admin_service.delivery_dao = mock_delivery_dao

    return admin_service



@pytest.fixture
def sample_order_pending():
    """Provides a mock Order with 'pending' status."""
    return MagicMock(spec=Order, status="pending", id=101)


@pytest.fixture
def sample_order_validated():
    """Provides a mock Order with 'validated' status."""
    return MagicMock(spec=Order, status="validated", id=102)


@pytest.fixture
def sample_order_delivered():
    """Provides a mock Order with 'delivered' status."""
    return MagicMock(spec=Order, status="delivered", id=103)


@pytest.fixture
def sample_delivery_inprogress():
    """Provides a mock Delivery with 'in_progress' status."""
    return MagicMock(spec=Delivery, status="in_progress", id=50)


@pytest.fixture
def sample_delivery_completed():
    """Provides a mock Delivery with 'completed' status."""
    return MagicMock(spec=Delivery, status="completed", id=51)



def test_list_waiting_orders_filters_pending(
    service: AdminOrderService,
    mock_order_dao: MagicMock,
    sample_order_pending: Order,
    sample_order_validated: Order,
    sample_order_delivered: Order,
):
    """
    Tests that list_waiting_orders returns only orders with status 'pending'.
    """
    all_orders = [sample_order_pending, sample_order_validated, sample_order_delivered]
    mock_order_dao.find_all_orders.return_value = all_orders

    result = service.list_waiting_orders()

    mock_order_dao.find_all_orders.assert_called_once()
    assert len(result) == 1
    assert result == [sample_order_pending]


def test_list_waiting_orders_returns_empty_list_if_none_pending(
    service: AdminOrderService,
    mock_order_dao: MagicMock,
    sample_order_validated: Order,
):
    """
    Tests that an empty list is returned if no orders have the 'pending' status.
    """
    non_pending_orders = [sample_order_validated]
    mock_order_dao.find_all_orders.return_value = non_pending_orders

    result = service.list_waiting_orders()

    assert result == []


def test_list_waiting_orders_returns_empty_list_if_dao_returns_empty(
    service: AdminOrderService, mock_order_dao: MagicMock
):
    """
    Tests that an empty list is returned if the DAO finds no orders.
    """
    mock_order_dao.find_all_orders.return_value = []

    result = service.list_waiting_orders()

    assert result == []



def test_list_deliveries_success(
    service: AdminOrderService,
    mock_delivery_dao: MagicMock,
    sample_delivery_inprogress: Delivery,
    sample_delivery_completed: Delivery,
):
    """
    Tests that list_deliveries calls the underlying DAO and returns the results.
    """
    expected_deliveries = [sample_delivery_inprogress, sample_delivery_completed]

    mock_delivery_dao.list_deliveries = MagicMock(return_value=expected_deliveries)

    result = service.list_deliveries()

    mock_delivery_dao.list_deliveries.assert_called_once()
    assert result == expected_deliveries
    assert len(result) == 2


def test_list_deliveries_returns_empty_list(service: AdminOrderService, mock_delivery_dao: MagicMock):
    """
    Tests that an empty list is returned if the DAO finds no deliveries.
    """
    mock_delivery_dao.list_deliveries = MagicMock(return_value=[])

    result = service.list_deliveries()

    mock_delivery_dao.list_deliveries.assert_called_once()
    assert result == []
