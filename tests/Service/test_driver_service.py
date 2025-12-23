from datetime import datetime
from unittest.mock import ANY, MagicMock

import pytest

from src.DAO.addressDAO import AddressDAO
from src.DAO.bundleDAO import BundleDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.deliveryDAO import DeliveryDAO
from src.DAO.itemDAO import ItemDAO
from src.DAO.orderDAO import OrderDAO
from src.DAO.userDAO import UserDAO
from src.Model.address import Address
from src.Model.customer import Customer
from src.Model.delivery import Delivery
from src.Model.driver import Driver
from src.Model.order import Order
from src.Service.driver_service import DriverService


@pytest.fixture
def mock_db_connector():
    return MagicMock(spec=DBConnector)


@pytest.fixture
def mock_item_dao():
    return MagicMock(spec=ItemDAO)


@pytest.fixture
def mock_user_dao():
    return MagicMock(spec=UserDAO)


@pytest.fixture
def mock_address_dao():
    return MagicMock(spec=AddressDAO)


@pytest.fixture
def mock_bundle_dao():
    return MagicMock(spec=BundleDAO)


@pytest.fixture
def mock_order_dao():
    return MagicMock(spec=OrderDAO)


@pytest.fixture
def mock_delivery_dao():
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
    mocker.patch("src.Service.driver_service.ItemDAO", return_value=mock_item_dao)
    mocker.patch("src.Service.driver_service.UserDAO", return_value=mock_user_dao)
    mocker.patch("src.Service.driver_service.AddressDAO", return_value=mock_address_dao)
    mocker.patch("src.Service.driver_service.BundleDAO", return_value=mock_bundle_dao)
    mocker.patch("src.Service.driver_service.OrderDAO", return_value=mock_order_dao)
    mocker.patch("src.Service.driver_service.DeliveryDAO", return_value=mock_delivery_dao)
    mocker.patch("src.Service.driver_service.ApiMapsService")

    driver_service = DriverService(db_connector=mock_db_connector)
    return driver_service


@pytest.fixture
def sample_driver_available():
    driver = MagicMock(spec=Driver)
    driver.id = 1
    driver.name = "Test Driver"
    driver.availability = True
    return driver


@pytest.fixture
def sample_driver_unavailable():
    driver = MagicMock(spec=Driver)
    driver.id = 2
    driver.name = "Busy Driver"
    driver.availability = False
    return driver


@pytest.fixture
def sample_customer():
    customer = MagicMock(spec=Customer)
    customer.id = 10
    customer.name = "Test Customer"
    customer.phone_number = "+33612345678"
    return customer


@pytest.fixture
def sample_address():
    address = MagicMock(spec=Address)
    address.street_number = "123"
    address.street_name = "Main St"
    address.city = "Testville"
    return address


@pytest.fixture
def sample_order_pending(sample_customer, sample_address):
    order = MagicMock(spec=Order)
    order.id = 101
    order.status = "pending"
    order.customer = sample_customer
    order.address = sample_address
    order.id_order = 101
    return order


@pytest.fixture
def sample_order_validated(sample_customer, sample_address):
    order = MagicMock(spec=Order)
    order.id = 102
    order.status = "validated"
    order.customer = sample_customer
    order.address = sample_address
    return order


@pytest.fixture
def sample_delivery_inprogress(sample_driver_available, sample_order_pending):
    delivery = MagicMock(spec=Delivery)
    delivery.id = 50
    delivery.driver = sample_driver_available
    delivery.orders = [sample_order_pending]
    delivery.status = "in_progress"
    delivery.delivery_time = None
    return delivery


@pytest.fixture
def sample_delivery_pending():
    delivery = MagicMock(spec=Delivery)
    delivery.id = 51
    delivery.status = "pending"
    return delivery


