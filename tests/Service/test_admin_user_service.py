from unittest.mock import ANY, MagicMock

import pytest

from src.DAO.DBConnector import DBConnector
from src.DAO.userDAO import UserDAO
from src.Model.admin import Admin
from src.Model.customer import Customer
from src.Model.driver import Driver

from src.Service.admin_user_service import AdminUserService
from src.Service.password_service import PasswordService



@pytest.fixture
def mock_db_connector():
    """Provides a mock DBConnector."""
    return MagicMock(spec=DBConnector)


@pytest.fixture
def mock_user_dao():
    """Provides a mock UserDAO."""
    return MagicMock(spec=UserDAO)


@pytest.fixture
def mock_password_service():
    """Provides a mock PasswordService instance."""
    mock_ps = MagicMock(spec=PasswordService)
    mock_ps.create_salt.return_value = "generated_salt"
    mock_ps.hash_password.return_value = "generated_hash"
    mock_ps.check_password_strength.return_value = None
    return mock_ps


@pytest.fixture
def service(mock_db_connector, mock_user_dao, mock_password_service, mocker):
    """
    Provides an AdminUserService instance with mocked UserDAO and PasswordService.
    """
    mocker.patch("src.Service.admin_user_service.UserDAO", return_value=mock_user_dao)

    admin_service = AdminUserService(db_connector=mock_db_connector, password_service=mock_password_service)

    assert admin_service.user_dao == mock_user_dao
    assert admin_service.password_service == mock_password_service

    return admin_service


@pytest.fixture
def sample_admin():
    """Provides a mock Admin user."""
    return MagicMock(spec=Admin, id=1, name="Sample Admin")


@pytest.fixture
def sample_driver():
    """Provides a mock Driver user."""
    return MagicMock(spec=Driver, id=2, name="Sample Driver", availability=True)


@pytest.fixture
def sample_customer():
    """Provides a mock Customer user."""
    return MagicMock(spec=Customer, id=3, name="Sample Customer")


@pytest.fixture
def sample_user_list(sample_admin, sample_driver, sample_customer):
    """Provides a list of various users."""
    return [sample_admin, sample_driver, sample_customer]


@pytest.fixture
def sample_driver_list(sample_driver):
    """Provides a list containing only drivers."""
    driver2 = MagicMock(spec=Driver, id=4, name="Driver Two", availability=False)
    return [sample_driver, driver2]


def test_create_admin_account_success(
    service: AdminUserService, mock_user_dao: MagicMock, mock_password_service: MagicMock
):
    """Tests the successful creation of an admin account."""
    mock_user_dao.find_user_by_username.return_value = None
    mock_password_service.create_salt.return_value = "testsalt"
    mock_password_service.hash_password.return_value = "testhash123"

    created_admin_mock = MagicMock(spec=Admin, id=1, username="newadmin", name="New Admin")
    mock_user_dao.add_user.return_value = created_admin_mock

    result = service.create_admin_account("newadmin", "ValidPass123", "New Admin", "123456")

    mock_user_dao.find_user_by_username.assert_called_once_with("newadmin")
    mock_password_service.check_password_strength.assert_called_once_with("ValidPass123")
    mock_password_service.create_salt.assert_called_once()
    mock_password_service.hash_password.assert_called_once_with("ValidPass123", "testsalt")

    mock_user_dao.add_user.assert_called_once_with(ANY)
    called_admin_obj = mock_user_dao.add_user.call_args[0][0]

    assert isinstance(called_admin_obj, Admin)
    assert called_admin_obj.username == "newadmin"
    assert called_admin_obj._hash_password == "testhash123"
    assert called_admin_obj._salt == "testsalt"
    assert called_admin_obj.phone_number == "123456"

    assert result == created_admin_mock


def test_create_admin_account_username_exists(
    service: AdminUserService, mock_user_dao: MagicMock, mock_password_service: MagicMock
):
    """Tests that a ValueError is raised if the username already exists."""
    mock_user_dao.find_user_by_username.return_value = MagicMock(spec=Admin)

    with pytest.raises(ValueError, match="Username 'admin' already exists."):
        service.create_admin_account("admin", "pass123", "Name", "111")

    mock_password_service.hash_password.assert_not_called()
    mock_user_dao.add_user.assert_not_called()


@pytest.mark.parametrize(
    "username, password, name",
    [
        ("", "pass123", "Name"),
        ("admin", "", "Name"),
        ("admin", "pass123", ""),
    ],
)
def test_create_admin_account_empty_fields(service: AdminUserService, username, password, name):
    """Tests that required fields (username, password, name) cannot be empty."""
    with pytest.raises(ValueError, match="Username, password, and name are required."):
        service.create_admin_account(username, password, name, "123456")


