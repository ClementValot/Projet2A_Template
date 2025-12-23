from unittest.mock import ANY, MagicMock

import pytest

from src.DAO.addressDAO import AddressDAO
from src.DAO.DBConnector import DBConnector
from src.Model.address import Address
from src.Service.address_service import AddressService


@pytest.fixture
def mock_env(monkeypatch):
    """Sets up environment variables required by the service."""
    monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "dummy_api_key")


@pytest.fixture
def mock_db_connector():
    """Provides a mock DBConnector."""
    return MagicMock(spec=DBConnector)


@pytest.fixture
def mock_address_dao():
    """Provides a mock AddressDAO."""
    return MagicMock(spec=AddressDAO)


@pytest.fixture
def service(mock_db_connector, mock_address_dao, mock_env, mocker):
    """
    Provides an AddressService instance with mocks injected.
    Patches the AddressDAO constructor to return our mock instance.
    """
    mocker.patch("src.Service.address_service.AddressDAO", return_value=mock_address_dao)
    return AddressService(db_connector=mock_db_connector)


@pytest.fixture
def sample_address():
    """Provides a sample Address object."""
    return Address(id_address=1, street_name="Rue de la Paix", street_number="10", city="Paris", postal_code=75001)


def test_init_service(mock_db_connector, mock_env, mocker):
    """Tests that the service initializes correctly and loads the API key."""
    mock_dao_class = mocker.patch("src.Service.address_service.AddressDAO")

    service = AddressService(db_connector=mock_db_connector)

    assert service.api_key == "dummy_api_key"
    mock_dao_class.assert_called_once_with(db_connector=mock_db_connector)


def test_get_or_create_address_existing(service, mock_address_dao, sample_address):
    """Tests returning an existing address if found in the database."""
    mock_address_dao.find_address_by_components.return_value = sample_address

    result = service.get_or_create_address("Rue de la Paix", "Paris", 75001, "10")

    assert result == sample_address
    mock_address_dao.find_address_by_components.assert_called_once_with(
        city="Paris", postal_code=75001, street_name="Rue de la Paix", street_number="10"
    )
    mock_address_dao.add_address.assert_not_called()


def test_get_or_create_address_new(service, mock_address_dao, sample_address):
    """Tests creating a new address if it does not exist."""
    mock_address_dao.find_address_by_components.return_value = None
    mock_address_dao.add_address.return_value = sample_address

    result = service.get_or_create_address("Rue de la Paix", "Paris", 75001, "10")

    assert result == sample_address
    mock_address_dao.add_address.assert_called_once()

    called_address = mock_address_dao.add_address.call_args[0][0]
    assert isinstance(called_address, Address)
    assert called_address.city == "Paris"
    assert called_address.street_name == "Rue de la Paix"


def test_get_or_create_address_creation_failure(service, mock_address_dao):
    """Tests that a ValueError is raised if the DAO fails to create the address."""
    mock_address_dao.find_address_by_components.return_value = None
    mock_address_dao.add_address.return_value = None

    with pytest.raises(ValueError, match="Database error while saving address"):
        service.get_or_create_address("Rue Fail", "ErrorCity", 99999)


def test_get_address_by_id_success(service, mock_address_dao, sample_address):
    """Tests successfully retrieving an address by ID."""
    mock_address_dao.find_address_by_id.return_value = sample_address

    result = service.get_address_by_id(1)

    assert result == sample_address
    mock_address_dao.find_address_by_id.assert_called_once_with(1)


def test_get_address_by_id_not_found(service, mock_address_dao):
    """Tests that a ValueError is raised if the address ID does not exist."""
    mock_address_dao.find_address_by_id.return_value = None

    with pytest.raises(ValueError, match="No address found with ID 999"):
        service.get_address_by_id(999)


def test_delete_address_success(service, mock_address_dao, sample_address):
    """Tests successfully deleting an address."""
    mock_address_dao.find_address_by_id.return_value = sample_address
    mock_address_dao.delete_address.return_value = True

    result = service.delete_address(1)

    assert result is True
    mock_address_dao.find_address_by_id.assert_called_once_with(1)
    mock_address_dao.delete_address.assert_called_once_with(1)


def test_delete_address_not_found(service, mock_address_dao):
    """Tests attempting to delete a non-existent address raises ValueError."""
    mock_address_dao.find_address_by_id.return_value = None

    with pytest.raises(ValueError, match="No address found with ID 999"):
        service.delete_address(999)

    mock_address_dao.delete_address.assert_not_called()


def test_delete_address_dao_failure(service, mock_address_dao, sample_address):
    """Tests that an Exception is raised if the DAO fails to delete the address."""
    mock_address_dao.find_address_by_id.return_value = sample_address
    mock_address_dao.delete_address.return_value = False

    with pytest.raises(Exception, match="Failed to delete address 1"):
        service.delete_address(1)


def test_list_all_addresses(service, mock_address_dao, sample_address):
    """Tests retrieving the list of all addresses."""
    address_list = [sample_address, sample_address]
    mock_address_dao.find_all_addresses.return_value = address_list

    result = service.list_all_addresses()

    assert result == address_list
    assert len(result) == 2
    mock_address_dao.find_all_addresses.assert_called_once()