def test_create_and_assign_delivery_success(
    service: DriverService,
    mock_user_dao: MagicMock,
    mock_order_dao: MagicMock,
    mock_delivery_dao: MagicMock,
    sample_driver_available: Driver,
    sample_order_pending: Order,
):
    mock_user_dao.find_user_by_id.return_value = sample_driver_available
    mock_order_dao.find_order_by_id.return_value = sample_order_pending

    mock_created_delivery = MagicMock(spec=Delivery, id=1)
    mock_delivery_dao.add_delivery.return_value = mock_created_delivery
    mock_order_dao.update_order.return_value = True
    mock_user_dao.update_user.return_value = True

    order_ids = [sample_order_pending.id]
    driver_id = sample_driver_available.id

    result = service.create_and_assign_delivery(order_ids, driver_id)

    mock_user_dao.find_user_by_id.assert_called_once_with(driver_id)
    mock_order_dao.find_order_by_id.assert_called_once_with(sample_order_pending.id)

    assert sample_order_pending.status == "in_progress"
    mock_order_dao.update_order.assert_called_once_with(sample_order_pending)

    assert sample_driver_available.availability is False
    mock_user_dao.update_user.assert_called_once_with(sample_driver_available)

    mock_delivery_dao.add_delivery.assert_called_once_with(ANY)
    called_delivery = mock_delivery_dao.add_delivery.call_args[0][0]
    assert isinstance(called_delivery, Delivery)
    assert called_delivery.driver == sample_driver_available
    assert called_delivery.orders == [sample_order_pending]
    assert called_delivery.status == "in_progress"

    assert result == mock_created_delivery


def test_create_delivery_validation_no_orders(service: DriverService):
    with pytest.raises(ValueError, match="Cannot create a delivery with no orders."):
        service.create_and_assign_delivery(order_ids=[], user_id=1)


def test_create_delivery_validation_driver_not_found(service: DriverService, mock_user_dao: MagicMock):
    mock_user_dao.find_user_by_id.return_value = None
    with pytest.raises(ValueError, match="No valid driver found with ID 999"):
        service.create_and_assign_delivery(order_ids=[101], user_id=999)


def test_create_delivery_validation_user_is_not_driver(service: DriverService, mock_user_dao: MagicMock):
    not_a_driver = MagicMock(spec=Customer)
    mock_user_dao.find_user_by_id.return_value = not_a_driver
    with pytest.raises(ValueError, match="No valid driver found with ID 3"):
        service.create_and_assign_delivery(order_ids=[101], user_id=3)


def test_create_delivery_validation_driver_not_available(
    service: DriverService, mock_user_dao: MagicMock, sample_driver_unavailable: Driver
):
    mock_user_dao.find_user_by_id.return_value = sample_driver_unavailable
    with pytest.raises(ValueError, match="is not available to start a new delivery."):
        service.create_and_assign_delivery(order_ids=[101], user_id=sample_driver_unavailable.id)


def test_create_delivery_validation_order_not_found(
    service: DriverService, mock_user_dao: MagicMock, mock_order_dao: MagicMock, sample_driver_available: Driver
):
    mock_user_dao.find_user_by_id.return_value = sample_driver_available
    mock_order_dao.find_order_by_id.return_value = None
    with pytest.raises(ValueError, match="Order with ID 999 not found."):
        service.create_and_assign_delivery(order_ids=[999], user_id=sample_driver_available.id)


def test_create_delivery_validation_order_not_pending(
    service: DriverService,
    mock_user_dao: MagicMock,
    mock_order_dao: MagicMock,
    sample_driver_available: Driver,
    sample_order_validated: Order,
):
    mock_user_dao.find_user_by_id.return_value = sample_driver_available
    mock_order_dao.find_order_by_id.return_value = sample_order_validated
    with pytest.raises(ValueError, match="has not the pending status. Current status: validated"):
        service.create_and_assign_delivery(order_ids=[sample_order_validated.id], user_id=sample_driver_available.id)