def test_create_admin_account_weak_password(
    service: AdminUserService, mock_user_dao: MagicMock, mock_password_service: MagicMock
):
    """Tests that a weak password (as defined by PasswordService) raises an exception."""
    mock_user_dao.find_user_by_username.return_value = None
    mock_password_service.check_password_strength.side_effect = ValueError("Password is too weak.")

    with pytest.raises(ValueError, match="Password is too weak."):
        service.create_admin_account("newadmin", "123", "New Admin", "123456")

    mock_user_dao.add_user.assert_not_called()


def test_create_admin_account_dao_failure(
    service: AdminUserService, mock_user_dao: MagicMock, mock_password_service: MagicMock
):
    """Tests that an Exception is raised if the DAO fails to add the user."""
    mock_user_dao.find_user_by_username.return_value = None
    mock_password_service.create_salt.return_value = "testsalt"
    mock_password_service.hash_password.return_value = "testhash123"
    mock_user_dao.add_user.return_value = None

    with pytest.raises(Exception, match="Failed to create admin account in the database."):
        service.create_admin_account("newadmin", "ValidPass123", "New Admin", "123456")




def test_create_driver_account_success_secure(
    service: AdminUserService, mock_user_dao: MagicMock, mock_password_service: MagicMock
):
    """
    Tests successful creation of a driver, verifying that hashing and salting are used.
    """
    mock_user_dao.find_user_by_username.return_value = None 
    mock_password_service.create_salt.return_value = "driversalt"
    mock_password_service.hash_password.return_value = "driverhash"

    created_driver_mock = MagicMock(spec=Driver, id=2, username="newdriver", name="New Driver", availability=True)
    mock_user_dao.add_user.return_value = created_driver_mock

    result = service.create_driver_account(
        "newdriver", "DriverPass123", "New Driver", "555666", "car", availability=True
    )

    mock_user_dao.find_user_by_username.assert_called_once_with("newdriver")

    mock_password_service.check_password_strength.assert_called_once_with("DriverPass123")
    mock_password_service.create_salt.assert_called_once()
    mock_password_service.hash_password.assert_called_once_with("DriverPass123", "driversalt")

    mock_user_dao.add_user.assert_called_once_with(ANY)
    called_driver_obj = mock_user_dao.add_user.call_args[0][0]

    assert isinstance(called_driver_obj, Driver)
    assert called_driver_obj.username == "newdriver"
    assert called_driver_obj._hash_password == "driverhash" 
    assert called_driver_obj._salt == "driversalt"
    assert called_driver_obj.vehicle_type == "car"
    assert called_driver_obj.availability is True

    assert result == created_driver_mock


def test_create_driver_account_username_exists(service: AdminUserService, mock_user_dao: MagicMock):
    """Tests that a ValueError is raised if the driver's username already exists."""
    mock_user_dao.find_user_by_username.return_value = MagicMock(spec=Customer)  

    with pytest.raises(ValueError, match="Username 'driver' already exists."):
        service.create_driver_account("driver", "pass123", "Name", "111", "van")

    mock_user_dao.add_user.assert_not_called()


@pytest.mark.parametrize(
    "username, password, name, phone_number, vehicle_type, error_match",
    [
        ("", "p", "N", "1", "car", "Username, password, name, and phone number are required."),
        ("u", "", "N", "1", "car", "Username, password, name, and phone number are required."),
        ("u", "p", "", "1", "car", "Username, password, name, and phone number are required."),
        ("u", "p", "N", "", "car", "Username, password, name, and phone number are required."),
        ("u", "p", "N", "1", "", "Vehicle type is required for a driver."),
    ],
)
def test_create_driver_account_empty_required_fields(
    service: AdminUserService, username, password, name, phone_number, vehicle_type, error_match
):
    """Tests that required fields cannot be empty."""
    with pytest.raises(ValueError, match=error_match):
        service.create_driver_account(username, password, name, phone_number, vehicle_type)

    service.user_dao.find_user_by_username.assert_not_called()


def test_create_driver_account_weak_password(
    service: AdminUserService, mock_user_dao: MagicMock, mock_password_service: MagicMock
):
    """Tests that a weak password (as defined by PasswordService) raises an exception."""
    mock_user_dao.find_user_by_username.return_value = None
    mock_password_service.check_password_strength.side_effect = ValueError("Driver password is too weak.")

    with pytest.raises(ValueError, match="Driver password is too weak."):
        service.create_driver_account("newdriver", "123", "New Driver", "555666", "car")

    mock_user_dao.add_user.assert_not_called()


def test_create_driver_account_dao_failure(service: AdminUserService, mock_user_dao: MagicMock):
    """Tests that an Exception is raised if the DAO fails to add the driver."""
    mock_user_dao.find_user_by_username.return_value = None
    mock_user_dao.add_user.return_value = None

    with pytest.raises(Exception, match="Failed to create driver account in the database."):
        service.create_driver_account("newdriver", "DriverPass123", "New Driver", "555666", "car")




