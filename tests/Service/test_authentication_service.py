from unittest import mock
from unittest.mock import ANY, MagicMock

import pytest

from src.DAO.DBConnector import DBConnector
from src.Model.customer import Customer
from src.Service.authentication_service import AuthenticationService
from src.Service.password_service import PasswordService


@pytest.fixture
def mock_db_connector() -> MagicMock:
    """
    Provides a mock for the DBConnector.
    """
    return MagicMock(spec=DBConnector)


@pytest.fixture
def mock_password_service() -> MagicMock:
    """
    Provides a mock for the PasswordService.
    """
    mock_ps = MagicMock(spec=PasswordService)
    mock_ps.check_password_strength.return_value = None
    mock_ps.create_salt.return_value = "generated_mock_salt"
    mock_ps.hash_password.return_value = "generated_mock_hash"
    # Mock set_password to mimic success by default
    mock_ps.set_password.return_value = None
    # Mock verify_password default to True to simplify login success tests
    mock_ps.verify_password.return_value = True
    return mock_ps


@pytest.fixture
def mock_user_dao(request) -> mock.MagicMock:
    """
    Patches the UserDAO class using standard mock mechanism.
    Ensures the mock is automatically cleaned up after the test.
    """
    mock_instance = mock.MagicMock()
    mock_instance.find_user_by_username.return_value = None
    mock_instance.add_user.side_effect = lambda user: user
    patcher = mock.patch("src.Service.authentication_service.UserDAO", return_value=mock_instance)
    patcher.start()
    request.addfinalizer(patcher.stop)

    return mock_instance


@pytest.fixture
def dummy_customer() -> Customer:
    """
    Provides a constant Customer object for login tests.
    """
    c = Customer(
        id_user=1,
        username="existing_user",
        phone_number="+33 6 12 34 56 78",
    )
    c._salt = "jambon"
    c._hash_password = "7877d4860ef88458096f549b618667d860540db5d59b1d153557d5cdbe1221e7"
    return c


@pytest.fixture
def service(
    mock_db_connector: MagicMock, mock_password_service: MagicMock, mock_user_dao: MagicMock
) -> AuthenticationService:
    """
    Provides an AuthenticationService instance for each test,
    injected with the necessary mocks.
    """
    return AuthenticationService(db_connector=mock_db_connector, password_service=mock_password_service)


def test_login_successful(
    service: AuthenticationService, mock_user_dao: MagicMock, mock_password_service: MagicMock, dummy_customer: Customer
):
    """
    Tests that a user can successfully log in with a valid username and password.
    """
    username = "existing_user"
    password = "soleil1234"

    mock_user_dao.find_user_by_username.return_value = dummy_customer
    mock_password_service.verify_password.return_value = True

    try:
        logged_in_user = service.login(username, password)

        assert logged_in_user is dummy_customer
        mock_user_dao.find_user_by_username.assert_called_with(username)
        mock_password_service.verify_password.assert_called_with(dummy_customer, password)

    except Exception as e:
        pytest.fail(f"login raised an unexpected exception: {e}")


def test_login_user_not_found(service: AuthenticationService, mock_user_dao: MagicMock):
    """
    Tests that login raises a ValueError if the user does not exist.
    """

    with pytest.raises(ValueError, match="User not found."):
        service.login("unknown_user", "any_password")

    mock_user_dao.find_user_by_username.assert_called_with("unknown_user")


def test_login_incorrect_password(
    service: AuthenticationService, mock_user_dao: MagicMock, mock_password_service: MagicMock, dummy_customer: Customer
):
    """
    Tests that login raises a ValueError if the password is incorrect.
    """
    username = "existing_user"
    wrong_password = "wrong_password"
    mock_user_dao.find_user_by_username.return_value = dummy_customer
    mock_password_service.verify_password.return_value = False

    with pytest.raises(ValueError, match="Incorrect password."):
        service.login(username, wrong_password)

    mock_password_service.verify_password.assert_called_with(dummy_customer, wrong_password)