def test_create_delivery_dao_failure(
    service: DriverService,
    mock_user_dao: MagicMock,
    mock_order_dao: MagicMock,
    mock_delivery_dao: MagicMock,
    sample_driver_available: Driver,
    sample_order_pending: Order,
):
    mock_user_dao.find_user_by_id.return_value = sample_driver_available
    mock_order_dao.find_order_by_id.return_value = sample_order_pending
    mock_delivery_dao.add_delivery.return_value = None

    with pytest.raises(Exception, match="Failed to create and assign the delivery in the database."):
        service.create_and_assign_delivery(order_ids=[101], user_id=1)


def test_complete_delivery_success(
    service: DriverService,
    mock_delivery_dao: MagicMock,
    mock_order_dao: MagicMock,
    sample_delivery_inprogress: Delivery,
    mocker,
):
    mock_delivery_dao.find_delivery_by_id.return_value = sample_delivery_inprogress
    mock_delivery_dao.update_delivery.return_value = sample_delivery_inprogress

    mock_now = datetime(2025, 11, 5, 12, 30, 0)
    mocker.patch("src.Service.driver_service.datetime").now.return_value = mock_now

    result = service.complete_delivery(sample_delivery_inprogress.id)

    mock_delivery_dao.find_delivery_by_id.assert_called_once_with(sample_delivery_inprogress.id)

    assert sample_delivery_inprogress.status == "delivered"
    assert sample_delivery_inprogress.delivery_time == mock_now

    for order in sample_delivery_inprogress.orders:
        assert order.status == "delivered"
        mock_order_dao.update_order.assert_called_with(order)

    mock_delivery_dao.update_delivery.assert_called_once_with(sample_delivery_inprogress)
    assert result == sample_delivery_inprogress


def test_complete_delivery_validation_not_found(service: DriverService, mock_delivery_dao: MagicMock):
    mock_delivery_dao.find_delivery_by_id.return_value = None
    with pytest.raises(ValueError, match="No delivery found with ID 999."):
        service.complete_delivery(999)


def test_complete_delivery_validation_wrong_status(
    service: DriverService, mock_delivery_dao: MagicMock, sample_delivery_pending: Delivery
):
    mock_delivery_dao.find_delivery_by_id.return_value = sample_delivery_pending
    with pytest.raises(ValueError, match="Only 'in_progress' deliveries can be completed. Current status: pending"):
        service.complete_delivery(sample_delivery_pending.id)


def test_complete_delivery_order_update_fails(
    service: DriverService,
    mock_delivery_dao: MagicMock,
    mock_order_dao: MagicMock,
    sample_delivery_inprogress: Delivery,
    caplog,
):
    mock_delivery_dao.find_delivery_by_id.return_value = sample_delivery_inprogress
    mock_delivery_dao.update_delivery.return_value = sample_delivery_inprogress
    mock_order_dao.update_order.side_effect = Exception("DB Error")

    service.complete_delivery(sample_delivery_inprogress.id)

    assert "Could not update status for orders in delivery 50: DB Error" in caplog.text

    assert sample_delivery_inprogress.status == "delivered"
    mock_delivery_dao.update_delivery.assert_called_once_with(sample_delivery_inprogress)


def test_complete_delivery_dao_failure(
    service: DriverService, mock_delivery_dao: MagicMock, sample_delivery_inprogress: Delivery
):
    mock_delivery_dao.find_delivery_by_id.return_value = sample_delivery_inprogress
    mock_delivery_dao.update_delivery.return_value = None

    with pytest.raises(Exception, match="Failed to update delivery status to completed."):
        service.complete_delivery(sample_delivery_inprogress.id)