def test_update_driver_availability_success(service: AdminUserService, mock_user_dao: MagicMock, sample_driver: Driver):
    """Tests successfully updating a driver's availability from True to False."""
    sample_driver.availability = True 
    mock_user_dao.find_user_by_id.return_value = sample_driver
    mock_user_dao.update_user.return_value = sample_driver

    result = service.update_driver_availability(driver_id=2, availability=False)

    mock_user_dao.find_user_by_id.assert_called_once_with(2)
    assert sample_driver.availability is False
    mock_user_dao.update_user.assert_called_once_with(sample_driver)
    assert result == sample_driver


def test_update_driver_availability_no_change(
    service: AdminUserService, mock_user_dao: MagicMock, sample_driver: Driver
):
    """Tests that updating to the same status still works."""
    sample_driver.availability = True
    mock_user_dao.find_user_by_id.return_value = sample_driver
    mock_user_dao.update_user.return_value = sample_driver

    result = service.update_driver_availability(driver_id=2, availability=True)

    assert sample_driver.availability is True
    mock_user_dao.update_user.assert_called_once_with(sample_driver)
    assert result == sample_driver


def test_update_driver_availability_not_found(service: AdminUserService, mock_user_dao: MagicMock):
    """Tests that a ValueError is raised if the driver ID is not found."""
    mock_user_dao.find_user_by_id.return_value = None

    with pytest.raises(ValueError, match="No valid driver found with ID 999"):
        service.update_driver_availability(driver_id=999, availability=True)

    mock_user_dao.update_user.assert_not_called()


def test_update_driver_availability_user_is_customer(
    service: AdminUserService, mock_user_dao: MagicMock, sample_customer: Customer
):
    """Tests that a ValueError is raised if the user ID is not a Driver."""
    mock_user_dao.find_user_by_id.return_value = sample_customer

    with pytest.raises(ValueError, match="No valid driver found with ID 3"):
        service.update_driver_availability(driver_id=3, availability=True)

    mock_user_dao.update_user.assert_not_called()


def test_update_driver_availability_dao_failure(
    service: AdminUserService, mock_user_dao: MagicMock, sample_driver: Driver
):
    """Tests that an Exception is raised if the DAO update fails."""
    mock_user_dao.find_user_by_id.return_value = sample_driver
    mock_user_dao.update_user.return_value = None  

    with pytest.raises(Exception, match="Failed to update driver availability."):
        service.update_driver_availability(driver_id=2, availability=False)





def test_delete_user_success(service: AdminUserService, mock_user_dao: MagicMock, sample_driver: Driver):
    """Tests that any user (e.g., a Driver) can be deleted."""
    mock_user_dao.find_user_by_id.return_value = sample_driver
    mock_user_dao.delete_user.return_value = True 

    result = service.delete_user(user_id=2)

    mock_user_dao.find_user_by_id.assert_called_once_with(2)
    mock_user_dao.delete_user.assert_called_once_with(2)
    assert result is True


def test_delete_user_not_found(service: AdminUserService, mock_user_dao: MagicMock):
    """Tests that a ValueError is raised if the user to delete is not found."""
    mock_user_dao.find_user_by_id.return_value = None

    with pytest.raises(ValueError, match="No user found with ID 999."):
        service.delete_user(user_id=999)

    mock_user_dao.delete_user.assert_not_called()


def test_delete_user_dao_failure(service: AdminUserService, mock_user_dao: MagicMock, sample_admin: Admin):
    """Tests that an Exception is raised if the DAO deletion fails."""
    mock_user_dao.find_user_by_id.return_value = sample_admin
    mock_user_dao.delete_user.return_value = False

    with pytest.raises(Exception, match="Failed to delete user 1."):
        service.delete_user(user_id=1)




def test_list_all_users_success(service: AdminUserService, mock_user_dao: MagicMock, sample_user_list: list):
    """Tests retrieving a list of all user types."""
    mock_user_dao.find_all.return_value = sample_user_list

    result = service.list_all_users()

    mock_user_dao.find_all.assert_called_once_with()
    assert result == sample_user_list
    assert len(result) == 3


def test_list_all_users_empty(service: AdminUserService, mock_user_dao: MagicMock):
    """Tests retrieving an empty list when no users exist."""
    mock_user_dao.find_all.return_value = []

    result = service.list_all_users()

    assert result == []


def test_list_drivers_success(service: AdminUserService, mock_user_dao: MagicMock, sample_driver_list: list):
    """Tests retrieving a list of only 'driver' type users."""
    mock_user_dao.find_all.return_value = sample_driver_list

    result = service.list_drivers()

    mock_user_dao.find_all.assert_called_once_with(user_type="driver")
    assert result == sample_driver_list
    assert len(result) == 2


def test_list_drivers_empty(service: AdminUserService, mock_user_dao: MagicMock):
    """Tests retrieving an empty list when no drivers exist."""
    mock_user_dao.find_all.return_value = []

    result = service.list_drivers()

    mock_user_dao.find_all.assert_called_once_with(user_type="driver")
    assert result == []