def test_register_customer_successful(
    service: AuthenticationService, mock_user_dao: MagicMock, mock_password_service: MagicMock
):
    """
    Tests the successful registration of a new user.
    """
    username = "new_user_1"
    password = "ValidPassword123"
    phone = "+33 6 12 34 56 78"
    name = "John Doe" 

    try:
        new_user = service.register_customer(username, password, name, phone)
        
        mock_user_dao.find_user_by_username.assert_called_with(username)
        # We check that set_password was called, which implies handling of password/strength internally
        mock_password_service.set_password.assert_called_once()
        
        mock_user_dao.add_user.assert_called_once_with(ANY)
        created_user_arg = mock_user_dao.add_user.call_args[0][0]

        assert isinstance(created_user_arg, Customer)
        assert created_user_arg.username == username
        assert created_user_arg.phone_number == "+33 6 12 34 56 78"
        assert new_user is created_user_arg

    except Exception as e:
        pytest.fail(f"register_customer raised an unexpected exception: {e}")


def test_register_customer_successful_phone_unformatted(
    service: AuthenticationService, mock_user_dao: MagicMock, mock_password_service: MagicMock
):
    """
    Tests successful registration when the phone number is provided without spaces or country code (assumes FR).
    """
    username = "user_ok"
    password = "ValidPassword123"
    phone = "0612345678"
    name = "Jane Doe" 

    service.register_customer(username, password, name, phone)

    created_user_arg = mock_user_dao.add_user.call_args[0][0]
    assert created_user_arg.phone_number == "+33 6 12 34 56 78"


def test_register_customer_username_exists(
    service: AuthenticationService, mock_user_dao: MagicMock, dummy_customer: Customer
):
    """
    Tests that register raises a ValueError if the username is already taken.
    """
    mock_user_dao.find_user_by_username.return_value = dummy_customer

    existing_username = "existing_user"

    with pytest.raises(ValueError, match=f"Username '{existing_username}' already exists."):
        service.register_customer(existing_username, "any_password", "Name", "+33612345678")

    mock_user_dao.find_user_by_username.assert_called_with(existing_username)
    mock_user_dao.add_user.assert_not_called()


@pytest.mark.parametrize(
    "invalid_username, error_match",
    [
        ("short", "Username must contain at least 6 characters."),
        ("user!x", "Username may only contain letters"),
        ("user space", "Username may only contain letters"),
        ("user@name", "Username may only contain letters"),
    ],
)
def test_register_customer_invalid_username(
    service: AuthenticationService,
    mock_user_dao: MagicMock,
    mock_password_service: MagicMock,
    invalid_username,
    error_match,
):
    """
    Tests that register raises ValueError for username validation failures (length or characters).
    """
    with pytest.raises(ValueError, match=error_match):
        service.register_customer(invalid_username, "ValidPassword123", "Name", "+33612345678")

    mock_user_dao.find_user_by_username.assert_called_with(invalid_username)
    # We do not check set_password because validation fails before
    mock_user_dao.add_user.assert_not_called()


@pytest.mark.parametrize(
    "invalid_phone, error_match",
    [
        ("1234", "Invalid phone number. Please enter the full international format if outside France."),
        ("+33 12 34 56 78", "Invalid phone number. Please enter the full international format if outside France."),
        ("0000000000", "Invalid phone number. Please enter the full international format if outside France."),
    ],
)
def test_register_customer_invalid_phone_number(
    service: AuthenticationService,
    mock_user_dao: MagicMock,
    mock_password_service: MagicMock,
    invalid_phone,
    error_match,
):
    """
    Tests that register raises ValueError for invalid phone numbers (using phonenumbers library).
    """
    valid_username = "validuser"

    with pytest.raises(ValueError, match=error_match):
        service.register_customer(valid_username, "ValidPassword123", "Name", invalid_phone)

    mock_user_dao.find_user_by_username.assert_called_with(valid_username)
    mock_user_dao.add_user.assert_not_called()


def test_register_weak_password(
    service: AuthenticationService, mock_user_dao: MagicMock, mock_password_service: MagicMock
):
    """
    Tests that register raises an Exception if the password strength check fails.
    We configure the mocked set_password to raise the error.
    """
    weak_password = "short"
    error_message = "Password length must be at least 8 characters"

    mock_password_service.set_password.side_effect = ValueError(error_message)

    with pytest.raises(ValueError, match=error_message):
        service.register_customer("another_user_ok", weak_password, "Name", "+33612345678")

    mock_user_dao.find_user_by_username.assert_called_with("another_user_ok")
    mock_password_service.set_password.assert_called()
    mock_user_dao.add_user.assert_not_called()