def test_get_delivery_details_returns_dicts(
    service: DriverService,
    mock_delivery_dao: MagicMock,
    mock_user_dao: MagicMock,
    sample_delivery_inprogress: Delivery,
    sample_address: Address,
    sample_customer: Customer,
):
    mock_delivery_dao.find_delivery_by_id.return_value = sample_delivery_inprogress
    mock_user_dao.find_user_by_id.return_value = sample_customer

    result_addresses, result_customers, result_phones = service.get_delivery_details(sample_delivery_inprogress.id)

    mock_delivery_dao.find_delivery_by_id.assert_called_once_with(sample_delivery_inprogress.id)

    expected_address = sample_address
    assert isinstance(result_addresses, dict)
    assert len(result_addresses) == 1
    assert result_addresses[sample_delivery_inprogress.orders[0].id] == expected_address

    expected_customer_name = sample_customer.name
    assert isinstance(result_customers, dict)
    assert len(result_customers) == 1
    assert result_customers[sample_delivery_inprogress.orders[0].id] == expected_customer_name


def test_get_delivery_details_not_found(service: DriverService, mock_delivery_dao: MagicMock):
    mock_delivery_dao.find_delivery_by_id.return_value = None

    with pytest.raises(ValueError, match="No delivery found with ID 999."):
        service.get_delivery_details(999)


def test_list_pending_orders_success(
    service: DriverService,
    mock_order_dao: MagicMock,
    sample_order_pending: Order,
    sample_order_validated: Order,
):
    all_orders = [sample_order_pending, sample_order_validated]
    mock_order_dao.find_all_orders.return_value = all_orders

    result = service.list_pending_orders()

    assert result == [sample_order_pending]
    mock_order_dao.find_all_orders.assert_called_once()


def test_list_pending_orders_empty(service: DriverService, mock_order_dao: MagicMock):
    mock_order_dao.find_all_orders.return_value = []

    result = service.list_pending_orders()

    assert result == []


def test_get_assigned_delivery_success(
    service: DriverService, mock_delivery_dao: MagicMock, sample_delivery_inprogress: Delivery
):
    mock_delivery_dao.find_in_progress_deliveries_by_driver.return_value = [sample_delivery_inprogress]

    result = service.get_assigned_delivery(user_id=1)

    mock_delivery_dao.find_in_progress_deliveries_by_driver.assert_called_once_with(1)
    assert result == [sample_delivery_inprogress]


def test_get_assigned_delivery_no_delivery(service: DriverService, mock_delivery_dao: MagicMock):
    mock_delivery_dao.find_in_progress_deliveries_by_driver.return_value = []

    result = service.get_assigned_delivery(user_id=1)

    assert result == []


def test_get_itinerary_success(
    service: DriverService,
    mock_delivery_dao: MagicMock,
    mock_user_dao: MagicMock,
    sample_driver_available: Driver,
    sample_delivery_inprogress: Delivery,
    mocker,
):
    mock_delivery_dao.find_in_progress_deliveries_by_driver.return_value = [sample_delivery_inprogress]
    mock_user_dao.find_user_by_id.return_value = sample_driver_available

    mock_api_class = mocker.patch("src.Service.driver_service.ApiMapsService")
    mock_api_instance = mock_api_class.return_value
    mock_api_instance.Driveritinerary.return_value = "Itinerary map URL"

    result = service.get_itinerary(user_id=sample_driver_available.id)

    expected_addresses = [
        f"{sample_delivery_inprogress.orders[0].address.street_number} "
        f"{sample_delivery_inprogress.orders[0].address.street_name}, "
        f"{sample_delivery_inprogress.orders[0].address.city}, France"
    ]

    mock_api_instance.Driveritinerary.assert_called_once_with(expected_addresses)
    assert result == "Itinerary map URL"


def test_get_itinerary_no_delivery(service: DriverService, mock_delivery_dao: MagicMock):
    mock_delivery_dao.find_in_progress_deliveries_by_driver.return_value = []

    result = service.get_itinerary(user_id=1)

    assert result is None


def test_get_itinerary_driver_not_found(service: DriverService, mock_delivery_dao: MagicMock, mock_user_dao: MagicMock):
    mock_delivery_dao.find_in_progress_deliveries_by_driver.return_value = [MagicMock(spec=Delivery)]
    mock_user_dao.find_user_by_id.return_value = None

    with pytest.raises(ValueError, match="No valid driver found with ID 99"):
        service.get_itinerary(user_id=99)